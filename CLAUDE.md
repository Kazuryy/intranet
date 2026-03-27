# Guardia Intranet — Contexte projet pour Claude Code

## Vue d'ensemble

Projet académique DevSecOps (GCS2-UE7-2, Guardia Cybersecurity School, 25 mars → 10 avril 2026).
Application web de gestion académique sécurisée : notes, classes, emplois du temps.
Groupe de 4 étudiants, évaluation en deux phases : développement (semaine 1) + pentest croisé (semaine 2).

---

## Stack technique

| Composant | Technologie |
|---|---|
| Back-end | Python 3.11 + Flask |
| Templating | Jinja2 |
| CSS | Tailwind CSS |
| Base de données | MySQL 8 |
| ORM | SQLAlchemy + Flask-SQLAlchemy |
| Auth | Flask-Login + bcrypt |
| Formulaires | Flask-WTF (CSRF automatique) |
| Conteneurisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## Architecture du projet

```
guardia-intranet/
├── app/
│   ├── __init__.py              # Application factory (create_app)
│   ├── models.py                # Modèles SQLAlchemy (User, Note, Course, Class, Schedule, Log)
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py            # /login, /logout, /register
│   ├── notes/
│   │   ├── __init__.py
│   │   └── routes.py            # CRUD notes, calcul moyennes
│   ├── admin/
│   │   ├── __init__.py
│   │   └── routes.py            # Gestion users, classes, matières
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── routes.py            # Stats, vue d'ensemble par rôle
│   ├── templates/
│   │   ├── base.html            # Layout principal
│   │   ├── partials/            # Composants réutilisables
│   │   ├── auth/
│   │   ├── notes/
│   │   ├── admin/
│   │   └── dashboard/
│   └── static/
│       ├── css/
│       └── js/
├── tests/
│   ├── conftest.py              # Fixtures pytest (app, db, users de test)
│   ├── test_auth.py
│   ├── test_notes.py
│   ├── test_rbac.py             # Tests d'accès par rôle — critique
│   └── test_admin.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml            # Pipeline complète
├── .zap/
│   └── rules.tsv                # Règles OWASP ZAP
├── .flake8
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── sonar-project.properties
└── CLAUDE.md                    # Ce fichier
```

---

## Modèles de données

### User
```python
id, email, password_hash, first_name, last_name,
role (enum: 'admin' | 'teacher' | 'student'),
class_id (FK → Class, nullable),
is_active, created_at
```

### Class
```python
id, name, year, created_at
```

### Course (matière)
```python
id, name, coefficient, teacher_id (FK → User), class_id (FK → Class)
```

### Note
```python
id, student_id (FK → User), course_id (FK → Course),
value (float, 0-20), comment, created_at, updated_at,
created_by (FK → User)
```

### Schedule (emploi du temps)
```python
id, class_id (FK → Class), course_id (FK → Course),
day_of_week (0-4), start_time, end_time, room
```

### Log (audit)
```python
id, user_id (FK → User), action, target_type, target_id,
ip_address, user_agent, created_at
```

---

## RBAC — Règles d'accès strictes

Trois rôles. **Toute violation renvoie un 403 et est loggée en base.**

### Admin
- Créer / modifier / désactiver des comptes utilisateurs
- Créer / gérer les classes et les matières
- Créer les emplois du temps par classe
- Voir tous les logs d'audit
- Accès total en lecture

### Teacher (Professeur)
- Voir uniquement ses classes attribuées
- Créer des évaluations pour ses matières
- Saisir / modifier les notes de ses étudiants uniquement
- Voir les emplois du temps de ses classes

### Student (Étudiant)
- Voir uniquement ses propres notes (jamais celles des autres)
- Voir son emploi du temps
- Aucun accès en écriture

**Implémentation :** décorateur custom `@role_required('admin')` qui vérifie le rôle côté serveur. Ne jamais se fier au front pour les permissions.

---

## Exigences de sécurité (toutes obligatoires)

1. **Hachage mots de passe** — bcrypt uniquement, jamais de mot de passe en clair
2. **CSRF** — Flask-WTF sur tous les formulaires, token dans chaque form
3. **Validation des entrées** — valider et sanitiser côté serveur, pas uniquement côté client
4. **Requêtes paramétrées** — SQLAlchemy ORM uniquement, zéro concaténation SQL
5. **Headers HTTP** — Flask-Talisman : CSP, X-Frame-Options, HSTS, X-Content-Type-Options
6. **Sessions** — durée de vie limitée, invalidation à la déconnexion, cookie HttpOnly + SameSite=Lax
7. **Rate limiting** — Flask-Limiter sur /login et /register (ex: 5 tentatives / minute)
8. **Audit log** — toutes les actions sensibles loggées (login, logout, création/modification note, accès 403)
9. **Route /health** — endpoint de healthcheck sans auth, nécessaire pour OWASP ZAP dans la CI

---

## Pipeline CI/CD (GitHub Actions)

Fichier : `.github/workflows/ci-cd.yml`
Déclenchement : push et PR sur `main` et `develop`

| Job | Outil | Description |
|---|---|---|
| 01 lint | Flake8 + isort | Qualité et style du code Python |
| 02 sast | SonarCloud | Analyse statique de sécurité |
| 03 pip-audit | pip-audit | Scan des dépendances vulnérables |
| 04 tests | pytest + coverage | Tests unitaires et couverture |
| 05 docker-build | Docker + hadolint | Build image + lint Dockerfile |
| 06 zap-scan | OWASP ZAP | Scan DAST sur app lancée via docker compose |
| 07 deploy | SSH + docker compose | CD uniquement sur push main |

Le job ZAP démarre l'app via docker compose, attend le /health, scanne, puis stoppe.
Le rapport ZAP HTML est uploadé en artifact à chaque run.

---

## Conventions de code

- **Langue** : code en anglais (variables, fonctions, commentaires), UI en français
- **Style** : PEP8, max 88 caractères par ligne (config Flake8)
- **Commits** : `feat:` / `fix:` / `chore:` / `ci:` / `docs:` + description courte en minuscules
- **Branches** : `feature/nom-court` depuis `develop`, PRs vers `develop`, `develop` → `main` pour release
- **Tests** : au moins un test par route, toujours tester l'accès avec le mauvais rôle (403 attendu)
- **Pas de secret dans le code** : tout passe par variables d'environnement via `.env` (jamais commité)

---

## Variables d'environnement

Voir `.env.example` à la racine. En dev, copier en `.env`.

```
FLASK_ENV=development
SECRET_KEY=...
DATABASE_URL=mysql+pymysql://user:password@localhost/guardia_db
MYSQL_ROOT_PASSWORD=...
MYSQL_DATABASE=guardia_db
MYSQL_USER=guardia
MYSQL_PASSWORD=...
```

---

## Contexte évaluation

- **Pipeline CI/CD fonctionnelle** = 10% de la note projet — critique
- **RBAC + sécurité applicative** = 10%
- **Semaine 2** : un autre groupe va activement chercher des failles dans notre app (RBAC bypass, SQLi, XSS, IDOR, manipulation de sessions). Le code doit être blindé.
- Le rapport ZAP et les artifacts CI sont à conserver pour la soutenance.