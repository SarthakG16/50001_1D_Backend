import functools, sqlite3

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from actual.db import get_db

bp = Blueprint('posters', __name__, url_prefix='/posters')

@bp.route('/mine', methods=['GET'])
def my_posters():
    if request.method == 'GET':
        user_id = session.get('user_id')
        if not user_id: return send_error('Not logged in.')
        ignore_image = 0
        if request.args.get('ignore_image') and request.args.get('ignore_image') == '1':
            ignore_image = 1
        try:
            db = get_db()
            info = db.execute('SELECT * FROM poster WHERE uploader_id = ?', (user_id,)).fetchall()
            if info is None: return send_error('Requested id not found.')
            return jsonify([buildRowDictNonNull(i, 1, ignore_image) for i in info])
        except Exception as e:
            print(e)
            return send_error(str(e))

@bp.route('/', methods=['GET', 'POST', 'DELETE'])
def posters():
    if request.method == 'DELETE':
        requested_id = request.args.get('id')
        user_privilege = session.get('user_privilege')
        if not user_privilege or user_privilege == 0: return send_error('Unauthorized.')
        if requested_id == None: return send_error('Id not specified.')

        db = get_db()
        #info = db.execute('SELECT * FROM poster WHERE id = ?', (requested_id,)).fetchone()
        #if info is None: return send_error('Id not found.')

        db.execute('DELETE FROM poster WHERE id = ?', (requested_id,))
        db.commit()
        return send_success()

    if request.method == 'GET':
        requested_id = request.args.get('id')
        requested_status = request.args.get('status')

        ignore_image = 0
        if request.args.get('ignore_image') and request.args.get('ignore_image') == '1':
            ignore_image = 1

        user_privilege = 0
        user_privilege = session.get('user_privilege')
        db = get_db()

        if requested_id:
            try:
                info = db.execute('SELECT * FROM poster WHERE id = ?', (requested_id,)).fetchone()
                if info is None: return send_error('Requested id not found.')
                return jsonify(buildRowDictNonNull(info, user_privilege, ignore_image))
            except Exception as e:
                print(e)
                return send_error(str(e))

        if requested_status:
            if user_privilege == 0: return jsonify([])
            info = db.execute('SELECT * FROM poster WHERE status = ?', (requested_status,)).fetchall()
            if info is None: return send_error('No posters matching the requested status.')
            ls = [buildRowDictNonNull(i, user_privilege, ignore_image) for i in info]
            return jsonify(ls)

        if user_privilege == 1: info = db.execute('SELECT * FROM poster').fetchall()
        else: info = db.execute('SELECT * FROM poster WHERE status="posted"').fetchall()

        ls = [buildRowDictNonNull(i, user_privilege, ignore_image) for i in info]
        print(ls)
        print(jsonify(ls))
        return jsonify(ls)

    if request.method == 'POST':
        user_privilege = session.get('user_privilege')
        user_id = session.get('user_id')
        if not user_privilege or user_privilege == 0: return send_error('Unauthorized.')
        json = request.get_json()
        db = get_db()

        if 'id' not in json:
            if 'title' not in json or json['title'] == "":
                return send_error('Missing title. New posters must have a title.')

            title = json['title']
            json['uploader_id'] = user_id

            if db.execute(
                'SELECT id FROM poster WHERE title = ?', (title,)
            ).fetchone() is not None:
                return send_error('Poster already exists with given title.')

            db.execute(
                'INSERT INTO poster (title, status) VALUES (?, ?)',
                (title, 'pending')
            )

            json.pop('title')
            if len(json) == 0:
                db.commit()
                return send_success()

            ls = []
            print(json)
            for key in json:
                if key.startswith('date') and json[key]:
                    if ' ' not in json[key]: return send_error('Invalid date format')
                    s = json[key].split(' ')
                    if len(s[0].split('-')) != 3 or len(s[1].split(':')) != 3:
                         return send_error('Invalid date format')

                value = '"{}"'.format(json[key]) if json[key] else 'NULL'
                ls.append('{} = {}'.format(key, value))
            print('command', 'UPDATE poster SET ' + ', '.join(ls) + ' WHERE title = "' + str(title) + '"')
            try:
                db.execute('UPDATE poster SET ' + ', '.join(ls) + ' WHERE title = "' + str(title) + '"')
            except sqlite3.OperationalError as e:
                print(e)
                return send_error('Invalid parameter. {}'.format(e))
            except Exception as e:
                print(e)
                return send_error('Error in updating the databse. {}'.format(e))

            db.commit()
            return send_success()

        else:
            id = json['id']
            if id == '': return send_error('Missing Id in request.')
            json.pop('id')

            info = db.execute('SELECT * FROM poster WHERE id = ?', (id,)).fetchone()
            if info is None:
                return send_error('Id not found.')

            ls = []
            for key in json:
                if key.startswith('date'):
                    if json[key] and len(json[key].split(' ')) == 1:
                        return send_error('Invalid date format for {}'.format(key))
                ls.append('{} = "{}"'.format(key, json[key]))
            try:
                db.execute('UPDATE poster SET ' + ', '.join(ls) + ' WHERE id = ' + str(id))
            except sqlite3.OperationalError:
                return send_error('Invalid parameter.')
            except:
                return send_error('Error in updating the databse.')

            db.commit()

            return send_success()



    return ""

@bp.route('/debug_all', methods = ['GET'])
def debug():
    ignore_image = 0
    if request.args.get('ignore_image') and request.args.get('ignore_image') == '1':
        ignore_image = 1

    db = get_db()
    info = db.execute('SELECT * FROM poster').fetchall()
    posters = [buildRowDictNonNull(i, 1, ignore_image, 1) for i in info]

    if len(posters) == 0: return 'No posters.'
    return jsonify(posters)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    user_privilege = session.get('user_privilege')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

def send_error(text):
    return jsonify(status = 'failure', error_message = text)

def send_success():
    return jsonify(status = 'success')

def buildRowDict(row, force_uploader = 0):
    print(row)
    d = {}
    d['id'] = row[0]
    if force_uploader == 1:
        d['uploader_id'] = row[1]
    d['title'] = row[2]
    d['status'] = row[3]
    d['serialized_image_data'] = row[4]
    d['description'] = row[5]
    d['link'] = row[6]
    d['category'] = row[7]
    d['locations'] = row[8]
    d['contact_name'] = row[9]
    d['contact_email'] = row[10]
    d['contact_number'] = row[11]
    d['date_submitted'] = str(row[12])
    d['date_approved'] = str(row[13])
    d['date_posted'] = str(row[14])
    d['date_expiry'] = str(row[15])


    return d

def buildRowDictNonNull(row, privilege = -1, ignore_image = 0, force_uploader = 0):
    d = buildRowDict(row, force_uploader)
    if privilege == -1:
        d['date_submitted'] = None
        d['date_approved'] = None
        d['date_posted'] = None
        d['date_expiry'] = None
    if ignore_image == 1:
        d['serialized_image_data'] = None
    return {k:d[k] for k in d if d[k] and d[k] != 'None'}
