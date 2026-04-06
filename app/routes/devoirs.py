from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime
import bleach

from ..models import db, Prof, Matiere, Classe, Eleve, Devoir, Cours


def sanitize(text):
    return bleach.clean(text, tags=[], strip=True)


TYPES_VALIDES = ['exercice', 'controle', 'expose', 'projet', 'soutenance', 'autre']

devoirs_bp = Blueprint('devoirs', __name__, url_prefix='/api/devoirs')


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_prof():
    if current_user.type != 'employé':
        return None
    return Prof.query.filter_by(id_user=current_user.id).first()


def _require_prof():
    """Retourne (prof, None) ou (None, réponse 403)."""
    prof = _get_prof()
    if not prof:
        return None, (jsonify({'error': 'Acces reserve aux professeurs'}), 403)
    return prof, None


def _prof_enseigne(prof, id_classe, id_matiere):
    """Vérifie qu'un Cours lie ce prof à cette classe et matière."""
    return (
        db.session.query(Cours)
        .filter_by(id_prof=prof.id, id_classe=id_classe, id_matiere=id_matiere)
        .first() is not None
    )


def _serialize(d, m, c):
    dl = d.date_limite
    if isinstance(dl, datetime):
        dl = dl.date()
    return {
        'id':          d.id,
        'type':        d.type,
        'date_limite': str(dl),
        'consigne':    d.consigne,
        'matiere':     m.nom,
        'niveau':      c.niveau,
        'suffixe':     c.suffixe,
    }


def _parse_date(value):
    if isinstance(value, str):
        return datetime.combine(
            datetime.strptime(value, '%Y-%m-%d').date(),
            datetime.min.time()
        )
    return value


# ─── Lecture ──────────────────────────────────────────────────────────────────

@devoirs_bp.route('/', methods=['GET'])
@login_required
def get_devoirs():
    q = (
        db.session.query(Devoir, Matiere, Classe)
        .join(Matiere, Devoir.id_matiere == Matiere.id)
        .join(Classe, Devoir.id_classe == Classe.id)
    )

    if current_user.type == 'employé':
        prof = _get_prof()
        if prof:
            q = q.filter(Devoir.id_prof == prof.id)
    elif current_user.type == 'élève':
        q = (
            q.join(Eleve, Eleve.id_classe == Devoir.id_classe)
            .filter(Eleve.id_user == current_user.id)
        )

    rows = q.order_by(Devoir.date_limite.desc()).all()
    return jsonify([_serialize(d, m, c) for d, m, c in rows]), 200


@devoirs_bp.route('/<int:id_devoir>', methods=['GET'])
@login_required
def get_devoir(id_devoir):
    q = (
        db.session.query(Devoir, Matiere, Classe)
        .join(Matiere, Devoir.id_matiere == Matiere.id)
        .join(Classe, Devoir.id_classe == Classe.id)
        .filter(Devoir.id == id_devoir)
    )

    if current_user.type == 'employé':
        prof = _get_prof()
        if prof:
            q = q.filter(Devoir.id_prof == prof.id)
    elif current_user.type == 'élève':
        q = (
            q.join(Eleve, Eleve.id_classe == Devoir.id_classe)
            .filter(Eleve.id_user == current_user.id)
        )

    row = q.first()
    if not row:
        return jsonify({'error': 'Devoir introuvable ou acces refuse'}), 404
    d, m, c = row
    return jsonify(_serialize(d, m, c)), 200


@devoirs_bp.route('/tri/a_venir', methods=['GET'])
@login_required
def get_devoirs_a_venir():
    aujourd_hui = datetime.combine(date.today(), datetime.min.time())

    q = (
        db.session.query(Devoir, Matiere, Classe)
        .join(Matiere, Devoir.id_matiere == Matiere.id)
        .join(Classe, Devoir.id_classe == Classe.id)
        .filter(Devoir.date_limite > aujourd_hui)
    )

    if current_user.type == 'employé':
        prof = _get_prof()
        if prof:
            q = q.filter(Devoir.id_prof == prof.id)
    elif current_user.type == 'élève':
        q = (
            q.join(Eleve, Eleve.id_classe == Devoir.id_classe)
            .filter(Eleve.id_user == current_user.id)
        )

    rows = q.order_by(Devoir.date_limite.asc()).all()
    return jsonify([_serialize(d, m, c) for d, m, c in rows]), 200


# ─── Écriture ─────────────────────────────────────────────────────────────────

@devoirs_bp.route('/creer', methods=['POST'])
@login_required
def create_devoir():
    prof, err = _require_prof()
    if err:
        return err

    data = request.get_json(silent=True) or {}

    for field in ['id_classe', 'id_matiere', 'type', 'date_limite', 'consigne']:
        if field not in data:
            return jsonify(
                {'error': f'Champ manquant : {field}', 'consigne': 'requis'}
            ), 400

    if data['type'] not in TYPES_VALIDES:
        return jsonify(
            {'error': f"Type invalide. Valeurs acceptees : {TYPES_VALIDES}"}
        ), 400

    id_classe = data['id_classe']
    id_matiere = data['id_matiere']
    if not _prof_enseigne(prof, id_classe, id_matiere):
        return jsonify(
            {'error': 'Le prof n\'enseigne pas cette matiere dans cette classe'}
        ), 403

    try:
        dl = _parse_date(data['date_limite'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Format date invalide (YYYY-MM-DD attendu)'}), 400

    d = Devoir(
        id_classe=id_classe,
        id_matiere=id_matiere,
        id_prof=prof.id,
        type=sanitize(data['type']),
        date_limite=dl,
        consigne=sanitize(data['consigne']),
    )
    db.session.add(d)
    db.session.commit()
    return jsonify({'message': 'Devoir cree', 'id': d.id}), 201


@devoirs_bp.route('/modifier/<int:id_devoir>', methods=['PUT'])
@login_required
def update_devoir(id_devoir):
    prof, err = _require_prof()
    if err:
        return err

    d = Devoir.query.filter_by(id=id_devoir, id_prof=prof.id).first()
    if not d:
        return jsonify({'error': 'Devoir introuvable ou acces refuse'}), 403

    data = request.get_json(silent=True) or {}
    champs = ['id_classe', 'id_matiere', 'type', 'date_limite', 'consigne']
    updates = {k: data[k] for k in champs if k in data}
    if not updates:
        return jsonify({'error': 'Aucun champ a modifier'}), 400

    for k, v in updates.items():
        if k in ('consigne', 'type'):
            v = sanitize(v)
        elif k == 'date_limite':
            try:
                v = _parse_date(v)
            except (ValueError, TypeError):
                return jsonify(
                    {'error': 'Format date invalide (YYYY-MM-DD attendu)'}
                ), 400
        setattr(d, k, v)

    db.session.commit()
    return jsonify({'message': 'Devoir mis a jour'}), 200


@devoirs_bp.route('/supprimer/<int:id_devoir>', methods=['DELETE'])
@login_required
def delete_devoir(id_devoir):
    prof, err = _require_prof()
    if err:
        return err

    d = Devoir.query.filter_by(id=id_devoir, id_prof=prof.id).first()
    if not d:
        return jsonify({'error': 'Devoir introuvable ou acces refuse'}), 403

    db.session.delete(d)
    db.session.commit()
    return jsonify({'message': 'Devoir supprime'}), 200


# ─── Formulaires ──────────────────────────────────────────────────────────────

@devoirs_bp.route('/tri/classes', methods=['GET'])
@login_required
def get_classes_prof():
    prof, err = _require_prof()
    if err:
        return err

    classes = (
        db.session.query(Classe)
        .join(Cours, Cours.id_classe == Classe.id)
        .filter(Cours.id_prof == prof.id)
        .distinct()
        .all()
    )
    return jsonify(
        [{'id': c.id, 'niveau': c.niveau, 'suffixe': c.suffixe} for c in classes]
    ), 200


@devoirs_bp.route('/tri/matieres', methods=['GET'])
@login_required
def get_matieres_prof():
    prof, err = _require_prof()
    if err:
        return err

    return jsonify(
        [{'id': m.id, 'nom': m.nom} for m in prof.matieres]
    ), 200
