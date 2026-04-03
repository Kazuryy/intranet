# API — Emploi du temps

> Dernière mise à jour : 3 avril 2026
> Blueprint : `edt_bp` — préfixe `/edt`

**Auth requise sur toutes les routes** : oui.

---

## RBAC — Scopes automatiques sur GET

| Rôle | Données visibles |
|---|---|
| `élève` | Cours de sa classe uniquement |
| `parent` | Cours de la classe de son élève |
| `employé` (prof) | Ses cours uniquement |
| `employé` (direction) | Tous les cours, filtres libres |
| `administrateur` | Tous les cours, filtres libres |

Les routes POST / PATCH / DELETE sont réservées à `administrateur` et `employé` direction.

---

## Format d'une date

Toutes les dates sont en **ISO 8601** avec timezone. Exemples acceptés :
```
2026-04-07T08:00:00+02:00
2026-04-07T08:00:00Z
2026-04-07T08:00:00
```

---

## Routes

### GET /edt/cours

Retourne la liste des cours selon le scope du rôle connecté.

**Query params (admin et direction uniquement) :**
| Param | Type | Description |
|---|---|---|
| `debut` | datetime ISO 8601 | Filtre les cours dont `debut >= valeur` |
| `fin` | datetime ISO 8601 | Filtre les cours dont `fin <= valeur` |
| `classe_id` | integer | Filtre par classe |
| `prof_id` | integer | Filtre par professeur |

**Réponse 200 :**
```json
[
  {
    "id": 1,
    "debut": "2026-04-07T08:00:00+00:00",
    "fin": "2026-04-07T10:00:00+00:00",
    "etat": "planifié",
    "matiere": { "id": 3, "nom": "Mathématiques" },
    "classe": { "id": 2, "niveau": 1, "suffixe": "A" },
    "prof": { "id": 5, "nom": "Dupont", "prenom": "Paul" },
    "salle": { "id": 7, "nom": "Salle 101" }
  }
]
```

**Réponses :**
| Code | Cas |
|---|---|
| 200 | Liste (vide si aucun résultat) |
| 400 | Format de date invalide |
| 401 | Non authentifié |

---

### POST /edt/cours

Crée un nouveau cours.

**Rôles autorisés :** `administrateur`, `employé` direction.

**Corps (JSON) :**
```json
{
  "id_matiere": 3,
  "id_prof": 5,
  "id_classe": 2,
  "debut": "2026-04-07T08:00:00Z",
  "fin": "2026-04-07T10:00:00Z",
  "id_salle": 7,
  "etat": "planifié"
}
```

| Champ | Requis | Description |
|---|---|---|
| `id_matiere` | oui | ID d'une `Matiere` existante |
| `id_prof` | oui | ID d'un `Prof` existant |
| `id_classe` | oui | ID d'une `Classe` existante |
| `debut` | oui | ISO 8601 |
| `fin` | oui | ISO 8601, doit être après `debut` |
| `id_salle` | non | ID d'une `Salle` existante |
| `etat` | non | `planifié` (défaut), `en cours`, `terminé`, `annulé` |

**Réponse 201 :** objet cours complet (même format que GET).

**Réponses :**
| Code | Cas |
|---|---|
| 201 | Cours créé |
| 400 | Champs manquants, date invalide, `fin` avant `debut`, état invalide |
| 401 | Non authentifié |
| 403 | Rôle insuffisant |
| 404 | Matière, prof, classe ou salle introuvable |

---

### PATCH /edt/cours/\<cours_id\>

Modifie un cours existant. Seuls les champs fournis sont mis à jour.

**Rôles autorisés :** `administrateur`, `employé` direction.

**Corps (JSON) — tous optionnels, au moins un requis :**
```json
{
  "debut": "2026-04-07T09:00:00Z",
  "fin": "2026-04-07T11:00:00Z",
  "id_matiere": 3,
  "id_prof": 5,
  "id_classe": 2,
  "id_salle": 7,
  "etat": "annulé"
}
```

**Note :** si `debut` ou `fin` est fourni, les deux sont recalculés ensemble — la cohérence `fin > debut` est toujours vérifiée.

**Réponse 200 :** objet cours complet mis à jour.

**Réponses :**
| Code | Cas |
|---|---|
| 200 | Cours mis à jour |
| 400 | Aucun champ valide, date invalide, `fin` avant `debut`, état invalide |
| 401 | Non authentifié |
| 403 | Rôle insuffisant |
| 404 | Cours, matière, prof, classe ou salle introuvable |

---

### DELETE /edt/cours/\<cours_id\>

Supprime définitivement un cours.

**Rôles autorisés :** `administrateur`, `employé` direction.

**Réponses :**
| Code | Cas |
|---|---|
| 200 | `{ "message": "Cours supprimé" }` |
| 401 | Non authentifié |
| 403 | Rôle insuffisant |
| 404 | Cours introuvable |

---

## Valeurs d'état (`etat`)

| Valeur | Description |
|---|---|
| `planifié` | Cours prévu (défaut à la création) |
| `en cours` | Cours actuellement en train de se dérouler |
| `terminé` | Cours passé |
| `annulé` | Cours annulé |
