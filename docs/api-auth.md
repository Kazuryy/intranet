# API — Auth & Profils

> Dernière mise à jour : 30 mars 2026
> Blueprint : `auth_bp` — préfixe `/auth`

---

## Routes

### POST /auth/login

Authentifie un utilisateur et ouvre une session.

**Rate limit :** 5 requêtes / minute par IP.

**Corps (JSON) :**
```json
{
  "username": "string",
  "password": "string"
}
```

**Réponses :**
| Code | Cas |
|---|---|
| 200 | Authentification réussie — retourne `{ "message": "Connecté", "role": "<type>" }` |
| 401 | Identifiants invalides |
| 429 | Trop de tentatives |

---

### POST /auth/logout

Invalide la session courante.

**Auth requise :** oui

**Réponses :**
| Code | Cas |
|---|---|
| 200 | Session fermée |
| 401 | Non authentifié |

---

### PATCH /auth/profile/password

Modifie le mot de passe de l'utilisateur connecté.

**Auth requise :** oui

**Corps (JSON) :**
```json
{
  "current_password": "string",
  "new_password": "string (min. 8 caractères)"
}
```

**Validations :**
- `current_password` vérifié contre le hash bcrypt en base
- `new_password` : minimum 8 caractères

**Réponses :**
| Code | Cas |
|---|---|
| 200 | Mot de passe mis à jour |
| 400 | Mot de passe actuel incorrect ou nouveau trop court |
| 401 | Non authentifié |

---

### PATCH /auth/profile/phone

Modifie le numéro de téléphone de l'utilisateur connecté (table `Information`).

**Auth requise :** oui

**Corps (JSON) :**
```json
{
  "numero": "string (format français : 0XXXXXXXXX)"
}
```

**Validations :**
- Format validé par regex : `0[1-9]\d{8}` (numéro français 10 chiffres)
- Crée une entrée `Information` si elle n'existe pas encore

**Réponses :**
| Code | Cas |
|---|---|
| 200 | Numéro mis à jour |
| 400 | Format invalide |
| 401 | Non authentifié |

---

### POST /auth/profile/contact-direction

Envoie un mail interne à la direction pour demander la modification d'un champ verrouillé du profil.

**Auth requise :** oui

**Corps (JSON) :**
```json
{
  "champ": "nom | prenom | adresse"
}
```

**Validations :**
- `champ` doit appartenir à `{ nom, prenom, adresse }`
- Un utilisateur `Direction` doit exister en base

**Comportement :**
Crée une entrée `Mail` avec objet et corps pré-remplis (identité de l'expéditeur + champ concerné), destinée au premier utilisateur `Direction` trouvé.

**Réponses :**
| Code | Cas |
|---|---|
| 201 | Mail créé |
| 400 | Champ non autorisé |
| 404 | Aucun responsable direction en base |
| 401 | Non authentifié |

---

## Sécurité transversale

| Mesure | Détail |
|---|---|
| Rate limiting | 5 req/min sur `/auth/login` via Flask-Limiter |
| Headers HTTP | CSP, HSTS, X-Frame-Options DENY, X-Content-Type-Options via Flask-Talisman |
| Sessions | `HttpOnly`, `SameSite=Lax`, durée de vie 3600 s |
| Mots de passe | Hachage bcrypt uniquement, jamais stockés en clair |
| Accès non authentifié | `login_manager.unauthorized_handler` retourne 401 JSON (pas de redirect) |

---

## Tests

Fichier : `tests/test_auth.py`

| Test | Route | Cas couvert |
|---|---|---|
| `test_login_success` | POST /login | Credentials valides → 200 |
| `test_login_wrong_password` | POST /login | Mauvais mot de passe → 401 |
| `test_login_unknown_user` | POST /login | Username inexistant → 401 |
| `test_logout` | POST /logout | Session active → 200 |
| `test_change_password_success` | PATCH /profile/password | Changement valide → 200 |
| `test_change_password_wrong_current` | PATCH /profile/password | Mauvais mot de passe actuel → 400 |
| `test_change_password_too_short` | PATCH /profile/password | Nouveau mot de passe < 8 chars → 400 |
| `test_change_password_unauthenticated` | PATCH /profile/password | Non connecté → 401 |
| `test_change_phone_success` | PATCH /profile/phone | Numéro valide → 200 |
| `test_change_phone_invalid` | PATCH /profile/phone | Format invalide → 400 |
| `test_change_phone_unauthenticated` | PATCH /profile/phone | Non connecté → 401 |
| `test_contact_direction_success` | POST /profile/contact-direction | Champ valide + direction existe → 201 |
| `test_contact_direction_invalid_champ` | POST /profile/contact-direction | Champ non autorisé → 400 |
| `test_contact_direction_no_direction` | POST /profile/contact-direction | Pas de direction en base → 404 |
| `test_contact_direction_unauthenticated` | POST /profile/contact-direction | Non connecté → 401 |
