from functools import wraps
from flask import jsonify
from flask_login import current_user


def is_direction():
    from .models import Direction
    return Direction.query.filter_by(id_user=current_user.id).first() is not None


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentification requise'}), 401
            if getattr(current_user, 'type', None) not in roles:
                return jsonify({'error': 'Accès refusé'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
