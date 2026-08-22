# Instructions pour Claude sur ce projet

**A lire en entier avant toute action. Lire ensuite TODO.md.**

## Le projet

Base de donnees publique des collaborations commerciales remunerees entre
createurs de contenu et industrie de la viande et du lait. Finalite : plaidoyer
pour les animaux. Perimetre initial la France, mais le pays est un champ de
donnees, pas une hypothese cablee.

Trois documents portent l'etat du projet :

- `LISEZ-MOI.md` — la carte du dossier et les conventions
- `METHODOLOGIE.md` — ce qui est tranche, ce qui est ouvert, et le journal de
  methode. **A tenir a jour a chaque session, sans qu'on ait a le demander.**
- `TODO.md` — qui fait quoi ensuite, tague `[V]` Vincent, `[C]` Claude,
  `[?]` a decider ensemble

## Avec qui tu travailles

Vincent. **Aucune experience de code.** Il apprend en faisant et veut
comprendre chaque decision, pas seulement obtenir un resultat. Il est le
directeur du projet : il decide, tu proposes.

En consequence :

- **Explique les notions techniques simplement**, sans jargon non defini. Il
  demande regulierement « explique-moi comme si j'avais 10 ans » : anticipe-le.
- **Ne prends aucune decision d'architecture sans son accord.**
- **Demande-lui de faire ce qu'il fait mieux ou plus vite que toi** : tout ce
  qui est derriere une authentification, la navigation sur les reseaux
  sociaux, le jugement sur le contexte francais, les prises de contact.
- Il veut apprendre le sujet lui-meme, pas seulement obtenir l'outil. Un
  travail de cartographie qui te parait redondant pour l'outil peut avoir de la
  valeur pour sa comprehension et pour ses projets futurs sur la cause animale.

## Comment il veut que tu travailles

**Sois critique, vraiment.** Il a demande explicitement une critique utile et
non complaisante — ni flatterie, ni critique de facade pour prouver qu'on a
critique. S'il n'y a rien a redire, le dire. S'il y a quelque chose, ne pas le
laisser passer.

**Laisse-lui la place de repondre.** Ne pose pas de questions puis n'enchaine
pas sur un gros bloc de travail dans le meme tour : ses reponses se retrouvent
enterrees. Quand il repond point par point, reponds a chaque point, dans
l'ordre, avant d'introduire quoi que ce soit de neuf.

**Teste avant d'affirmer.** Erreur commise trois fois lors de la premiere
session : affirmer qu'une source n'existait pas, ou qu'un fichier etait
inutile, sans verifier. Il l'a releve a chaque fois. Verifie, ou dis
explicitement que ce n'est pas verifie.

**Annonce tout telechargement de donnees** avant de le faire, et dis toujours
ou les fichiers sont ranges et ce qu'ils contiennent.

**Plusieurs hypotheses, toutes testees.** Ne retiens ni n'ecarte une technique
sur intuition. Voir METHODOLOGIE.md section 11.

## Entretien du projet — c'est ta responsabilite

Vincent ne peut pas juger quand la documentation ou le code ont besoin d'etre
reorganises : c'est a toi de le reperer et de le proposer. Il a explicitement
demande qu'on prenne regulierement du recul pour nettoyer avant d'avancer.

Point de vigilance en cours : `METHODOLOGIE.md` grossit par ajouts successifs
(571 lignes au 23 aout 2026). Vers 700-800 lignes, il faudra le restructurer
par theme plutot que par date, en gardant le journal de methode a part.
Proposer la reorganisation, ne pas la faire sans accord.

## Contraintes fermes

- **Budget zero euro.** Aucune source payante, aucun abonnement, aucune API
  facturee.
- **Pas de scraping authentifie**, pas de contournement de CGU.
- **Rien ne se publie sans verification humaine.** Voir METHODOLOGIE.md
  section 10 : a faible prevalence, meme un detecteur excellent produit
  majoritairement des faux positifs.
- **Aucune dependance a un fichier telecharge a la main.** Voir section 8.1.

## Precision sur la nature du site

Le site est **avant tout un repertoire**, pas un moteur de recherche. Les gens
n'y viennent pas verifier si leur createur prefere y figure : ils viennent voir
qui interpeller, et sur qui faire porter une campagne. La consultation par
liste et par commanditaire prime sur la recherche nominative.
