# app/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

prof_matiere = db.Table('prof_matiere',
    db.Column('id_prof',    db.Integer, db.ForeignKey('prof.id'),    primary_key=True),
    db.Column('id_matiere', db.Integer, db.ForeignKey('matiere.id'), primary_key=True),
)

class User(db.Model):
    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key=True)
    type     = db.Column(db.String(50), nullable=False)
    nom      = db.Column(db.String(100))
    prenom   = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class SessionAuth(db.Model):
    __tablename__ = 'session'
    id        = db.Column(db.Integer, primary_key=True)
    suid      = db.Column(db.String(36), unique=True, nullable=False)
    id_user   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expire_le = db.Column(db.DateTime, nullable=False)

class Matiere(db.Model):
    __tablename__ = 'matiere'
    id  = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

class Prof(db.Model):
    __tablename__ = 'prof'
    id      = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    matieres = db.relationship('Matiere', secondary=prof_matiere, backref='profs')

class Classe(db.Model):
    __tablename__ = 'classe'
    id      = db.Column(db.Integer, primary_key=True)
    niveau  = db.Column(db.Integer, nullable=False)
    suffixe = db.Column(db.String(10))
    annee   = db.Column(db.Integer)

class Eleve(db.Model):
    __tablename__ = 'eleve'
    id_user   = db.Column(db.Integer, db.ForeignKey('user.id'),   primary_key=True)
    id_classe = db.Column(db.Integer, db.ForeignKey('classe.id'), primary_key=True)

class Direction(db.Model):
    __tablename__ = 'direction'
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    role    = db.Column(db.String(50))

class Devoir(db.Model):
    __tablename__ = 'devoir'
    id         = db.Column(db.Integer, primary_key=True)
    id_classe  = db.Column(db.Integer, db.ForeignKey('classe.id'),  nullable=False)
    id_matiere = db.Column(db.Integer, db.ForeignKey('matiere.id'), nullable=False)
    id_prof    = db.Column(db.Integer, db.ForeignKey('prof.id'),    nullable=False)
    type       = db.Column(db.String(50), nullable=False)
    date_limite = db.Column(db.DateTime, nullable=False)
    consigne   = db.Column(db.Text, nullable=False)

class Cours(db.Model):
    __tablename__ = 'cours'
    id         = db.Column(db.Integer, primary_key=True)
    id_matiere = db.Column(db.Integer, db.ForeignKey('matiere.id'), nullable=False)
    id_prof    = db.Column(db.Integer, db.ForeignKey('prof.id'),    nullable=False)
    id_classe  = db.Column(db.Integer, db.ForeignKey('classe.id'),  nullable=False)
    debut      = db.Column(db.DateTime)
    fin        = db.Column(db.DateTime)
    etat       = db.Column(db.String(50))
    
class Information(db.Model):
    __tablename__ = 'information'
    id      = db.Column(db.Integer, primary_key=True)
    titre   = db.Column(db.String(255))
    contenu = db.Column(db.Text)
    date    = db.Column(db.DateTime)

class Log(db.Model):
    __tablename__ = 'log'
    id      = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    action  = db.Column(db.String(255))
    date    = db.Column(db.DateTime)

class Mail(db.Model):
    __tablename__ = 'mail'
    id         = db.Column(db.Integer, primary_key=True)
    id_user    = db.Column(db.Integer, db.ForeignKey('user.id'))
    sujet      = db.Column(db.String(255))
    contenu    = db.Column(db.Text)
    date_envoi = db.Column(db.DateTime)