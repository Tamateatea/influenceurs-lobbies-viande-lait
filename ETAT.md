# Etat du projet

**Si tu es une nouvelle session de Claude : lis ce fichier en entier avant
toute action.** Il est fait pour ca. Il est mis a jour a la fin de chaque
session de travail.

Derniere mise a jour : **29 aout 2026, fin de semaine**.

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

### Le jeu de donnees est un MOYEN, pas la livraison

Precision de Vincent le 27 aout 2026, apres avoir lu un resume qui disait
« construire le registre » :

> « ce qu'on veut, c'est construire un outil qui pourrait surveiller
> semi-automatiquement les reseaux sociaux en continu. Si pour l'instant on
> explore et qu'on essaie de constituer un premier jeu de donnees complet, ce
> but ultime ne doit pas etre oublie. »

Le premier jeu de donnees sert a savoir **si l'outil marche**. Il n'est pas la
chose a livrer.

Consequence concrete sur ce qu'on optimise. Deux criteres passent devant la
precision brute sur un corpus fige :

- **le cout d'un tour de veille** — ce qui se paie a chaque passage, en quota,
  en temps machine et surtout en heures de verification humaine ;
- **la resistance au changement** — un nouveau commanditaire, un nouvel alias,
  une plateforme qui modifie ses pages. Une regle qui exige qu'on l'entretienne
  a la main se perime le jour ou personne ne l'entretient.

C'est ce qui departage deux regles a performance egale : voir JOURNAL 61, et la
recommandation de la regle B.

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

## 6. Prochaine session — LIRE CECI EN ENTIER

**Le projet est en pause de methode.** Vincent, le 29 aout au soir :

> « C'est assez decevant. Il va falloir qu'on revoit serieusement notre methode
> lundi. Je suis assez mecontent qu'apres une semaine de travail on en soit la.
> Mais tout ca n'etait pas pour rien. Je sais mieux ce que je veux maintenant.
> Je vais reflechir plus serieusement a comment repartir sur de bonnes bases. »

Il travaille seul le 30 aout, a la main, et **construira lui-meme un jeu de
donnees de depart** pour montrer ce qu'il attend. **Ne rien reconstruire avant
d'avoir vu ce fichier.**

### Ce qu'il faut avoir compris avant de reprendre

**1. On ne fait pas valider une extraction, on fait valider une entite.**

Le jeu « valide » contenait encore `LES JONES` (un groupe fictif invente pour
une video), `Mister V diffuse le vendredi` et `Mister V Vous nous l'aviez de` —
des fragments de titre. Vincent les avait tous marques « c'est un createur ».

Il n'avait pas tort : devant « Mister V diffuse le vendredi », un humain voit
Mister V et repond oui. **La question etait mal posee.** Voir JOURNAL 73.2.

Consequence : la **normalisation et la deduplication des noms doivent preceder
la validation**. Si l'outil ne sait pas produire une entite propre — un nom, un
compte, une plateforme, une audience — il ne doit pas poser la question.

**2. Le format cible a change**, formule par Vincent le 29/08 :

- un **onglet de synthese** : une ligne par influenceur, le nombre de contenus,
  les lobbies concernes ;
- **un onglet par influenceur** : une ligne par contenu ;
- les **restaurateurs traites separement** des createurs de contenu.

**3. Le rendement compare des canaux**, mesure le 29/08 (JOURNAL 71.3) :

    sites des lobbies      42 createurs   5 pages web, une heure
    description YouTube    13 createurs   332 119 videos, six jours
    chaines des lobbies     7 createurs   9 chaines, 40 unites
    publicites payees       ?             jamais mesure valablement

**4. Le canal des publicites n'est PAS invalide.** J'avais conclu 0 % de
precision le 29/08 ; cette mesure etait fausse, l'extrait montre a Vincent ne
contenant pas le pseudo detecte. Voir JOURNAL 72. La question reste ouverte.

### Ce qui tourne tout seul, sans rien faire

La tache planifiee Windows « Veille filiere - tour de nuit » passe a 3h et
9h30, onze etapes. TikTok avance de deux mois par nuit — 9 mois sur 47 au
29/08, le reste vers la mi-septembre.

### Etat au 29 aout 2026

| | |
|---|---|
| YouTube | 2 897 chaines, 332 119 videos |
| TikTok | 9 mois sur 47, 149 711 contenus |
| Meta Ad Library | 7 148 annonces, 69 pages de commanditaires |
| Createurs confirmes par Vincent | **56**, dont 50 jamais documentes ailleurs |
| Jeu de donnees | `cartographie/DATASET.xlsx`, 177 lignes |

