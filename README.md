# Intranet Guardia

Application web de gestion académique sécurisée — GCS2-UE7-2 DevSecOps.

## Prérequis

- Git
- Python 3.13+
- Docker + Docker Compose

## Installation rapide

### macOS / Linux

```bash
git clone https://github.com/TON_USERNAME/intranet.git
cd intranet
chmod +x setup.sh
./setup.sh
```

### Windows (PowerShell en administrateur)

```powershell
git clone https://github.com/Kazuryy/intranet.git
cd intranet
.\setup.ps1
```

---

## Installation manuelle (si le script ne fonctionne pas)

### 1. Installer Docker

- **macOS** : https://docs.docker.com/desktop/install/mac-install/
- **Windows** : https://docs.docker.com/desktop/install/windows-install/
- **Linux** : https://docs.docker.com/engine/install/

### 2. Installer Python 3.13

- **macOS** : `brew install python@3.13`
- **Windows** : https://www.python.org/downloads/
- **Linux** : `sudo apt install python3.13 python3.13-venv` (Ubuntu/Debian)

### 3. Cloner le repo et configurer l'environnement

```bash
git clone https://github.com/TON_USERNAME/intranet.git
cd intranet

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
# macOS / Linux :
source venv/bin/activate
# Windows :
venv\Scripts\activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Ouvre `.env` et modifie les valeurs si besoin (les valeurs par défaut fonctionnent pour le dev local).

### 5. Lancer l'application

```bash
docker compose up -d
```

L'application est accessible sur http://localhost:5000

---

## Commandes utiles

```bash
# Lancer l'application
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter l'application
docker compose down

# Arrêter et supprimer les volumes (reset BDD)
docker compose down -v

# Lancer les tests
pytest tests/

# Lancer le linting
flake8 app/
```

---

## Workflow Git

```
main        → code stable, déclenche le déploiement
develop     → branche d'intégration
feature/*   → vos branches de travail
```

**Toujours travailler sur une branche feature/fix/ci ... :**

```bash
git checkout develop
git pull origin develop
git checkout -b feature/ma-feature

# ... travail ...

git add .
git commit -m "feat: description courte"
git push origin feature/ma-feature
# → ouvrir une PR vers develop sur GitHub
```

**Convention de commits :**

| Préfixe | Usage |
|---|---|
| `feat:` | Nouvelle fonctionnalité |
| `fix:` | Correction de bug |
| `chore:` | Maintenance, config |
| `ci:` | Pipeline CI/CD |
| `docs:` | Documentation |

---

## Structure du projet

```
intranet/
├── app/
│   ├── __init__.py         # Application factory
│   ├── models.py           # Modèles SQLAlchemy
│   ├── auth/               # Blueprint authentification
│   ├── notes/              # Blueprint notes
│   ├── admin/              # Blueprint administration
│   ├── dashboard/          # Blueprint dashboard
│   ├── templates/          # Templates Jinja2
│   └── static/             # CSS, JS
├── tests/                  # Tests pytest
├── docs/                   # Documentation
├── .github/workflows/      # Pipeline CI/CD
├── .env.example            # Template variables d'environnement
├── docker-compose.yml      # Orchestration Docker
├── Dockerfile              # Image de l'application
└── requirements.txt        # Dépendances Python
```

---

## Compte de test

Une fois l'application lancée, des comptes de test sont disponibles :

| Rôle | Email | Mot de passe |
|---|---|---|
| Admin | admin@guardia.fr | Admin1234! |
| Professeur | prof@guardia.fr | Prof1234! |
| Étudiant | etudiant@guardia.fr | Etudiant1234! |

---

## Problèmes fréquents

**Le port 5000 est déjà utilisé**
```bash
# Trouver le processus qui utilise le port
lsof -i :5000        # macOS / Linux
netstat -ano | findstr :5000   # Windows
```

**Erreur de connexion à la base de données**
```bash
# Vérifier que le conteneur MySQL tourne
docker compose ps
# Attendre quelques secondes que MySQL soit prêt, puis relancer
docker compose restart app
```

**Permission denied sur setup.sh (macOS/Linux)**
```bash
chmod +x setup.sh
```