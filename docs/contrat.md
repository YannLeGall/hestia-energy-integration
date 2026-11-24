# Le contrat et les prix

- **Les tarifs réglementés (Tarif Bleu d’EDF) sont dans l’intégration** : Base, heures pleines / heures creuses et Tempo, abonnements compris, tels que la Commission de régulation de l’énergie les publie depuis 2012. Chaque jour passé est compté au prix de son époque. Cette version a les tarifs du 1er août 2026 ; ils sont mis à jour avec chaque nouvelle version.
- **Une autre offre ?** Dans **Réglages → Prix du kWh**, choisissez **Une autre offre** et recopiez les prix de votre facture.
- **Les heures creuses** sont lues sur le compteur quand c’est possible, sinon apprises sur la courbe de la maison. Vous pouvez ajouter plusieurs plages.
- **Une maison qui revend** : le prix de revente se règle aussi.

## Un compteur par période

Quand la page Énergie a une source réseau par période (un compteur heures pleines et un heures creuses, ou les registres du Linky : heures pleines et creuses d’hiver et d’été, pointe…) :

- **Les jours passés sont comptés registre par registre.** Chaque registre ne compte que sa période, et son énergie est comptée au prix que la page Énergie lui donne. La grille des heures creuses ne sert pas à ce calcul : la changer ne change pas le coût des jours passés.
- **La grille sert à l’heure en cours** : dire si l’on est en heures creuses, à quelle heure le prix change, et les conseils qui en dépendent.
- **Le prix du moment** est celui du registre qui compte en ce moment : le Linky n’en fait avancer qu’un à la fois. **La période en cours** vient du libellé du Linky (« H CREUSE HIVER », « H POINTE ») quand il est dans Home Assistant, sinon de ce registre, sinon de la grille.
- **Les prix « heures pleines » et « heures creuses » de la saison** sont ceux des registres qui ont le plus compté ces deux dernières semaines.

Un prix inconnu reste inconnu : Énergie n’invente jamais un euro.

[← Retour au README](../README.md)
