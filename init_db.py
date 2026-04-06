"""
Initialisation de la base de donnees.
- Cree les tables si elles n'existent pas
- Cree le compte admin par defaut (admin@guardiaschool.fr)
  uniquement si aucun administrateur n'existe deja.
  Mot de passe lu depuis ADMIN_PASSWORD (env), defaut : 'admin'
"""
import os
from app import bcrypt, create_app
from app.models import db, User

app = create_app()

with app.app_context():
    db.create_all()
    print('[init_db] Tables creees.')

    if not User.query.filter_by(type='administrateur').first():
        password = os.environ.get('ADMIN_PASSWORD', 'admin')
        admin = User(
            nom='Admin',
            prenom='Systeme',
            username='admin',
            mail_interne='admin@guardiaschool.fr',
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            type='administrateur',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f'[init_db] Compte admin cree : admin@guardiaschool.fr')
    else:
        print('[init_db] Admin existant, rien a faire.')
