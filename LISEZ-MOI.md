# Carte du dossier

Projet : base de donnees publique des collaborations commerciales remunerees
entre createurs de contenu et industrie de la viande et du lait, en France.

Rien n'est encore construit. A ce stade le dossier contient de la recherche,
une cartographie et des tests de sources, pas un outil.

Etat au **24 aout 2026**.

---

## Ou est quoi

```
InfluencersxMeat&MilkLobbyTracker/
│
├── LISEZ-MOI.md          ← ce fichier : la carte du dossier
├── TODO.md               ← A LIRE EN DEBUT DE SESSION. Qui fait quoi ensuite.
├── METHODOLOGIE.md       ← comment on compte s'y prendre, et ce qui n'est pas tranche
├── CLAUDE.md             ← instructions de travail pour Claude
│
├── cartographie/
│   └── cartographie_filiere.xlsx
│         Le classeur principal. 12 feuilles : interprofessions, industriels,
│         marques, alias, agences, influenceurs, sources de donnees, journal,
│         et 3 feuilles HATVP_* extraites du repertoire des lobbies.
│         C'est le document a partager avec des collegues.
│
├── outils/               ← les scripts. Chacun dit en tete ce qu'il fait.
│   ├── generer_cartographie.py
│   │     Fabrique le classeur ci-dessus. Tout le contenu ecrit a la main
│   │     est lisible ici en texte clair.
│   ├── extraire_hatvp.py
│   │     Extrait le sous-graphe viande/lait du repertoire des lobbies.
│   │     Produit les 3 feuilles HATVP_* du classeur.
│   ├── extraire_meta_adlibrary.py
│   │     Filtre le rapport public Meta Ad Library France sur la filiere.
│   │     Produit donnees/sources/meta/annonceurs_filiere.csv
│   └── test_croise_youtube.py
│         Mesure, sur des chaines francaises, le croisement des deux signaux
│         de collaboration : declaration YouTube et segment SponsorBlock.
│         Ecrit ses resultats dans recherche/.
│
├── donnees/              ← ce qu'on a telecharge. Instantanes, pas production.
│   ├── paye_ton_influence/
│   │     Ne contient plus qu'une NOTE.md. Les fichiers telecharges depuis leur
│   │     observatoire etaient vides : supprimes le 22/08. La note garde leurs
│   │     ordres de grandeur, qui servent a dimensionner notre collecte.
│   ├── sources/hatvp/
│   │     Le repertoire HATVP des representants d'interets (open data Etalab,
│   │     telecharge le 22/08/2026), sa notice, son dictionnaire de donnees,
│   │     et dans extraits/ le sous-graphe viande-lait qu'on en tire.
│   └── sources/meta/
│         Le rapport public Meta Ad Library France (telecharge le 22/08/2026)
│         et annonceurs_filiere.csv, les 39 pages de la filiere qu'on en tire.
│
└── recherche/            ← les MESURES qu'on produit. Chaque releve est date.
      test_croise_youtube_AAAA-MM-JJ_HHMM.csv  le detail, une ligne par video
      test_croise_youtube_AAAA-MM-JJ_HHMM.md   le resume lisible du meme releve
```

---

## Regle : une mesure non ecrite n'existe pas

Erreur commise le 23/08 et corrigee le 24/08 : un test avait ete lance sans
enregistrer sa sortie. Ses chiffres ne vivaient que dans un tableau recopie a
la main dans METHODOLOGIE.md, et n'ont pas pu etre reproduits.

Consequence, valable pour tout le projet : **tout script qui mesure quelque
chose ecrit son resultat dans `recherche/`, horodate, avec le detail ligne par
ligne** — pas seulement le resume. Sans cela on ne peut ni comparer deux
releves, ni verifier une affirmation, ni reprendre le travail a la session
suivante.

---

## Qui edite quoi

C'est la seule regle technique du dossier, et elle evite de perdre du travail.

| Fichier | Qui l'edite | Attention |
|---|---|---|
| `cartographie_filiere.xlsx` | **Le script** | Une modification faite directement dans Excel sera ecrasee au prochain lancement. |
| `outils/*.py` | Claude, ou toi | Source de verite du contenu produit. |
| `LISEZ-MOI.md`, `METHODOLOGIE.md`, `TODO.md` | Les deux | |
| `donnees/**` | Depots manuels | Chaque telechargement est annonce avant d'etre fait. |
| `recherche/**` | Les scripts | Ne jamais modifier a la main : c'est la trace des mesures. |

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

## Etat des sources, au 24 aout 2026

| Source | Etat |
|---|---|
| Declaration « communication commerciale » YouTube | **Testee et reproduite.** Lisible sans compte ni cle. Signal stable : 3 relectures identiques. Le plus solide a ce jour. |
| API SponsorBlock | **Testee.** Fonctionne sans cle. Couvre bien les chaines francaises testees. Dump en masse desactive : interrogation video par video. |
| Flux RSS de chaine YouTube | **Testes.** Fonctionnent sans cle. Ne donnent que les ~15 dernieres videos. |
| HATVP open data | **Telecharge et exploite.** 35 organisations de la filiere, 132 mandats, 60 affiliations. |
| Rapport Meta Ad Library France | **Telecharge et exploite.** 39 pages de la filiere. Ne couvre que les publicites dites politiques, pas les contenus de marque. |
| API Meta Ad Library (`ad_type=ALL`) | Identifiee, **pas testee** : demande un jeton developpeur Meta (gratuit). |
| Meta Content Library (chercheurs) | Identifiee, **pas testee** : demande une affiliation universitaire. |
| TikTok Commercial Content Library | Accessible, **pas encore testee**. |
| DGCCRF, Legifrance, AGRIP | Identifiees, pas encore explorees. |
| Observatoire Paye Ton Influence | Export teste : ne renvoie que des agregats. Ecartee comme source. |
| Observatoire Citoyen de la Publicite | Code source lu. Pas de jeu de donnees. |
| ARPP | Fiabilite limitee, voir METHODOLOGIE.md section 5. |

Le detail complet est dans la feuille `Sources_de_donnees` du classeur.
