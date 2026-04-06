"""
Seed script - genere des donnees de test realistes en DB.
Usage : python3 seed.py [--reset]

  --reset  vide les tables avant d'inserer (ne supprime pas le schema)
"""
import sys
from datetime import datetime, timedelta
import random

from app import bcrypt, create_app
from app.models import (
    db, User, Direction, Prof, Eleve, Parent, Employe,
    Classe, Matiere, Cours, Evaluation, Batiment, Etage, Salle,
)

RESET = '--reset' in sys.argv

app = create_app()

# ─── Donnees ──────────────────────────────────────────────────────────────────

MATIERES = [
    'Mathematiques', 'Physique-Chimie', 'Francais',
    'Histoire-Geographie', 'Anglais', 'Informatique',
    'Philosophie', 'SVT', 'EPS',
]

CLASSES = [
    {'niveau': 10, 'suffixe': 'A', 'annee': 2026},
    {'niveau': 10, 'suffixe': 'B', 'annee': 2026},
    {'niveau': 11, 'suffixe': 'A', 'annee': 2026},
    {'niveau': 12, 'suffixe': 'A', 'annee': 2026},
    {'niveau': 12, 'suffixe': 'B', 'annee': 2026},
]

PROFS_DATA = [
    {'nom': 'Dupont',  'prenom': 'Marc',    'matieres': ['Mathematiques', 'Physique-Chimie']},
    {'nom': 'Leroy',   'prenom': 'Sophie',  'matieres': ['Francais', 'Philosophie']},
    {'nom': 'Martin',  'prenom': 'Pierre',  'matieres': ['Histoire-Geographie', 'Anglais']},
    {'nom': 'Bernard', 'prenom': 'Claire',  'matieres': ['Informatique', 'Mathematiques']},
    {'nom': 'Moreau',  'prenom': 'Julie',   'matieres': ['SVT', 'EPS']},
]

ELEVES_DATA = [
    {'nom': 'Dubois',    'prenom': 'Lucas'},
    {'nom': 'Petit',     'prenom': 'Emma'},
    {'nom': 'Robert',    'prenom': 'Noah'},
    {'nom': 'Richard',   'prenom': 'Lea'},
    {'nom': 'Thomas',    'prenom': 'Hugo'},
    {'nom': 'Simon',     'prenom': 'Camille'},
    {'nom': 'Laurent',   'prenom': 'Antoine'},
    {'nom': 'Michel',    'prenom': 'Chloe'},
    {'nom': 'Garcia',    'prenom': 'Raphael'},
    {'nom': 'Martinez',  'prenom': 'Manon'},
    {'nom': 'Lefebvre',  'prenom': 'Ethan'},
    {'nom': 'Roux',      'prenom': 'Inès'},
    {'nom': 'Fontaine',  'prenom': 'Tom'},
    {'nom': 'Chevalier', 'prenom': 'Jade'},
    {'nom': 'Bonnet',    'prenom': 'Louis'},
]

BATIMENTS = ['Batiment A', 'Batiment B']
SALLES_PAR_BATIMENT = [
    ['101', '102', '103', '201', '202'],
    ['Labo 1', 'Labo 2', 'Salle Info', 'Gymnase'],
]


def make_mail(prenom, nom, suffix=''):
    base = f"{prenom.lower()}.{nom.lower()}{suffix}".replace('-', '').replace(' ', '')
    return f"{base}@guardiaschool.fr"


def make_username(prenom, nom, suffix=''):
    return f"{prenom.lower()}.{nom.lower()}{suffix}".replace('-', '').replace(' ', '')


def hash_pwd(pwd):
    return bcrypt.generate_password_hash(pwd).decode('utf-8')


# ─── Reset ────────────────────────────────────────────────────────────────────

def reset_tables():
    print("  Suppression des donnees existantes...")
    for model in [Evaluation, Cours, Eleve, Parent, Prof, Direction, Employe,
                  Salle, Etage, Batiment, Matiere, Classe, User]:
        db.session.query(model).delete()
    db.session.commit()
    print("  Tables videes.")


# ─── Creation ─────────────────────────────────────────────────────────────────

def seed():
    with app.app_context():
        db.create_all()

        if RESET:
            reset_tables()

        print("\n[1/8] Admin...")
        admin_user = User(
            type='administrateur', nom='Admin', prenom='Guardia',
            username='admin',
            mail_interne='admin@guardiaschool.fr',
            password=hash_pwd('admin'),
            is_active=True,
        )
        db.session.add(admin_user)
        db.session.flush()
        print(f"  admin@guardiaschool.fr  /  admin")

        print("\n[2/8] Batiments et salles...")
        salles = []
        for i, bat_nom in enumerate(BATIMENTS):
            bat = Batiment(nom=bat_nom)
            db.session.add(bat)
            db.session.flush()
            etage = Etage(numero=1, id_batiment=bat.id)
            db.session.add(etage)
            db.session.flush()
            for salle_nom in SALLES_PAR_BATIMENT[i]:
                s = Salle(nom=salle_nom, id_etage=etage.id)
                db.session.add(s)
                db.session.flush()
                salles.append(s)
        print(f"  {len(salles)} salles creees")

        print("\n[3/8] Matieres...")
        matieres_map = {}
        for nom in MATIERES:
            m = Matiere(nom=nom)
            db.session.add(m)
            db.session.flush()
            matieres_map[nom] = m
        print(f"  {len(matieres_map)} matieres creees")

        print("\n[4/8] Classes...")
        classes = []
        for c in CLASSES:
            classe = Classe(**c)
            db.session.add(classe)
            db.session.flush()
            classes.append(classe)
        print(f"  {len(classes)} classes creees")

        print("\n[5/8] Profs...")
        profs = []
        for i, pd in enumerate(PROFS_DATA):
            u = User(
                type='employé',
                nom=pd['nom'], prenom=pd['prenom'],
                username=make_username(pd['prenom'], pd['nom']),
                mail_interne=make_mail(pd['prenom'], pd['nom']),
                password=hash_pwd('prof1234'),
                is_active=True,
            )
            db.session.add(u)
            db.session.flush()
            prof = Prof(id_user=u.id)
            prof.matieres = [matieres_map[m] for m in pd['matieres']]
            db.session.add(prof)
            db.session.flush()
            profs.append(prof)
            print(f"  {u.mail_interne}  /  prof1234  ({', '.join(pd['matieres'])})")

        print("\n[6/8] Eleves et parents...")
        eleves = []
        nb_par_classe = len(ELEVES_DATA) // len(classes)
        for idx, ed in enumerate(ELEVES_DATA):
            classe = classes[idx // nb_par_classe] if idx // nb_par_classe < len(classes) else classes[-1]

            u_eleve = User(
                type='élève',
                nom=ed['nom'], prenom=ed['prenom'],
                username=make_username(ed['prenom'], ed['nom']),
                mail_interne=make_mail(ed['prenom'], ed['nom']),
                password=hash_pwd('eleve1234'),
                is_active=True,
            )
            db.session.add(u_eleve)
            db.session.flush()

            eleve = Eleve(id_user=u_eleve.id, id_classe=classe.id,
                          groupe='A', date_naissance=datetime(2008, 1 + idx % 12, 1 + idx % 28).date())
            db.session.add(eleve)
            db.session.flush()

            # Parent
            u_parent = User(
                type='parent',
                nom=ed['nom'], prenom=f"Parent-{ed['prenom']}",
                username=make_username(ed['prenom'], ed['nom'], suffix='-parent'),
                mail_interne=make_mail(ed['prenom'], ed['nom'], suffix='.parent'),
                password=hash_pwd('parent1234'),
                is_active=True,
            )
            db.session.add(u_parent)
            db.session.flush()
            parent = Parent(id_user=u_parent.id, id_eleve=eleve.id)
            db.session.add(parent)

            eleves.append((eleve, classe))
            print(f"  {u_eleve.mail_interne}  /  eleve1234  -> {classe.niveau}{classe.suffixe}")

        print("\n[7/8] Cours (planning)...")
        nb_cours = 0
        jours_base = [
            datetime(2026, 1, 12, 8, 0),   # lundi
            datetime(2026, 1, 13, 10, 0),  # mardi
            datetime(2026, 1, 14, 14, 0),  # mercredi
            datetime(2026, 1, 15, 8, 0),   # jeudi
            datetime(2026, 1, 16, 10, 0),  # vendredi
        ]
        for prof in profs:
            for matiere in prof.matieres:
                for classe in random.sample(classes, k=min(2, len(classes))):
                    debut = random.choice(jours_base)
                    fin = debut + timedelta(hours=2)
                    salle = random.choice(salles)
                    cours = Cours(
                        id_matiere=matiere.id,
                        id_prof=prof.id,
                        id_classe=classe.id,
                        debut=debut,
                        fin=fin,
                        etat='planifié',
                        id_salle=salle.id,
                    )
                    db.session.add(cours)
                    nb_cours += 1
        db.session.flush()
        print(f"  {nb_cours} cours crees")

        print("\n[8/8] Evaluations (notes)...")
        nb_evals = 0
        # Dates d'eval sur l'annee scolaire
        dates_eval = [
            datetime(2025, 10, 5),
            datetime(2025, 10, 20),
            datetime(2025, 11, 8),
            datetime(2025, 11, 25),
            datetime(2025, 12, 10),
            datetime(2026, 1, 15),
            datetime(2026, 2, 3),
            datetime(2026, 3, 10),
            datetime(2026, 4, 2),
        ]
        # Pour chaque classe, quelques evals par matiere
        for classe in classes:
            eleves_classe = [e for e, c in eleves if c.id == classe.id]
            if not eleves_classe:
                continue
            # Trouver les profs qui enseignent dans cette classe
            cours_classe = db.session.query(Cours).filter_by(id_classe=classe.id).all()
            combos = {(c.id_matiere, c.id_prof) for c in cours_classe}

            for (id_matiere, id_prof) in combos:
                # 2 a 4 evaluations par (classe, matiere)
                for date in random.sample(dates_eval, k=random.randint(2, 4)):
                    note_max = random.choice([10, 20])
                    coef = random.choice([1, 1, 2])
                    for eleve in eleves_classe:
                        note = round(random.uniform(note_max * 0.3, note_max), 2)
                        ev = Evaluation(
                            id_eleve=eleve.id,
                            id_matiere=id_matiere,
                            note=note,
                            note_max=note_max,
                            coefficient=coef,
                            date=date,
                        )
                        db.session.add(ev)
                        nb_evals += 1

        db.session.commit()
        print(f"  {nb_evals} evaluations creees")

        print("\n=== Seed termine ===")
        print("\nComptes de test :")
        print("  admin@guardiaschool.fr          /  admin       (administrateur)")
        print("  marc.dupont@guardiaschool.fr    /  prof1234    (prof Maths/Physique)")
        print("  sophie.leroy@guardiaschool.fr   /  prof1234    (prof Francais/Philo)")
        print("  lucas.dubois@guardiaschool.fr   /  eleve1234   (eleve classe 10A)")
        print("  emma.petit@guardiaschool.fr     /  eleve1234   (eleve classe 10A)")
        print("  lucas.dubois.parent@...         /  parent1234  (parent de Lucas)")
        print("\nUtiliser --reset pour vider la DB avant de re-seeder.")


if __name__ == '__main__':
    seed()
