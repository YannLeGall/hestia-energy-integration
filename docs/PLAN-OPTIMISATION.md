# Hestia Énergie 1.0.0b1 — plan d'optimisation avant publication

Version 0.2 du 10 nov. 2026, sur le commit baca66d. Même démarche que Weather 3.2.0 et Confort 3.0.0 : mesurer, puis
corriger lot par lot, en mesurant avant et après. **Tous les lots accordés par Frank le 10 nov. ; faits et mesurés au
labo (§ 5), non commités.**

## 1. Ce qui a été mesuré

Labo (NAS, Celeron J4125, la vraie maison recopiée, 9 cartes Énergie dans le tableau Labo) et banc local (la vraie année
de la maison, `hestia-labo/energie/banc-local.py`). Scripts : `hestia-labo/energie/mesurer.py` et `lire-profil.py`.

| Mesure | Résultat | Comparaison |
|---|---|---|
| Calcul d'Énergie pendant 3 min avec un bilan horaire | **13,6 s** | Weather 0,45 s, Confort 1,0 s |
| Calcul d'Énergie les 5 min après un redémarrage | **25,7 s** (3 bilans en 5 min) | Weather 0,65 s, Confort 2,0 s |
| Premiers chiffres prêts après un redémarrage | 57 s | |
| Boucle de HA bloquée par Énergie elle-même | 0,10 à 0,19 s, 4 fois au démarrage | règle : jamais plus de 0,1 s |
| Lenteurs des autres pendant le calcul d'Énergie | jusqu'à 1,2 s (Remote HA, automatismes, tableaux) | le calcul d'Énergie occupe le processeur |
| Mémoire gardée (statistiques d'un an) | **215 Mo** (541 000 heures, 71 compteurs) | |
| Vue envoyée à chaque carte | 33 ko, dont 23 ko que les cartes ne lisent pas | |
| Envois aux cartes | 9 cartes × 1 demande par minute chacune | jusqu'à 1 min de retard sur « en ce moment » |
| Onglet : ouverture d'une page | 10 ms, 26 ko | règle : 0,25 s ✔ |
| Onglet : page Bilan (12 mois) | **2,0 s** | règle : 0,25 s ✘ |
| Commande `periods` jour par jour sur un an | **54 s** | |
| Fichiers servis | compressés (.gz) ✔, polices woff2 ✔ | `manrope-variable` (194 ko) jamais utilisée |

Sur un HA Green (processeur plus lent que le NAS), il faut compter environ 1,5 à 2 fois ces temps : **20 à 25 s de
calcul chaque heure**, la page Bilan à 3-4 s. C'est le même genre de charge qui a fait retirer Confort et Weather à un
utilisateur le 5 nov.

### D'où vient le coût

- **Chaque heure, toute l'année est recalculée**, alors que seuls les 3 derniers jours sont relus. 90 % du temps part
  dans la relecture des 71 compteurs heure par heure et dans leurs contrôles (sauts, compteur figé, unité).
- Chaque total (un jour, un mois, l'hiver…) reparcourt l'année entière, compteur par compteur ; la page Bilan en fait 12,
  la commande « jour par jour » 365.
- Au démarrage, trois bilans complets en 5 minutes (au lancement, quand HA a fini de démarrer, puis 5 min après) alors que
  les deux derniers ne servent qu'à repérer une extension arrivée en retard.
- Les statistiques sont gardées en mémoire sous une forme très lourde (un petit dictionnaire par heure et par compteur).

## 2. Ce que la relecture du code a trouvé (bugs et blocages)

1. **L'écouteur de la page Énergie n'est jamais retiré** (HA ne donne pas de moyen de le retirer). Après un rechargement
   d'Énergie, l'ancienne copie reste en vie avec ses 215 Mo et refait un bilan complet à chaque changement de la page
   Énergie. Chaque rechargement en ajoute une.
2. **Les premiers bilans ne sont pas arrêtés au déchargement** : s'ils finissent après, ils réabonnent les capteurs en
   direct, et cet abonnement n'est plus jamais retiré.
3. L'interface donnée aux autres briques garde l'ancienne copie après un déchargement (Confort lirait de vieux prix).
4. **Degrés-jours de Météo** : demandés jour par jour depuis la boucle (0,19 s bloquées au démarrage), et les jours que
   Météo ne connaît pas sont redemandés **chaque heure** (jusqu'à 400 lectures de l'historique par heure sur une
   installation neuve).
5. Le contrat est modifié pendant le calcul, alors que le direct et Confort le lisent au même moment : pendant un
   instant, le prix du jour peut servir pour le passé.
6. Si le premier bilan échoue (donnée imprévue), rien n'est réessayé avant l'heure suivante et la carte reste sur
   « Hestia Énergie lit la page Énergie… » sans rien dire ; un bilan qui échoue plus tard n'est pas signalé clairement.
7. Un réglage enregistré dans l'onglet relance un bilan complet (13 s au labo) ; l'onglet relit après 20 s, trop tôt
   sur un HA Green.

Rien de grave ailleurs : le direct coûte 0,3 ms toutes les 10 s, l'onglet répond en 10 ms, les cartes et l'onglet sont
compressés, aucun autre écouteur ni tâche oubliés.

## 3. Les lots proposés

Chaque lot se mesure avant et après au labo, avec les tests verts (`unittest` et `npm run validate` dans `frontend/` et
`card/`). Les chiffres affichés ne doivent pas bouger d'un centime : chaque lot est vérifié sur la vraie année (bilans,
facture EDF de juillet) et en comparant la vue complète avant/après.

### Lot 1 — Ne plus refaire toute l'année chaque heure (le gros gain)

1. **Relire seulement ce qui a changé** : si les statistiques relues sont les mêmes qu'à l'heure d'avant (HA Linky
   n'envoie qu'une fois par jour), on ne relit pas les compteurs, on remet seulement les chiffres à l'heure.
2. **Calculs moins chers** : chaque compteur garde ses totaux par jour une fois pour toutes ; un total de mois ou d'hiver
   additionne des jours au lieu de reparcourir 8 760 heures ; les contrôles (sauts, figé) ne regardent que les jours
   nouveaux entre deux bilans complets.
3. **Un seul bilan au démarrage** : les deux suivants ne font plus que regarder si une extension est apparue, et ne
   recalculent que dans ce cas.

But : de 13,6 s à moins de 2 s par heure au labo, de 25,7 s à moins de 8 s au démarrage.

### Lot 2 — Moins de mémoire

4. Garder les statistiques sous une forme compacte (des nombres côte à côte au lieu d'un dictionnaire par heure), et ne
   lire que ce qui sert : la somme pour un compteur, la puissance moyenne et maximale pour une prise.

But : de 215 Mo à moins de 50 Mo.

### Lot 3 — Rien de bloqué, rien d'oublié (les bugs du § 2)

5. Retirer l'écouteur de la page Énergie au déchargement (point 1), arrêter les premiers bilans avec l'entrée (point 2),
   détacher l'interface (point 3).
6. Degrés-jours : lus en une fois hors de la boucle ; un jour sans réponse n'est redemandé qu'une fois par jour (point 4).
7. Le contrat et les chiffres sont préparés à part, puis remplacés d'un coup (point 5).
8. Un bilan qui échoue : les derniers chiffres restent affichés, une ligne claire dans le journal, nouvel essai 5 minutes
   plus tard (point 6).

### Lot 4 — Les cartes : un seul abonnement, tout de suite

9. Un abonnement partagé par toutes les cartes Énergie d'un tableau (comme Weather et Confort) : Énergie envoie dès que
   quelque chose change, au lieu de 9 cartes qui redemandent tout chaque minute. « En ce moment » suit le direct à 10 s
   près au lieu d'une minute.
10. Seulement ce que les cartes lisent (33 ko → environ 10 ko), puis seulement les parties qui ont changé.

### Lot 5 — L'onglet sous 0,25 s partout

11. Page Bilan : les mois passés ne changent plus, ils sont gardés au bilan horaire ; la page répond tout de suite
    (2 s → moins de 0,25 s).
12. Commande « jour par jour » : profite du lot 1 (54 s → environ 1 s), limitée à un an.
13. Après un réglage, l'onglet relit quand le nouveau bilan est vraiment prêt, au lieu d'attendre 20 s au hasard (point 7).

### Lot 6 — Le paquet

14. Retirer `manrope-variable.ttf` et `.woff2` (194 ko jamais chargés).
15. À la publication : numéro de version changé à chaque préversion pour que les navigateurs prennent la nouvelle carte.

## 4. Ordre conseillé

Lot 3 d'abord (des bugs, petits et sûrs), puis lots 1 et 2 ensemble (ils touchent les mêmes fichiers du moteur),
puis lots 5, 4 et 6. Les lots 1 et 2 sont les plus longs : chaque euro doit rester identique sur la vraie année.

## 5. Résultats (10 nov. 2026, labo et vraie année)

Tous les chiffres affichés sont restés identiques au centime : vue des cartes, onglet, réglages trouvés, 12 mois,
60 jours et interface, comparés avant/après à deux instants fixes sur la vraie année (`hestia-labo/energie/reference.py`).
Tests : 121 verts (`unittest`), `npm run validate` vert dans `frontend/` et `card/`.

| Mesure (labo) | Avant | Après |
|---|---|---|
| Calcul d'un bilan horaire sans statistique nouvelle (bilan de 19 h, un réglage, HA Linky) | 13,6 s | 1,1 à 1,2 s |
| Calcul d'un bilan horaire avec une heure nouvelle | 13,6 s | environ 5 s (estimé : 2,9 → 1,1 s sur le banc) |
| Calcul les 5 min après un redémarrage | 25,7 s | 8,5 s |
| Premiers chiffres prêts après un redémarrage | 57 s | 43 s |
| Boucle de HA bloquée par Énergie | 0,10 à 0,19 s, 4 fois | plus rien au-dessus de 0,1 s |
| Mémoire gardée (banc, vraie année) | 215 Mo | 42 Mo |
| Page Bilan (12 mois) | 2,0 s | 88 ms |
| `periods` jour par jour sur un an | 54 s | 0,24 s |
| Ce que reçoivent les cartes d'un tableau en 2 min | 9 × 33 ko × 2 ≈ 600 ko | 20 ko (1 abonnement) |
| Retard de « en ce moment » sur les cartes | jusqu'à 1 min | 10 s au plus |

Ce qui a été fait, lot par lot :
- **Lot 3** : écouteur de la page Énergie retiré au déchargement (relais qui ne retient pas la brique),
  premiers bilans arrêtés avec l'entrée, interface détachée, degrés-jours demandés une fois par jour pour un jour
  manquant et sans tenir la boucle, contrat préparé à part puis remplacé d'un coup, bilan raté = derniers chiffres
  gardés, une ligne dans le journal, nouvel essai 5 min plus tard (`coordinator.py`, `reader.py`, `api.py`,
  `__init__.py`). Recherche des extensions en un seul passage (0,13 s de boucle au démarrage).
- **Lots 1 et 2** : statistiques gardées en colonnes (`engine/rows.py`) ; la maison n'est relue que si les
  statistiques, la page ou les extensions ont changé ; totaux et euros trouvés par dichotomie au lieu de reparcourir
  l'année ; totaux par jour, nuits et contrôles de compteur (échelle, retard) calculés une fois ; prix réglementés
  cherchés une fois par jour (`engine/stats.py`, `health.py`, `home.py`, `baseline.py`, `tariff.py`, `anomaly.py`,
  `solar.py`, `cards.py`).
- **Lot 5** : la page Bilan et le jour par jour profitent des lots 1-2 ; jour par jour limité à un an ; après un
  réglage, l'onglet relit dès que le nouveau bilan est fait (toutes les 2 s, une minute au plus).
- **Lot 4** : `hestia_energy/subscribe` (vue des cartes seulement, entière une fois puis les parties changées,
  `reload` quand la brique redémarre) et `card/src/stream.ts` (un abonnement par connexion pour toutes les cartes).
  `hestia_energy/view` reste pour les anciennes cartes. Vérifié sur un banc navigateur avec les vrais messages du
  labo : 10 cartes, 1 abonnement, réabonnement après `reload`, désabonnement quand les cartes partent.
- **Lot 6** : `manrope-variable` n'est **pas** retirée : elle vient de la copie commune du socle (`copier.sh` la
  remettrait) et sert aux cartes Météo et Confort. La carte Énergie, elle, ne charge aucune police Manrope (elle prend
  celle du thème tant que le hub ou une carte Météo ne l'a pas chargée) : à décider avec Frank, c'est de l'apparence.
  Le numéro de version se change à la publication.

Restent hors de ce plan : `npm run test:loading` de la carte ne cherche que les cartes Météo et Confort (copié du
socle) et échoue déjà sur baca66d.
