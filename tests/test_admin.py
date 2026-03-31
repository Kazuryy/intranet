import pytest
from datetime import datetime, timedelta, timezone
from app import bcrypt
from app.models import Employe, User, db


@pytest.fixture
def admin(app):
    with app.app_context():
        u = User(
            type='administrateur', nom='Admin', prenom='Test',
            username='admin',
            mail_interne='test.admin@guardiaschool.fr',
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
            username='jdupont',
            mail_interne='jean.dupont@guardiaschool.fr',
            password=bcrypt.generate_password_hash('password').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield u


def test_list_users_success(client, admin, eleve):
    # admin connecté => 200 + liste des users
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/admin/users')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_list_users_filter_type(client, admin, eleve):
    # filtre par type => retourne uniquement les élèves
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/admin/users?type=élève')
    assert response.status_code == 200
    data = response.get_json()
    assert all(u['type'] == 'élève' for u in data)
    assert len(data) == 1


def test_list_users_search(client, admin, eleve):
    # recherche par nom => retourne uniquement Dupont
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/admin/users?search=dupont')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['nom'] == 'Dupont'


def test_list_users_search_username(client, admin, eleve):
    # recherche par username
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/admin/users?search=jdupont')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['username'] == 'jdupont'


def test_list_users_forbidden_eleve(client, admin, eleve):
    # élève => 403
    client.post('/auth/login', json={
        'email': 'jean.dupont@guardiaschool.fr', 'password': 'password'
    })
    response = client.get('/admin/users')
    assert response.status_code == 403


def test_list_users_unauthenticated(client):
    # non connecté => 401
    response = client.get('/admin/users')
    assert response.status_code == 401


# --- POST /admin/users ---

def test_create_user_success(client, admin):
    # admin crée un élève => 201 + setup_link
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/admin/users', json={
        'nom': 'Martin', 'prenom': 'Alice', 'type': 'élève'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'setup_token' in data
    assert data['mail_interne'] == 'alice.martin@guardiaschool.fr'


def test_create_user_email_dedup(client, admin, eleve):
    # jean.dupont existe déjà => jean.dupont2
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/admin/users', json={
        'nom': 'Dupont', 'prenom': 'Jean', 'type': 'élève'
    })
    assert response.status_code == 201
    assert response.get_json()['mail_interne'] == 'jean.dupont2@guardiaschool.fr'


def test_create_user_missing_fields(client, admin):
    # champs manquants => 400
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/admin/users', json={'nom': 'Martin'})
    assert response.status_code == 400


def test_create_user_invalid_type(client, admin):
    # type inconnu => 400
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/admin/users', json={
        'nom': 'Martin', 'prenom': 'Alice', 'type': 'inconnu'
    })
    assert response.status_code == 400


def test_create_user_direction_forbidden_type(client, app):
    # direction ne peut pas créer un admin => 403
    with app.app_context():
        dir_user = User(
            type='employé', nom='Dir', prenom='Chef',
            username='cdirecteur',
            mail_interne='chef.dir@guardiaschool.fr',
            password=bcrypt.generate_password_hash('dirpass').decode('utf-8')
        )
        db.session.add(dir_user)
        db.session.flush()
        db.session.add(Employe(id_user=dir_user.id, role='direction'))
        db.session.commit()
    client.post('/auth/login', json={
        'email': 'chef.dir@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.post('/admin/users', json={
        'nom': 'Martin', 'prenom': 'Alice', 'type': 'administrateur'
    })
    assert response.status_code == 403


def test_create_user_forbidden_eleve(client, admin, eleve):
    # élève => 403
    client.post('/auth/login', json={
        'email': 'jean.dupont@guardiaschool.fr', 'password': 'password'
    })
    response = client.post('/admin/users', json={
        'nom': 'Martin', 'prenom': 'Alice', 'type': 'élève'
    })
    assert response.status_code == 403


def test_create_user_unauthenticated(client):
    # non connecté => 401
    response = client.post('/admin/users', json={
        'nom': 'Martin', 'prenom': 'Alice', 'type': 'élève'
    })
    assert response.status_code == 401


# --- POST /auth/setup-password ---

def test_setup_password_success(client, app):
    # token valide => 200, password configuré
    with app.app_context():
        u = User(
            type='élève', nom='New', prenom='User',
            username='nuser',
            mail_interne='user.new@guardiaschool.fr',
            password='',
            setup_token='validtoken123',
            setup_token_expires=datetime.now(timezone.utc) + timedelta(hours=48)
        )
        db.session.add(u)
        db.session.commit()
    response = client.post('/auth/setup-password', json={
        'token': 'validtoken123',
        'password': 'MonMotDePasse1!'
    })
    assert response.status_code == 200


def test_setup_password_invalid_token(client):
    # token inexistant => 400
    response = client.post('/auth/setup-password', json={
        'token': 'tokeninexistant',
        'password': 'MonMotDePasse1!'
    })
    assert response.status_code == 400


def test_setup_password_expired_token(client, app):
    # token expiré => 400
    with app.app_context():
        u = User(
            type='élève', nom='Old', prenom='User',
            username='ouser',
            mail_interne='user.old@guardiaschool.fr',
            password='',
            setup_token='expiredtoken123',
            setup_token_expires=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        db.session.add(u)
        db.session.commit()
    response = client.post('/auth/setup-password', json={
        'token': 'expiredtoken123',
        'password': 'MonMotDePasse1!'
    })
    assert response.status_code == 400


def test_setup_password_too_short(client, app):
    # mot de passe trop court => 400
    with app.app_context():
        u = User(
            type='élève', nom='Short', prenom='User',
            username='suser',
            mail_interne='user.short@guardiaschool.fr',
            password='',
            setup_token='shortpasstoken',
            setup_token_expires=datetime.now(timezone.utc) + timedelta(hours=48)
        )
        db.session.add(u)
        db.session.commit()
    response = client.post('/auth/setup-password', json={
        'token': 'shortpasstoken',
        'password': 'court'
    })
    assert response.status_code == 400


# --- PATCH /admin/users/<id> ---

def test_update_user_success(client, admin, eleve):
    # admin modifie nom et is_active => 200
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/admin/users/{eleve.id}', json={
        'nom': 'Durand', 'is_active': False
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['nom'] == 'Durand'
    assert data['is_active'] is False


def test_update_user_invalid_type(client, admin, eleve):
    # type invalide => 400
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/admin/users/{eleve.id}', json={'type': 'inconnu'})
    assert response.status_code == 400


def test_update_user_empty_nom(client, admin, eleve):
    # nom vide => 400
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/admin/users/{eleve.id}', json={'nom': '  '})
    assert response.status_code == 400


def test_update_user_no_fields(client, admin, eleve):
    # aucun champ modifiable => 400
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/admin/users/{eleve.id}', json={})
    assert response.status_code == 400


def test_update_user_not_found(client, admin):
    # user inexistant => 404
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch('/admin/users/9999', json={'nom': 'Test'})
    assert response.status_code == 404


def test_update_user_forbidden(client, admin, eleve):
    # élève => 403
    client.post('/auth/login', json={
        'email': 'jean.dupont@guardiaschool.fr', 'password': 'password'
    })
    response = client.patch(f'/admin/users/{eleve.id}', json={'nom': 'Hack'})
    assert response.status_code == 403


def test_update_user_unauthenticated(client, eleve):
    # non connecté => 401
    response = client.patch(f'/admin/users/{eleve.id}', json={'nom': 'Test'})
    assert response.status_code == 401


# --- DELETE /admin/users/<id> ---

def test_delete_user_success(client, admin, eleve):
    # admin supprime un élève => 200
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.delete(f'/admin/users/{eleve.id}')
    assert response.status_code == 200


def test_delete_user_self(client, admin):
    # admin ne peut pas se supprimer lui-même => 403
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.delete(f'/admin/users/{admin.id}')
    assert response.status_code == 403


def test_delete_user_not_found(client, admin):
    # user inexistant => 404
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.delete('/admin/users/9999')
    assert response.status_code == 404


def test_delete_user_forbidden(client, admin, eleve):
    # élève => 403
    client.post('/auth/login', json={
        'email': 'jean.dupont@guardiaschool.fr', 'password': 'password'
    })
    response = client.delete(f'/admin/users/{eleve.id}')
    assert response.status_code == 403


def test_delete_user_unauthenticated(client, eleve):
    # non connecté => 401
    response = client.delete(f'/admin/users/{eleve.id}')
    assert response.status_code == 401
