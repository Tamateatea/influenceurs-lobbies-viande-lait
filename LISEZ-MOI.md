# Carte du dossier

Projet : base de donnees publique des collaborations commerciales remunerees
entre createurs de contenu et industrie de la viande et du lait.

Etat au **24 aout 2026**. Depot **prive** sur GitHub :
`github.com/Tamateatea/influenceurs-lobbies-viande-lait`

**Le point d'entree du projet est `ETAT.md`, pas ce fichier.** Ici on decrit
seulement ou sont rangees les choses.

---

## Les documents

| Fichier | Contenu | Qui l'ecrit |
|---|---|---|
| **`ETAT.md`** | **Le point d'entree.** Ou en est le projet maintenant. | Claude |
| **`HYPOTHESES.md`** | Ce qui est teste, confirme, **refute**. A lire avant de tester. | Claude |
| `METHODOLOGIE.md` | Ce qui est **tranche** : principes, definitions, decisions. | Les deux |
| `JOURNAL.md` | Ce qu'on a fait, quand, ce qu'on en a appris. On ajoute a la fin. | Claude |
| `TODO.md` | Qui fait quoi ensuite. | Les deux |
| `CLAUDE.md` | Instructions de travail pour Claude. | Vincent |
| `LISEZ-MOI.md` | Ce fichier. | Les deux |
| `SECRETS.txt` | Jetons et mots de passe. **Jamais envoye sur GitHub.** | Vincent |

---

## Les dossiers

### `cartographie/` — ce que des humains lisent et remplissent

- **`MES_TACHES.xlsx`** — **tout ce qui bloque Claude, en un fichier.** Les
  taches, les comptes dont relever les abonnements, les sites ou chercher des
  noms de campagne. C'est ici qu'on commence.
- **`A_VERIFIER_2.xlsx`** — les candidats a juger. Colonne jaune : l'extrait
  qui a declenche la detection.
- `A_VERIFIER.xlsx` — les 271 candidats juges le 25/08. **Le jeu de
  reference** : il sert a mesurer toute nouvelle regle de detection.
- `A_COMPLETER.xlsx`, `PSEUDOS_A_ARBITRER.xlsx` — **acheves**. Conserves : ils
  contiennent des reponses de Vincent, qui sont des donnees d'entree.
- **`COMPTES.xlsx`** — **le registre des comptes.** Tous les comptes connus du
  projet, une ligne par couple (plateforme, identifiant). Fabrique par script :
  ne pas l'editer a la main, il serait ecrase.
- `PSEUDOS_A_ARBITRER.xlsx` — les jugements de Vincent. **Lu** par le script de
  consolidation, jamais ecrase.
- `cartographie_filiere.xlsx` — le classeur de reference, 12 feuilles :
  interprofessions, industriels, marques, **alias**, agences, influenceurs,
  sources de donnees, journal, et 3 feuilles HATVP_*. Fabrique par un script :
  une modification faite directement dans Excel sera ecrasee.

### `outils/` — les scripts

Chacun explique en tete ce qu'il fait et comment le lancer.

| Script | Ce qu'il fait |
|---|---|
| `generer_cartographie.py` | Fabrique `cartographie_filiere.xlsx`. Tout le contenu ecrit a la main est lisible ici en clair. |
| `generer_classeur_a_completer.py` | Fabrique `A_COMPLETER.xlsx`. Refuse d'ecraser un classeur existant. |
| `extraire_hatvp.py` | Sous-graphe viande/lait du repertoire des lobbies. |
| `extraire_meta_adlibrary.py` | Filtre le rapport Meta Ad Library France sur la filiere. |
| ~~`test_croise_youtube.py`~~ | **Remplace** par `surveiller_youtube.py`. Conserve pour la tracabilite. |
| ~~`extraire_descriptions_youtube.py`~~ | **Remplace** par `surveiller_youtube.py`. C'est lui qui a trouve le premier cas ; conserve pour la tracabilite. |
| `extraire_comptes_suivis.py` | Sort les listes d'abonnements collees dans `A_COMPLETER.xlsx` vers des fichiers propres et dates. |
| `fouiller_sites_lobbies.py` | Cherche des createurs dans les sites des commanditaires eux-memes. |
| `consolider_comptes.py` | **Rassemble toutes les sources en un seul registre**, `COMPTES.xlsx`. |
| `moissonner_videos.py` | Moissonne le catalogue complet des chaines et y cherche la filiere. |
| `moissonner_tiktok.py` | Moissonne la bibliotheque TikTok, mois par mois. |
| `audiences_youtube.py` | Releve le nombre d'abonnes par l'API officielle. |
| `croiser_instagram_youtube.py` | Trouve la chaine YouTube d'un compte Instagram. |
| `croiser_tiktok_youtube.py` | Idem pour les createurs commerciaux TikTok. |
| `croiser_tiktok_registre.py` | Croise les createurs TikTok avec le registre. |
| `decouvrir_alias.py` | Cherche la FORME du remerciement pour trouver des annonceurs inconnus. |
| `nettoyer_detections.py` | Separe les preuves fortes du bruit. Aucun appel reseau. |
| `evaluer_detection.py` | **Mesure les regles contre le jeu de reference de Vincent.** |
| `mesurer_signaux.py` | Compare les signaux entre eux sur le jeu de reference. |
| `balayer_annonceurs_tiktok.py` | Balaye la publicite TikTok sur les termes de la filiere. |
| `generer_classeur_verification.py` | Fabrique les classeurs de verification. |
| `generer_mes_taches.py` | Fabrique `MES_TACHES.xlsx`. |
| `tester_tiktok_commercial.py` | Interroge la Commercial Content Library de TikTok (attend les identifiants). |
| `tester_meta_adlibrary.py` | Interroge l'API Meta Ad Library (attend un jeton utilisateur). |
| `surveiller_youtube.py` | La chaine de surveillance YouTube, quatre signaux. |

### `donnees/` — ce qu'on a telecharge ou releve. Instantanes, pas production.

- `sources/hatvp/` — le repertoire HATVP des representants d'interets (open
  data Etalab, telecharge le 22/08/2026), et dans `extraits/` le sous-graphe
  viande-lait qu'on en tire.
- `sources/meta/` — le rapport public Meta Ad Library France, et
  `annonceurs_filiere.csv`, les 39 pages de la filiere.
- `comptes_vitrines/` — les listes d'abonnements **Instagram** des comptes
  vitrines des lobbies, relevees a la main. Un fichier par compte, date.
- `paye_ton_influence/` — une `NOTE.md` seulement. Leurs fichiers etaient
  vides, supprimes le 22/08. La note garde leurs ordres de grandeur.

### `recherche/` — les MESURES qu'on produit

Chaque releve est horodate, avec le detail ligne par ligne. **Ne jamais
modifier ces fichiers a la main : c'est la trace des mesures.**

```
test_croise_youtube_AAAA-MM-JJ_HHMM.csv / .md
descriptions_youtube_AAAA-MM-JJ_HHMM.csv / .md
comptes_suivis_AAAA-MM-JJ.csv
```

---

## Regle : une mesure non ecrite n'existe pas

Erreur commise le 23/08 et corrigee le 24/08 : un test avait ete lance sans
enregistrer sa sortie. Ses chiffres ne vivaient que dans un tableau recopie a
la main, et n'ont jamais pu etre reproduits.

**Tout script qui mesure ecrit son resultat dans `recherche/`, horodate, avec
le detail ligne par ligne** — pas seulement le resume. Et tout extracteur
prouve par un total qu'il n'a rien perdu en silence.

---

## Qui edite quoi

| Fichier | Qui l'edite | Attention |
|---|---|---|
| `cartographie_filiere.xlsx` | **Le script** | Une modification faite dans Excel sera ecrasee au prochain lancement. |
| `A_COMPLETER.xlsx` | **Vincent** | Aucun script ne l'ecrase. |
| `outils/*.py` | Claude, ou toi | Source de verite du contenu produit. |
| `recherche/**` | Les scripts | Ne jamais modifier a la main. |
| `donnees/**` | Depots manuels | Chaque telechargement est annonce avant d'etre fait. |
| `SECRETS.txt` | Vincent | Exclu de GitHub par `.gitignore`. Verifie. |

Pour corriger une ligne du classeur de reference : me le dire, ou modifier la
liste correspondante dans le script puis relancer :

```
python outils/generer_cartographie.py
```

---

## Conventions du classeur de reference

Chaque ligne factuelle porte un **statut** et une **source**.

| Statut | Signification |
|---|---|
| `CONFIRME` | Verifie sur une source primaire, citee dans la colonne source. |
| `A VERIFIER` | Repris d'une source secondaire, de la presse, ou de memoire. Surligne en orange. |
| `HYPOTHESE` | Suppose, pas encore cherche. Surligne en orange. |

**Rien qui ne soit pas `CONFIRME` ne sort du dossier.** Le classeur est un
outil de travail, pas une publication.

---

## Etat des sources

Le detail des hypotheses testees est dans `HYPOTHESES.md`. Resume :

| Source | Etat |
|---|---|
| Declaration « communication commerciale » YouTube | **Testee.** Fiable, mais ne capte que 2 collaborations sur 14 chez Inoxtag. |
| API SponsorBlock | **Testee.** Precise (12/12), couverture inegale selon les chaines. |
| Description publique YouTube | **Testee.** A trouve le premier cas du projet. |
| Sous-titres YouTube via `yt-dlp` | **Testee.** Atteint le contenu parle. Riche, mais bruyante. |
| Flux RSS de chaine YouTube | **Testes.** 15 dernieres videos seulement, pas de retroactif. |
| HATVP open data | **Exploite.** 35 organisations, 132 mandats, 60 affiliations. |
| Rapport Meta Ad Library France | **Exploite.** 39 pages. Publicites politiques seulement. |
| API Meta Ad Library | **Pas testee.** Attend un jeton et une verification d'identite. |
| Meta Content Library (chercheurs) | **Ecartee.** Affiliation universitaire requise, non disponible. |
| TikTok Commercial Content Library | **Pas testee.** Le plus gros trou du projet. |
| DGCCRF, Legifrance, AGRIP | Identifiees, pas explorees. |
| Paye Ton Influence, Observatoire Citoyen, ARPP | Ecartees. Voir `HYPOTHESES.md`. |
