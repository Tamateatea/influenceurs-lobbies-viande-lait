# Etat du projet

**Si tu es une nouvelle session de Claude : lis ce fichier en entier avant
toute action.** Il est fait pour ca. Il est mis a jour a la fin de chaque
session de travail.

Derniere mise a jour : **27 aout 2026, matin**.

---

## 1. Ce qu'on construit

Un outil qui **surveille en continu YouTube, Instagram et TikTok** et detecte
automatiquement les **collaborations commerciales remunerees** entre createurs
de contenu a forte audience et l'**industrie de la viande et du lait**.

Chaque plateforme demande sa propre methode de collecte, a trouver, tester et
mesurer separement. Le resultat alimente un **repertoire public**, verifie par
un humain avant toute publication, au service du **plaidoyer animaliste**.

Perimetre de depart : la France. Le pays est un champ de donnees, jamais une
hypothese cablee.

### Quatre choses a ne pas confondre

1. **Le but n'est pas de cartographier la filiere.** La cartographie est un
   moyen : elle sert a construire la table d'alias. Le but est de trouver des
   collaborations.
2. **Un abonnement, une mention, une proximite ne sont pas une collaboration.**
   Seule une collaboration commerciale remuneree, etablie sur une source
   primaire, entre au registre.
3. **Un createur generaliste vaut plus qu'un createur culinaire**, pour le
   plaidoyer. Qu'un compte cuisine travaille avec une interprofession de la
   viande n'etonne personne. Qu'Inoxtag soit paye par un lobby laitier rend le
   mecanisme visible. Ce n'est pas un critere d'inclusion — le registre
   n'exclut personne — c'est un **critere de priorite de recherche**.
4. **On est en R&D, pas en production.** Rien n'est publie. On cherche encore
   quelles methodes marchent. Plusieurs semaines ou mois sont acceptables ;
   une affirmation fausse ne l'est pas.

---

## 2. Dans quel ordre lire

| Fichier | Contenu |
|---|---|
| **`ETAT.md`** | Ce fichier. Ou on en est. |
| **`HYPOTHESES.md`** | Ce qui est teste, confirme, **refute**. A lire avant de tester quoi que ce soit. |
| `CLAUDE.md` | Comment travailler avec Vincent. Contraintes fermes. |
| `METHODOLOGIE.md` | Ce qui est **tranche** : principes, definitions, decisions. |
| `JOURNAL.md` | Ce qui a ete fait, quand, et ce qu'on en a appris. |
| `TODO.md` | Qui fait quoi ensuite. |
| `LISEZ-MOI.md` | La carte des dossiers. |

**Le piege le plus couteux : refaire un test deja fait, ou reprendre une piste
deja refutee.** `HYPOTHESES.md` existe pour ca. Le consulter coute deux
minutes.

---

## 3. Ou en est chaque plateforme

### YouTube — chaine validee de bout en bout

**Quatre signaux independants**, tous gratuits, sans compte ni cle :

1. la case « communication commerciale » de YouTube,
2. les segments sponsorises de SponsorBlock,
3. la description publique,
4. la transcription automatique, via `yt-dlp`.

**Les quatre sont mesures contre les jugements de Vincent** (27/08) :

| Signal | Precision | Rappel |
|---|---:|---:|
| Case de declaration | **91 %** | 44 % |
| Transcription | 81 % | 49 % |
| Description | 78 % | **100 %** |
| SponsorBlock | 69 % | 13 % |

**Aucun n'est suffisant seul.** Le chiffre qui justifie le projet : **40 vraies
collaborations sur 71 ne sont pas declarees**. Et la case dit qu'un partenariat
paye existe, **pas par qui** — seule la conjonction avec l'alias designe le
commanditaire.

La transcription atteint l'oral que rien d'autre ne voit — un cas sur 37 videos
sans signal en description — mais coute plusieurs secondes par video. Elle est
donc employee **en second rideau**, sur les chaines deja identifiees, jamais a
grande echelle. Voir JOURNAL 53 et 57.

**Premier cas reel trouve** : Inoxtag x CNIEL (`@lesproduitslaitiers`), non
declare sur YouTube, identifie par la table d'alias.

**La recherche retroactive fonctionne.** L'API rend 50 videos avec leurs
descriptions pour 1 unite de quota. Au 27/08 au soir : **2 157 chaines sur
2 660 et 306 630 videos** moissonnees. Le flux RSS, limite a 15 videos, n'est
plus la contrainte.

> **Ou reprendre :** `python outils/moissonner_videos.py --budget 4000` reprend
> tout seul a la 2 158e chaine — l'etat est dans `donnees/moisson_videos.json`.
> Puis `exporter_moisson.py`, `nettoyer_detections.py`, et le classeur.
> `exporter_moisson.py` peut tourner a tout moment, meme pendant la moisson :
> il relit l'etat, sans reseau.

**247 videos citent un alias d'interprofession** apres nettoyage. 175 sont
deja tranchees ; les **72 nouvelles** attendent dans `A_VERIFIER_3.xlsx`.

**Ce qui reste a faire :** instruire ces 72 videos, trancher
`CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx`, et decider du sort de la liste
`GENERIQUES` de la regle D — mesuree le 27/08 comme **nuisible hors CNIEL**
(JOURNAL 56).

### Instagram — bloquee sur l'acces

Le mode A (interroger par annonceur) suppose l'API Ad Library, donc un jeton
Meta, donc une verification d'identite que Vincent a accepte de faire.

La question ouverte, et c'est la plus importante : **l'API expose-t-elle les
contenus de marque**, ou seulement les publicites achetees ?

Acquis : les listes d'abonnements des comptes vitrines ont ete relevees a la
main (538 comptes, `recherche/comptes_suivis_2026-08-24.csv`). Elles servent a
**cibler**, jamais a conclure.

### TikTok — accessible depuis le 25/08. Riche, mais pas ce qu'on croyait

L'API Commercial Content de TikTok rend **directement** ce que le registre
cherche : `creator.username` + `brand_names` + `label` + date, pour l'EEE,
depuis octobre 2022. Pas d'inference, pas de faux positif : c'est la
plateforme qui declare.

**Et elle n'exige pas d'affiliation universitaire** — contrairement a la
Research API de TikTok et a la Meta Content Library. Elle est ouverte au
public, aux journalistes et aux associations. Gratuite, ~2 jours ouvres.

**Resultat reel :** 8 061 createurs francais avec un label de partenariat
remunere declare par la plateforme. Mais `brand_names` est vide (2 sur
20 000) : on sait qu'il y a partenariat, pas pour qui.

L'endpoint `ad/query` couvre les publicites achetees et permet, lui, une
recherche par mot-cle qui fonctionne : « lait » sort NESTLE FRANCE, « fromage »
sort BEL. Il nomme aussi l'agence (`advertiser.paid_for_by`).

**Les deux ne se joignent pas** : aucun chemin de l'annonceur au createur.
TikTok apporte donc une **population de reference** plutot qu'un moteur de
decouverte. Voir JOURNAL 34.

### Sites des commanditaires — piste ouverte le 24 aout

La seule source dont les resultats sont des **declarations du commanditaire**
et non des inferences sur du contenu. 26 pseudos recoltes sur les sites des
interprofessions ; INAPORC a une rubrique « Les recettes des influenceurs »
qui nomme ses partenaires, et decrit sur son site deux lives Twitch avec
Gastronogeek et LeBouseuh, produits avec Webedia.

Inegal selon les entites : INAPORC publie beaucoup, INTERBEV presque rien.
`outils/fouiller_sites_lobbies.py`.

---

## 4. Les regles de travail, en resume

Le detail est en METHODOLOGIE.md section 13. L'essentiel :

- **Etiqueter chaque affirmation** : `MESURE` (fichier nomme), `RAPPORTE`
  (source citee), `SUPPOSE` (rien derriere). Y compris dans les messages a
  Vincent.
- **Ne jamais ecrire un chiffre sans nommer le fichier qui le produit.**
- **Tout script qui mesure ecrit** dans `recherche/`, horodate, ligne par
  ligne.
- **Tout extracteur prouve qu'il n'a rien perdu**, par un total.
- **Rien ne se publie sans verification humaine.** Ce n'est pas une bequille
  temporaire : voir JOURNAL 20.4, ou la transcription produit un faux positif
  parfaitement credible des la premiere video.

---

## 5. Qui porte quoi

**Vincent** — il est le seul element constant du projet, donc il porte ce dont
la continuite depend :

- les **decisions et leurs raisons**, dans son propre fichier de notes ;
- les **jugements humains** : arbitrage de contenus, contexte francais,
  confirmation de comptes ;
- les **contacts** et les relations.

**Claude** — les mesures, les scripts, `HYPOTHESES.md`, `JOURNAL.md`, et la
tenue a jour de ce fichier.

En cas de desaccord entre les deux memoires : **Vincent fait foi sur ce qui a
ete decide, les fichiers font foi sur ce qui a ete mesure.**

Vincent n'a **aucune experience de code**. Les taches qu'on lui confie passent
par la conversation et par `cartographie/A_COMPLETER.xlsx`, jamais par un
fichier `.md`.

---

## 6. Prochaine session — a faire en premier

**La source la plus directe du projet, trouvee le 27/08 :** les
interprofessions ont **leurs propres chaines YouTube**, ou elles publient des
videos nommant les createurs invites. Ici le commanditaire annonce lui-meme la
collaboration : plus aucune inference.

**218 noms** apres correction du rapprochement (JOURNAL 55 et 58), dont **42
par la voie fiable** — Pierre Chomet (31 videos, CIFOG et CNIEL), Morgan VS
(12, CNIEL), L'Amour Boeuf (10, INTERBEV), **Mister V** (CNIEL), Brigitte
Lecordier (CNIEL). Les 176 autres viennent d'une voie non mesuree et sont
peut-etre des noms de series : `CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx` attend
le jugement de Vincent.

> Une version anterieure de cette section annoncait **Norman (11,2 M)** et
> **Inoxtag** en tete. **C'etait faux** : « Norman » etait « e-Boucherie
> normande », reconnu sur six caracteres. Voir JOURNAL 58. Mister V, lui, est
> confirme.

**Etat du registre au 27/08 : 6 875 comptes** — 2 620 YouTube, 2 187 TikTok,
2 039 Instagram. 39 % avec audience connue. La population de surveillance est
passee de 27 chaines nommees a la main a 2 620 derivees des sources.

**Ancien etat au 24/08 au soir :** `cartographie/COMPTES.xlsx` —
**766 comptes** (552 Instagram, 185 YouTube, 29 indetermines), dont 26 % avec
audience connue. La liste de surveillance YouTube est passee de 27 chaines
nommees a la main a **185 derivees des sources**.

**Pour Vincent, par ordre de valeur :**

1. **Candidater a la Commercial Content API de TikTok** —
   `developers.tiktok.com/application/commercial-content-api`. Gratuit,
   ~2 jours, **pas d'affiliation universitaire requise**. C'est le meilleur
   rapport effort/resultat de tout le projet.
2. **Arbitrer les 26 pseudos recoltes** sur les sites des lobbies : lesquels
   sont des createurs remuneres, lesquels sont des eleveurs ou des marques ?
3. **Meta** : reprendre apres TikTok. Le jeton d'application est refuse, il
   faut un jeton UTILISATEUR.

**Pour Claude :**

4. **Relancer `outils/surveiller_youtube.py`** sur les 24 chaines officielles
   une fois la limitation HTTP 429 retombee. Commencer par `--videos 10`.
5. **Verifier les chaines YouTube et Twitch de LeBouseuh et Gastronogeek**
   pour retrouver les « best of » des lives INAPORC — un cas documente par le
   commanditaire, donc un excellent test de bout en bout.
6. **Resoudre Seb la Frite et Zack Nani**, dont aucune chaine verifiee ne
   remonte sous ce nom.
7. **Ajouter Webedia a la feuille Agences** du classeur, avec sa source
   primaire (le site d'INAPORC).

**Ne pas oublier :** un createur a plusieurs chaines, et la collaboration
CNIEL trouvee etait sur une chaine secondaire.

Vincent doit, de son cote : terminer la verification d'identite Meta, et
arbitrer les nouveaux cas que le test elargi fera remonter.
