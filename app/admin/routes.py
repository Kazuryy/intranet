import secrets
import unicodedata
from datetime import datetime, timedelta, timezone
from flask import request, jsonify
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError
from . import admin_bp
from ..models import db, Batiment, Classe, Etage, Log, Matiere, Prof, Salle, User
from ..decorators import is_direction, role_required


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
    prenom_norm = _normalize(prenom)
    nom_norm = _normalize(nom)
    first = prenom_norm[0] if prenom_norm else (nom_norm[0] if nom_norm else 'u')
    nom_norm = nom_norm or 'ser'
    base = f'{first}{nom_norm}'
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
    if current_user.type == 'employé' and is_direction():
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
        if not is_direction():
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
    if data is None:
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

    mail_interne = _generate_email(prenom, nom)
    username = _generate_username(prenom, nom)
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=48)

    for _ in range(5):
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
                'setup_token': token
            }), 201
        except IntegrityError:
            db.session.rollback()
            mail_interne = _generate_email(prenom, nom)
            username = _generate_username(prenom, nom)
            token = secrets.token_urlsafe(32)
            expires = datetime.now(timezone.utc) + timedelta(hours=48)

    return jsonify({'error': 'Impossible de générer un identifiant unique'}), 500


@admin_bp.patch('/users/<int:user_id>')
@login_required
@role_required('administrateur', 'employé')
def update_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    if current_user.type == 'employé':
        if not is_direction() or user.type not in DIRECTION_TYPES:
            return jsonify({'error': 'Accès refusé'}), 403
    data = request.get_json(silent=True)
    if data is None:
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
@role_required('administrateur', 'employé')
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    if current_user.type == 'employé':
        if not is_direction() or user.type not in DIRECTION_TYPES:
            return jsonify({'error': 'Accès refusé'}), 403

    if user.id == current_user.id:
        return jsonify({'error': 'Impossible de supprimer son propre compte'}), 403

    _log('user_deleted', target_id=user.id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Compte supprimé'}), 200


@admin_bp.post('/users/<int:user_id>/set-prof')
@login_required
@role_required('administrateur')
def set_prof(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({'error': 'Utilisateur introuvable'}), 404
    if user.type != 'employé':
        return jsonify({'error': "L'utilisateur doit être de type employé"}), 400

    existing = Prof.query.filter_by(id_user=user_id).first()
    if existing:
        return jsonify({'message': 'Déjà professeur', 'id_prof': existing.id}), 200

    prof = Prof(id_user=user_id)
    db.session.add(prof)
    _log('set_prof', target_id=user_id)
    db.session.commit()
    return jsonify({'message': 'Professeur créé', 'id_prof': prof.id}), 201


@admin_bp.delete('/users/<int:user_id>/set-prof')
@login_required
@role_required('administrateur')
def unset_prof(user_id):
    prof = Prof.query.filter_by(id_user=user_id).first()
    if not prof:
        return jsonify({'error': 'Cet utilisateur n\'est pas professeur'}), 404
    _log('unset_prof', target_id=user_id)
    db.session.delete(prof)
    db.session.commit()
    return jsonify({'message': 'Statut professeur retiré'}), 200


@admin_bp.get('/users/<int:user_id>/prof-status')
@login_required
@role_required('administrateur')
def prof_status(user_id):
    prof = Prof.query.filter_by(id_user=user_id).first()
    matieres = [{'id': m.id, 'nom': m.nom} for m in prof.matieres] if prof else []
    return jsonify({
        'is_prof': prof is not None,
        'id_prof': prof.id if prof else None,
        'matieres': matieres,
    }), 200


@admin_bp.post('/users/<int:user_id>/prof-matieres')
@login_required
@role_required('administrateur')
def set_prof_matieres(user_id):
    prof = Prof.query.filter_by(id_user=user_id).first()
    if not prof:
        return jsonify({'error': 'Cet utilisateur n\'est pas professeur'}), 404

    data = request.get_json(silent=True) or {}
    matiere_ids = data.get('matiere_ids', [])
    if not isinstance(matiere_ids, list):
        return jsonify({'error': 'matiere_ids doit être une liste'}), 400

    matieres = Matiere.query.filter(Matiere.id.in_(matiere_ids)).all()
    prof.matieres = matieres
    _log('prof_matieres_updated', target_id=user_id)
    db.session.commit()
    return jsonify({'matieres': [{'id': m.id, 'nom': m.nom} for m in matieres]}), 200


# ── Matières ─────────────────────────────────────────────────────

@admin_bp.get('/matieres')
@login_required
@role_required('administrateur')
def list_matieres():
    matieres = Matiere.query.order_by(Matiere.nom).all()
    return jsonify([{'id': m.id, 'nom': m.nom} for m in matieres]), 200


@admin_bp.post('/matieres')
@login_required
@role_required('administrateur')
def create_matiere():
    data = request.get_json(silent=True)
    if not data or not str(data.get('nom', '')).strip():
        return jsonify({'error': 'Nom requis'}), 400
    nom = str(data['nom']).strip()[:100]
    if Matiere.query.filter_by(nom=nom).first():
        return jsonify({'error': 'Cette matière existe déjà'}), 409
    m = Matiere(nom=nom)
    db.session.add(m)
    db.session.commit()
    return jsonify({'id': m.id, 'nom': m.nom}), 201


@admin_bp.patch('/matieres/<int:mid>')
@login_required
@role_required('administrateur')
def update_matiere(mid):
    m = db.session.get(Matiere, mid)
    if not m:
        return jsonify({'error': 'Matière introuvable'}), 404
    data = request.get_json(silent=True)
    if not data or not str(data.get('nom', '')).strip():
        return jsonify({'error': 'Nom requis'}), 400
    m.nom = str(data['nom']).strip()[:100]
    db.session.commit()
    return jsonify({'id': m.id, 'nom': m.nom}), 200


@admin_bp.delete('/matieres/<int:mid>')
@login_required
@role_required('administrateur')
def delete_matiere(mid):
    m = db.session.get(Matiere, mid)
    if not m:
        return jsonify({'error': 'Matière introuvable'}), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify({'message': 'Supprimée'}), 200


# ── Classes ───────────────────────────────────────────────────────

def _classe_to_dict(c):
    prof = None
    if c.id_prof_principal:
        p = db.session.get(Prof, c.id_prof_principal)
        if p and p.user:
            prof = {'id': p.id, 'nom': p.user.nom, 'prenom': p.user.prenom}
    return {
        'id': c.id,
        'niveau': c.niveau,
        'suffixe': c.suffixe or '',
        'annee': c.annee,
        'prof_principal': prof,
    }


@admin_bp.get('/classes')
@login_required
@role_required('administrateur')
def list_classes():
    classes = Classe.query.order_by(
        Classe.annee.desc(), Classe.niveau, Classe.suffixe
    ).all()
    return jsonify([_classe_to_dict(c) for c in classes]), 200


@admin_bp.post('/classes')
@login_required
@role_required('administrateur')
def create_classe():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON requis'}), 400
    try:
        niveau = int(data.get('niveau', 0))
        annee = int(data.get('annee', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'niveau et annee doivent être des entiers'}), 400
    if not niveau or not annee:
        return jsonify({'error': 'niveau et annee requis'}), 400
    suffixe = str(data.get('suffixe') or '').strip()[:10] or None
    id_prof = data.get('id_prof_principal') or None
    if id_prof and not db.session.get(Prof, id_prof):
        return jsonify({'error': 'Prof introuvable'}), 404
    c = Classe(niveau=niveau, suffixe=suffixe, annee=annee, id_prof_principal=id_prof)
    db.session.add(c)
    db.session.commit()
    return jsonify(_classe_to_dict(c)), 201


@admin_bp.patch('/classes/<int:cid>')
@login_required
@role_required('administrateur')
def update_classe(cid):
    c = db.session.get(Classe, cid)
    if not c:
        return jsonify({'error': 'Classe introuvable'}), 404
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON requis'}), 400
    if 'niveau' in data:
        try:
            c.niveau = int(data['niveau'])
        except (ValueError, TypeError):
            return jsonify({'error': 'niveau doit être un entier'}), 400
    if 'annee' in data:
        try:
            c.annee = int(data['annee'])
        except (ValueError, TypeError):
            return jsonify({'error': 'annee doit être un entier'}), 400
    if 'suffixe' in data:
        c.suffixe = str(data['suffixe'] or '').strip()[:10] or None
    if 'id_prof_principal' in data:
        id_prof = data['id_prof_principal'] or None
        if id_prof and not db.session.get(Prof, id_prof):
            return jsonify({'error': 'Prof introuvable'}), 404
        c.id_prof_principal = id_prof
    db.session.commit()
    return jsonify(_classe_to_dict(c)), 200


@admin_bp.delete('/classes/<int:cid>')
@login_required
@role_required('administrateur')
def delete_classe(cid):
    c = db.session.get(Classe, cid)
    if not c:
        return jsonify({'error': 'Classe introuvable'}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': 'Supprimée'}), 200


# ── Salles ────────────────────────────────────────────────────────

@admin_bp.get('/salles')
@login_required
@role_required('administrateur')
def list_salles():
    salles = Salle.query.order_by(Salle.nom).all()
    return jsonify([{'id': s.id, 'nom': s.nom} for s in salles]), 200


@admin_bp.post('/salles')
@login_required
@role_required('administrateur')
def create_salle():
    data = request.get_json(silent=True)
    if not data or not str(data.get('nom', '')).strip():
        return jsonify({'error': 'Nom requis'}), 400
    nom = str(data['nom']).strip()[:100]
    etage = Etage.query.first()
    if not etage:
        bat = Batiment(nom='Principal')
        db.session.add(bat)
        db.session.flush()
        etage = Etage(numero=0, id_batiment=bat.id)
        db.session.add(etage)
        db.session.flush()
    s = Salle(nom=nom, id_etage=etage.id)
    db.session.add(s)
    db.session.commit()
    return jsonify({'id': s.id, 'nom': s.nom}), 201


@admin_bp.delete('/salles/<int:sid>')
@login_required
@role_required('administrateur')
def delete_salle(sid):
    s = db.session.get(Salle, sid)
    if not s:
        return jsonify({'error': 'Salle introuvable'}), 404
    db.session.delete(s)
    db.session.commit()
    return jsonify({'message': 'Supprimée'}), 200
