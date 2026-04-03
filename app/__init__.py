import os
from flask import Flask, jsonify
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.errors import RateLimitExceeded
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from .models import db


bcrypt = Bcrypt()
limiter = Limiter(get_remote_address)
talisman = Talisman()


def create_app(config=None):
    app = Flask(__name__)

    # COnfig
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///:memory:'
    )
    flask_env = os.environ.get('FLASK_ENV', '').lower()
    is_testing = (config or {}).get('TESTING', False)
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        if flask_env in ('development', 'dev', 'testing', 'test') or is_testing:
            secret_key = 'dev_secret_key'
        else:
            raise RuntimeError(
                'SECRET_KEY must be set in non-development environments'
            )
    app.config['SECRET_KEY'] = secret_key
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600

    if config:
        app.config.update(config)

    db.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    talisman.init_app(
        app,
        force_https=os.environ.get('FLASK_ENV') == 'production',
        strict_transport_security=os.environ.get('FLASK_ENV') == 'production',
        frame_options='DENY',
        x_content_type_options=True,
        content_security_policy={
            'default-src': "'self'"
        }
    )

    login_manager = LoginManager()
    login_manager.init_app(app)

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(e):
        return jsonify({'error': 'Trop de tentatives, réessayez plus tard.'}), 429

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Authentification requise'}), 401

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from .routes import messagesbp
    app.register_blueprint(messagesbp, url_prefix='/api/messages') 

    return app