"""
Apparier un alias a un texte, sans fabriquer de mots qui n'existent pas.

LE PROBLEME, EN UNE LIGNE

Tout le projet compare des chaines **aplaties** : accents retires, espaces et
ponctuation supprimes, tout en minuscules. C'est indispensable — « Les Produits
Laitiers », « lesproduitslaitiers » et « @LesProduits-Laitiers » doivent se
reconnaitre.

Mais l'aplatissement **colle les mots voisins**, et fabrique des chaines qui
n'existent nulle part dans le texte reel :

    « je te ramene du charbon et de la viande frerot »
        -> « ...etdelaviandefrerot... »   contient  « laviandefr »   (INTERBEV)

    « no clippant »        -> « noclippant »   contient  « clipp »   (CLIPP)
    « Clip para »          -> « clippara »     contient  « clipp »

Trois faux positifs mesures, aux entrees 45 et 59 du journal.

CE QUI NE MARCHE PAS

**La longueur minimale.** C'est la parade retenue le 27/08 au matin — huit
caracteres — et elle n'attrape pas `laviandefr`, qui en fait dix. Elle ecarte
du bruit, elle ne traite pas la cause.

CE QUI MARCHE

Le texte aplati a perdu ses espaces : la coupure n'y est plus visible. Mais si
l'on garde, pour chaque caractere aplati, **sa position dans le texte
d'origine**, il suffit de regarder le caractere qui suit la correspondance dans
le texte VRAI. S'il est alphanumerique, la correspondance mord sur le mot
suivant, et c'est un artefact. Idem en amont.

MESURE — sur le second rideau, ce garde-fou a retire exactement le cas
« la viande frerot » et aucun autre.

CE QUE CE MODULE NE FAIT PAS

Il ne juge pas si la mention est commerciale. « Un beau petit foie gras »
offert pour un pot de depart passe la frontiere de mot sans probleme : c'est
une vraie occurrence du terme, dans un contexte sans rapport. Ce tri-la revient
au voisinage commercial et, au bout du compte, a un humain.
"""

import unicodedata


def aplatir(texte):
    """Minuscules, sans accents, sans rien qui ne soit lettre ou chiffre."""
    t = unicodedata.normalize("NFKD", str(texte or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return "".join(c for c in t if c.isalnum())


def aplatir_avec_index(texte):
    """Rend (texte aplati, index) ou index[i] est la position d'origine.

    Sans cet index, une position trouvee dans le texte aplati ne designe pas la
    meme chose dans le texte d'origine — et l'ecart grandit a mesure qu'on
    avance. Couper un extrait a la position aplatie affiche un passage sans
    rapport : fait trois fois le 27/08, dont une en presentant un resultat.
    """
    texte = str(texte or "")
    plat, index = [], []
    for position, caractere in enumerate(texte):
        c = unicodedata.normalize("NFKD", caractere)
        c = "".join(x for x in c if not unicodedata.combining(x)).lower()
        for lettre in c:
            if lettre.isalnum():
                plat.append(lettre)
                index.append(position)
    return "".join(plat), index


def coupe_un_mot(texte, index, debut_plat, longueur):
    """La correspondance mord-elle sur un mot voisin du texte d'origine ?"""
    if not index or debut_plat >= len(index):
        return True
    fin_plat = debut_plat + longueur - 1
    if fin_plat >= len(index):
        return True
    apres = index[fin_plat] + 1
    if apres < len(texte) and texte[apres].isalnum():
        return True
    avant = index[debut_plat] - 1
    if avant >= 0 and texte[avant].isalnum():
        return True
    return False


def trouver(texte, forme, plat=None, index=None):
    """Premiere occurrence de `forme` qui ne morde pas sur un mot voisin.

    Rend la position dans le texte D'ORIGINE, ou -1. `plat` et `index` peuvent
    etre fournis pour ne pas recalculer sur chaque forme d'une table d'alias.
    """
    if plat is None or index is None:
        plat, index = aplatir_avec_index(texte)
    depart = plat.find(forme)
    while depart >= 0:
        if not coupe_un_mot(texte, index, depart, len(forme)):
            return index[depart]
        depart = plat.find(forme, depart + 1)
    return -1


def extrait_autour(texte, position, avant=200, apres=320):
    """La fenetre de texte autour d'une position, pour qu'un humain juge."""
    if position < 0:
        return ""
    debut = max(0, position - avant)
    return (("..." if debut > 0 else "")
            + texte[debut:position + apres].strip())
