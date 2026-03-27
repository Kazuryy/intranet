## Description

<!-- Décris les changements apportés et pourquoi -->
<!-- Si cette PR corrige une issue, lie-la ici -->

- Fixes #XXXX

## Comment tester ?

<!-- Décris comment vérifier que ça fonctionne -->

```bash
docker compose up -d
pytest tests/
```

## Captures / Logs (si applicable)

## Checklist

- [ ] `flake8` passe sans erreur
- [ ] `pytest` passe sans erreur
- [ ] Pas de secret dans le code
- [ ] Les nouvelles routes ont `@login_required` + `@role_required`
- [ ] Les inputs sont validés côté serveur
- [ ] Les formulaires ont un token CSRF
