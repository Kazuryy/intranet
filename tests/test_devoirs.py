from datetime import date, timedelta, datetime
from app.models import db, Devoir


# ── GET /api/devoirs/ ─────────────────────────────────────────────────────────

def test_get_devoirs_suid_manquant(client):
    assert client.get('/api/devoirs/').status_code == 401


def test_get_devoirs_suid_invalide(client):
    assert client.get('/api/devoirs/?suid=faux').status_code == 401


def test_get_devoirs_prof(client, prof_suid, devoirs):
    r = client.get(f'/api/devoirs/?suid={prof_suid}')
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert all(d['Matiere'] == 'Mathematiques' for d in data)


def test_get_devoirs_eleve(client, eleve_suid, devoirs):
    r = client.get(f'/api/devoirs/?suid={eleve_suid}')
    assert r.status_code == 200
    assert len(r.get_json()) == 5


def test_get_devoirs_admin(client, admin_suid, devoirs):
    r = client.get(f'/api/devoirs/?suid={admin_suid}')
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


# ── GET /api/devoirs/<id> ─────────────────────────────────────────────────────

def test_get_devoir_par_id(client, admin_suid, devoirs):
    id_devoir = devoirs[0].id
    r = client.get(f'/api/devoirs/{id_devoir}?suid={admin_suid}')
    assert r.status_code == 200
    assert r.get_json()['ID'] == id_devoir


def test_get_devoir_introuvable(client, admin_suid):
    assert client.get(f'/api/devoirs/99999?suid={admin_suid}').status_code == 404


def test_get_devoir_eleve_sa_classe(client, eleve_suid, devoirs):
    assert client.get(
        f'/api/devoirs/{devoirs[0].id}?suid={eleve_suid}'
    ).status_code == 200


def test_get_devoir_eleve_autre_classe(client, eleve_suid, app):
    from app.models import db, Classe, Matiere, Devoir
    with app.app_context():
        c = Classe(niveau=2, suffixe='Z', annee=2026)
        m = Matiere(nom='Physique')
        db.session.add_all([c, m])
        db.session.flush()
        d = Devoir(
            id_classe=c.id, id_matiere=m.id, id_prof=1,
            type='exercice',
            date_limite=datetime.combine(
                date.today() + timedelta(days=5), datetime.min.time()
            ),
            consigne='Autre classe'
        )
        db.session.add(d)
        db.session.commit()
        id_etranger = d.id
    assert client.get(
        f'/api/devoirs/{id_etranger}?suid={eleve_suid}'
    ).status_code == 404


# ── GET /api/devoirs/tri/a_venir ──────────────────────────────────────────────

def test_a_venir_seulement_futurs(client, eleve_suid, devoirs):
    r = client.get(f'/api/devoirs/tri/a_venir?suid={eleve_suid}')
    assert r.status_code == 200
    assert len(r.get_json()) == 3


def test_a_venir_tries_par_date(client, eleve_suid, devoirs):
    r = client.get(f'/api/devoirs/tri/a_venir?suid={eleve_suid}')
    dates = [d['Date_Limite'] for d in r.get_json()]
    assert dates == sorted(dates)


def test_a_venir_aucun_passe(client, admin_suid, devoirs):
    r = client.get(f'/api/devoirs/tri/a_venir?suid={admin_suid}')
    today_str = str(date.today())
    for d in r.get_json():
        assert d['Date_Limite'] > today_str


def test_a_venir_prof(client, prof_suid, devoirs):
    r = client.get(f'/api/devoirs/tri/a_venir?suid={prof_suid}')
    assert r.status_code == 200
    assert len(r.get_json()) == 3


# ── POST /api/devoirs/creer ───────────────────────────────────────────────────

def test_creer_devoir_ok(client, prof_suid, eleve_suid, app):
    from app.models import Classe, Matiere
    with app.app_context():
        c = Classe.query.filter_by(niveau=1, suffixe='A', annee=2026).first()
        m = Matiere.query.filter_by(nom='Mathematiques').first()
        cid, mid = c.id, m.id
    r = client.post('/api/devoirs/creer', json={
        'suid': prof_suid, 'id_classe': cid, 'id_matiere': mid,
        'type': 'exercice',
        'date_limite': str(date.today() + timedelta(days=10)),
        'consigne': 'Faire les exercices 1 a 5 page 42.'
    })
    assert r.status_code == 201
    assert 'id' in r.get_json()


def test_creer_devoir_champ_manquant(client, prof_suid, eleve_suid, app):
    from app.models import Classe, Matiere
    with app.app_context():
        c = Classe.query.filter_by(niveau=1, suffixe='A', annee=2026).first()
        m = Matiere.query.filter_by(nom='Mathematiques').first()
        cid, mid = c.id, m.id
    r = client.post('/api/devoirs/creer', json={
        'suid': prof_suid, 'id_classe': cid, 'id_matiere': mid,
        'type': 'exercice',
        'date_limite': str(date.today() + timedelta(days=10))
        # consigne intentionnellement absente
    })
    assert r.status_code == 400
    assert b'consigne' in r.data


def test_creer_devoir_type_invalide(client, prof_suid, eleve_suid, app):
    from app.models import Classe, Matiere
    with app.app_context():
        c = Classe.query.filter_by(niveau=1, suffixe='A', annee=2026).first()
        m = Matiere.query.filter_by(nom='Mathematiques').first()
        cid, mid = c.id, m.id
    r = client.post('/api/devoirs/creer', json={
        'suid': prof_suid, 'id_classe': cid, 'id_matiere': mid,
        'type': 'invention',
        'date_limite': str(date.today() + timedelta(days=10)),
        'consigne': 'Test.'
    })
    assert r.status_code == 400


def test_creer_devoir_eleve_interdit(client, eleve_suid):
    response = client.post('/api/devoirs/creer', json={
        'suid':        eleve_suid,
        'id_classe':   1,
        'id_matiere':  1,
        'type':        'exercice',
        'date_limite': str(date.today() + timedelta(days=10)),
        'consigne':    'Test.'
    })
    assert response.status_code == 403



def test_creer_devoir_suid_manquant(client):
    r = client.post('/api/devoirs/creer', json={
        'id_classe': 1, 'id_matiere': 1,
        'type': 'exercice',
        'date_limite': str(date.today() + timedelta(days=10)),
        'consigne': 'Test.'
    })
    assert r.status_code == 401


def test_creer_devoir_xss(client, prof_suid, eleve_suid, app):
    from app.models import Classe, Matiere
    with app.app_context():
        classe  = Classe.query.filter_by(niveau=1, suffixe='A', annee=2026).first()
        matiere = Matiere.query.filter_by(nom='Mathematiques').first()

    r = client.post('/api/devoirs/creer', json={
        'suid':        prof_suid,
        'id_classe':   classe.id,
        'id_matiere':  matiere.id,
        'type':        'exercice',
        'date_limite': str(date.today() + timedelta(days=10)),
        'consigne':    "<script>alert('xss')</script>Faire les exos"
    })
    assert r.status_code == 201

    devoir_id = r.get_json()['id']   # ← extrait l'ID ici, hors du with

    with app.app_context():
        d = db.session.get(Devoir, devoir_id)
        assert '<script>' not in d.consigne


# ── PUT /api/devoirs/modifier/<id> ────────────────────────────────────────────

def test_modifier_devoir_ok(client, prof_suid, devoirs):
    r = client.put(f'/api/devoirs/modifier/{devoirs[0].id}',
                   json={'suid': prof_suid, 'consigne': 'Nouvelle consigne'})
    assert r.status_code == 200


def test_modifier_devoir_aucun_champ(client, prof_suid, devoirs):
    r = client.put(f'/api/devoirs/modifier/{devoirs[0].id}',
                   json={'suid': prof_suid})
    assert r.status_code == 400
    assert b'Aucun champ' in r.data


def test_modifier_devoir_pas_au_prof(client, prof_suid, app):
    from app.models import db, Devoir, Classe, Matiere
    with app.app_context():
        c = Classe(niveau=3, suffixe='X', annee=2026)
        m = Matiere(nom='Histoire')
        db.session.add_all([c, m])
        db.session.flush()
        d = Devoir(
            id_classe=c.id, id_matiere=m.id, id_prof=999,
            type='exercice',
            date_limite=datetime.combine(
                date.today() + timedelta(days=7), datetime.min.time()
            ),
            consigne="Devoir d'un autre prof"
        )
        db.session.add(d)
        db.session.commit()
        id_etranger = d.id
    r = client.put(f'/api/devoirs/modifier/{id_etranger}',
                   json={'suid': prof_suid, 'consigne': 'Tentative'})
    assert r.status_code == 403


def test_modifier_devoir_suid_manquant(client, devoirs):
    r = client.put(f'/api/devoirs/modifier/{devoirs[0].id}',
                   json={'consigne': 'X'})
    assert r.status_code == 401


# ── DELETE /api/devoirs/supprimer/<id> ────────────────────────────────────────

def test_supprimer_devoir_ok(client, prof_suid, devoirs):
    r = client.delete(f'/api/devoirs/supprimer/{devoirs[0].id}',
                      json={'suid': prof_suid})
    assert r.status_code == 200