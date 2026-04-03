from datetime import datetime, timezone
from flask import request, jsonify
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from . import edt_bp
from ..models import db, Classe, Cours, Eleve, Log, Matiere, Parent, Prof, Salle
from ..decorators import is_direction, role_required


def _log(action, target_id=None):
    db.session.add(Log(
        user_id=current_user.id,
        action=action,
        target_type='cours',
        target_id=target_id,
        ip_address=request.remote_addr,
        user_agent=(request.user_agent.string or '')[:255],
        created_at=datetime.now(timezone.utc)
    ))


def _cours_to_dict(c):
    return {
        'id': c.id,
        'debut': c.debut.isoformat(),
        'fin': c.fin.isoformat(),
        'etat': c.etat,
        'matiere': {'id': c.id_matiere, 'nom': c.matiere.nom if c.matiere else None},
        'classe': {
            'id': c.id_classe,
            'niveau': c.classe.niveau if c.classe else None,
            'suffixe': c.classe.suffixe if c.classe else None,
        },
        'prof': {
            'id': c.id_prof,
            'nom': c.prof.user.nom if c.prof and c.prof.user else None,
            'prenom': c.prof.user.prenom if c.prof and c.prof.user else None,
        },
        'salle': {
            'id': c.id_salle,
            'nom': c.salle.nom if c.salle else None,
        },
    }


def _parse_dt(value):
    try:
        if isinstance(value, str):
            value = value.replace('Z', '+00:00')
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _norm_dt(dt):
    return dt.replace(tzinfo=timezone.utc) if dt and dt.tzinfo is None else dt


ALLOWED_ETATS = {'planifié', 'en cours', 'terminé', 'annulé'}


@edt_bp.get('/cours')
@login_required
def list_cours():
    debut_str = request.args.get('debut')
    fin_str = request.args.get('fin')
    classe_id = request.args.get('classe_id', type=int)
    prof_id = request.args.get('prof_id', type=int)

    query = Cours.query.options(
        joinedload(Cours.matiere),
        joinedload(Cours.classe),
        joinedload(Cours.prof).joinedload(Prof.user),
        joinedload(Cours.salle),
    )
    direction = current_user.type == 'employé' and is_direction()

    # scope automatique selon le rôle
    if current_user.type == 'élève':
        eleve = Eleve.query.filter_by(id_user=current_user.id).first()
        if not eleve or not eleve.id_classe:
            return jsonify([]), 200
        query = query.filter(Cours.id_classe == eleve.id_classe)

    elif current_user.type == 'parent':
        parent = Parent.query.filter_by(id_user=current_user.id).first()
        if not parent or not parent.eleve or not parent.eleve.id_classe:
            return jsonify([]), 200
        query = query.filter(Cours.id_classe == parent.eleve.id_classe)

    elif current_user.type == 'employé':
        if direction:
            # direction : filtres libres comme admin
            if classe_id:
                query = query.filter(Cours.id_classe == classe_id)
            if prof_id:
                query = query.filter(Cours.id_prof == prof_id)
        else:
            # prof : uniquement ses cours
            prof = Prof.query.filter_by(id_user=current_user.id).first()
            if not prof:
                return jsonify([]), 200
            query = query.filter(Cours.id_prof == prof.id)

    else:
        # admin : filtres libres
        if classe_id:
            query = query.filter(Cours.id_classe == classe_id)
        if prof_id:
            query = query.filter(Cours.id_prof == prof_id)

    if debut_str:
        debut = _parse_dt(debut_str)
        if not debut:
            return jsonify({'error': 'Format de date invalide pour debut'}), 400
        query = query.filter(Cours.debut >= debut)

    if fin_str:
        fin = _parse_dt(fin_str)
        if not fin:
            return jsonify({'error': 'Format de date invalide pour fin'}), 400
        query = query.filter(Cours.fin <= fin)

    cours = query.order_by(Cours.debut).all()

    if current_user.type == 'administrateur' or direction:
        filters = []
        if classe_id:
            filters.append(f'classe_id={classe_id}')
        if prof_id:
            filters.append(f'prof_id={prof_id}')
        if filters:
            _log(f'cours_listed:{",".join(filters)}')
            db.session.commit()

    return jsonify([_cours_to_dict(c) for c in cours]), 200


@edt_bp.post('/cours')
@login_required
@role_required('administrateur', 'employé')
def create_cours():
    if current_user.type == 'employé' and not is_direction():
        return jsonify({'error': 'Accès refusé'}), 403

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'JSON requis'}), 400

    required = ['id_matiere', 'id_prof', 'id_classe', 'debut', 'fin']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Champs requis : {", ".join(missing)}'}), 400

    debut = _parse_dt(data['debut'])
    fin = _parse_dt(data['fin'])
    if not debut or not fin:
        return jsonify({'error': 'Format de date invalide (ISO 8601 attendu)'}), 400
    if fin <= debut:
        return jsonify({'error': 'fin doit être après debut'}), 400

    if not db.session.get(Matiere, data['id_matiere']):
        return jsonify({'error': 'Matière introuvable'}), 404
    if not db.session.get(Prof, data['id_prof']):
        return jsonify({'error': 'Prof introuvable'}), 404
    if not db.session.get(Classe, data['id_classe']):
        return jsonify({'error': 'Classe introuvable'}), 404

    id_salle = data.get('id_salle')
    if id_salle and not db.session.get(Salle, id_salle):
        return jsonify({'error': 'Salle introuvable'}), 404

    etat = data.get('etat', 'planifié')
    if etat not in ALLOWED_ETATS:
        return jsonify({'error': 'État invalide'}), 400

    cours = Cours(
        id_matiere=data['id_matiere'],
        id_prof=data['id_prof'],
        id_classe=data['id_classe'],
        debut=debut,
        fin=fin,
        etat=etat,
        id_salle=id_salle
    )
    db.session.add(cours)
    db.session.flush()
    _log('cours_created', target_id=cours.id)
    db.session.commit()

    return jsonify(_cours_to_dict(cours)), 201


@edt_bp.patch('/cours/<int:cours_id>')
@login_required
@role_required('administrateur', 'employé')
def update_cours(cours_id):
    if current_user.type == 'employé' and not is_direction():
        return jsonify({'error': 'Accès refusé'}), 403

    cours = db.session.get(Cours, cours_id)
    if cours is None:
        return jsonify({'error': 'Cours introuvable'}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'JSON requis'}), 400

    changes = []

    if 'debut' in data or 'fin' in data:
        debut = _parse_dt(data['debut']) if 'debut' in data else _norm_dt(cours.debut)
        fin = _parse_dt(data['fin']) if 'fin' in data else _norm_dt(cours.fin)
        if not debut or not fin:
            return jsonify({'error': 'Format de date invalide (ISO 8601 attendu)'}), 400
        if fin <= debut:
            return jsonify({'error': 'fin doit être après debut'}), 400
        cours.debut = debut
        cours.fin = fin
        changes.append('horaires')

    if 'id_matiere' in data:
        if not db.session.get(Matiere, data['id_matiere']):
            return jsonify({'error': 'Matière introuvable'}), 404
        cours.id_matiere = data['id_matiere']
        changes.append('matiere')

    if 'id_prof' in data:
        if not db.session.get(Prof, data['id_prof']):
            return jsonify({'error': 'Prof introuvable'}), 404
        cours.id_prof = data['id_prof']
        changes.append('prof')

    if 'id_classe' in data:
        if not db.session.get(Classe, data['id_classe']):
            return jsonify({'error': 'Classe introuvable'}), 404
        cours.id_classe = data['id_classe']
        changes.append('classe')

    if 'id_salle' in data:
        id_salle = data['id_salle']
        if id_salle and not db.session.get(Salle, id_salle):
            return jsonify({'error': 'Salle introuvable'}), 404
        cours.id_salle = id_salle
        changes.append('salle')

    if 'etat' in data:
        if data['etat'] not in ALLOWED_ETATS:
            return jsonify({'error': 'État invalide'}), 400
        cours.etat = data['etat']
        changes.append('etat')

    if not changes:
        return jsonify({'error': 'Aucun champ modifiable fourni'}), 400

    _log(f'cours_updated:{",".join(changes)}', target_id=cours.id)
    db.session.commit()

    return jsonify(_cours_to_dict(cours)), 200


@edt_bp.delete('/cours/<int:cours_id>')
@login_required
@role_required('administrateur', 'employé')
def delete_cours(cours_id):
    if current_user.type == 'employé' and not is_direction():
        return jsonify({'error': 'Accès refusé'}), 403

    cours = db.session.get(Cours, cours_id)
    if cours is None:
        return jsonify({'error': 'Cours introuvable'}), 404

    _log('cours_deleted', target_id=cours.id)
    db.session.delete(cours)
    db.session.commit()

    return jsonify({'message': 'Cours supprimé'}), 200
