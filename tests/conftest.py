import pytest
from datetime import datetime, date, timedelta
from app import bcrypt, create_app
from app.models import Direction, User
from app.models import db


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


# ── Fixtures auth ─────────────────────────────────────────────────────────────

@pytest.fixture
def user(app):
    with app.app_context():
        u = User(
            type='administrateur', nom='Test', prenom='User',
            username='testuser',
            mail_interne='user.test@guardiaschool.fr',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield u


@pytest.fixture
def direction(app):
    with app.app_context():
        dir_user = User(
            type='employé', nom='Direction', prenom='Admin',
            username='direction',
            mail_interne='admin.direction@guardiaschool.fr',
            password=bcrypt.generate_password_hash('dirpassword').decode('utf-8')
        )
        db.session.add(dir_user)
        db.session.flush()
        d = Direction(id_user=dir_user.id, role='direction')
        db.session.add(d)
        db.session.commit()
        yield d


# ── Fixtures devoirs ──────────────────────────────────────────────────────────

@pytest.fixture
def prof_devoirs(app):
    from app.models import Matiere, Prof
    with app.app_context():
        matiere = Matiere(nom='Mathematiques')
        db.session.add(matiere)
        db.session.flush()
        u = User(
            type='employé', nom='Dupont', prenom='Paul',
            username='prof_dupont',
            mail_interne='paul.dupont@guardiaschool.fr',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(u)
        db.session.flush()
        p = Prof(id_user=u.id)
        p.matieres.append(matiere)
        db.session.add(p)
        db.session.commit()
        yield {'mail': u.mail_interne, 'prof_id': p.id, 'matiere_id': matiere.id}


@pytest.fixture
def eleve_devoirs(app):
    from app.models import Classe, Eleve
    with app.app_context():
        classe = Classe(niveau=1, suffixe='A', annee=2026)
        db.session.add(classe)
        db.session.flush()
        u = User(
            type='élève', nom='Martin', prenom='Lea',
            username='eleve_martin',
            mail_interne='lea.martin@guardiaschool.fr',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(u)
        db.session.flush()
        db.session.add(Eleve(id_user=u.id, id_classe=classe.id))
        db.session.commit()
        yield {'mail': u.mail_interne, 'classe_id': classe.id}


@pytest.fixture
def admin_devoirs(app):
    with app.app_context():
        u = User(
            type='administrateur', nom='Admin', prenom='Sys',
            username='admin_sys',
            mail_interne='sys.admin@guardiaschool.fr',
            password=bcrypt.generate_password_hash('password123').decode('utf-8')
        )
        db.session.add(u)
        db.session.commit()
        yield {'mail': u.mail_interne}


@pytest.fixture
def cours_devoirs(app, prof_devoirs, eleve_devoirs):
    """Cours liant le prof à la classe de l'élève — requis pour créer des devoirs."""
    from app.models import Classe, Matiere, Prof, Cours
    with app.app_context():
        classe = Classe.query.filter_by(niveau=1, suffixe='A', annee=2026).first()
        matiere = Matiere.query.filter_by(nom='Mathematiques').first()
        prof = Prof.query.filter(Prof.matieres.any(id=matiere.id)).first()
        cours = Cours(
            id_matiere=matiere.id,
            id_prof=prof.id,
            id_classe=classe.id,
            debut=datetime.now(),
            fin=datetime.now() + timedelta(hours=2),
            etat='planifie'
        )
        db.session.add(cours)
        db.session.commit()
        yield {'cours_id': cours.id, 'classe_id': classe.id, 'matiere_id': matiere.id}
        db.session.query(Cours).filter_by(id=cours.id).delete()
        db.session.commit()


@pytest.fixture
def devoirs(app, cours_devoirs, prof_devoirs, eleve_devoirs):
    """5 devoirs : 2 passes, 3 futurs."""
    from app.models import Devoir, Classe, Matiere, Prof
    today = date.today()
    with app.app_context():
        classe = Classe.query.filter_by(niveau=1, suffixe='A', annee=2026).first()
        matiere = Matiere.query.filter_by(nom='Mathematiques').first()
        prof = Prof.query.filter(Prof.matieres.any(id=matiere.id)).first()

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
        db.session.commit()
