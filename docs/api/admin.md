# API — Administration

> Dernière mise à jour : 3 avril 2026
> Blueprint : `admin_bp` — préfixe `/admin`

**Auth requise sur toutes les routes** : oui (`administrateur` ou `employé` direction).

---

## RBAC

| Rôle | Périmètre |
|---|---|
| `administrateur` | Tous les types d'utilisateurs |
| `employé` (direction uniquement) | `élève` et `parent` uniquement |
| Autres | 403 |

---

## Routes

### GET /admin/users

Liste les utilisateurs avec filtres optionnels.

**Query params :**
| Param | Type | Description |
|---|---|---|
| `type` | string | Filtre par type (`élève`, `employé`, `parent`, `administrateur`) |
| `search` | string | Recherche sur `nom`, `prenom`, `username` (insensible à la casse) |

**Réponse 200 :**
```json
[
  {
    "id": 1,
    "nom": "Martin",
    "prenom": "Alice",
    "username": "amartin",
    "type": "élève",
    "is_active": true
  }
]
```

**Réponses :**
| Code | Cas |
|---|---|
| 200 | Liste (vide si aucun résultat) |
| 401 | Non authentifié |
| 403 | Rôle insuffisant ou employé hors direction |

---

### POST /admin/users

Crée un nouveau compte utilisateur. Le mot de passe n'est pas défini à la création — un `setup_token` valable 48h est retourné pour que l'utilisateur configure son mot de passe via `POST /auth/setup-password`.

**Corps (JSON) :**
```json
{
  "nom": "string",
  "prenom": "string",
  "type": "élève | employé | parent | administrateur"
}
```

**Comportement :**
- `mail_interne` généré automatiquement : `prenom.nom@guardiaschool.fr` (déduplication si collision)
- `username` généré automatiquement : initiale prénom + nom (déduplication si collision)
- `setup_token` à transmettre à l'utilisateur pour qu'il définisse son mot de passe

**Réponse 201 :**
```json
{
  "id": 42,
  "mail_interne": "alice.martin@guardiaschool.fr",
  "username": "amartin",
  "setup_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

**Réponses :**
| Code | Cas |
|---|---|
| 201 | Compte créé |
| 400 | Champs manquants ou type invalide |
| 401 | Non authentifié |
| 403 | Rôle insuffisant ou type non autorisé pour la direction |
| 500 | Impossible de générer un identifiant unique (rare) |

---

### PATCH /admin/users/\<user_id\>

Modifie un compte existant. Seuls les champs fournis sont mis à jour.

**Corps (JSON) — tous optionnels, au moins un requis :**
```json
{
  "nom": "string",
  "prenom": "string",
  "type": "élève | employé | parent | administrateur",
  "is_active": true
}
```

**Réponse 200 :**
```json
{
  "id": 42,
  "nom": "Martin",
  "prenom": "Alice",
  "type": "élève",
  "is_active": true
}
```

**Réponses :**
| Code | Cas |
|---|---|
| 200 | Compte mis à jour |
| 400 | Aucun champ valide, champ vide, type invalide, `is_active` non booléen |
| 401 | Non authentifié |
| 403 | Rôle insuffisant |
| 404 | Utilisateur introuvable |

---

### DELETE /admin/users/\<user_id\>

Supprime définitivement un compte.

**Contraintes :**
- Impossible de supprimer son propre compte (→ 403)
- Direction : uniquement les comptes `élève` et `parent`

**Réponses :**
| Code | Cas |
|---|---|
| 200 | `{ "message": "Compte supprimé" }` |
| 401 | Non authentifié |
| 403 | Rôle insuffisant ou tentative d'auto-suppression |
| 404 | Utilisateur introuvable |

---

## Flux typique — création d'un compte

```
1. Admin  →  POST /admin/users          →  reçoit setup_token
2. Admin  →  transmet le setup_token à l'utilisateur (email externe, etc.)
3. User   →  POST /auth/setup-password  →  définit son mot de passe
4. User   →  POST /auth/login           →  connecté
```
