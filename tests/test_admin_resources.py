import pytest
from app import bcrypt
from app.models import Batiment, Classe, Etage, Matiere, Prof, Salle, User, db


@pytest.fixture
def admin(app):
    with app.app_context():
        u = User(
            type='administrateur', nom='Admin', prenom='Test',
            username='admin_res',
            mail_interne='admin.res@guardiaschool.fr',
            password=bcrypt.generate_password_hash('adminpass').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield u


@pytest.fixture
def eleve(app):
    with app.app_context():
        u = User(
            type='élève', nom='Dupont', prenom='Jean',
            username='jdupont_res',
            mail_interne='jean.dupont.res@guardiaschool.fr',
            password=bcrypt.generate_password_hash('password').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield u


@pytest.fixture
def matiere(app):
    with app.app_context():
        m = Matiere(nom='Mathématiques')
        db.session.add(m)
        db.session.commit()
        yield m


@pytest.fixture
def classe(app):
    with app.app_context():
        c = Classe(niveau=1, suffixe='A', annee=2026)
        db.session.add(c)
        db.session.commit()
        yield c


@pytest.fixture
def salle(app):
    with app.app_context():
        bat = Batiment(nom='Principal')
        db.session.add(bat)
        db.session.flush()
        etage = Etage(numero=0, id_batiment=bat.id)
        db.session.add(etage)
        db.session.flush()
        s = Salle(nom='A101', id_etage=etage.id)
        db.session.add(s)
        db.session.commit()
        yield s


def login_admin(client):
    client.post('/auth/login', json={
        'email': 'admin.res@guardiaschool.fr', 'password': 'adminpass'
    })


def login_eleve(client):
    client.post('/auth/login', json={
        'email': 'jean.dupont.res@guardiaschool.fr', 'password': 'password'
    })


# ════════════════════════════════════════════════════════════════
# ║                       MATIÈRES                               ║
# ════════════════════════════════════════════════════════════════

def test_list_matieres_admin(client, admin, matiere):
    login_admin(client)
    res = client.get('/admin/matieres')
    assert res.status_code == 200
    data = res.get_json()
    assert any(m['nom'] == 'Mathématiques' for m in data)


def test_list_matieres_forbidden(client, admin, eleve, matiere):
    login_eleve(client)
    res = client.get('/admin/matieres')
    assert res.status_code == 403


def test_list_matieres_unauthenticated(client):
    res = client.get('/admin/matieres')
    assert res.status_code == 401


def test_create_matiere_success(client, admin):
    login_admin(client)
    res = client.post('/admin/matieres', json={'nom': 'Informatique'})
    assert res.status_code == 201
    assert res.get_json()['nom'] == 'Informatique'


def test_create_matiere_duplicate(client, admin, matiere):
    login_admin(client)
    res = client.post('/admin/matieres', json={'nom': 'Mathématiques'})
    assert res.status_code == 409


def test_create_matiere_missing_nom(client, admin):
    login_admin(client)
    res = client.post('/admin/matieres', json={})
    assert res.status_code == 400


def test_create_matiere_empty_nom(client, admin):
    login_admin(client)
    res = client.post('/admin/matieres', json={'nom': '   '})
    assert res.status_code == 400


def test_create_matiere_forbidden(client, admin, eleve):
    login_eleve(client)
    res = client.post('/admin/matieres', json={'nom': 'Informatique'})
    assert res.status_code == 403


def test_create_matiere_unauthenticated(client):
    res = client.post('/admin/matieres', json={'nom': 'Informatique'})
    assert res.status_code == 401


def test_update_matiere_success(client, admin, matiere):
    login_admin(client)
    res = client.patch(f'/admin/matieres/{matiere.id}', json={'nom': 'Maths'})
    assert res.status_code == 200
    assert res.get_json()['nom'] == 'Maths'


def test_update_matiere_not_found(client, admin):
    login_admin(client)
    res = client.patch('/admin/matieres/9999', json={'nom': 'X'})
    assert res.status_code == 404


def test_update_matiere_empty_nom(client, admin, matiere):
    login_admin(client)
    res = client.patch(f'/admin/matieres/{matiere.id}', json={'nom': ''})
    assert res.status_code == 400


def test_update_matiere_forbidden(client, admin, eleve, matiere):
    login_eleve(client)
    res = client.patch(f'/admin/matieres/{matiere.id}', json={'nom': 'Hack'})
    assert res.status_code == 403


def test_delete_matiere_success(client, admin, matiere):
    login_admin(client)
    res = client.delete(f'/admin/matieres/{matiere.id}')
    assert res.status_code == 200
    assert client.get('/admin/matieres').get_json() == []


def test_delete_matiere_not_found(client, admin):
    login_admin(client)
    res = client.delete('/admin/matieres/9999')
    assert res.status_code == 404


def test_delete_matiere_forbidden(client, admin, eleve, matiere):
    login_eleve(client)
    res = client.delete(f'/admin/matieres/{matiere.id}')
    assert res.status_code == 403


def test_delete_matiere_unauthenticated(client, matiere):
    res = client.delete(f'/admin/matieres/{matiere.id}')
    assert res.status_code == 401


# ════════════════════════════════════════════════════════════════
# ║                       CLASSES                                ║
# ════════════════════════════════════════════════════════════════

def test_list_classes_admin(client, admin, classe):
    login_admin(client)
    res = client.get('/admin/classes')
    assert res.status_code == 200
    data = res.get_json()
    assert any(c['niveau'] == 1 and c['suffixe'] == 'A' for c in data)


def test_list_classes_forbidden(client, admin, eleve, classe):
    login_eleve(client)
    res = client.get('/admin/classes')
    assert res.status_code == 403


def test_list_classes_unauthenticated(client):
    res = client.get('/admin/classes')
    assert res.status_code == 401


def test_create_classe_success(client, admin):
    login_admin(client)
    res = client.post('/admin/classes', json={'niveau': 2, 'suffixe': 'B', 'annee': 2026})
    assert res.status_code == 201
    data = res.get_json()
    assert data['niveau'] == 2
    assert data['suffixe'] == 'B'
    assert data['annee'] == 2026


def test_create_classe_missing_fields(client, admin):
    login_admin(client)
    res = client.post('/admin/classes', json={'niveau': 1})
    assert res.status_code == 400


def test_create_classe_invalid_niveau(client, admin):
    login_admin(client)
    res = client.post('/admin/classes', json={'niveau': 'abc', 'annee': 2026})
    assert res.status_code == 400


def test_create_classe_invalid_prof(client, admin):
    login_admin(client)
    res = client.post('/admin/classes', json={
        'niveau': 1, 'annee': 2026, 'id_prof_principal': 9999
    })
    assert res.status_code == 404


def test_create_classe_forbidden(client, admin, eleve):
    login_eleve(client)
    res = client.post('/admin/classes', json={'niveau': 1, 'annee': 2026})
    assert res.status_code == 403


def test_create_classe_unauthenticated(client):
    res = client.post('/admin/classes', json={'niveau': 1, 'annee': 2026})
    assert res.status_code == 401


def test_update_classe_success(client, admin, classe):
    login_admin(client)
    res = client.patch(f'/admin/classes/{classe.id}', json={'suffixe': 'C', 'annee': 2027})
    assert res.status_code == 200
    data = res.get_json()
    assert data['suffixe'] == 'C'
    assert data['annee'] == 2027


def test_update_classe_not_found(client, admin):
    login_admin(client)
    res = client.patch('/admin/classes/9999', json={'suffixe': 'X'})
    assert res.status_code == 404


def test_update_classe_invalid_annee(client, admin, classe):
    login_admin(client)
    res = client.patch(f'/admin/classes/{classe.id}', json={'annee': 'nope'})
    assert res.status_code == 400


def test_update_classe_forbidden(client, admin, eleve, classe):
    login_eleve(client)
    res = client.patch(f'/admin/classes/{classe.id}', json={'suffixe': 'X'})
    assert res.status_code == 403


def test_delete_classe_success(client, admin, classe):
    login_admin(client)
    res = client.delete(f'/admin/classes/{classe.id}')
    assert res.status_code == 200
    assert client.get('/admin/classes').get_json() == []


def test_delete_classe_not_found(client, admin):
    login_admin(client)
    res = client.delete('/admin/classes/9999')
    assert res.status_code == 404


def test_delete_classe_forbidden(client, admin, eleve, classe):
    login_eleve(client)
    res = client.delete(f'/admin/classes/{classe.id}')
    assert res.status_code == 403


def test_delete_classe_unauthenticated(client, classe):
    res = client.delete(f'/admin/classes/{classe.id}')
    assert res.status_code == 401


# ════════════════════════════════════════════════════════════════
# ║                        SALLES                                ║
# ════════════════════════════════════════════════════════════════

def test_list_salles_admin(client, admin, salle):
    login_admin(client)
    res = client.get('/admin/salles')
    assert res.status_code == 200
    data = res.get_json()
    assert any(s['nom'] == 'A101' for s in data)


def test_list_salles_forbidden(client, admin, eleve, salle):
    login_eleve(client)
    res = client.get('/admin/salles')
    assert res.status_code == 403


def test_list_salles_unauthenticated(client):
    res = client.get('/admin/salles')
    assert res.status_code == 401


def test_create_salle_success(client, admin):
    login_admin(client)
    res = client.post('/admin/salles', json={'nom': 'Labo Info'})
    assert res.status_code == 201
    assert res.get_json()['nom'] == 'Labo Info'


def test_create_salle_missing_nom(client, admin):
    login_admin(client)
    res = client.post('/admin/salles', json={})
    assert res.status_code == 400


def test_create_salle_empty_nom(client, admin):
    login_admin(client)
    res = client.post('/admin/salles', json={'nom': '  '})
    assert res.status_code == 400


def test_create_salle_forbidden(client, admin, eleve):
    login_eleve(client)
    res = client.post('/admin/salles', json={'nom': 'Hack'})
    assert res.status_code == 403


def test_create_salle_unauthenticated(client):
    res = client.post('/admin/salles', json={'nom': 'X'})
    assert res.status_code == 401


def test_delete_salle_success(client, admin, salle):
    login_admin(client)
    res = client.delete(f'/admin/salles/{salle.id}')
    assert res.status_code == 200
    assert client.get('/admin/salles').get_json() == []


def test_delete_salle_not_found(client, admin):
    login_admin(client)
    res = client.delete('/admin/salles/9999')
    assert res.status_code == 404


def test_delete_salle_forbidden(client, admin, eleve, salle):
    login_eleve(client)
    res = client.delete(f'/admin/salles/{salle.id}')
    assert res.status_code == 403


def test_delete_salle_unauthenticated(client, salle):
    res = client.delete(f'/admin/salles/{salle.id}')
    assert res.status_code == 401
