# A faire

Mis a jour le **27 aout 2026 au soir**. A relire au debut de chaque session.

Convention : `[V]` = pour Vincent, `[C]` = pour Claude, `[?]` = a decider ensemble.

**Les taches de Vincent sont dans `cartographie/A_FAIRE.xlsx`** — trois
feuilles : ce qu'il a a faire, les decisions qu'il est seul a pouvoir prendre,
et ce qui avance sans lui. Ce fichier-ci sert de memoire au projet ; il ne lit
pas les `.md`.

`MES_TACHES.xlsx` contient ses reponses des 25 et 26 aout : **ne pas
l'ecraser**. `A_FAIRE.xlsx` est regenere a volonte par
`outils/generer_a_faire.py`, il ne contient aucune de ses reponses.

---

## Pour Vincent — le detail est dans MES_TACHES.xlsx

- [ ] `[V]` **Relever les abonnements des GRANDES MARQUES** — Danone, Lactalis,
      Bel, Nestle France, puis Savencia, Sodiaal, Fleury Michon, Herta, LDC,
      Bigard. **Mesure du 26/08 : 2,12 vraies pistes par chaine contre 0,16
      pour la semence TikTok.** Jamais releves alors que ce sont des
      commanditaires directs.
- [ ] `[V]` **Chercher les noms de campagne** sur les sites des lobbies. Deux
      trouves par hasard le 26/08 — « En Mode Actif » (CNIEL) et « Made in
      Viande » (INTERBEV) — dans des donnees deja collectees. C'est le point
      faible identifie : completer la table d'alias rapporte plus que
      raffiner le filtre (JOURNAL 48.4).
- [ ] `[V]` **Trancher `CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx`** — 218 noms
      trouves dans les videos publiees par les lobbies eux-memes. Une seule
      question : createur, ou nom de serie ? Trie par valeur, il peut s'arreter
      apres la 60e ligne. **C'est ce qui mesurera la voie « motif dans le
      titre »** (YT-42), la seule des deux dont on ignore ce qu'elle vaut.
- [ ] `[V]` **Juger `A_VERIFIER_3.xlsx`** — 72 candidats jamais vus, sortis de
      la moisson elargie (977 chaines, 230 503 videos). Les 175 deja tranches
      ont ete ecartes automatiquement.
- [ ] `[V]` **Meta : obtenir un jeton UTILISATEUR.** Le jeton d'application est
      refuse. Verification d'identite sur facebook.com/ID, puis Graph API
      Explorer en mode « User token » avec la permission `ads_read`.
      **Ne donnera PAS les nombres d'abonnes Instagram.**
- [ ] `[V]` **Relever les abonnements des vitrines sur TikTok et YouTube** —
      les memes comptes qu'Instagram, ou les abonnements different.
- [ ] `[V]` **Chercher les comptes regionaux d'INTERBEV.**
- [ ] `[V]` **Verifier l'orthographe de `@ouefsdefrance`** — un « e » semble
      inverse.

### Contacts a prendre

- [ ] `[V]` **Paye Ton Influence** — partenaire de diffusion naturel, ils
      travaillent deja Interbev et Cniel.
- [ ] `[V]` **L214 et Foodwatch** — quelqu'un tient-il deja ce registre ?
- [ ] `[V]` **Un ami universitaire**, si on veut un jour la Meta Content
      Library. Deprioritise : l'API TikTok a montre qu'on peut avancer sans.
      A cadrer avant de demander : ce que la personne signe, ce a quoi elle
      s'engage, ce qu'elle attend en retour.

---

## Pour Claude — au retour du quota

- [x] `[C]` ~~Finir la moisson YouTube~~ **FAIT le 27/08** : 2 660 chaines sur
      2 660, 307 191 videos. Premiere revue complete du registre.
- [x] `[C]` ~~Evaluer les deux signaux jamais mesures~~ **FAIT le 27/08.**
      Case de declaration 91 % / 44 % ; transcription 81 % / 49 %. Les quatre
      signaux YouTube sont desormais tous mesures (JOURNAL 53 et 57).
- [x] `[C]` ~~Tester la regle D sur des entites jamais vues~~ **FAIT le 27/08,
      et le resultat est l'inverse de l'attendu** : la liste `GENERIQUES`
      retire du signal hors CNIEL (JOURNAL 56). Remesure complete des six
      regles en JOURNAL 61 — **la regle B, la plus simple, fait aussi bien**.
- [x] `[C]` ~~Corriger l'appariement des marques au nom courant~~ **traite en
      partie le 27/08** : le garde-fou de frontiere de mot retire 244
      detections, dont 23 sur `president` et 30 sur les formes de
      `@la_viande_fr` (JOURNAL 60). Reste le cas des marques dont le nom EST
      un mot courant meme correctement delimite — « Marie », « Societe ».

- [ ] `[C]` **Reprendre la moisson TikTok** : 42 mois sur 47. Le quota
      journalier n'en autorise qu'environ deux par jour — compter trois
      semaines. `outils/moissonner_tiktok.py` reprend ou il s'arrete, et un
      mois en echec n'est PAS marque fait.
- [ ] `[C]` **Relancer la detection avec les nouveaux alias** — « En Mode
      Actif » et « Made in Viande ». Sur des donnees deja moissonnees, donc
      sans quota.
- [ ] `[C]` **Finir le croisement TikTok → YouTube** : 1 061 createurs sur
      8 061, quota epuise en cours de route.
- [ ] `[C]` **Etendre le second rideau** aux chaines a preuve forte, pas
      seulement aux 11 confirmees par Vincent. La technique a rapporte 4 liens
      reels sur 232 transcriptions (JOURNAL 59).
- [ ] `[C]` **Partager `charger_alias`**, recopiee dans six outils. Une
      correction dans l'une ne se propage pas aux autres — c'est exactement ce
      qui a laisse `moissonner_chaines_lobbies.py` avec un seuil de six
      caracteres quand les autres etaient a huit.
- [ ] `[C]` **Ajouter Webedia et les agences TikTok** a la feuille Agences.
- [ ] `[C]` **Extraire les budgets de communication** des bilans annuels
      d'Interbev et du Cniel. Le chiffre de 30 M EUR vient d'une critique de
      la Confederation paysanne : inutilisable publiquement.
- [ ] `[C]` **Ecrire l'extracteur des injonctions DGCCRF** (page paginee).
- [ ] `[C]` **Verifier la feuille `Marques`** — 52 lignes etablies de memoire,
      toutes en A VERIFIER. Une erreur de rattachement marque → groupe
      decredibiliserait le registre.

---

## Decisions en attente

- [ ] `[?]` **Faut-il continuer a versionner `donnees/moisson_videos.json` ?**
      Il pese 26 Mo et atteindra ~68 Mo quand les 2 660 chaines seront faites.
      Git en garde une copie entiere a chaque commit — le depot fait deja 40 Mo.
      Pour : c'est la sauvegarde de trois jours de quota d'API, qu'on ne
      rachete pas. Contre : le depot devient lourd a cloner.
      Proposition : le compresser (`.json.gz`, environ 4 Mo) plutot que de
      choisir entre les deux. **A trancher par Vincent.**

- [ ] `[?]` **Quelle regle de detection garder ?** MESURE du 27/08 : B, C, D
      et F font toutes 85 % de precision, intervalles de confiance
      entierement recouvrants, et **B a le meilleur rappel** (90 %).
      Recommandation : **prendre B**, la seule sans liste ecrite a la main.
      La liste `GENERIQUES` disparaitrait au lieu d'etre corrigee.
      C'est un choix d'architecture : **il revient a Vincent** (JOURNAL 61).

- [ ] `[?]` **Le CNPO (oeufs) est-il dans le perimetre ?**
      `cartographie_filiere.xlsx` le marque « HORS PERIMETRE », alors que
      Vincent a confirme « Oeufs de France » le 25/08. Aucun CNPO n'est retenu
      en pratique, donc rien n'est casse — mais les deux sources se
      contredisent (JOURNAL 60).

- [ ] `[?]` **Reecrire METHODOLOGIE 9.2 ?** La section prescrit un tirage
      aleatoire de createurs, annotes exhaustivement. **MESURE du 27/08 : c'est
      arithmetiquement impossible.** A 1,35 % de chaines portant une preuve
      forte, il en faudrait annoter **739 a la main pour en obtenir dix**, et
      2 217 pour trente. Une note d'avertissement a ete posee dans la section.
      Recommandation : passer a la capture-recapture (section 9.3), pour
      laquelle les chaines des lobbies fournissent enfin une seconde source
      independante. **A trancher par Vincent** (JOURNAL 62).
      **Prealable : definir la population dans laquelle tirer.**
- [ ] `[?]` **Qui publie le registre** : Vincent en nom propre, une association
      existante, une nouvelle structure ? Determine la posture juridique et
      bloque toute publication.
- [ ] `[?]` **Ecrit-on aux createurs avant publication ?** Proposition de
      Vincent le 25/08 : cela vaut verification et droit de reponse. A
      trancher : a partir de quand, et sous quelle signature ?
- [ ] `[?]` **Unite de la base** : le post, la campagne, ou le **segment** ?
      Une seule video peut porter trois annonceurs a trois endroits
      differents (JOURNAL 20.2).
- [ ] `[?]` **Rattacher les comptes aux personnes.** La colonne `personne` de
      COMPTES.xlsx est vide a dessein : le rapprochement est un jugement
      humain, jamais une deduction par le nom (risque d'homonyme).
- [ ] `[?]` **Extension de navigateur** — retenue comme composant du projet
      (METHODOLOGIE 14bis.5), a construire APRES le registre.
- [ ] `[?]` **Reconstruire le lien createur → marque sur TikTok.** L'API ne le
      donne pas, mais chaque contenu porte l'URL de sa video. Vaut-il le cout
      de les lire ?
- [ ] `[?]` **Produire des jeux de donnees pour la recherche.** Les
      collaborations anciennes ne servent pas au plaidoyer direct mais restent
      utiles a la recherche. A cadrer : licence, format, anonymisation.
- [ ] `[?]` **ARPP** — demander les donnees brutes de leur Observatoire. Refus
      probable, mais un refus est lui-meme documentable.
- [ ] `[?]` **AGRIP** — les beneficiaires des subventions europeennes de
      promotion. Devenu concret : la campagne « En Mode Actif » du CNIEL est
      declaree **cofinancee par l'UE**.

---

## Fait

**22 aout** — recherche de faisabilite ; cartographie de la filiere en
12 feuilles ; lecture du schema de l'Observatoire Citoyen ; constat que
l'export de Paye Ton Influence ne donne que des agregats ; extraction du
sous-graphe viande/lait du repertoire HATVP.

**23 aout** — confirme que la declaration « communication commerciale » de
YouTube est lisible par un programme, gratuitement et sans compte.

**24 aout** — test croise refait et **enregistre** (les chiffres du 23/08
etaient irreproductibles) ; **premier cas reel trouve**, Inoxtag x CNIEL ;
un troisieme signal identifie ; listes d'abonnements Instagram relevees par
Vincent (538 comptes) ; documentation scindee en ETAT / HYPOTHESES /
METHODOLOGIE / JOURNAL ; projet mis sur GitHub ; affiliation UCD verifiee
(morte) ; perimetre de collecte tranche (option A, le CNIEL) ; les 12 videos
d'Inoxtag arbitrees ; sites des commanditaires fouilles — 92 recettes
creditees chez INAPORC, et le cas Twitch avec Gastronogeek et LeBouseuh.

**25 aout** — API TikTok obtenue et exploitee ; 8 061 createurs francais a
partenariat declare ; **Vincent annote les 271 candidats** — le jeu de
reference qui manquait depuis le debut ; precision mesuree a 25 %, portee a
77 % par la regle D ; moisson de 35 612 videos YouTube ; registre consolide
des comptes ; croisement TikTok → YouTube, 2 187 chaines.

**26 aout** — mesure decisive : la semence « abonnements des vitrines » est
**treize fois** plus productive que la semence TikTok ; la regle D se revele
etre une regle du CNIEL, aveugle sur les autres interprofessions ; deux alias
inconnus decouverts, « En Mode Actif » et « Made in Viande » ; classeur unique
des taches de Vincent.
