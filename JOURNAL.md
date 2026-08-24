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
