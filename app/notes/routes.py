from datetime import datetime
from flask import jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import func, extract
from . import notes_bp
from ..models import db, Classe, Cours, Eleve, Evaluation, Matiere, Parent, Prof, User


# Palette de couleurs stables par matiere (index = id_matiere % len)
COULEURS = [
    '#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6',
    '#8b5cf6', '#ef4444', '#14b8a6', '#f97316', '#06b6d4',
]

TRIMESTRES = {
    1: (9, 11),   # septembre - novembre
    2: (12, 2),   # decembre - fevrier
    3: (3, 6),    # mars - juin
}


def _get_eleve_id():
    """Retourne l'id eleve selon le role de l'utilisateur connecte."""
    if current_user.type == 'élève':
        eleve = Eleve.query.filter_by(id_user=current_user.id).first()
        return eleve.id if eleve else None
    if current_user.type == 'parent':
        parent = Parent.query.filter_by(id_user=current_user.id).first()
        return parent.id_eleve if parent else None
    return None


def _stats_classe(id_matiere, id_classe):
    """
    Calcule moyenne, note max et note min de la classe
    pour une matiere donnee.
    """
    subq = (
        db.session.query(Evaluation.note)
        .join(Eleve, Eleve.id == Evaluation.id_eleve)
        .filter(
            Evaluation.id_matiere == id_matiere,
            Eleve.id_classe == id_classe,
        )
        .subquery()
    )
    row = db.session.query(
        func.avg(subq.c.note),
        func.max(subq.c.note),
        func.min(subq.c.note),
    ).one()
    avg, maximum, minimum = row
    return (
        round(float(avg), 2) if avg is not None else None,
        float(maximum) if maximum is not None else None,
        float(minimum) if minimum is not None else None,
    )


def _eval_to_dict(ev, matiere_nom, id_classe):
    moyenne, plus_haute, plus_basse = _stats_classe(ev.id_matiere, id_classe)
    couleur = COULEURS[ev.id_matiere % len(COULEURS)]
    return {
        'id': ev.id,
        'matiere': matiere_nom,
        'note': float(ev.note),
        'note_max': float(ev.note_max),
        'coefficient': ev.coefficient,
        'date_evaluation': ev.date.date().isoformat(),
        'moyenne_classe': moyenne,
        'note_plus_haute': plus_haute,
        'note_plus_basse': plus_basse,
        'couleur': couleur,
    }


def _filter_trimestre(query, trimestre):
    debut_mois, fin_mois = TRIMESTRES[trimestre]
    month = extract('month', Evaluation.date)
    if debut_mois <= fin_mois:
        return query.filter(month >= debut_mois, month <= fin_mois)
    # cas trimestre 2 : decembre (12) -> fevrier (2)
    return query.filter(db.or_(month >= debut_mois, month <= fin_mois))


@notes_bp.route('/api/notes')
@login_required
def get_notes():
    if current_user.type not in ('élève', 'parent', 'administrateur'):
        return jsonify({'error': 'Acces interdit'}), 403

    eleve_id = _get_eleve_id()
    if eleve_id is None:
        return jsonify({'error': 'Eleve introuvable'}), 404

    eleve = db.session.get(Eleve, eleve_id)
    rows = (
        db.session.query(Evaluation, Matiere.nom)
        .join(Matiere, Matiere.id == Evaluation.id_matiere)
        .filter(Evaluation.id_eleve == eleve_id)
        .order_by(Evaluation.date.desc())
        .all()
    )
    return jsonify([_eval_to_dict(ev, nom, eleve.id_classe) for ev, nom in rows])


@notes_bp.route('/api/notes/trimestre/<int:trimestre>')
@login_required
def get_notes_trimestre(trimestre):
    if current_user.type not in ('élève', 'parent', 'administrateur'):
        return jsonify({'error': 'Acces interdit'}), 403

    if trimestre not in TRIMESTRES:
        return jsonify({'error': 'Trimestre invalide (1, 2 ou 3)'}), 400

    eleve_id = _get_eleve_id()
    if eleve_id is None:
        return jsonify({'error': 'Eleve introuvable'}), 404

    eleve = db.session.get(Eleve, eleve_id)
    q = (
        db.session.query(Evaluation, Matiere.nom)
        .join(Matiere, Matiere.id == Evaluation.id_matiere)
        .filter(Evaluation.id_eleve == eleve_id)
        .order_by(Evaluation.date.desc())
    )
    q = _filter_trimestre(q, trimestre)
    return jsonify([_eval_to_dict(ev, nom, eleve.id_classe) for ev, nom in q.all()])


@notes_bp.route('/api/notes/eleve/<int:eleve_id>')
@login_required
def get_notes_eleve(eleve_id):
    """Admin ou prof : voir les notes d'un eleve specifique."""
    if current_user.type not in ('employé', 'administrateur'):
        return jsonify({'error': 'Acces interdit'}), 403

    eleve = db.session.get(Eleve, eleve_id)
    if not eleve:
        return jsonify({'error': 'Eleve introuvable'}), 404

    if current_user.type == 'employé':
        prof = _get_prof()
        if not prof:
            return jsonify({'error': 'Profil prof introuvable'}), 404
        # Le prof doit enseigner au moins une matiere dans la classe de cet eleve
        cours_existe = (
            db.session.query(Cours)
            .filter_by(id_prof=prof.id, id_classe=eleve.id_classe)
            .first()
        )
        if not cours_existe:
            return jsonify({'error': 'Acces interdit a cet eleve'}), 403

    q = (
        db.session.query(Evaluation, Matiere.nom)
        .join(Matiere, Matiere.id == Evaluation.id_matiere)
        .filter(Evaluation.id_eleve == eleve_id)
        .order_by(Evaluation.date.desc())
    )
    trimestre = request.args.get('trimestre', type=int)
    if trimestre and trimestre in TRIMESTRES:
        q = _filter_trimestre(q, trimestre)
    return jsonify([_eval_to_dict(ev, nom, eleve.id_classe) for ev, nom in q.all()])


@notes_bp.route('/api/notes/evaluations')
@login_required
def get_evaluations_classe():
    """
    Prof/admin : liste les evaluations d'une (classe, matiere).
    Params : classe_id, matiere_id
    """
    if current_user.type not in ('employé', 'administrateur'):
        return jsonify({'error': 'Acces interdit'}), 403

    id_classe = request.args.get('classe_id', type=int)
    id_matiere = request.args.get('matiere_id', type=int)
    if not id_classe or not id_matiere:
        return jsonify({'error': 'Paramètres classe_id et matiere_id requis'}), 400

    if current_user.type == 'employé':
        prof = _get_prof()
        if not prof or not _prof_can_access(prof, id_classe, id_matiere):
            return jsonify({'error': 'Acces interdit'}), 403

    rows = (
        db.session.query(Evaluation, User.nom, User.prenom)
        .join(Eleve, Eleve.id == Evaluation.id_eleve)
        .join(User, User.id == Eleve.id_user)
        .filter(
            Evaluation.id_matiere == id_matiere,
            Eleve.id_classe == id_classe,
        )
        .order_by(Evaluation.date.desc(), User.nom)
        .all()
    )
    return jsonify([{
        'id': ev.id,
        'id_eleve': ev.id_eleve,
        'eleve_nom': nom,
        'eleve_prenom': prenom,
        'note': float(ev.note),
        'note_max': float(ev.note_max),
        'coefficient': ev.coefficient,
        'date': ev.date.date().isoformat(),
    } for ev, nom, prenom in rows])


@notes_bp.route('/api/couleurs-matieres')
@login_required
def get_couleurs():
    matieres = Matiere.query.all()
    return jsonify({
        m.nom: COULEURS[m.id % len(COULEURS)]
        for m in matieres
    })


# ─── Helpers prof ─────────────────────────────────────────────────────────────

def _get_prof():
    return Prof.query.filter_by(id_user=current_user.id).first()


def _prof_can_access(prof, id_classe, id_matiere):
    """Verifie que le prof enseigne cette matiere dans cette classe."""
    return (
        db.session.query(Cours)
        .filter_by(id_prof=prof.id, id_classe=id_classe, id_matiere=id_matiere)
        .first() is not None
    )


# ─── GET /api/notes/classes ───────────────────────────────────────────────────

@notes_bp.route('/api/notes/classes')
@login_required
def get_classes_prof():
    """
    Retourne les couples (classe, matiere) que le prof connecte enseigne.
    Admin : toutes les classes x toutes les matieres.
    """
    if current_user.type == 'administrateur':
        classes = Classe.query.all()
        matieres = Matiere.query.all()
        return jsonify({
            'classes': [{'id': c.id, 'nom': f"{c.niveau}{c.suffixe} ({c.annee})"} for c in classes],
            'matieres': [{'id': m.id, 'nom': m.nom} for m in matieres],
        })

    if current_user.type != 'employé':
        return jsonify({'error': 'Acces interdit'}), 403

    prof = _get_prof()
    if not prof:
        return jsonify({'error': 'Profil prof introuvable'}), 404

    # Combinaisons (classe, matiere) extraites des cours du prof
    rows = (
        db.session.query(Classe, Matiere)
        .join(Cours, Cours.id_classe == Classe.id)
        .join(Matiere, Matiere.id == Cours.id_matiere)
        .filter(Cours.id_prof == prof.id)
        .distinct()
        .all()
    )
    classes_vues = {}
    matieres_vues = {}
    combinaisons = []
    for classe, matiere in rows:
        classes_vues[classe.id] = {'id': classe.id, 'nom': f"{classe.niveau}{classe.suffixe} ({classe.annee})"}
        matieres_vues[matiere.id] = {'id': matiere.id, 'nom': matiere.nom}
        combinaisons.append({'id_classe': classe.id, 'id_matiere': matiere.id})

    return jsonify({
        'classes': list(classes_vues.values()),
        'matieres': list(matieres_vues.values()),
        'combinaisons': combinaisons,
    })


# ─── GET /api/notes/eleves/<classe_id> ────────────────────────────────────────

@notes_bp.route('/api/notes/eleves/<int:classe_id>')
@login_required
def get_eleves_classe(classe_id):
    """Liste les eleves d'une classe (pour saisie de notes)."""
    if current_user.type not in ('employé', 'administrateur'):
        return jsonify({'error': 'Acces interdit'}), 403

    if current_user.type == 'employé':
        prof = _get_prof()
        if not prof:
            return jsonify({'error': 'Profil prof introuvable'}), 404

    eleves = (
        db.session.query(Eleve, User)
        .join(User, User.id == Eleve.id_user)
        .filter(Eleve.id_classe == classe_id)
        .order_by(User.nom, User.prenom)
        .all()
    )
    return jsonify([
        {'id': e.id, 'nom': u.nom, 'prenom': u.prenom}
        for e, u in eleves
    ])


# ─── POST /api/notes/evaluations ──────────────────────────────────────────────

@notes_bp.route('/api/notes/evaluations', methods=['POST'])
@login_required
def create_evaluations():
    """
    Cree des evaluations en batch pour une classe.
    Body : {
        id_classe, id_matiere, date, note_max, coefficient,
        notes: [{id_eleve, note}]
    }
    """
    if current_user.type not in ('employé', 'administrateur'):
        return jsonify({'error': 'Acces interdit'}), 403

    data = request.get_json(silent=True) or {}
    id_classe = data.get('id_classe')
    id_matiere = data.get('id_matiere')
    notes_list = data.get('notes', [])
    note_max = data.get('note_max', 20)
    coefficient = data.get('coefficient', 1)
    date_str = data.get('date')

    if not all([id_classe, id_matiere, date_str, notes_list]):
        return jsonify({'error': 'Champs manquants : id_classe, id_matiere, date, notes'}), 400

    try:
        date = datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'Format de date invalide (ISO 8601 attendu)'}), 400

    if current_user.type == 'employé':
        prof = _get_prof()
        if not prof or not _prof_can_access(prof, id_classe, id_matiere):
            return jsonify({'error': 'Acces interdit a cette classe ou matiere'}), 403

    # Verification que tous les eleves appartiennent bien a la classe
    ids_eleves = [n['id_eleve'] for n in notes_list if 'id_eleve' in n]
    eleves_valides = {
        e.id for e in Eleve.query.filter(
            Eleve.id.in_(ids_eleves), Eleve.id_classe == id_classe
        ).all()
    }

    created = []
    for entry in notes_list:
        id_eleve = entry.get('id_eleve')
        note = entry.get('note')
        if id_eleve not in eleves_valides or note is None:
            continue
        ev = Evaluation(
            id_eleve=id_eleve,
            id_matiere=id_matiere,
            note=note,
            note_max=note_max,
            coefficient=coefficient,
            date=date,
        )
        db.session.add(ev)
        created.append(id_eleve)

    db.session.commit()
    return jsonify({'created': len(created), 'eleves': created}), 201


# ─── PUT /api/notes/evaluations/<eval_id> ─────────────────────────────────────

@notes_bp.route('/api/notes/evaluations/<int:eval_id>', methods=['PUT'])
@login_required
def update_evaluation(eval_id):
    """Modifie la note d'un eleve."""
    if current_user.type not in ('employé', 'administrateur'):
        return jsonify({'error': 'Acces interdit'}), 403

    ev = db.session.get(Evaluation, eval_id)
    if not ev:
        return jsonify({'error': 'Evaluation introuvable'}), 404

    if current_user.type == 'employé':
        prof = _get_prof()
        eleve = db.session.get(Eleve, ev.id_eleve)
        if not prof or not eleve or not _prof_can_access(prof, eleve.id_classe, ev.id_matiere):
            return jsonify({'error': 'Acces interdit'}), 403

    data = request.get_json(silent=True) or {}
    if 'note' in data:
        ev.note = data['note']
    if 'note_max' in data:
        ev.note_max = data['note_max']
    if 'coefficient' in data:
        ev.coefficient = data['coefficient']

    db.session.commit()
    return jsonify({'id': ev.id, 'note': float(ev.note)})


# ─── DELETE /api/notes/evaluations/<eval_id> ──────────────────────────────────

@notes_bp.route('/api/notes/evaluations/<int:eval_id>', methods=['DELETE'])
@login_required
def delete_evaluation(eval_id):
    """Supprime une evaluation."""
    if current_user.type not in ('employé', 'administrateur'):
        return jsonify({'error': 'Acces interdit'}), 403

    ev = db.session.get(Evaluation, eval_id)
    if not ev:
        return jsonify({'error': 'Evaluation introuvable'}), 404

    if current_user.type == 'employé':
        prof = _get_prof()
        eleve = db.session.get(Eleve, ev.id_eleve)
        if not prof or not eleve or not _prof_can_access(prof, eleve.id_classe, ev.id_matiere):
            return jsonify({'error': 'Acces interdit'}), 403

    db.session.delete(ev)
    db.session.commit()
    return jsonify({'deleted': eval_id})
