import pytest
from app import bcrypt, create_app
from app.models import (
    db, User, Eleve, Parent, Classe, Matiere, Evaluation, Prof, Cours, Salle,
    Batiment, Etage
)
from datetime import datetime


@pytest.fixture
def app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _make_user(type, username):
    return User(
        type=type,
        nom='Test',
        prenom=username.capitalize(),
        username=username,
        mail_interne=f'{username}@guardiaschool.fr',
        password=bcrypt.generate_password_hash('pass123').decode('utf-8'),
    )


def _login(client, mail_interne, password='pass123'):
    return client.post('/auth/login', json={
        'email': mail_interne, 'password': password
    })


@pytest.fixture
def seed(app):
    """Cree : 1 classe, 1 matiere, 1 eleve, 1 parent, 2 evaluations."""
    with app.app_context():
        classe = Classe(niveau=12, suffixe='A', annee=2026)
        db.session.add(classe)
        db.session.flush()

        matiere = Matiere(nom='Mathematiques')
        db.session.add(matiere)
        db.session.flush()

        u_eleve = _make_user('élève', 'eleve1')
        db.session.add(u_eleve)
        db.session.flush()

        eleve = Eleve(id_user=u_eleve.id, id_classe=classe.id)
        db.session.add(eleve)
        db.session.flush()

        u_parent = _make_user('parent', 'parent1')
        db.session.add(u_parent)
        db.session.flush()

        parent = Parent(id_user=u_parent.id, id_eleve=eleve.id)
        db.session.add(parent)

        ev1 = Evaluation(
            id_eleve=eleve.id, id_matiere=matiere.id,
            note=14, note_max=20, coefficient=2,
            date=datetime(2025, 10, 15),
        )
        ev2 = Evaluation(
            id_eleve=eleve.id, id_matiere=matiere.id,
            note=16, note_max=20, coefficient=1,
            date=datetime(2025, 11, 20),
        )
        db.session.add_all([ev1, ev2])
        db.session.commit()
        yield {
            'eleve_mail': u_eleve.mail_interne,
            'parent_mail': u_parent.mail_interne,
            'matiere_nom': matiere.nom,
        }


# ─── /api/notes ──────────────────────────────────────────────────────────────

class TestGetNotes:
    def test_non_authentifie_retourne_401(self, client):
        r = client.get('/api/notes')
        assert r.status_code == 401

    def test_eleve_voit_ses_notes(self, client, seed):
        _login(client, seed['eleve_mail'])
        r = client.get('/api/notes')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) == 2
        assert data[0]['matiere'] == seed['matiere_nom']
        assert 'note' in data[0]
        assert 'moyenne_classe' in data[0]
        assert 'note_plus_haute' in data[0]
        assert 'note_plus_basse' in data[0]
        assert 'couleur' in data[0]

    def test_parent_voit_notes_de_son_eleve(self, client, seed):
        _login(client, seed['parent_mail'])
        r = client.get('/api/notes')
        assert r.status_code == 200
        assert len(r.get_json()) == 2

    def test_autre_role_retourne_403(self, client, app):
        with app.app_context():
            u = _make_user('employé', 'employe1')
            db.session.add(u)
            db.session.commit()
        _login(client, 'employe1@guardiaschool.fr')
        r = client.get('/api/notes')
        assert r.status_code == 403

    def test_notes_triees_par_date_desc(self, client, seed):
        _login(client, seed['eleve_mail'])
        data = client.get('/api/notes').get_json()
        dates = [d['date_evaluation'] for d in data]
        assert dates == sorted(dates, reverse=True)

    def test_stats_classe_presentes(self, client, seed):
        _login(client, seed['eleve_mail'])
        data = client.get('/api/notes').get_json()
        for note in data:
            assert note['moyenne_classe'] is not None
            assert note['note_plus_haute'] >= note['note_plus_basse']


# ─── /api/notes/trimestre/<n> ─────────────────────────────────────────────────

class TestGetNotesTrimestre:
    def test_trimestre_1_retourne_notes_oct_nov(self, client, seed):
        _login(client, seed['eleve_mail'])
        r = client.get('/api/notes/trimestre/1')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) == 2  # oct + nov

    def test_trimestre_3_retourne_vide(self, client, seed):
        _login(client, seed['eleve_mail'])
        r = client.get('/api/notes/trimestre/3')
        assert r.status_code == 200
        assert r.get_json() == []

    def test_trimestre_invalide_retourne_400(self, client, seed):
        _login(client, seed['eleve_mail'])
        r = client.get('/api/notes/trimestre/5')
        assert r.status_code == 400

    def test_non_authentifie_retourne_401(self, client):
        r = client.get('/api/notes/trimestre/1')
        assert r.status_code == 401


# ─── /api/couleurs-matieres ───────────────────────────────────────────────────

class TestGetCouleurs:
    def test_non_authentifie_retourne_401(self, client):
        r = client.get('/api/couleurs-matieres')
        assert r.status_code == 401

    def test_retourne_dict_matiere_couleur(self, client, seed):
        _login(client, seed['eleve_mail'])
        r = client.get('/api/couleurs-matieres')
        assert r.status_code == 200
        data = r.get_json()
        assert seed['matiere_nom'] in data
        assert data[seed['matiere_nom']].startswith('#')


# ─── Fixture prof ─────────────────────────────────────────────────────────────

@pytest.fixture
def seed_prof(app):
    """
    Cree : 1 classe, 1 matiere, 2 eleves, 1 prof qui enseigne la matiere
    dans la classe (via un Cours), 1 admin.
    """
    with app.app_context():
        classe = Classe(niveau=12, suffixe='B', annee=2026)
        db.session.add(classe)
        db.session.flush()

        matiere = Matiere(nom='Physique')
        db.session.add(matiere)
        db.session.flush()

        # Prof
        u_prof = _make_user('employé', 'prof1')
        db.session.add(u_prof)
        db.session.flush()
        prof = Prof(id_user=u_prof.id)
        db.session.add(prof)
        db.session.flush()

        # Salle minimale pour le Cours
        batiment = Batiment(nom='Bat A')
        db.session.add(batiment)
        db.session.flush()
        etage = Etage(numero=1, id_batiment=batiment.id)
        db.session.add(etage)
        db.session.flush()
        salle = Salle(nom='101', id_etage=etage.id)
        db.session.add(salle)
        db.session.flush()

        # Cours liant prof -> classe -> matiere
        cours = Cours(
            id_matiere=matiere.id,
            id_prof=prof.id,
            id_classe=classe.id,
            debut=datetime(2026, 1, 10, 8, 0),
            fin=datetime(2026, 1, 10, 10, 0),
            etat='planifié',
            id_salle=salle.id,
        )
        db.session.add(cours)

        # 2 eleves dans la classe
        u_e1 = _make_user('élève', 'eleve_a')
        u_e2 = _make_user('élève', 'eleve_b')
        db.session.add_all([u_e1, u_e2])
        db.session.flush()
        e1 = Eleve(id_user=u_e1.id, id_classe=classe.id)
        e2 = Eleve(id_user=u_e2.id, id_classe=classe.id)
        db.session.add_all([e1, e2])

        # Admin
        u_admin = _make_user('administrateur', 'admin1')
        db.session.add(u_admin)

        db.session.commit()
        yield {
            'prof_mail': u_prof.mail_interne,
            'admin_mail': u_admin.mail_interne,
            'classe_id': classe.id,
            'matiere_id': matiere.id,
            'matiere_nom': matiere.nom,
            'eleve1_id': e1.id,
            'eleve2_id': e2.id,
        }


# ─── /api/notes/classes ───────────────────────────────────────────────────────

class TestGetClassesProf:
    def test_non_authentifie_retourne_401(self, client):
        assert client.get('/api/notes/classes').status_code == 401

    def test_eleve_retourne_403(self, client, seed):
        _login(client, seed['eleve_mail'])
        assert client.get('/api/notes/classes').status_code == 403

    def test_prof_voit_ses_classes_et_matieres(self, client, seed_prof):
        _login(client, seed_prof['prof_mail'])
        r = client.get('/api/notes/classes')
        assert r.status_code == 200
        data = r.get_json()
        assert any(c['id'] == seed_prof['classe_id'] for c in data['classes'])
        assert any(m['id'] == seed_prof['matiere_id'] for m in data['matieres'])
        assert {'id_classe': seed_prof['classe_id'], 'id_matiere': seed_prof['matiere_id']} in data['combinaisons']

    def test_admin_voit_tout(self, client, seed_prof):
        _login(client, seed_prof['admin_mail'])
        r = client.get('/api/notes/classes')
        assert r.status_code == 200
        data = r.get_json()
        assert 'classes' in data and 'matieres' in data


# ─── /api/notes/eleves/<classe_id> ───────────────────────────────────────────

class TestGetElevesClasse:
    def test_non_authentifie_retourne_401(self, client, seed_prof):
        assert client.get(f'/api/notes/eleves/{seed_prof["classe_id"]}').status_code == 401

    def test_eleve_retourne_403(self, client, seed):
        _login(client, seed['eleve_mail'])
        assert client.get('/api/notes/eleves/1').status_code == 403

    def test_prof_voit_eleves_de_la_classe(self, client, seed_prof):
        _login(client, seed_prof['prof_mail'])
        r = client.get(f'/api/notes/eleves/{seed_prof["classe_id"]}')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) == 2
        ids = [e['id'] for e in data]
        assert seed_prof['eleve1_id'] in ids
        assert seed_prof['eleve2_id'] in ids

    def test_admin_voit_eleves(self, client, seed_prof):
        _login(client, seed_prof['admin_mail'])
        r = client.get(f'/api/notes/eleves/{seed_prof["classe_id"]}')
        assert r.status_code == 200
        assert len(r.get_json()) == 2


# ─── POST /api/notes/evaluations ─────────────────────────────────────────────

class TestCreateEvaluations:
    def _payload(self, seed_prof, notes=None):
        return {
            'id_classe': seed_prof['classe_id'],
            'id_matiere': seed_prof['matiere_id'],
            'date': '2026-02-01',
            'note_max': 20,
            'coefficient': 1,
            'notes': notes or [
                {'id_eleve': seed_prof['eleve1_id'], 'note': 12},
                {'id_eleve': seed_prof['eleve2_id'], 'note': 15},
            ],
        }

    def test_non_authentifie_retourne_401(self, client):
        assert client.post('/api/notes/evaluations', json={}).status_code == 401

    def test_eleve_retourne_403(self, client, seed, seed_prof):
        _login(client, seed['eleve_mail'])
        assert client.post('/api/notes/evaluations', json=self._payload(seed_prof)).status_code == 403

    def test_prof_cree_evaluations(self, client, seed_prof):
        _login(client, seed_prof['prof_mail'])
        r = client.post('/api/notes/evaluations', json=self._payload(seed_prof))
        assert r.status_code == 201
        assert r.get_json()['created'] == 2

    def test_admin_cree_evaluations(self, client, seed_prof):
        _login(client, seed_prof['admin_mail'])
        r = client.post('/api/notes/evaluations', json=self._payload(seed_prof))
        assert r.status_code == 201

    def test_champs_manquants_retourne_400(self, client, seed_prof):
        _login(client, seed_prof['prof_mail'])
        r = client.post('/api/notes/evaluations', json={'id_classe': seed_prof['classe_id']})
        assert r.status_code == 400

    def test_date_invalide_retourne_400(self, client, seed_prof):
        _login(client, seed_prof['prof_mail'])
        payload = self._payload(seed_prof)
        payload['date'] = 'pas-une-date'
        assert client.post('/api/notes/evaluations', json=payload).status_code == 400

    def test_prof_ne_peut_pas_noter_autre_classe(self, client, seed_prof, seed):
        """Un prof ne peut pas noter une classe qui n'est pas dans ses cours."""
        _login(client, seed_prof['prof_mail'])
        payload = self._payload(seed_prof)
        payload['id_classe'] = 9999
        assert client.post('/api/notes/evaluations', json=payload).status_code == 403

    def test_eleve_hors_classe_ignore(self, client, seed_prof):
        """Un id_eleve n'appartenant pas a la classe est silencieusement ignore."""
        _login(client, seed_prof['prof_mail'])
        payload = self._payload(seed_prof, notes=[
            {'id_eleve': seed_prof['eleve1_id'], 'note': 10},
            {'id_eleve': 9999, 'note': 10},  # eleve inexistant
        ])
        r = client.post('/api/notes/evaluations', json=payload)
        assert r.status_code == 201
        assert r.get_json()['created'] == 1


# ─── PUT /api/notes/evaluations/<id> ─────────────────────────────────────────

class TestUpdateEvaluation:
    @pytest.fixture
    def eval_id(self, client, seed_prof):
        _login(client, seed_prof['prof_mail'])
        r = client.post('/api/notes/evaluations', json={
            'id_classe': seed_prof['classe_id'],
            'id_matiere': seed_prof['matiere_id'],
            'date': '2026-02-01',
            'note_max': 20,
            'coefficient': 1,
            'notes': [{'id_eleve': seed_prof['eleve1_id'], 'note': 10}],
        })
        return r.get_json()['eleves'][0]  # id_eleve cree

    def test_non_authentifie_retourne_401(self, client, app, seed_prof):
        with app.app_context():
            ev = Evaluation(
                id_eleve=seed_prof['eleve1_id'], id_matiere=seed_prof['matiere_id'],
                note=10, note_max=20, coefficient=1, date=datetime(2026, 1, 1)
            )
            db.session.add(ev)
            db.session.commit()
            ev_id = ev.id
        assert client.put(f'/api/notes/evaluations/{ev_id}', json={'note': 15}).status_code == 401

    def test_prof_met_a_jour_la_note(self, client, seed_prof, app):
        with app.app_context():
            ev = Evaluation(
                id_eleve=seed_prof['eleve1_id'], id_matiere=seed_prof['matiere_id'],
                note=10, note_max=20, coefficient=1, date=datetime(2026, 1, 1)
            )
            db.session.add(ev)
            db.session.commit()
            ev_id = ev.id
        _login(client, seed_prof['prof_mail'])
        r = client.put(f'/api/notes/evaluations/{ev_id}', json={'note': 18})
        assert r.status_code == 200
        assert r.get_json()['note'] == 18.0

    def test_evaluation_inexistante_retourne_404(self, client, seed_prof):
        _login(client, seed_prof['prof_mail'])
        assert client.put('/api/notes/evaluations/9999', json={'note': 15}).status_code == 404


# ─── DELETE /api/notes/evaluations/<id> ──────────────────────────────────────

class TestDeleteEvaluation:
    def test_non_authentifie_retourne_401(self, client, app, seed_prof):
        with app.app_context():
            ev = Evaluation(
                id_eleve=seed_prof['eleve1_id'], id_matiere=seed_prof['matiere_id'],
                note=10, note_max=20, coefficient=1, date=datetime(2026, 1, 1)
            )
            db.session.add(ev)
            db.session.commit()
            ev_id = ev.id
        assert client.delete(f'/api/notes/evaluations/{ev_id}').status_code == 401

    def test_prof_supprime_evaluation(self, client, seed_prof, app):
        with app.app_context():
            ev = Evaluation(
                id_eleve=seed_prof['eleve1_id'], id_matiere=seed_prof['matiere_id'],
                note=10, note_max=20, coefficient=1, date=datetime(2026, 1, 1)
            )
            db.session.add(ev)
            db.session.commit()
            ev_id = ev.id
        _login(client, seed_prof['prof_mail'])
        r = client.delete(f'/api/notes/evaluations/{ev_id}')
        assert r.status_code == 200
        assert r.get_json()['deleted'] == ev_id

    def test_evaluation_inexistante_retourne_404(self, client, seed_prof):
        _login(client, seed_prof['prof_mail'])
        assert client.delete('/api/notes/evaluations/9999').status_code == 404

    def test_eleve_ne_peut_pas_supprimer(self, client, seed, app, seed_prof):
        with app.app_context():
            ev = Evaluation(
                id_eleve=seed_prof['eleve1_id'], id_matiere=seed_prof['matiere_id'],
                note=10, note_max=20, coefficient=1, date=datetime(2026, 1, 1)
            )
            db.session.add(ev)
            db.session.commit()
            ev_id = ev.id
        _login(client, seed['eleve_mail'])
        assert client.delete(f'/api/notes/evaluations/{ev_id}').status_code == 403
