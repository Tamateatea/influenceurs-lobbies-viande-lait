# Etat du projet

**Si tu es une nouvelle session de Claude : lis ce fichier en entier avant
toute action.** Il est fait pour ca. Il est mis a jour a la fin de chaque
session de travail.

Derniere mise a jour : **24 aout 2026, fin de la 2e session** (nuit).

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

**Aucun n'est suffisant seul, et c'est mesure.** La case de declaration ne
capte que 2 collaborations sur 14 chez Inoxtag. SponsorBlock est precis mais
inegal selon les chaines. La description rate l'oral. La transcription atteint
tout mais produit des faux positifs qu'aucun motif automatique ne rattrape.

**Premier cas reel trouve** : Inoxtag x CNIEL (`@lesproduitslaitiers`), non
declare sur YouTube, identifie par la table d'alias.

**Ce qui reste a faire :** elargir a plusieurs dizaines de chaines pour passer
de la preuve d'existence a la mesure.

### Instagram — bloquee sur l'acces

Le mode A (interroger par annonceur) suppose l'API Ad Library, donc un jeton
Meta, donc une verification d'identite que Vincent a accepte de faire.

La question ouverte, et c'est la plus importante : **l'API expose-t-elle les
contenus de marque**, ou seulement les publicites achetees ?

Acquis : les listes d'abonnements des comptes vitrines ont ete relevees a la
main (538 comptes, `recherche/comptes_suivis_2026-08-24.csv`). Elles servent a
**cibler**, jamais a conclure.

### TikTok — la source la plus prometteuse, bloquee sur une candidature

L'API Commercial Content de TikTok rend **directement** ce que le registre
cherche : `creator.username` + `brand_names` + `label` + date, pour l'EEE,
depuis octobre 2022. Pas d'inference, pas de faux positif : c'est la
plateforme qui declare.

**Et elle n'exige pas d'affiliation universitaire** — contrairement a la
Research API de TikTok et a la Meta Content Library. Elle est ouverte au
public, aux journalistes et aux associations. Gratuite, ~2 jours ouvres.

L'endpoint est verifie vivant. L'outil est ecrit et pret
(`outils/tester_tiktok_commercial.py`). **Il ne manque que la candidature,
qui revient a Vincent.**

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

**Etat du registre au 24/08 au soir :** `cartographie/COMPTES.xlsx` —
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
