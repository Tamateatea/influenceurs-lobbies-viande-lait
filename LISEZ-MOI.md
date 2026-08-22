# Carte du dossier

Projet : base de donnees publique des collaborations commerciales remunerees
entre createurs de contenu et industrie de la viande et du lait, en France.

Rien n'est encore construit. A ce stade le dossier contient de la recherche et
une cartographie, pas un outil.

---

## Ou est quoi

```
InfluencersxMeat&MilkLobbyTracker/
│
├── LISEZ-MOI.md          ← ce fichier : la carte du dossier
├── TODO.md               ← A LIRE EN DEBUT DE SESSION. Qui fait quoi ensuite.
├── METHODOLOGIE.md       ← comment on compte s'y prendre, et ce qui n'est pas tranche
│
├── cartographie/
│   └── cartographie_filiere.xlsx
│         Le classeur principal. 12 feuilles : interprofessions, industriels,
│         marques, alias, agences, influenceurs, sources de donnees, journal,
│         et 3 feuilles HATVP_* extraites du repertoire des lobbies.
│         C'est le document a partager avec des collegues.
│
├── outils/
│   ├── generer_cartographie.py
│   │     Le script qui fabrique le classeur ci-dessus. Tout le contenu ecrit
│   │     a la main est lisible ici en texte clair.
│   └── extraire_hatvp.py
│         Extrait le sous-graphe viande/lait du repertoire des lobbies.
│         Produit les 3 feuilles HATVP_* du classeur.
│
├── donnees/
│   ├── paye_ton_influence/
│   │     Ne contient plus qu'une NOTE.md. Les fichiers telecharges depuis leur
│   │     observatoire etaient vides : supprimes le 22/08. La note garde leurs
│   │     ordres de grandeur, qui servent a dimensionner notre collecte.
│   └── sources/hatvp/
│         Le repertoire HATVP des representants d'interets (open data Etalab,
│         telecharge le 22/08/2026), sa notice, son dictionnaire de donnees,
│         et dans extraits/ le sous-graphe viande-lait qu'on en tire.
│
└── recherche/
      Vide pour l'instant. Notes et extractions ponctuelles.
```

---

## Qui edite quoi

C'est la seule regle technique du dossier, et elle evite de perdre du travail.

| Fichier | Qui l'edite | Attention |
|---|---|---|
| `cartographie_filiere.xlsx` | **Le script** | Une modification faite directement dans Excel sera ecrasee au prochain lancement. |
| `outils/generer_cartographie.py` | Claude, ou toi | Source de verite du contenu du classeur. |
| `LISEZ-MOI.md`, `METHODOLOGIE.md` | Les deux | |
| `donnees/**` | Depots manuels | Chaque telechargement est annonce avant d'etre fait. |

Si tu veux corriger une ligne du classeur, deux options : me le dire, ou
modifier la liste correspondante dans le script puis relancer :

```
python outils/generer_cartographie.py
```

Si tu preferes editer le classeur a la main et te passer du script, dis-le :
on supprime le script et le `.xlsx` devient la source de verite. C'est un
arbitrage, pas une contrainte technique.

---

## Conventions du classeur

Chaque ligne factuelle porte un **statut** et une **source**.

| Statut | Signification |
|---|---|
| `CONFIRME` | Verifie sur une source primaire, citee dans la colonne source. |
| `A VERIFIER` | Repris d'une source secondaire, de la presse, ou de memoire. Surligne en orange. |
| `HYPOTHESE` | Suppose, pas encore cherche. Surligne en orange. |

Regle : **rien qui ne soit pas `CONFIRME` ne sort du dossier.** Le classeur est
un outil de travail, pas une publication.

Aujourd'hui, sur 142 lignes, une bonne moitie est en orange. C'est normal a ce
stade et c'est fait pour se voir.

---

## Etat des sources, au 22 aout 2026

| Source | Etat |
|---|---|
| Observatoire Citoyen de la Publicite | Code source lu. Pas de jeu de donnees. |
| Observatoire Paye Ton Influence | Export teste : ne renvoie que les tuiles. Aucune donnee a recuperer. Abandonne comme source. |
| HATVP open data | **Telecharge et exploite.** 35 organisations de la filiere, 132 mandats, 60 affiliations. |
| SponsorBlock, Meta Ad Library, TikTok CCL | Identifiees, **pas encore testees**. |
| DGCCRF, Legifrance, AGRIP | Identifiees, pas encore explorees. |
| ARPP | Fiabilite limitee, voir METHODOLOGIE.md. |

Le detail complet est dans la feuille `Sources_de_donnees` du classeur.
