from flask import Blueprint, request, jsonify
from models.db import get_db
import bleach
from datetime import date
from mysql.connector import Error


def sanitize(text):
    return bleach.clean(text, tags=[], strip=True)


# Rôles qui peuvent VOIR les devoirs
ROLES_LECTURE  = ['élève', 'prof', 'direction', 'cpe', 'parent', 'administrateur']

# Rôles qui peuvent CRÉER/MODIFIER/SUPPRIMER
ROLES_ECRITURE = ['prof']


def get_user_from_suid(suid):
    conn = get_db()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT u.ID, u.Type
        FROM Session s
        JOIN User u ON s.ID_User = u.ID
        WHERE s.SUID = %s AND s.Expire_Le > NOW()
    """, (suid,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return None

    role = user['Type']
    user['ID_Prof'] = None

    if user['Type'] == 'employé':
        cursor.execute("SELECT ID FROM Prof WHERE ID_User = %s", (user['ID'],))
        prof = cursor.fetchone()

        if prof:
            role = 'prof'
            user['ID_Prof'] = prof['ID']
        else:
            cursor.execute("SELECT Role FROM Direction WHERE ID_User = %s", (user['ID'],))
            direction = cursor.fetchone()
            if direction:
                role = 'direction'
            else:
                cursor.execute("SELECT Role FROM Employe WHERE ID_User = %s", (user['ID'],))
                employe = cursor.fetchone()
                if employe and employe['Role']:
                    role = employe['Role'].lower()

    cursor.close()
    conn.close()
    user['role'] = role
    return user


def verif_role(suid, roles_autorises):
    if not suid:
        return None, (jsonify({"error": "SUID manquant"}), 401)

    user = get_user_from_suid(suid)

    if not user:
        return None, (jsonify({"error": "Session invalide ou expirée"}), 401)

    if user['role'] not in roles_autorises:
        return None, (jsonify({"error": "Accès non autorisé"}), 403)

    return user, None


devoirs_bp = Blueprint('devoirs', __name__, url_prefix='/api/devoirs')


###################################################################################################################
# ROUTES EN LECTURE
###################################################################################################################


@devoirs_bp.route('/', methods=['GET'])
def get_devoirs():
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_LECTURE)
    if err: return err

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        if user['role'] == 'prof':
            cursor.execute("""
                SELECT d.ID, d.Type, d.Date_Limite, d.Consigne,
                       c.Niveau, c.Suffixe, m.Nom AS Matiere
                FROM Devoir d
                JOIN Classe  c ON d.ID_Classe  = c.ID
                JOIN Matiere m ON d.ID_Matiere = m.ID
                WHERE d.ID_Prof = %s
                ORDER BY d.Date_Limite DESC
            """, (user['ID_Prof'],))

        elif user['role'] == 'élève':
            cursor.execute("""
                SELECT d.ID, d.Type, d.Date_Limite, d.Consigne,
                       c.Niveau, c.Suffixe, m.Nom AS Matiere
                FROM Devoir d
                JOIN Classe  c ON d.ID_Classe  = c.ID
                JOIN Matiere m ON d.ID_Matiere = m.ID
                JOIN Eleve   e ON e.ID_Classe  = d.ID_Classe
                WHERE e.ID_User = %s
                ORDER BY d.Date_Limite DESC
            """, (user['ID'],))

        else:
            cursor.execute("""
                SELECT d.ID, d.Type, d.Date_Limite, d.Consigne,
                       c.Niveau, c.Suffixe, m.Nom AS Matiere
                FROM Devoir d
                JOIN Classe  c ON d.ID_Classe  = c.ID
                JOIN Matiere m ON d.ID_Matiere = m.ID
                ORDER BY d.Date_Limite DESC
            """)

        devoirs = cursor.fetchall()
        return jsonify(devoirs), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@devoirs_bp.route('/<int:id_devoir>', methods=['GET'])
def get_devoir(id_devoir):
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_LECTURE)
    if err: return err

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        if user['role'] == 'prof':
            cursor.execute("""
                SELECT d.*, c.Niveau, c.Suffixe, m.Nom AS Matiere
                FROM Devoir d
                JOIN Classe  c ON d.ID_Classe  = c.ID
                JOIN Matiere m ON d.ID_Matiere = m.ID
                WHERE d.ID = %s AND d.ID_Prof = %s
            """, (id_devoir, user['ID_Prof']))

        elif user['role'] == 'élève':
            cursor.execute("""
                SELECT d.*, c.Niveau, c.Suffixe, m.Nom AS Matiere
                FROM Devoir d
                JOIN Classe  c ON d.ID_Classe  = c.ID
                JOIN Matiere m ON d.ID_Matiere = m.ID
                JOIN Eleve   e ON e.ID_Classe  = d.ID_Classe
                WHERE d.ID = %s AND e.ID_User = %s
            """, (id_devoir, user['ID']))

        else:
            cursor.execute("""
                SELECT d.*, c.Niveau, c.Suffixe, m.Nom AS Matiere
                FROM Devoir d
                JOIN Classe  c ON d.ID_Classe  = c.ID
                JOIN Matiere m ON d.ID_Matiere = m.ID
                WHERE d.ID = %s
            """, (id_devoir,))

        devoir = cursor.fetchone()
        if not devoir:
            return jsonify({"error": "Devoir introuvable ou accès refusé"}), 404
        return jsonify(devoir), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@devoirs_bp.route('/tri/a_venir', methods=['GET'])
def get_devoirs_a_venir():
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_LECTURE)
    if err: return err

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        aujourd_hui = date.today()

        if user['role'] == 'prof':
            cursor.execute("""
                SELECT d.ID, d.Type, d.Date_Limite, d.Consigne,
                       m.Nom AS Matiere, c.Niveau, c.Suffixe
                FROM Devoir d
                JOIN Matiere m ON d.ID_Matiere = m.ID
                JOIN Classe  c ON d.ID_Classe  = c.ID
                WHERE d.ID_Prof = %s AND d.Date_Limite > %s
                ORDER BY d.Date_Limite ASC
            """, (user['ID_Prof'], aujourd_hui))

        elif user['role'] == 'élève':
            cursor.execute("""
                SELECT d.ID, d.Type, d.Date_Limite, d.Consigne,
                       m.Nom AS Matiere, c.Niveau, c.Suffixe
                FROM Devoir d
                JOIN Matiere m ON d.ID_Matiere = m.ID
                JOIN Classe  c ON d.ID_Classe  = c.ID
                JOIN Eleve   e ON e.ID_Classe  = d.ID_Classe
                WHERE e.ID_User = %s AND d.Date_Limite > %s
                ORDER BY d.Date_Limite ASC
            """, (user['ID'], aujourd_hui))

        else:
            cursor.execute("""
                SELECT d.ID, d.Type, d.Date_Limite, d.Consigne,
                       m.Nom AS Matiere, c.Niveau, c.Suffixe
                FROM Devoir d
                JOIN Matiere m ON d.ID_Matiere = m.ID
                JOIN Classe  c ON d.ID_Classe  = c.ID
                WHERE d.Date_Limite > %s
                ORDER BY d.Date_Limite ASC
            """, (aujourd_hui,))

        devoirs = cursor.fetchall()
        return jsonify(devoirs), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


###################################################################################################################
# ROUTES EN ÉCRITURE (prof uniquement)
###################################################################################################################


@devoirs_bp.route('/creer', methods=['POST'])
def create_devoir():
    data = request.get_json() or {}
    user, err = verif_role(data.get('suid'), ROLES_ECRITURE)
    if err: return err

    required = ['id_classe', 'id_matiere', 'type', 'date_limite', 'consigne']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Champ manquant : {field}"}), 400

    types_valides = ['exercice', 'soutenance', 'exposé', 'contrôle', 'autre']
    if data['type'] not in types_valides:
        return jsonify({"error": f"Type invalide. Valeurs acceptées : {types_valides}"}), 400

    data['consigne'] = sanitize(data['consigne'])
    data['type']     = sanitize(data['type'])

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Devoir (ID_Classe, ID_Matiere, Type, Date_Limite, Consigne, ID_Prof)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['id_classe'], data['id_matiere'], data['type'], data['date_limite'], data['consigne'], user['ID_Prof']))
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({"message": "Devoir créé", "id": new_id}), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@devoirs_bp.route('/modifier/<int:id_devoir>', methods=['PUT'])
def update_devoir(id_devoir):
    data = request.get_json() or {}
    user, err = verif_role(data.get('suid'), ROLES_ECRITURE)
    if err: return err

    if 'consigne' in data:
        data['consigne'] = sanitize(data['consigne'])
    if 'type' in data:
        data['type'] = sanitize(data['type'])

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM Devoir WHERE ID = %s AND ID_Prof = %s", (id_devoir, user['ID_Prof']))
        if not cursor.fetchone():
            return jsonify({"error": "Devoir introuvable ou accès refusé"}), 403

        fields = ['id_classe', 'id_matiere', 'type', 'date_limite', 'consigne']
        updates = {k: data[k] for k in fields if k in data}
        if not updates:
            return jsonify({"error": "Aucun champ à modifier"}), 400

        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [id_devoir]
        cursor.execute(f"UPDATE Devoir SET {set_clause} WHERE ID = %s", values)
        conn.commit()
        return jsonify({"message": "Devoir mis à jour"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@devoirs_bp.route('/supprimer/<int:id_devoir>', methods=['DELETE'])
def delete_devoir(id_devoir):
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_ECRITURE)
    if err: return err

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM Devoir WHERE ID = %s AND ID_Prof = %s", (id_devoir, user['ID_Prof']))
        if not cursor.fetchone():
            return jsonify({"error": "Devoir introuvable ou accès refusé"}), 403

        cursor.execute("DELETE FROM Devoir WHERE ID = %s", (id_devoir,))
        conn.commit()
        return jsonify({"message": "Devoir supprimé"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


###################################################################################################################
# ROUTES FORMULAIRES (prof uniquement)
###################################################################################################################


@devoirs_bp.route('/tri/classes', methods=['GET'])
def get_classes_prof():
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_ECRITURE)
    if err: return err

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT cl.ID, cl.Niveau, cl.Suffixe
            FROM Cours c
            JOIN Classe cl ON c.ID_Classe = cl.ID
            WHERE c.ID_Prof = %s
        """, (user['ID_Prof'],))
        classes = cursor.fetchall()
        return jsonify(classes), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@devoirs_bp.route('/tri/matieres', methods=['GET'])
def get_matieres_prof():
    suid = request.args.get('suid')
    user, err = verif_role(suid, ROLES_ECRITURE)
    if err: return err

    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT m.ID, m.Nom
            FROM Prof p
            JOIN Matiere m ON p.ID_Matiere = m.ID
            WHERE p.ID = %s
        """, (user['ID_Prof'],))
        matieres = cursor.fetchall()
        return jsonify(matieres), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()