"""
Fabrique cartographie/CREATEURS_DANS_LES_ANNONCES.xlsx.

CE QUE CE CLASSEUR MESURE

`createurs_dans_annonces.py` trouve des createurs nommes dans des annonces
payees par les commanditaires. Il les trouve par TROIS voies, et on ignore ce
que chacune vaut :

    pseudo ecrit tel quel        le plus sur a priori
    compte connu du registre     sur, mais peut confondre des homonymes
    vocabulaire de collaboration douteux — « avec X » attrape des mots courants

C'est la meme situation que pour les chaines YouTube des lobbies (JOURNAL 55),
et elle se tranche de la meme facon : Vincent juge, on mesure.

L'ordre des lignes suit cette hierarchie presumee, et Vincent peut s'arreter
quand il veut : les premieres lignes sont les plus informatives.

Colonnes vertes = a remplir.

Usage :  python outils/generer_classeur_annonces.py
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
CIBLE = RACINE / "cartographie" / "CREATEURS_DANS_LES_ANNONCES.xlsx"

VERT = PatternFill("solid", fgColor="D9EAD3")
GRIS = PatternFill("solid", fgColor="EFEFEF")
ENTETE = PatternFill("solid", fgColor="434343")

# Sans virgule : Excel s'en sert comme separateur dans une liste en ligne.
CHOIX = [
    "oui — createur remunere par ce commanditaire",
    "oui — createur mais lien non commercial",
    "non — c'est la marque elle-meme",
    "non — mot courant ou faux positif",
    "non — c'est un media",
    "je ne sais pas",
]

RANG = {"pseudo ecrit tel quel": 0, "compte connu du registre": 1,
        "vocabulaire de collaboration": 2}


def main():
    fichiers = sorted(RECHERCHE.glob("createurs_annonces_*.csv"))
    if not fichiers:
        print("Aucun createurs_annonces_*.csv.", file=sys.stderr)
        return 1

    par = defaultdict(lambda: {"n": 0, "pages": set(), "voie": "", "date": "",
                               "extrait": "", "url": "", "plateformes": ""})
    with fichiers[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            d = par[l["createur"]]
            d["n"] += 1
            d["pages"].add(l["page_annonceuse"])
            if not d["voie"] or RANG.get(l["voie"], 9) < RANG.get(d["voie"], 9):
                d["voie"] = l["voie"]
                d["extrait"] = l["extrait"]
                d["url"] = l["url_apercu"]
                d["date"] = l["debut_diffusion"]
                d["plateformes"] = l["plateformes"]

    lignes = sorted(par.items(),
                    key=lambda x: (RANG.get(x[1]["voie"], 9), -x[1]["n"],
                                   x[0].lower()))

    wb = Workbook()
    ws = wb.active
    ws.title = "createurs"

    intro = [
        "CE QUE TU AS SOUS LES YEUX",
        "",
        "Chaque ligne est un nom trouve dans une PUBLICITE PAYEE par un "
        "commanditaire de la filiere.",
        "C'est la preuve la plus forte du projet : l'annonceur a paye Meta pour "
        "diffuser un contenu qui nomme ce createur.",
        "",
        "CE QUE CA N'ETABLIT PAS",
        "",
        "Que l'argent soit alle AU CREATEUR. Une marque peut promouvoir un "
        "contenu sans avoir remunere celui qui y figure.",
        "",
        "CE QU'ON TE DEMANDE",
        "",
        "Une question par ligne. Les lignes sont triees par fiabilite presumee "
        "de la methode de detection.",
        "Juger les 80 premieres suffit a mesurer les trois voies.",
        "",
        "LES TROIS VOIES",
        "",
        "  pseudo ecrit tel quel        — un @pseudo apparait dans l'annonce",
        "  compte connu du registre     — le nom correspond a un compte deja "
        "repere",
        "  vocabulaire de collaboration — « avec X » ou « merci a X » (fond "
        "gris : le plus douteux)",
        "",
    ]
    for i, l in enumerate(intro, 1):
        c = ws.cell(row=i, column=1, value=l)
        c.font = Font(bold=bool(l) and l.isupper(), size=11)
    depart = len(intro) + 2

    colonnes = [("N", 5), ("Createur trouve", 30), ("Annonceur(s)", 34),
                ("Comment on l'a trouve", 30), ("Annonces", 9), ("Date", 11),
                ("Plateformes", 20), ("Ce que dit l'annonce", 62),
                ("Voir", 10), ("TON VERDICT", 38), ("Ton commentaire", 30)]
    for j, (titre, largeur) in enumerate(colonnes, 1):
        c = ws.cell(row=depart, column=j, value=titre)
        c.fill = ENTETE
        c.font = Font(bold=True, color="FFFFFF", size=11)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = largeur
    ws.row_dimensions[depart].height = 32

    lst = wb.create_sheet("listes")
    for i, v in enumerate(CHOIX, 1):
        lst.cell(row=i, column=1, value=v)
    lst.sheet_state = "hidden"
    dv = DataValidation(type="list", allow_blank=True,
                        formula1=f"=listes!$A$1:$A${len(CHOIX)}")
    ws.add_data_validation(dv)

    for i, (nom, d) in enumerate(lignes, 1):
        r = depart + i
        douteux = d["voie"] == "vocabulaire de collaboration"
        valeurs = [i, nom, ", ".join(sorted(d["pages"]))[:120], d["voie"],
                   d["n"], d["date"], d["plateformes"], d["extrait"][:300],
                   "", "", ""]
        for j, v in enumerate(valeurs, 1):
            c = ws.cell(row=r, column=j, value=v)
            c.alignment = Alignment(vertical="top", wrap_text=(j in (2, 3, 8)))
            if j in (10, 11):
                c.fill = VERT
            elif douteux:
                c.fill = GRIS
        lien = ws.cell(row=r, column=9, value="voir l'annonce")
        if d["url"]:
            lien.hyperlink = d["url"]
        lien.font = Font(color="1155CC", underline="single")
        dv.add(ws.cell(row=r, column=10))
        ws.row_dimensions[r].height = 46

    ws.freeze_panes = ws.cell(row=depart + 1, column=1)

    lg = wb.create_sheet("d'ou ca vient")
    compte = defaultdict(int)
    for _n, d in lignes:
        compte[d["voie"]] += 1
    for i, l in enumerate([
            f"Source : {fichiers[-1].name}",
            f"Genere le {date.today().isoformat()}",
            "",
            f"Createurs distincts : {len(lignes)}",
    ] + [f"  {v} : {n}" for v, n in sorted(compte.items(), key=lambda x: -x[1])]
        + ["",
           "Deja ecartes en amont, sans te les montrer :",
           "  - les medias et emissions ;",
           "  - les noms cites par plus de six commanditaires differents :",
           "    personne ne travaille pour six marques concurrentes, donc",
           "    c'est un mot courant. « jour » ressortait 369 fois ;",
           "  - les pages qui se citent elles-memes."], 1):
        lg.cell(row=i, column=1, value=l)
    lg.column_dimensions["A"].width = 78

    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"{len(lignes)} createurs a juger")
    for v, n in sorted(compte.items(), key=lambda x: -x[1]):
        print(f"   {n:>4d}  {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
