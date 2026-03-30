import re
from flask import request, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from . import auth_bp
from ..models import db, Information, User
from .. import bcrypt
from app import limiter


@auth_bp.post('/login')
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if not user or not bcrypt.check_password_hash(user.password, data.get('password')):
        return jsonify({'error': 'Identifiants invalides'}), 401

    login_user(user)
    return jsonify({'message': 'Connecté', 'role': user.type}), 200


@auth_bp.post('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Déconnecté'}), 200


@auth_bp.patch('/profile/password')
@login_required
def change_password():
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not bcrypt.check_password_hash(current_user.password, current_password):
        return jsonify({'error': 'Mot de passe actuel incorrect'}), 400

    if len(new_password) < 8:
        return jsonify(
            {'error': 'Le mot de passe doit contenir au moins 8 caractères'}
        ), 400

    hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
    current_user.password = hashed
    db.session.commit()
    return jsonify({'message': 'Mot de passe mis à jour'}), 200


@auth_bp.patch('/profile/phone')
@login_required
def change_phone():
    data = request.get_json()
    numero = data.get('numero', '').strip()

    if not re.fullmatch(r'0[1-9]\d{8}', numero):
        return jsonify({'error': 'Numéro de téléphone invalide'}), 400

    info = Information.query.filter_by(id_user=current_user.id).first()
    if info:
        info.numero = int(numero)
    else:
        db.session.add(Information(id_user=current_user.id, numero=int(numero)))
    db.session.commit()
    return jsonify({'message': 'Numéro mis à jour'}), 200
