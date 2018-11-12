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

        if 'username' not in json or json['username'] == '': return send_error('Username is required.')
        if 'password' not in json or json['password'] == '': return send_error('Password is required.')
        if 'privelage' in json :
            if json['privelage'] == 'administrator': privelage = 1
            else: return send_error('Unauthorized.')

        username = json['username']
        password = json['password']

        if db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            return send_error('Username already exists.')

        db.execute(
            'INSERT INTO user (username, password, privelage) VALUES (?, ?, ?)',
            (username, generate_password_hash(password), privelage)
        )
        db.commit()
        return send_success()

    return ""

@bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        json = request.get_json()
        privelage = 0
        db = get_db()
        error = None

        if 'username' not in json or json['username'] == '': return send_error('Username is required.')
        if 'password' not in json or json['password'] == '': return send_error('Username is required.')
        if 'requested_privelage' in json:
            if json['requested_privelage'] == 'administrator': privelage = 1
            else: return send_error('Unauthorized.')

        username = json['username']
        password = json['password']

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if not user: return send_error('Invalid username or password.')
        if not check_password_hash(user['password'], password):
            return send_error('Invalid username or password.')
        if privelage > user['privelage']:
            return send_error('Unauthorized')

        session.clear()
        session['user_id'] = user['id']
        session['user_privelage'] = user['privelage']
        return jsonify(status = 'success', privelage = user['privelage'])

    return ""

@bp.route('/logout')
def logout():
    session.clear()
    return send_success()


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

def send_error(text):
    return jsonify(status = 'failure', error_message = text)

def send_success(text = None):
    if text: return jsonify(status = 'success')
    return jsonify(status = 'success', description = text)
