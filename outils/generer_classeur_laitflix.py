"""
Fabrique cartographie/LAITFLIX_A_VERIFIER.xlsx.

CE QUE C'EST

Le catalogue LAIT'FLIX du CNIEL, releve sur produits-laitiers.com le 28/08 —
la page que Vincent avait signalee comme « une mine d'or » le 26, et que je
n'avais pas ouverte.

107 videos, 12 series, des dizaines de createurs nommes. Le CNIEL les publie
lui-meme : ce n'est pas une inference.

POURQUOI IL FAUT LE VERIFIER

La liste vient d'une **lecture automatique de la page**. Une lecture
automatique peut mal decouper un nom, en fusionner deux, ou en inventer un.
Aucune ligne ne doit entrer dans le registre sans passer par ici.

CE QUE CETTE SOURCE A REVELE

Neuf des douze series sont ABSENTES de la chaine YouTube `@lesproduitslaitiers`
qu'on avait moissonnee. Moissonner la chaine officielle d'un lobby ne suffit
donc pas : il diffuse aussi par les chaines des createurs qu'il paie, et la, il
n'y a aucune trace cote commanditaire — sauf sur son propre site.

Usage :  python outils/generer_classeur_laitflix.py
"""

import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

RACINE = Path(__file__).resolve().parent.parent
CIBLE = RACINE / "cartographie" / "LAITFLIX_A_VERIFIER.xlsx"

VERT = PatternFill("solid", fgColor="D9EAD3")
ENTETE = PatternFill("solid", fgColor="434343")

# Sans virgule : Excel s'en sert comme separateur dans une liste en ligne.
CHOIX = [
    "oui — createur de contenu",
    "oui — chef ou restaurateur",
    "oui — humoriste ou rappeur",
    "oui — mais je ne le connais pas",
    "non — ce n'est pas une personne",
    "nom mal lu — voir mon commentaire",
    "je ne sais pas",
]

CATALOGUE = [
    ("CHAUD!", 6, ["Quentin Mauro", "Jorick Dorignac", "Guillaume Sanchez",
                   "Jeffrey Cagnes", "Philippine Jaillet", "Morgan VS",
                   "GMK", "Ragnar Le Breton"]),
    ("Billy et Amine decouvrent les specialites de nos regions", 5,
     ["Inoxtag", "Billy", "Amine (@Aminematue)"]),
    ("La ferme des celebrites", 10,
     ["Redouane Bougheraba", "Nino Arial", "Agriskippy", "Loris",
      "Danielle", "Denitsa", "Golo & Ritchie"]),
    ("Mister V : les copains au lait", 3, ["Mister V"]),
    ("La Carotte d'Avner", 2,
     ["Avner", "Morgan VS", "Anthony Lastella", "Hugo Tout Seul"]),
    ("Morgan decouvre les AOP", 7, ["Morgan VS"]),
    ("Humour", 14,
     ["Jamy", "Medine", "Mister V", "Redouane Bougheraba", "Hakim Jemili",
      "Pierre Chomet", "TOKOU"]),
    ("Le Tour du Monde de Loris", 10, ["Loris (LORIS GIULIANO)"]),
    ("Le Tour de France de Loris", 20, ["Loris (LORIS GIULIANO)"]),
    ("Frere !", 15, ["TOKOU", "Vinz"]),
    ("Check Food", 10,
     ["Gaelle Garcia Diaz", "Alkpote", "KIKESA", "Jok'air", "Roi Heenok",
      "Philippe Katerine", "Caballero & JeanJass", "Mehdi Maizi", "Mister V",
      "Seth Gueko", "47Ter", "Matou", "P.Prod", "Haristone", "Medine",
      "Youssoupha", "Lino", "Oxmo Puccino", "Remy", "Pirate", "S.Pri Noir",
      "Still Fresh", "Chef Pincemin"]),
    ("Myriam met du beurre dans tes epinards", 5, ["Myriam", "Sido Cuisto"]),
]

INTRO = [
    "CE QUE TU AS SOUS LES YEUX",
    "",
    "Le catalogue LAIT'FLIX du CNIEL, releve sur la page que TU m'avais "
    "signalee le 26/08 et que je n'avais pas ouverte.",
    "107 videos, 12 series. Le CNIEL les publie lui-meme : ce n'est pas une "
    "inference, c'est le commanditaire qui l'annonce.",
    "",
    "POURQUOI IL FAUT VERIFIER",
    "",
    "Cette liste vient d'une LECTURE AUTOMATIQUE de la page. Elle peut mal "
    "decouper un nom, en fusionner deux, ou en inventer un.",
    "Aucune ligne n'entrera dans le registre sans ton passage.",
    "",
    "CE QUE CETTE SOURCE A REVELE",
    "",
    "Neuf des douze series sont ABSENTES de la chaine YouTube du CNIEL qu'on "
    "avait moissonnee.",
    "Moissonner la chaine officielle d'un lobby ne suffit donc pas : il "
    "diffuse aussi par les chaines des createurs qu'il paie.",
    "",
    "CE QU'ON TE DEMANDE",
    "",
    "Pour chaque nom : est-ce bien une personne, et laquelle ? Si le nom est "
    "mal lu, corrige-le en commentaire.",
    "",
]


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "createurs"

    for i, l in enumerate(INTRO, 1):
        c = ws.cell(row=i, column=1, value=l)
        c.font = Font(bold=bool(l) and l.isupper(), size=11)
    depart = len(INTRO) + 2

    colonnes = [("N", 5), ("Nom releve", 32), ("Serie", 42),
                ("Videos dans la serie", 12), ("EST-CE UNE PERSONNE ?", 34),
                ("Ton commentaire", 44)]
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

    n = 0
    for serie, videos, createurs in CATALOGUE:
        for createur in createurs:
            n += 1
            r = depart + n
            for j, v in enumerate([n, createur, serie, videos, "", ""], 1):
                cell = ws.cell(row=r, column=j, value=v)
                cell.alignment = Alignment(vertical="top",
                                           wrap_text=(j in (2, 3)))
                if j in (5, 6):
                    cell.fill = VERT
            dv.add(ws.cell(row=r, column=5))
            ws.row_dimensions[r].height = 22
    ws.freeze_panes = ws.cell(row=depart + 1, column=1)

    lg = wb.create_sheet("d'ou ca vient")
    provenance = [
        "Source : https://www.produits-laitiers.com/laitflix/divertissement/",
        f"Releve le {date.today().isoformat()} par lecture automatique",
        "Signale par Vincent le 26/08 : « Le site est une mine d'or »",
        "",
        f"{len(CATALOGUE)} series, {sum(v for _s, v, _c in CATALOGUE)} videos,",
        f"{n} noms de createurs a verifier.",
        "",
        "Series presentes dans la moisson YouTube du CNIEL : CHAUD!,",
        "Les copains au lait, Myriam met du beurre. Les NEUF autres n'y sont",
        "pas — elles vivent sur le site du CNIEL, ou sur les chaines des",
        "createurs eux-memes.",
    ]
    for i, l in enumerate(provenance, 1):
        lg.cell(row=i, column=1, value=l)
    lg.column_dimensions["A"].width = 78

    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"{len(CATALOGUE)} series, {n} noms a verifier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
