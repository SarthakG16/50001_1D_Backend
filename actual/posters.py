import functools, sqlite3

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from actual.db import get_db

bp = Blueprint('posters', __name__, url_prefix='/posters')

@bp.route('/', methods=['GET', 'POST', 'DELETE'])
def posters():
    if request.method == 'DELETE':
        requested_id = request.args.get('id')
        user_privelage = session.get('user_privelage')
        if user_privelage == 0: return error('Unauthorized.')
        if requested_id == None: return error('Id not specified.')

        db = get_db()
        #info = db.execute('SELECT * FROM poster WHERE id = ?', (requested_id,)).fetchone()
        #if info is None: return error('Id not found.')

        db.execute('DELETE FROM poster WHERE id = ?', (requested_id,))
        db.commit()
        return success()

    if request.method == 'GET':
        requested_id = request.args.get('id')
        requested_status = request.args.get('status')
        user_privelage = session.get('user_privelage')
        db = get_db()

        if requested_id:
            info = db.execute('SELECT * FROM poster WHERE id = ?', (requested_id,)).fetchone()
            if info is None: return error('Requested id not found.')
            return jsonify(buildRowDictNonNull(info, user_privelage))

        if requested_status:
            if user_privelage == 0: return jsonify([])
            info = db.execute('SELECT * FROM poster WHERE status = ?', (requested_status,)).fetchall()
            if info is None: return error('No posters matching the requested status.')
            ls = [buildRowDictNonNull(i, user_privelage) for i in info]
            return jsonify(ls)

        if user_privelage == 1: info = db.execute('SELECT * FROM poster').fetchall()
        else: info = db.execute('SELECT * FROM poster WHERE status="posted"').fetchall()

        ls = [buildRowDictNonNull(i, user_privelage) for i in info]
        print(ls)
        print(jsonify(ls))
        return jsonify(ls)

    if request.method == 'POST':
        user_privelage = session.get('user_privelage')
        if user_privelage == 0: return error('Unauthorized.')
        json = request.get_json()
        db = get_db()

        if 'id' not in json:
            if 'title' not in json or json['title'] == "":
                return error('Missing title. New posters must have a title.')

            title = json['title']

            if db.execute(
                'SELECT id FROM poster WHERE title = ?', (title,)
            ).fetchone() is not None:
                return error('Poster already exists with given title.')

            db.execute(
                'INSERT INTO poster (title, status) VALUES (?, ?)',
                (title, 'pending')
            )

            json.pop('title')
            ls = []
            for key in json:
                ls.append('{} = "{}"'.format(key, json[key]))
            try:
                db.execute('UPDATE poster SET ' + ', '.join(ls) + ' WHERE title = ' + str(title))
            except sqlite3.OperationalError as e:
                print(e)
                return error('Invalid parameter. {}'.format(e))
            except as e:
                print(e)
                return error('Error in updating the databse. {}'.format(e))

            db.commit()
            return success()

        else:
            id = json['id']
            if id == '': return error('Missing Id in request.')
            json.pop('id')

            info = db.execute('SELECT * FROM poster WHERE id = ?', (id,)).fetchone()
            if info is None:
                return error('Id not found.')

            ls = []
            for key in json:
                if key.startswith('date'):
                    if len(json[key].split(' ')) == 1:
                        return error('Invalid date format for {}'.format(key))
                ls.append('{} = "{}"'.format(key, json[key]))
            try:
                db.execute('UPDATE poster SET ' + ', '.join(ls) + ' WHERE id = ' + str(id))
            except sqlite3.OperationalError:
                return error('Invalid parameter.')
            except:
                return error('Error in updating the databse.')

            db.commit()

            return success()



    return ""


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    user_privelage = session.get('user_privelage')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

def error(text):
    return jsonify(status = 'failure', error_message = text)

def success():
    return jsonify(status = 'success')

def buildRowDict(row):
    d = {}
    d['id'] = row[0]
    d['title'] = row[1]
    d['status'] = row[2]
    d['serialized_image_data'] = row[3]
    d['description'] = row[4]
    d['link'] = row[5]
    d['category'] = row[6]
    d['locations'] = row[7]
    d['contact_name'] = row[8]
    d['contact_email'] = row[9]
    d['contact_number'] = row[10]
    d['date_submitted'] = str(row[11])
    d['date_approved'] = str(row[12])
    d['date_posted'] = str(row[13])
    d['date_expiry'] = str(row[14])

    return d

def buildRowDictNonNull(row, privelage = 0):
    d = buildRowDict(row)
    if privelage == 0:
        d['date_submitted'] = None
        d['date_approved'] = None
        d['date_posted'] = None
        d['date_expiry'] = None
    return {k:d[k] for k in d if d[k] and d[k] != 'None'}
