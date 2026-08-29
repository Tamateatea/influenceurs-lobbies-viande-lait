"""
Une seule question, posee une seule fois : est-ce un createur, ou celui qui paie ?

POURQUOI CE MODULE EXISTE

Le 29/08, Vincent ouvre le jeu de donnees et constate que la colonne
« influenceur » — la plus importante — contient des noms de marques : Maitre
CoQ, Justin Bridou, La Volaille Francaise, Les Produits Tripiers.

MESURE : **373 lignes sur 1 039, soit 36 %.**

Sa question : « si apres tout le travail qu'on a fait, on est toujours pas
capable de faire un dataset correct, c'est qu'on a encore beaucoup de travail,
ou bien qu'il va falloir revoir notre methode de fond en comble. »

LA REPONSE, ET ELLE N'EST NI L'UNE NI L'AUTRE

La regle « un commanditaire n'est pas un createur » avait deja ete ecrite
**trois fois**, chaque fois localement, chaque fois apres qu'un cas eut echappe :

    27/08  moissonner_chaines_lobbies.py   la chaine se citait elle-meme
    29/08  createurs_dans_annonces.py      @regilaitfr, @justinbridou_fr
    29/08  moissonner_chaines_lobbies.py   le TITRE de la chaine, « Le Porc Francais »

Et jamais dans le canal « description », qui prend le nom de la chaine ayant
publie la video. Quand une marque tient sa propre chaine YouTube et y parle de
ses produits, elle devenait un « influenceur ».

Ce n'est donc pas la methode qui est fausse. C'est qu'une regle a ete corrigee
trois fois a trois endroits au lieu d'etre ecrite une fois pour tous. Le projet
a deja fait ce mouvement quatre fois — `appariement.py` pour l'aplatissement,
`medias.py` pour les medias, `perimetre.py` pour le perimetre, `table_alias.py`
pour les alias — et a chaque fois la classe de defaut a disparu.

Ceci est le cinquieme.

CE QUE CE MODULE DECIDE, ET CE QU'IL NE DECIDE PAS

Il repond a : **ce nom designe-t-il un commanditaire ?** Il ne dit pas si la
personne est un influenceur au sens du projet — c'est une question de jugement,
elle revient a Vincent, et METHODOLOGIE 8 la traite.

Il ne dit pas non plus qu'une ligne est fausse. Une video publiee par la chaine
d'une marque est un fait interessant : c'est du contenu de marque, pas une
collaboration remuneree avec un tiers. Vincent l'a note lui-meme le 29/08 :
« c'est bien de ne pas exclure au cas ou ». Ces lignes sont donc **etiquetees**,
pas jetees.
"""

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir

# Suffixes et prefixes que les marques ajoutent a leur nom sur les reseaux.
# Sans eux, « @regilaitfr » ne se reconnait pas dans « Regilait ».
AFFIXES = ("fr", "france", "officiel", "official", "off", "pro", "professionnel",
           "professionnels", "shop", "store", "paris", "tv", "media", "group",
           "groupe", "le", "la", "les")

_cache = None


def noms_de_commanditaires(recharger=False):
    """Toutes les formes aplaties designant un commanditaire connu.

    Reunit la table d'alias — interprofessions, vitrines, marques, campagnes —
    et les entites qu'elle designe. Les groupes temoins sont inclus : ils sont
    hors sujet, mais ce ne sont pas davantage des createurs.
    """
    global _cache
    if _cache is not None and not recharger:
        return _cache
    import table_alias
    formes = set()
    termes = table_alias.charger(seuil=4, avec_marques=True,
                                 avec_hors_perimetre=True)
    for forme, (lisible, entite) in termes.items():
        formes.add(forme)
        formes.add(aplatir(lisible))
        formes.add(aplatir(entite.split(" (")[0]))
    _cache = {f for f in formes if len(f) >= 4}
    return _cache


def _variantes(plat):
    """Le nom, plus ses formes sans les affixes que les marques ajoutent."""
    formes = {plat}
    for a in AFFIXES:
        if plat.endswith(a) and len(plat) > len(a) + 3:
            formes.add(plat[:-len(a)])
        if plat.startswith(a) and len(plat) > len(a) + 3:
            formes.add(plat[len(a):])
    return formes


def est_un_commanditaire(nom, connus=None):
    """Ce nom designe-t-il un commanditaire plutot qu'un createur ?

    La comparaison va dans les DEUX sens et sur les variantes sans affixe :
    « @regilaitfr » et « Regilait » doivent se reconnaitre mutuellement. Une
    seule direction laissait passer tous les pseudos de marque suffixes.
    """
    plat = aplatir(nom)
    if len(plat) < 4:
        return False
    if connus is None:
        connus = noms_de_commanditaires()
    for forme in _variantes(plat):
        if forme in connus:
            return True
        # egalite seulement, jamais inclusion : « marie » ne doit pas rendre
        # vrai pour « Marie Dupont », et « lait » ne doit pas attraper
        # « Laitue ». L'inclusion produisait plus de degats qu'elle n'en evitait.
    return False


if __name__ == "__main__":
    connus = noms_de_commanditaires()
    print(f"{len(connus)} formes de commanditaires connues")
    for essai in ("Maître CoQ", "Justin Bridou", "La Volaille Française",
                  "@regilaitfr", "Produits Laitiers", "Aimez la viande",
                  "Inoxtag", "Mister V", "FlorianOnAir", "Squeezie",
                  "Marie Dupont", "LORIS GIULIANO"):
        r = "COMMANDITAIRE" if est_un_commanditaire(essai) else "createur"
        print(f"   {essai:<26s} -> {r}")
