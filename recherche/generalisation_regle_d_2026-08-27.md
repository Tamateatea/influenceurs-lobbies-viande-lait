# La regle D tient-elle sur une entite jamais vue ? — 2026-08-27

Produit par `outils/generaliser_regle_d.py`. Aucun reseau.

La regle D contient une liste d'alias « generiques » ecrite a la main,
terme par terme, **apres** avoir vu les cas de chaque interprofession.
Les 83 % annonces sont donc mesures sur ce qui a servi a la construire.

Ici, pour chaque entite, on retire de la liste les termes qui la
designent, puis on la teste. C'est la situation d'un commanditaire
decouvert demain.

| Entite | Cas | Vrais | Termes retires | Precision avec | sans | Rappel avec | sans |
|---|---:|---:|---|---:|---:|---:|---:|
| **CNIEL** | 128 | 57 | — | 85 % | 85 % | 100 % | 100 % |
| **INTERBEV** | 31 | 7 | — | 33 % | 33 % | 14 % | 14 % |
| **INAPORC** | 7 | 2 | le porc francais | 0 % | 100 % | 0 % | 100 % |
| **ANVOL** | 2 | 1 | volaille francaise | 0 % | 0 % | 0 % | 0 % |

## Ce que ca dit

2 entites du jeu juge sont designees par un terme
de la liste. Retirer ce terme — c'est-a-dire faire comme si on
n'avait jamais vu l'entite — donne :

- precision **amelioree** pour : INAPORC
- precision **degradee** pour : aucune

Ecart le plus fort : **INAPORC**, 0 % -> 100 % de precision et 0 % -> 100 % de rappel.

**Le resultat va dans le sens inverse de ce qui etait predit**,
et c'est le fait marquant de cette mesure.

La liste des generiques a ete concue pour retirer du bruit. Sur
les entites autres que le CNIEL, elle retire du **signal** : le
terme dit « generique » y est precisement l'alias sous lequel
l'interprofession fait campagne. « Le Porc Francais » n'est pas
une categorie alimentaire qui traine dans une description, c'est
la signature d'INAPORC.

Ce n'est donc pas que la regle D **generalise mal** faute d'avoir
vu l'entite. C'est qu'elle generalise mieux quand on ne lui a
rien appris de l'entite. La liste, ecrite en regardant le CNIEL,
**nuit** ailleurs.

Ce que ca implique, et qui reste a trancher par Vincent : soit on
restreint `est_generique` au CNIEL, soit on l'abandonne au profit
de la regle F, qui exige un @pseudo ecrit tel quel et ne depend
d'aucune liste manuelle.

## Limite de cette mesure

Le jeu juge est petit et tres deseque vers le CNIEL. Les entites a
deux ou trois cas donnent des pourcentages qu'il ne faut pas lire
comme des taux. Ce tableau montre un SENS, pas des valeurs.

