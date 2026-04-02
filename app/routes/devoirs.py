from flask import Blueprint, request, jsonify
from ..models import db, User, Prof, Matiere, Classe, Eleve, Devoir, Cours, Direction
from ..models import SessionAuth as DBSession
from datetime import date, datetime
import bleach


def sanitize(text):
    return bleach.clean(text, tags=[], strip=True)


ROLES_LECTURE  = ['eleve', 'prof', 'direction', 'cpe', 'parent', 'administrateur']
ROLES_ECRITURE = ['prof']

TYPES_VALIDES = ['exercice', 'controle', 'expose', 'projet', 'soutenance', 'autre']


# ─── Auth ─────────────────────────────────────────────────────────────────────

_NORM = {'élève': 'eleve', 'employé': 'employe'}

def get_user_from_suid(suid):
    session = DBSession.query.filter(
        DBSession.suid == suid,
        DBSession.expire_le > datetime.now()
    ).first()
    if not session:
        return None

    user = db.session.get(User, session.id_user)
    if not user:
        return None

    role = _NORM.get(user.type, user.type)
    result = {'ID': user.id, 'role': role, 'ID_Prof': None}

    if role in ('employe', 'prof'):
        prof = Prof.query.filter_by(id_user=user.id).first()
        if prof:
            result['role']    = 'prof'
            result['ID_Prof'] = prof.id
        else:
            direction = Direction.query.filter_by(id_user=user.id).first()
            if direction:
                result['role'] = 'direction'

    return result

def verif_role(suid, roles_autorises):
    if not suid:
        return None, (jsonify({'error': 'SUID manquant'}), 401)
    user = get_user_from_suid(suid)
    if not user:
        return None, (jsonify({'error': 'Session invalide ou expiree'}), 401)
    if user['role'] not in roles_autorises:
        return None, (jsonify({'error': 'Acces non autorise'}), 403)
    return user, None


# ─── Blueprint ────────────────────────────────────────────────────────────────

devoirs_bp = Blueprint('devoirs', __name__, url_prefix='/api/devoirs')


def _serialize(d, m, c):
    dl = d.date_limite
    if isinstance(dl, datetime):
        dl = dl.date()
    return {
        'ID':          d.id,
        'Type':        d.type,
        'Date_Limite': str(dl),
        'Consigne':    d.consigne,
        'Matiere':     m.nom,
        'Niveau':      c.niveau,
        'Suffixe':     c.suffixe,
    }


# ─── Lecture ──────────────────────────────────────────────────────────────────

@devoirs_bp.route('/', methods=['GET'])
def get_devoirs():
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_LECTURE)
    if err:
        return err

    q = (db.session.query(Devoir, Matiere, Classe)
         .join(Matiere, Devoir.id_matiere == Matiere.id)
         .join(Classe,  Devoir.id_classe  == Classe.id))

    if user['role'] == 'prof':
        q = q.filter(Devoir.id_prof == user['ID_Prof'])
    elif user['role'] == 'eleve':
        q = (q.join(Eleve, Eleve.id_classe == Devoir.id_classe)
              .filter(Eleve.id_user == user['ID']))

    rows = q.order_by(Devoir.date_limite.desc()).all()
    return jsonify([_serialize(d, m, c) for d, m, c in rows]), 200


@devoirs_bp.route('/<int:id_devoir>', methods=['GET'])
def get_devoir(id_devoir):
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_LECTURE)
    if err:
        return err

    q = (db.session.query(Devoir, Matiere, Classe)
         .join(Matiere, Devoir.id_matiere == Matiere.id)
         .join(Classe,  Devoir.id_classe  == Classe.id)
         .filter(Devoir.id == id_devoir))

    if user['role'] == 'prof':
        q = q.filter(Devoir.id_prof == user['ID_Prof'])
    elif user['role'] == 'eleve':
        q = (q.join(Eleve, Eleve.id_classe == Devoir.id_classe)
              .filter(Eleve.id_user == user['ID']))

    row = q.first()
    if not row:
        return jsonify({'error': 'Devoir introuvable ou acces refuse'}), 404
    d, m, c = row
    return jsonify(_serialize(d, m, c)), 200


@devoirs_bp.route('/tri/a_venir', methods=['GET'])
def get_devoirs_a_venir():
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_LECTURE)
    if err:
        return err

    aujourd_hui = datetime.combine(date.today(), datetime.min.time())

    q = (db.session.query(Devoir, Matiere, Classe)
         .join(Matiere, Devoir.id_matiere == Matiere.id)
         .join(Classe,  Devoir.id_classe  == Classe.id)
         .filter(Devoir.date_limite > aujourd_hui))

    if user['role'] == 'prof':
        q = q.filter(Devoir.id_prof == user['ID_Prof'])
    elif user['role'] == 'eleve':
        q = (q.join(Eleve, Eleve.id_classe == Devoir.id_classe)
              .filter(Eleve.id_user == user['ID']))

    rows = q.order_by(Devoir.date_limite.asc()).all()
    return jsonify([_serialize(d, m, c) for d, m, c in rows]), 200


# ─── Écriture ─────────────────────────────────────────────────────────────────

@devoirs_bp.route('/creer', methods=['POST'])
def create_devoir():
    data = request.get_json() or {}
    user, err = verif_role(data.get('suid'), ROLES_ECRITURE)
    if err:
        return err

    for field in ['id_classe', 'id_matiere', 'type', 'date_limite', 'consigne']:
        if field not in data:
            return jsonify({'error': f'Champ manquant : {field}', 'consigne': 'requis'}), 400

    if data['type'] not in TYPES_VALIDES:
        return jsonify({'error': f"Type invalide. Valeurs acceptees : {TYPES_VALIDES}"}), 400

    consigne = sanitize(data['consigne'])
    type_    = sanitize(data['type'])

    dl = data['date_limite']
    if isinstance(dl, str):
        dl = datetime.combine(datetime.strptime(dl, '%Y-%m-%d').date(), datetime.min.time())

    d = Devoir(
        id_classe=data['id_classe'],
        id_matiere=data['id_matiere'],
        id_prof=user['ID_Prof'],
        type=type_,
        date_limite=dl,
        consigne=consigne,
    )
    db.session.add(d)
    db.session.commit()
    return jsonify({'message': 'Devoir cree', 'id': d.id}), 201


@devoirs_bp.route('/modifier/<int:id_devoir>', methods=['PUT'])
def update_devoir(id_devoir):
    data = request.get_json() or {}
    user, err = verif_role(data.get('suid'), ROLES_ECRITURE)
    if err:
        return err

    d = Devoir.query.filter_by(id=id_devoir, id_prof=user['ID_Prof']).first()
    if not d:
        return jsonify({'error': 'Devoir introuvable ou acces refuse'}), 403

    champs = ['id_classe', 'id_matiere', 'type', 'date_limite', 'consigne']
    updates = {k: data[k] for k in champs if k in data}
    if not updates:
        return jsonify({'error': 'Aucun champ a modifier'}), 400

    for k, v in updates.items():
        if k in ('consigne', 'type'):
            v = sanitize(v)
        setattr(d, k, v)

    db.session.commit()
    return jsonify({'message': 'Devoir mis a jour'}), 200


@devoirs_bp.route('/supprimer/<int:id_devoir>', methods=['DELETE'])
def delete_devoir(id_devoir):
    # suid accepté en JSON body OU en query param
    data = request.get_json(silent=True) or {}
    suid = data.get('suid') or request.args.get('suid')
    user, err = verif_role(suid, ROLES_ECRITURE)
    if err:
        return err

    d = Devoir.query.filter_by(id=id_devoir, id_prof=user['ID_Prof']).first()
    if not d:
        return jsonify({'error': 'Devoir introuvable ou acces refuse'}), 403

    db.session.delete(d)
    db.session.commit()
    return jsonify({'message': 'Devoir supprime'}), 200


# ─── Formulaires ──────────────────────────────────────────────────────────────

@devoirs_bp.route('/tri/classes', methods=['GET'])
def get_classes_prof():
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_ECRITURE)
    if err:
        return err

    classes = (db.session.query(Classe)
               .join(Cours, Cours.id_classe == Classe.id)
               .filter(Cours.id_prof == user['ID_Prof'])
               .distinct().all())
    return jsonify([{'ID': c.id, 'Niveau': c.niveau, 'Suffixe': c.suffixe}
                    for c in classes]), 200


@devoirs_bp.route('/tri/matieres', methods=['GET'])
def get_matieres_prof():
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_ECRITURE)
    if err:
        return err

    prof = db.session.get(Prof, user['ID_Prof'])
    if not prof:
        return jsonify([]), 200
    return jsonify([{'ID': m.id, 'Nom': m.nom} for m in prof.matieres]), 200