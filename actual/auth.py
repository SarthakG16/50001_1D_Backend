import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from actual.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        json = request.get_json()
        # requested_privelage = request.get_json()['requested_privelage']
        db = get_db()
        privelage = 0
        error = None

        if 'username' not in json or json['username'] == '': return error('Username is required.')
        if 'password' not in json or json['password'] == '': return error('Password is required.')
        if 'privelage' in json :
            if json['privelage'] == 'administrator': privelage = 1
            else: return error('Unauthorized.')

        username = json['username']
        password = json['password']

        if db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            return error('Username already exists.')

        db.execute(
            'INSERT INTO user (username, password, privelage) VALUES (?, ?, ?)',
            (username, generate_password_hash(password), privelage)
        )
        db.commit()
        return success()

    return ""

@bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        json = request.get_json()
        privelage = 0
        db = get_db()
        error = None

        if 'username' not in json or json['username'] == '': return error('Username is required.')
        if 'password' not in json or json['password'] == '': return error('Username is required.')
        if 'requested_privelage' in json:
            if json['requested_privelage'] == 'administrator': privelage = 1
            else: return error('Unauthorized.')

        username = json['username']
        password = json['password']

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None: return error('Invalid username or password.')
        if not check_password_hash(user['password'], password):
            return error('Invalid username or password.')
        if privelage > user['privelage']:
            return error('Unauthorized')

        session.clear()
        session['user_id'] = user['id']
        session['user_privelage'] = user['privelage']
        return success()

    return ""

@bp.route('/logout')
def logout():
    session.clear()
    return success()


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


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def error(text):
    return jsonify(status = 'failure', error_message = text)

def success():
    return jsonify(status = 'success')
