# Mesure des signaux contre le jeu de reference — 2026-08-25

Produit par `outils/mesurer_signaux.py`.

- Candidats juges par Vincent : **271**
- Interrogations SponsorBlock exploitables : **271**
- Vraies collaborations dans cet ensemble : **67**

| Signal | Retenus | Vrais | Faux | Precision | Rappel |
|---|---:|---:|---:|---:|---:|
| SponsorBlock : au moins un segment | 13 | 9 | 4 | 69 % | 13 % |
| Indice commercial en description | 82 | 58 | 24 | 71 % | 87 % |
| Mention legale en description | 21 | 15 | 6 | 71 % | 22 % |
| Code promo en description | 2 | 0 | 2 | 0 % | 0 % |
| SponsorBlock OU indice commercial | 83 | 59 | 24 | 71 % | 88 % |
| SponsorBlock ET indice commercial | 12 | 8 | 4 | 67 % | 12 % |

## Capture-recapture entre SponsorBlock et la description

METHODOLOGIE section 9.3 : deux methodes independantes appliquees au
meme echantillon permettent d'estimer ce que **les deux** ratent.

- Vraies collaborations vues par SponsorBlock : **9**
- Vues par la description : **58**
- Vues par les deux : **8**

- Estimation de la population totale (a x b / m) : **65** collaborations
- Soit **-2** que les deux methodes manquent ensemble

## Limite de cette mesure

Les 271 candidats viennent tous du canal « description ». Un signal
peut donc paraitre faible ici simplement parce qu'on ne le mesure
que la ou l'autre a deja trouve quelque chose. **Ces chiffres
decrivent le comportement des signaux sur ce sous-ensemble, pas
dans l'absolu.** Seul le tirage aleatoire y remediera.

