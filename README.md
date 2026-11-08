# Hestia Énergie — intégration

**Le conseiller énergie de la maison.** Hestia Énergie lit la page Énergie de Home Assistant et ses statistiques. Elle dit où part l’argent de l’électricité et de l’eau, quand lancer les machines, et signale ce qui est anormal.

> Préversion en construction (1.0.0b1). Rien n’est encore publié.

Une brique de l’ensemble **Hestia-FB**, avec Hestia Météo et Hestia Confort.

## Ce qu’elle fera dans la première préversion

- Des bilans en euros, tirés des statistiques de la page Énergie (même sans compteur en direct).
- La veille de nuit, les journées anormales, les compteurs qui sautent et les capteurs figés.
- Le contrat : Base, heures pleines / heures creuses, Tempo lu ; le prochain passage en heures creuses.
- Avec un compteur en direct : le prix de l’heure, la pointe proche du disjoncteur, le bon moment.
- Une carte (tuile, carte complète, cartes de détail) et l’onglet « Énergie » du panneau Hestia-FB.

## Développement

```sh
python -m unittest discover -s tests -p 'test_*.py'
cd frontend && npm ci && npm run validate
cd card && npm ci && npm run validate
```

Le moteur (`custom_components/hestia_energy/engine/`) n’importe rien de Home Assistant : il se teste seul, par rejeu de vraies statistiques.
