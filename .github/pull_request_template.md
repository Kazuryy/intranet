## Quoi ?

<!-- Ce que cette PR change -->

## Pourquoi ?

<!-- La raison du changement -->

## Comment tester ?

<!-- Commandes à lancer pour vérifier que ça marche -->

```bash
# ex:
docker compose up -d
pytest tests/
```

## Checklist

- [ ] `flake8` passe sans erreur
- [ ] `pytest` passe sans erreur
- [ ] Pas de secret dans le code
- [ ] Les nouvelles routes ont `@login_required` + `@role_required`
