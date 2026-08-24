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
| YT-04 | SponsorBlock couvre les chaines francaises | **PARTIELLE** | Inoxtag 14/15, Squeezie 1/15. `test_croise_youtube_2026-08-24_1050.csv` |
| YT-05 | Un segment SponsorBlock correspond a un sponsor exterieur reel, pas a de l'auto-promotion | **CONFIRMEE** | 12 sur 12, arbitrage humain. JOURNAL 18.1 |
| YT-06 | La case de declaration YouTube capte la majorite des collaborations reelles | **REFUTEE** | 2 sur 14 chez Inoxtag. JOURNAL 18.1 |
| YT-07 | La description publique nomme l'annonceur | **CONFIRMEE** | `descriptions_youtube_2026-08-24_1234.csv` |
| YT-08 | La table d'alias relie l'annonceur cite a l'entite reelle | **CONFIRMEE** | `@lesproduitslaitiers` → CNIEL. JOURNAL 17.1 |
| YT-09 | Les sous-titres sont telechargeables par requete HTTP simple | **REFUTEE** | HTTP 200, corps vide. **Ne pas reessayer ainsi.** JOURNAL 17.3 |
| YT-10 | Les sous-titres sont accessibles via yt-dlp | **CONFIRMEE** | 37 733 caracteres. JOURNAL 20.1 |
| YT-11 | La table d'alias fonctionne aussi sur le contenu parle | **CONFIRMEE** | 1 cas. JOURNAL 20.3 |
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
| IG-01 | L'API Ad Library renvoie les publicites commerciales ordinaires pour la France | **CONFIRMEE (documentation)** | Doc officielle `ads_archive` : la restriction aux pubs politiques ne vise que le hors-UE |
| IG-02 | L'API Ad Library expose les **contenus de marque** (post de createur etiquete partenariat) | **A TESTER** | **La question la plus importante pour Instagram.** Bloquee sur le jeton |
| IG-03 | Un jeton d'API s'obtient sans verification d'identite | **A TESTER** | Sources secondaires : verification requise, non confirmee en pratique |
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
| TT-03 | Elle est interrogeable sans liste de createurs prealable | **CONFIRMEE (documentation)** | Filtre `creator_country_code: FR` seul suffit. JOURNAL 25 |
| TT-04 | Un point d'acces JSON existe derriere l'interface web publique | **REFUTEE** | 12 chemins candidats testes, tous 404 ou HTML. **Passer par l'API officielle.** JOURNAL 25 |
| TT-05 | L'API officielle existe et repond | **CONFIRMEE** | `open.tiktokapis.com/v2/research/adlib/commercial_content/query/` renvoie une erreur JSON structuree, pas un 404. JOURNAL 25 |
| TT-06 | L'acces exige une affiliation universitaire | **REFUTEE** | Ouverte au public et aux chercheurs, contrairement a la Research API. **C'est ce qui la rend accessible.** JOURNAL 25 |
| TT-07 | Les marques de la filiere y figurent pour la France | **A TESTER** | Bloquee sur la candidature |

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
| TR-01 | Les registres DSA de Google et Meta incluent les publications organiques a label de partenariat, comme celui de TikTok | **A TESTER** | Affirmation jamais verifiee. JOURNAL 12 |
| TR-02 | Un modele de langage lisant description et transcription fait mieux qu'un motif regulier | **A TESTER** | Fortement suggere par YT-13, jamais mesure |
| TR-03 | La distinction contrat remunere / cadeau est lisible dans le contenu | **A TESTER** | METHODOLOGIE.md section 4 |
| TR-04 | Les bilans annuels d'Interbev et du Cniel donnent les budgets de communication | **A TESTER** | Remplacerait le chiffre de 30 M EUR, aujourd'hui inutilisable |
| TR-05 | Les injonctions DGCCRF sont extractibles de leur page paginee | **A TESTER** | — |
| TR-06 | Twitch merite d'etre collecte directement | **REFUTEE pour l'instant** | VOD ephemeres (14 a 60 j), aucun registre publicitaire, et les best-of migrent vers YouTube — constate sur le cas INAPORC. JOURNAL 24.3 |
| TR-07 | Les **clips** Twitch, permanents, sont accessibles via l'API officielle gratuite | **A TESTER** | Piste etroite et bon marche, a garder pour apres TikTok |

---

## Sources ecartees — ne pas y revenir sans raison nouvelle

| Source | Pourquoi | Preuve |
|---|---|---|
| Observatoire Paye Ton Influence | Aucun jeu de donnees exportable, seulement des agregats | JOURNAL 7 |
| Observatoire Citoyen de la Publicite | Pas de donnees publiques. Code source utile, modele repris | JOURNAL 7 |
| ARPP | Organe d'autoregulation finance par les annonceurs, publie des agregats seulement | METHODOLOGIE.md section 5 |
| Dump complet SponsorBlock | Telechargement en masse desactive (rsync uniquement) | JOURNAL 7 |
