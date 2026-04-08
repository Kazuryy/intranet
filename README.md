# Intranet Guardia

Application web de gestion academique securisee - GCS2-UE7-2 DevSecOps.

## Prerequis

- Docker + Docker Compose

## Deploiement

```bash
git clone https://github.com/Kazuryy/intranet.git
cd intranet

cp .env.example .env
# Editer .env et definir les valeurs (voir ci-dessous)

docker compose up -d
```

L'application est accessible sur http://localhost (port 80).

## Variables d'environnement (.env)

| Variable | Description |
|---|---|
| `SECRET_KEY` | Cle secrete Flask (chaine aleatoire longue) |
| `MYSQL_DATABASE` | Nom de la base de donnees |
| `MYSQL_USER` | Utilisateur MySQL |
| `MYSQL_PASSWORD` | Mot de passe MySQL |
| `MYSQL_ROOT_PASSWORD` | Mot de passe root MySQL |
| `DATABASE_URL` | URL de connexion SQLAlchemy |
| `ADMIN_PASSWORD` | Mot de passe du compte administrateur |
| `FRONTEND_PORT` | Port expose par nginx (defaut : 80) |

## Commandes utiles

```bash
# Voir les logs
docker compose logs -f

# Arreter
docker compose down

# Reset complet (supprime la BDD)
docker compose down -v

# Mode developpement (hot reload)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Tests et linting
flake8 app/ tests/ && pytest tests/ -v
```

## Base de donnees

Le compte admin est cree automatiquement au premier demarrage (`init_db.py` execute par l'entrypoint).

- **Identifiant** : `admin@guardiaschool.fr`
- **Mot de passe** : valeur de `ADMIN_PASSWORD` dans `.env`

Pour charger des donnees de test (profs, eleves, notes, planning) :

```bash
# Depuis le conteneur app
docker compose exec app python seed.py

# Reset complet + re-seed
docker compose exec app python seed.py --reset
```

Comptes crees par la seed :

| Role | Identifiant | Mot de passe |
|---|---|---|
| Admin | `admin@guardiaschool.fr` | `admin` |
| Prof | `marc.dupont@guardiaschool.fr` | `prof1234` |
| Eleve | `lucas.dubois@guardiaschool.fr` | `eleve1234` |
| Parent | `lucas.dubois.parent@guardiaschool.fr` | `parent1234` |
