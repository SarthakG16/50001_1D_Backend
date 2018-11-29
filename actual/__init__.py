import os
from flask import Flask, jsonify, session
from actual.db import get_db

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config = True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent = True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/debug_current_user')
    def current():
        d = {}
        d['user_id'] = session.get('user_id')
        d['privilege'] = session.get('user_privilege')
        return jsonify(d)

    @app.route('/debug_users', methods = ['GET'])
    def debug():
        db = get_db()
        info = db.execute('SELECT * FROM user').fetchall()
        ls = []
        for user in info:
            d = {}
            d['username'] = user[1]
            d['privilege'] = user[3]
            ls.append(d)

        if len(ls) == 0: return 'No users.'

        return jsonify(ls)

    from . import db
    db.init_app(app)

    from . import auth, posters
    app.register_blueprint(auth.bp)
    app.register_blueprint(posters.bp)

    return app
