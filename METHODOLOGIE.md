# Methodologie

Etat au 23 aout 2026.

Ce document dit ce qui est **tranche**, ce qui est **ouvert**, et ce qui sera
**decide apres avoir regarde des donnees reelles** — pas avant. La distinction
compte : figer des regles avant d'avoir vu un jeu de donnees produit des regles
fausses qu'on defend ensuite par entetement.

---

## 1. Ce qui est tranche

Quatre decisions prises par Vincent le 22 aout 2026.

**Perimetre etroit, extensible.** Interprofessions et marques productrices de
viande et de lait. La restauration rapide, les complements proteines et l'oeuf
sont exclus pour l'instant. Le secteur est un champ du modele de donnees, pas
une constante : elargir plus tard ne demandera pas de tout refaire.

**Registre factuel, plaidoyer separe.** Le site public enonce des faits sourcés
et archives, sans jugement editorial. Le naming and shaming, s'il a lieu, se
fait ailleurs et sous une autre voix. Raison principale : en France la
diffamation est un delit penal, et le caractere factuel et documente du
registre est sa meilleure protection. Raison secondaire : Paye Ton Influence
occupe deja le terrain de la campagne, et le fait bien.

**Decouverte par le commanditaire.** On part des lobbies, des marques et de
leurs agences, pas d'une liste d'influenceurs. Une interprofession lance
quelques campagnes par an : l'ensemble est fini et donc traitable. Partir des
influenceurs, c'est un crawl infini.

**Contrats remuneres.** Les envois de produits gratuits ne sont pas l'objet.
Voir la section 4 : ce choix n'est pas encore traduisible en regle technique.

Et une contrainte : **budget zero euro.** Toute source payante est hors jeu.

---

## 2. L'idee centrale : la table d'alias

C'est le seul element de methode qui nous distingue reellement de l'existant,
et il est ne d'une observation, pas d'une intuition.

Sur la campagne Interbev de 2025, le compte partenaire commercial
`@la_viande_fr` n'apparaissait que sur **une publication sur trois**, Interbev
n'etait jamais nomme, et le nom de la campagne — « Celles et ceux qui font la
viande » — etait presente dans une video comme un collectif d'eleveurs
independant.

Consequence : une detection qui lit le nom de la marque tel qu'il apparait dans
le post ne verra jamais le lobby. Elle verra une chaine de caracteres.

Or les deux projets francais existants font exactement cela :

- **Paye Ton Influence** extrait la marque par expression reguliere sur la
  description du post.
- **L'Observatoire Citoyen de la Publicite** stocke la marque dans un champ
  texte libre, sans table d'entites (verifie dans leur schema Rails).

Ni l'un ni l'autre ne peut donc relier `@la_viande_fr` a Interbev. Ce n'est pas
un defaut de leur travail : c'est le prix de leur largeur de perimetre. Notre
perimetre est etroit, donc on peut se permettre une table faite a la main.

La feuille `Alias` du classeur est le debut de cette table : chaque chaine
observable (pseudo, hashtag, slogan, nom de campagne, faux collectif) et
l'entite reelle derriere.

---

## 3. Le trajet d'une entree, en principe

Cinq etapes. Aucune n'est encore construite.

```
  1. CIBLAGE          Reduire l'espace de recherche avant toute analyse.
                      Comptes suivis par les vitrines, rosters d'agences,
                      collaborations deja documentees.
                              │
  2. COLLECTE         Recuperer les publications des comptes cibles.
                      Sources gratuites uniquement.
                              │
  3. DETECTION        Reperer les publications commerciales.
                              │
  4. RESOLUTION       Relier la marque citee a l'entite reelle,
                      via la table d'alias.
                              │
  5. VERIFICATION     Un humain valide. Rien ne se publie sans ce passage.
                              │
                          PUBLICATION
```

L'etape 5 n'est pas une bequille temporaire en attendant que l'automatisation
s'ameliore. Un registre nominatif qui publie une accusation fausse sur dix
n'est pas un registre a 90 % de qualite, c'est un registre inutilisable. La
separation entre ce que la machine trouve et ce que le site affiche est
permanente.

Elle a d'ailleurs un precedent qui tourne : l'Observatoire Citoyen de la
Publicite separe dans sa base les `reports` (signalements bruts) des `problems`
(cas instruits et publies), relies par un workflow d'etapes. On reprendra cette
forme.

---

## 4. Questions ouvertes — a trancher sur donnees, pas maintenant

Aucune de ces questions ne recevra de reponse ferme avant qu'on ait collecte et
regarde un vrai echantillon.

**Remunere ou cadeau ?** La mention legale « Collaboration commerciale »
couvre les deux. La detection ne pourra donc pas filtrer la-dessus : elle
rendra un ensemble plus large que ce qu'on veut publier. Reste a savoir si la
distinction est faisable a la lecture du contenu, ou seulement au cas par cas.
A regarder sur un echantillon reel avant de decider quoi que ce soit.

**Quelle detection ?** Regex, modele de langage, ou combinaison. Paye Ton
Influence obtient 1 033 collaborations sur ~31 000 videos YouTube, soit 3,3 % :
c'est vraisemblablement tres sous-estime, parce que sur YouTube la mention est
souvent orale ou incrustee a l'image, pas ecrite dans la description. Il faut
mesurer cet ecart nous-memes avant de choisir.

**Quelle couverture par plateforme ?** Instagram Stories disparait en 24 h et
restera hors de portee d'une collecte retroactive. Reels, en revanche, est
aujourd'hui le format dominant et Paye Ton Influence l'exclut : peut-etre un
gisement. A mesurer.

**Quelle unite : le post ou la campagne ?** L'exemple Interbev suggere qu'un
post isole est la mauvaise maille, puisque deux tiers d'une meme campagne ne
portent aucun tag. A trancher apres observation.

**Structure juridique et hebergement.** Non aborde. Depend de qui publie, ce
qui n'est pas decide.

---

## 5. Fiabilite des sources — deux mises en garde

**L'ARPP est juge et partie.** L'Autorite de Regulation Professionnelle de la
Publicite est l'organe d'**autoregulation des annonceurs**, financee par eux.
Son Observatoire de l'Influence Responsable analyse de gros volumes — 13 356
contenus au premier semestre 2024 — mais ne publie que des agregats, jamais les
donnees sous-jacentes, et n'a aucun interet a ce que les taux de non-conformite
paraissent eleves. A citer comme position d'un acteur du secteur, jamais comme
mesure independante. En revanche, leur demander les donnees brutes ne coute
rien et un refus est lui-meme documentable.

**Les valorisations media ne sont pas des montants verses.** La campagne
Interbev x Ogilvy x Valouzz est annoncee a « 3,6 M EUR de valorisation media
equivalente ». C'est un indicateur d'agence mesurant l'audience atteinte, pas
une somme payee a un createur. Si ce chiffre apparait un jour dans le registre
comme une remuneration, un journaliste detruira la credibilite du projet avec.
Le modele de donnees devra separer explicitement `montant_verse` et
`valorisation_annoncee`.

---

## 6. Ce que le projet ne fera pas

- Estimer combien il en couterait de « racheter » un influenceur. Les tarifs ne
  sont pas publics et une estimation inventee decredibiliserait le reste.
- Pretendre a l'exhaustivite. Le registre publiera ce qu'il couvre et ce qu'il
  manque.
- Contourner une authentification ou faire du scraping connecte. Interdiction
  de fait : risque juridique disproportionne pour un projet dont la valeur
  repose entierement sur sa credibilite.

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

## 8. Principes d'architecture

Trois regles posees le 23 aout 2026, avant tout developpement.

### 8.1 Aucune dependance a un fichier telecharge a la main

Les fichiers presents dans `donnees/sources/` sont des **instantanes de
travail**, utilises pour explorer et mesurer. L'outil final ne devra jamais
lire un fichier depose manuellement : il interroge les sources a la source.

Exemple concret : le repertoire HATVP est mis a jour toutes les nuits. Notre
copie du 22 aout 2026 sera fausse dans un mois. Elle sert a savoir ce que la
source contient et si elle vaut le coup, pas a alimenter le registre.

Corollaire : chaque source retenue doit avoir une **URL stable interrogeable
par un programme**. Une source qui n'existe que sous forme de fichier a
telecharger depuis un formulaire est une source de recherche, pas une source
de production.

### 8.2 Le perimetre geographique n'est pas la France par nature

Le projet commence par la France parce que c'est le terrain de la personne a
l'origine de l'idee, pas parce que la methode y serait specifique. Le pays
doit rester un **champ de donnees**, jamais une hypothese cablee dans le code.

Ce qui est reellement specifique a la France : la loi du 9 juin 2023, la
DGCCRF, l'ARPP, les interprofessions et leurs CVO, le repertoire HATVP.
Ce qui ne l'est pas : la chaine YouTube, les registres publicitaires imposes
par le DSA a l'echelle europeenne, la table d'alias comme principe.

Consequence pratique : si une technique ne fonctionne bien qu'en anglais ou
qu'aux Etats-Unis, elle n'est pas abandonnee — elle est notee comme applicable
a un autre perimetre.

### 8.3 SponsorBlock — ce que c'est, et pourquoi on s'y interesse

*Note redigee pour pouvoir etre expliquee telle quelle a un tiers.*

Beaucoup de spectateurs trouvent penibles les sequences sponsorisees dans les
videos YouTube — le moment ou le createur s'interrompt pour dire « cette video
vous est proposee par... ». Une extension de navigateur, SponsorBlock, les
saute automatiquement.

Pour les sauter, il faut savoir ou elles commencent et ou elles finissent. Ce
reperage est fait a la main par des volontaires, depuis des annees, et stocke
dans une base publique interrogeable gratuitement et sans authentification.

**L'interet pour nous :** une communaute de benevoles a deja fait, sans le
savoir et sans nous demander un centime, le travail le plus couteux de notre
chaine — localiser precisement le moment ou un createur est paye pour parler
d'une marque. Nous n'avons plus qu'a lire les horodatages et regarder ce qui
est dit a cet endroit.

**Deux limites, a mesurer avant de s'appuyer dessus :**

1. SponsorBlock indique *ou* est la sequence sponsorisee, jamais *pour qui*.
   L'identification de la marque reste entierement a notre charge.
2. La couverture depend entierement du benevolat, et la communaute est
   historiquement orientee vers les contenus tech, gaming et anglophones.
   Rien ne garantit qu'elle connaisse les chaines francaises de cuisine ou de
   lifestyle. **C'est une hypothese non verifiee, pas un acquis.**

Le telechargement de la base complete est desactive (rsync uniquement) :
l'usage retenu est l'interrogation video par video via l'API publique.

---

## 9. Qu'est-ce qu'un influenceur, pour ce registre

Une definition est necessaire, et pour une raison technique autant que
juridique : sans population definie, la section 10 ne veut rien dire. On ne
peut pas affirmer « absent du registre signifie probablement sans contrat »
si l'on n'a pas dit de quelle population le registre parle.

**Base retenue : la definition legale francaise.** La loi n° 2023-451 du
9 juin 2023 vise les personnes physiques ou morales qui, a titre onereux,
mobilisent leur notoriete aupres de leur audience pour communiquer par voie
electronique des contenus visant a promouvoir des biens, des services ou une
cause. Trois avantages : elle est francaise, elle est defendable devant un
tribunal, et elle aligne le registre sur le cadre de conformite que la DGCCRF
applique deja.

Criteres operationnels ajoutes :

- une **personne**, pas un compte de marque ni un media,
- une audience **publique** sur une plateforme sociale,
- une audience **francophone ou orientee marche francais**, tant que le
  perimetre est la France (voir 8.2 : le pays est un champ, pas une hypothese).

**Pas de seuil d'audience pour l'instant.** Decision de Vincent, 23 aout 2026 :
fixer un seuil avant d'avoir teste les methodes de collecte reviendrait a
decider a l'aveugle ou se trouve l'argent. Un seuil a 100 000 abonnes attrape
les personnalites connues et manque des createurs plus petits qui peuvent
concentrer une part importante des budgets. Le seuil sera fixe, s'il doit
l'etre, au vu des donnees.

Note : aucune categorie de contenu n'est privilegiee. Les faits collectes
jusqu'ici montrent que les lobbies achetent d'abord des createurs gaming,
humour et divertissement — Squeezie, Mister V, McFly & Carlito, Valouzz,
Inoxtag — precisement parce que l'association y parait spontanee.

---

## 10. Comment on saura si l'outil est bon

C'est la question que la methodologie doit resoudre avant d'ecrire du code de
production. Montrer qu'un outil **peut** trouver des collaborations ne dit rien
de sa qualite : un outil qui trouve 1 % des cas reels serait une demonstration
reussie et un registre inutile.

### 10.1 Deux grandeurs, deux difficultes tres inegales

**La precision** — parmi ce que l'outil signale, quelle proportion est vraie —
est mesurable directement : on verifie a la main tout ce qui sort. C'est
fastidieux mais sans piege.

**Le rappel** — parmi les collaborations reelles, quelle proportion l'outil
trouve — est le vrai probleme, parce qu'il faut connaitre le denominateur.
Or personne ne connait le nombre reel de collaborations. C'est un chiffre qui
n'existe nulle part.

### 10.2 Le jeu de reference

Premiere brique. Tirer un echantillon **aleatoire** de createurs dans une
population definie, puis annoter a la main, exhaustivement, toutes leurs
collaborations viande/lait sur une fenetre de temps fixee — en y passant le
temps qu'il faut et par tous les moyens. On fait ensuite tourner la chaine
automatique sur exactement le meme echantillon et la meme fenetre, et on
compare.

Deux pieges a ne pas se cacher :

- Le tirage doit etre **aleatoire**. Les collaborations deja documentees par
  StreetPress ou France Culture forment un jeu de test utile mais biaise :
  les journalistes ont trouve les cas les plus visibles. Retrouver ces cas est
  necessaire, jamais suffisant.
- L'annotation manuelle **rate aussi des choses**. Le jeu de reference n'est
  pas la verite, c'est une meilleure approximation.

### 10.3 Capture-recapture, pour estimer ce que tout le monde rate

Pour sortir du probleme du denominateur inconnu, on emprunte une methode
d'epidemiologie et d'ecologie, utilisee pour estimer la taille d'une population
qu'on ne peut pas compter entierement.

Principe : on applique **deux methodes de detection aussi independantes que
possible** au meme echantillon. Si la methode A trouve *a* cas, la methode B
en trouve *b*, et qu'elles en ont *m* en commun, alors la taille totale de la
population est estimable par *a x b / m*. Plus le recouvrement est faible,
plus il reste de cas que les deux methodes ont manques.

Cela donne une estimation du **rappel absolu**, et donc une reponse chiffree a
« notre registre est-il exhaustif ? », sans jamais avoir eu besoin de compter
tous les cas reels.

Condition de validite : l'independance des deux methodes. Deux detecteurs qui
echouent sur les memes contenus — par exemple deux methodes qui lisent toutes
deux la description du post — surestimeront fortement la couverture. Le choix
des paires de methodes est donc lui-meme un choix methodologique a documenter.

### 10.4 Ce que le site devra publier sur lui-meme

Consequence directe : **l'absence d'un createur du registre ne doit jamais
pouvoir se lire comme un certificat.** Chaque fiche portera son perimetre de
surveillance — quelles plateformes, depuis quelle date, quels formats exclus.
C'est l'equivalent de publier les conditions d'un test, pas seulement son
resultat.

---

## 11. Principe de travail : plusieurs hypotheses, toutes testees

Pose par Vincent le 23 aout 2026. Aucune technique de detection n'est retenue
ou ecartee sur intuition. Pour chaque plateforme, on formule plusieurs
hypotheses de collecte, on les teste, on les mesure selon la section 10, et
**on garde toutes celles qui apportent quelque chose**, quitte a superposer
plusieurs couches de detection.

Le cas de YouTube illustre pourquoi. Deux signaux existent :

- la mention de communication commerciale declaree par le createur,
- les segments sponsorises reperes par les benevoles de SponsorBlock.

Ils ne se recouvrent pas. Lors du test du 23 aout, une video presentait un
segment sponsorise identifie par SponsorBlock **sans** declaration officielle
du createur. Autrement dit, le desaccord entre les deux sources n'est pas du
bruit : c'est le signal d'une collaboration potentiellement non declaree,
c'est-a-dire exactement le cas le plus interessant pour le plaidoyer et le
plus difficile a detecter autrement.

Ce sont aussi deux methodes largement independantes, donc un bon candidat pour
l'estimation par capture-recapture de la section 10.3.

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

## 13. Nature du site public — precision de Vincent, 23 aout 2026

Le registre est **d'abord un repertoire consultable, pas un moteur de
recherche**. Le public vise n'est pas quelqu'un qui verifie si son createur
prefere y figure : ce sont des militants, des journalistes et des associations
qui cherchent **qui interpeller** et **sur qui faire porter une campagne**.

Consequence pour la conception : la navigation par liste, par commanditaire et
par filiere prime sur la recherche nominative. La recherche par nom doit
exister, mais elle n'est pas l'entree principale.

---

## 14. Journal de methode — premier test croise, 23 aout 2026

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
protocole de la section 10 reste necessaire.

---

## 15. Deux modes de decouverte — a ne pas confondre

Clarification apportee par une objection de Vincent le 23 aout 2026, qui a mis
le doigt sur une circularite dans la facon dont la chaine etait decrite.

### Mode A — interroger le commanditaire

Certaines sources permettent d'interroger **par annonceur** et renvoient les
createurs. On demande « montre-moi tout ce qui est etiquete partenariat avec le
Cniel » et la source rend les publications, quel qu'en soit l'auteur.

C'est le cas de la bibliotheque de contenus commerciaux de TikTok et de la
Meta Ad Library. **Aucune liste de createurs n'est necessaire en amont** : on
part du lobby et les noms tombent. C'est ce qui justifie le choix, fait des le
depart, de la decouverte par le commanditaire.

### Mode B — surveiller le createur

YouTube n'offre aucun moyen de demander « toutes les videos sponsorisees par le
Cniel ». On ne peut interroger qu'une video a la fois. Il faut donc decider en
amont **qui** on surveille.

Cette liste ne peut pas etre definie comme « les createurs lies aux lobbies » :
ce serait la reponse, pas l'entree. C'est une **hypothese sur la population a
surveiller**, construite a partir de ce qui est connaissable avant d'avoir la
reponse :

- les createurs francais les plus suivis, toutes categories confondues,
- ceux deja documentes par la presse,
- **les comptes suivis par les vitrines des lobbies** — non circulaire, puisque
  c'est un signal emis par le commanditaire lui-meme.

### Les deux modes s'alimentent

Tout nom revele par le mode A entre dans la liste de surveillance du mode B.
TikTok nous apprend qu'un createur a travaille avec le Cniel ; a partir de la
on surveille aussi son YouTube, et on y trouve des collaborations que le mode A
ne pouvait pas voir.

### La faille assumee

Un createur ayant une seule collaboration, sur YouTube uniquement, jamais
etiquetee, absent des listes d'abonnements des vitrines et trop peu suivi pour
figurer dans un classement, echappe aux deux modes. Le mode A ne le voit pas
faute d'etiquette, le mode B faute d'etre sur la liste.

C'est un trou de rappel reel. Il ne se comble pas par une meilleure technique :
il se **mesure** (section 10.3) et se compense partiellement par le signalement
citoyen. Ne jamais le presenter comme resolu.

### Consequence de dimensionnement

La liste de surveillance du mode B doit etre **large, pas etroite**. Le cout
par video est quasi nul : la contrainte n'est pas la puissance de calcul mais
la qualite de la table d'alias. Viser quelques milliers de createurs plutot que
quelques centaines.
