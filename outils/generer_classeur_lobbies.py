"""
Fabrique cartographie/CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx.

CE QUE CE CLASSEUR TRANCHE

`moissonner_chaines_lobbies.py` extrait les createurs nommes dans les videos
publiees par les lobbies eux-memes — la source la plus directe du projet,
puisque c'est le commanditaire qui parle.

Il les trouve par deux voies, et **on ne sait pas encore ce que chacune vaut** :

  - « compte connu » : le nom correspond a un compte du registre. A l'oeil,
    cette voie donne des personnes — Pierre Chomet, Morgan VS, Mister V.
  - « motif dans le titre » : « feat X », « avec X », « X : ... ». A l'oeil,
    cette voie donne surtout des noms de SERIES — « Interview Metiers »,
    « Milk Check », « Generation XYZ ».

« A l'oeil » n'est pas une mesure. Ce classeur la produit : Vincent tranche,
et on saura s'il faut garder la seconde voie, la durcir, ou l'abandonner.

Un tri est deja fait en amont : les comptes des lobbies eux-memes et les
medias sont ecartes avant d'arriver ici.

Colonnes vertes = a remplir. Le reste ne se touche pas.

Usage :  python outils/generer_classeur_lobbies.py
"""

import csv
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CIBLE = RACINE / "cartographie" / "CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx"

VERT = PatternFill("solid", fgColor="D9EAD3")
GRIS = PatternFill("solid", fgColor="EFEFEF")
ENTETE = PatternFill("solid", fgColor="434343")

CHOIX = [
    "oui, c'est un createur",
    "non, c'est un nom de serie ou de campagne",
    "non, c'est une marque ou un label",
    "non, c'est un media",
    "je ne sais pas",
]


def main():
    fichiers = sorted(RECHERCHE.glob("chaines_lobbies_*.csv"))
    if not fichiers:
        print("Aucun chaines_lobbies_*.csv — lancer d'abord "
              "moissonner_chaines_lobbies.py", file=sys.stderr)
        return 1
    source = fichiers[-1]

    par_createur = defaultdict(lambda: {"n": 0, "entites": set(), "via": "",
                                        "exemple": "", "url": "", "date": ""})
    with source.open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            noms = l["createurs_nommes"].split(" | ")
            vias = l.get("reconnu_par", "").split(" | ")
            for i, nom in enumerate(noms):
                if not nom.strip():
                    continue
                d = par_createur[nom]
                d["n"] += 1
                d["entites"].add(l["entite"])
                if not d["via"]:
                    d["via"] = vias[i] if i < len(vias) else ""
                if not d["url"]:
                    d["exemple"] = l["titre"]
                    d["url"] = l["url"]
                    d["date"] = l.get("publiee", "")

    # Les cas les plus solides d'abord : voie « compte connu », puis nombre de
    # videos. Vincent juge le plus important tant qu'il est frais.
    lignes = sorted(par_createur.items(),
                    key=lambda x: (not x[1]["via"].startswith("compte connu"),
                                   -x[1]["n"], x[0].lower()))

    wb = Workbook()
    ws = wb.active
    ws.title = "createurs"

    intro = [
        "CE QUE TU AS SOUS LES YEUX",
        "",
        "Chaque ligne est un nom trouve dans le titre ou la description d'une "
        "video publiee par un lobby lui-meme.",
        "C'est la source la plus directe du projet : ce n'est pas nous qui "
        "deduisons une collaboration, c'est le commanditaire qui la publie.",
        "",
        "CE QU'ON TE DEMANDE",
        "",
        "Une seule question, colonne verte : est-ce un createur de contenu, ou "
        "autre chose ?",
        "Beaucoup de ces noms sont des titres de series (« Milk Check ») ou des "
        "labels (« Label Rouge »). L'outil ne sait pas les distinguer.",
        "",
        "POURQUOI CA COMPTE",
        "",
        "L'outil a deux facons de reconnaitre un nom, indiquee colonne "
        "« Comment on l'a trouve ».",
        "Tes reponses mesureront ce que chacune vaut. Si « motif dans le titre » "
        "ne donne que des series, on l'abandonne.",
        "Les lignes sur fond gris viennent de cette voie-la, les blanches de "
        "l'autre.",
        "",
        "TU PEUX T'ARRETER EN COURS DE ROUTE",
        "",
        "Les lignes sont triees par valeur : les plus solides en haut. Juger les "
        "60 premieres suffit a mesurer les deux voies.",
        "Le reste est la pour ne rien perdre, pas pour t'occuper une soiree.",
        "",
        "ATTENTION",
        "",
        "Etre nomme par un lobby etablit une collaboration, PAS une "
        "remuneration. La question du paiement vient apres.",
        "",
    ]
    for i, ligne in enumerate(intro, 1):
        c = ws.cell(row=i, column=1, value=ligne)
        c.font = Font(bold=bool(ligne) and ligne.isupper(), size=11)
    depart = len(intro) + 2

    colonnes = [
        ("N", 5), ("Nom trouve", 34), ("Commanditaire", 20),
        ("Comment on l'a trouve", 40), ("Videos", 8), ("Date", 11),
        ("Titre de la video", 52), ("Regarder", 13),
        ("EST-CE UN CREATEUR ?", 34), ("Ton commentaire", 34),
    ]
    for j, (titre, largeur) in enumerate(colonnes, 1):
        c = ws.cell(row=depart, column=j, value=titre)
        c.fill = ENTETE
        c.font = Font(bold=True, color="FFFFFF", size=11)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = largeur
    ws.row_dimensions[depart].height = 32

    dv = DataValidation(type="list", formula1='"' + ",".join(CHOIX) + '"',
                        allow_blank=True)
    ws.add_data_validation(dv)

    for i, (nom, d) in enumerate(lignes, 1):
        r = depart + i
        connu = d["via"].startswith("compte connu")
        valeurs = [i, nom, ", ".join(sorted(d["entites"])), d["via"], d["n"],
                   d["date"], d["exemple"][:150], "", "", ""]
        for j, v in enumerate(valeurs, 1):
            c = ws.cell(row=r, column=j, value=v)
            c.alignment = Alignment(vertical="top", wrap_text=(j in (2, 4, 7)))
            if j in (9, 10):
                c.fill = VERT
            elif not connu:
                c.fill = GRIS
        lien = ws.cell(row=r, column=8, value="voir la video")
        if d["url"]:
            lien.hyperlink = d["url"]
        lien.font = Font(color="1155CC", underline="single")
        dv.add(ws.cell(row=r, column=9))
        ws.row_dimensions[r].height = 30

    ws.freeze_panes = ws.cell(row=depart + 1, column=1)

    n_connu = sum(1 for _n, d in lignes if d["via"].startswith("compte connu"))
    lg = wb.create_sheet("d'ou ca vient")
    provenance = [
        f"Source : {source.name}",
        f"Genere le {date.today().isoformat()} par "
        f"outils/generer_classeur_lobbies.py",
        "",
        f"Noms distincts : {len(lignes)}",
        f"  dont voie « compte connu » (fond blanc) : {n_connu}",
        f"  dont voie « motif dans le titre » (fond gris) : "
        f"{len(lignes) - n_connu}",
        "",
        "Deja ecartes en amont, sans te les montrer :",
        "  - les comptes des lobbies eux-memes (volaillefrancaise se",
        "    reconnaissait 36 fois dans ses propres titres) ;",
        "  - les medias et emissions (Le Monde, Top Chef, C a vous) ;",
        "  - les formes de moins de huit caracteres ;",
        "  - les formes que plusieurs comptes revendiquent : 2 357 ecartees,",
        "    soit 30 % de la table. C'etaient elles qui attribuaient",
        "    « Morgan VS » a un compte nomme morganabbou.",
    ]
    for i, ligne in enumerate(provenance, 1):
        lg.cell(row=i, column=1, value=ligne)
    lg.column_dimensions["A"].width = 78

    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"{len(lignes)} noms a trancher — {n_connu} par compte connu, "
          f"{len(lignes) - n_connu} par motif")
    return 0


if __name__ == "__main__":
    sys.exit(main())
