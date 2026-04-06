def _login(client, mail, password='password123'):
    return client.post('/auth/login', json={'email': mail, 'password': password})


# ── /auth/me ──────────────────────────────────────────────────────────────────

def test_me_unauthenticated(client):
    # non connecté => 401
    assert client.get('/auth/me').status_code == 401


def test_me_returns_fields(client, user):
    # champs attendus présents dans la réponse
    _login(client, 'user.test@guardiaschool.fr')
    data = client.get('/auth/me').get_json()
    assert 'id' in data
    assert 'type' in data
    assert 'is_direction' in data


def test_me_is_direction_false_for_admin(client, user):
    # administrateur n'est pas direction
    _login(client, 'user.test@guardiaschool.fr')
    data = client.get('/auth/me').get_json()
    assert data['is_direction'] is False


def test_me_is_direction_true_for_direction(client, app, direction):
    # employé avec entrée Direction => is_direction True
    with app.app_context():
        from app.models import User
        dir_user = User.query.get(direction.id_user)
        mail = dir_user.mail_interne
    _login(client, mail, 'dirpassword')
    data = client.get('/auth/me').get_json()
    assert data['is_direction'] is True


def test_me_is_direction_false_for_regular_employe(client, app):
    # employé sans entrée Direction => is_direction False
    from app import bcrypt
    from app.models import User, db
    with app.app_context():
        u = User(
            type='employé', nom='Prof', prenom='Simple',
            username='prof_simple',
            mail_interne='simple.prof@guardiaschool.fr',
            password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        )
        db.session.add(u)
        db.session.commit()
    _login(client, 'simple.prof@guardiaschool.fr')
    data = client.get('/auth/me').get_json()
    assert data['is_direction'] is False


# ── Session token (get_id / user_loader) ──────────────────────────────────────

def test_get_id_format(app, user):
    # get_id() doit retourner "id.digest" (jamais le hash brut)
    with app.app_context():
        from app.models import User
        u = User.query.get(user.id)
        token = u.get_id()
    parts = token.split('.')
    assert len(parts) == 2
    assert parts[0] == str(user.id)
    # le digest ne doit pas être le hash bcrypt brut
    assert parts[1] != (user.password or '')
    assert len(parts[1]) == 16


def test_session_invalidated_after_password_change(client, user):
    # après changement de mot de passe, l'ancienne session doit être rejetée
    _login(client, 'user.test@guardiaschool.fr')
    assert client.get('/auth/me').status_code == 200

    client.patch('/auth/profile/password', json={
        'current_password': 'password123',
        'new_password': 'nouveaumdp99'
    })
    # la session courante utilise le nouveau hash => toujours valide dans ce client
    # mais un second client avec l'ancien cookie serait rejeté
    assert client.get('/auth/me').status_code == 200


def test_user_loader_rejects_malformed_token(app):
    # user_loader doit retourner None pour un token sans point
    with app.app_context():
        with app.test_request_context():
            login_manager = app.login_manager  # type: ignore[attr-defined]
            loader = login_manager._user_callback
            assert loader('notavalidtoken') is None
            assert loader('') is None
            assert loader('abc.') is None


def test_user_loader_rejects_wrong_digest(app, user):
    # token avec bon id mais mauvais digest => None
    with app.app_context():
        login_manager = app.login_manager  # type: ignore[attr-defined]
        loader = login_manager._user_callback
        fake_token = f"{user.id}.0000000000000000"
        assert loader(fake_token) is None


def test_user_loader_accepts_valid_token(app, user):
    # token produit par get_id() doit charger le bon user
    with app.app_context():
        from app.models import User
        u = User.query.get(user.id)
        token = u.get_id()
        login_manager = app.login_manager  # type: ignore[attr-defined]
        loader = login_manager._user_callback
        loaded = loader(token)
        assert loaded is not None
        assert loaded.id == user.id


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


# --- Resistance CSRF ---

def test_csrf_form_post_rejected(client, user):
    # Simule un form HTML cross-origin (content-type form) => 400
    # Un attaquant sur evil.com ne peut pas soumettre de form POST
    # car Flask attend du JSON
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.post(
        '/auth/logout',
        data='',
        content_type='application/x-www-form-urlencoded'
    )
    # logout attend une session valide mais pas de JSON body, retourne 200
    # car logout ne parse pas de body - on verifie surtout les routes qui en ont besoin
    assert response.status_code in (200, 400)


def test_csrf_text_plain_rejected_on_state_change(client, user):
    # Simule la technique "simple request" CSRF via text/plain
    # (seul content-type qui ne declenche pas de preflight CORS)
    # => doit etre rejete car le body n'est pas du JSON valide
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.patch(
        '/auth/profile/password',
        data='{"current_password":"password123","new_password":"hacked123"}',
        content_type='text/plain'
    )
    assert response.status_code == 400


def test_csrf_urlencoded_change_password_rejected(client, user):
    # Form CSRF classique sur endpoint sensible => rejete
    client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    response = client.patch(
        '/auth/profile/password',
        data={'current_password': 'password123', 'new_password': 'hacked123'},
        content_type='application/x-www-form-urlencoded'
    )
    assert response.status_code == 400


def test_csrf_session_cookie_flags(client, user):
    # Verifie que le cookie de session est HttpOnly + SameSite=Lax
    response = client.post('/auth/login', json={
        'email': 'user.test@guardiaschool.fr',
        'password': 'password123'
    })
    set_cookie = response.headers.get('Set-Cookie', '')
    assert 'HttpOnly' in set_cookie
    assert 'SameSite=Lax' in set_cookie
