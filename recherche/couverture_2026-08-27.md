# Quelle part des collaborations voit-on ? — 2026-08-27

Produit par `outils/estimer_couverture.py`. Aucun reseau.

## 1. Le tirage aleatoire est arithmetiquement hors de portee

METHODOLOGIE 9.2 prescrit un tirage de **createurs**, chacun annote
ensuite exhaustivement « par tous les moyens ». C'est donc par chaine
qu'il faut compter, pas par video.

- Chaines moissonnees : **2 660**
- Dont une preuve forte : **36** (1.35 %)
- Dont une collaboration confirmee : **11** (0.41 %)

| Pour obtenir | Il faudrait annoter | Soit |
|---|---:|---:|
| 10 chaines a preuve forte | 739 chaines | 28 % du registre |
| 10 chaines confirmees | 2 418 chaines | 91 % du registre |
| 30 chaines a preuve forte | 2 217 chaines | 83 % du registre |
| 30 chaines confirmees | 7 255 chaines | 273 % du registre |

Et « annoter exhaustivement » veut dire parcourir tout le
catalogue d'une chaine a la main. Sept cent trente-neuf fois.

**Ce n'est pas une difficulte d'organisation, c'est une
impossibilite arithmetique.** Une tache portee au TODO pendant
quatre jours ne pouvait pas etre faite, et personne ne s'en etait
avise parce que personne n'avait pose l'operation.

Pour memoire, le corpus compte **307 191** videos et
**71** collaborations confirmees — une prevalence par video de
**0.0231 %** si jamais on voulait tirer a ce
niveau-la, ce que 9.2 ne demande pas.

## 2. Capture-recapture, sur deux sources vraiment distinctes

| Source | Createurs trouves |
|---|---:|
| A — la description cite un alias | **36** |
| B — un lobby le nomme dans ses propres videos | **42** |
| **Recouvrement** | **1** |

Les createurs vus par les deux : LeStream

Estimateur de Chapman : **794 createurs** dans la
population totale, contre **77** effectivement trouves.

## 3. Ce que ce chiffre vaut — et ce qu'il ne vaut pas

**Un recouvrement de 1 ne permet aucune estimation fiable.**
Le chiffre ci-dessus est arithmetiquement correct et
statistiquement creux : faire varier le recouvrement de 1 a 2
le ferait passer de 794 a 529. Il ne faut pas le citer comme une
estimation de population.

**Ce qui est solide, c'est le sens** : deux methodes ont trouve
36 et 42 createurs, et n'en partagent que 1. Elles ne
voient donc presque pas les memes gens.

### Deux lectures possibles, que les donnees ne separent pas

**Lecture 1 — la couverture est faible.** Chaque methode
n'attrape qu'un coin d'un ensemble bien plus grand, et le
projet est loin du compte.

**Lecture 2 — les deux populations different.** Les chaines des
lobbies mettent en avant des chefs, des eleveurs et des
personnalites de television ; l'appariement de descriptions
trouve des youtubeurs a sponsors. Si ce sont deux mondes, la
capture-recapture ne s'applique pas : elle exige que les deux
sources tirent dans la meme population.

**Aucune donnee disponible ne tranche entre les deux**, et il
serait malhonnete de presenter la lecture 1 seule — c'est
pourtant celle qui sert le projet.

### Ce qui trancherait

Faire juger a Vincent, dans
`CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx`, **quel type de
personne** chaque nom designe. Si les 42 noms de la voie fiable
sont majoritairement des chefs et des eleveurs, c'est la
lecture 2. S'ils sont des createurs de contenu comparables a
ceux du canal description, c'est la lecture 1 — et la couverture
du projet est mauvaise.

C'est donc la meme tache qui debloque les deux mesures.

