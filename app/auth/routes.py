from flask import request, jsonify
from flask_login import login_user, logout_user
from . import auth_bp
from ..models import User
from .. import bcrypt


@auth_bp.post('/login')
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if not user or not bcrypt.check_password_hash(user.password, data.get('password')):
        return jsonify({'error': 'Identifiants invalides'}), 401

    login_user(user)
    return jsonify({'message': 'Connecté', 'role': user.type}), 200


@auth_bp.post('/logout')
def logout():
    logout_user()
    return jsonify({'message': 'Déconnecté'}), 200
