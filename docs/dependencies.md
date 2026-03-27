# Dépendances du projet

> Dernière mise à jour : 25 mars 2026

## Stack principale

| Package | Version | Rôle |
|---|---|---|
| Flask | 3.1.3 | Framework web principal |
| Flask-SQLAlchemy | 3.1.1 | ORM — interface Python ↔ MySQL |
| PyMySQL | 1.1.1 | Driver MySQL pour SQLAlchemy |
| Flask-Login | 0.6.3 | Gestion des sessions utilisateur |
| Flask-Bcrypt | 1.0.1 | Hachage des mots de passe |
| Flask-WTF | 1.2.2 | Formulaires + protection CSRF |
| Flask-Limiter | 3.9.3 | Rate limiting sur les routes sensibles |
| Flask-Talisman | 1.1.0 | Headers HTTP de sécurité (CSP, HSTS, X-Frame-Options) |

## Tests & qualité

| Package | Version | Rôle |
|---|---|---|
| pytest | 8.3.5 | Framework de tests |
| pytest-cov | 6.0.0 | Rapport de couverture de code |
| flake8 | 7.2.0 | Linting Python (PEP8) |

## Environnement

- **Python** : 3.13 (CI) / 3.14 (local)
- **MySQL** : 8.x
- **Docker** : voir `docker-compose.yml`

## Pourquoi ces choix ?

### Flask-Bcrypt plutôt que bcrypt seul
Flask-Bcrypt est un wrapper Flask autour de bcrypt. Il expose directement `bcrypt.generate_password_hash()` et `bcrypt.check_password_hash()` sans configuration supplémentaire.

### PyMySQL plutôt que mysql-connector-python
PyMySQL est plus léger, entièrement en Python (pas de dépendances C), et fonctionne nativement avec SQLAlchemy via l'URL `mysql+pymysql://`.

### Flask-Talisman
Ajoute en une ligne les headers de sécurité HTTP requis par le CDC : `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`.

### Flask-Limiter
Permet de limiter le nombre de requêtes par IP sur les endpoints sensibles (`/login`, `/register`) pour se protéger contre le brute force.

## Mise à jour des dépendances

Pour vérifier si des mises à jour sont disponibles :
```bash
pip list --outdated
```

Pour auditer les vulnérabilités connues (job CI pip-audit) :
```bash
pip install pip-audit
pip-audit -r requirements.txt
```