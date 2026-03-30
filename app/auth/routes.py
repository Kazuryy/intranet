import re
from datetime import datetime, timezone
from flask import request, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from . import auth_bp
from ..models import db, Direction, Information, Mail, User
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


@auth_bp.post('/profile/contact-direction')
@login_required
def contact_direction():
    data = request.get_json()
    champ = data.get('champ', '').strip()

    allowed_champs = {'nom', 'prenom', 'adresse'}
    if champ not in allowed_champs:
        return jsonify({'error': 'Champ invalide'}), 400

    direction = Direction.query.first()
    if not direction:
        return jsonify({'error': 'Aucun responsable trouvé'}), 404

    objet = f'Demande de modification — {champ}'
    contenu = (
        f"Bonjour,\n\n"
        f"{current_user.prenom} {current_user.nom} "
        f"(username : {current_user.username}) "
        f"souhaite modifier le champ « {champ} » de son profil.\n\n"
        f"Merci de traiter cette demande."
    )

    mail = Mail(
        id_expediteur=current_user.id,
        id_destinataire=direction.id_user,
        objet=objet,
        contenu=contenu,
        date=datetime.now(timezone.utc)
    )
    db.session.add(mail)
    db.session.commit()
    return jsonify({'message': 'Demande envoyée à la direction'}), 201
