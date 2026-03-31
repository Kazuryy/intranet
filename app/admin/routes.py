import secrets
import unicodedata
from datetime import datetime, timedelta, timezone
from flask import request, jsonify
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
from . import admin_bp
from ..models import db, Employe, Log, User
from ..decorators import role_required


def _log(action, target_id=None):
    db.session.add(Log(
        user_id=current_user.id,
        action=action,
        target_type='user',
        target_id=target_id,
        ip_address=request.remote_addr,
        user_agent=(request.user_agent.string or '')[:255],
        created_at=datetime.now(timezone.utc)
    ))


ALLOWED_TYPES = {'élève', 'employé', 'parent', 'administrateur'}
DIRECTION_TYPES = {'élève', 'parent'}


def _normalize(s):
    """Lowercase, remove accents and spaces."""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower().replace(' ', '').replace('-', '')


def _generate_email(prenom, nom):
    base = f'{_normalize(prenom)}.{_normalize(nom)}@guardiaschool.fr'
    if not User.query.filter_by(mail_interne=base).first():
        return base
    i = 2
    while True:
        candidate = (
            f'{_normalize(prenom)}.{_normalize(nom)}{i}@guardiaschool.fr'
        )
        if not User.query.filter_by(mail_interne=candidate).first():
            return candidate
        i += 1


def _generate_username(prenom, nom):
    base = f'{_normalize(prenom)[0]}{_normalize(nom)}'
    if not User.query.filter_by(username=base).first():
        return base
    i = 2
    while True:
        candidate = f'{base}{i}'
        if not User.query.filter_by(username=candidate).first():
            return candidate
        i += 1


def _can_create(requested_type):
    if current_user.type == 'administrateur':
        return True
    if current_user.type == 'employé':
        emp = Employe.query.filter_by(id_user=current_user.id).first()
        if emp and emp.role == 'direction':
            return requested_type in DIRECTION_TYPES
    return False


@admin_bp.get('/users')
@login_required
@role_required('administrateur', 'employé')
def list_users():
    type_filter = request.args.get('type', '').strip()
    search = request.args.get('search', '').strip()

    query = User.query

    if current_user.type == 'employé':
        emp = Employe.query.filter_by(id_user=current_user.id).first()
        if not emp or emp.role != 'direction':
            return jsonify({'error': 'Accès refusé'}), 403
        query = query.filter(User.type.in_(DIRECTION_TYPES))

    if type_filter:
        query = query.filter(User.type == type_filter)

    if search:
        query = query.filter(
            (User.nom.ilike(f'%{search}%')) |
            (User.prenom.ilike(f'%{search}%')) |
            (User.username.ilike(f'%{search}%'))
        )

    users = query.order_by(User.nom, User.prenom).all()

    return jsonify([{
        'id': u.id,
        'nom': u.nom,
        'prenom': u.prenom,
        'username': u.username,
        'type': u.type,
        'is_active': u.is_active
    } for u in users]), 200


@admin_bp.post('/users')
@login_required
@role_required('administrateur', 'employé')
def create_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON requis'}), 400

    nom = (data.get('nom') or '').strip()
    prenom = (data.get('prenom') or '').strip()
    user_type = (data.get('type') or '').strip()

    if not nom or not prenom or not user_type:
        return jsonify({'error': 'nom, prenom et type sont requis'}), 400

    if user_type not in ALLOWED_TYPES:
        return jsonify({'error': 'Type invalide'}), 400

    if not _can_create(user_type):
        return jsonify({'error': 'Accès refusé'}), 403

    for _ in range(5):
        mail_interne = _generate_email(prenom, nom)
        username = _generate_username(prenom, nom)
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=48)

        user = User(
            nom=nom,
            prenom=prenom,
            type=user_type,
            username=username,
            mail_interne=mail_interne,
            password='',
            setup_token=token,
            setup_token_expires=expires
        )
        db.session.add(user)
        try:
            db.session.flush()
            _log('user_created', target_id=user.id)
            db.session.commit()
            return jsonify({
                'id': user.id,
                'mail_interne': mail_interne,
                'username': username,
                'setup_link': f'/auth/setup-password?token={token}'
            }), 201
        except IntegrityError:
            db.session.rollback()

    return jsonify({'error': 'Impossible de générer un identifiant unique'}), 500


@admin_bp.patch('/users/<int:user_id>')
@login_required
@role_required('administrateur')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON requis'}), 400

    changes = []

    if 'nom' in data:
        nom = (data['nom'] or '').strip()
        if not nom:
            return jsonify({'error': 'nom ne peut pas être vide'}), 400
        user.nom = nom
        changes.append('nom')

    if 'prenom' in data:
        prenom = (data['prenom'] or '').strip()
        if not prenom:
            return jsonify({'error': 'prenom ne peut pas être vide'}), 400
        user.prenom = prenom
        changes.append('prenom')

    if 'type' in data:
        user_type = (data['type'] or '').strip()
        if user_type not in ALLOWED_TYPES:
            return jsonify({'error': 'Type invalide'}), 400
        user.type = user_type
        changes.append('type')

    if 'is_active' in data:
        if not isinstance(data['is_active'], bool):
            return jsonify({'error': 'is_active doit être un booléen'}), 400
        user.is_active = data['is_active']
        changes.append('is_active')

    if not changes:
        return jsonify({'error': 'Aucun champ modifiable fourni'}), 400

    _log(f'user_updated:{",".join(changes)}', target_id=user.id)
    db.session.commit()

    return jsonify({
        'id': user.id,
        'nom': user.nom,
        'prenom': user.prenom,
        'type': user.type,
        'is_active': user.is_active
    }), 200


@admin_bp.delete('/users/<int:user_id>')
@login_required
@role_required('administrateur')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        return jsonify({'error': 'Impossible de supprimer son propre compte'}), 403

    _log('user_deleted', target_id=user.id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Compte supprimé'}), 200
