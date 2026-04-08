# API — Auth & Profils

> Dernière mise à jour : 3 avril 2026
> Blueprint : `auth_bp` — préfixe `/auth`

---

## Routes

### POST /auth/login

Authentifie un utilisateur et ouvre une session.

**Rate limit :** 5 requêtes / minute par IP.

**Corps (JSON) :**
```json
{
  "email": "string (mail interne, ex: prenom.nom@guardiaschool.fr)",
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

**Rate limit :** 5 requêtes / minute par IP.

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

### POST /auth/setup-password

Permet à un nouvel utilisateur de définir son mot de passe via le lien de setup envoyé par l'admin.

**Auth requise :** non

**Rate limit :** 5 requêtes / minute par IP.

**Corps (JSON) :**
```json
{
  "token": "string (token reçu par l'admin à la création du compte)",
  "password": "string (min. 8 caractères)"
}
```

**Validations :**
- `token` vérifié en base (`setup_token`) et non expiré (`setup_token_expires`)
- `password` : minimum 8 caractères
- Après succès : `setup_token` et `setup_token_expires` remis à `null`

**Réponses :**
| Code | Cas |
|---|---|
| 200 | Mot de passe configuré |
| 400 | Token ou password manquant, password trop court, lien invalide ou expiré |

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
| `test_login_success` | POST /auth/login | Credentials valides → 200 |
| `test_login_wrong_password` | POST /auth/login | Mauvais mot de passe → 401 |
| `test_login_unknown_user` | POST /auth/login | Username inexistant → 401 |
| `test_logout` | POST /auth/logout | Session active → 200 |
| `test_logout_unauthenticated` | POST /auth/logout | Non connecté → 401 |
| `test_login_inactive_user` | POST /auth/login | Compte désactivé → 403 |
| `test_login_no_json` | POST /auth/login | Pas de JSON → 400 |
| `test_login_empty_fields` | POST /auth/login | Champs vides → 400 |
| `test_change_password_success` | PATCH /auth/profile/password | Changement valide → 200 |
| `test_change_password_wrong_current` | PATCH /auth/profile/password | Mauvais mot de passe actuel → 400 |
| `test_change_password_too_short` | PATCH /auth/profile/password | Nouveau mot de passe < 8 chars → 400 |
| `test_change_password_unauthenticated` | PATCH /auth/profile/password | Non connecté → 401 |
| `test_change_phone_success` | PATCH /auth/profile/phone | Numéro valide → 200 |
| `test_change_phone_invalid` | PATCH /auth/profile/phone | Format invalide → 400 |
| `test_change_phone_unauthenticated` | PATCH /auth/profile/phone | Non connecté → 401 |
| `test_contact_direction_success` | POST /auth/profile/contact-direction | Champ valide + direction existe → 201 |
| `test_contact_direction_invalid_champ` | POST /auth/profile/contact-direction | Champ non autorisé → 400 |
| `test_contact_direction_no_direction` | POST /auth/profile/contact-direction | Pas de direction en base → 404 |
| `test_contact_direction_unauthenticated` | POST /auth/profile/contact-direction | Non connecté → 401 |
