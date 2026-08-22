# Paye Ton Influence — source evaluee et ecartee

Evalue le 22 aout 2026. **Ce dossier ne contient volontairement aucune donnee.**

## Ce qui a ete teste

L'observatoire de l'association (https://observatoire.payetoninfluence.org/)
affiche un tableau de bord avec des boutons d'export en CSV, JSON et XLSX.
Six exports ont ete telecharges le 22/08/2026.

**Resultat : chaque fichier pesait entre 10 et 45 octets et ne contenait qu'une
seule valeur agregee** — celle affichee sur la tuile du tableau de bord. Exemple
integral d'un fichier :

    Valeurs distinctes de post_id
    185 425

Le bouton exporte la tuile, pas la table qui la sous-tend. Il n'existe pas de
jeu de donnees telechargeable. Les fichiers ont ete supprimes le 22/08 : ils
n'apportaient rien et encombraient le dossier.

## Ce qu'on en garde quand meme

Deux choses utiles ont survecu a ce test.

**1. Leur schema**, deduit des intitules de colonnes exportes :
`account_id`, `post_id`, `brand_name`, `label`.

**2. Leurs ordres de grandeur**, qui servent a dimensionner notre propre
collecte :

| Indicateur | Valeur |
|---|---|
| Comptes suivis | 1 147 |
| Posts analyses | 185 425 |
| Posts en collaboration | 7 518 (4,1 %) |
| Marques identifiees | 1 308 |
| Marques classees "impact negatif" | 10 % |
| Posts sponsorises "impact negatif" | 18 % |
| Repartition | TikTok 5 036 collabs / Instagram 1 449 / YouTube 1 033 |

Le chiffre de 1 033 collaborations sur ~31 000 videos YouTube, soit 3,3 %, est
tres probablement sous-estime : leur detection lit uniquement la description du
post, alors que sur YouTube la mention de partenariat est le plus souvent orale
ou incrustee a l'image. C'est l'un des arguments qui nous a fait retenir
SponsorBlock pour YouTube.

## Pourquoi on ne leur demande pas leurs donnees

Decide avec Vincent le 22/08 : il n'y a pas de jeu de donnees a recuperer, et
leur methode — detection par expression reguliere sur la description, sans
relecture humaine, marque extraite en texte libre sans table d'entites — ne
correspond pas a ce qu'on veut faire.

**En revanche l'association reste un contact prioritaire**, comme partenaire de
diffusion et non comme source. Ils travaillent deja les sujets Interbev et
Cniel, ils ont obtenu que Squeezie exprime publiquement des regrets sur sa
collaboration avec le lobby laitier, et leur audience est exactement celle que
notre registre doit atteindre. Voir TODO.md, section contacts.
