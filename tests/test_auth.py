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
