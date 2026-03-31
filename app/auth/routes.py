import re
from datetime import datetime, timezone
from flask import request, jsonify, session
from flask_login import current_user, login_required, login_user, logout_user
from . import auth_bp
from ..models import db, Direction, Information, Log, Mail, User
from .. import bcrypt
from .. import limiter


def _log(action, user_id=None, target_type=None, target_id=None):
    db.session.add(Log(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        ip_address=request.remote_addr,
        user_agent=(request.user_agent.string or '')[:255],
        created_at=datetime.now(timezone.utc)
    ))


@auth_bp.post('/login')
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON requis'}), 400

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'Identifiants requis'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        _log('login_failure')
        db.session.commit()
        return jsonify({'error': 'Identifiants invalides'}), 401

    if not user.is_active:
        _log('login_inactive', user_id=user.id)
        db.session.commit()
        return jsonify({'error': 'Compte désactivé'}), 403

    session.permanent = True
    login_user(user)
    _log('login_success', user_id=user.id)
    db.session.commit()
    return jsonify({'message': 'Connecté', 'role': user.type}), 200


@auth_bp.post('/logout')
@login_required
def logout():
    _log('logout', user_id=current_user.id)
    db.session.commit()
    logout_user()
    return jsonify({'message': 'Déconnecté'}), 200


@auth_bp.patch('/profile/password')
@login_required
@limiter.limit("5 per minute")
def change_password():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON requis'}), 400

    current_password = data.get('current_password') or ''
    new_password = data.get('new_password') or ''

    if not bcrypt.check_password_hash(current_user.password, current_password):
        return jsonify({'error': 'Mot de passe actuel incorrect'}), 400

    if len(new_password) < 8:
        return jsonify(
            {'error': 'Le mot de passe doit contenir au moins 8 caractères'}
        ), 400

    user = db.session.get(User, current_user.id)
    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    _log('password_changed', user_id=current_user.id)
    db.session.commit()
    return jsonify({'message': 'Mot de passe mis à jour'}), 200


@auth_bp.patch('/profile/phone')
@login_required
def change_phone():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON requis'}), 400

    numero = (data.get('numero') or '').strip()

    if not re.fullmatch(r'0[1-9]\d{8}', numero):
        return jsonify({'error': 'Numéro de téléphone invalide'}), 400

    info = Information.query.filter_by(id_user=current_user.id).first()
    if info:
        info.numero = numero
    else:
        db.session.add(Information(id_user=current_user.id, numero=numero))
    _log('phone_changed', user_id=current_user.id)
    db.session.commit()
    return jsonify({'message': 'Numéro mis à jour'}), 200


@auth_bp.post('/profile/contact-direction')
@login_required
def contact_direction():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON requis'}), 400

    champ = (data.get('champ') or '').strip()

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

    db.session.add(Mail(
        id_expediteur=current_user.id,
        id_destinataire=direction.id_user,
        objet=objet,
        contenu=contenu,
        date=datetime.now(timezone.utc)
    ))
    _log('contact_direction', user_id=current_user.id, target_type='direction')
    db.session.commit()
    return jsonify({'message': 'Demande envoyée à la direction'}), 201
