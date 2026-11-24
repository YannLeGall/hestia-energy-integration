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

## Le week-end et les jours fériés

Certaines offres (Enercoop « 2 saisons », par exemple) sont en heures creuses toute la journée le samedi, le dimanche et les jours fériés.

- Hestia le voit seule sur les compteurs : si tous les week-ends et jours fériés des quatre dernières semaines sont en heures creuses, elle apprend les heures de la semaine à part.
- Sinon, dans **Réglages → Votre contrat**, choisissez **Le week-end et les jours fériés : Toute la journée**.
- Les onze jours fériés français sont connus d’Hestia, Pâques, l’Ascension et la Pentecôte compris.

Les heures apprises suivent les quatre dernières semaines. Juste après le changement de saison d’une offre, elles mélangent les deux saisons pendant quelques semaines : écrivez alors les heures de la nouvelle saison dans Réglages, ou laissez une automatisation le faire (ci-dessous).

## Régler le contrat par une automatisation

L’action **`hestia_energy.set_settings`** change les mêmes réglages que la page Réglages : `option`, `offer`, `offpeak`, `offpeak_weekend`, `price_hp`, `price_hc`, `price_base`, `subscription`, `kva`, `export_price`. Une valeur vide (`null`) rend à Hestia ce qu’elle a trouvé.

Par exemple, pour passer à l’hiver le 1er novembre :

```yaml
action: hestia_energy.set_settings
data:
  offpeak: "00:00-07:00, 13:00-16:00"
  offpeak_weekend: tout
```

Un prix inconnu reste inconnu : Énergie n’invente jamais un euro.

[← Retour au README](../README.md)
