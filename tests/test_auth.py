def test_login_success(client, user):
    # POST /auth/login avec bon username/password => 200 + role
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert response.get_json()['role'] == 'administrateur'


def test_login_wrong_password(client, user):
    # POST /auth/login avec mauvais password => 401
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401


def test_login_unknown_user(client):
    # POST /auth/login avec username inexistant => 401
    response = client.post('/auth/login', json={
        'username': 'unknownuser',
        'password': 'password123'
    })
    assert response.status_code == 401


def test_logout(client, user):
    # login d'abord, puis POST /auth/logout => 200
    client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    response = client.post('/auth/logout')
    assert response.status_code == 200


def test_change_password_success(client, user):
    # login, puis changement de mot de passe valide => 200
    client.post('/auth/login', json={
        'username': 'testuser',
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
        'username': 'testuser',
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
        'username': 'testuser',
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
        'username': 'testuser',
        'password': 'password123'
    })
    response = client.patch('/auth/profile/phone', json={'numero': '0612345678'})
    assert response.status_code == 200


def test_change_phone_invalid(client, user):
    # numéro invalide => 400
    client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    response = client.patch('/auth/profile/phone', json={'numero': '123'})
    assert response.status_code == 400


def test_change_phone_unauthenticated(client):
    # non connecté => 401
    response = client.patch('/auth/profile/phone', json={'numero': '0612345678'})
    assert response.status_code == 401
