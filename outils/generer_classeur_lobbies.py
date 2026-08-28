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

CE QUE LA SECONDE COLONNE DECIDE

Une seconde question a ete ajoutee le 27/08 : **quel type de personne** ?

Elle sert a une mesure qui n'a rien a voir avec la premiere. Le projet cherche
a savoir quelle part des collaborations il voit — et le tirage aleatoire
prescrit par METHODOLOGIE 9.2 s'est revele arithmetiquement impraticable : a
0,023 % de prevalence, il faudrait faire juger 130 000 videos.

La voie de rechange est la capture-recapture entre deux sources distinctes :
l'appariement de descriptions (36 createurs) et les chaines des lobbies
(42 createurs). **Elles n'ont qu'UN nom en commun.**

Deux lectures possibles, et les donnees ne les separent pas :

  1. la couverture du projet est mauvaise, chaque methode ne voyant qu'un coin ;
  2. les deux sources ne tirent pas dans la meme population — auquel cas la
     capture-recapture ne s'applique pas du tout.

Si les 42 noms sont surtout des chefs et des eleveurs, c'est la lecture 2. Si
ce sont des createurs de contenu comparables, c'est la lecture 1, et il faut
le savoir.

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

# ATTENTION AUX VIRGULES. Excel utilise la virgule comme separateur dans une
# liste deroulante ecrite en ligne : « non, c'est un nom de serie » devenait
# DEUX options, « non » et « c'est un nom de serie ». Vincent l'a signale le
# 27/08 — « des menus deroulant defectueux, passage a la ligne au milieu d'une
# seule option ».
#
# Deux parades appliquees : plus aucune virgule dans les intitules, et la liste
# est rangee dans une feuille a part puis referencee par plage. La reference
# par plage n'a ni limite de longueur ni probleme de separateur.
CHOIX = [
    "oui — c'est un createur",
    "non — nom de serie ou de campagne",
    "non — marque ou label",
    "non — media",
    "je ne sais pas",
]

# Seconde question, ajoutee le 27/08. Elle tranche une ambiguite que rien
# d'autre ne tranche : voir l'en-tete « CE QUE LA SECONDE COLONNE DECIDE ».
CHOIX_TYPE = [
    "createur de contenu (youtube / tiktok / instagram)",
    "chef ou restaurateur",
    "eleveur ou agriculteur",
    "personnalite de television ou de radio",
    "sportif",
    "autre",
    "je ne sais pas",
]


def jugements_existants():
    """Ce que Vincent a deja repondu, pour ne pas l'ecraser en regenerant.

    ERREUR COMMISE LE 29/08 : regenerer ce classeur apres l'ajout de la chaine
    INAPORC a efface 36 jugements. Recuperes depuis git. Un generateur qui
    detruit le travail de l'utilisateur est un generateur casse, meme s'il
    produit un beau fichier.

    Les reponses sont indexees par NOM de createur : c'est la seule cle stable
    quand le nombre de lignes change.
    """
    if not CIBLE.exists():
        return {}
    import openpyxl
    try:
        ws = openpyxl.load_workbook(CIBLE, data_only=True)["createurs"]
    except Exception:
        return {}
    entete = None
    for r in range(1, 60):
        for c in range(1, 14):
            if str(ws.cell(row=r, column=c).value or "").startswith("EST-CE"):
                entete = r
                break
        if entete:
            break
    if not entete:
        return {}
    out = {}
    for r in range(entete + 1, ws.max_row + 1):
        nom = ws.cell(row=r, column=2).value
        if not nom:
            continue
        reponses = [ws.cell(row=r, column=c).value for c in (9, 10, 11)]
        if any(reponses):
            out[str(nom).strip()] = reponses
    return out


def main():
    anciens = jugements_existants()
    if anciens:
        print(f"{len(anciens)} jugements existants seront preserves",
              file=sys.stderr)
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
        "Deux questions, colonnes vertes.",
        "",
        "  1. Est-ce un createur de contenu, ou autre chose ?",
        "  2. Quel type de personne ? (createur, chef, eleveur, personnalite "
        "TV...)",
        "Beaucoup de ces noms sont des titres de series (« Milk Check ») ou des "
        "labels (« Label Rouge »). L'outil ne sait pas les distinguer.",
        "",
        "POURQUOI CA COMPTE",
        "",
        "L'outil a deux facons de reconnaitre un nom, indiquee colonne "
        "« Comment on l'a trouve ».",
        "Tes reponses mesureront ce que chacune vaut. Si « motif dans le titre » "
        "ne donne que des series, on l'abandonne.",
        "",
        "La SECONDE question sert a tout autre chose : savoir quelle part des "
        "collaborations le projet voit.",
        "Nos deux methodes trouvent 36 et 42 createurs, et n'ont qu'UN nom en "
        "commun. Soit on rate enormement, soit les deux methodes cherchent des "
        "gens differents.",
        "Si ces 42 noms sont surtout des chefs et des eleveurs, c'est la "
        "seconde explication. S'ils ressemblent aux youtubeurs qu'on trouve "
        "par ailleurs, c'est la premiere — et notre couverture est mauvaise.",
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
        ("EST-CE UN CREATEUR ?", 34), ("QUEL TYPE DE PERSONNE ?", 32),
        ("Ton commentaire", 30),
    ]
    for j, (titre, largeur) in enumerate(colonnes, 1):
        c = ws.cell(row=depart, column=j, value=titre)
        c.fill = ENTETE
        c.font = Font(bold=True, color="FFFFFF", size=11)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = largeur
    ws.row_dimensions[depart].height = 32

    # Les listes vivent dans une feuille dediee et sont referencees par plage.
    # Voir le commentaire sur CHOIX : une liste ecrite en ligne se casse sur la
    # premiere virgule d'un intitule.
    lst = wb.create_sheet("listes")
    for i, v in enumerate(CHOIX, 1):
        lst.cell(row=i, column=1, value=v)
    for i, v in enumerate(CHOIX_TYPE, 1):
        lst.cell(row=i, column=2, value=v)
    lst.sheet_state = "hidden"

    dv = DataValidation(type="list", allow_blank=True,
                        formula1=f"=listes!$A$1:$A${len(CHOIX)}")
    ws.add_data_validation(dv)
    dv2 = DataValidation(type="list", allow_blank=True,
                         formula1=f"=listes!$B$1:$B${len(CHOIX_TYPE)}")
    ws.add_data_validation(dv2)

    for i, (nom, d) in enumerate(lignes, 1):
        r = depart + i
        connu = d["via"].startswith("compte connu")
        garde = anciens.get(nom, [None, None, None])
        valeurs = [i, nom, ", ".join(sorted(d["entites"])), d["via"], d["n"],
                   d["date"], d["exemple"][:150], "",
                   garde[0] or "", garde[1] or "", garde[2] or ""]
        for j, v in enumerate(valeurs, 1):
            c = ws.cell(row=r, column=j, value=v)
            c.alignment = Alignment(vertical="top", wrap_text=(j in (2, 4, 7)))
            if j in (9, 10, 11):
                c.fill = VERT
            elif not connu:
                c.fill = GRIS
        lien = ws.cell(row=r, column=8, value="voir la video")
        if d["url"]:
            lien.hyperlink = d["url"]
        lien.font = Font(color="1155CC", underline="single")
        dv.add(ws.cell(row=r, column=9))
        dv2.add(ws.cell(row=r, column=10))
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
