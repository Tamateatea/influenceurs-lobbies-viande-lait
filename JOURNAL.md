# Journal de methode

**A quoi sert ce document.** Pouvoir expliquer plus tard, a un journaliste ou
a un partenaire, **comment on sait ce qu'on affirme** — y compris les pistes
abandonnees et pourquoi. Un registre dont on ne sait plus reconstituer la
fabrication n'est pas defendable.

**Regle d'ecriture : on ajoute a la fin, on ne reecrit jamais.** Une erreur
constatee plus tard devient une nouvelle entree qui corrige l'ancienne, et
l'ancienne recoit un avertissement. On ne fait pas disparaitre une mesure
fausse : on montre comment on s'en est apercu.

Les numeros de section sont ceux d'origine et ne bougent pas : d'autres
entrees y renvoient.

| Entree | Date | Sujet |
|---|---|---|
| 7 | 22-23 aout | Recherche de faisabilite, premiers tests de sources |
| 12 | 23 aout | La declaration YouTube est lisible par un programme |
| 14 | 23 aout | Premier test croise — **chiffres retires de l'usage** |
| 16 | 24 aout | Test croise refait ; correction d'un bug de resolution |
| 17 | 24 aout | **Premier cas reel trouve** ; un troisieme signal |
| 18 | 24 aout | Arbitrage humain des 12 videos ; listes Instagram |
| 19 | 24 aout | Ce qu'un abonnement ne prouve pas — recadrage |
| 20 | 24 aout | Les sous-titres deviennent accessibles ; mise sur GitHub |

---

## 7. Journal de methode

Cette section est tenue a jour a chaque session. Objectif : pouvoir expliquer
plus tard, a un journaliste ou a un partenaire, **comment on sait ce qu'on
affirme** — y compris les pistes abandonnees et pourquoi. Un registre dont on
ne sait plus reconstituer la fabrication n'est pas defendable.

### 22-23 aout 2026 — recherche de faisabilite et test des sources

**Ce qui a ete etabli sur le cadre juridique.** La loi n° 2023-451 du 9 juin
2023 impose la mention « Publicite » ou « Collaboration commerciale » sur
chaque contenu. Une brigade de 15 agents de la DGCCRF controle son application.
Consequence pour nous : le signal existe legalement, mais l'observation de
terrain (voir plus bas) montre qu'il est applique de facon tres partielle.

**Sources ecartees.**

- *Observatoire Paye Ton Influence* : pas de jeu de donnees exportable, seulement
  des agregats. Detail dans donnees/paye_ton_influence/NOTE.md.
- *Observatoire Citoyen de la Publicite* : pas de donnees non plus, mais leur
  code source est public (Rails). Leur modele separe `reports` (signalements
  bruts) de `problems` (cas instruits et publies) via un workflow d'etapes.
  On reprend cette forme. Leur champ `brand` est une chaine libre sans table
  d'entites : meme angle mort que Paye Ton Influence.
- *ARPP* : organe d'autoregulation des annonceurs, finance par eux, ne publie
  que des agregats. Position d'acteur, pas mesure independante.

**Source exploitee : le repertoire HATVP des representants d'interets.**
Archive « Vues separees CSV », licence Etalab, mise a jour quotidienne.
Extraction par outils/extraire_hatvp.py : filtrage des denominations sur un
motif viande/lait, exclusion manuelle des faux positifs (peche et « elevages
marins », HLM du Limousin, mutuelles, patronymes en « Boucher »). Resultat :
35 organisations, 132 mandats, 60 affiliations, toutes avec SIREN et dates.

Limite a retenir : **ce jeu de donnees decrit le lobbying institutionnel, pas
le marketing d'influence.** Ogilvy, Herezie et Shokola n'y figurent pas au
titre de leurs campagnes, parce que le marketing d'influence n'est pas
juridiquement une activite de representation d'interets. Ne jamais presenter
ces mandats comme des contrats de campagne.

**Source exploitee : le rapport public de la Meta Ad Library (France, 15 avril
2019 - 5 octobre 2025).** 63 707 annonceurs. Filtrage sur motif viande/lait.

Perimetre exact, et c'est essentiel : ce rapport ne couvre **que les publicites
relatives a des enjeux sociaux, electoraux ou politiques**. Il ne contient ni
les publicites commerciales ordinaires, ni les contenus de marque.

Constat central : Meta classe la publicite des lobbies de la viande et du lait
dans les **publicites a caractere politique**. « Aimez la viande » (Interbev),
« Les Produits Laitiers » (Cniel) et la Confederation Nationale de l'Elevage y
figurent avec montants, nombre d'annonces et identifiants de page.

Second constat, verifiable ligne par ligne : la majorite de ces annonces ont
ete diffusees **sans mention du financeur** (« These ads ran without a
disclaimer »). Sur les 9 annonces de la page « Aimez la viande », 3 seulement
declarent Interbev. C'est le meme brouillage du donneur d'ordre que celui
observe sur les campagnes d'influence.

**Sources testees techniquement, accessibles sans cle ni compte.**

- *API SponsorBlock* : fonctionnelle, gratuite, sans authentification. Renvoie
  les segments sponsorises horodates d'une video YouTube. En revanche le
  telechargement en masse de la base est desactive (« CSV downloads disabled,
  please use sb-mirror rsync »). L'usage retenu est donc l'interrogation video
  par video, pas le dump.
- *Flux RSS de chaine YouTube* : `youtube.com/feeds/videos.xml?channel_id=...`
  repond sans cle API et donne les dernieres videos d'une chaine. Combine a
  SponsorBlock, cela forme une chaine de surveillance YouTube a cout nul.
- *library.tiktok.com* : accessible.

**Limite connue de l'API Meta Ad Library.** Le parametre `ad_type=ALL`, qui
renvoie les publicites commerciales ordinaires, ne fonctionne que pour les pays
de l'Union europeenne et le Royaume-Uni — donc la France est couverte, avec une
fenetre glissante d'un an et une limite de 200 appels par heure. Les publicites
politiques, elles, sont conservees sept ans. A tester reellement : un compte
developpeur Meta est necessaire.

---

## 12. Journal de methode — 23 aout 2026 (suite)

**Confirme : la mention de communication commerciale de YouTube est lisible par
un programme, gratuitement et sans compte.** La page publique d'une video
contient un objet `paidContentOverlay.paidContentOverlayRenderer` lorsque le
createur a coche la case de declaration. Verifie sur quatre videos : present
sur la video de controle positive, absent sur les trois autres. Le nom du
champ est stable ; seul le texte affiche est traduit selon la langue servie.

Portee : ce signal n'est ni francais ni dependant d'une communaute de
benevoles. Il couvre toute video declaree sur YouTube, partout. C'est le signal
le plus solide identifie a ce jour, toutes plateformes confondues.

Limite : il indique qu'il y a partenariat, pas avec qui. L'identification du
commanditaire reste a faire — c'est le role de la table d'alias.

**Correction a une affirmation precedente sur le DSA.** Il avait ete suggere
que TikTok beneficiait d'un regime de transparence particulier du fait du DSA.
C'est inexact : le DSA impose un registre publicitaire a **toutes** les tres
grandes plateformes, YouTube et Meta comprises. La distinction reelle, plus
etroite, est que la bibliotheque de TikTok inclut explicitement les
**publications organiques portant le label de partenariat remunere**, et pas
seulement les publicites achetees. Reste a verifier si les registres de Google
et de Meta font de meme. **Non teste a ce jour.**

---

## 14. Journal de methode — premier test croise, 23 aout 2026

> **AVERTISSEMENT, ajoute le 24 aout 2026.** Les chiffres de cette section ne
> sont pas reproductibles : le script ne les enregistrait pas, et sa resolution
> des chaines etait defectueuse. Ils sont conserves pour la tracabilite du
> journal mais **ne doivent plus etre cites**. Voir section 16.

Premiere mesure reelle, sur 32 videos recentes de deux grandes chaines
francaises (Squeezie, Inoxtag), en croisant les deux signaux YouTube.

| Situation | Videos |
|---|---|
| Declaree ET segment SponsorBlock | 3 |
| Declaree seulement | 2 |
| **Segment SponsorBlock SANS declaration** | **2** |
| Aucun signal | 25 |

**Trois enseignements.**

1. L'hypothese du desaccord tient sur des cas francais reels : deux videos
   d'Inoxtag portent des segments sponsorises reperes par SponsorBlock sans
   mention de communication commerciale declaree.
2. **SponsorBlock couvre les chaines francaises mieux que prevu.** Le
   pessimisme exprime plus haut dans ce document etait excessif : les deux
   chaines testees sont annotees.
3. Environ 22 % des videos recentes de ces chaines portent au moins un signal
   commercial. Utile comme ordre de grandeur pour dimensionner la suite.

**Ce que ce test ne prouve pas.** 32 videos et deux chaines, ce n'est pas une
mesure, c'est une preuve d'existence. Deux chaines n'ont pas pu etre resolues.
Surtout, « SponsorBlock sans declaration » ne prouve pas la non-declaration :
le createur a pu annoncer le partenariat oralement ou a l'ecran sans cocher la
case, et un benevole a pu etiqueter comme sponsor une auto-promotion. Le
protocole de la METHODOLOGIE.md section 9 reste necessaire.

---

## 16. Journal de methode — 24 aout 2026 : le test croise refait, et une correction

### 16.1 Pourquoi on l'a refait

Vincent ne se souvenait pas du test decrit en section 14. Verification faite :
le script existait bien, mais **il n'ecrivait rien** — il affichait ses
resultats a l'ecran et rien d'autre. Le tableau de la section 14 avait donc ete
recopie a la main depuis une sortie de console perdue depuis.

C'est une faute de methode, pas un detail. Un projet qui doit pouvoir expliquer
« comment on sait ce qu'on affirme » ne peut pas reposer sur des chiffres qu'on
ne peut ni retrouver, ni recompter, ni rattacher a des videos precises.

**Regle posee, valable pour tout le projet :** tout script qui mesure ecrit
son resultat dans `recherche/`, horodate, avec **le detail ligne par ligne** et
pas seulement le resume. Voir LISEZ-MOI.md, « Une mesure non ecrite n'existe
pas ».

### 16.2 Le releve du 24 aout

Meme protocole, meme liste de chaines, script corrige et cette fois enregistre :
`recherche/test_croise_youtube_2026-08-24_1050.csv` et son resume `.md`.

| Situation | 23/08 (non reproductible) | 24/08 (enregistre) |
|---|---|---|
| Declaree ET segment SponsorBlock | 3 | 3 |
| Declaree seulement | 2 | 0 |
| **Segment SponsorBlock SANS declaration** | **2** | **12** |
| Aucun signal | 25 | 17 |
| Total videos | 32 | 32 |

Les deux relevés portent sur 32 videos et sur les memes chaines resolues
(Squeezie, Inoxtag, Valouzz — Mister V et McFly & Carlito restent non resolus).
Une journee d'ecart ne peut pas expliquer un tel deplacement.

**Cause la plus probable, et elle est technique.** L'ancien script resolvait un
`@pseudo` en identifiant de chaine en prenant *la chaine `UC...` la plus
frequente dans la page*. Or une page de chaine YouTube contient les
identifiants de toutes les chaines recommandees. Cette heuristique pouvait
donc designer une autre chaine que celle demandee. Le script lit desormais la
cle `"channelId"` du JSON embarque, ce qui est univoque. **On ne peut pas
savoir sur quelles chaines portait reellement le releve du 23/08** : c'est
precisement ce que l'absence d'enregistrement rend indecidable.

**Les chiffres de la section 14 sont donc retires de l'usage.** Ils restent
ecrits pour la tracabilite du journal, mais ne doivent plus etre cites.

### 16.3 Le signal de declaration est stable

Doute legitime souleve par le releve : si la page video etait servie
differemment d'un appel a l'autre (page de consentement, blocage automatise),
la declaration serait detectee au hasard. Teste : six videos relues trois fois
chacune, dix-huit lectures, **resultat identique a chaque fois**, pages
completes d'environ 1,2 Mo. Le signal `paidContentOverlayRenderer` est donc
reproductible et n'est pas la source de l'ecart.

### 16.4 Ce que le releve montre vraiment — et le piege qu'il tend

Le detail par chaine est bien plus parlant que le total :

| Chaine | Videos | Segment SponsorBlock | Declaration |
|---|---|---|---|
| Inoxtag | 15 | **14** | 2 |
| Squeezie | 15 | 1 | 1 |
| Valouzz | 2 | 0 | 0 |

Quatorze videos sur quinze annotees chez Inoxtag, une sur quinze chez Squeezie.
Un tel ecart entre deux chaines comparables ne se lit pas comme « Inoxtag est
quatorze fois plus sponsorise que Squeezie ».

Trois lectures concurrentes, aucune ecartee pour l'instant (METHODOLOGIE.md section 10) :

1. Inoxtag place effectivement un sponsor dans presque chaque video et ne coche
   pas la case de declaration.
2. Les benevoles de SponsorBlock etiquettent chez lui des sequences
   d'auto-promotion recurrentes — annonce de sa propre marque, de son film, de
   son merchandising — qui ne sont pas des collaborations remunerees par un
   tiers.
3. Une chaine tres annotee par la communaute recoit des segments plus
   systematiquement qu'une chaine peu annotee, independamment du contenu reel.

**Conclusion operationnelle : le taux de « SponsorBlock sans declaration » n'est
pas utilisable comme mesure de non-declaration tant que ces 12 videos n'ont pas
ete regardees a la main.** C'est exactement le probleme de precision de la
METHODOLOGIE.md section 8.1, et il se resout en verifiant, pas en raisonnant.

### 16.5 Limite de couverture a retenir pour le dimensionnement

Le flux RSS d'une chaine ne renvoie que ses **quinze dernieres videos**. Il ne
permet donc aucune recherche retroactive : impossible d'y retrouver une
collaboration de 2023. Pour les cas anciens deja documentes — la Tomme de
Savoie d'Inoxtag avec le Cniel, la video Cniel de Squeezie — il faudra pointer
les identifiants de video directement. Le flux RSS est un outil de
**surveillance continue**, pas d'enquete sur le passe.

---

## 17. Journal de methode — 24 aout 2026, apres-midi : premier cas trouve par la chaine

### 17.1 L'observation de Vincent, transformee en mesure

Vincent, apres avoir ouvert a la main les videos du releve du matin :
« les collaborations commerciales sont visibles en description, je crois qu'il
n'y a pas besoin de regarder les videos ». Testee le jour meme par
`outils/extraire_descriptions_youtube.py`.

**L'observation est exacte, et elle a produit le premier cas reel du projet.**

MESURE — `recherche/descriptions_youtube_2026-08-24_1234.csv`, 32 videos :

| Chaine | Entite | Alias reconnu | Case YouTube | Segments SB |
|---|---|---|---|---|
| Inoxtag | **CNIEL** | `@lesproduitslaitiers` | **non cochee** | 1 |

Description : « Merci aux Produits Laitiers de nous avoir accompagnes sur ce
projet et cette degustation du plus grand plateau de fromage au monde ! »

C'est exactement le cas que le registre existe pour trouver : une
collaboration avec une interprofession laitiere, non declaree par la case
YouTube, reperee par le croisement des signaux. La chaine complete de la
METHODOLOGIE.md section 3 — ciblage, collecte, detection, resolution par la table d'alias — a
fonctionne de bout en bout, sans cle d'API et sans depenser un euro.

Reserve : **un cas n'est pas une mesure.** Cela prouve que la chaine peut
produire un vrai positif, pas qu'elle en produit beaucoup ni qu'elle n'en
manque pas.

### 17.2 Il y a un TROISIEME signal, et il change le comptage

La description contient parfois la mention legale ecrite en toutes lettres,
alors que la case YouTube n'est pas cochee. MESURE, meme fichier :

| | Videos |
|---|---|
| Mention « collaboration commerciale » ecrite en description | 5 |
| — dont case YouTube **non** cochee | **4** |
| Case YouTube cochee | 3 |

Autrement dit, la case YouTube manque la majorite des collaborations que le
createur declare pourtant lui-meme par ecrit. **Le signal presente en section
12 comme « le plus solide identifie a ce jour » sous-compte donc largement.**
Il reste le plus fiable quand il est present ; il n'est pas le plus complet.

Trois signaux independants sont desormais identifies sur YouTube :

1. la case de declaration YouTube (`paidContentOverlayRenderer`),
2. le segment sponsorise de SponsorBlock,
3. la mention legale ecrite dans la description.

Sur 32 videos, **15 portent au moins un des trois**.

Consequence pour la METHODOLOGIE.md section 8.3 : on dispose de trois methodes a apparier
pour la capture-recapture, pas deux.

### 17.3 Les sous-titres ne sont PAS accessibles simplement

Hypothese testee le meme jour : recuperer la transcription automatique pour
lire ce qui est dit pendant le segment SponsorBlock.

MESURE : sur les 32 videos, **32 annoncent des sous-titres** (piste `asr`
francaise presente dans la page). **Zero est telechargeable** par simple
requete HTTP. L'URL `youtube.com/api/timedtext?...` repond **HTTP 200 avec un
corps vide** : YouTube exige desormais un jeton de session que la page seule
ne fournit pas.

Statut : **hypothese refutee pour cette methode**, pas pour toutes. D'autres
voies existent (outils tiers type yt-dlp) et n'ont pas ete testees. A ne pas
reessayer par requete HTTP simple : c'est deja fait, ca ne marche pas.

Portee : la lecture du contenu parle reste hors d'atteinte pour l'instant. La
description est donc, a ce jour, **la seule source textuelle exploitable** sur
YouTube. C'est suffisant pour le cas ci-dessus, et insuffisant pour les
collaborations annoncees uniquement a l'oral.

### 17.4 Correction de perimetre, apportee par Vincent

Vincent a conteste la presence des interprofessions cerealieres
(Intercereales, FNPSMS) dans SA liste de taches, au motif qu'elles sont hors
sujet. **Il a raison sur la priorite.** L'idee de groupe temoin — verifier
qu'un detecteur ne se declenche pas sur n'importe quoi — reste methodo-
logiquement valable, mais elle n'a d'utilite qu'au moment de valider un
detecteur, ce qui n'arrivera pas avant plusieurs semaines. Elle ne justifiait
pas de lui faire collecter des donnees maintenant.

Ces entites restent dans la cartographie, marquees HORS PERIMETRE. Elles
sortent des taches humaines jusqu'a la phase de validation.

---

## 18. Journal de methode — 24 aout 2026, soir : l'arbitrage humain et les listes Instagram

### 18.1 Les 12 videos arbitrees : SponsorBlock a eu raison 12 fois sur 12

Vincent a examine les 12 videos d'Inoxtag portant un segment SponsorBlock sans
case YouTube cochee. Verdict, pour les douze : **vrai sponsor exterieur.**

Annonceurs identifies en description : air up, **Les Produits Laitiers
(CNIEL)**, Dyson, TentBox, Ultra Premium Direct, Rhinoshield, Deezer, Revolut
(x3), HelloFresh, Sport 2000.

**L'hypothese « les benevoles etiquettent de l'auto-promotion » est REFUTEE**
sur cet echantillon. Elle avait ete posee en section 16.4 comme l'explication
la plus probable de l'ecart entre Inoxtag et Squeezie. Elle etait fausse.

Consequence chiffree, sur les 15 dernieres videos d'Inoxtag :

| | Videos |
|---|---|
| Portant un sponsor exterieur reel | **14** |
| Declarees par la case YouTube | **2** |

**La case de declaration YouTube ne rattrape que 2 des 14 collaborations
reelles de cette chaine, soit environ 14 %.** C'est la premiere mesure de
rappel du projet, sur un echantillon d'une seule chaine.

Cela corrige definitivement la section 12, qui presentait ce signal comme « le
plus solide identifie a ce jour ». Il est le plus **fiable** quand il est
present. Il est, sur cette chaine, le moins **complet** des trois.

### 18.2 Le detecteur automatique a fait moins bien que la lecture humaine

Le script du matin n'a repere une formule commerciale que sur 8 des 12 videos
que Vincent a toutes identifiees a la main. Cause : la liste de formules
cherchait le vocabulaire de la conformite legale (« collaboration
commerciale », « en partenariat avec ») alors que le signal reel est
**commercial** : « avec le code INOXTAG », « mon lien », « -15 % sur tout le
site », lien d'affiliation vers un domaine de marque.

A retenir pour la detection : **le code promotionnel et le lien d'affiliation
sont de meilleurs indices que la mention legale.** Ils sont ecrits pour etre
utilises, donc ils sont toujours la ; la mention legale, elle, est optionnelle
dans les faits.

Non teste : la precision de cette regle elargie. Un lien d'affiliation peut
exister sans contrat de campagne.

### 18.3 Listes d'abonnements Instagram — premiere recolte

Vincent a releve a la main les comptes suivis par les comptes vitrines.
MESURE — `recherche/comptes_suivis_2026-08-24.csv`, plateforme **Instagram** :

| Entite | Compte vitrine | Comptes suivis |
|---|---|---|
| INTERBEV | `@la_viande_fr` | 209 |
| CNIEL | `@lesproduitslaitiers` | 150 |
| INAPORC | `@leporcfrancais` | 117 |
| ANVOL | `@volaillefrancaise` | 88 |
| CNPO | `@ouefsdefrance` | 0 (22 abonnes, ne suit personne) |
| CIFOG | aucun compte trouve | — |
| CLIPP | aucun compte trouve | — |

**538 comptes distincts. 25 sont suivis par au moins deux interprofessions.**
Ce recoupement est le meilleur point de depart connu pour la liste de
surveillance du mode B : ce sont les createurs que plusieurs commanditaires
de la filiere surveillent simultanement.

Trois pseudos passent du statut A VERIFIER a CONFIRME : `@leporcfrancais`
(INAPORC), `@volaillefrancaise` (ANVOL), `@ouefsdefrance` (CNPO — orthographe
a reverifier, un « e » semble inverse).

**Observation qui nuance la METHODOLOGIE.md section 8.** Les campagnes documentees par la
presse visaient des createurs gaming et humour. Les comptes suivis par les
vitrines Instagram sont massivement des createurs **cuisine et food** : Cyril
Lignac, Julien Duboue, Dorian Cuisine, Gueuleton, Marmiton, 750g, Papilles et
Pupilles. Les deux constats ne se contredisent pas — ils decrivent deux
canaux differents, gros budgets audiovisuels d'un cote, animation continue de
l'autre. Le registre doit couvrir les deux.

### 18.4 Un bug qui aurait fait perdre la moitie de la recolte

L'extracteur supposait que la liste Instagram alterne strictement pseudo puis
nom affiche. **Un seul compte sans nom affiche decale toute la suite** : le
premier essai n'a extrait que 56 comptes sur 150 pour le CNIEL, en en jetant
92 silencieusement.

Regle retenue : toute ligne ayant la forme d'un pseudo est un compte ; la
ligne suivante n'est son nom que si elle n'a PAS cette forme. Verification
ajoutee : comptes extraits + noms affiches doit egaler le nombre de lignes
collees. Pour le CNIEL, 150 + 145 = 295 = le collage exact.

A generaliser : **tout extracteur doit rendre compte de chaque ligne d'entree,
et le verifier par un total.** Un extracteur qui perd des donnees en silence
est plus dangereux qu'un extracteur qui plante.

### 18.5 Erreur de conception du classeur A_COMPLETER

Sur les 21 lignes du classeur, Vincent a repondu aux 12 qui portaient un lien
video. **Il n'a compris aucune des 9 autres** : « Je ne comprends pas ce que
tu attends de moi sur cette ligne. »

Cause : ces lignes etaient des intitules de taches qui n'avaient de sens que
pour quelqu'un ayant lu la conversation — meme faute que la colonne nommee
« TA REPONSE », que Vincent a renommee « Type de collaboration commerciale ».

Regle posee : **le classeur ne contient que des taches auto-portantes**, dont
l'enonce, le lien et le format de reponse suffisent sans aucun contexte
exterieur. Une tache qui demande une explication prealable reste dans la
conversation jusqu'a ce qu'elle soit expliquee.

---

## 19. Correction — 24 aout 2026 : ce qu'un abonnement ne prouve pas

### 19.1 Recadrage demande par Vincent

Objection de Vincent a la section 18.3 : **« ce n'est pas parce qu'un compte
est suivi par un lobby qu'il y a collaboration commerciale. »**

Elle est fondee. La section 18.3 presentait les listes d'abonnements comme un
constat sur qui les lobbies achetent. Ce n'est pas ce qu'elles sont.

**Ce qu'un abonnement est :** une hypothese de ciblage. Un signal emis par le
commanditaire sur qui l'interesse. Il reduit l'espace de recherche du mode B
(METHODOLOGIE.md section 12), rien de plus.

**Ce qu'un abonnement n'est pas :** une collaboration, ni un debut de preuve
de collaboration. Aucune ligne du registre ne pourra jamais s'appuyer sur un
abonnement. Le registre ne publie que des collaborations commerciales
remunerees, etablies sur une source primaire.

Regle : **les 538 comptes de `recherche/comptes_suivis_2026-08-24.csv` sont un
vivier de candidats a surveiller, jamais un resultat.**

### 19.2 Rappel de l'objectif, puisqu'il a fallu le rappeler

Le projet documente **des collaborations commerciales remunerees entre des
createurs de contenu a forte audience et l'industrie de la viande et du lait**,
pour servir le plaidoyer animaliste.

Precision apportee par Vincent le 24 aout, qui a une consequence operationnelle
directe : **un createur generaliste a plus de valeur pour le plaidoyer qu'un
createur culinaire.** Qu'un compte dont la cuisine est le sujet unique
travaille avec une interprofession de la viande n'etonne personne et ne
deplace rien. Qu'Inoxtag ou Mister V, sans aucun rapport avec les produits
animaux, soient remuneres par un lobby laitier est precisement ce qui rend le
mecanisme visible.

Ce n'est pas un critere d'inclusion — le registre reste factuel et n'exclut
personne. C'est un critere de **priorite de recherche**.

### 19.3 Ce que disent reellement les listes, entite par entite

L'erreur de la section 18.3 etait une generalisation : les quatre listes y
etaient decrites d'un bloc comme « massivement cuisine et food ». C'est faux
pour la principale. Verification faite, meme fichier :

| Compte vitrine | Profil dominant des comptes suivis |
|---|---|
| `@lesproduitslaitiers` (CNIEL) | **Createurs generalistes a forte audience**, plus des celebrites internationales |
| `@la_viande_fr` (INTERBEV) | Bouchers, chefs, medias culinaires, salons |
| `@leporcfrancais` (INAPORC) | Cuisine et charcuterie |
| `@volaillefrancaise` (ANVOL) | Cuisine et filiere avicole |

Grands createurs generalistes presents dans la liste du **CNIEL** :
Inoxtag, Squeezie, Valouzz, Michou, Kameto, Domingo, Norman, Zack Nani,
Freddy Gladieux, Grimkujow, LeBouseuh, Seb la Frite.
Dans celle d'INTERBEV : deux, dont Mister V.

**Les trois collaborations CNIEL deja documentees — Squeezie, Inoxtag,
Valouzz — figurent toutes les trois dans la liste d'abonnements du CNIEL.**
Trois sur trois. Ce n'est pas une preuve de collaboration pour les autres
comptes de la liste ; c'est une indication que ce vivier contient bien les
cas recherches, donc que le ciblage du mode B a du sens.

### 19.4 Consequences

1. Le CNIEL est confirme comme le bon sujet de la tranche verticale : c'est
   celui dont les cibles correspondent au profil qui interesse le plaidoyer.
2. La liste de surveillance prioritaire est celle du CNIEL, pas la reunion des
   quatre.
3. Le recoupement « suivi par plusieurs interprofessions » (25 comptes) est
   surtout un recoupement entre listes culinaires : interessant, mais de
   moindre priorite que les generalistes suivis par le seul CNIEL.

---

## 20. Journal de methode — 24 aout 2026, nuit : le contenu parle devient lisible

### 20.1 yt-dlp fonctionne, la piste refutee en 17.3 est rouverte

L'entree 17.3 concluait que les sous-titres n'etaient pas telechargeables. Ce
constat valait **pour la requete HTTP simple**, et il reste vrai pour elle.

Vincent a autorise l'ajout d'une dependance exterieure. `yt-dlp` (libre,
gratuit, version 2026.08.19) recupere sans difficulte les sous-titres
automatiques francais.

MESURE : sur la video `XgW3Nnskq8Q` (Inoxtag), 387 Ko de sous-titres, soit
**37 733 caracteres de transcription**, 2 609 blocs horodates.

**Le contenu parle d'une video YouTube est donc lisible par un programme,
gratuitement.** C'est le quatrieme signal du projet, et le seul qui atteigne
ce qui est dit plutot que ce qui est ecrit.

### 20.2 Une video peut porter PLUSIEURS collaborations, a des endroits differents

C'est le resultat le plus important de la soiree, et il invalide une hypothese
implicite du projet : « une video = un annonceur ».

La video `XgW3Nnskq8Q` en contient **trois**, chacune visible par un signal
different et un seul :

| Annonceur | Ou | Vu par |
|---|---|---|
| **Les Produits Laitiers (CNIEL)** | description, et a l'oral a 16m40 et 18m01 | description, transcription |
| Une marque de boisson en canette | segment SponsorBlock, 10m35 a 11m51 | SponsorBlock, transcription |
| « Odica », appareils auditifs | a l'oral a 31m51 | transcription seule |

**Le segment SponsorBlock n'etait PAS la collaboration CNIEL.** La chaine de
detection avait donc raison sur le resultat pour de mauvaises raisons : elle
avait signale la video grace a un segment qui concernait un tout autre
annonceur.

Vincent l'avait anticipe en annotant le classeur : « c'est difficile de
regarder toute la video pour m'assurer qu'il n'y a pas d'autre collaboration
commerciale ». Il avait raison.

Consequence pour le modele de donnees : **l'unite ne peut pas etre la video.**
Une video porte N collaborations, chacune avec son annonceur, sa position et
son signal d'origine. Cela alimente la question ouverte de la section 4 de
METHODOLOGIE.md — le post ou la campagne — en ajoutant un troisieme niveau :
le **segment**.

### 20.3 La transcription trouve le lobby, et le nomme

A 18m01, dans le contenu parle :

> « Lui c'est Xavier Turé à Cheese Guru, meilleur ouvrier de France fromager.
> Il a conçu le plus grand plateau de fromage du monde, mais **il est aussi
> ambassadeur dans le monde pour les produits laitiers.** »

Et a 16m40 : « on n'oublie pas le beurre dans les produits laitiers ».

La transcription mentionne aussi la **tomme de savoie**, qui est precisement
l'objet de la collaboration Inoxtag x Cniel deja documentee par la presse.

La table d'alias fonctionne donc **aussi sur le contenu parle**, sans
adaptation. C'est le meme mecanisme que sur la description.

### 20.4 Et elle produit un faux positif immediat — la demonstration la plus utile

A 31m51, la transcription dit textuellement :

> « La vidéo, elle est sponsorisée par Odica. — Ah ouais, appareil auditif.
> — La sponso, tu as pris 200k pour les appareils auditifs. »

**C'est une blague.** Les deux createurs plaisantent sur un appareil auditif
apres un gag sonore. Il n'y a aucune collaboration avec « Odica ».

Un motif automatique sur « sponsorisee par X » aurait enregistre un annonceur
inexistant, avec une citation textuelle a l'appui — un faux positif
parfaitement credible et parfaitement faux.

**C'est la demonstration la plus concrete obtenue a ce jour de la necessite de
la verification humaine** (METHODOLOGIE.md section 3, etape 5). Elle n'est pas
une precaution de principe : sur la premiere video ou l'on applique la
transcription, elle attrape deja une erreur.

Cela tranche aussi le debat sur la methode de detection : un motif regulier ne
peut pas distinguer une blague d'un contrat. Un lecteur qui comprend le
contexte le peut. La transcription se lit, elle ne se filtre pas.

### 20.5 Le projet est sur GitHub

Depot prive `Tamateatea/influenceurs-lobbies-viande-lait`, branche `main`,
29 fichiers, 4 enregistrements.

Les trois enregistrements de la premiere session portaient une adresse
universitaire qui n'est plus active. Ils ont ete reecrits avant tout envoi.
`SECRETS.txt` est exclu par `.gitignore` — verifie apres envoi : absent du
depot.

---

## 21. Journal de methode — 24 aout 2026 : la surveillance elargie, et un faux negatif total evite de justesse

### 21.1 Ce qui a ete lance

Premier essai d'elargissement, de 2 chaines a 13 createurs generalistes tires
de la liste d'abonnements du CNIEL. Outil consolide :
`outils/surveiller_youtube.py`, qui absorbe les deux scripts precedents et
porte les quatre signaux.

MESURE — `recherche/surveillance_youtube_2026-08-24_1639.csv`, **174 videos,
13 chaines** :

| Signal | Videos | Part |
|---|---|---|
| 1. Case de declaration YouTube | 23 | 13 % |
| 2. Segment SponsorBlock | 19 | 11 % |
| 3. Indice commercial en description | 42 | 24 % |
| **Au moins un signal** | **49** | **28 %** |

**Entites de la filiere viande/lait trouvees : aucune.** C'est une mesure, pas
un echec — mais voir 21.3, qui l'explique en partie.

### 21.2 Un createur n'a pas une chaine, il en a plusieurs

Decouvert en verifiant pourquoi les identifiants de chaine du matin ne
correspondaient pas a ceux de l'apres-midi. Aucun des deux n'etait faux :
c'etaient **des chaines differentes du meme createur**.

| Nom demande | Resolution par pseudo | Resolution par recherche |
|---|---|---|
| Inoxtag | « Inoxtag 2.0 » (secondaire) | « Inoxtag » (principale) |
| Squeezie | « SQUEEZIE GAMING » (secondaire) | « SQUEEZIE » (principale) |

**Et la chaine secondaire est bien plus sponsorisee que la principale :**

| Chaine | Videos avec segment SponsorBlock |
|---|---|
| Inoxtag 2.0 (secondaire) | **14 / 15** |
| Inoxtag (principale) | 4 / 15 |

**La collaboration Inoxtag x CNIEL trouvee le matin etait sur la chaine
secondaire.** Une surveillance limitee aux chaines principales l'aurait
manquee — et le rapport aurait dit « aucune entite trouvee » avec assurance.

Consequence, inscrite dans l'outil : **on surveille toutes les chaines
officielles d'un createur, pas la principale.** Hypothese ouverte, non
mesuree : les chaines secondaires sont moins regardees par les journalistes et
pourraient concentrer les collaborations les moins visibles.

### 21.3 Le filtre du badge de verification

Une recherche « Squeezie » remonte 17 chaines, dont la plupart sont des
reuploads de fans. Les inclure aurait attribue a un createur des videos qu'il
n'a pas publiees — une erreur qui, dans un registre nominatif, est
disqualifiante.

Le **badge de verification** separe proprement les chaines officielles des
autres. Retenu comme filtre. 13 createurs donnent 24 chaines officielles.

Deux createurs ne remontent aucune chaine verifiee sous ce nom : **Seb la
Frite** et **Zack Nani**. A resoudre, ce ne sont pas des absences reelles.

### 21.4 HTTP 429 — le faux negatif que le rapport allait annoncer

Le releve elargi a 288 videos a rendu, dans son rapport :

> Case de declaration : **0 video (0 %)**
> Indice commercial en description : **0 video (0 %)**
> Entites de la filiere : **aucune**

**Tout etait faux.** YouTube avait repondu **HTTP 429 (« Too Many Requests »)**
aux 288 telechargements de pages — consequence de deux releves lances coup sur
coup. Le script comptait une page non telechargee comme une video sans signal.
Seul SponsorBlock, servi par un autre serveur, avait repondu.

Rien dans le rapport ne le signalait. Il annoncait « aucune entite trouvee »
sur un echantillon ou **rien n'avait ete lu**.

C'est le pire type d'erreur possible pour ce projet : un **faux negatif
silencieux et credible**. Il ne se manifeste par aucun plantage, aucun message,
aucune anomalie visible. Un registre qui affirme « ce createur n'a pas de
collaboration » sur cette base est pire qu'inutile — il blanchit.

Il n'a ete repere que parce que deux signaux tombaient a zero *exactement*, ce
qui etait incompatible avec le releve d'une heure plus tot.

**Corrections apportees le jour meme :**

1. `get()` renvoie desormais **(contenu, erreur)**. Une chaine vide n'est plus
   jamais silencieuse.
2. Pause de 0,35 s entre appels, 3 fils au lieu de 8, et reessai avec attente
   croissante sur 429.
3. **Le script s'arrete et ne produit aucun rapport si plus de 10 % des pages
   manquent.** Verifie : sur un essai a 48 videos encore limite, il refuse de
   conclure au lieu d'annoncer « aucun signal ».
4. Le releve fautif `surveillance_youtube_2026-08-24_1642.md` porte un
   avertissement en tete et ne doit pas etre cite.

**Regle generale, a ajouter a METHODOLOGIE 13.3 :** un extracteur ne doit pas
seulement rendre compte de ses lignes d'entree — il doit **distinguer
l'absence de resultat de l'absence de mesure**, et refuser de conclure quand
il n'a pas pu lire. « Je n'ai rien trouve » et « je n'ai pas regarde » ne
doivent jamais produire la meme sortie.

### 21.5 Le detecteur elargi, mesure

L'hypothese YT-14 disait que le code promo et le lien d'affilie valent mieux
que la mention legale. Mesure sur les 174 videos valides :

| Famille d'indices | Videos | Part |
|---|---|---|
| remerciement | 27 | 16 % |
| mention legale | 18 | 10 % |
| lien affilie | 18 | 10 % |
| code promo | 11 | 6 % |

L'elargissement double bien la couverture : 42 videos portent un indice
commercial contre 18 pour la seule mention legale.

**Mais la famille « remerciement » est imprecise** : sur 14 videos, elle se
declenche seule, et les exemples melangent de vrais annonceurs (« merci a
NordVPN », « merci a happn ») et de simples remerciements entre createurs
(« merci a Doigby »). A conserver comme indice faible, jamais comme preuve.

Statut de YT-14 : **confirmee pour le gain de rappel, avec une reserve de
precision documentee.**

---

## 22. Journal de methode — 24 aout 2026 : le robots.txt de YouTube, et une question de conformite

### 22.1 Ce qui a ete verifie

Question de Vincent apres l'erreur HTTP 429 : « ca veut dire que YouTube
empeche des outils automatiques de faire ce qu'on essaie de faire ? »

Le 429 lui-meme est une **limitation de debit**, pas une interdiction. Mais la
question a conduit a lire le `robots.txt` de YouTube, ce qui n'avait jamais
ete fait. MESURE, lecture directe de `https://www.youtube.com/robots.txt` :

```
User-agent: *
Disallow: /feeds/videos.xml
Disallow: /results
Disallow: /api/
Disallow: /youtubei/
Disallow: /timedtext_video
...
```

**Deux des techniques centrales du projet sont sur la liste des chemins
interdits aux robots :**

| Technique | Chemin | Statut robots.txt |
|---|---|---|
| Flux RSS de chaine | `/feeds/videos.xml` | **Disallow** |
| Resolution de chaine par recherche | `/results` | **Disallow** |
| Lecture de la page video | `/watch` | autorise |
| Sous-titres via yt-dlp | `/api/timedtext` | **Disallow** |

La lecture des pages `/watch` — d'ou viennent la declaration et la description,
donc le premier cas trouve — n'est pas concernee.

### 22.2 Pourquoi ca compte pour ce projet en particulier

`robots.txt` n'est pas un contrat, et son non-respect n'est pas en soi une
infraction en droit francais. Mais c'est la declaration lisible par machine de
ce que l'exploitant autorise aux programmes, et les CGU de YouTube restreignent
par ailleurs l'acces automatise hors API.

Or la valeur de ce registre repose **entierement sur sa credibilite**
(METHODOLOGIE.md section 6). Un registre nominatif construit sur des techniques
que la plateforme declare interdire offre a toute partie attaquee un argument
qui n'a rien a voir avec le fond : « ces donnees ont ete collectees en
violation des regles du site ». C'est exactement le type de contre-attaque que
le projet ne peut pas se permettre.

**Ce n'est pas une question technique, c'est une question de posture, et elle
revient a Vincent.**

### 22.3 L'alternative existe et rentre dans le budget

RAPPORTE, a verifier : l'**API YouTube Data v3** offre un quota gratuit
(de l'ordre de 10 000 unites par jour) et couvre precisement les deux usages
problematiques — rechercher une chaine, et lister les videos d'une chaine.
Elle demande une cle, gratuite, sans moyen de paiement.

Cela ne contredit pas la contrainte « budget zero euro » : une cle gratuite
n'est pas un abonnement. Cela contredit en revanche le confort du « sans cle »
qui avait guide les premiers choix — un confort, pas un principe.

Ce que l'API ne couvre pas : la case de declaration
(`paidContentOverlayRenderer`), qui n'existe que dans la page `/watch`, elle
autorisee. Et SponsorBlock est un service tiers, sans rapport avec YouTube.

**Decision a prendre par Vincent, non tranchee a ce jour.** Trois options :
migrer vers l'API pour les deux usages concernes ; rester en l'etat en
l'assumant ; ou un intermediaire. Aucune n'est engagee.

---

## 23. Arbitrage de Vincent — 24 aout 2026 : robots.txt, et la superposition des couches

### 23.1 La regle, telle que Vincent la formule

Objection posee en 22.2 : construire le registre sur des chemins que le
`robots.txt` de YouTube declare interdits offrirait un argument de procedure
a toute partie mise en cause.

Reponse de Vincent, qui tranche : **« si on peut faire techniquement quelque
chose sans enfreindre la loi, on peut le faire ».**

C'est sa decision et elle est fondee : un `robots.txt` est une preference
d'exploitant, pas une norme juridique. Le contourner n'est pas une infraction
en droit francais.

**Ce qui reste ferme, et n'a pas change :** ne franchir aucune
authentification, ne contourner aucun paywall, ne lire que du contenu
publiquement accessible. C'est cette limite-la qui protege le projet, pas le
`robots.txt`.

### 23.2 Et la bonne reponse a l'objection : superposer, pas choisir

Deuxieme remarque de Vincent, et elle vaut mieux que ma recommandation :
**« ne peut-on pas avoir plusieurs couches ? plusieurs outils en meme temps ? »**

Oui. C'est meme le principe deja pose en METHODOLOGIE.md section 10 — plusieurs
hypotheses, toutes testees, on garde tout ce qui apporte — et je ne l'avais pas
applique a cette question. J'avais presente une alternative la ou il fallait
une addition.

Superposer l'API officielle et la lecture directe apporte trois choses :

1. **Redondance.** Si une voie casse — changement d'interface, limitation de
   debit, quota epuise — l'autre continue.
2. **Deux methodes independantes**, donc un couple utilisable pour
   l'estimation par capture-recapture de METHODOLOGIE.md section 9.3.
3. **Le choix de la posture reste ouvert.** Si le projet doit un jour ne
   dependre que de sources sanctionnees, la couche existe deja et il suffit
   d'eteindre l'autre.

Reformulation retenue : l'API YouTube Data v3 devient une **couche
supplementaire a construire**, pas un remplacement. La decision de posture
n'a plus a etre prise aujourd'hui, ce qui est preferable : on la prendra avec
des mesures des deux voies plutot que sur une intuition.

---

## 24. Journal de methode — 24 aout 2026, soiree : une nouvelle source, et elle est primaire

*Travail mene en autonomie pendant l'absence de Vincent, sur sa demande.*

### 24.1 Renverser le sens de la recherche

Toutes les methodes du projet partaient jusqu'ici du **contenu du createur**,
pour y reconnaitre un annonceur. Hypothese nouvelle, formulee et testee le
meme soir : **partir du site du commanditaire et y chercher des createurs.**

Interet immediat : ce sont des **sources primaires**. Un lobby qui ecrit
lui-meme « recette par @X » etablit la relation bien mieux qu'une inference
sur une description de video. Ces sites sont publics, sans authentification,
et exposent des plans de site complets.

Outil : `outils/fouiller_sites_lobbies.py`. Il lit les plans de site des
interprofessions, telecharge les pages, et y cherche deux choses independantes :
le vocabulaire de l'influence, et **tout pseudo publie**.

La deuxieme est la bonne. Chercher des createurs *deja connus* ne fait que
confirmer ce qu'on sait ; **recolter tous les pseudos publies trouve des
createurs qu'on ignorait.**

### 24.2 Resultat : 26 pseudos, publies par les lobbies eux-memes

MESURE — `recherche/sites_lobbies_2026-08-24_1719.csv`, 360 pages lues sur
trois sites.

**INAPORC (leporc.com) a une rubrique dediee : « Les recettes des
influenceurs ».** Elle nomme ses partenaires et publie leurs recettes :

| Pseudo ou nom | Pages |
|---|---|
| @pepites2noisette | 41 |
| @chateau.leg0 | 33 |
| @olivier.moulin | 31 |
| @juliamaufay | 24 |
| @mummyfast | 17 |
| @julienduboue | 12 |
| @menthe_banane, @sophiecuisine | 8 |
| @woodmoodfood, @florianonair, @agatheduchesne_ | 2 |
| **Mercotte**, Dorian, Audrey | pages nominatives |

CNIEL (produits-laitiers.com) : @minireyve, @lesprolaitiers, @agriskippy,
@onestpret, @valentinwerther — ces trois derniers etant des **eleveurs**
presentes comme « eleveurs connectes », pas des createurs remuneres.

**Reserve ferme : un credit de recette n'est pas une preuve de remuneration.**
Il etablit une relation de travail documentee, pas son caractere onereux.
C'est un candidat solide, pas une entree de registre.

### 24.3 Le cas le plus important : INAPORC x Twitch x LeBouseuh

Page `leporc.com/le-porc-en-france/le-metier-d-eleveur-de-porcs-mis-en-lumiere-sur-twitch`,
ecrite par INAPORC. Citations exactes :

> « Lors d'un premier live, **@Gastronogeek**, auteur culinaire et candidat Top
> Chef, a accueilli Sophie, eleveuse de porcs en Bretagne [...] Le "live" a
> dure pres de deux heures et a fait l'objet d'un "best of" sur les chaines
> youtube et Twitch de @Gastronogeek. **Chaine Youtube de webedia** pour le
> live cuisine »

> « Pour le deuxieme live, **@Lebouseuh, youtuber breton**, a accueilli Hugo,
> futur eleveur en Normandie autour d'un defi en live gaming autour de la
> creation d'un elevage de porcs sur MineCraft »

Cible declaree : « les jeunes de 18 a 30 ans ».

**Trois enseignements, chacun important :**

1. **LeBouseuh est exactement le profil vise par le plaidoyer** : un youtubeur
   gaming generaliste, sans rapport avec l'alimentation, remunere par une
   interprofession de la viande. Et il figurait deja dans la liste
   d'abonnements du CNIEL relevee par Vincent.
2. **L'hypothese YT-16 est confirmee par un cas reel.** Elle disait que les
   sponsorings Twitch pouvaient ressortir via les extraits reuploades sur
   YouTube. Le lobby ecrit lui-meme que les lives ont fait l'objet d'un
   « best of » sur les chaines YouTube des deux createurs. **Twitch n'est donc
   pas hors de portee : il transite par YouTube.**
3. **Webedia est identifie comme producteur** de l'operation. C'est une agence
   a ajouter a la feuille Agences du classeur, avec une source primaire — ce
   qui manquait (voir TODO, « Completer la feuille Agences »).

### 24.4 Ce que cette source ne fera pas

Le resultat est excellent pour INAPORC et faible pour le CNIEL et INTERBEV.
Ce n'est probablement pas un hasard : plus une interprofession assume ses
partenariats, plus elle les publie. Celles qui brouillent le donneur d'ordre —
le cas d'INTERBEV decrit en METHODOLOGIE.md section 2 — n'auront rien a
recolter ici.

**Cette source ne remplace donc rien.** Elle s'ajoute, et elle a l'avantage
d'etre la seule dont les resultats sont des declarations du commanditaire
plutot que des inferences. C'est aussi un bon candidat pour l'estimation par
capture-recapture (METHODOLOGIE.md section 9.3) : elle est totalement
independante des signaux YouTube.

### 24.5 Faux positif corrige

Les reglements de jeu-concours listent des domaines de courriel jetables
(`@jetable.com`, `@yopmail.com`, `@spambox.us`). Le motif les prenait pour des
pseudos. Filtre ajoute sur les extensions de domaine.

---

## 25. Journal de methode — 24 aout 2026 : TikTok, la source la plus prometteuse du projet

*Travail mene en autonomie pendant l'absence de Vincent, sur sa demande.*

### 25.1 L'interface web publique est un cul-de-sac

`library.tiktok.com` repond, mais ne sert qu'une coquille JavaScript de 38 Ko :
aucun chemin d'API dans le HTML. Douze chemins candidats ont ete essayes
(`/api/v1/ad/query`, `/api/v1/search/ad`, `/api/v1/commercial_content/query`...) :
tous en 404, sauf un qui renvoie du HTML.

**Hypothese TT-04 refutee. Ne pas y revenir par ce chemin.**

### 25.2 L'API officielle est exactement ce qu'il nous faut

Point d'acces :
`https://open.tiktokapis.com/v2/research/adlib/commercial_content/query/`

Verifie : il repond une erreur JSON structuree (`code 40006, no schema found`)
et non un 404 — **l'endpoint existe et repond**, il attend une authentification.

Ce qu'il rend, d'apres la documentation officielle :

| Champ | Contenu |
|---|---|
| `creator.username` | le createur |
| `brand_names` | **la ou les marques qui le remunerent** |
| `label` | le label de partenariat |
| `create_date` | la date |
| `videos` | les URL |

**C'est le modele de donnees du registre, deja constitue, et declare par la
plateforme elle-meme.** Pas d'inference, pas de table d'alias a appliquer sur
du texte libre, pas de faux positif de type blague sur un sponsor (JOURNAL
20.4).

Filtres : `content_published_date_range` (depuis le 1er octobre 2022),
`creator_country_code`, `creator_usernames`. Perimetre EEE : la France est
couverte, le Royaume-Uni et la Suisse sont exclus.

Il n'y a **pas de filtre par marque**. La bonne strategie est donc de
recuperer tout le contenu commercial francais de la periode et de filtrer sur
`brand_names` chez nous, contre la table d'alias. C'est meme preferable : on
ne depend pas de la facon dont TikTok orthographie « Cniel ».

### 25.3 Et l'acces n'exige PAS d'affiliation universitaire

C'est le point decisif, et il corrige un decouragement premature.

TikTok a **deux** programmes distincts, qu'on confondait :

| Programme | Public vise | Notre situation |
|---|---|---|
| **Research API** | chercheurs academiques, a but non lucratif | hors de portee, affiliation UCD morte |
| **Commercial Content API** | RAPPORTE : « le public et les chercheurs », journalistes et associations compris | **accessible** |

Delai annonce : environ 2 jours ouvres. Gratuit. Candidature sur
`developers.tiktok.com/application/commercial-content-api` — page verifiee,
elle existe et demande une connexion. Contact :
`commercial-research-questions@tiktok.com`.

**C'est la meilleure nouvelle du projet depuis le premier cas trouve.** La
Meta Content Library etait perdue faute d'affiliation ; l'equivalent TikTok ne
la demande pas, et son perimetre — contenus organiques a label de partenariat,
avec la marque ET le createur — est meilleur que ce qu'on esperait de Meta.

Outil ecrit et pret : `outils/tester_tiktok_commercial.py`. Il attend
`TIKTOK_CLIENT_KEY` et `TIKTOK_CLIENT_SECRET` dans SECRETS.txt.

### 25.4 Ce qui reste incertain

`SUPPOSE` : que la candidature soit acceptee pour un projet de plaidoyer
associatif. La documentation dit « public et chercheurs », mais l'examen est
discretionnaire. Le formulaire demande de decrire le projet — c'est la que
Vincent devra soigner sa formulation : recherche d'interet public sur la
transparence de la communication commerciale, ce qui est exactement vrai.

---

## 26. Journal de methode — 24 aout 2026 : une erreur d'appariement, et ce qu'elle enseigne

Tentative de retrouver les « best of » des lives INAPORC sur les chaines de
LeBouseuh et Gastronogeek (cas documente en 24.3).

La recherche YouTube a remonte une video `40JkqP1gYqA` intitulee « 24H A LA
FERME ! » attribuee a LeBouseuh. Verification faite avant d'aller plus loin :
**c'est en realite « Lebouseuh est un gros porc ! » de la chaine « Yuki
Shorts »**, une chaine de fan sans rapport.

Cause : une seule expression reguliere cherchant `videoId`, `title` et
`ownerText` **a travers** un gros bloc JSON apparie des champs qui
n'appartiennent pas au meme objet.

C'est la troisieme fois de la journee que ce type d'erreur apparait :
resolution de chaine par frequence (JOURNAL 16.2), alternance des listes
d'abonnements (JOURNAL 18.4), et maintenant l'appariement de resultats de
recherche.

**Regle a appliquer partout : ne jamais extraire plusieurs champs d'un meme
objet avec une expression reguliere qui traverse le document.** Decouper
d'abord en blocs par objet, extraire ensuite dans chaque bloc. C'est ce que
fait `resoudre_chaines()` depuis sa correction — l'outil de production est
donc sain ; c'est la verification improvisee qui ne l'etait pas.

Consequence pratique : les best-of des lives INAPORC restent **a retrouver**.
Ils sont dates de la campagne Twitch et ne figurent donc plus dans les flux
RSS, limites aux 15 dernieres videos (YT-03). Il faudra passer par la
recherche, avec un decoupage par bloc, ou par l'API YouTube Data.

---

## 27. Journal de methode — 24 aout 2026 : 92 recettes creditees, et une erreur de conception que Vincent a relevee

### 27.1 L'erreur : avoir donne l'URL la moins informative

Le premier classeur d'arbitrage donnait, pour chaque pseudo, « l'URL la plus
courte ou il apparait », en supposant que la plus courte serait la plus
canonique. **C'est l'inverse.**

Un pseudo present sur 41 pages l'est parce qu'il figure dans un encart
« recette du moment » repris dans toute la navigation du site. L'URL la plus
courte est donc la page d'accueil, `/contact` ou `/faq` — precisement les
pages qui ne montrent pas la relation.

Vincent : « Je ne vois pas le lien avec les influenceurs pour la plupart. »
Il avait raison, et il ne pouvait pas conclure autrement.

**Regle : la preuve jointe a un candidat doit etre la page qui MONTRE la
relation, pas n'importe quelle page ou la chaine apparait.** Choisir l'URL la
plus specifique — celle dont l'adresse ou le titre porte le nom du createur —
et non la plus courte.

### 27.2 Sa deuxieme question etait la meilleure : « pourquoi avais-tu besoin de moi ? »

Reponse honnete : pour l'essentiel, je n'en avais pas besoin. Ces pages sont
publiques et lisibles par le script. J'ai demande un arbitrage humain sur un
travail que je pouvais faire moi-meme, et je l'ai demande sans avoir regarde
les pages.

**Regle : ne demander a Vincent que ce qui exige reellement son jugement.**
L'identification se fait par lecture — c'est mon travail. Ce qui lui revient,
c'est la **priorite** : quels cas valent d'etre poursuivis pour le plaidoyer.
C'est un jugement editorial que je ne peux pas rendre a sa place.

### 27.3 Ce que la lecture a donne : bien plus qu'un credit isole

MESURE, en lisant le plan de site d'INAPORC — 521 pages de recettes :

| Createur | Recettes creditees a son nom |
|---|---|
| @pepites2noisette | **32** |
| @olivier.moulin | **19** |
| @juliamaufay | 13 |
| @mummyfast | 12 |
| @menthe_banane | 5 |
| @sophiecuisine | 4 |
| @julienduboue, @woodmoodfood | 3 |
| @florianonair | 1 |

**Au moins 92 recettes** portent le nom d'un createur dans leur adresse et
dans leur titre. Ce n'est pas un credit ponctuel : c'est un **programme
editorial suivi**.

Et INAPORC publie une **notice biographique** pour chacun sur sa page « Dans
la cuisine des influenceurs » — dont **Mercotte**, jury du Meilleur Patissier
sur M6, Agathe Duchesne, Dorian et Audrey, qui n'apparaissaient pas dans la
recolte de pseudos faute d'arobase.

### 27.4 Tri des faux positifs, fait par lecture

- `@onestpret` n'est pas une personne : c'est le hashtag de la campagne climat
  **#OnEstPrets**. Faux positif.
- `@agriskippy` (Antoine Thibault) et `@valentinwerther` sont des **eleveurs**
  cites dans un article editorial du CNIEL sur les « eleveurs connectes ».
  Aucun partenariat commercial n'y est decrit.
- `@interbev_fr` et `@laviandetv` sont les comptes d'INTERBEV lui-meme.

Restent trois pseudos **non verifies** : `@minireyve`, `@lesprolaitiers`,
`@lamourboeuf`.

### 27.5 Ce que ca dit du perimetre

Les partenaires d'INAPORC identifies ici sont, a deux exceptions pres, des
createurs **culinaires**. Les deux exceptions sont precisement celles qui
interessent le plaidoyer : **@gastronogeek** et **@lebouseuh**, generalistes,
sur l'operation Twitch.

Cela confirme la lecture de METHODOLOGIE.md section 1 : le registre inclut
tout le monde, mais la priorite de recherche va aux generalistes.

---

## 28. Journal de methode — 24 aout 2026 : la limitation YouTube est cumulative, pas instantanee

### 28.1 Trois tentatives, un resultat contre-intuitif

MESURE, trois lancements de `outils/surveiller_youtube.py` dans la soiree :

| Videos | Pause | Fils | Pages refusees | Part |
|---|---|---|---|---|
| 288 | 0,35 s | 8 | 288 | **100 %** |
| 300 | 0,35 s | 3 | 37 | 12 % |
| 240 | **1,2 s** | **2** | 85 | **35 %** |

**Ralentir a aggrave le taux d'echec.** Trois fois moins de debit, trois fois
plus de refus en proportion.

### 28.2 Ce que ca signifie

L'hypothese implicite etait que YouTube limite un **debit** — trop de requetes
par seconde. Elle est fausse, ou du moins insuffisante.

Le comportement observe correspond a un **budget cumule sur la journee**,
attache a l'adresse IP. Chaque lancement successif part d'un budget deja
entame par le precedent ; ralentir n'y change rien, puisque ce n'est pas la
vitesse qui est comptee mais le nombre.

Consequence pratique immediate : **le quota YouTube de la journee est epuise.**
La mesure elargie attendra. Inutile de reessayer aujourd'hui, quels que soient
les reglages — c'est mesure, pas suppose.

### 28.3 Et ca tranche la question de l'API officielle, par la mesure

Vincent avait tranche le 24/08 que ce qui est techniquement possible sans
enfreindre la loi est permis, et propose de superposer plusieurs couches
plutot que de choisir (JOURNAL 23). Il avait raison sur le principe. On a
maintenant l'argument chiffre.

La lecture directe des pages a une limite **non documentee, non annoncee, et
qui se degrade sans prevenir**. On ne peut pas planifier une surveillance
continue dessus : impossible de savoir combien de videos on peut examiner
avant d'etre coupe, ni quand le budget se reconstitue.

L'API YouTube Data v3 a, elle, un quota **documente et compte** — de l'ordre
de 10 000 unites par jour, RAPPORTE, a verifier. On sait a l'avance ce qu'on
peut faire.

**Ce n'est plus une question de posture, c'est une question d'exploitabilite.**
Un outil de surveillance continue a besoin d'une limite connue. La couche API
devient donc necessaire pour deux des quatre signaux — la liste des videos
d'une chaine et la resolution des chaines — pendant que la lecture directe
reste indispensable pour la case de declaration, absente de l'API.

Cout : une cle gratuite. Ne contredit pas la contrainte de budget zero.

### 28.4 Limite de resolution a retenir

La recherche par nom, filtree sur le badge de verification, ecarte bien les
chaines de fans mais **pas les homonymes reels** : « Norman » remonte aussi
Norman Greenbaum, musicien americain ; « Domingo » remonte Domingo Legal et
Domingo Gomes.

Sans effet sur la mesure — ces chaines ne porteront aucun signal viande/lait —
mais **ne jamais attribuer automatiquement une collaboration a un nom sans
verifier de quelle personne il s'agit.** Le registre est nominatif : une
confusion d'homonyme y serait disqualifiante.

Ces chaines gonflent aussi le volume, donc consomment le budget quotidien pour
rien. A filtrer.

---

## 29. Journal de methode — 24 aout 2026 : Vincent corrige trois de mes erreurs

Arbitrage des 24 pseudos, avec verification des comptes Instagram et de leur
nombre d'abonnes — un travail que je ne peux pas faire, la navigation sociale
etant derriere une authentification.

### 29.1 Trois erreurs de ma part

**`@onestpret` n'est pas un hashtag.** J'avais ecrit « pas une personne :
hashtag de la campagne climat #OnEstPrets. Faux positif. » C'est un **compte
reel, 194 000 abonnes**, mouvement de mobilisation pour le climat. Vincent :
« ce serait incroyable qu'il collabore avec un lobby laitier ». En effet — et
c'est desormais une piste, pas un faux positif.

**`@lesprolaitiers` existe, mais sur Twitter.** Vincent l'a cherche sur
Instagram, ne l'a pas trouve, et a conclu qu'il n'existait pas. Verification :
la page du CNIEL ecrit « leur compte **Twitter** @LesProLaitiers ». Le pseudo
est reel ; c'est ma recolte qui ne retenait pas la plateforme.

**`@interbev_fr` et `@laviandetv` n'existent pas sur Instagram** non plus : la
page « nous suivre » liste des comptes de plusieurs plateformes.

**Cause commune : un pseudo sans sa plateforme est ininterpretable.** Corrige
dans `fouiller_sites_lobbies.py`, qui capture desormais la plateforme nommee
au voisinage du pseudo. C'est aussi ce constat qui a fait poser l'unite de
collecte (METHODOLOGIE section 8).

### 29.2 Ce que son arbitrage a apporte

Il a releve les nombres d'abonnes, ce qui manquait completement : le projet
n'avait aucune mesure d'audience alors que c'est son critere de priorite.

Priorite haute retenue : **@lebouseuh (2,4 M)**, @lacuisinedemercotte (580 k),
@gastronogeek (364 k), @florianonair (231 k), @menthe_banane (208 k),
@onestpret (194 k), @minireyve (193 k), @mummyfast (83 k), @chateau.leg0
(80 k), @juliamaufay.

Ecartes : @agriskippy (agriculteur), @valentinwerther, @woodmoodfood, Dorian
et Audrey (introuvables sur Instagram), @interbev_fr, @laviandetv.

**Un raisonnement a garder :** il classe @menthe_banane en priorite haute bien
qu'il soit dieteticien, « car du point de vue du plaidoyer, un dieteticien n'a
pas le meme statut » — l'autorite sanitaire pretee a la profession change la
portee du message. La congruence seule ne capture pas ce critere ; il meritera
un champ ou une note.

### 29.3 Defaut d'ergonomie a corriger

Excel refuse une saisie commencant par `@` : il la prend pour une formule.
Vincent n'a pas pu entrer `@lacuisinedemercotte`. **Les colonnes destinees a
des pseudos doivent etre formatees en texte a la generation.**

---

## 30. Journal de methode — 24 aout 2026 : le registre des comptes, enfin consolide

### 30.1 Le probleme, souleve par Vincent

« Je crains que tu ne fasses pas ce travail de consolidation et qu'on se
retrouve avec des dizaines de fichiers avec des informations utiles qui
devraient etre consolidees dans un seul. »

Il avait raison, et le reproche etait deja dans le TODO de la premiere
session : « sans identifiant stable, impossible de joindre les sources entre
elles ». Cinq fichiers contenaient les memes comptes sans jamais se parler.

### 30.2 Ce qui a ete construit

`outils/consolider_comptes.py` lit les cinq sources et produit **un fichier
unique**, `cartographie/COMPTES.xlsx`, plus un CSV horodate dans `recherche/`.

Cle d'un compte : **le couple (plateforme, identifiant)**, jamais le nom
(METHODOLOGIE section 8).

MESURE, premier passage :

| Source | Lignes lues |
|---|---|
| Abonnements Instagram des vitrines | 564 |
| Pseudos publies par les sites des lobbies | 194 |
| Chaines YouTube surveillees | 24 |
| Jugements de Vincent | 22 |
| Feuille Alias | 4 |

**605 comptes distincts** : 552 Instagram, 24 YouTube, 29 de plateforme
indeterminee.

**11 comptes sont attestes par au moins deux methodes independantes** —
@gastronogeek, @chateau.leg0, @juliamaufay, @florianonair, @julienduboue,
@pepites2noisette... A la fois suivis par une vitrine ET publies sur le site
du lobby. C'est le premier recoupement multi-sources du projet, et c'est
exactement le materiau de la capture-recapture (section 9.3).

Le script parse aussi les nombres d'abonnes releves par Vincent dans ses
commentaires libres (« ~25k followers », « 2,4M followers! ») : c'est
aujourd'hui **la seule mesure d'audience du projet**.

### 30.3 Le trou que la consolidation rend visible

**Seuls 3 % des comptes ont une audience connue** — 16 sur 605, tous releves
a la main par Vincent.

Or l'audience est le critere de priorite declare du projet : « les createurs
les plus vus du public » (METHODOLOGIE section 8). On priorise donc
aujourd'hui sur une mesure qu'on n'a presque pas.

C'est le meilleur argument pour la cle API YouTube : `channels.list` renvoie
le nombre d'abonnes, ce qui comblerait immediatement les 24 chaines et toutes
celles a venir. Pour Instagram, la mesure restera manuelle tant que l'API Meta
n'est pas debloquee.

### 30.4 Ce que la consolidation ne fait PAS, volontairement

La colonne `personne` reste presque vide. **C'est voulu.**

`@lebouseuh` sur Instagram, `levraibouseuh` sur Instagram, la chaine
`UCUl7mwOyySfZzUkq4H29nug` sur YouTube : le script ne les rattache pas
automatiquement a une meme personne. Rapprocher deux comptes par la
ressemblance de leur nom, c'est exactement ce qui produit une confusion
d'homonyme — et « Norman » a deja montre que deux personnes peuvent porter le
meme nom (JOURNAL 28.4).

Le rattachement compte → personne est un **jugement humain explicite, date et
source** (METHODOLOGIE section 8). Il sera demande a Vincent quand il servira
a quelque chose, pas avant.

---

## 31. Journal de methode — 24 aout 2026 : l'API YouTube, et l'audience comme detecteur d'erreur

Cle fournie par Vincent. `outils/audiences_youtube.py` ecrit.

### 31.1 Le trou d'audience est comble cote YouTube

MESURE — `recherche/audiences_youtube_2026-08-24.csv`, **27 chaines,
3 unites de quota depensees sur ~10 000 par jour.**

| Chaine | Abonnes |
|---|---|
| SQUEEZIE | 20 200 000 |
| Norman | 11 200 000 |
| Michou | 11 000 000 |
| Inoxtag | 9 470 000 |
| Mcfly et Carlito | 7 660 000 |
| Mister V | 6 540 000 |
| SEB (@SEBFRIT) | 5 850 000 |
| MichouOff | 5 550 000 |
| SQUEEZIE GAMING | 5 100 000 |
| **LeBouseuh** | **4 620 000** |
| Inoxtag 2.0 | 3 140 000 |
| ZACK (@ZackNani) | 974 000 |

La couverture d'audience du registre passe de **3 % a 7 %** ; elle est
desormais complete pour toutes les chaines YouTube surveillees.

**LeBouseuh a 4,62 M d'abonnes sur YouTube contre 2,4 M sur Instagram.**
Illustration directe de METHODOLOGIE section 8 : l'audience est un attribut du
COMPTE, pas de la personne. Un seul chiffre par createur n'aurait aucun sens.

### 31.2 L'audience a servi de detecteur d'erreur

Le releve a fait apparaitre deux chaines absurdes : « seb la frite » avec
**1 630 abonnes** et « Zack Nani » avec **0 abonne**.

Origine : le releve de 16h39, anterieur au filtre du badge de verification,
avait resolu ces noms vers des chaines d'imposteurs. Les vraies chaines sont
@SEBFRIT (5,85 M) et @ZackNani (974 k).

**Une chaine a 0 abonne qui pretend etre un createur connu est une erreur
visible.** L'audience n'est donc pas seulement un critere de priorite : c'est
un **controle de coherence** sur la resolution des chaines. A utiliser
systematiquement.

Les deux fausses chaines sont inscrites dans `donnees/chaines_youtube.json`
sous `ecartes` : elles ne reviendront plus.

### 31.3 Resoudre par pseudo coute 1 unite, par recherche 100

Decouverte a l'usage. `channels.list?forHandle=SEBFRIT` renvoie directement la
chaine pour **1 unite**. `search.list` en coute **100**.

Et ce n'est pas qu'une question de cout : **un pseudo designe une seule
chaine**, alors qu'une recherche par nom ramene des homonymes et des chaines
de fans — c'est exactement ce qui avait produit la fausse « seb la frite ».

Regle : **toujours resoudre par pseudo quand on le connait.** La recherche est
un dernier recours, cher et ambigu. Consequence pratique : demander a Vincent
les @pseudos plutot que les noms usuels est cent fois moins couteux en quota
et plus sur.

### 31.4 Ce que l'API ne remplace pas

Elle ne donne pas la case de declaration « communication commerciale », qui
n'existe que dans la page publique `/watch`. La lecture directe reste donc
necessaire pour ce signal — conformement a l'arbitrage de Vincent : on
superpose les couches, on n'en choisit pas une (JOURNAL 23).

### 31.5 Etat du registre consolide

608 comptes distincts : 552 Instagram, 27 YouTube, 29 de plateforme
indeterminee. 43 avec audience connue. 22 arbitres par Vincent.

---

## 32. Journal de methode — 24 aout 2026 : la liste de surveillance se derive enfin toute seule

### 32.1 L'objection de Vincent

« Est-ce bien clair que le but de l'outil qu'on essaie de developper est
d'identifier ces createurs ? Lors du travail, je peux etre amene a t'en fournir
pour avancer, mais le produit final ne devra pas reposer sur mon travail. »

Objection fondee. La journee avait pris cette pente : je lui demandais des
pseudos, des comptes, des arbitrages. Legitime en R&D, disqualifiant comme
architecture. Inscrit en METHODOLOGIE section 7.1bis.

### 32.2 Premiere application : 162 chaines derivees, zero saisie

`outils/croiser_instagram_youtube.py` demande a l'API YouTube, pour chacun des
538 comptes Instagram suivis par les vitrines, s'il existe une chaine portant
le meme pseudo. `channels.list?forHandle` coute 1 unite.

MESURE — `recherche/croisement_ig_yt_2026-08-24.csv` :

- 538 pseudos essayes, **162 chaines YouTube trouvees**, 0 erreur
- **538 unites de quota** sur ~10 000 par jour

La liste de surveillance passe de 27 chaines nommees a la main a **162 derivees
des sources**. Les plus suivies, toutes issues des abonnements du CNIEL :

| Chaine | Abonnes |
|---|---|
| Michou | 11 000 000 |
| Inoxtag | 9 470 000 |
| Valouzz | 3 280 000 |
| Chefclub | 2 920 000 |
| BouziTV (@levraibouseuh) | 2 850 000 |
| Nota Bene | 2 770 000 |
| Djilsi | 2 350 000 |
| Pidi | 2 040 000 |
| Loris Giuliano | 1 920 000 |
| Juste Zoe | 1 560 000 |
| Doigby | 1 390 000 |
| Kemar | 1 280 000 |
| RebeuDeter | 1 060 000 |
| YanissaXoxo | 1 020 000 |

**Une dizaine de ces noms n'avaient jamais ete cites dans le projet.** Ils ne
viennent ni de la presse, ni de Vincent : ils sont derives du signal emis par
le commanditaire lui-meme.

### 32.3 Deux reserves, fermes

1. **Un meme pseudo sur deux plateformes ne prouve pas la meme personne.**
   Le rattachement est enregistre comme HYPOTHESE, jamais comme fait.
   La colonne le dit explicitement dans le fichier.
2. **Etre suivi par une vitrine ne prouve aucune collaboration** (JOURNAL 19).
   Ce croisement elargit la liste a SURVEILLER, rien de plus.

Le bruit est visible dans le resultat : @vice (19,2 M), @therock (7,1 M),
@primevideofr, @nytcooking sont des medias et des celebrites internationales
que le CNIEL suit sans rapport avec une collaboration francaise.

### 32.4 Correction de perimetre demandee par Vincent

« On veut aussi identifier des collaborations commerciales avec l'industrie
directement, un producteur de yaourts par exemple, pas seulement celles avec
les representants de l'industrie. »

C'est deja le perimetre ecrit en section 1 — « interprofessions **et marques
productrices** » — mais la table d'alias ne traite bien que les vitrines. Les
52 lignes de la feuille `Marques` sont toutes en statut A VERIFIER et ne sont
pas exploitees par les detecteurs.

**Trou reel a combler** : Danone, Lactalis, Herta, Bigard, Sodiaal doivent
entrer dans la table d'alias au meme titre que `@lesproduitslaitiers`.

---

## 33. Journal de methode — 24 aout 2026, nuit : 35 612 videos, et la recherche retroactive devient possible

Vincent, avant d'aller dormir : « es-tu sur qu'il n'y a pas un travail long et
laborieux qu'on pourrait lancer maintenant ? » Il avait raison d'insister.

### 33.1 Le deblocage : 50 videos avec descriptions pour 1 unite

`playlistItems.list` renvoie **50 videos avec leur description complete pour
1 unite de quota**. Verifie avant de s'en servir.

Le catalogue entier d'une chaine de 1 000 videos coute donc 20 unites sur les
~10 000 quotidiennes — **cinquante fois moins cher que telecharger les pages
une par une**, et sans la limitation opaque qui avait bloque la journee
(JOURNAL 28).

**L'hypothese YT-03 est levee.** Le flux RSS limitait a 15 videos par chaine
et interdisait toute recherche retroactive. L'API rend tout le catalogue.

### 33.2 La moisson

MESURE — `recherche/moisson_videos_2026-08-24.csv` :

| | |
|---|---|
| Chaines moissonnees | **185 sur 185** |
| Videos examinees | **35 612** |
| Quota depense | **806 unites** sur ~10 000 |
| Videos portant un signal commercial | 5 164 |
| Videos citant une entite de la filiere | 1 574 |
| **dont sur alias d'INTERPROFESSION (fiable)** | **271** |

### 33.3 Deux cas reels, hors de portee ce matin

**Michou — 11 000 000 d'abonnes — 8 mai 2022**

> « Merci aux produits laitiers ainsi qu'a la Federation francaise de Hockey
> sur glace de nous avoir accompagne sur ce projet ! »

Createur gaming generaliste, audience enorme, congruence faible : exactement
le profil defini avec Vincent le meme jour.

**Inoxtag — KAIZEN, le documentaire sur l'Everest — 20 septembre 2024**

> « Merci a mes partenaires air up, Nike, Deezer, Fitness Park, Erborian,
> **Les Produits Laitiers**, Orange, et Therm-ic de m'avoir accompagne et
> soutenu dans ce projet fou ! »

Le CNIEL etait partenaire de l'un des plus gros evenements YouTube francais
de 2024.

**Piste : Loris Giuliano, 35 videos** citant les produits laitiers entre 2019
et 2025. Trente-cinq occurrences etalees sur six ans ne sont pas un hasard :
c'est un partenariat suivi, a instruire. Idem **FlorianOnAir, 48 videos**.

Repartition des 271 detections fiables sur les grandes chaines : Michou (1),
Inoxtag (7, plus 2 sur sa chaine secondaire), Mister V (1), Valouzz (2),
Nota Bene (1), RebeuDeter (4), Juste Zoe (1).

### 33.4 Le bruit, et d'ou il vient

Sur 1 574 detections, **la majorite sont fausses**, et la cause est identifiee :
la feuille `Marques` — que Vincent a demande a integrer le meme soir — contient
des marques dont le nom est un **mot courant du francais**.

| Terme | Detections | Realite |
|---|---|---|
| « Marie » (LDC) | 308 | le prenom |
| « Societe » (Lactalis) | 228 | le mot |
| « President » (Lactalis) | 162 | le mot |
| « Le Foie Gras » (CIFOG) | 91 | l'aliment, pas la marque |

**Ce n'est pas un argument contre l'integration des marques** : elle etait
necessaire et Vincent avait raison de la demander. C'est un probleme de
methode d'appariement, a resoudre.

Piste retenue, non encore implementee : exiger qu'un terme figurant dans une
liste de « noms trop courants » **co-occure avec un indice commercial**
(code promo, mention legale, lien d'affiliation) pour compter. Les alias
d'interprofession, eux, sont specifiques et n'ont pas besoin de cette garde —
`@lesproduitslaitiers` ne ressemble a rien d'autre.

### 33.5 Ce que la moisson ne remplace pas

Ni la case de declaration (absente de l'API, page publique seulement), ni les
segments SponsorBlock (service tiers). Elle sert a **reduire l'espace de
recherche** : sur 35 612 videos elle en designe 271 a instruire. Les signaux
couteux ne s'appliqueront qu'a celles-la — ce qui rend enfin la surveillance
continue tenable en quota.

---

## 34. Journal de methode — 25 aout 2026 : l'API TikTok livre, et decoit sur un point precis

Candidature approuvee le 25/08. Identifiants recuperes par Vincent. Deux
blocages triviaux d'abord, tous deux resolus par le message d'erreur de l'API :
le champ s'appelle `creator` et non `creator.username`, et la borne haute de
date doit etre **strictement anterieure** au jour courant.

### 34.1 Ce que `commercial_content/query` rend vraiment

MESURE — `recherche/tiktok_commercial_2026-08-25_0539.csv` :

| | |
|---|---|
| Contenus recuperes | **20 000** (plafond de pagination atteint, il y en a plus) |
| **Createurs francais distincts** | **8 061** |
| Label « Paid Partnership » | 15 685 |
| Label « Promotional Content » | 4 313 |
| **`brand_names` renseigne** | **2 sur 20 000, soit 0 %** |

**TT-02 est CONFIRMEE** : les publications organiques a label de partenariat
figurent bien dans la bibliotheque. Ce n'est pas qu'un catalogue de publicites
achetees, et le filtre `creator_country_code: FR` suffit — **aucune liste de
createurs n'est necessaire en amont**, ce qui satisfait la contrainte posee par
Vincent (METHODOLOGIE 7.1bis).

**Mais `brand_names` est vide.** On sait qu'il y a partenariat remunere, on
sait qui est le createur, on ne sait pas **pour qui**. C'est precisement
l'information qui fait le registre.

### 34.2 Un piege : `search_term` est accepte et silencieusement ignore

Teste explicitement sur `commercial_content/query` :

| Terme cherche | Resultats | Memes identifiants que sans terme ? |
|---|---|---|
| aucun | 20 | — |
| « produits laitiers » | 20 | **oui** |
| « zzzzqqqxxx » | 20 | **oui** |

Un terme absurde rend exactement les memes contenus qu'une recherche vide.
**Le parametre est accepte sans erreur et n'a aucun effet.**

C'est le pire comportement possible pour un outil de recherche : rien ne
signale l'echec. Sans ce test a trois branches — sans terme, terme plausible,
terme absurde — on aurait conclu que la filiere viande/lait est absente de
TikTok, alors qu'on n'avait rien cherche du tout.

**A generaliser : toute fonction de recherche fournie par un tiers doit etre
validee par un terme absurde avant d'etre exploitee.** Si le terme absurde
rend des resultats, la recherche ne marche pas.

### 34.3 L'autre endpoint, lui, cherche vraiment — et nomme l'annonceur

`ad/query/` couvre les **publicites achetees**, pas les partenariats de
createurs. Mais son `search_term` fonctionne, verifie de la meme facon :

| Terme | Resultats | Annonceurs |
|---|---|---|
| « lait » | 10 | **NESTLE FRANCE**, MONDELEZ EUROPE SERVICES |
| « fromage » | 10 | **BEL**, BARILLA |
| « zzzqqqxxx » | **0** | — |

Zero resultat sur le terme absurde : le filtre est reel.

Champs valides, verifies un par un :

| Champ | Contenu |
|---|---|
| `advertiser.business_name` | l'annonceur — NESTLE FRANCE, BEL |
| **`advertiser.paid_for_by`** | **l'agence** — « Publicis Media - Starcom » |
| `ad.reach.unique_users_seen` | audience, par tranche (« 1M-10M ») |
| `ad.first_shown_date`, `ad.last_shown_date` | periode de diffusion |
| `ad.videos`, `ad.image_urls`, `ad.status` | le creatif |

`ad.creator` et `ad.audience` n'existent pas.

### 34.4 Le verdict, sans enjoliver

**Les deux endpoints ne se joignent pas.** L'un donne le createur sans la
marque, l'autre la marque sans le createur. **Il n'existe pas, dans cette API,
de chemin qui aille de l'annonceur au createur remunere.**

**TT-03 est donc REFUTEE** : la bibliotheque n'est pas interrogeable par
annonceur pour retrouver des createurs. C'etait l'esperance principale placee
dans TikTok, et elle ne se realise pas telle quelle.

**Ce qui reste, et qui est loin d'etre rien :**

1. **8 061 createurs francais** dont TikTok declare qu'ils ont fait du
   partenariat remunere. C'est une population definie, exactement ce qui
   manquait a la section 9.2 pour constituer un jeu de reference.
2. **Les annonceurs de la filiere sont identifiables** par mot-cle : NESTLE
   FRANCE et BEL sont deja sortis sur deux essais de dix resultats.
3. **`paid_for_by` nomme les agences** — la feuille Agences du classeur en
   avait quatre lignes ; cette source peut la nourrir systematiquement.
4. Chaque contenu porte l'**URL de sa video**. Le lien createur → marque
   manquant peut donc etre reconstruit en lisant la video elle-meme. C'est
   du travail, mais la voie existe.

### 34.5 Consequence pour la strategie

TikTok ne remplace pas la chaine YouTube, contrairement a ce qu'on esperait
hier. Il apporte autre chose, peut-etre plus precieux : **une population de
reference declaree par la plateforme**, sur laquelle mesurer le rappel de nos
propres methodes (METHODOLOGIE section 9).

---

## 35. Journal de methode — 25 aout 2026 : nettoyage des detections, et cartographie des annonceurs

### 35.1 Le bruit tombe de 1 029 detections

`outils/nettoyer_detections.py`, sans aucun appel reseau, retrie la moisson du
24/08 en separant deux familles de termes qui ne se valent pas :

| Famille | Exigence | Justification |
|---|---|---|
| Alias d'interprofession | une occurrence suffit | `@lesproduitslaitiers` ne ressemble a rien d'autre en francais |
| Nom de marque | **+ un indice commercial** | « Marie » et « Societe » sont des mots courants |

MESURE — `recherche/detections_nettoyees_2026-08-25.csv` :

| | |
|---|---|
| Detections brutes | 5 164 |
| **Preuves fortes** | **271** |
| Preuves faibles (marque + indice) | 274 |
| **Ecartees** | **1 029** |

Raisonnement de la regle : une vraie collaboration laisse presque toujours une
trace commerciale a cote du nom de la marque — code promo, lien, remerciement.
Un prenom dans un titre, non.

Ce que la regle coute : les mentions de marque sans indice commercial. Elles ne
sont pas supprimees mais classees « preuves faibles », et restent consultables.

### 35.2 Balayage de la bibliotheque publicitaire TikTok

`outils/balayer_annonceurs_tiktok.py` interroge `ad/query` sur les 52 marques
du classeur, les alias d'interprofession et douze termes generiques.

**Garde-fou applique d'emblee** : le script cherche d'abord un terme absurde et
s'arrete si celui-ci rend des resultats. Lecon directe de TT-09, ou
`search_term` etait silencieusement ignore sur l'autre endpoint. Controle
passe : 0 resultat.

MESURE — `recherche/tiktok_annonceurs_2026-08-25.csv` : 85 termes balayes,
**2 054 publicites, 655 annonceurs distincts**.

### 35.3 Ce que ca donne pour la filiere

| Annonceur | Pubs | Agence declaree (`paid_for_by`) |
|---|---|---|
| **INTERBEV** | **26** | **iProspect Conseil France** |
| FLEURY MICHON | 60 | en propre |
| YOPLAIT FRANCE | 60 | WPP MEDIA FRANCE |
| **BEL** (Babybel, Kiri, La Vache qui rit) | 56 | Publicis Media - Starcom |
| Entremont | 45 | Attraptemps |
| **NESTLE FRANCE** | 38 | VMLY&R France, WPP MEDIA FRANCE |
| DANONE PRODUITS FRAIS FRANCE | 17 | WPP MEDIA FRANCE |
| Candia (Sodiaal) | 8 | Vanksen |
| Savencia | 5 | Publicis Media - Blue449 |
| SOCOPA VIANDES | 5 | Gulfstream Communication |
| LACTALIS (Lactel) | 4 | Havas Media France |

**INTERBEV achete de la publicite sur TikTok via iProspect Conseil France.**
C'est une interprofession, pas une marque : elle fait de la publicite en son
nom propre sur une plateforme dont le public est tres jeune. L'agence n'etait
pas connue du projet — la feuille `Agences` comptait quatre lignes, dont deux
sans agence nommee.

Sept agences ont ete ajoutees a la feuille `Agences` avec cette source
primaire.

### 35.4 Deux limites a ne pas oublier

1. **Aucun createur dans ces donnees.** `ad/query` couvre les publicites
   achetees ; l'API ne relie jamais un annonceur a un createur remunere
   (TT-12, JOURNAL 34.4). Ces lignes enrichissent la cartographie des
   commanditaires, elles ne produisent aucune entree de registre.
2. **Faux positifs residuels** sur les marques au nom courant : « MADAM
   PRESIDENT » et « Artists for President B.V. » sortent sur le terme
   « President » (Lactalis). Le meme probleme qu'en 33.4, ici sans
   consequence puisque le tri est visuel.

---

## 36. Journal de methode — 25 aout 2026 : croisement TikTok x registre

`outils/croiser_tiktok_registre.py`, sans appel reseau.

MESURE — `recherche/croisement_tiktok_registre_2026-08-25.csv` :
8 060 createurs TikTok a partenariat declare, 764 identifiants au registre,
**31 comptes presents dans les deux**.

Les plus notables, par audience de l'autre plateforme :

| Pseudo | Contenus TikTok | Autre plateforme | Audience | Lien avec la filiere |
|---|---:|---|---:|---|
| **@justezoe** | **16** | YouTube | 1 560 000 | derive d'un compte suivi par le CNIEL |
| @doigby_ | 1 | YouTube | 1 390 000 | idem |
| @zacknani | 1 | YouTube | 974 000 | chaine surveillee |
| @florianonair | 3 | YouTube | 734 000 | idem, et partenaire INAPORC connu |
| @minireyve | 1 | Instagram | 193 000 | arbitre par Vincent, priorite haute |
| @herta_france | 13 | Instagram | — | **compte de marque**, suivi par INAPORC |
| @rorocuistot, @totocuistot | 14, 13 | Instagram | — | suivis par une vitrine |

**@justezoe est le candidat le plus fort du croisement** : 1,56 M d'abonnes
YouTube, seize contenus commerciaux declares sur TikTok, et son compte
Instagram figure dans les abonnements de la vitrine du CNIEL.

### Ce que ce croisement etablit, et rien de plus

Ces personnes font du partenariat remunere **declare par la plateforme**, ET
une source independante les associe deja a la filiere. **Cela ne dit pas que
le partenariat TikTok soit avec la filiere** : un createur peut etre suivi par
le CNIEL et faire du partenariat pour une marque de telephones. Les deux faits
sont vrais et independants ; leur conjonction est une **priorite d'enquete**.

Cas particulier : `@herta_france` est le compte d'une marque, pas d'un
createur. Il apparait parce qu'INAPORC le suit. A ecarter de la liste des
createurs, mais utile pour la table d'alias.

### Deux methodes independantes, enfin

C'est le premier croisement du projet entre deux sources qui n'ont rien en
commun : la declaration de TikTok d'un cote, les abonnements Instagram des
vitrines de l'autre. Cette independance est exactement la condition de
validite de l'estimation par capture-recapture (METHODOLOGIE section 9.3),
qui reste a mettre en oeuvre.

---

## 37. Journal de methode — 25 aout 2026 : le classeur de verification

Vincent : « quand j'ouvre le CSV, ce n'est pas evident a lire, c'est meme
illisible. Le .md n'est pas plus facile. Pense a me faciliter la tache. »

Troisieme reproche du meme ordre en deux jours. Regle inscrite en
METHODOLOGIE 13.4 : **tout ce qu'on lui demande arrive en classeur Excel mis
en forme.**

### 37.1 Ce qui rend un candidat jugeable

`outils/generer_classeur_verification.py` produit `cartographie/A_VERIFIER.xlsx`
— 271 videos triees par audience decroissante, deux colonnes a remplir.

L'element decisif n'est pas la mise en forme : c'est **l'extrait**. Le classeur
montre le passage de la description qui a declenche la detection, pas la
description entiere. Un passage de 300 caracteres se juge sans ouvrir la video.

### 37.2 Trois defauts corriges avant livraison

**L'extrait tombait a cote dans 3 cas sur 4.** L'appariement se fait sur une
forme aplatie — sans accents, sans espaces — pour que `@lesproduitslaitiers`
rencontre « Les Produits Laitiers ». Mais l'extrait doit etre decoupe dans le
texte ORIGINAL. Il fallait donc garder la correspondance entre les deux
positions, ce que le premier jet ne faisait pas.

**La fenetre etait mal placee.** Elle montrait 200 caracteres avant la mention
et s'arretait juste apres. Or c'est ce qui SUIT qui renseigne : « merci aux
Produits Laitiers **pour nous avoir finance le voyage** ». Fenetre passee a
90 avant, 330 apres.

**27 mentions sont hors de portee.** La moisson n'avait conserve que les 900
premiers caracteres de chaque description ; quand la mention est au-dela, le
classeur l'ecrit explicitement au lieu d'afficher un debut de texte sans
rapport. Un extrait trompeur ferait juger sur le mauvais passage.

Resultat : **244 extraits exploitables sur 271**.

### 37.3 Un cas explicite

Inoxtag, 15 aout 2020 :

> « Merci aux Produits Laitiers pour nous avoir **financer le voyage** ! »

Le createur ecrit lui-meme que le CNIEL a finance le deplacement. C'est le
libelle le plus explicite rencontre jusqu'ici.

### 37.4 A quoi servent ces annotations — la reponse a Vincent

Sa question : « est-ce que ca a des chances de mener a une automatisation ?
Le but final n'est pas que je passe des heures a valider toutes les nouvelles
videos. »

**Non, ces annotations ne sont pas de la validation perpetuelle. Elles
construisent l'instrument de mesure.**

Sans un ensemble de cas juges par un humain, aucune detection automatique ne
peut etre EVALUEE. On peut faire lire les descriptions par un modele de
langage — c'est deja techniquement possible et gratuit — mais on n'aurait
aucun moyen de savoir si ses jugements sont bons. Les annotations de Vincent
donnent cette reference.

Le chemin, en trois temps :

1. Vincent juge une centaine de cas. Cout : quelques heures, une fois.
2. La detection automatique tourne sur **exactement les memes cas**. On
   compare, on obtient un taux d'erreur chiffre — ce que le projet n'a jamais
   eu (METHODOLOGIE section 9).
3. Si le taux est bon, l'automatisation prend le relais et l'humain ne
   verifie plus que par sondage. S'il est mauvais, on sait **ou** elle se
   trompe, donc quoi corriger.

**Annoter maintenant, c'est ce qui permettra de ne plus annoter plus tard.**
C'est ecrit dans l'onglet « COMMENT FAIRE » du classeur.

---

## 38. Journal de methode — 25 aout 2026 : le projet a enfin une mesure

Vincent a juge **les 271 candidats**, un par un — pas la centaine suggeree.
C'est le **jeu de reference** qui manquait depuis le premier jour
(METHODOLOGIE section 9.2).

### 38.1 La verite de terrain

MESURE — `cartographie/A_VERIFIER.xlsx`, 271 lignes annotees :

| Verdict | Videos |
|---|---|
| **collaboration remuneree** | **67** |
| hors sujet | 195 |
| je ne sais pas | 9 |

**Precision de la detection actuelle : 25 %.** Trois candidats sur quatre
etaient du bruit. C'est la premiere fois que le projet peut ecrire ce chiffre.

### 38.2 Pourquoi, entite par entite

| Entite | Vrais / total | Precision |
|---|---|---|
| CNIEL | 57 / 129 | 44 % |
| INTERBEV | 7 / 31 | 23 % |
| INAPORC | 2 / 7 | 29 % |
| ANVOL | 1 / 3 | 33 % |
| **CIFOG** | **0 / 91** | **0 %** |
| **CLIPP** | **0 / 10** | **0 %** |

**CIFOG a produit a lui seul 88 des 195 faux positifs.** Son alias est « Le
Foie Gras » — qui designe l'aliment bien plus souvent que la marque.

Meme mecanisme, plus discret, pour `@lesproduitslaitiers` : 45 faux positifs,
parce que « produits laitiers » est une categorie alimentaire courante.

**Constat de fond : les interprofessions ont choisi des noms generiques a
dessein.** « Les Produits Laitiers », « Le Foie Gras », « Le Porc Francais »,
« La Viande ». C'est toute la strategie de la vitrine, decrite en
METHODOLOGIE section 2 — et elle **defait l'appariement de chaines de
caracteres par construction**. Ce n'est pas un defaut de notre table d'alias :
c'est le resultat d'un choix de communication de l'industrie.

Ce qui distingue une vraie mention n'est donc pas le terme, mais **ce qu'il y
a autour**. « Merci aux Produits Laitiers **de nous avoir accompagnes** » n'est
pas « bien manger, avec des produits laitiers ».

### 38.3 Quatre regles mises a l'epreuve du jeu de reference

`outils/evaluer_detection.py`. Descriptions **completes** recuperees par
l'API (`videos.list`, 6 unites) — la moisson n'en avait garde que 900
caracteres, ce qui coupait la mention dans 27 cas.

| Regle | Retenus | Vrais | Faux | Precision | Rappel |
|---|---:|---:|---:|---:|---:|
| **A.** l'alias suffit *(actuelle)* | 271 | 67 | 204 | **25 %** | 100 % |
| **B.** + vocabulaire de collaboration dans la description | 99 | 60 | 39 | 61 % | 90 % |
| **C.** + vocabulaire **pres** de la mention | 92 | 60 | 32 | 65 % | 90 % |
| **D.** C, et alias generique ecarte s'il est seul | **69** | **57** | **12** | **83 %** | **85 %** |

**La regle D fait passer la precision de 25 % a 83 % en ne perdant que 15 %
des vrais cas.** Le travail humain de verification est divise par quatre.

C'est la reponse chiffree a la question de Vincent — « est-ce que ca a des
chances de mener a une automatisation ? ». Oui, et voici de combien.

### 38.4 Ce que ca dit du role de l'annotation

Aucune de ces quatre regles n'aurait pu etre comparee sans les jugements de
Vincent. On aurait choisi a l'intuition, et on aurait probablement garde la
regle A en croyant bien faire.

**Le jeu de reference ne sert pas a valider des videos : il sert a choisir des
methodes.** Il se reutilise a chaque nouvelle idee de detection, indefiniment.
Les heures passees a annoter sont un investissement a rendement permanent.

Limite honnete : 271 cas venant de 6 entites et d'un seul canal de detection.
Le jeu est **biaise vers ce que la methode actuelle trouve** — il ne dit rien
des collaborations qu'aucune de nos regles ne voit. Pour cela il faudra le
tirage aleatoire de la section 9.2, qui reste a faire.

### 38.5 Les cas ou Vincent ne peut pas trancher

Neuf « je ne sais pas », et ses notes disent pourquoi :

> « Pas sur a 100 %, mais presque. Une mention d'un lobby identifie est tres
> probablement le signe d'une collaboration remuneree. »

> « Comment je fais pour savoir s'ils ont recu des sous ? »

Ce n'est pas un defaut d'attention : **l'information n'existe pas dans le
contenu.** En l'absence de declaration du createur, la remuneration n'est pas
etablissable par observation. Cela confirme le champ `degre de certitude`
decide le 24/08 (METHODOLOGIE section 1) — et cela justifie la proposition
qu'il formule au meme moment : publier les **signaux observes** plutot qu'un
verdict.

---

## 39. Journal de methode — 25 aout 2026 : cinq orientations, et une reserve sur la solidite

Vincent, apres avoir annote les 271 : « si tu es sur qu'on tient la piste
d'une methode solide, je suis content. Mais en es-tu sur ? »

**Reponse donnee, et a garder : on tient un morceau solide de methode, pas une
methode solide.**

Ce qui est solide : sur YouTube, le canal « description » fonctionne, il est
mesure, on sait l'ameliorer. 83 % de precision est exploitable.

Ce qui ne l'est pas :

1. **On ne sait pas ce qu'on rate.** Le « rappel » de 85 % se mesure sur les
   67 cas que la regle A avait trouves — pas sur la realite. Le vrai rappel
   reste inconnu.
2. Une plateforme sur trois est operationnelle.
3. Six entites testees, dont deux a 0 % de precision.
4. **Un signal sur quatre a ete evalue.** La case de declaration, SponsorBlock
   et la transcription n'ont jamais ete confrontes au jeu de reference.

Les cinq orientations formulees par Vincent pendant l'annotation sont
inscrites en METHODOLOGIE 14bis. La quatrieme — publier les signaux plutot
qu'un verdict — change la nature du produit final et merite d'etre relue en
entier.

---

## 40. Journal de methode — 25 aout 2026, nuit : la decouverte d'alias inconnus

Mise en oeuvre de l'orientation 14bis.1. `outils/decouvrir_alias.py`.

### 40.1 Le renversement

Toute la detection cherchait des alias **connus**. Elle ne pouvait donc, par
construction, rien trouver de nouveau : une marque creee demain resterait
invisible jusqu'a ce qu'un humain l'ajoute a la main.

Ce script cherche la **forme** du remerciement commercial — « merci a X »,
« en partenariat avec X », « avec le soutien de X », « sponsorisee par X » —
et recolte le X **quel qu'il soit**. Les X connus sont ecartes ; les autres
deviennent des candidats.

Le pari : le vocabulaire de l'industrie change, la forme du remerciement non.

### 40.2 Verification a petite echelle

MESURE, 13 chaines, 2 448 videos, 62 unites de quota : **51 annonceurs
inconnus de la table d'alias**, dont

| Annonceur | Chaines distinctes |
|---|---|
| Air up | 5 |
| NordVPN | 4 |
| Rhinoshield | 4 |
| Saily | 3 |
| Ultra Premium Direct | 3 |
| Revolut, Odoo, happn, Qonto, Holy | 2 |

Aucun n'est de la filiere viande/lait — c'etait attendu. **Ce n'est pas un
echec : c'est la demonstration que le mecanisme fonctionne** sur des
annonceurs que personne n'avait saisis. Le jour ou une marque laitiere apparait
dans un remerciement, elle sera capturee sans intervention.

Bruit residuel a trier : « tous ceux », « toute l'equipe », et des prenoms de
createurs qui se remercient entre eux. Le tri reste humain — **aucun jugement
automatique n'est porte sur le secteur d'un annonceur**, ce serait exactement
l'inference dont ce projet se mefie.

### 40.3 Ce que ca change pour la robustesse

La table d'alias cesse d'etre uniquement une **entree** du systeme : elle en
devient aussi une **sortie**. C'est la reponse a l'inquietude de Vincent —
« l'industrie va toujours creer de nouvelles marques ».

Le cout est faible : environ 9 unites de quota par chaine pour 600 videos,
soit moins de 2 000 unites pour les 185 chaines surveillees, sur 10 000
disponibles par jour.

---

## 41. Journal de methode — 25 aout 2026, nuit : la moisson complete de decouverte

MESURE — `recherche/alias_candidats_2026-08-25.csv` :

| | |
|---|---|
| Chaines parcourues | **185 sur 185** |
| Videos examinees | **31 149** |
| Quota depense | **851 unites** sur ~10 000 |
| Mentions de remerciement capturees | 2 661 |
| **Annonceurs inconnus de la table d'alias** | **229** |

Les plus repandus : Air up (8 chaines), Saily (7), NordVPN (7), Ultra Premium
Direct (7), Rhinoshield (5), happn, Epic Games, IGraal, Revolut, Vinted,
BoursoBank, HelloFresh, FRUITZ.

### 41.1 Le mecanisme s'est valide lui-meme, par accident

Au premier passage, le script a signale **« Produits Laitiers » comme annonceur
INCONNU** — 4 chaines, 8 mentions.

C'etait un bug : la comparaison aplatissait `@lesproduitslaitiers` en
`lesproduitslaitiers`, alors que la capture donnait `produitslaitiers`, sans
l'article. Les deux ne se reconnaissaient pas.

**Mais c'est aussi la meilleure validation possible du mecanisme.** Sans rien
savoir de la filiere, en cherchant seulement la forme « merci a X », le script
a redecouvert tout seul le principal commanditaire du projet, sur quatre
chaines differentes. C'est exactement ce qu'on lui demande de faire pour une
marque qui n'existe pas encore.

Corrige : les formes sans article sont ajoutees a l'ensemble des connus.

### 41.2 Deuxieme correction : le drapeau « connu » se recalcule

Le drapeau etait fige au moment de la capture. Or **la table d'alias evolue** :
un candidat d'hier peut etre un alias connu aujourd'hui. Fige, il aurait fallu
re-moissonner 31 000 videos pour le mettre a jour.

Il est desormais recalcule a l'agregation, sur le cache existant, sans aucun
appel reseau. C'est ce qui permet de relancer le tri gratuitement chaque fois
que la table change.

### 41.3 Le bruit restant

Sur les 229 candidats, une part notable n'est pas un annonceur : « tous ceux »,
« toutes les personnes », des prenoms de createurs qui se remercient entre eux,
et des URL capturees par le motif. Le tri reste humain, comme prevu.

Le rapport de cout est neanmoins favorable : **851 unites de quota pour
parcourir 31 149 videos** et en extraire 229 candidats a examiner.

---

## 42. Correction — 25 aout 2026 : ce que la decouverte a reellement montre

Reaction de Vincent au compte rendu de l'entree 41 : « la plupart ne sont pas
lies au lobby de la viande ou du lait. Qu'est-ce que tu racontes ? »

**Il a raison, et le compte rendu etait fautif.** L'entree 41 mettait en avant
Air up, NordVPN, Saily, Vinted, Epic Games comme s'il s'agissait de resultats
du projet. Ce sont des prises accessoires d'un test de mecanisme. Le cadrage
avait ete donne au message precedent puis abandonne au moment de presenter la
moisson complete.

### 42.1 Le resultat reel, verifie

Balayage des 229 candidats sur un motif alimentaire large — lait, fromage,
viande, porc, volaille, oeuf, ferme, elevage, plus les noms des grands groupes
(Danone, Lactalis, Nestle, Bel, Savencia, Sodiaal, Bigard, Herta, LDC...) :

**1 candidat sur 229**, et c'est « Noblessa Cuisines » — du mobilier.

**Zero nouvel annonceur de la filiere viande/lait sur 31 149 videos et
185 chaines.**

### 42.2 Ce que ce zero veut dire, et ce qu'il ne veut pas dire

**Ce qu'il dit :** la table d'alias n'est pas gravement incomplete sur cette
population. C'est une mesure de completude, et c'est la seule vraie trouvaille
de la moisson.

**Ce qu'il ne dit pas :** que la filiere soit absente de ces 185 chaines. Le
mecanisme ne detecte que les annonceurs **nommes dans une formule de
remerciement**.

Or METHODOLOGIE section 2 documente exactement le contraire : sur la campagne
INTERBEV de 2025, **le commanditaire n'etait jamais nomme**, et le compte
partenaire n'apparaissait que sur une publication sur trois.

**Un lobby qui applique la strategie de la vitrine a fond est invisible pour
cet outil, par construction.** Le zero prouve l'absence de mentions nommees,
pas l'absence de collaborations.

### 42.3 Consequence

La decouverte par la forme du remerciement reste utile — c'est un filet de
securite contre les marques nouvelles — mais elle **ne peut pas etre le
principal moyen de detection**. Elle partage l'angle mort du reste de la
chaine : tout ce qui repose sur le nom echoue quand le nom est volontairement
absent.

Les signaux qui ne dependent pas du nom gardent donc leur importance : la case
de declaration YouTube, les segments SponsorBlock, et le signalement citoyen
prevu par l'extension (METHODOLOGIE 14bis.5). Aucun des trois n'a encore ete
mesure contre le jeu de reference.

---

## 43. Journal de methode — 25 aout 2026, nuit : SponsorBlock mesure, et il decoit

`outils/mesurer_signaux.py`, sur les 271 candidats juges par Vincent.
SponsorBlock est un service tiers gratuit : la mesure n'a coute aucun quota.

MESURE — `recherche/mesure_signaux_2026-08-25.md`, 271 interrogations,
0 erreur :

| Signal | Retenus | Vrais | Precision | Rappel |
|---|---:|---:|---:|---:|
| **Indice commercial en description** | 82 | 58 | 71 % | **87 %** |
| Mention legale en description | 21 | 15 | 71 % | 22 % |
| **SponsorBlock : au moins un segment** | 13 | 9 | 69 % | **13 %** |
| SponsorBlock OU indice en description | 83 | 59 | 71 % | 88 % |
| SponsorBlock ET indice en description | 12 | 8 | 67 % | 12 % |
| Code promo en description | 2 | 0 | 0 % | 0 % |

### 43.1 SponsorBlock n'apporte presque rien

**Precision honorable (69 %), rappel tres faible (13 %).** Sur 67 vraies
collaborations, SponsorBlock n'en voit que 9.

Pire pour la strategie : **8 de ces 9 sont deja vues par la description.**
Ajouter SponsorBlock a la detection par description fait passer le rappel de
87 % a 88 % — un point.

C'est une revision nette de l'entree JOURNAL 18.1, qui saluait la precision de
SponsorBlock (12 sur 12 a l'arbitrage humain). Cette precision est reelle ;
c'est sa **couverture** qui est insuffisante.

### 43.2 La capture-recapture echoue, et c'est instructif

METHODOLOGIE section 9.3 exige deux methodes **independantes**. Calcul sur les
vraies collaborations : SponsorBlock en voit 9, la description 58, les deux en
commun 8. L'estimation *a x b / m* donne **65**, pour 67 cas observes.

Une estimation egale au nombre deja observe signifie que les deux methodes ne
sont pas independantes : elles se trompent sur les memes videos. **La
capture-recapture entre ces deux signaux-la est donc inutilisable.**

Il faut chercher des paires reellement independantes. Candidats : la
declaration YouTube, le contenu parle par transcription, le signalement
citoyen de la future extension.

### 43.3 Le code promo, contre-mesure

L'entree 18.2 avancait que le code promo est un meilleur indice que la
mention legale, parce qu'il est ecrit pour etre utilise. **Sur ce jeu, il fait
0 sur 2.** L'echantillon est minuscule et ne refute rien, mais il n'appuie
rien non plus : l'idee reste a tester ailleurs.

### 43.4 La limite qui pese sur toute cette mesure

Les 271 candidats viennent **tous** du canal « description ». Le faible rappel
de SponsorBlock est donc en partie un artefact : on ne mesure sa couverture que
la ou la description a deja trouve quelque chose.

Ce qui reste solide malgre l'artefact : **8 des 9 cas SponsorBlock sont aussi
des cas description**. La ou SponsorBlock voit quelque chose, la description
voit presque toujours la meme chose. Ce recouvrement-la ne depend pas du biais
d'echantillonnage.

---

## 44. Journal de methode — 25 aout 2026, nuit : la population de surveillance x13

### 44.1 Une meilleure semence

Les 185 chaines surveillees venaient des abonnements Instagram des vitrines.
**Etre suivi par un lobby ne prouve rien** (JOURNAL 19) : ce vivier n'est
qu'une hypothese de ciblage.

Les createurs de la Commercial Content Library sont d'une autre nature :
**TikTok declare qu'ils ont fait du partenariat remunere**. Ce sont des
createurs commerciaux averes. Comme semence, c'est strictement meilleur.

MESURE — `recherche/croisement_tt_yt_2026-08-25.csv` :

| | |
|---|---|
| Createurs TikTok essayes | **7 000** sur 8 061 |
| **Chaines YouTube trouvees** | **2 187** |
| dont au moins 100 000 abonnes | **373** |
| Quota depense | 7 000 unites (budget du jour epuise) |

Taux de correspondance : **31 %**, identique a celui du croisement Instagram.
Les 1 061 createurs restants attendent le quota de demain.

Les plus grosses chaines ainsi trouvees : FastGoodCuisine (8,77 M),
L'atelier de Roxane (4,52 M), Nicocapone (6,37 M), Victor de Martrin (4,86 M),
Gotaga (4,43 M), Greg Guillotin (4,41 M), Poisson Fecond, Studio Bagel,
EnjoyPhoenix (3,71 M), Guillaume Pley.

**Aucune n'etait dans la liste de surveillance.**

### 44.2 Un defaut du filtre a signaler

Le filtre `creator_country_code: FR` remonte aussi David Guetta (27,9 M),
Neymar Jr (9,07 M) et Christian Dior. Ce ne sont pas des createurs francais au
sens du projet : le champ decrit apparemment le marche vise ou la localisation
declaree, pas la nationalite du compte.

Sans consequence pour la detection — ces comptes ne porteront simplement aucun
signal filiere — mais **il ne faudra jamais decrire cette population comme
« les createurs francais »** sans cette reserve.

### 44.3 Etat du registre

`cartographie/COMPTES.xlsx` passe de 766 a **5 129 comptes** :

| Plateforme | Comptes |
|---|---|
| YouTube | 2 361 |
| TikTok | 2 187 |
| Instagram | 552 |
| indeterminee | 29 |

**46 % ont une audience connue**, contre 3 % ce matin.

### 44.4 Ce qui reste a faire, et son cout

Moissonner les descriptions de ces 2 361 chaines coutera environ **20 000
unites** de quota — deux jours de budget. C'est la prochaine etape, et elle
demultipliera d'autant la detection : la moisson de 185 chaines avait deja
sorti 271 candidats dont 67 vraies collaborations.

---

## 45. Correction — 25 aout 2026 : la « population de reference » TikTok n'en est pas une

### 45.1 Ce que la moisson a reellement couvert

Le rapport genere annoncait « 47 mois sur 47 » et « 6 227 createurs francais
distincts ». **Les deux chiffres sont trompeurs.**

Verification de l'etat reel :

| Mois | Contenus |
|---|---|
| Octobre 2022 | 13 038 |
| Novembre 2022 | 2 747 |
| **Decembre 2022 a aout 2026** | **0 — jamais interroges** |

**TikTok a un quota journalier**, epuise apres deux mois de moisson. Tous les
appels suivants ont echoue en `daily_quota_limit_exceeded`, et le script les a
comptabilises comme des mois « faits » a zero contenu.

La population n'est donc pas « les createurs francais de 2022 a 2026 » : c'est
**deux mois de fin 2022**, vieux de bientot quatre ans.

### 45.2 Le bug, et pourquoi il est grave

Le script marquait un mois comme **fait** meme quand l'appel avait echoue. Une
reprise le lendemain aurait saute les 45 mois manquants et **le trou serait
devenu permanent et invisible** : le fichier aurait affiche « 47 mois sur 47 »
indefiniment.

C'est exactement la faute que METHODOLOGIE 13.3 interdit — confondre l'absence
de resultat et l'absence de mesure — appliquee cette fois a la **reprise**
plutot qu'a la collecte. Je l'avais ecrite le 24/08 et je l'ai refaite le 25.

Corrige : un mois en echec n'est plus enregistre, et un epuisement de quota
arrete proprement la boucle au lieu de la laisser echouer 45 fois de suite.
L'etat a ete nettoye : 45 mois sont a reprendre.

### 45.3 Ce que ca dit du volume reel

Octobre 2022 seul rend **13 038 contenus commerciaux francais**. Si l'ordre de
grandeur tient sur 47 mois, la bibliotheque contient **plusieurs centaines de
milliers** de contenus pour la France.

Au rythme observe — environ deux mois de donnees par jour de quota — la
moisson complete demanderait **une vingtaine de jours**. C'est faisable, mais
c'est un chantier de fond, pas une tache de nuit.

### 45.4 Ce qui reste vrai malgre la correction

- `brand_names` est vide sur **15 781 contenus** verifies, soit 0,00 %.
  L'hypothese TT-08 est refutee de facon bien plus solide qu'hier.
- Le decoupage mensuel **fonctionne** : il contourne le plafond de pagination.
  Octobre 2022 a rendu 13 038 contenus la ou une requete unique plafonnait a
  20 000 pour toute la periode.
- Les 8 061 createurs issus de la premiere moisson restent valides comme
  vivier — ils ont produit 2 187 chaines YouTube.

Mais **le projet n'a toujours pas de population de reference complete**, et
donc toujours pas de moyen de tirer un echantillon aleatoire.

---

## 46. Journal de methode — 26 aout 2026 : la semence TikTok est treize fois moins productive

### 46.1 Ce que j'avais affirme

Le 25 aout au soir, en lancant le croisement TikTok, j'ai ecrit que ces
createurs etaient « **strictement meilleurs** » comme semence que les
abonnements des vitrines, au motif que TikTok **declare** leur partenariat
remunere la ou un abonnement ne prouve rien.

Le raisonnement etait plausible. Il n'avait pas ete teste.

### 46.2 La mesure

Moisson du 26/08 : 426 chaines, **113 364 videos**, 2 103 unites de quota
avant epuisement. Preuves fortes obtenues, rapportees a leur semence :

| Semence | Chaines | Preuves fortes | Par chaine |
|---|---:|---:|---:|
| **Abonnements des vitrines → YouTube** | 126 | **267** | **2,12** |
| Createurs TikTok → YouTube | 207 | 33 | **0,16** |
| Liste initiale, nommee a la main | 22 | 4 | 0,18 |

**La semence « abonnements des vitrines » est treize fois plus productive.**

### 46.3 Pourquoi — et cette fois c'est explique par la methodologie, pas invente

METHODOLOGIE section 12 le disait deja : les comptes suivis par une vitrine
sont « un signal emis par le commanditaire lui-meme ». Ce n'est pas une
proximite vague : c'est le lobby qui designe qui l'interesse.

Un createur commercial avere sur TikTok, lui, est commercial **pour n'importe
quel secteur** — VPN, telephones, applications. Sa probabilite de travailler
pour la filiere viande/lait n'est pas superieure a celle d'un createur
quelconque.

J'avais confondu deux qualites : « fait du commercial » et « fait du commercial
POUR LA FILIERE ». La premiere est plus facile a etablir ; c'est la seconde
qui interesse le projet.

### 46.4 Consequence strategique, immediate

**La priorite d'elargissement n'est pas TikTok, c'est d'obtenir davantage de
listes d'abonnements de vitrines.**

Vincent en a releve quatre : `@lesproduitslaitiers`, `@la_viande_fr`,
`@leporcfrancais`, `@volaillefrancaise`. Chacune produit environ deux preuves
fortes par chaine derivee. Il reste a explorer :

- les comptes regionaux d'INTERBEV, reperes sur leur site ;
- les comptes de campagne (`Naturellement Flexitariens`, `Aimez la viande`) ;
- les comptes des grandes marques (Danone, Lactalis, Bel, Nestle France) —
  jamais releves, alors que ce sont des commanditaires directs ;
- les memes comptes sur TikTok et YouTube, ou les abonnements different.

Les 1 935 chaines TikTok restantes conservent une valeur, mais **beaucoup plus
faible que je ne l'ai annonce**. Elles passent apres.

### 46.5 Ce que cette erreur enseigne

C'est le meme mecanisme que pour David Guetta et que pour le compte rendu des
annonceurs : **une explication plausible enoncee avec l'assurance d'un
constat**. Trois fois en deux jours.

La regle ajoutee hier — toute affirmation causale porte une etiquette, et un
constat surprenant appelle un test avant une phrase — s'applique ici
integralement. « Strictement meilleur » etait une prediction, pas une mesure,
et elle etait fausse.

---

## 47. Journal de methode — 26 aout 2026 : Studio Danielle, et une campagne inconnue

### 47.1 Le classeur des nouveaux candidats

33 nouvelles preuves fortes, hors des 271 deja jugees par Vincent.
`cartographie/A_VERIFIER_2.xlsx`, avec deux nouveautes :

- une colonne **« Retenu par la regle D »**, pour que l'arbitrage de Vincent
  serve aussi a evaluer la regle sur des entites jamais testees ;
- les **descriptions completes** recuperees par l'API (1 unite de quota), au
  lieu des 900 caracteres tronques de la moisson. Sans cela, 30 des 33
  extraits etaient inutilisables.

La regle D n'en retient que **5 sur 33**. Elle ecarte notamment David Guetta
(ANVOL), Lena Situations (ANVOL) et Violin Phonix (CLIPP) — trois faux
positifs previsibles sur des alias generiques.

### 47.2 Studio Danielle : quatre videos, mentions explicites

**Studio Danielle, 1 740 000 abonnes.** Extraits des descriptions, verbatim :

> « Cette video est en partenariat avec Les Produits Laitiers et leur campagne
> **En Mode Actif cofinancee par l'UE**, qui vise a lutter contre la
> sedentarite. »

> « Merci aux Produits Laitiers pour l'invitation au salon et pour **la
> sponsorisation de cette video**. »

> « Merci aux Produits Laitiers d'avoir **sponsorise cette video**. »

Quatre videos, dont deux portant la mention « Collaboration commerciale ».
C'est le libelle le plus explicite rencontre depuis le debut du projet.

### 47.3 « En Mode Actif » : un alias que la table ignorait

La campagne **En Mode Actif** n'etait pas dans la feuille Alias. Elle y est
ajoutee, statut CONFIRME, source primaire : la description du createur qui la
nomme.

**Et elle est declaree « cofinancee par l'Union europeenne ».** Cela relie
directement au dossier AGRIP inscrit au TODO depuis la premiere session — les
subventions europeennes de promotion agricole. Une campagne d'influence
francaise financee en partie par de l'argent public europeen est exactement le
type de fait que le registre existe pour documenter.

### 47.4 Ce que ca valide

C'est le premier alias decouvert **par la chaine elle-meme** plutot que saisi a
la main. Il n'est pas venu du script de decouverte de JOURNAL 41, mais de la
lecture d'un candidat : la mention etait dans une description qu'on avait deja
moissonnee, invisible faute de description complete.

Lecon operationnelle : **la troncature a 900 caracteres coutait des
decouvertes**, pas seulement de la lisibilite. Les descriptions completes
devraient etre recuperees systematiquement pour tout candidat retenu.

---

## 48. Journal de methode — 26 aout 2026 : la regle D est une regle du CNIEL

### 48.1 Ce que le detail par entite revele

La regle D annoncait 83 % de precision et 85 % de rappel. **Ces chiffres
cachaient une repartition tres inegale.** Evaluation entite par entite contre
les jugements de Vincent :

| Entite | Candidats | Vrais | Gardes par D | Dont vrais | **Vrais perdus** |
|---|---:|---:|---:|---:|---:|
| CNIEL | 129 | 57 | 67 | **57** | **0** |
| CIFOG | 91 | 0 | 0 | 0 | 0 |
| CLIPP | 10 | 0 | 0 | 0 | 0 |
| **INTERBEV** | 31 | 7 | 2 | 0 | **7** |
| **INAPORC** | 7 | 2 | 0 | 0 | **2** |
| **ANVOL** | 3 | 1 | 0 | 0 | **1** |

**La regle D est parfaite sur le CNIEL et aveugle sur tout le reste.** Elle
conserve les 57 vrais cas du CNIEL et perd les 10 des trois autres
interprofessions.

Le rappel de 85 % annonce hier etait donc trompeur : les 15 % perdus n'etaient
pas repartis au hasard, c'etaient **toutes** les entites non-CNIEL.

### 48.2 Deux causes, deux corrections

**Cause 1 — l'appariement des termes generiques etait fait par sous-chaine.**
« Aimez la viande, mangez-en mieux » etait classe generique parce qu'il
contient « la viande ». Or c'est un **slogan**, aussi specifique qu'un pseudo.
Corrige : un alias est generique s'il **EST** un terme courant, pas s'il en
contient un.

**Cause 2 — j'ai cru qu'un @pseudo se reconnaissait a son etiquette.** La
regle E accordait sa confiance a tout alias dont le libelle commence par `@`.
Mais l'appariement travaille sur une forme aplatie : l'etiquette
« @lesproduitslaitiers » peut avoir ete declenchee par « produits laitiers »
sans arobase, qui est une categorie alimentaire.

Resultat : la regle E tombe a **43 % de precision** pour 96 % de rappel.

Regle F, qui teste la presence **litterale** du pseudo, arobase comprise :
elle donne exactement les memes chiffres que D. Autrement dit, dans ce corpus,
un pseudo ecrit tel quel est toujours accompagne de vocabulaire de
collaboration. **Le test litteral n'apporte rien de plus.**

| Regle | Retenus | Precision | Rappel |
|---|---:|---:|---:|
| A. l'alias suffit | 271 | 25 % | 100 % |
| D. vocabulaire proche + generique exclu | 75 | **77 %** | **87 %** |
| E. etiquette portant un @ | 149 | 43 % | 96 % |
| F. pseudo litteral | 75 | 77 % | 87 % |

### 48.3 La vraie cause des cas perdus : deux alias manquants

En cherchant pourquoi les six cas FlorianOnAir resistaient, la reponse n'etait
pas dans la regle mais dans la table. Leurs descriptions parlent de
**« Made in Viande »** — les portes ouvertes annuelles d'INTERBEV.

**Cette operation n'etait pas dans la feuille Alias.** La detection attrapait
ces videos par appariement approximatif, sans savoir de quoi il s'agissait.
Ajoutee, statut CONFIRME.

C'est le deuxieme alias decouvert aujourd'hui, apres « En Mode Actif » du
CNIEL. Tous deux etaient **deja presents dans des descriptions moissonnees**.

### 48.4 Ce qu'il faut en retenir

Ameliorer la regle de decision a un rendement decroissant : de A a D, la
precision triple. De D a F, elle ne bouge pas.

**Ce qui manque n'est pas une meilleure regle, c'est une meilleure table
d'alias.** Deux campagnes trouvees en une matinee, toutes deux dans des
donnees qu'on avait deja. La priorite est la completude de la table, pas le
raffinement du filtre.

---

## 49. Journal de methode — 27 aout 2026 : neuf nouvelles listes, et une validation croisee

Vincent a releve neuf listes d'abonnements et les a livrees en copier-coller
brut, comme convenu. `outils/extraire_abonnements_brut.py` les traite.

### 49.1 Le format brut, et pourquoi il tient

Un seul fichier, neuf comptes sources a la suite, des commentaires libres, des
noms affiches contenant des emoji et des barres verticales.

Deux pieges evites :

- **Les lignes `@quelquechose` ne sont pas des delimiteurs fiables** : un nom
  affiche peut commencer par `@`, constate avec
  « @lespetitestrouvaillesdeludi ». Ce sont les lignes
  `From <https://www.instagram.com/X/>` qui nomment le compte source sans
  ambiguite.
- **Le controle de non-perte etait faux au premier essai** : il additionnait
  les noms affiches deux fois et annoncait un ecart sur tous les blocs. Corrige,
  les neuf blocs passent.

MESURE : **1 677 nouveaux liens, 2 027 comptes Instagram distincts** contre 538
la veille.

| Compte source | Comptes suivis |
|---|---:|
| @charal_officiel | 332 |
| @savencia_groupe | 254 |
| @legaulois_officiel | 221 |
| **@naturellementflexitariens** | **221** |
| @lifeatdanone | 157 |
| @nestleenfrance | 155 |
| @fleurymichon | 140 |
| **@enmodeactif** | **134** |
| @herta_france | 63 |

### 49.2 Les comptes de campagne se comportent comme des vitrines

C'etait l'hypothese posee avant le releve, et elle etait incertaine : un compte
corporate de multinationale n'a pas de raison de tenir une liste curatee.

**@enmodeactif, la campagne CNIEL cofinancee par l'UE, suit 134 comptes et
c'est une liste de partenaires.** On y trouve :

- **@lestudiodanielle** — deja confirme par une voie totalement independante,
  les descriptions de ses videos (JOURNAL 47.2) ;
- **@grimkujow** — deja dans la liste de surveillance YouTube ;
- **@hervecuisine**, **@sandquetier**, **@marinlle**, **@annedubndidu** — des
  createurs cuisine, sport et course a pied, coherents avec une campagne
  anti-sedentarite.

**La validation croisee est le point important.** Studio Danielle a ete trouve
deux fois, par deux chemins qui n'ont rien en commun : la lecture des
descriptions de ses videos, et la liste d'abonnements du commanditaire. C'est
exactement le type d'independance que la capture-recapture exige
(METHODOLOGIE 9.3), et que le couple SponsorBlock / description n'offrait pas
(JOURNAL 43.2).

### 49.3 Les memes createurs travaillent pour plusieurs interprofessions

**@naturellementflexitariens** (INTERBEV) suit **@menthe_banane**,
**@chateau.leg0** et **@pepites2noisette** — trois des createurs dont INAPORC
publie les recettes (JOURNAL 27.3).

Ce ne sont pas des prestataires d'une filiere : ce sont des createurs que
**plusieurs interprofessions** emploient. Le registre devra donc relier un
createur a plusieurs commanditaires, et l'affichage par commanditaire seul
manquerait ce fait.

### 49.4 Ce que Vincent a note sur les comptes corporate

Ses reponses au classeur, qui valent mesure :

- **Lactalis, Sodiaal, Groupe Bel : aucun compte francais trouve.** Bel n'a
  qu'un compte neo-zelandais, Lactalis des comptes suisse, turc, bresilien et
  americain.
- **Danone** n'a pas de `@danone.france` : le compte trouve est
  `@lifeatdanone`, oriente marque employeur.
- **Made in Viande** n'a pas de compte propre, mais plusieurs comptes
  regionaux d'INTERBEV existent.

Autrement dit, **les grandes marques laitieres francaises communiquent peu en
direct sur Instagram**. Elles passent par les interprofessions et par les
campagnes. C'est coherent avec toute la strategie de la vitrine decrite en
METHODOLOGIE section 2 — et cela renforce la priorite donnee aux comptes de
campagne plutot qu'aux comptes corporate.

### 49.5 Alias reperes par Vincent sur les sites

- **LAIT'FLIX** — serie de videos de divertissement du CNIEL. Le compte
  `@laitflix` figurait deja dans les abonnements du CNIEL sans qu'on sache ce
  que c'etait.
- **L'Amour Boeuf** — serie de videos d'INTERBEV. Le compte `@lamourboeuf`
  etait deja repere, juge « ressemble a un truc de lobby » par Vincent le
  24/08. Confirme.
- **@foiegrasfrancais** — le compte du CIFOG, enfin identifie. L'alias
  « Le Foie Gras » qui a produit 91 faux positifs pourra etre remplace par ce
  pseudo, specifique lui.

---

## 50. Journal de methode — 27 aout 2026 : « CLIPP », et la routine quotidienne

### 50.1 Les 33 nouveaux candidats juges

Vincent a juge les 33 candidats de `A_VERIFIER_2.xlsx`.

| Verdict | Videos |
|---|---:|
| hors sujet | 21 |
| je ne sais pas | 6 |
| **collaboration remuneree** | **4** |
| mention sans collaboration | 2 |

Les quatre vraies sont les videos **Studio Danielle**, toutes CNIEL, toutes
avec mention explicite : « en partenariat avec Les Produits Laitiers et leur
campagne En Mode Actif cofinancee par l'UE ».

**La regle D fait 80 % de precision et 100 % de rappel sur ce lot** : elle
retient 5 candidats dont les 4 vrais, et n'en perd aucun. Meilleur que sur les
271 (77 % / 87 %) — mais l'echantillon ne compte que 4 vrais cas, tous CNIEL.
Elle reste non testee sur les autres interprofessions.

### 50.2 « CLIPP » : 31 candidats, zero vrai

Sur les 21 « hors sujet », l'ecrasante majorite venaient de l'alias **CLIPP**
(interprofession du lapin). En cumulant les deux lots : **31 candidats, aucun
vrai.**

La cause, verifiee :

- « no**clipp**ant » contient litteralement la chaine cherchee ;
- l'appariement **supprime les espaces**, donc « Clip para » devient
  « clippara », qui contient « clipp ».

Un sigle de cinq lettres n'est pas exploitable par appariement sur forme
aplatie. Vincent n'a d'ailleurs trouve **aucun compte vitrine** pour cette
interprofession.

### 50.3 Le correctif, et une erreur en le faisant

Premier jet : ecarter les ENTITES trop courtes — CLIPP, CNPO, ANVOL, CIFOG.
**Faux.** Cela supprimait aussi les cas trouves par « Volaille Francaise »,
un alias de 17 caracteres parfaitement specifique, simplement parce que son
entite s'appelle ANVOL.

Corrige : **on ecarte l'ALIAS, jamais l'entite.** Un alias doit faire au moins
8 caracteres, et une courte liste d'alias generiques connus est exclue
explicitement (« Le Foie Gras », 12 caracteres mais qui designe l'aliment).

MESURE apres correction, contre les 288 jugements de Vincent :

| | Avant | Apres |
|---|---:|---:|
| Preuves fortes | 304 | **175** |
| Vraies collaborations conservees | 71 | **71** |
| Precision | 23 % | **41 %** |
| Rappel | 100 % | **100 %** |

**La moitie du bruit disparait sans perdre un seul vrai cas.** Et la regle D
s'applique ensuite par-dessus.

### 50.4 La routine quotidienne

`outils/routine_quotidienne.py` enchaine cinq etapes : moisson YouTube,
croisement TikTok → YouTube, moisson TikTok, consolidation du registre, tri des
detections.

Trois principes :

1. **Les etapes qui consomment du quota d'abord**, les etapes locales ensuite.
   Une journee ou le quota est epuise produit quand meme un registre a jour.
2. **Chaque etape est isolee** : si l'une echoue, les suivantes tournent.
3. **Un journal lisible par jour** dans `recherche/routine/`, qui dit ce qui a
   tourne et ce que ca a produit — sans les milliers de lignes d'avancement.

Elle ne juge rien. Elle prepare le materiau ; l'analyse reste une session
humaine. C'est la repartition qui manquait : la collecte brulait du budget de
conversation a attendre des telechargements.

### 50.5 Pourquoi rien n'a repris cette nuit — hypothese corrigee

J'avais avance que la session s'etait fermee. **Vincent a corrige : elle est
restee ouverte, et le reglage « Continue automatically at usage limit » etait
actif.**

`SUPPOSE`, non verifie : ce reglage reprend probablement un **tour
interrompu**, pas une session au repos. Le dernier tour s'etait termine
proprement et aucune tache de fond ne tournait — il n'y avait rien a
reprendre.

Remede pratique, quel que soit le mecanisme : **laisser une tache de fond en
cours avant de partir.** Sa fin declenche un reveil. Et desormais la routine
planifiee rend la question secondaire.

---

## 51. Journal de methode — 27 aout 2026 : les chaines YouTube des lobbies

### 51.1 Vincent trouve LAIT'FLIX

En parcourant produits-laitiers.com, Vincent repere **LAIT'FLIX**, une serie de
videos de divertissement du CNIEL, avec des playlists nommees :

- « ON DEVIENT FERMIER 48H DANS LES MONTAGNES **Feat Inoxtag** »
- « **Mister V** : les copains au lait »
- « **Billy et Amine** decouvrent les specialites de nos regions »
- « La ferme des celebrites », « La Carotte d'Avner », « Morgane decouvre les AOP »

Sa reaction dit l'enjeu : « Certaines de ces series sont des videos que je
connaissais et qui ont ete beaucoup vues, **et je ne savais pas qu'elles
avaient ete financees par le lobby du lait**. »

Il identifie au passage les chaines YouTube officielles des interprofessions,
que le projet ignorait completement.

### 51.2 Une source d'un autre statut

Toutes les methodes precedentes partent du contenu d'un createur et
**inferent** qu'un lobby l'a paye. Ici **c'est le lobby qui publie**. Un
createur nomme dans le titre d'une video du CNIEL n'est pas une hypothese :
c'est le commanditaire qui l'annonce.

`outils/moissonner_chaines_lobbies.py`. MESURE — 20 unites de quota :

| Chaine du lobby | Abonnes | Videos | Nommant un createur |
|---|---:|---:|---:|
| Produits Laitiers (CNIEL) | 101 000 | 132 | 98 |
| Aimez la viande (INTERBEV) | 79 500 | 292 | 163 |
| LE FOIE GRAS (CIFOG) | 788 | 197 | 101 |
| Volaille Francaise (ANVOL) | 236 | 40 | 36 |
| Naturellement Flexitariens | 379 | 39 | 14 |
| INTERBEV Nouvelle-Aquitaine | 32 | 37 | 17 |

**429 videos nomment un createur ; 285 createurs distincts.**

### 51.3 Les createurs a forte audience

> **⚠ CE TABLEAU EST FAUX. Corrige le 27/08 — voir l'entree 58.**
> Il a ete produit par un rapprochement defectueux qui attribuait un titre au
> premier compte revendiquant une forme de six caracteres. « Norman » etait
> « e-Boucherie **norman**de » ; Inoxtag et Doigby ne resistent pas a la
> correction. **Mister V, lui, est confirme.** Le tableau est conserve tel
> quel : le journal enregistre ce qui a ete cru, pas seulement ce qui est vrai.

| Createur | Abonnes | Videos | Commanditaire |
|---|---:|---:|---|
| **Norman** | **11 200 000** | 3 | **CNIEL + INTERBEV** |
| **Inoxtag** | 9 470 000 | 1 | CNIEL |
| **Mister V** | 6 530 000 | **8** | CNIEL |
| L'EQUIPE | 2 040 000 | 2 | INTERBEV |
| Doigby | 1 390 000 | 1 | CNIEL |
| Kameto | 496 000 | 1 | CNIEL |
| LeStream | 206 000 | 1 | INTERBEV |
| Legend | 179 000 | 1 | CIFOG |
| YassEncore | 129 000 | 1 | CNIEL |
| MYRIAMANHATTAN | 128 000 | 4 | CNIEL |
| Charlot | 78 000 | 3 | CNIEL |

**Norman — le plus gros createur de nos donnees — apparait dans des videos du
CNIEL ET d'INTERBEV.** Les huit videos de Mister V correspondent a la serie
« les copains au lait » reperee par Vincent.

> **Faux pour Norman** (voir 58) : la reconnaissance portait sur
> « e-Boucherie normande ». La phrase sur Mister V, elle, tient.

### 51.4 Ce que cette source etablit, et ce qu'elle n'etablit pas

**Elle etablit la collaboration** : le commanditaire publie la video et nomme
le createur. Aucune inference.

**Elle n'etablit pas la remuneration.** Apparaitre dans une video du CNIEL peut
resulter d'un contrat, d'un partenariat de tournage, ou d'une invitation. C'est
exactement le champ `degre de certitude` de METHODOLOGIE section 1 : « lien
commercial documente », pas « remuneration confirmee ».

**Et elle ne dit rien du contenu diffuse par le createur sur SA chaine.** Une
video publiee par le CNIEL avec Mister V ne prouve pas que Mister V ait publie
quelque chose de son cote. Les deux faits sont distincts et tous deux
interessants.

### 51.5 Pourquoi personne n'y avait pense

Le projet cherchait les lobbies dans le contenu des createurs, et les
createurs dans les sites des lobbies (JOURNAL 24). **Personne n'avait regarde
les chaines YouTube des lobbies** — alors que c'est la source la plus directe
et la moins chere : 20 unites de quota pour 429 videos exploitables.

Elle a ete trouvee non par une idee de methode, mais parce que Vincent
parcourait un site a la main.

---

## 52. Journal de methode — 27 aout 2026 : 488 chaines de plus, et une distinction a mesurer

### 52.1 Le croisement

Les 2 027 comptes Instagram releves par Vincent, essayes un par un contre
YouTube. MESURE : **488 chaines trouvees**, 1 489 unites de quota, 0 erreur.

Un defaut corrige au passage : l'extracteur de listes brutes n'attribuait
**aucune entite** aux comptes releves. Le registre savait qu'un compte etait
suivi, sans savoir par qui. Une table `ENTITES` relie desormais chaque compte
vitrine a son commanditaire, et les 1 677 lignes deja produites ont ete
completees.

### 52.2 Chaines YouTube derivees, par commanditaire

| Commanditaire | Chaines |
|---|---:|
| CNIEL | 66 |
| INTERBEV — campagne Naturellement Flexitariens | 62 |
| Bigard / Charal | 59 |
| Danone | 56 |
| INTERBEV | 53 |
| LDC | 50 |
| Nestle France, Savencia | 44 |
| Fleury Michon | 38 |
| INAPORC | 35 |
| **CNIEL — campagne En Mode Actif** | 33 |
| ANVOL | 15 |

### 52.3 Une distinction visible, a confirmer par la mesure

`SUPPOSE`, non encore mesure : **les comptes de campagne et les comptes
corporate ne se valent pas comme semence.**

Ce que montrent les abonnements des campagnes :

- **@enmodeactif** (CNIEL) suit Pierre Croce (3,79 M), FabienOlicard (2,33 M),
  Herve Cuisine (1,6 M) — des createurs francais generalistes.
- **@naturellementflexitariens** (INTERBEV) suit FastGoodCuisine (8,77 M),
  Juju Fitcats (3,18 M), Herve Cuisine.

Ce que montrent les comptes corporate :

- **Danone** suit Olympic Games (16,6 M), Wimbledon (2,64 M), Konbini.
- **Nestle France** suit Minecraft (22,5 M), Amazon Prime Video, CANAL+.
- **Bigard** suit Zach Choi (33,7 M, americain), Tasty (21,2 M, americain),
  Guga Foods (americain).

Les premiers ressemblent a des listes de partenaires ; les seconds a des
abonnements d'interet general et de sponsoring sportif international.

**Mais ce n'est qu'une impression de lecture.** La mesure qui tranchera est
celle deja utilisee le 26/08 : combien de preuves fortes par chaine derivee,
semence par semence. Elle demande d'avoir moissonne ces 488 chaines, ce qui
coutera environ 4 500 unites de quota.

Prediction posee **avant** la mesure, pour qu'elle soit refutable : les
semences de campagne devraient produire au moins deux fois plus de preuves
fortes par chaine que les semences corporate.

### 52.4 Etat du registre

`cartographie/COMPTES.xlsx` : **6 875 comptes** — 2 620 YouTube, 2 187 TikTok,
2 039 Instagram, 29 indetermines. **39 % avec audience connue.**

Depuis le 24 aout, la population de surveillance est passee de 27 chaines
YouTube nommees a la main a **2 620 derivees des sources**.

---

## 53. Journal de methode — 27 aout 2026 : la transcription voit ce que la description tait

### 53.1 Une premiere mesure qui ne pouvait pas repondre

`outils/mesurer_transcriptions.py`, sur les 175 videos jugees par Vincent :

| Signal | Retenus | Vrais | Precision | Rappel |
|---|---:|---:|---:|---:|
| Transcription | 37 | 30 | **81 %** | 49 % |
| Description | 78 | 61 | 78 % | 100 % |

Vraies collaborations vues par la transcription **seule : zero**.

**Ce zero ne prouve rien**, et la limite avait ete inscrite avant la mesure :
l'echantillon est fait de videos trouvees PAR la description. Une
collaboration annoncee uniquement a l'oral n'avait aucune chance d'y figurer.
Le protocole mesurait une tautologie.

Ce qui reste informatif : la transcription est **plus precise** que la
description, 81 % contre 78 %.

### 53.2 L'experience correcte

`outils/experience_transcription.py`. On prend des videos **sans aucun signal
en description**, sur six chaines dont une collaboration filiere est etablie —
Inoxtag, Inoxtag 2.0, Michou, Mister V, Valouzz, Norman.

MESURE — 40 videos temoins, 37 transcriptions obtenues, 12 unites de quota.

**Une video sur 37 contient une mention de la filiere que la description ne
porte pas.**

### 53.3 Le cas

**Inoxtag 2.0**, 3 140 000 abonnes, « On a dormi au sommet d'une montagne ! ».
Description : aucun signal. Transcription automatique, verbatim :

> « ... comme d'habitude **les produits laitiers qui nous accompagnent
> partout**, ca fait plaisir. **Tomme de Savoie**, mon fromage prefere, on
> change pas des bonnes habitudes, on va gouter le potentiel de ce fromage... »

Deux choses en une phrase :

1. **« comme d'habitude »** — le createur signale une relation **suivie**, pas
   une operation isolee.
2. **« Tomme de Savoie »** — precisement le produit de la collaboration
   Inoxtag x Cniel documentee par la presse, et que le projet cherchait depuis
   le 24 aout sans la retrouver (JOURNAL 16.5 : le flux RSS ne remontait pas
   assez loin).

**Aucun autre signal du projet ne voyait cette video.** Ni la description, ni
la case de declaration, ni SponsorBlock.

### 53.4 Ce que ca decide

**La transcription n'est pas redondante.** Elle atteint un registre que rien
d'autre n'atteint : la mention orale, non declaree, non ecrite.

Et c'est le cas le plus interessant pour le plaidoyer — une collaboration que
le createur mentionne en passant, sans mention legale, sur une chaine de trois
millions d'abonnes.

Cout : plusieurs secondes par video, sans quota d'API. Sur 2 600 chaines et
500 videos chacune, c'est hors de portee. **La bonne strategie est donc de
l'appliquer en second rideau** : sur les chaines dont une collaboration est
deja etablie, pour trouver les autres videos de la meme relation.

Le cas ci-dessus l'illustre : c'est parce qu'Inoxtag etait deja identifie
qu'on a regarde ses autres videos, et qu'on a trouve « comme d'habitude ».

### 53.5 Reserves

- **Une video sur 37 n'est pas une frequence.** Les chaines ont ete choisies
  la ou il y avait le plus de chances de trouver. Un tirage aleatoire donnerait
  un tout autre chiffre, probablement bien plus bas.
- **La mention orale n'etablit pas la remuneration.** « Qui nous accompagnent »
  est ambigu : partenariat, dotation en produits, ou simple habitude.
  `degre de certitude` : lien commercial documente.
- **Mon extrait etait faux au premier affichage** : le script montrait le
  passage du premier terme de la table, pas celui qui avait declenche. Verifie
  a la main avant d'ecrire cette entree — sans quoi j'aurais rapporte un
  resultat en citant un texte sans rapport.

---

## 55. Journal de methode — 27 aout 2026 : l'outil accusait la mauvaise personne

### 55.1 Ce qui a ete trouve

`moissonner_chaines_lobbies.py` rapportait, en tete de liste :

| Createur | Videos | Commanditaire |
|---|---:|---|
| UC8tyTUppXI6PhWeU6CKOBEQ | 52 | CNIEL, INTERBEV |
| UCOkKpH6tIRaNKPsNB7a3r3w | 51 | CNIEL |
| volaillefrancaise | 36 | ANVOL |

Trois defauts visibles d'emblee : des identifiants bruts illisibles, et
`volaillefrancaise` qui est **la chaine ANVOL elle-meme** se reconnaissant
dans ses propres titres.

En resolvant les identifiants, un quatrieme, invisible et bien plus grave :

- `UCOkKpH6tIRaNKPsNB7a3r3w` = **Produits Laitiers**, la chaine du CNIEL.
- `UC8tyTUppXI6PhWeU6CKOBEQ` = **@salondelagriculture, 3 abonnes**.

Ce dernier n'a aucune raison d'apparaitre 52 fois. En cherchant quelle forme
declenchait, sur le titre « CHAUD! - Episode final (avec Morgan VS, GMK et
Ragnar Le Breton) » :

```
'morganvs' -> renvoie morgan.niquet  | nom reel : Morgan VS
'morgan'   -> renvoie morganabbou    | nom reel : Morgan
```

### 55.2 Le mecanisme

`comptes_connus()` construisait un dictionnaire `forme aplatie -> identifiant`,
en premier arrive premier servi :

```python
out.setdefault(a, l.get("identifiant", cle))   # 5 caracteres minimum
...
if len(a) >= 6 and a in plat:                  # 6 pour declencher
```

Deux consequences qui se composent :

1. Six caracteres suffisent, donc un **prenom** declenche — « morgan ».
2. La valeur rendue est l'identifiant du **premier compte** ayant revendique
   cette forme, qui n'est pas celui qu'on vient de lire.

Une video ou INTERBEV nomme « Morgan VS » etait donc versee au dossier de
`morganabbou`. **Ce n'est pas du bruit : c'est une mise en cause de la mauvaise
personne**, dans la source la plus autoritaire du projet — celle ou l'on ecrit
« le commanditaire lui-meme le nomme ».

C'est exactement le risque que la section 10 de METHODOLOGIE decrit, arrive par
un chemin qu'elle ne prevoyait pas : non pas un faux positif sur l'existence
d'une collaboration, mais **une vraie collaboration attribuee a autrui**.

### 55.3 Ce qui a ete corrige

1. **Huit caracteres minimum**, la regle deja retenue pour les alias le matin
   meme. Un prenom ne declenche plus.
2. **Toute forme revendiquee par plusieurs comptes est jetee.** C'est la
   correction qui compte : la longueur seule n'aurait pas empeche une collision
   entre deux comptes longs et homonymes.
3. **Le nom lisible est affiche**, plus jamais l'identifiant seul, et une
   colonne « reconnu par » donne **la chaine exacte qui a declenche**. Un humain
   peut contredire l'outil sans lire le code.
4. Les comptes des lobbies et les medias sont exclus en amont.

MESURE — **2 357 formes ecartees comme partagees, sur 7 920. Soit 30 % de la
table.** Ce n'etait pas un cas limite.

Apres correction, la tete de liste devient : Pierre Chomet (31 videos, CIFOG et
CNIEL), Morgan VS (12, CNIEL), L'Amour Boeuf (10, INTERBEV), Fabrice Mignot
(6, INTERBEV), Mister V (3, CNIEL), Brigitte Lecordier (3, CNIEL).

### 55.4 Ce qui reste ouvert, et qui tranchera

Il reste deux voies de reconnaissance, dont on ignore la valeur respective :

- **compte connu** — 42 noms. A l'oeil : des personnes.
- **motif dans le titre** (« feat X », « avec X ») — 176 noms. A l'oeil : des
  noms de series, « Interview Metiers », « Milk Check », « Generation XYZ ».

**« A l'oeil » n'est pas une mesure**, et la regle 13.1 interdit de trancher
la-dessus. `cartographie/CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx` pose la
question a Vincent, une seule colonne verte, les lignes triees par valeur avec
mention explicite qu'il peut s'arreter apres la soixantieme.

Ses reponses diront s'il faut garder la seconde voie, la durcir ou l'abandonner.

### 55.5 La lecon a retenir

Les trois defauts visibles — identifiants bruts, lobby qui se reconnait, noms
de series — etaient **cosmetiques**. Celui qui comptait ne se voyait pas : il
fallait resoudre un identifiant a 3 abonnes pour le trouver.

Regle : **quand une sortie contient un identifiant opaque, le resoudre avant de
lire le reste.** Un identifiant qu'on ne peut pas lire est un endroit ou une
erreur peut se cacher indefiniment.

---

## 56. Journal de methode — 27 aout 2026 : la liste qui devait retirer du bruit retirait le signal

### 56.1 Ce qu'on voulait savoir

La regle D est mesuree a 83 % de precision, et c'est sur ce chiffre que repose
le filtrage du projet. Mais elle contient une liste ecrite a la main :

```python
GENERIQUES = ["le foie gras", "produits laitiers", "le porc francais",
              "volaille francaise", "oeufs de france", "la viande", ...]
```

Chaque terme y a ete ajoute **apres** avoir vu les cas de l'interprofession
correspondante. Les 83 % sont donc mesures sur ce qui a servi a construire la
regle. Ce chiffre ne dit rien de ce qui arrivera sur un commanditaire
decouvert demain — et METHODOLOGIE 14 exige que l'outil re-derive.

### 56.2 Le protocole

`outils/generaliser_regle_d.py`. Pour chaque interprofession E : retirer de la
liste les termes qui designent E, puis evaluer la regle D **sur les seuls cas
de E**. C'est la situation d'une entite qu'on n'a jamais vue.

**Prediction inscrite avant la mesure :** le rappel ne bougera pas, la
precision tombera, et l'ampleur de la chute dira si la liste est indispensable.

### 56.3 MESURE

| Entite | Cas | Vrais | Terme retire | Precision avec / sans | Rappel avec / sans |
|---|---:|---:|---|---:|---:|
| CNIEL | 128 | 57 | — | 85 % / 85 % | 100 % / 100 % |
| INTERBEV | 31 | 7 | — | 33 % / 33 % | 14 % / 14 % |
| **INAPORC** | 7 | 2 | le porc francais | **0 % / 100 %** | **0 % / 100 %** |
| ANVOL | 2 | 1 | volaille francaise | 0 % / 0 % | 0 % / 0 % |

### 56.4 Les deux moities de la prediction sont fausses

**Le rappel a bouge**, de 0 a 100 % sur INAPORC. Et le raisonnement qui
annoncait le contraire etait incoherent avec lui-meme : `est_generique` ne fait
qu'ECARTER des cas, donc en retirer un terme ne peut qu'en garder plus, donc le
rappel ne peut que monter. Il suffisait de relire la phrase pour voir qu'elle
se contredisait.

**La precision n'est pas tombee, elle est montee**, de 0 a 100 % sur INAPORC.

Le sens de la mesure est donc l'inverse de celui qu'on cherchait : ce n'est pas
que la regle D generalise mal faute d'avoir vu l'entite. **Elle generalise
mieux quand on ne lui a rien appris de l'entite.**

L'explication tient en une ligne : « Le Porc Francais » n'est pas une categorie
alimentaire qui traine dans une description, c'est la **signature de campagne
d'INAPORC**. La liste, ecrite en regardant le CNIEL — ou « produits laitiers »
est effectivement un mot courant — retire ailleurs le seul vrai cas.

C'est la meme erreur que celle du 26/08 sur `est_generique` par sous-chaine
(JOURNAL 38), a un niveau au-dessus : ce n'est plus la comparaison qui est
fautive, c'est **l'idee meme qu'un terme puisse etre declare generique dans
l'absolu**. Il l'est relativement a une entite.

### 56.5 Un rapport qui affirmait le contraire de ses chiffres

La premiere version du script ecrivait, sous le tableau :

> Chute de precision moyenne : **-50 points**. Pire cas : **ANVOL**, de 0 % a
> 0 %. Autrement dit, la regle D perd cette part de precision.

Trois faussetes en trois lignes. Une chute de -50 points est un gain. « Pire
cas » designait l'entite qui n'avait pas bouge, parce que le `max` portait sur
une difference dont le signe etait suppose. Et la phrase de conclusion etait
ecrite dans le gabarit, quel que soit le resultat.

**Un rapport dont la conclusion est ecrite avant la mesure ne mesure rien.**
Le script lit desormais le signe au lieu de le supposer, et bifurque entre
trois conclusions selon ce qu'il trouve — dont « le resultat est mixte, cela ne
tranche rien ».

### 56.6 Ce qui reste a trancher

Deux voies, et c'est a Vincent :

- **restreindre `est_generique` au CNIEL**, la seule entite ou la liste aide ;
- **l'abandonner pour la regle F**, qui exige un `@pseudo` ecrit tel quel et ne
  depend d'aucune liste manuelle — donc qui re-derive vraiment.

### 56.7 Reserve

Sept cas INAPORC dont deux vrais, deux cas ANVOL dont un vrai. **Ces
pourcentages ne sont pas des taux** : 0 % et 100 % decrivent ici deux videos.
Le tableau montre un SENS, pas des valeurs, et le sens ne sera confirme qu'avec
plus de cas juges hors CNIEL.

---

## 57. Journal de methode — 27 aout 2026 : le quatrieme signal, et une contamination cherchee puis non trouvee

### 57.1 La case de declaration, enfin mesuree

`outils/mesurer_declaration.py`. 175 videos jugees, **175 pages lues, zero
echec** — le rythme d'une page toutes les 1,5 seconde suffit a eviter le
HTTP 429 qui avait fait derailler la journee du 24/08.

MESURE :

| Signal | Retenus | Vrais | Precision | Rappel |
|---|---:|---:|---:|---:|
| **Case de declaration** | 34 | 31 | **91 %** | **44 %** |

Les quatre signaux YouTube sont donc tous mesures :

| Signal | Precision | Rappel |
|---|---:|---:|
| Transcription | 81 % | 49 % |
| Description | 78 % | 100 % |
| **Case de declaration** | **91 %** | **44 %** |
| SponsorBlock | 69 % | 13 % |

La prediction inscrite avant la mesure tient : precision la plus haute des
quatre, rappel faible.

### 57.2 Le chiffre qui justifie le projet

**40 vraies collaborations sur 71 ne sont pas declarees. 56 %.**

Un outil qui se contenterait de lire la case officielle en manquerait plus de
la moitie. C'est la reponse chiffree a la question « a quoi sert ce projet ».

### 57.3 Ce que la case ne dit pas

Trois videos declarees ont ete jugees hors sujet. En les regardant :

- **Inoxtag, « KAIZEN : 1 an pour gravir l'Everest »** ;
- **Madrange, « Mes Knacks Madrange 2019 »** — chaine de marque, pas un
  createur ;
- **Poisson Fecond, « 1 an a boire que du lait »**.

La case dit « cette video contient une communication commerciale ». Elle ne dit
**pas par qui**. Une video peut etre sponsorisee par un VPN et citer les
produits laitiers pour une tout autre raison.

**Consequence pour METHODOLOGIE 1 :** la case seule ne peut pas porter le degre
« remuneration confirmee » pour un commanditaire donne. Elle etablit qu'un
partenariat paye existe dans la video ; c'est la conjonction avec l'alias qui
designe lequel.

En sens inverse, la conjonction est forte. Quatre videos d'Inoxtag portent des
formulations sans ambiguite dans leur description :

> « Merci a mes partenaires air up, Nike, Deezer, Fitness Park, Erborian,
> **Les Produits Laitiers**, Orange, et Therm-a-Rest »
>
> « **Merci aux Produits Laitiers d'etre le partenaire de cette video** »
>
> « **Merci aux Produits Laitiers pour nous avoir finance le voyage !** »

### 57.4 Une contamination cherchee — et non trouvee

En instruisant le point precedent, un defaut est apparu : la moisson ne garde
que les **900 premiers caracteres** de chaque description.

MESURE — sur 362 detections nettoyees : **153, soit 42 %, ont leur alias
declencheur au-dela de la coupure.** Pour ces cas, le texte enregistre ne
contient pas la preuve.

Hypothese immediate, et inquietante : Vincent aurait juge 42 % des cas sans
voir ce qui les avait declenches, donc les aurait rabattus sur « hors sujet »,
donc les 216 « hors sujet » du jeu de reference seraient contamines — et avec
eux toutes les precisions mesurees depuis, dont les 83 % de la regle D.

MESURE :

| Description | Jugees | Collaboration remuneree | Hors sujet |
|---|---:|---:|---:|
| entiere | 126 | 41 (**33 %**) | 83 |
| **coupee** | 49 | 30 (**61 %**) | 18 |

**L'hypothese est refutee, et dans le sens inverse.** Sur les descriptions
coupees, le taux de vrais est presque le double.

L'explication est dans le code : `generer_classeur_verification.py` detecte
deja le cas et affiche, a la place d'un extrait trompeur :

> [La mention est au-dela de ce qui a ete enregistre. Ouvrir la video pour lire
> la description complete.]

Vincent est donc alle voir les videos, et les a jugees sur piece. Le garde-fou
pose apres son reproche du 25/08 — « je ne vois pas le lien avec les
influenceurs pour la plupart » — a fait exactement son travail.

**Le jeu de reference n'est pas contamine.** C'est une bonne nouvelle qui ne
valait que parce qu'on a cherche a la contredire.

### 57.5 Corrige quand meme

Le defaut de donnees reste : 42 % des extraits demandent un aller-retour vers
YouTube. La moisson taille desormais l'extrait **dans le texte complet**, avant
de tronquer, et le range dans une colonne `extrait_declencheur`. Le classeur
l'utilise quand elle existe et retombe sur l'ancien comportement sinon.

L'export prend l'**union** des colonnes : le fichier de reprise melange
maintenant des lignes ecrites avant et apres la correction, et une ligne
ancienne doit laisser la case vide plutot que faire echouer l'export.

Les 22 000 detections deja moissonnees gardent l'avertissement : leur texte
complet n'a pas ete conserve, et le re-moissonner couterait un quota qu'on a
mieux a faire de depenser.

---

## 58. Journal de methode — 27 aout 2026 : ce que le defaut avait deja fait croire

### 58.1 Pourquoi cette entree existe

L'entree 55 decrit le defaut de rapprochement de
`moissonner_chaines_lobbies.py` : six caracteres suffisaient a declencher, et
l'identifiant rendu etait celui du **premier compte** ayant revendique la
forme.

Corriger le code ne suffit pas. Ce defaut avait deja produit des affirmations,
et ces affirmations avaient deja ete ecrites dans les documents que lisent les
sessions suivantes. Il fallait aller les chercher.

### 58.2 MESURE — ce qui survit a la correction

En relancant l'outil corrige et en cherchant les noms mis en avant :

| Nom annonce le 27/08 au matin | Apres correction |
|---|---|
| **Norman**, 11,2 M, CNIEL + INTERBEV | **N'EXISTE PAS.** La reconnaissance portait sur « e-Boucherie **norman**de », une boucherie citee dans une video INTERBEV sur des eleveurs du Label Rouge. |
| **Inoxtag**, 9,47 M, CNIEL | **Absent.** |
| Squeezie | **Absent.** |
| Michou | **Absent.** |
| **Mister V**, 6,53 M, CNIEL, 8 videos | **CONFIRME.** « PETIT CAFE BRIOCHE 2 AVEC MISTER V, AMINE, CEDRIC DOUMBE... », publie par le CNIEL. |

Deux des trois noms mis en avant etaient des artefacts. Le troisieme tient.

### 58.3 Ce qui avait ete ecrit, et ou

- **`JOURNAL.md` 51.3**, un tableau « les createurs a forte audience » ouvert
  par « Norman — le plus gros createur de nos donnees ».
- **`ETAT.md` section 6**, « prochaine session — a faire en premier », donc la
  premiere chose que lit une session neuve.

Le journal etant en ajout seul, le tableau de 51.3 est **conserve tel quel**,
avec un renvoi vers cette entree. Un journal qui se reecrit ne sert plus a
rien : il doit garder ce qui a ete cru, sinon on ne peut plus comprendre
pourquoi telle decision a ete prise. `ETAT.md`, lui, decrit l'etat present —
il a ete corrige.

### 58.4 La lecon, qui n'est pas celle du code

L'entree 55 concluait : « quand une sortie contient un identifiant opaque, le
resoudre avant de lire le reste ». C'est vrai mais insuffisant.

Le vrai enchainement est celui-ci : un outil produit un chiffre, le chiffre
entre dans un rapport, le rapport entre dans `ETAT.md`, et `ETAT.md` devient ce
que la session suivante tient pour acquis. **A la troisieme etape, plus
personne ne peut remonter a l'outil.**

D'ou la regle : **corriger un outil oblige a rouvrir ce qu'il a fait ecrire.**
Pas seulement le code, pas seulement le dernier rapport — tous les documents ou
son resultat a ete recopie.

Et une raison de plus de ne jamais mettre un nom de personne dans un document
sans la chaine qui y mene. « Norman, 11,2 M, CNIEL + INTERBEV » ne portait
aucune trace de ce qui l'avait produit ; il a fallu relancer l'outil corrige
pour decouvrir qu'il s'agissait d'une boucherie. La colonne « reconnu par »,
ajoutee le 27/08, existe pour ca.

### 58.5 Ce qui reste vrai de l'entree 51

La source elle-meme est intacte, et c'est toujours la meilleure du projet : les
interprofessions publient des videos ou elles nomment les createurs. Les
comptages de videos par chaine de lobby (132 pour le CNIEL, 292 pour INTERBEV,
197 pour le CIFOG) n'ont jamais dependu du rapprochement fautif.

Ce qui a change, c'est le nombre de createurs : **429 videos et 285 noms**
annonces le matin deviennent **218 noms** apres correction, dont 42 seulement
par la voie fiable. Et 176 des 218 restent a trancher — ce sont peut-etre des
noms de series.

---

## 59. Journal de methode — 27 aout 2026 : le second rideau produit, et le catalogue est complet

### 59.1 La moisson est terminee

MESURE — **2 660 chaines sur 2 660. 307 191 videos examinees.** C'est la
premiere fois que le catalogue complet du registre est passe en revue.

25 411 videos portent un signal commercial, 7 139 citent la filiere, et apres
nettoyage il reste **257 preuves fortes**, dont **82 jamais jugees** —
`A_VERIFIER_3.xlsx`.

La moisson a ete interrompue **cinq fois** dans la journee : une fois par une
`OSError` sur l'ecriture (entree 54), quatre fois par l'environnement qui a tue
les taches de fond. **Aucune n'a rien coute** : la reprise a chaque fois
retrouve son point exact. C'etait le but de la correction du matin, verifie
cinq fois plutot qu'une.

Note pratique pour une session suivante : quand les taches de fond sont tuees,
lancer au **premier plan par tranches** de moins de dix minutes fonctionne. Les
503 dernieres chaines sont passees comme ca.

### 59.2 Le second rideau

Strategie decidee le matin meme (entree 53.4) : ne pas transcrire au hasard,
transcrire les chaines ou une collaboration est **deja confirmee**.

MESURE — 11 chaines, 260 videos **sans aucun signal en description**,
232 transcriptions obtenues, 31 unites de quota. **5 videos citent la filiere.**

Quatre concernent Inoxtag et le CNIEL :

| Date | Ce qui est dit a l'oral | Lecture |
|---|---|---|
| 12/01/2024 | « parce que **j'etais en tournage pour les produits laitiers**, je suis alle faire du fromage » | **Aveu explicite d'un tournage commande.** |
| 23/02/2025 | « demain je serai au salon de l'agriculture […] **je serai sur le stand des produits laitiers** » | Presence sur le stand du commanditaire. |
| 20/05/2023 | « **Adrien des Produits Laitiers** » — au salon | Relation de travail nommee. |
| 13/01/2024 | « produits laitiers **sont nos amis pour la vie** » | Le slogan du CNIEL, cite dans du bavardage. Ambigu : blague ou placement. |

Et un faux positif : **Michou**, « vous lui avez offert un beau petit **foie
gras** » — un cadeau de pot de depart, le CIFOG n'a rien a y voir.

**Aucune de ces cinq videos n'a le moindre signal dans sa description.** Le
tournage du 12/01/2024 en particulier : rien, nulle part, sauf a l'oral.

### 59.3 Ce que ca etablit

La strategie du second rideau fonctionne, et le rendement le justifie : 4 liens
reels pour 232 transcriptions, sur des videos que **rien d'autre ne voyait**.

Elle confirme aussi ce que la phrase « comme d'habitude » laissait entendre
(entree 53.3) : **la relation Inoxtag x CNIEL est suivie, pas ponctuelle** —
2023, 2024 et 2025, avec un tournage, un stand et un salon.

Reserve, qui vaut pour tout ce paragraphe : une mention orale n'etablit pas la
remuneration. « J'etais en tournage pour les produits laitiers » est ce qui
s'en approche le plus — on ne tourne pas gratuitement pour une interprofession
— mais le degre reste **lien commercial documente**, pas plus.

### 59.4 Deux defauts corriges en chemin

**L'extrait pointait encore au mauvais endroit.** Troisieme fois dans la
journee. La cause est toujours la meme : `aplatir` supprime accents, espaces et
ponctuation, donc une position dans le texte aplati ne designe pas la meme
chose dans le texte d'origine, et l'ecart grandit a mesure qu'on avance.

`aplatir_avec_index` rend desormais les deux, et la conversion est faite avant
de couper. C'est la meme fonction que celle ajoutee a `moissonner_videos.py` le
matin — elle aurait du etre partagee des le debut.

**Une correspondance a cheval sur un mot.** « je te ramene du charbon et de
**la viande frerot** » aplati devient « laviandefrerot », qui contient l'alias
`laviandefr`. INTERBEV se retrouvait credite d'une partie de Minecraft.

Le texte aplati a perdu les espaces, donc la coupure n'y est pas visible. Mais
l'index rend les positions d'origine : il suffit de regarder le caractere qui
suit la correspondance **dans le texte vrai**. S'il est alphanumerique, la
correspondance mord sur le mot suivant.

MESURE — le garde-fou retire exactement ce cas et aucun autre : 6 detections
deviennent 5.

C'est la troisieme fois que l'aplatissement fabrique un faux positif — apres
« noclippant » qui contenait « clipp » et « Clip para » devenu « clippara »
(entree 45). **La regle des huit caracteres ne suffit pas** : `laviandefr` en
fait dix. C'est la frontiere de mot qui manquait.

---

## 60. Journal de methode — 27 aout 2026 : l'aplatissement, mesure et borne

### 60.1 Trois fois le meme mecanisme

Le projet apparie sur du texte **aplati** — sans accents, sans espaces, sans
ponctuation. C'est indispensable : « Les Produits Laitiers »,
« lesproduitslaitiers » et « @LesProduits-Laitiers » doivent se reconnaitre.

Mais l'aplatissement colle les mots voisins et fabrique des chaines absentes du
texte reel. Trois faux positifs avaient ete trouves un par un :

    « no clippant »   -> « noclippant »   contient « clipp »        (entree 45)
    « Clip para »     -> « clippara »     contient « clipp »        (entree 45)
    « la viande frerot » -> « laviandefrerot » contient « laviandefr » (entree 59)

Trois anecdotes ne disent pas l'ampleur. Cette entree la mesure.

### 60.2 La parade qui ne marchait pas

La reponse retenue le 27/08 au matin etait une **longueur minimale de huit
caracteres**. Elle n'attrape pas `laviandefr`, qui en fait dix. Elle ecarte du
bruit sans traiter la cause.

### 60.3 La parade qui marche

Le texte aplati a perdu ses espaces : la coupure n'y est plus visible. Mais si
l'on garde, pour chaque caractere aplati, **sa position dans le texte
d'origine**, il suffit de regarder le caractere qui suit la correspondance dans
le texte VRAI. S'il est alphanumerique, la correspondance mord sur le mot
suivant. Idem en amont.

`outils/appariement.py` porte ces trois fonctions — `aplatir_avec_index`,
`coupe_un_mot`, `trouver` — et remplace les copies eparpillees.

### 60.4 MESURE — l'ampleur

`outils/mesurer_artefacts_aplatissement.py`, sur les 385 detections nettoyees :

| | | |
|---|---:|---:|
| Frontiere de mot respectee | 284 | 74 % |
| **A cheval sur un mot — artefact** | **38** | **10 %** |
| Terme absent du texte conserve, inverifiable | 63 | 16 % |

Les 16 % d'inverifiables sont comptes a part, et c'est essentiel : la moisson
ne garde que 900 caracteres de description, alors que l'appariement a
travaille sur le texte complet. Quand le terme est au-dela, son absence ici ne
prouve rien. **Les compter comme artefacts multiplierait le chiffre par
quatre** — exactement le raccourci que le projet s'interdit.

Les formes fautives, par frequence : `president` (23), `viandefr` (20),
`laviandefr` (5), `aviandefr` (5), `entremont` (4), `erdammer` (4).

Deux enseignements. **Le decoupage par article fabrique des formes absurdes** :
`@la_viande_fr` engendre `viandefr`, huit caracteres qui attrapent « viande,
frites », « viande fraiche », « viande francaise ». Et **`president` est un mot
francais courant** — la marque de Lactalis paie le prix de son nom.

### 60.5 MESURE — le garde-fou detruit-il du signal ?

C'est la seule question qui compte. Croisement avec les 175 videos tranchees
par Vincent :

| | Collaboration remuneree | Hors sujet |
|---|---:|---:|
| Propre | **67** | 83 |
| **Artefact** | **0** | **12** |
| Inverifiable | 4 | 6 |

**Zero vrai cas perdu. Douze faux positifs retires.** Le garde-fou est branche
dans `nettoyer_detections.py`.

Effet sur le corpus complet : **244 detections ecartees comme artefacts**. Les
preuves fortes passent de 257 a **240**, les faibles de 128 a 107.
`A_VERIFIER_3.xlsx` passe de 82 a **78 candidats** — quatre de moins a
instruire, tous du bruit.

### 60.6 Ce que ca ne regle pas

Le garde-fou verifie qu'une correspondance est un vrai mot du texte. Il ne dit
rien de ce que ce mot **fait la**.

« Vous lui avez offert un beau petit **foie gras** » pour un pot de depart
passe la frontiere de mot sans probleme : c'est une occurrence authentique du
terme, dans un contexte sans aucun rapport commercial. Ce tri-la revient au
voisinage commercial, puis a un humain.

Autrement dit, cette mesure ameliore la **precision d'appariement**, pas la
precision de detection. Les deux se confondent facilement, et il vaut mieux les
tenir distinctes.

---

## 61. Journal de methode — 27 aout 2026 : la regle la plus simple fait aussi bien

### 61.1 Pourquoi remesurer

Le garde-fou de frontiere de mot (entree 60) a retire 244 detections du corpus.
Toutes les mesures de regles anterieures ont ete faites sur un vivier qui les
contenait. Il fallait recommencer.

Et une decision est en attente de Vincent : que faire de la liste `GENERIQUES`,
mesuree comme nuisible hors CNIEL (entree 56). Autant lui donner un chiffre a
jour.

### 61.2 MESURE — les six regles, sur 240 candidats et 67 vrais

| Regle | Retenus | Vrais | Precision | Rappel |
|---|---:|---:|---:|---:|
| A. l'alias suffit | 157 | 67 | 43 % | **100 %** |
| **B. + vocabulaire commercial dans la description** | 71 | 60 | **85 %** | **90 %** |
| C. + vocabulaire PRES de la mention | 71 | 60 | 85 % | 90 % |
| D. C, et alias generique exclu s'il est seul | 68 | 58 | 85 % | 87 % |
| E. l'etiquette porte un @ ; sinon vocabulaire proche | 134 | 64 | 48 % | 96 % |
| F. @pseudo litteral ; sinon vocabulaire proche ; generique exclu | 68 | 58 | 85 % | 87 % |

### 61.3 Ce que ca dit

**B, C, D et F sont indiscernables en precision — et B a le meilleur rappel.**

C donne exactement les memes 71 lignes que B : sur ce corpus, exiger que le
vocabulaire commercial soit **pres** de la mention ne change rien. D et F
retirent 3 lignes de plus, dont **2 vraies pour 1 fausse** — c'est un mauvais
echange.

Intervalles de confiance a 95 % sur la precision :

    B  85 %   [76 – 93]
    C  85 %   [76 – 93]
    D  85 %   [77 – 94]
    F  85 %   [77 – 94]
    E  48 %   [39 – 56]
    A  43 %   [35 – 50]

Les quatre premiers se recouvrent entierement. **On ne peut pas les
departager sur ce jeu**, et pretendre le contraire serait lire du bruit.

En revanche l'ecart avec A et E est net et hors de doute : le vocabulaire
commercial vaut plus de quarante points de precision, et le simple fait qu'une
etiquette porte un « @ » n'en vaut aucun.

### 61.4 La recommandation

**Prendre B**, la plus simple des quatre.

Ce n'est pas qu'elle soit meilleure — elle ne l'est pas de facon mesurable.
C'est qu'a performance egale, elle n'a **ni liste ecrite a la main, ni notion
de proximite a regler**. Elle ne demande aucun entretien, elle ne peut pas se
perimer quand un nouveau commanditaire arrive, et elle n'a pas la dette
identifiee a l'entree 56.

C'est aussi la reponse a la question laissee ouverte ce matin : **la liste
`GENERIQUES` peut disparaitre**, plutot que d'etre restreinte au CNIEL. B ne
l'utilise pas.

Cela reste **une proposition, pas une decision** : le choix de la regle est
une decision d'architecture, elle revient a Vincent.

### 61.5 Reserves

- **67 vrais cas.** C'est peu. Les intervalles ci-dessus le disent : tout ecart
  de moins de dix points est illisible.
- **Le corpus est deseque vers le CNIEL** — 128 des 240 candidats. Une regle
  qui plairait au CNIEL et deplairait ailleurs passerait inapercue.
- **Le rappel de 100 % de la regle A est un artefact de mesure** : les vrais
  cas ont ete trouves PAR l'appariement d'alias, donc A ne peut pas en manquer.
  Le vrai rappel, celui qui compte les collaborations que le projet ne voit pas
  du tout, demande un tirage aleatoire. Il n'a toujours pas ete fait.

---

## 62. Journal de methode — 27 aout 2026 : la mesure prescrite est impossible

### 62.1 Ce que METHODOLOGIE 9.2 demande

Toutes les mesures de rappel du projet sont des **plafonds**. Les cas juges
par Vincent ont ete trouves par l'appariement de descriptions : une
collaboration que ce canal ne voit pas n'a jamais eu de raison d'entrer dans
le jeu de reference.

METHODOLOGIE 9.2 prescrit donc un **tirage aleatoire de createurs**, annotes
ensuite exhaustivement a la main, pour connaitre le rappel vrai. C'est inscrit
au TODO depuis le debut, et jamais fait.

### 62.2 D'abord, une erreur de lecture de ma part

Mon premier calcul portait sur un tirage de **videos**. Or 9.2 prescrit un
tirage de **createurs**, chacun annote ensuite exhaustivement. Je repondais a
cote, et j'ai failli publier une critique d'une prescription que j'avais mal
lue. Refait au bon niveau.

### 62.3 MESURE — pourquoi ce n'etait pas de la paresse

`outils/estimer_couverture.py`. Sur les **2 660 chaines** moissonnees :

- **36 portent une preuve forte** — 1,35 %
- **11 une collaboration confirmee** par Vincent — 0,41 %

| Pour obtenir | Il faudrait annoter | Soit |
|---|---:|---:|
| 10 chaines a preuve forte | 739 chaines | **28 % du registre** |
| 30 chaines a preuve forte | 2 217 chaines | **83 %** |
| 10 chaines confirmees | 2 418 chaines | **91 %** |
| 30 chaines confirmees | 7 255 chaines | plus que le registre entier |

Et « annoter exhaustivement, par tous les moyens » veut dire parcourir tout le
catalogue d'une chaine a la main. Sept cent trente-neuf fois.

Ce n'est pas une difficulte d'organisation, c'est une impossibilite
arithmetique. Une tache portee au TODO pendant quatre jours ne pouvait pas
etre faite, et personne ne s'en etait avise parce que personne n'avait pose
l'operation.

C'est le meme raisonnement que la section 9 du reste : **a faible prevalence,
l'intuition se trompe de plusieurs ordres de grandeur.** La section le disait
des detecteurs ; elle vaut aussi de sa propre prescription.

### 62.4 La voie de rechange, et ses limites

La capture-recapture : si deux methodes trouvent chacune une partie de la
population, la taille du recouvrement dit quelque chose de la taille totale.

Une tentative anterieure avait echoue — SponsorBlock et description ne sont
pas independants, ils lisent la meme page. **Les chaines des lobbies, elles,
sont une source veritablement distincte** : c'est le commanditaire qui publie.

MESURE :

| Source | Createurs |
|---|---:|
| A — la description cite un alias | 36 |
| B — un lobby le nomme dans ses propres videos | 42 |
| **Recouvrement** | **1** (LeStream) |

Estimateur de Chapman : 794 createurs, contre 77 trouves.

### 62.5 Pourquoi ce 794 ne doit pas etre cite

**Un recouvrement de 1 ne permet aucune estimation.** Faire passer le
recouvrement de 1 a 2 ferait tomber l'estimation de 794 a 529. Le chiffre est
arithmetiquement correct et statistiquement creux.

Ce qui est solide, c'est le **sens** : deux methodes ont trouve 36 et 42
createurs et n'en partagent qu'un seul. Elles ne voient presque pas les memes
gens.

Et la, deux lectures que les donnees ne separent pas :

1. **La couverture est mauvaise.** Chaque methode n'attrape qu'un coin d'un
   ensemble bien plus grand.
2. **Les deux populations different.** Les chaines des lobbies mettent en
   avant des chefs, des eleveurs, des personnalites de television ;
   l'appariement de descriptions trouve des youtubeurs a sponsors. Si ce sont
   deux mondes, la capture-recapture **ne s'applique pas** : elle exige que
   les deux sources tirent dans la meme population.

La lecture 1 sert le projet — elle justifie d'en faire plus. C'est
precisement pour ca qu'il faut se retenir de la presenter seule.

### 62.6 Ce qui trancherait, et qui est deja demande

Savoir **quel type de personne** est chacun des 42 noms. Une colonne de plus
dans `CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx`, ajoutee aujourd'hui, a cote de
la question qui y etait deja.

Si ces noms sont majoritairement des chefs et des eleveurs : lecture 2, et la
capture-recapture est a abandonner. S'ils ressemblent aux createurs trouves
par le canal description : lecture 1, et **la couverture du projet est
mauvaise**, ce qu'il vaut mieux savoir.

Une seule tache de vingt minutes debloque donc deux mesures independantes :
la valeur de la voie « motif dans le titre », et la couverture du projet.

### 62.7 Consequence pour METHODOLOGIE

La section 9.2 prescrit une methode impraticable. Elle demande a etre revue —
mais c'est une decision de methode, donc elle revient a Vincent. Une note y
renvoie desormais a cette entree.
