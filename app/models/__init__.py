from datetime import datetime, timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


prof_matiere = db.Table(
    'prof_matiere',
    db.Column('id_prof', db.Integer, db.ForeignKey('prof.id'), primary_key=True),
    db.Column('id_matiere', db.Integer, db.ForeignKey('matiere.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(
        db.Enum('élève', 'employé', 'parent', 'administrateur'),
        nullable=False
    )
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    mail_interne = db.Column(db.String(150), unique=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class Information(db.Model):
    __tablename__ = 'information'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    numero = db.Column(db.String(15))
    mail = db.Column(db.String(150))
    adresse = db.Column(db.String(255))


class Direction(db.Model):
    __tablename__ = 'direction'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    role = db.Column(db.String(100))


class Matiere(db.Model):
    __tablename__ = 'matiere'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)


class Prof(db.Model):
    __tablename__ = 'prof'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    matieres = db.relationship('Matiere', secondary=prof_matiere, backref='profs')


class Classe(db.Model):
    __tablename__ = 'classe'

    id = db.Column(db.Integer, primary_key=True)
    niveau = db.Column(db.Integer, nullable=False)
    suffixe = db.Column(db.String(10))
    annee = db.Column(db.Integer, nullable=False)
    id_prof_principal = db.Column(
        db.Integer, db.ForeignKey('prof.id', ondelete='SET NULL'), nullable=True
    )


class Eleve(db.Model):
    __tablename__ = 'eleve'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    id_classe = db.Column(
        db.Integer, db.ForeignKey('classe.id', ondelete='RESTRICT'), nullable=True
    )
    id_responsable = db.Column(
        db.Integer,
        db.ForeignKey(
            'parent.id', ondelete='SET NULL',
            use_alter=True, name='fk_eleve_responsable'
        ),
        nullable=True
    )
    groupe = db.Column(db.String(1))
    date_naissance = db.Column(db.Date)


class Parent(db.Model):
    __tablename__ = 'parent'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    id_eleve = db.Column(
        db.Integer, db.ForeignKey('eleve.id', ondelete='CASCADE'), nullable=False
    )
    id_information = db.Column(
        db.Integer, db.ForeignKey('information.id', ondelete='SET NULL'), nullable=True
    )


class Employe(db.Model):
    __tablename__ = 'employe'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    role = db.Column(db.String(100))


class Batiment(db.Model):
    __tablename__ = 'batiment'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)


class Etage(db.Model):
    __tablename__ = 'etage'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    id_batiment = db.Column(
        db.Integer, db.ForeignKey('batiment.id', ondelete='CASCADE'), nullable=False
    )


class Salle(db.Model):
    __tablename__ = 'salle'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    id_etage = db.Column(
        db.Integer, db.ForeignKey('etage.id', ondelete='CASCADE'), nullable=False
    )


class Evenement(db.Model):
    __tablename__ = 'evenement'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(150), nullable=False)
    responsable = db.Column(db.String(150))
    date = db.Column(db.DateTime, nullable=False)
    invites = db.Column(db.Text)


class Menu(db.Model):
    __tablename__ = 'menu'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    entree = db.Column(db.String(150))
    plat = db.Column(db.String(150))
    dessert = db.Column(db.String(150))
    special = db.Column(db.Boolean, default=False)
    special_info = db.Column(db.String(255))
    id_evenement = db.Column(
        db.Integer, db.ForeignKey('evenement.id', ondelete='SET NULL'), nullable=True
    )


class Cours(db.Model):
    __tablename__ = 'cours'

    id = db.Column(db.Integer, primary_key=True)
    id_matiere = db.Column(
        db.Integer, db.ForeignKey('matiere.id', ondelete='RESTRICT'), nullable=False
    )
    id_prof = db.Column(
        db.Integer, db.ForeignKey('prof.id', ondelete='RESTRICT'), nullable=False
    )
    id_classe = db.Column(
        db.Integer, db.ForeignKey('classe.id', ondelete='CASCADE'), nullable=False
    )
    debut = db.Column(db.DateTime, nullable=False)
    fin = db.Column(db.DateTime, nullable=False)
    etat = db.Column(
        db.Enum('planifie', 'en cours', 'termine', 'annule'),
        nullable=False,
        default='planifie'
    )
    id_salle = db.Column(
        db.Integer, db.ForeignKey('salle.id', ondelete='SET NULL'), nullable=True
    )


class Devoir(db.Model):
    __tablename__ = 'devoir'

    id = db.Column(db.Integer, primary_key=True)
    id_classe = db.Column(
        db.Integer, db.ForeignKey('classe.id', ondelete='CASCADE'), nullable=False
    )
    id_matiere = db.Column(
        db.Integer, db.ForeignKey('matiere.id', ondelete='RESTRICT'), nullable=False
    )
    type = db.Column(
        db.Enum(
            'exercice', 'controle', 'expose',
            'projet', 'soutenance', 'autre'
        ),
        nullable=False
    )
    date_limite = db.Column(db.DateTime, nullable=False)
    consigne = db.Column(db.Text)
    id_prof = db.Column(
        db.Integer, db.ForeignKey('prof.id', ondelete='RESTRICT'), nullable=False
    )


class DevoirStatus(db.Model):
    __tablename__ = 'devoir_status'

    id = db.Column(db.Integer, primary_key=True)
    id_devoir = db.Column(
        db.Integer, db.ForeignKey('devoir.id', ondelete='CASCADE'), nullable=False
    )
    id_eleve = db.Column(
        db.Integer, db.ForeignKey('eleve.id', ondelete='CASCADE'), nullable=False
    )
    status = db.Column(db.Boolean, default=False)
    fichier = db.Column(db.String(255))


class Evaluation(db.Model):
    __tablename__ = 'evaluation'

    id = db.Column(db.Integer, primary_key=True)
    id_eleve = db.Column(
        db.Integer, db.ForeignKey('eleve.id', ondelete='CASCADE'), nullable=False
    )
    id_matiere = db.Column(
        db.Integer, db.ForeignKey('matiere.id', ondelete='RESTRICT'), nullable=False
    )
    note = db.Column(db.Numeric(4, 2), nullable=False)
    note_max = db.Column(db.Numeric(4, 2), nullable=False, default=20)
    coefficient = db.Column(db.Integer, nullable=False, default=1)
    date = db.Column(db.DateTime, nullable=False)


class Mail(db.Model):
    __tablename__ = 'mail'

    id = db.Column(db.Integer, primary_key=True)
    id_expediteur = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    id_destinataire = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    objet = db.Column(db.String(255))
    contenu = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False, server_default=db.func.now())


class Communication(db.Model):
    __tablename__ = 'communication'

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    cible = db.Column(
        db.Enum('parent', 'élève', 'prof', 'tous', 'classe'), nullable=False
    )
    id_cible = db.Column(db.Integer)
    objet = db.Column(db.String(255))
    contenu = db.Column(db.Text)
    date_debut = db.Column(db.DateTime)
    date_fin = db.Column(db.DateTime)


class Assiduite(db.Model):
    __tablename__ = 'assiduite'

    id = db.Column(db.Integer, primary_key=True)
    id_eleve = db.Column(
        db.Integer, db.ForeignKey('eleve.id', ondelete='CASCADE'), nullable=False
    )
    id_responsable = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='RESTRICT'), nullable=False
    )
    type = db.Column(
        db.Enum('absent', 'retard', 'présent', 'excusé'), nullable=False
    )
    date = db.Column(db.DateTime, nullable=False)


class Log(db.Model):
    __tablename__ = 'log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True
    )
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
class SessionAuth(db.Model):
    __tablename__ = 'session'
    id        = db.Column(db.Integer, primary_key=True)
    suid      = db.Column(db.String(36), unique=True, nullable=False)
    id_user   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expire_le = db.Column(db.DateTime, nullable=False)
