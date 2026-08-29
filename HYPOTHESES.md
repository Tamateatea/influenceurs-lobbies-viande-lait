# Registre des hypotheses

**A quoi sert ce document.** Le projet est en recherche et developpement : on
ne sait pas encore quelles methodes de collecte fonctionnent, plateforme par
plateforme. Ce registre est la memoire de ce qu'on a essaye.

**Il evite trois pertes de temps :** refaire un test deja fait, reprendre une
piste deja refutee, et confondre « on suppose » avec « on sait ».

## Comment on s'en sert

- Une hypothese est formulee de facon a pouvoir etre **fausse**. « SponsorBlock
  est utile » n'est pas une hypothese. « Un segment SponsorBlock correspond a
  un sponsor exterieur reel » en est une.
- Une hypothese **REFUTEE reste inscrite pour toujours**. C'est le principal
  interet du registre : personne ne doit reessayer par le meme chemin.
- Toute ligne CONFIRMEE ou REFUTEE nomme le fichier de `recherche/` ou l'entree
  de `JOURNAL.md` qui l'etablit. Sans preuve nommee, le statut reste
  **A TESTER**.
- Ajouter une hypothese ne coute rien. Ne pas l'ajouter coute une session.

| Statut | Signification |
|---|---|
| **CONFIRMEE** | Testee, ca marche. Preuve nommee. |
| **REFUTEE** | Testee, ca ne marche pas. **Ne pas reessayer par ce chemin.** |
| **PARTIELLE** | Marche dans certains cas seulement, decrits. |
| **EN COURS** | Test commence, resultat incomplet. |
| **A TESTER** | Formulee, jamais testee. |

Etat au **24 aout 2026**.

---

## YouTube

Plateforme la plus avancee. Quatre signaux independants identifies, tous
gratuits et sans authentification.

| ID | Hypothese | Statut | Preuve |
|---|---|---|---|
| YT-01 | La declaration « communication commerciale » est lisible dans la page publique, sans compte ni cle | **CONFIRMEE** | JOURNAL 12 ; 18 relectures stables, JOURNAL 16.3 |
| YT-02 | Le flux RSS de chaine donne les videos recentes sans cle | **CONFIRMEE** | JOURNAL 7 |
| YT-03 | Le flux RSS permet de remonter dans le passe d'une chaine | **REFUTEE** | 15 videos maximum. JOURNAL 16.5 |
| YT-27 | La recherche retroactive est hors de portee | **REFUTEE** | `playlistItems.list` rend 50 videos AVEC descriptions pour 1 unite. 35 612 videos moissonnees pour 806 unites. JOURNAL 33 |
| YT-28 | Les grandes chaines generalistes portent des collaborations CNIEL non documentees | **CONFIRMEE** | 67 collaborations confirmees par Vincent sur 271 candidats. JOURNAL 38.1 |
| YT-30 | L'appariement d'alias seul est exploitable | **REFUTEE** | Precision 25 %. CIFOG 0 %, CLIPP 0 %. Les vitrines ont des noms generiques a dessein. JOURNAL 38.2 |
| YT-31 | Exiger du vocabulaire de collaboration pres de la mention ameliore la precision | **CONFIRMEE** | 25 % → 77 %. JOURNAL 38.3 et 48.2 |
| YT-34 | La regle D fonctionne pour toutes les interprofessions | **REFUTEE** | Parfaite sur le CNIEL (57/57 conserves), elle perd **tous** les vrais cas d'INTERBEV, INAPORC et ANVOL. JOURNAL 48.1 |
| YT-35 | Un alias dont l'etiquette porte un @ est un signal fiable | **REFUTEE** | L'etiquette ne dit pas ce qui a matche : 43 % de precision. JOURNAL 48.2 |
| YT-36 | Raffiner la regle de decision a un rendement croissant | **REFUTEE** | De A a D la precision triple ; de D a F elle ne bouge pas. **C'est la table d'alias qu'il faut completer, pas le filtre.** JOURNAL 48.4 |
| YT-29 | Une marque au nom courant peut etre detectee par simple appariement | **REFUTEE** | « Marie », « Societe », « President » : 698 faux positifs. Il faut exiger un indice commercial. JOURNAL 33.4 |
| YT-04 | SponsorBlock couvre les chaines francaises | **PARTIELLE** | Inoxtag 14/15, Squeezie 1/15. `test_croise_youtube_2026-08-24_1050.csv` |
| YT-32 | SponsorBlock apporte une couverture utile en plus de la description | **REFUTEE** | Rappel 13 %, et 8 de ses 9 vrais cas sont deja vus par la description. Le gain total est de 1 point. JOURNAL 43.1 |
| YT-33 | SponsorBlock et la description sont independants (capture-recapture) | **REFUTEE** | Estimation 65 pour 67 observes : recouvrement quasi total. La paire est inutilisable pour estimer le rappel absolu. JOURNAL 43.2 |
| YT-05 | Un segment SponsorBlock correspond a un sponsor exterieur reel, pas a de l'auto-promotion | **CONFIRMEE** | 12 sur 12, arbitrage humain. JOURNAL 18.1 |
| YT-06 | La case de declaration YouTube capte la majorite des collaborations reelles | **REFUTEE** | 2 sur 14 chez Inoxtag. JOURNAL 18.1 |
| YT-07 | La description publique nomme l'annonceur | **CONFIRMEE** | `descriptions_youtube_2026-08-24_1234.csv` |
| YT-08 | La table d'alias relie l'annonceur cite a l'entite reelle | **CONFIRMEE** | `@lesproduitslaitiers` → CNIEL. JOURNAL 17.1 |
| YT-09 | Les sous-titres sont telechargeables par requete HTTP simple | **REFUTEE** | HTTP 200, corps vide. **Ne pas reessayer ainsi.** JOURNAL 17.3 |
| YT-10 | Les sous-titres sont accessibles via yt-dlp | **CONFIRMEE** | 37 733 caracteres. JOURNAL 20.1 |
| YT-11 | La table d'alias fonctionne aussi sur le contenu parle | **CONFIRMEE** | 1 cas. JOURNAL 20.3 |
| YT-37 | La transcription est redondante avec la description | **REFUTEE** | 1 video sur 37 sans signal en description porte une mention orale. Inoxtag 2.0 : « comme d'habitude les produits laitiers qui nous accompagnent partout ». JOURNAL 53.3 |
| YT-38 | La transcription est plus precise que la description | **CONFIRMEE** | 81 % contre 78 % sur le jeu de reference. JOURNAL 53.1 |
| YT-39 | La transcription est applicable a grande echelle | **REFUTEE** | Plusieurs secondes par video : hors de portee sur 2 600 chaines. A employer en second rideau, sur les chaines deja identifiees. JOURNAL 53.4 |
| YT-40 | Rapprocher un titre de lobby des comptes connus suffit a nommer un createur | **REFUTEE** | Six caracteres declenchaient, et la valeur rendue etait l'identifiant du PREMIER compte ayant revendique la forme : « Morgan VS » attribue a morganabbou. 30 % des formes sont partagees. Corrige. JOURNAL 55.2 |
| YT-41 | Les chaines des lobbies nomment des createurs identifiables | **CONFIRMEE** | Apres correction : Pierre Chomet, Morgan VS, L'Amour Boeuf, Fabrice Mignot, Mister V, Brigitte Lecordier. 42 noms par compte connu. JOURNAL 55.3 |
| YT-42 | La voie « motif dans le titre » nomme des createurs | **A MESURER** | 176 noms, dont beaucoup de series a l'oeil (Milk Check, Generation XYZ). CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx tranche. JOURNAL 55.4 |
| YT-43 | La case de declaration a une precision tres haute | **CONFIRMEE** | 91 % sur 175 videos jugees, la meilleure des quatre signaux. JOURNAL 57.1 |
| YT-44 | La filiere declare correctement ses collaborations | **REFUTEE** | Rappel 44 % : 40 vraies collaborations sur 71 ne sont pas declarees. C'est le chiffre qui justifie le projet. JOURNAL 57.2 |
| YT-45 | La case de declaration designe le commanditaire | **REFUTEE** | Elle dit qu'un partenariat paye existe, pas par qui. Seule la conjonction avec l'alias designe l'entite. JOURNAL 57.3 |
| YT-46 | La regle D generalise a une entite jamais vue | **REFUTEE, mais a l'envers** | Retirer les termes d'INAPORC fait passer precision ET rappel de 0 a 100 %. La liste des generiques, ecrite en regardant le CNIEL, retire du signal ailleurs. JOURNAL 56.4 |
| YT-47 | Le jeu de reference est contamine par la troncature a 900 caracteres | **REFUTEE** | 42 % des detections ont leur alias au-dela de la coupure, mais le taux de vrais y est de 61 % contre 33 % ailleurs : Vincent est alle voir les videos, l'avertissement du classeur a fonctionne. JOURNAL 57.4 |
| YT-48 | La transcription en second rideau trouve ce que rien d'autre ne voit | **CONFIRMEE** | 232 transcriptions de videos sans signal en description, 4 liens reels. Dont « j'etais en tournage pour les produits laitiers ». JOURNAL 59.2 |
| YT-49 | La relation Inoxtag x CNIEL est ponctuelle | **REFUTEE** | Traces orales en 2023, 2024 et 2025 : un tournage, un stand au salon, une personne du CNIEL nommee. JOURNAL 59.3 |
| YT-50 | La regle des huit caracteres suffit contre les artefacts d'aplatissement | **REFUTEE** | « la viande frerot » aplati contient `laviandefr`, dix caracteres. Il faut verifier la frontiere de mot dans le texte d'origine. JOURNAL 59.4 |
| YT-51 | Les artefacts d'aplatissement sont anecdotiques | **REFUTEE** | 10 % des detections nettoyees mordent sur un mot voisin. Formes fautives : `president`, `viandefr`, `entremont`. JOURNAL 60.4 |
| YT-52 | Le garde-fou de frontiere de mot detruit des vrais cas | **REFUTEE** | Sur les 175 videos jugees : 12 artefacts retires, tous « hors sujet », zero vrai cas perdu. JOURNAL 60.5 |
| YT-53 | La regle D vaut mieux que la regle B, plus simple | **REFUTEE** | 85 % / 87 % contre 85 % / 90 %. Les intervalles de confiance se recouvrent entierement ; B a le meilleur rappel et n'a aucune liste manuelle. JOURNAL 61.3 |
| YT-54 | Exiger le vocabulaire commercial PRES de la mention ameliore la precision | **REFUTEE** | La regle C retient exactement les memes 71 lignes que la regle B. La proximite n'apporte rien sur ce corpus. JOURNAL 61.3 |
| YT-55 | Aligner tous les outils sur huit caracteres est une amelioration | **REFUTEE** | Cela retire 43 formes de la moisson, dont Actimel, Activia, Babybel, Boursin, Candia, Aoste. C'est la frontiere de mot qui traite la cause, pas la longueur. JOURNAL 63.2 |
| YT-56 | Le second rideau gagnerait a voir les marques | **REFUTEE** | Sur les 236 memes transcriptions : 5 detections deviennent 57, presque toutes sur « marie », « societe », « president ». Des mots ordinaires du francais parle, contre lesquels la frontiere de mot ne peut rien. JOURNAL 63.3 |
| YT-57 | La detection se degrade sur le contenu recent | **REFUTEE** | 43 % du corpus est de 2025-2026 et la part de videos citant la filiere est stable (25 a 33 %). C'est la composition qui change, pas la detection. JOURNAL 64.3 |
| YT-58 | Une veille continue submergerait Vincent de verifications | **REFUTEE** | 12 preuves fortes sur les 12 derniers mois, soit une a deux par mois sur le canal interprofession. Tenable indefiniment. JOURNAL 64.5 |
| YT-59 | Le canal interprofession est le principal gisement | **REFUTEE** | En 2026 : 60 citations d'interprofession contre 1 635 de marques, et 33 des 60 sont le groupe temoin cerealier. Le gisement est le canal marque, dont la precision n'a JAMAIS ete mesuree. JOURNAL 64.4 |
| YT-12 | Le segment SponsorBlock correspond a l'annonceur cite en description | **REFUTEE** | Trois annonceurs distincts dans une meme video. JOURNAL 20.2 |
| YT-13 | Un motif regulier sur la transcription suffit a identifier un annonceur | **REFUTEE** | Faux positif sur une blague. JOURNAL 20.4 |
| YT-14 | Un code promo ou un lien d'affiliation est un meilleur indice que la mention legale | **CONFIRMEE, avec reserve** | 42 videos contre 18. Mais « remerciement » melange sponsors et amis. JOURNAL 21.5 |
| YT-15 | Les createurs generalistes suivis par le CNIEL portent des collaborations non encore documentees | **EN COURS** | 174 videos, 13 chaines : aucune entite trouvee. Mais chaines secondaires non couvertes a ce stade. `surveillance_youtube_2026-08-24_1639.csv` |
| YT-17 | Un createur n'a qu'une seule chaine YouTube | **REFUTEE** | 13 createurs → 24 chaines officielles. La collaboration CNIEL etait sur une secondaire. JOURNAL 21.2 |
| YT-18 | Les chaines secondaires sont plus densement sponsorisees que les principales | **PARTIELLE** | Inoxtag : 14/15 contre 4/15. Un seul createur, a confirmer. JOURNAL 21.2 |
| YT-19 | Le badge de verification suffit a ecarter les chaines de fans | **CONFIRMEE** | 17 chaines « Squeezie » → 3 officielles. JOURNAL 21.3 |
| YT-20 | On peut interroger YouTube en masse sans limitation | **REFUTEE** | HTTP 429 des ~300 pages consecutives. JOURNAL 21.4 |
| YT-21 | Ralentir suffit a contourner la limitation | **REFUTEE** | 3x moins de debit → 3x plus d'echecs. La limite est un budget cumule sur la journee, pas un debit. JOURNAL 28 |
| YT-22 | Le badge de verification ecarte les homonymes | **REFUTEE** | « Norman » remonte Norman Greenbaum ; « Domingo » remonte Domingo Legal. Ecarte les fans, pas les homonymes reels. JOURNAL 28.4 |
| YT-23 | L'API YouTube Data v3 offre un quota documente utilisable | **CONFIRMEE** | 27 chaines relevees pour 3 unites sur ~10 000. `audiences_youtube_2026-08-24.csv` |
| YT-24 | L'API donne le nombre d'abonnes | **CONFIRMEE** | `channels.list?part=statistics`. Couverture d'audience 3 % → 7 % |
| YT-25 | Resoudre une chaine par @pseudo coute autant que par recherche | **REFUTEE** | 1 unite contre 100. Et sans ambiguite d'homonyme. JOURNAL 31.3 |
| YT-26 | L'API expose la case de declaration commerciale | **REFUTEE** | Absente de l'API : elle n'existe que dans la page `/watch`. La lecture directe reste necessaire |
| YT-16 | Les sponsorings Twitch ressortent via les extraits reuploades sur YouTube | **CONFIRMEE** | INAPORC ecrit que les lives Gastronogeek et LeBouseuh ont fait l'objet d'un best of sur leurs chaines YouTube. JOURNAL 24.3 |

### Ce que YouTube a appris au projet

Quatre signaux, aucun suffisant seul :

1. **Case de declaration** — fiable quand presente, rate 6 collaborations sur 7.
2. **Segment SponsorBlock** — precis (12/12), mais couverture tres inegale
   selon les chaines, et ne dit jamais **pour qui**.
3. **Description** — nomme l'annonceur, mais ne montre pas les collaborations
   annoncees seulement a l'oral.
4. **Transcription** — atteint l'oral, donc le reste ; mais riche en bruit,
   et illisible sans jugement humain (YT-13).

Consequence : **on superpose, on ne choisit pas.** C'est le principe pose en
METHODOLOGIE.md section 10.

---

## Instagram

Bloquee sur l'acces. Aucune methode de collecte validee a ce jour.

| ID | Hypothese | Statut | Preuve |
|---|---|---|---|
| IG-01 | L'API Ad Library renvoie les publicites commerciales ordinaires pour la France | **CONFIRMEE (documentation, revue le 27/08)** | Doc officielle `ads_archive` : « Ads that did not reach any location in the EU will only return if they are about social issues, elections or politics ». La couverture commerciale existe **pour l'UE et le Royaume-Uni seulement**, au titre du DSA. La France est couverte |
| IG-02 | L'API Ad Library expose les **contenus de marque** (post de createur etiquete partenariat) | **A TESTER** | **La question la plus importante pour Instagram.** Bloquee sur le jeton |
| IG-03 | Un jeton d'API s'obtient sans verification d'identite | **REFUTEE** | Documentation Meta, verifiee le 27/08 : la confirmation d'identite sur facebook.com/ID — celle exigee pour les publicites politiques — est un prealable a TOUT appel a `ads_archive`. Piece d'identite officielle, 1 a 3 jours ouvres. Le HTTP 400 du 24/08 s'explique par la. JOURNAL 65 |
| IG-04 | La Meta Content Library est accessible sans affiliation universitaire | **REFUTEE** | Affiliation requise. Celle de Vincent (UCD) n'est plus active |
| IG-05 | Les comptes suivis par une vitrine contiennent les createurs ayant collabore | **PARTIELLE** | Les 3 cas CNIEL documentes y figurent. `comptes_suivis_2026-08-24.csv`. **Un abonnement ne prouve rien** — voir JOURNAL 19 |
| IG-06 | Les Stories sont collectables retroactivement | **REFUTEE** | 24 h de duree de vie. Compensable par le signalement citoyen seulement |
| IG-07 | Les Reels sont un gisement neglige par les projets existants | **A TESTER** | Paye Ton Influence les exclut |

---

## TikTok

**La source la plus prometteuse du projet.** Bloquee sur une candidature,
pas sur une difficulte technique.

| ID | Hypothese | Statut | Preuve |
|---|---|---|---|
| TT-01 | `library.tiktok.com` est accessible sans compte | **CONFIRMEE** | JOURNAL 7 |
| TT-02 | La bibliotheque inclut les publications organiques a label de partenariat | **CONFIRMEE (documentation)** | L'endpoint s'appelle `commercial_content/query/` et rend `label` + `brand_names` + `creator.username`. JOURNAL 25 |
| TT-03 | Elle est interrogeable sans liste de createurs prealable | **CONFIRMEE** | 8 061 createurs francais obtenus avec le seul filtre pays. JOURNAL 34.1 |
| TT-08 | `brand_names` permet de savoir POUR QUI travaille le createur | **REFUTEE** | Renseigne 2 fois sur 20 000. JOURNAL 34.1 |
| TT-09 | `search_term` filtre sur `commercial_content/query` | **REFUTEE** | Accepte et **silencieusement ignore** : un terme absurde rend les memes resultats. JOURNAL 34.2 |
| TT-10 | `search_term` filtre sur `ad/query` | **CONFIRMEE** | Terme absurde → 0 resultat. « lait » → NESTLE FRANCE. JOURNAL 34.3 |
| TT-11 | `ad/query` nomme l'agence | **CONFIRMEE** | 7 agences de la filiere identifiees, dont iProspect pour INTERBEV. JOURNAL 35.3 |
| TT-13 | Les interprofessions achetent de la publicite sur TikTok | **CONFIRMEE** | INTERBEV, 26 annonces via iProspect Conseil France. JOURNAL 35.3 |
| TT-12 | On peut aller de l'annonceur au createur remunere | **REFUTEE** | Les deux endpoints ne se joignent pas : l'un a le createur sans la marque, l'autre l'inverse. **C'etait l'esperance principale placee dans TikTok.** JOURNAL 34.4 |
| TT-04 | Un point d'acces JSON existe derriere l'interface web publique | **REFUTEE** | 12 chemins candidats testes, tous 404 ou HTML. **Passer par l'API officielle.** JOURNAL 25 |
| TT-05 | L'API officielle existe et repond | **CONFIRMEE** | `open.tiktokapis.com/v2/research/adlib/commercial_content/query/` renvoie une erreur JSON structuree, pas un 404. JOURNAL 25 |
| TT-06 | L'acces exige une affiliation universitaire | **REFUTEE** | Ouverte au public et aux chercheurs, contrairement a la Research API. **C'est ce qui la rend accessible.** JOURNAL 25 |
| TT-07 | Les marques de la filiere y figurent pour la France | **CONFIRMEE** | NESTLE FRANCE et BEL sortent sur deux essais de 10 resultats. JOURNAL 34.3 |
| TT-14 | L'API TikTok a un quota journalier | **CONFIRMEE** | `daily_quota_limit_exceeded` apres deux mois de moisson. JOURNAL 45.1 |
| TT-15 | Le decoupage mensuel contourne le plafond de pagination | **CONFIRMEE** | Octobre 2022 seul rend 13 038 contenus. JOURNAL 45.4 |
| TT-16 | La population de reference francaise est constituee | **REFUTEE** | 2 mois sur 47 moissonnes. Il faudra une vingtaine de jours de quota. JOURNAL 45.3 |

---

## Semences de la liste de surveillance — mesurees le 26 aout

Quelle source de noms produit le plus de vraies pistes filiere, par chaine
surveillee ?

| ID | Hypothese | Statut | Preuve |
|---|---|---|---|
| SE-01 | Les abonnements des vitrines sont une bonne semence | **CONFIRMEE** | 2,12 preuves fortes par chaine. JOURNAL 46.2 |
| SE-02 | Les createurs commerciaux TikTok sont une meilleure semence | **REFUTEE** | 0,16 par chaine, soit 13 fois moins. **J'avais affirme le contraire sans le tester.** JOURNAL 46.1 |
| SE-03 | Les comptes des grandes marques ont des abonnements exploitables | **A TESTER** | Danone, Lactalis, Bel, Nestle jamais releves |

---

## Chaines YouTube des lobbies — ouverte le 27 aout

La seule source ou **le commanditaire publie lui-meme** et nomme le createur.

| ID | Hypothese | Statut | Preuve |
|---|---|---|---|
| CL-01 | Les interprofessions ont leurs propres chaines YouTube | **CONFIRMEE** | 6 chaines, 737 videos. JOURNAL 51.2 |
| CL-02 | Leurs titres nomment les createurs invites | **CONFIRMEE** | 429 videos, 285 createurs distincts |
| CL-03 | On y trouve des createurs a tres forte audience | **CONFIRMEE** | Norman 11,2 M, Inoxtag 9,47 M, Mister V 6,53 M |
| CL-04 | Un createur ne travaille que pour une interprofession | **REFUTEE** | Norman apparait chez le CNIEL **et** INTERBEV |
| CL-05 | Cette source etablit la remuneration | **REFUTEE par principe** | Elle etablit la collaboration ; l'invitation et le contrat ne se distinguent pas |

---

## Sites des commanditaires — piste ouverte le 24 aout

Les seuls resultats du projet qui soient des **declarations du commanditaire**
plutot que des inferences sur du contenu.

| ID | Hypothese | Statut | Preuve |
|---|---|---|---|
| SC-01 | Les sites des interprofessions sont explorables par plan de site | **PARTIELLE** | 3 sur 5. `sites_lobbies_2026-08-24_1719.csv` |
| SC-02 | Ils publient des pseudos de createurs | **CONFIRMEE** | 26 pseudos distincts. JOURNAL 24.2 |
| SC-03 | Certains ont une rubrique dediee aux influenceurs | **CONFIRMEE** | INAPORC : « Les recettes des influenceurs ». JOURNAL 24.2 |
| SC-04 | Un credit de recette prouve une remuneration | **REFUTEE** | Etablit une relation de travail, pas son caractere onereux. **Mais publiable** avec le degre de certitude `lien commercial documente` — arbitrage de Vincent, METHODOLOGIE 1 |
| SC-05 | Toutes les interprofessions publient autant | **REFUTEE** | INAPORC beaucoup, CNIEL peu, INTERBEV presque rien. JOURNAL 24.4 |

---

## Transversal

| ID | Hypothese | Statut | Preuve |
|---|---|---|---|
| TR-08 | La detection par forme de remerciement trouve des annonceurs inconnus | **CONFIRMEE** | 229 annonceurs hors table sur 31 149 videos. JOURNAL 41 |
| TR-09 | Elle trouve des annonceurs de la filiere que la table ignore | **REFUTEE** | 1 candidat alimentaire sur 229, et c'est du mobilier de cuisine. JOURNAL 42.1 |
| TR-10 | Un zero de detection prouve l'absence de collaboration | **REFUTEE** | Le mecanisme n'attrape que les annonceurs NOMMES. La strategie de la vitrine consiste precisement a ne pas se nommer. JOURNAL 42.2 |
| TR-01 | Les registres DSA de Google et Meta incluent les publications organiques a label de partenariat, comme celui de TikTok | **A TESTER** | Affirmation jamais verifiee. JOURNAL 12 |
| TR-02 | Un modele de langage lisant description et transcription fait mieux qu'un motif regulier | **A TESTER** | Fortement suggere par YT-13, jamais mesure |
| TR-03 | La distinction contrat remunere / cadeau est lisible dans le contenu | **A TESTER** | METHODOLOGIE.md section 4 |
| TR-04 | Les bilans annuels d'Interbev et du Cniel donnent les budgets de communication | **A TESTER** | Remplacerait le chiffre de 30 M EUR, aujourd'hui inutilisable |
| TR-05 | Les injonctions DGCCRF sont extractibles de leur page paginee | **A TESTER** | — |
| TR-06 | Les best-of Twitch migrent vers YouTube, donc Twitch est couvert indirectement | **REFUTEE — teste le 29/08** | Catalogue COMPLET de Lebouseuh (1 773 videos) et 300 de Gastronogeek : **zero mention** d'INAPORC, du Porc Francais, de leporc.com ou de la filiere porcine. 42 unites de quota. JOURNAL 70 |
| TR-07 | Les **clips** Twitch, permanents, sont accessibles via l'API officielle gratuite | **A TESTER** | Piste etroite et bon marche, a garder pour apres TikTok |

---

## Sources ecartees — ne pas y revenir sans raison nouvelle

| Source | Pourquoi | Preuve |
|---|---|---|
| Observatoire Paye Ton Influence | Aucun jeu de donnees exportable, seulement des agregats | JOURNAL 7 |
| Observatoire Citoyen de la Publicite | Pas de donnees publiques. Code source utile, modele repris | JOURNAL 7 |
| ARPP | Organe d'autoregulation finance par les annonceurs, publie des agregats seulement | METHODOLOGIE.md section 5 |
| Dump complet SponsorBlock | Telechargement en masse desactive (rsync uniquement) | JOURNAL 7 |

| IG-08 | L'acces a l'Ad Library passe par un « use case » d'application | **REFUTEE** | Aucun des use cases proposes par Meta ne concerne l'Ad Library. L'acces est gate sur la confirmation d'identite, pas sur la configuration de l'app. Mes instructions du 27/08 decrivaient un parcours de creation d'app qui n'existe plus. JOURNAL 65 |
| IG-09 | Le quota de l'Ad Library permet un balayage large | **A TESTER** | Environ 200 appels par heure d'apres les sources secondaires. A verifier des que le jeton fonctionne — cela dimensionne toute la strategie Instagram |
| SE-04 | Le projet voit la majorite des collaborations existantes | **PARTIELLE** | **Chiffre corrige le 28/08.** Le canal description seul en voit 3 sur 12. Mais en comptant TOUS les canaux — chaines des lobbies, publicites Meta, sites — on en voit **8 sur 12, soit 67 %**. Le 25 % annonce d'abord ne mesurait qu'un canal. JOURNAL 68 et 69 |
| SE-05 | Le journalisme est une source independante utilisable | **CONFIRMEE, avec reserve** | Il n'apparie pas de chaines de caracteres, il enquete. Mais il trouve les cas les plus visibles, comme nous : les 119 sont un plancher. JOURNAL 68.7 |
| SE-06 | Twitch est hors sujet pour le projet | **REFUTEE — avec mesure, le 29/08** | J'ai d'abord ecrit « REFUTEE ». C'etait trop rapide : TR-06 disait que les best-of migrent vers YouTube, et cette hypothese n'a jamais ete TESTEE dans nos donnees. Les chaines de Lebouseuh et Gastronogeek ont ete moissonnees, mais la moisson n'enregistre que les videos A SIGNAL : impossible de savoir si le best-of a ete vu et rejete, ou jamais vu. Test a faire : lister leurs catalogues et chercher le best-of INAPORC. JOURNAL 69 |
| SE-07 | Une video peut etre dans nos donnees sans que le createur y soit rattache | **CONFIRMEE** | « 1990 VS 2000 » figure dans le catalogue LAIT'FLIX qu'on a releve, mais la page ne nomme pas Squeezie. La video est vue, l'attribution manque. JOURNAL 69.4 |
| TR-11 | Un createur ne travaille que pour une seule filiere | **REFUTEE** | Lebouseuh est associe a l'INAPORC par la presse, et porte quatre videos pour Nature de Breton, marque beurriere. JOURNAL 70.4 |
| IG-10 | Le canal « publicites payees » identifie des createurs | **REFUTEE** | 60 jugements de Vincent, **0 % de precision**. Une annonce est ecrite par le commanditaire : le nom qui y domine est le sien. JOURNAL 71.2 |
| SE-08 | La moisson massive de YouTube est le meilleur canal du projet | **REFUTEE** | 332 119 videos ont donne 13 createurs confirmes. Cinq pages web en ont donne 42. Rapport de 1 a 60 en faveur de la lecture de sites. JOURNAL 71.3 |
