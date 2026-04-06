import pytest
from datetime import datetime, timedelta, timezone
from app import bcrypt
from app.models import Direction, User, db


@pytest.fixture
def direction_user(app):
    with app.app_context():
        u = User(
            type='employé', nom='Dir', prenom='Chef',
            username='cdirecteur',
            mail_interne='chef.dir@guardiaschool.fr',
            password=bcrypt.generate_password_hash('dirpass').decode('utf-8')
        )
        db.session.add(u)
        db.session.flush()
        db.session.add(Direction(id_user=u.id))
        db.session.commit()
        yield u


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


def test_create_user_direction_forbidden_type(client, direction_user):
    # direction ne peut pas créer un admin => 403
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


# --- RBAC direction sur PATCH/DELETE ---

def test_direction_can_update_eleve(client, direction_user, eleve):
    # direction peut modifier un élève => 200
    client.post('/auth/login', json={
        'email': 'chef.dir@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.patch(f'/admin/users/{eleve.id}', json={'is_active': False})
    assert response.status_code == 200


def test_direction_cannot_update_admin(client, direction_user, admin):
    # direction ne peut pas modifier un admin => 403
    client.post('/auth/login', json={
        'email': 'chef.dir@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.patch(f'/admin/users/{admin.id}', json={'nom': 'Hack'})
    assert response.status_code == 403


def test_direction_can_delete_eleve(client, direction_user, eleve):
    # direction peut supprimer un élève => 200
    client.post('/auth/login', json={
        'email': 'chef.dir@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.delete(f'/admin/users/{eleve.id}')
    assert response.status_code == 200


def test_direction_cannot_delete_admin(client, direction_user, admin):
    # direction ne peut pas supprimer un admin => 403
    client.post('/auth/login', json={
        'email': 'chef.dir@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.delete(f'/admin/users/{admin.id}')
    assert response.status_code == 403


@pytest.fixture
def employe_non_dir(app):
    with app.app_context():
        u = User(
            type='employé', nom='Cantine', prenom='Agent',
            username='cantine_admin',
            mail_interne='cantine.admin@guardiaschool.fr',
            password=bcrypt.generate_password_hash('cantinepass').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield u


@pytest.fixture
def employe_user(app):
    with app.app_context():
        u = User(
            type='employé', nom='Prof', prenom='Jean',
            username='jprof_admin',
            mail_interne='jean.prof.admin@guardiaschool.fr',
            password=bcrypt.generate_password_hash('profpass').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield u


def test_list_users_non_direction_forbidden(client, admin, employe_non_dir):
    # employé non-direction => 403
    client.post('/auth/login', json={
        'email': 'cantine.admin@guardiaschool.fr', 'password': 'cantinepass'
    })
    response = client.get('/admin/users')
    assert response.status_code == 403


def test_create_user_no_json(client, admin):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post(
        '/admin/users', data='notjson', content_type='text/plain'
    )
    assert response.status_code == 400


def test_update_user_no_json(client, admin, eleve):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(
        f'/admin/users/{eleve.id}',
        data='notjson', content_type='text/plain'
    )
    assert response.status_code == 400


def test_update_user_empty_prenom(client, admin, eleve):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/admin/users/{eleve.id}', json={'prenom': '  '})
    assert response.status_code == 400


def test_update_user_type_change(client, admin, eleve):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/admin/users/{eleve.id}', json={'type': 'parent'})
    assert response.status_code == 200
    assert response.get_json()['type'] == 'parent'


def test_update_user_is_active_not_bool(client, admin, eleve):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(
        f'/admin/users/{eleve.id}', json={'is_active': 'oui'}
    )
    assert response.status_code == 400


# --- /admin/users/<id>/set-prof ---

def test_set_prof_success(client, admin, employe_user):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post(f'/admin/users/{employe_user.id}/set-prof')
    assert response.status_code == 201
    assert 'id_prof' in response.get_json()


def test_set_prof_already_prof(client, admin, employe_user):
    # deux fois => 200 la deuxième fois (idempotent)
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    client.post(f'/admin/users/{employe_user.id}/set-prof')
    response = client.post(f'/admin/users/{employe_user.id}/set-prof')
    assert response.status_code == 200


def test_set_prof_not_employe(client, admin, eleve):
    # user n'est pas employé => 400
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post(f'/admin/users/{eleve.id}/set-prof')
    assert response.status_code == 400


def test_set_prof_not_found(client, admin):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/admin/users/9999/set-prof')
    assert response.status_code == 404


def test_unset_prof_success(client, admin, employe_user):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    client.post(f'/admin/users/{employe_user.id}/set-prof')
    response = client.delete(f'/admin/users/{employe_user.id}/set-prof')
    assert response.status_code == 200


def test_unset_prof_not_prof(client, admin, employe_user):
    # user n'est pas prof => 404
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.delete(f'/admin/users/{employe_user.id}/set-prof')
    assert response.status_code == 404


def test_prof_status(client, admin, employe_user):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    client.post(f'/admin/users/{employe_user.id}/set-prof')
    response = client.get(f'/admin/users/{employe_user.id}/prof-status')
    assert response.status_code == 200
    data = response.get_json()
    assert data['is_prof'] is True


def test_prof_status_not_prof(client, admin, employe_user):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get(f'/admin/users/{employe_user.id}/prof-status')
    assert response.status_code == 200
    assert response.get_json()['is_prof'] is False


def test_set_prof_matieres_success(client, admin, employe_user, app):
    from app.models import Matiere
    with app.app_context():
        m = Matiere(nom='Histoire')
        db.session.add(m)
        db.session.commit()
        matiere_id = m.id
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    client.post(f'/admin/users/{employe_user.id}/set-prof')
    response = client.post(
        f'/admin/users/{employe_user.id}/prof-matieres',
        json={'matiere_ids': [matiere_id]}
    )
    assert response.status_code == 200
    assert len(response.get_json()['matieres']) == 1


def test_set_prof_matieres_not_prof(client, admin, employe_user):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post(
        f'/admin/users/{employe_user.id}/prof-matieres',
        json={'matiere_ids': []}
    )
    assert response.status_code == 404


def test_set_prof_matieres_invalid_list(client, admin, employe_user):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    client.post(f'/admin/users/{employe_user.id}/set-prof')
    response = client.post(
        f'/admin/users/{employe_user.id}/prof-matieres',
        json={'matiere_ids': 'pas-une-liste'}
    )
    assert response.status_code == 400


# --- Classes avec prof_principal ---

def test_create_classe_with_prof(client, admin, employe_user, app):
    # crée une classe avec prof_principal => _classe_to_dict avec prof
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    client.post(f'/admin/users/{employe_user.id}/set-prof')
    from app.models import Prof
    with app.app_context():
        prof = Prof.query.filter_by(id_user=employe_user.id).first()
        prof_id = prof.id
    response = client.post('/admin/classes', json={
        'niveau': 3, 'annee': 2026, 'id_prof_principal': prof_id
    })
    assert response.status_code == 201
    assert response.get_json()['prof_principal'] is not None


def test_create_classe_no_json(client, admin):
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post(
        '/admin/classes', data='notjson', content_type='text/plain'
    )
    assert response.status_code == 400


def test_update_classe_no_json(client, admin, app):
    from app.models import Classe
    with app.app_context():
        c = Classe(niveau=1, suffixe='Z', annee=2026)
        db.session.add(c)
        db.session.commit()
        cid = c.id
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(
        f'/admin/classes/{cid}', data='notjson', content_type='text/plain'
    )
    assert response.status_code == 400


def test_update_classe_invalid_niveau(client, admin, app):
    from app.models import Classe
    with app.app_context():
        c = Classe(niveau=1, suffixe='Z', annee=2026)
        db.session.add(c)
        db.session.commit()
        cid = c.id
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/admin/classes/{cid}', json={'niveau': 'abc'})
    assert response.status_code == 400


def test_update_classe_prof_not_found(client, admin, app):
    from app.models import Classe
    with app.app_context():
        c = Classe(niveau=1, suffixe='Z', annee=2026)
        db.session.add(c)
        db.session.commit()
        cid = c.id
    client.post('/auth/login', json={
        'email': 'test.admin@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(
        f'/admin/classes/{cid}', json={'id_prof_principal': 9999}
    )
    assert response.status_code == 404
