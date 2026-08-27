"""
Quels comptes sont des medias, et doivent etre ecartes des candidats.

POURQUOI CE MODULE EXISTE

La liste etait ecrite **dans le code, en deux copies differentes** —
`nettoyer_detections.py` et `moissonner_chaines_lobbies.py` — qui avaient
commence a diverger. Vincent ne pouvait pas l'amender sans passer par moi,
alors que c'est exactement le genre de jugement qui lui revient : savoir si un
compte francais est un media est une question de contexte, pas de code.

Elle vit desormais dans la feuille `Medias` de `cartographie_filiere.xlsx`.
Il ajoute une ligne, l'outil suit.

C'est la meme correction que pour la table d'alias et pour le perimetre : **ce
que Vincent doit pouvoir changer ne doit pas etre en dur.**

LA RESERVE, QUI COMPTE

Un media **peut** etre remunere par un lobby, et ce serait un fait
interessant. Mais c'est une autre enquete — celle des partenariats de presse —
et melanger les deux noierait les deux : les medias parlent de viande et de
lait tout le temps, pour des raisons journalistiques, et ils produiraient
l'essentiel du bruit.

Ecarter n'est donc pas juger. C'est mettre de cote une question qui merite
d'etre posee separement.
"""

import sys
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CARTO = RACINE / "cartographie" / "cartographie_filiere.xlsx"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir

# Filet de securite si le classeur est absent ou illisible. La source de verite
# reste la feuille `Medias` ; ceci evite seulement qu'un outil tourne sans
# aucun filtre et inonde Vincent de candidats mediatiques.
SECOURS = {
    "le monde", "le parisien", "le figaro", "liberation", "franceinfo",
    "bfmtv", "tf1", "m6", "konbini", "brut", "lequipe", "top chef",
}

_cache = None


def medias(recharger=False):
    """Formes aplaties des comptes a ecarter. Lue une fois, puis mise en cache."""
    global _cache
    if _cache is not None and not recharger:
        return _cache
    noms = set(SECOURS)
    try:
        import openpyxl
        wb = openpyxl.load_workbook(CARTO, read_only=True, data_only=True)
        if "Medias" in wb.sheetnames:
            ws = wb["Medias"]
            entete = None
            for i, ligne in enumerate(ws.iter_rows(values_only=True), 1):
                premier = str(ligne[0] or "").strip()
                if premier == "nom_du_media":
                    entete = i
                    continue
                if entete and premier:
                    noms.add(premier)
        wb.close()
    except Exception as e:
        print(f"  feuille Medias illisible ({type(e).__name__}), "
              f"liste de secours utilisee", file=sys.stderr)
    _cache = {aplatir(n) for n in noms if aplatir(n)}
    return _cache


def est_media(nom):
    """Ce compte est-il un media, une emission ou une plateforme ?

    Comparaison sur la forme aplatie ET egalite exacte : un media ne doit pas
    ecarter un createur dont le nom le contient. « Le Monde a L'Envers » est
    une chaine de createurs, pas Le Monde.
    """
    n = unicodedata.normalize("NFKD", str(nom or "").lower())
    n = "".join(c for c in n if not unicodedata.combining(c)).strip()
    return n in {m for m in medias()} or aplatir(n) in medias()


if __name__ == "__main__":
    m = medias()
    print(f"{len(m)} formes de medias chargees depuis la feuille « Medias »")
    for essai in ("Le Monde", "Le Monde à L'Envers", "Wimbledon", "Inoxtag"):
        print(f"   {essai:<24s} -> {'ECARTE' if est_media(essai) else 'garde'}")
