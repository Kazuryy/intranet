import os
from flask import Flask, jsonify
from flask_login import LoginManager
from .models import db


def create_app(config=None):
    app = Flask(__name__)

    # COnfig
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///:memory:'
        )
    app.config['SECRET_KEY'] = 'dev_secret_key'

    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app
