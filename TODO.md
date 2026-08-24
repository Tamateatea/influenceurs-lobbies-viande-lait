# A faire

Mis a jour le **24 aout 2026**. A relire au debut de chaque session.

Convention : `[V]` = pour Vincent, `[C]` = pour Claude, `[?]` = a decider ensemble.

---

## Prochaine session — a faire en premier

- [ ] `[V]` **CANDIDATER A L'API TIKTOK.** La plus haute valeur de toute la
      liste. `developers.tiktok.com/application/commercial-content-api`.
      Gratuit, ~2 jours ouvres, **aucune affiliation universitaire requise**
      (contrairement a Meta). Elle rend directement le createur, la marque et
      le label de partenariat pour la France. Decrire le projet comme une
      recherche d'interet public sur la transparence de la communication
      commerciale — ce qui est exactement vrai. Voir JOURNAL 25.
- [ ] `[V]` **Arbitrer les 26 pseudos** recoltes sur les sites des lobbies :
      createur remunere, eleveur, ou marque ? Voir
      `recherche/sites_lobbies_2026-08-24_1719.md`.
- [ ] `[C]` **Retrouver les best-of des lives INAPORC** sur les chaines de
      LeBouseuh et Gastronogeek. Cas documente par le commanditaire lui-meme :
      c'est le meilleur test de bout en bout disponible.
- [ ] `[C]` **Ajouter Webedia a la feuille Agences**, source primaire : le
      site d'INAPORC la nomme comme productrice des lives Twitch.

- [ ] `[?]` **Conformite YouTube — a trancher.** Le `robots.txt` de YouTube
      interdit aux programmes `/feeds/videos.xml` (nos flux RSS) et `/results`
      (notre resolution de chaines). L'API YouTube Data v3 couvre ces deux
      usages avec une cle gratuite. Migrer, assumer, ou intermediaire ?
      Voir JOURNAL 22. **Decision de posture, pas technique.**
- [ ] `[C]` **Reprendre Meta plus tard.** Le jeton d'application est refuse
      (« Application does not have permission »). Il faut un jeton UTILISATEUR
      et probablement une verification d'identite. Note demandee par Vincent
      le 24/08 : ne pas abandonner, y revenir apres TikTok.
- [ ] `[C]` **Mesurer l'audience des chaines surveillees.** Le critere de
      priorite est « les createurs les plus vus du public » (precision de
      Vincent, 24/08). Or on ne collecte aujourd'hui NI le nombre d'abonnes,
      NI le nombre de vues. On ne peut donc pas verifier qu'on couvre bien
      les plus vus.

- [ ] `[V]` **Mettre le projet sur GitHub.** Le depot local existe deja, le
      premier commit est fait. Il reste a creer un depot **prive** sur
      github.com/new (ne pas cocher "Add a README"), coller l'URL a Claude,
      qui fera le raccordement et l'envoi. Vincent veut changer de compte
      GitHub d'abord.
- [ ] `[V]` **Verifier si l'affiliation UCD est encore active.** Adresse
      ucdconnect.ie reperee dans la configuration git ; Vincent pense qu'elle
      ne l'est plus, a confirmer. Enjeu : la Meta Content Library (la vraie
      reponse pour Instagram) et l'API de recherche TikTok sont gratuites mais
      reservees aux chercheurs affilies. Une affiliation universitaire
      debloquerait la plateforme la plus difficile du projet sans depenser un
      euro. Potentiellement le point le plus rentable de toute la liste.
- [ ] `[V]` **Solliciter un ami universitaire, si l'affiliation UCD est morte.**
      Vincent a indique pouvoir demander a une connaissance affiliee a une
      universite. C'est une voie tout aussi valable : ces programmes demandent
      un chercheur responsable, pas necessairement le porteur du projet.
      A cadrer avant de demander : ce que la personne accepte de signer, a quoi
      elle s'engage vis-a-vis de la plateforme, et ce qu'elle attend en retour
      (co-signature d'une publication, acces aux donnees, simple coup de main).
      Ne pas approcher quelqu'un sans avoir clarifie ces trois points.

- [ ] `[C]` **LE test a faire en premier : les cas connus.** Inoxtag a fait une
      Tomme de Savoie avec le Cniel, Squeezie a fait une video Cniel qu'il a
      publiquement regrettee. Ce sont deux collaborations laitieres certaines,
      sur deux chaines deja testees techniquement. Pointer la chaine complete
      sur ces videos precises et voir si elle les detecte.
      Si oui : la chaine fonctionne de bout en bout sur du contenu reel.
      Si non : on apprend que les collaborations des lobbies ne laissent pas
      les traces sur lesquelles on comptait — information plus precieuse encore.
      **Precision du 24/08 :** le flux RSS ne donne que les 15 dernieres videos
      d'une chaine. Ces deux collaborations sont anciennes, donc hors de portee
      du flux : il faut les identifiants de video exacts. `[V]` retrouver les
      deux liens, ou `[C]` les chercher — a decider.

- [ ] `[?]` **Trancher la question du perimetre de la collecte.** On a maintenant
      la carte des acteurs. Il faut decider ce qu'on collecte en premier :
      un seul commanditaire a fond (CNIEL, le mieux documente), ou une passe
      large et superficielle sur tous. Ne rien coder avant.
- [ ] `[C]` **Prototype YouTube de bout en bout.** La chaine technique est
      validee : flux RSS de chaine (sans cle) -> identifiants de videos ->
      API SponsorBlock (sans cle) -> segments sponsorises -> transcription du
      segment -> marque. Reste a mesurer la COUVERTURE reelle de SponsorBlock
      sur les chaines francaises : c'est le seul chiffre qui decide si YouTube
      est traitable a cout zero.
- [ ] `[V]` **Creer un compte developpeur Meta** (gratuit) pour obtenir un
      jeton d'API Ad Library. Sans jeton, impossible de tester si l'API renvoie
      les contenus de marque pour la France.
- [ ] `[V]` **Recuperer les listes d'abonnements des comptes vitrines.**
      `@lesproduitslaitiers` en priorite, puis `@la_viande_fr`. Copier-coller
      brut suffit. Derouler jusqu'en bas avant de selectionner : la liste se
      charge par paquets.

## Ameliorer la cartographie

Ce qui manque, par ordre d'impact sur la suite :

- [ ] `[C]` **Croiser les 3 sources deja en main.** Les feuilles HATVP_* et
      Meta_annonceurs contiennent des entites absentes des feuilles ecrites a
      la main (CNE, Sommet de l'Elevage, FNIL, Syndifrais, Culture Viande...).
      Les reconcilier en une seule liste d'entites avec identifiant stable.
- [ ] `[C]` **Ajouter une colonne identifiant** (SIREN, Page ID Meta, pseudo
      par plateforme) a chaque entite. Sans identifiant stable, impossible de
      joindre les sources entre elles.
- [ ] `[C]` **Enrichir la feuille Alias** (Claude redige, Vincent corrige) : c'est elle qui fait la valeur du
      projet, et elle ne compte que 12 lignes.

## Verifications de la cartographie

Environ la moitie des lignes du classeur sont en orange. Par ordre d'utilite :

- [ ] `[V]` **Confirmer les comptes vitrines** de INAPORC, ANVOL, CNPO, CIFOG.
      Quatre recherches, cinq minutes. Reporter le pseudo exact dans la
      feuille `Alias`.
- [ ] `[C]` **Remplacer le chiffre de 30 M EUR de communication d'Interbev**
      par une source primaire, depuis leurs bilans annuels publies.
      Aujourd'hui ce chiffre vient d'une critique de la Confederation paysanne :
      inutilisable publiquement en l'etat.
- [ ] `[C]` **Verifier la feuille `Marques`** (52 lignes, toutes en orange).
      Etablie de memoire. Une erreur de rattachement marque -> groupe est le
      genre d'erreur qui decredibilise.
- [ ] `[C]` **Completer la feuille `Agences`.** Qui a produit les campagnes
      d'influence du CNIEL ? Shokola est identifie pour le digital global,
      mais le pool d'influenceurs a probablement un autre prestataire.

## Mesurer la qualite de l'outil (section 10 de METHODOLOGIE.md)

Chantier prioritaire : sans cela on ne saura jamais si le registre vaut quelque chose.

- [ ] `[?]` **Definir la population de reference** : dans quel ensemble tire-t-on
      l'echantillon aleatoire de createurs ? Decision a prendre ensemble.
- [ ] `[V]` **Constituer le jeu de reference** : annoter a la main, exhaustivement,
      toutes les collaborations viande/lait d'un petit echantillon tire au sort,
      sur une fenetre de temps fixee. Long, mais c'est le seul etalon possible.
- [ ] `[V]` **Regarder a la main les 12 videos d'Inoxtag** marquees
      « segment SponsorBlock sans declaration » au releve du 24/08. Question a
      trancher pour chacune : est-ce un vrai sponsor exterieur, ou Inoxtag qui
      fait la promotion de ses propres projets ? Sans cette verification, le
      chiffre de non-declaration ne veut rien dire. Liste des URL dans
      `recherche/test_croise_youtube_2026-08-24_1050.md`.
- [ ] `[C]` **Resoudre Mister V et McFly & Carlito.** Leurs @pseudos exacts
      sont faux dans le script ; les deux chaines echouent encore au 24/08.
- [ ] `[C]` **Refaire le test croise a grande echelle**, une fois les 12 videos
      arbitrees. Quelques centaines de videos et plusieurs dizaines de chaines,
      pour que ce soit une mesure et non une anecdote.
- [ ] `[C]` **Mettre en place la capture-recapture** entre la mention YouTube et
      SponsorBlock, pour estimer le rappel absolu.
- [ ] `[C]` **Verifier que les cas deja documentes sont retrouves** (Squeezie,
      Inoxtag, Valouzz, Mister V...). Test necessaire mais non suffisant : ces
      cas sont ceux que les journalistes ont trouves, donc les plus visibles.

## Fonctionnalites a garder en tete pour le site

Pas pour tout de suite, mais a ne pas oublier.

- [ ] Un **bouton de signalement** sur le site public, pour que chacun puisse
      remonter une collaboration reperee. C'est aussi la seule reponse credible
      aux Stories Instagram, invisibles a toute collecte retroactive.
- [ ] Une **extension de navigateur** permettant de signaler une collaboration
      directement depuis la page ou on la voit. Techniquement simple, et ca
      transforme des militants en capteurs.
- [ ] Sur chaque fiche createur, le **perimetre de surveillance** : plateformes
      couvertes, depuis quelle date, formats exclus. Pour que l'absence ne se
      lise jamais comme un certificat.

## Sources a tester

- [x] SponsorBlock — API fonctionnelle sans cle. Dump en masse desactive
      (rsync uniquement) : on interrogera video par video.
- [x] Flux RSS YouTube — fonctionnels sans cle API.
- [x] Rapport Meta Ad Library France — exploite, 39 pages de la filiere.
- [ ] `[C]` SponsorBlock — mesurer la couverture francaise (voir plus haut)
- [ ] `[C]` API Meta Ad Library — tester `ad_type=ALL` sur la France, une fois
      le jeton obtenu. Les contenus de marque y sont-ils ?
- [ ] `[C]` TikTok Commercial Content Library — accessible, non teste.
      Interroger sur les marques de la feuille Marques. Chercher l'endpoint
      JSON derriere l'interface web.
- [ ] `[C]` **Verifier si les registres DSA de Google et Meta incluent, comme
      celui de TikTok, les publications organiques a label de partenariat**,
      ou seulement les publicites achetees. Affirmation non testee.
- [ ] `[C]` **Twitch** — pas de registre publicitaire, VOD ephemeres. Verifier
      si les sponsorings Twitch ressortent via les extraits reuploades sur
      YouTube, qui eux sont couverts.
- [ ] `[C]` **Meta Content Library** (programme chercheurs, acces gratuit sur
      affiliation) — recherche plein texte sur les contenus publics Instagram
      et Facebook. Le plus gros deblocage possible pour Instagram. Cout : une
      affiliation, pas de l'argent.
- [ ] `[C]` DGCCRF injonctions — ecrire l'extracteur de la page paginee
- [ ] `[C]` Bilans annuels Interbev et Cniel — extraire les budgets communication
- [ ] `[?]` AGRIP — les beneficiaires des subventions europeennes de promotion

## Contacts a prendre

- [ ] `[V]` **Paye Ton Influence.** Pas pour leurs donnees (il n'y en a pas a
      recuperer), mais parce qu'ils sont le partenaire de diffusion naturel et
      qu'ils travaillent deja le sujet Interbev et Cniel.
- [ ] `[V]` **L214 et Foodwatch** — quelqu'un tient-il deja ce registre ?
- [ ] `[?]` **ARPP** — demander les donnees brutes de leur Observatoire. Refus
      probable, mais un refus est lui-meme documentable.

## Decisions en attente

- [ ] `[?]` Qui publie le registre : Vincent en nom propre, une association
      existante, une nouvelle structure ? Determine la posture juridique.
- [ ] `[?]` Le classeur reste-t-il genere par script, ou devient-il un fichier
      que Vincent edite directement ? (voir LISEZ-MOI.md, "Qui edite quoi")
- [ ] `[?]` Unite de la base : le post, ou la campagne ?

---

## Fait

- [x] 22/08 Recherche de faisabilite : lois, autorites, registres publicitaires,
      antecedents associatifs
- [x] 22/08 Cartographie de la filiere — 12 feuilles
- [x] 22/08 Lecture du schema de l'Observatoire Citoyen de la Publicite
- [x] 22/08 Constat : l'export de Paye Ton Influence ne donne que des agregats
- [x] 22/08 Extraction du sous-graphe viande/lait du repertoire HATVP
- [x] 23/08 Confirme : la declaration « communication commerciale » de YouTube
      est lisible par un programme, gratuitement et sans compte
- [x] 24/08 Test croise YouTube **refait et enregistre** dans `recherche/`.
      Correction d'un bug de resolution des chaines ; les chiffres du 23/08
      sont retires de l'usage. Voir METHODOLOGIE.md section 16.
- [x] 24/08 Verifie que le signal de declaration est stable : 18 relectures,
      resultat identique
- [x] 24/08 Remise a jour de LISEZ-MOI.md, en retard d'une session
