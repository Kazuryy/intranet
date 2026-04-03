from flask import jsonify, request
from app.models import db, User, Communication, Direction, SessionAuth
from datetime import datetime
from . import messagesbp
from markupsafe import escape


CIBLES_VALIDES = {'parent', 'élève', 'prof', 'tous', 'classe'}

# Mapping type User → cibles visibles
CIBLES_PAR_TYPE = {
    'élève':          ['élève', 'tous', 'classe'],
    'parent':         ['parent', 'tous'],
    'employé':        ['prof', 'tous'],
    'administrateur': ['parent', 'élève', 'prof', 'tous', 'classe'],
}


def get_user_from_suid(suid):
    if not suid:
        return None
    s = SessionAuth.query.filter_by(suid=suid).first()
    if not s or s.expire_le < datetime.now():
        return None
    return User.query.get(s.id_user)


def is_direction(user):
    return user and Direction.query.filter_by(id_user=user.id).first() is not None


@messagesbp.route('', methods=['GET'])
def get_messages():
    user = get_user_from_suid(request.args.get('suid'))
    if not user:
        return jsonify(error="Authentification requise"), 401

    cibles = CIBLES_PAR_TYPE.get(user.type, ['tous'])
    msgs = Communication.query.filter(Communication.cible.in_(cibles)).all()
    return jsonify([{
        'id':      m.id,
        'objet':   m.objet,
        'contenu': m.contenu,
        'cible':   m.cible,
    } for m in msgs]), 200


@messagesbp.route('/<int:msg_id>', methods=['GET'])
def get_message(msg_id):
    user = get_user_from_suid(request.args.get('suid'))
    if not user:
        return jsonify(error="Authentification requise"), 401

    msg = Communication.query.get(msg_id)
    if not msg:
        return jsonify(error="Message introuvable"), 404

    cibles = CIBLES_PAR_TYPE.get(user.type, ['tous'])
    if msg.cible not in cibles:
        return jsonify(error="Accès interdit"), 403

    return jsonify({
        'id':      msg.id,
        'objet':   msg.objet,
        'contenu': msg.contenu,
        'cible':   msg.cible,
    }), 200


@messagesbp.route('', methods=['POST'])
def publier_message():
    user = get_user_from_suid(request.args.get('suid'))
    if not user:
        return jsonify(error="Authentification requise"), 401
    if not is_direction(user):
        return jsonify(error="Réservé à la direction"), 403

    data = request.get_json() or {}
    objet   = str(escape(data.get('objet',   '').strip()))
    contenu = str(escape(data.get('contenu', '').strip()))
    cible   = data.get('cible',   '').strip()

    if not objet or not contenu or not cible:
        return jsonify(error="Champs objet, contenu et cible requis"), 400
    if cible not in CIBLES_VALIDES:
        return jsonify(error=f"Cible invalide. Valeurs: {CIBLES_VALIDES}"), 400

    msg = Communication(
        id_user=user.id,     # ← id_user direct
        cible=cible,
        objet=objet,
        contenu=contenu
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify(id=msg.id, objet=msg.objet), 201


@messagesbp.route('/<int:msg_id>', methods=['PATCH'])
def modifier_message(msg_id):
    user = get_user_from_suid(request.args.get('suid'))
    if not user:
        return jsonify(error="Authentification requise"), 401
    if not is_direction(user):
        return jsonify(error="Réservé à la direction"), 403

    msg = Communication.query.get(msg_id)
    if not msg:
        return jsonify(error="Message introuvable"), 404

    data = request.get_json() or {}
    if not any(k in data for k in ('objet', 'contenu', 'cible')):
        return jsonify(error="Aucun champ valide fourni"), 400

    if 'objet'   in data: msg.objet   = data['objet'].strip()
    if 'contenu' in data: msg.contenu = data['contenu'].strip()
    if 'cible'   in data:
        if data['cible'] not in CIBLES_VALIDES:
            return jsonify(error="Cible invalide"), 400
        msg.cible = data['cible']

    db.session.commit()
    return jsonify(id=msg.id, objet=msg.objet, contenu=msg.contenu), 200


@messagesbp.route('/<int:msg_id>', methods=['DELETE'])
def supprimer_message(msg_id):
    user = get_user_from_suid(request.args.get('suid'))
    if not user:
        return jsonify(error="Authentification requise"), 401
    if not is_direction(user):
        return jsonify(error="Réservé à la direction"), 403

    msg = Communication.query.get(msg_id)
    if not msg:
        return jsonify(error="Message introuvable"), 404

    db.session.delete(msg)
    db.session.commit()
    return jsonify(message="Message supprimé"), 200


# ── Messages automatiques ─────────────────────────────────────────────────────

def _get_dir_user_id():
    """Récupère l'id_user d'un membre de la direction."""
    d = Direction.query.first()
    return d.id_user if d else None


def message_auto_cours_annule(cours):
    uid = _get_dir_user_id()
    if not uid:
        return
    db.session.add(Communication(
        id_user=uid,
        cible="tous",
        objet="Cours annulé",
        contenu=f"Le cours du {cours.debut.strftime('%d/%m/%Y à %H:%M')} a été annulé."
    ))


def message_auto_cours_deplace(cours, nouvelle_date):
    uid = _get_dir_user_id()
    if not uid: return
    db.session.add(Communication(
        id_user=uid,
        cible="tous",
        objet="Cours déplacé",
        contenu=f"Le cours a été déplacé au {nouvelle_date}."
    ))


def message_auto_evenement_cree(evenement):
    uid = _get_dir_user_id()
    if not uid: return
    db.session.add(Communication(
        id_user=uid,
        cible="tous",
        objet=f"Événement : {evenement.titre}",
        contenu=(
            f"{evenement.description or ''}\n"
            f"📅 {evenement.date_debut.strftime('%d/%m/%Y à %H:%M')}"
            f"{f' — {evenement.lieu}' if evenement.lieu else ''}"
        )
    ))