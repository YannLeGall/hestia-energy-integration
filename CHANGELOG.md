## À venir

### Améliorations

- « Pour économiser » dit chaque conseil en trois temps : ce qui se fait aujourd'hui, ce qui serait mieux, et ce que ça rapporte. Le chauffe-eau et chaque machine y ont leur ligne, rangée par euros avec la veille et le chauffage.
- Pour le chauffe-eau et les machines, une frise de 24 heures montre quand ils tournent aujourd'hui, et quand ils tourneraient mieux.
- Le chauffe-eau : Hestia voit s'il est programmé à heure fixe et à quelle heure. Avec des panneaux, elle dit les mois où le soleil ne l'atteint pas et conseille la nuit pour ces mois-là seulement.
- Les machines : l'heure où elles démarrent le plus souvent, combien de cycles sur 10 tombent au prix fort, et le gain par lavage ou par séchage. Un départ différé déjà utilisé est salué.
- La veille : le gain est dit pour 50 W coupés, pas pour toute la veille.
- « Votre contrat, bien utilisé » garde la jauge des heures creuses et le verdict de l'option.
- « En ce moment » : les flux redessinés d'après le modèle de Frank. Un léger halo de couleur entoure chaque cercle, plus vif quand la puissance monte : jaune orangé pour la production, et pour la maison et le réseau la couleur de l'heure (rouge en heures pleines, bleu en heures creuses). Sur chaque trait, des bulles grossissent au milieu, et elles vont plus vite quand la puissance monte. La tuile garde la hauteur des deux autres colonnes : l'eau du jour tient en une petite ligne sous la maison.

### Corrections

- Le soleil pris par un appareil : quand le chauffe-eau mange tout le surplus des panneaux, la maison ne revend plus rien. Hestia comptait alors ces heures en heures pleines. Elle compte maintenant le soleil qu'il y aurait eu sans l'appareil.

## 1.0.0b2 — Votre contrat, bien utilisé

### Nouveautés

- « Votre contrat, bien utilisé », dans la carte complète : sur les 12 derniers mois, la part de vos achats en heures creuses face à la part à partir de laquelle elles rapportent, et si votre option est la bonne (ce qu'aurait coûté la Base). Jamais sur un seul mois : en hiver, la part des heures creuses baisse.
- Pour le chauffe-eau et les machines (lave-linge, lave-vaisselle, sèche-linge) : ce qu'ils prennent au soleil, la nuit et en heures pleines, et ce que rapporterait de décaler les heures pleines, en euros par an. Avec des panneaux, le conseil dit « au soleil d'abord, sinon la nuit ».
- La puissance souscrite : chaque jour, la plus forte pointe achetée sur 12 mois, face à la puissance juste en dessous. Hestia dit de la garder, ou ce que la puissance plus basse ferait gagner sur l'abonnement.
- Dans la carte Contrat : « Quand tournent vos machines », et les jours de chaque mois où le soleil en trop suffit pour une machine.
- Le bandeau « Le chauffe-eau chauffe en partie au réseau » dit ce qu'il y a à gagner par an.

### Corrections

- « Un compteur compte double » ne parle plus d'un jour ancien : un saut de compteur passé dans l'historique ne se corrige pas. Le message n'apparaît que si les appareils dépassent la maison au moins 3 jours sur les 30 derniers.
- Quand il apparaît, il dit le dernier jour en chiffres et le compteur à regarder (deux appareils qui comptent pareil, ou les plus gros ce jour-là), et il ouvre la page Énergie de Home Assistant, où cela se corrige. Avant, il renvoyait vers la page où on était déjà.
- La nuit, les panneaux à 0 W qui se taisent ne sont plus pris pour un capteur en panne : « Donnée douteuse » ne s'allume plus chaque nuit.
- La carte ne dit plus « Un capteur ne répond plus » pour un point déjà réglé (le poêle déclaré en granulés) ou qu'on ne peut pas régler. Elle renvoie vers « À régler » seulement quand il y a vraiment quelque chose à faire.
- Quand la revente dépasse la production (une partie de la production n'a pas été mesurée), la part du soleil n'est plus affichée à 0 % : la carte dit que la production manque.

## 1.0.0b1 — Le conseiller énergie de la maison

### Nouveautés

- Première préversion d’Hestia Énergie, la troisième brique d’Hestia-FB, avec Hestia Météo et Hestia Confort.
- Il suffit d’une source de consommation dans la page Énergie de Home Assistant : HA Linky, MyElectricalData, un module sur le Linky ou tout autre compteur. Sans elle, l’assistant montre les trois chemins les plus courts.
- Les euros de chaque jour, de chaque mois et des 12 derniers mois, même avec un Linky seul. Quand Enedis est lu, il fait foi.
- Les tarifs réglementés (Tarif Bleu d’EDF : Base, heures pleines / heures creuses, Tempo) sont dans l’intégration, depuis 2012 : chaque jour passé est compté au prix de son époque.
- Le contrat est trouvé tout seul : option, heures creuses lues sur le compteur ou apprises sur la courbe, puissance souscrite. Tout reste modifiable, avec « Rétablir ».
- Des conseils pour économiser, avec les euros en jeu : ce qui tourne la nuit, un degré de chauffage en moins (avec Hestia Météo), l’option Base quand les heures creuses ne rapportent pas, la journée qui sort de l’ordinaire, le mois plus cher que l’an dernier.
- Avec Hestia Météo, le froid de chaque jour pour le chauffage. Avec plusieurs lieux, celui de la maison se choisit dans Extensions › Hestia Météo ; si le froid manque, Énergie dit pourquoi dans « À régler ».
- Avec un compteur en direct : ce que consomme la maison, le prix de l’heure, le prochain passage en heures creuses, la pointe proche du disjoncteur.
- La fuite d’eau et l’appareil oublié allumé sont signalés.
- Le soleil : la part couverte par les panneaux, la revente, et un panneau qui produit moins que d’habitude.
- Le chauffage de la saison : radiateurs, et poêle à granulés avec Suivi Stock Pellet.
- La carte Hestia Énergie : complète, tuile, conseils, et sept cartes de détail (soleil, chauffage, veille, eau, appareils, pointe, contrat). Chacune répond en une phrase, sur une seule période.
- La carte complète s’ouvre sur l’horloge de la journée : un trait par heure, ce que la maison a acheté (heures pleines et creuses) et ce que le soleil a donné, une aiguille sur l’heure, et à côté le prix du moment, l’heure la plus chargée et le soleil du jour. Avec un Linky lu le lendemain, elle montre la veille.
- L’onglet Énergie du panneau Hestia-FB : vue d’ensemble, sources, appareils, réglages, extensions, bilan, à propos.
- Les bilans d’hier, de la semaine et du mois, et les alertes, en notification si vous le voulez (aucune par défaut).
- Des entités pour vos automatisations : coût du jour et du mois, prix du moment, heures creuses, veille de nuit, soleil en trop, pointe proche, conseil et sa couleur.
