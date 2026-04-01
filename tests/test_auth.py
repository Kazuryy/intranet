def test_login_success(client, user):
    # POST /auth/login avec bon email/password => 200 + role
    response = client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert response.get_json()['role'] == 'administrateur'


def test_login_wrong_password(client, user):
    # POST /auth/login avec mauvais password => 401
    response = client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401


def test_login_unknown_user(client):
    # POST /auth/login avec email inexistant => 401
    response = client.post('/auth/login', json={
        'email': 'inconnu@guardiaschool.fr',
        'password': 'password123'
    })
    assert response.status_code == 401


def test_login_inactive_user(client, app):
    # compte désactivé => 403
    from app import bcrypt
    from app.models import User, db
    with app.app_context():
        u = User(
            type='élève', nom='Inactif', prenom='User',
            username='inactif',
            mail_interne='user.inactif@guardiaschool.fr',
            password=bcrypt.generate_password_hash('password123').decode('utf-8'),
            is_active=False
        )
        db.session.add(u)
        db.session.commit()
    response = client.post('/auth/login', json={
        'email': 'user.inactif@guardiaschool.fr',
        'password': 'password123'
    })
    assert response.status_code == 403


def test_login_no_json(client):
    # pas de JSON => 400
    response = client.post(
        '/auth/login', data='notjson', content_type='text/plain'
    )
    assert response.status_code == 400


def test_login_empty_fields(client):
    # champs vides => 400
    response = client.post('/auth/login', json={'email': '', 'password': ''})
    assert response.status_code == 400


def test_logout(client, user):
    # login d'abord, puis POST /auth/logout => 200
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.post('/auth/logout')
    assert response.status_code == 200


def test_logout_unauthenticated(client):
    # non connecté => 401
    response = client.post('/auth/logout')
    assert response.status_code == 401


def test_change_password_success(client, user):
    # login, puis changement de mot de passe valide => 200
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.patch('/auth/profile/password', json={
        'current_password': 'password123',
        'new_password': 'nouveaumdp99'
    })
    assert response.status_code == 200


def test_change_password_wrong_current(client, user):
    # mauvais mot de passe actuel => 400
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.patch('/auth/profile/password', json={
        'current_password': 'mauvaismdp',
        'new_password': 'nouveaumdp99'
    })
    assert response.status_code == 400


def test_change_password_too_short(client, user):
    # nouveau mot de passe trop court => 400
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.patch('/auth/profile/password', json={
        'current_password': 'password123',
        'new_password': 'court'
    })
    assert response.status_code == 400


def test_change_password_unauthenticated(client):
    # non connecté => 401
    response = client.patch('/auth/profile/password', json={
        'current_password': 'password123',
        'new_password': 'nouveaumdp99'
    })
    assert response.status_code == 401


def test_change_phone_success(client, user):
    # login, puis numéro valide => 200
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.patch('/auth/profile/phone', json={'numero': '0612345678'})
    assert response.status_code == 200


def test_change_phone_invalid(client, user):
    # numéro invalide => 400
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.patch('/auth/profile/phone', json={'numero': '123'})
    assert response.status_code == 400


def test_change_phone_unauthenticated(client):
    # non connecté => 401
    response = client.patch('/auth/profile/phone', json={'numero': '0612345678'})
    assert response.status_code == 401


def test_contact_direction_success(client, user, direction):
    # login, champ valide, direction existe => 201
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.post('/auth/profile/contact-direction', json={'champ': 'nom'})
    assert response.status_code == 201


def test_contact_direction_invalid_champ(client, user, direction):
    # champ non autorisé => 400
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.post(
        '/auth/profile/contact-direction', json={'champ': 'username'}
    )
    assert response.status_code == 400


def test_contact_direction_no_direction(client, user):
    # pas de direction en base => 404
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.post('/auth/profile/contact-direction', json={'champ': 'nom'})
    assert response.status_code == 404


def test_contact_direction_unauthenticated(client):
    # non connecté => 401
    response = client.post('/auth/profile/contact-direction', json={'champ': 'nom'})
    assert response.status_code == 401
