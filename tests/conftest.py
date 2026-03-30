import pytest
from app import bcrypt, create_app
from app.models import Direction, User, db


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


@pytest.fixture
def user(app):
    with app.app_context():
        u = User(
            type='administrateur',
            nom='Test',
            prenom='User',
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
            type='employé',
            nom='Direction',
            prenom='Admin',
            username='direction',
            password=bcrypt.generate_password_hash('dirpassword').decode('utf-8')
        )
        db.session.add(dir_user)
        db.session.flush()
        d = Direction(id_user=dir_user.id, role='direction')
        db.session.add(d)
        db.session.commit()
        yield d
