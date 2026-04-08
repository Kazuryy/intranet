import pytest
from datetime import datetime
from app import bcrypt
from app.models import (
    Batiment, Classe, Cours, Direction, Eleve, Etage,
    Matiere, Parent, Prof, Salle, User, db
)


@pytest.fixture
def admin(app):
    with app.app_context():
        u = User(
            type='administrateur', nom='Admin', prenom='Test',
            username='admin_edt',
            mail_interne='admin.edt@guardiaschool.fr',
            password=bcrypt.generate_password_hash('adminpass').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield u


@pytest.fixture
def direction_user(app):
    with app.app_context():
        u = User(
            type='employé', nom='Dir', prenom='Chef',
            username='dir_edt',
            mail_interne='dir.edt@guardiaschool.fr',
            password=bcrypt.generate_password_hash('dirpass').decode('utf-8')
        )
        db.session.add(u)
        db.session.flush()
        db.session.add(Direction(id_user=u.id))
        db.session.commit()
        yield u


@pytest.fixture
def setup(app):
    """Crée matière, classe, prof, salle et un cours."""
    with app.app_context():
        matiere = Matiere(nom='Mathématiques')
        db.session.add(matiere)

        classe = Classe(niveau=1, suffixe='A', annee=2026)
        db.session.add(classe)

        prof_user = User(
            type='employé', nom='Prof', prenom='Jean',
            username='jprof',
            mail_interne='jean.prof@guardiaschool.fr',
            password=bcrypt.generate_password_hash('profpass').decode('utf-8')
        )
        db.session.add(prof_user)
        db.session.flush()

        prof = Prof(id_user=prof_user.id)
        db.session.add(prof)

        batiment = Batiment(nom='Bâtiment A')
        db.session.add(batiment)
        db.session.flush()

        etage = Etage(numero=1, id_batiment=batiment.id)
        db.session.add(etage)
        db.session.flush()

        salle = Salle(nom='A101', id_etage=etage.id)
        db.session.add(salle)
        db.session.flush()

        cours = Cours(
            id_matiere=matiere.id,
            id_prof=prof.id,
            id_classe=classe.id,
            debut=datetime(2026, 4, 7, 8, 0),
            fin=datetime(2026, 4, 7, 10, 0),
            etat='planifie',
            id_salle=salle.id
        )
        db.session.add(cours)
        db.session.commit()

        yield {
            'matiere': matiere,
            'classe': classe,
            'prof': prof,
            'prof_user': prof_user,
            'salle': salle,
            'cours': cours,
        }


@pytest.fixture
def eleve_user(app, setup):
    with app.app_context():
        u = User(
            type='élève', nom='Dupont', prenom='Jean',
            username='jdupont_edt',
            mail_interne='jean.dupont.edt@guardiaschool.fr',
            password=bcrypt.generate_password_hash('elevepass').decode('utf-8')
        )
        db.session.add(u)
        db.session.flush()
        eleve = Eleve(id_user=u.id, id_classe=setup['classe'].id)
        db.session.add(eleve)
        db.session.commit()
        yield u


@pytest.fixture
def parent_user(app, setup, eleve_user):
    with app.app_context():
        eleve = Eleve.query.filter_by(id_user=eleve_user.id).first()
        u = User(
            type='parent', nom='Dupont', prenom='Marie',
            username='mdupont_edt',
            mail_interne='marie.dupont.edt@guardiaschool.fr',
            password=bcrypt.generate_password_hash('parentpass').decode('utf-8')
        )
        db.session.add(u)
        db.session.flush()
        parent = Parent(id_user=u.id, id_eleve=eleve.id)
        db.session.add(parent)
        db.session.commit()
        yield u


# --- GET /edt/cours ---

def test_list_cours_admin(client, admin, setup):
    # admin voit tous les cours
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/edt/cours')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_list_cours_eleve_scope(client, eleve_user, setup):
    # élève voit uniquement les cours de sa classe
    client.post('/auth/login', json={
        'email': 'jean.dupont.edt@guardiaschool.fr', 'password': 'elevepass'
    })
    response = client.get('/edt/cours')
    assert response.status_code == 200
    data = response.get_json()
    assert all(c['classe']['id'] == setup['classe'].id for c in data)


def test_list_cours_parent_scope(client, parent_user, setup):
    # parent voit les cours de la classe de son enfant
    client.post('/auth/login', json={
        'email': 'marie.dupont.edt@guardiaschool.fr', 'password': 'parentpass'
    })
    response = client.get('/edt/cours')
    assert response.status_code == 200
    data = response.get_json()
    assert all(c['classe']['id'] == setup['classe'].id for c in data)


def test_list_cours_direction_sees_all(client, direction_user, setup):
    # direction voit tous les cours sans restriction
    client.post('/auth/login', json={
        'email': 'dir.edt@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.get('/edt/cours')
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_list_cours_filter_debut(client, admin, setup):
    # filtre par debut : aucun cours après le 8 avril
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/edt/cours?debut=2026-04-08T00:00:00')
    assert response.status_code == 200
    assert response.get_json() == []


def test_list_cours_invalid_date(client, admin, setup):
    # date invalide en querystring => 400
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/edt/cours?debut=pas-une-date')
    assert response.status_code == 400


def test_list_cours_prof_scope(client, setup):
    # prof voit uniquement ses propres cours
    client.post('/auth/login', json={
        'email': 'jean.prof@guardiaschool.fr', 'password': 'profpass'
    })
    response = client.get('/edt/cours')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['prof']['id'] == setup['prof'].id


def test_list_cours_unauthenticated(client):
    response = client.get('/edt/cours')
    assert response.status_code == 401


# --- POST /edt/cours ---

def test_create_cours_success(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['etat'] == 'planifie'
    assert data['matiere']['nom'] == 'Mathématiques'


def test_create_cours_missing_fields(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
    })
    assert response.status_code == 400


def test_create_cours_fin_before_debut(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T10:00:00',
        'fin': '2026-04-08T08:00:00',
    })
    assert response.status_code == 400


def test_create_cours_invalid_etat(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
        'etat': 'inconnu',
    })
    assert response.status_code == 400


def test_create_cours_non_direction_forbidden(client, app, setup):
    # employé non-direction => 403
    with app.app_context():
        u = User(
            type='employé', nom='Cantine', prenom='Agent',
            username='cantine_edt',
            mail_interne='cantine.edt@guardiaschool.fr',
            password=bcrypt.generate_password_hash('cantinepass').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
    client.post('/auth/login', json={
        'email': 'cantine.edt@guardiaschool.fr', 'password': 'cantinepass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
    })
    assert response.status_code == 403


def test_create_cours_direction_allowed(client, direction_user, setup):
    client.post('/auth/login', json={
        'email': 'dir.edt@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
    })
    assert response.status_code == 201


def test_create_cours_eleve_forbidden(client, eleve_user, setup):
    client.post('/auth/login', json={
        'email': 'jean.dupont.edt@guardiaschool.fr', 'password': 'elevepass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
    })
    assert response.status_code == 403


def test_create_cours_unauthenticated(client, setup):
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
    })
    assert response.status_code == 401


# --- PATCH /edt/cours/<id> ---

def test_update_cours_success(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'etat': 'annule'
    })
    assert response.status_code == 200
    assert response.get_json()['etat'] == 'annule'


def test_update_cours_not_found(client, admin):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch('/edt/cours/9999', json={'etat': 'annule'})
    assert response.status_code == 404


def test_update_cours_no_fields(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={})
    assert response.status_code == 400


def test_update_cours_direction_allowed(client, direction_user, setup):
    client.post('/auth/login', json={
        'email': 'dir.edt@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'etat': 'annule'
    })
    assert response.status_code == 200


def test_update_cours_partial_debut_only(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'debut': '2026-04-07T09:00:00',
    })
    assert response.status_code == 200
    assert response.get_json()['debut'].startswith('2026-04-07T09:00:00')


def test_update_cours_partial_fin_only(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'fin': '2026-04-07T11:00:00',
    })
    assert response.status_code == 200
    assert response.get_json()['fin'].startswith('2026-04-07T11:00:00')


def test_update_cours_forbidden(client, eleve_user, setup):
    client.post('/auth/login', json={
        'email': 'jean.dupont.edt@guardiaschool.fr', 'password': 'elevepass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={'etat': 'annule'})
    assert response.status_code == 403


# --- DELETE /edt/cours/<id> ---

def test_delete_cours_success(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.delete(f'/edt/cours/{setup["cours"].id}')
    assert response.status_code == 200


def test_delete_cours_not_found(client, admin):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.delete('/edt/cours/9999')
    assert response.status_code == 404


def test_delete_cours_direction_allowed(client, direction_user, setup):
    client.post('/auth/login', json={
        'email': 'dir.edt@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.delete(f'/edt/cours/{setup["cours"].id}')
    assert response.status_code == 200


def test_delete_cours_forbidden(client, eleve_user, setup):
    client.post('/auth/login', json={
        'email': 'jean.dupont.edt@guardiaschool.fr', 'password': 'elevepass'
    })
    response = client.delete(f'/edt/cours/{setup["cours"].id}')
    assert response.status_code == 403


def test_delete_cours_unauthenticated(client, setup):
    response = client.delete(f'/edt/cours/{setup["cours"].id}')
    assert response.status_code == 401


@pytest.fixture
def employe_user(app):
    """Employé non-direction (ex: cantine)."""
    with app.app_context():
        u = User(
            type='employé', nom='Cantine', prenom='Agent',
            username='cantine_edt2',
            mail_interne='cantine2.edt@guardiaschool.fr',
            password=bcrypt.generate_password_hash('cantinepass2').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield u


# --- GET /edt/cours : cas limites de scope ---

def test_list_cours_eleve_without_classe(client, app, setup):
    # élève sans classe assignée => liste vide
    with app.app_context():
        u = User(
            type='élève', nom='Orphelin', prenom='Eleve',
            username='orphelin_edt',
            mail_interne='orphelin.edt@guardiaschool.fr',
            password=bcrypt.generate_password_hash('orphelinpass').decode('utf-8')
        )
        db.session.add(u)
        db.session.flush()
        db.session.add(Eleve(id_user=u.id, id_classe=None))
        db.session.commit()
    client.post('/auth/login', json={
        'email': 'orphelin.edt@guardiaschool.fr', 'password': 'orphelinpass'
    })
    response = client.get('/edt/cours')
    assert response.status_code == 200
    assert response.get_json() == []


def test_list_cours_employe_not_prof(client, employe_user):
    # employé non-direction qui n'est pas prof => liste vide
    client.post('/auth/login', json={
        'email': 'cantine2.edt@guardiaschool.fr', 'password': 'cantinepass2'
    })
    response = client.get('/edt/cours')
    assert response.status_code == 200
    assert response.get_json() == []


def test_list_cours_admin_filter_classe(client, admin, setup):
    # admin filtre par classe_id => log déclenché
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get(f'/edt/cours?classe_id={setup["classe"].id}')
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_list_cours_admin_filter_prof(client, admin, setup):
    # admin filtre par prof_id
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get(f'/edt/cours?prof_id={setup["prof"].id}')
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_list_cours_direction_filter_classe(client, direction_user, setup):
    # direction filtre par classe_id
    client.post('/auth/login', json={
        'email': 'dir.edt@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.get(f'/edt/cours?classe_id={setup["classe"].id}')
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_list_cours_direction_filter_prof(client, direction_user, setup):
    # direction filtre par prof_id
    client.post('/auth/login', json={
        'email': 'dir.edt@guardiaschool.fr', 'password': 'dirpass'
    })
    response = client.get(f'/edt/cours?prof_id={setup["prof"].id}')
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_list_cours_invalid_fin_date(client, admin):
    # date fin invalide en querystring => 400
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/edt/cours?fin=pas-une-date')
    assert response.status_code == 400


# --- POST /edt/cours : cas limites ---

def test_create_cours_no_json(client, admin):
    # pas de JSON => 400
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post(
        '/edt/cours', data='notjson', content_type='text/plain'
    )
    assert response.status_code == 400


def test_create_cours_invalid_date_format(client, admin, setup):
    # format de date invalide => 400
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': 'pas-une-date',
        'fin': '2026-04-08T10:00:00',
    })
    assert response.status_code == 400


def test_create_cours_matiere_not_found(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': 9999,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
    })
    assert response.status_code == 404


def test_create_cours_prof_not_found(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': 9999,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
    })
    assert response.status_code == 404


def test_create_cours_classe_not_found(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': 9999,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
    })
    assert response.status_code == 404


def test_create_cours_salle_not_found(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.post('/edt/cours', json={
        'id_matiere': setup['matiere'].id,
        'id_prof': setup['prof'].id,
        'id_classe': setup['classe'].id,
        'debut': '2026-04-08T08:00:00',
        'fin': '2026-04-08T10:00:00',
        'id_salle': 9999,
    })
    assert response.status_code == 404


# --- PATCH /edt/cours : cas limites ---

def test_update_cours_non_direction_forbidden(client, employe_user, setup):
    # employé non-direction => 403
    client.post('/auth/login', json={
        'email': 'cantine2.edt@guardiaschool.fr', 'password': 'cantinepass2'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'etat': 'annule'
    })
    assert response.status_code == 403


def test_update_cours_no_json(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(
        f'/edt/cours/{setup["cours"].id}',
        data='notjson', content_type='text/plain'
    )
    assert response.status_code == 400


def test_update_cours_invalid_date(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'debut': 'pas-une-date',
        'fin': '2026-04-07T11:00:00',
    })
    assert response.status_code == 400


def test_update_cours_fin_before_debut(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'debut': '2026-04-07T10:00:00',
        'fin': '2026-04-07T08:00:00',
    })
    assert response.status_code == 400


def test_update_cours_matiere_not_found(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'id_matiere': 9999
    })
    assert response.status_code == 404


def test_update_cours_prof_not_found(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'id_prof': 9999
    })
    assert response.status_code == 404


def test_update_cours_classe_not_found(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'id_classe': 9999
    })
    assert response.status_code == 404


def test_update_cours_salle_not_found(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'id_salle': 9999
    })
    assert response.status_code == 404


def test_update_cours_invalid_etat(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.patch(f'/edt/cours/{setup["cours"].id}', json={
        'etat': 'inconnu'
    })
    assert response.status_code == 400


# --- DELETE /edt/cours : cas limites ---

def test_delete_cours_non_direction_forbidden(client, employe_user, setup):
    # employé non-direction => 403
    client.post('/auth/login', json={
        'email': 'cantine2.edt@guardiaschool.fr', 'password': 'cantinepass2'
    })
    response = client.delete(f'/edt/cours/{setup["cours"].id}')
    assert response.status_code == 403


# --- GET /edt/matieres, /edt/classes, /edt/profs, /edt/salles ---

def test_list_matieres_admin(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/edt/matieres')
    assert response.status_code == 200
    assert any(m['nom'] == 'Mathématiques' for m in response.get_json())


def test_list_matieres_non_direction_forbidden(client, employe_user):
    client.post('/auth/login', json={
        'email': 'cantine2.edt@guardiaschool.fr', 'password': 'cantinepass2'
    })
    response = client.get('/edt/matieres')
    assert response.status_code == 403


def test_list_classes_admin(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/edt/classes')
    assert response.status_code == 200
    assert len(response.get_json()) >= 1


def test_list_classes_non_direction_forbidden(client, employe_user):
    client.post('/auth/login', json={
        'email': 'cantine2.edt@guardiaschool.fr', 'password': 'cantinepass2'
    })
    response = client.get('/edt/classes')
    assert response.status_code == 403


def test_list_profs_admin(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/edt/profs')
    assert response.status_code == 200
    assert len(response.get_json()) >= 1


def test_list_profs_non_direction_forbidden(client, employe_user):
    client.post('/auth/login', json={
        'email': 'cantine2.edt@guardiaschool.fr', 'password': 'cantinepass2'
    })
    response = client.get('/edt/profs')
    assert response.status_code == 403


def test_list_salles_admin(client, admin, setup):
    client.post('/auth/login', json={
        'email': 'admin.edt@guardiaschool.fr', 'password': 'adminpass'
    })
    response = client.get('/edt/salles')
    assert response.status_code == 200
    assert len(response.get_json()) >= 1


def test_list_salles_non_direction_forbidden(client, employe_user):
    client.post('/auth/login', json={
        'email': 'cantine2.edt@guardiaschool.fr', 'password': 'cantinepass2'
    })
    response = client.get('/edt/salles')
    assert response.status_code == 403
