import pytest
from app import bcrypt
from app.models import User, db


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
