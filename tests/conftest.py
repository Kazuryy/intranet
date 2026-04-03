import uuid
import pytest
from datetime import datetime, date, timedelta
from app import bcrypt, create_app
from app.models import db, Direction, User, SessionAuth, Communication, Cours


# ── App & client ──────────────────────────────────────────────────────────────

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


# ── Helper SUID (niveau racine) ───────────────────────────────────────────────

def _creer_suid(app, user_id):
    suid = str(uuid.uuid4())
    with app.app_context():
        db.session.add(SessionAuth(
            suid=suid,
            id_user=user_id,
            expire_le=datetime.now() + timedelta(days=1)
        ))
        db.session.commit()
    return suid


# ── Fixtures utilisateurs génériques ─────────────────────────────────────────

@pytest.fixture
def user(app):
    with app.app_context():
        u = User(
            type='administrateur', nom='Test', prenom='User',
            username='testuser',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield u


@pytest.fixture
def direction(app):
    with app.app_context():
        dir_user = User(
            type='employe', nom='Direction', prenom='Admin',
            username='direction',
            password=bcrypt.generate_password_hash('dirpassword').decode('utf-8')
        )
        db.session.add(dir_user)
        db.session.flush()
        d = Direction(id_user=dir_user.id, role='direction')
        db.session.add(d)
        db.session.commit()
        yield d


##################################################################################################################
# PARTIE TEST DEVOIRS
##################################################################################################################

@pytest.fixture
def prof_suid(app):
    from app.models import Matiere, Prof
    with app.app_context():
        matiere = Matiere(nom='Mathematiques')
        db.session.add(matiere)
        db.session.flush()
        u = User(
            type='employé', nom='Dupont', prenom='Paul',
            username='prof_dupont',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(u)
        db.session.flush()
        p = Prof(id_user=u.id)
        p.matieres.append(matiere)
        db.session.add(p)
        db.session.commit()
        suid = _creer_suid(app, u.id)
        # Retourne un tuple (suid, user_id) — compatible messages ET devoirs
        yield suid, u.id
        db.session.query(SessionAuth).filter_by(suid=suid).delete()
        p_obj = db.session.get(Prof, p.id)
        if p_obj:
            p_obj.matieres.clear()
            db.session.delete(p_obj)
        db.session.query(User).filter_by(id=u.id).delete()
        db.session.query(Matiere).filter_by(id=matiere.id).delete()
        db.session.commit()


@pytest.fixture
def eleve_suid(app):
    from app.models import Classe, Eleve
    with app.app_context():
        classe = Classe(niveau=1, suffixe='A', annee=2026)
        db.session.add(classe)
        db.session.flush()
        u = User(
            type='élève', nom='Martin', prenom='Lea',
            username='eleve_martin',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(u)
        db.session.flush()
        db.session.add(Eleve(id_user=u.id, id_classe=classe.id))
        db.session.commit()
        suid = _creer_suid(app, u.id)
        yield suid, u.id
        db.session.query(SessionAuth).filter_by(suid=suid).delete()
        db.session.query(Eleve).filter_by(id_user=u.id).delete()
        db.session.query(User).filter_by(id=u.id).delete()
        db.session.query(Classe).filter_by(id=classe.id).delete()
        db.session.commit()


@pytest.fixture
def admin_suid(app):
    with app.app_context():
        u = User(
            type='administrateur',
            nom='Admin', prenom='Sys',
            username='admin_sys',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        suid = _creer_suid(app, u.id)
        yield suid, u.id
        db.session.query(SessionAuth).filter_by(suid=suid).delete()
        db.session.query(User).filter_by(id=u.id).delete()
        db.session.commit()


@pytest.fixture
def devoirs(app, prof_suid, eleve_suid):
    from app.models import Devoir, Classe, Matiere, Prof
    today = date.today()
    _, _ = prof_suid   # on ignore les valeurs, les objets sont en BDD
    with app.app_context():
        classe  = Classe.query.filter_by(niveau=1, suffixe='A', annee=2026).first()
        matiere = Matiere.query.filter_by(nom='Mathematiques').first()
        prof    = Prof.query.filter(Prof.matieres.any(id=matiere.id)).first()

        cours = Cours(
            id_matiere=matiere.id,
            id_prof=prof.id,
            id_classe=classe.id,
            debut=datetime.now(),
            fin=datetime.now() + timedelta(hours=2),
            etat='planifie'
        )
        db.session.add(cours)
        db.session.flush()

        specs = [
            ('exercice', -10, 'Passe 1 - exercices chapitre 3'),
            ('controle',  -3, 'Passe 2 - controle flash'),
            ('exercice',  +5, 'A venir 1 - exos p.42'),
            ('expose',   +14, 'A venir 2 - expose sur les integrales'),
            ('projet',   +30, 'A venir 3 - projet de fin de module'),
        ]
        created = []
        for t, delta, consigne in specs:
            d = Devoir(
                id_classe=classe.id,
                id_matiere=matiere.id,
                id_prof=prof.id,
                type=t,
                date_limite=datetime.combine(
                    today + timedelta(days=delta), datetime.min.time()
                ),
                consigne=consigne
            )
            db.session.add(d)
            created.append(d)
        db.session.commit()
        yield created

        for d in created:
            db.session.query(Devoir).filter_by(id=d.id).delete()
        db.session.query(Cours).filter_by(id=cours.id).delete()
        db.session.commit()


##################################################################################################################
# PARTIE TEST MESSAGES
##################################################################################################################

@pytest.fixture
def direction_suid(app):
    with app.app_context():
        u = User(
            type="employé",
            nom="Directeur",
            prenom="Pierre",
            username="pierre.directeur",
            password=bcrypt.generate_password_hash("password123").decode("utf-8")
        )
        db.session.add(u)
        db.session.flush()
        d = Direction(id_user=u.id, role="Proviseur")
        db.session.add(d)
        db.session.commit()
        suid = _creer_suid(app, u.id)   # ← _creer_suid avec user_id
        yield suid, u.id
        db.session.query(SessionAuth).filter_by(suid=suid).delete()
        db.session.query(Direction).filter_by(id_user=u.id).delete()
        db.session.query(User).filter_by(id=u.id).delete()
        db.session.commit()


@pytest.fixture
def message_fixture(app, direction_suid):
    _, id_dir_user = direction_suid
    with app.app_context():
        msg = Communication(
            id_user=id_dir_user,     # ← id_user, pas id_direction
            cible="élève",
            objet="Avis aux élèves",
            contenu="Contenu du test"
        )
        db.session.add(msg)
        db.session.commit()
        yield {"msg_id": msg.id}
        db.session.query(Communication).filter_by(id=msg.id).delete()
        db.session.commit()


@pytest.fixture
def message_fixture_profs(app, direction_suid):
    _, id_dir_user = direction_suid
    with app.app_context():
        msg = Communication(
            id_user=id_dir_user,     # ← id_user, pas id_direction
            cible="prof",            # ← 'prof' pas 'profs'
            objet="Avis aux profs",
            contenu="Réunion pédagogique jeudi."
        )
        db.session.add(msg)
        db.session.commit()
        yield {"msg_id": msg.id}
        db.session.query(Communication).filter_by(id=msg.id).delete()
        db.session.commit()


@pytest.fixture
def cours_fixture(app, prof_suid):
    pytest.skip("blueprint cours pas encore créé")
    from app.models import Matiere, Classe
    _, id_prof = prof_suid
    with app.app_context():
        # Réutilise les objets créés par prof_suid
        matiere = Matiere.query.filter_by(nom='Mathematiques').first()
        classe  = Classe.query.filter_by(niveau=1, suffixe='A', annee=2026).first()

        # Crée une classe si elle n'existe pas encore
        if not classe:
            classe = Classe(niveau=1, suffixe='A', annee=2026)
            db.session.add(classe)
            db.session.flush()

        cours = Cours(
            id_matiere=matiere.id,
            id_prof=id_prof,
            id_classe=classe.id,
            debut=datetime.now() + timedelta(days=1),
            fin=datetime.now()   + timedelta(days=1, hours=2),
            etat='planifie'
        )
        db.session.add(cours)
        db.session.commit()
        yield {"cours_id": cours.id}
        db.session.query(Cours).filter_by(id=cours.id).delete()
        db.session.commit()