# Scripts

Le rejeu des vraies statistiques arrive à l'étape 2. Les données restent hors du dépôt : `../hestia-energie/donnees-test/`.

## `tarifs_cre.py` — la table des tarifs réglementés

Reconstruit `engine/data/tarifs-reglementes.json` à partir des données ouvertes de la CRE sur data.gouv.fr (« Historique
des tarifs réglementés de vente d'électricité pour les consommateurs résidentiels » : Base, Heures pleines / creuses,
Tempo, TTC, depuis 2012). À lancer à chaque changement de prix (1er février, 1er août), relire le diff, puis livrer avec
la version suivante :

    python scripts/tarifs_cre.py
