# Pour les développeurs

```sh
python -m unittest discover -s tests -p 'test_*.py'
cd frontend && npm ci && npm run validate
cd card && npm ci && npm run validate
```

Le moteur (`custom_components/hestia_energy/engine/`) n’importe rien de Home Assistant : il se teste seul, par rejeu de vraies statistiques. La table des tarifs se reconstruit avec `scripts/tarifs_cre.py` à chaque changement de prix (1er février, 1er août).

[← Retour au README](../README.md)
