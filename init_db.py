"""
Initialisation de la base de donnees.
- Cree les tables si elles n'existent pas
- Cree le compte admin par defaut (admin@guardiaschool.fr / admin)
  uniquement si aucun administrateur n'existe deja.
"""
from app import bcrypt, create_app
from app.models import db, User

app = create_app()

with app.app_context():
    db.create_all()
    print('[init_db] Tables creees.')

    if not User.query.filter_by(type='administrateur').first():
        admin = User(
            nom='Admin',
            prenom='Systeme',
            username='admin',
            mail_interne='admin@guardiaschool.fr',
            password=bcrypt.generate_password_hash('admin').decode('utf-8'),
            type='administrateur',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print('[init_db] Compte admin cree : admin@guardiaschool.fr / admin')
        print('[init_db] Changez le mot de passe apres la premiere connexion !')
    else:
        print('[init_db] Admin existant, rien a faire.')
