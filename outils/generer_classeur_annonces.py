"""
Fabrique cartographie/ANNONCES_A_JUGER.xlsx — le canal jamais mesure.

CE QU'IL FAUT MESURER, ET POURQUOI C'EST URGENT

Le canal « publicite payee » fournit la plus grosse part du jeu de donnees, et
c'est **le seul des trois dont la precision n'a jamais ete etablie**. Un jeu de
donnees domine par le canal dont on ignore la fiabilite n'est pas solide.

Il trouve les createurs par trois voies, qu'il faut departager :

    pseudo ecrit tel quel        un @pseudo apparait dans le texte de l'annonce
    compte connu du registre     le nom correspond a un compte deja repere
    vocabulaire de collaboration « avec X », « merci a X » — la plus douteuse

CE QUI A ETE CORRIGE AVANT DE REDEMANDER SON TEMPS A VINCENT

Le 29/08 il a ouvert la premiere version et l'a jugee sans detour : « c'est de
la merde ». Il avait raison sur deux points, tous deux reels :

**Les liens etaient tous morts.** Ils pointaient vers `ad_snapshot_url`, qui
n'est consultable que par le detenteur du jeton l'ayant generee — et le jeton
expire en deux heures. Ils portaient d'ailleurs ce jeton en clair, ce qui l'a
fait fuiter dans sept fichiers pousses sur GitHub.

Ce classeur utilise la **bibliotheque publicitaire publique** :
`facebook.com/ads/library/?id=<ad_id>`. Aucun jeton, consultable par tout le
monde, et c'est la meme page que celle qu'un journaliste citerait.

**Des marques etaient presentees comme des createurs** — `@justinbridou_fr`,
`@legaulois_officiel`, `@regilaitfr`. Le test d'auto-mention ne regardait que
dans un sens : « regilaitfr » n'est pas contenu dans « Regilait ». Corrige, et
la regle est desormais partagee dans `createurs.py`.

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
CIBLE = RACINE / "cartographie" / "ANNONCES_A_JUGER.xlsx"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir
from createurs import est_un_commanditaire

VERT = PatternFill("solid", fgColor="D9EAD3")
GRIS = PatternFill("solid", fgColor="EFEFEF")
ENTETE = PatternFill("solid", fgColor="434343")

# Sans virgule : Excel s'en sert comme separateur dans une liste en ligne.
CHOIX = [
    "oui — createur remunere par ce commanditaire",
    "oui — createur mais le lien n'est pas commercial",
    "non — c'est la marque ou le commanditaire",
    "non — mot courant ou faux positif",
    "non — c'est un media",
    "je ne sais pas",
]

# L'ordre de fiabilite presumee. Vincent juge du plus sur au plus douteux, et
# peut s'arreter quand il veut : les premieres lignes sont les plus utiles.
RANG = {"pseudo ecrit tel quel": 0, "compte connu du registre": 1,
        "vocabulaire de collaboration": 2}

PAR_VOIE = 30      # combien de lignes par voie — assez pour mesurer, pas plus


def main():
    fichiers = sorted(RECHERCHE.glob("createurs_annonces_*.csv"))
    if not fichiers:
        print("Aucun createurs_annonces_*.csv.", file=sys.stderr)
        return 1

    # une ligne par createur, en gardant l'annonce la plus parlante
    par_createur = {}
    with fichiers[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            nom = l["createur"].strip()
            if not nom or est_un_commanditaire(nom):
                continue
            cle = aplatir(nom)
            d = par_createur.setdefault(cle, {"nom": nom, "n": 0, "pages": set(),
                                              "voie": "", "extrait": "",
                                              "ad_id": "", "date": ""})
            d["n"] += 1
            d["pages"].add(l["page_annonceuse"])
            # ON GARDE L'ANNONCE OU LE NOM EST VISIBLE DANS L'EXTRAIT.
            #
            # La version precedente gardait l'extrait le plus LONG, ce qui
            # revenait a montrer n'importe laquelle des annonces du createur —
            # souvent une ou son nom n'apparait pas. Vincent a juge 60 lignes
            # ainsi, sans jamais voir de nom, et a repondu « c'est la marque ».
            # Sa reponse etait la seule possible.
            #
            # Un extrait qui ne montre pas ce qui a declenche la detection ne
            # permet pas de juger. C'est la quatrieme fois que ce defaut
            # apparait dans le projet.
            extrait = l.get("extrait", "")
            nom_visible = nom.lower().lstrip("@") in extrait.lower()
            deja_visible = nom.lower().lstrip("@") in d["extrait"].lower()
            meilleur = (
                RANG.get(l["voie"], 9) < RANG.get(d["voie"], 9)
                or (RANG.get(l["voie"], 9) == RANG.get(d["voie"], 9)
                    and (nom_visible > deja_visible
                         or (nom_visible == deja_visible
                             and len(extrait) > len(d["extrait"]))))
                or not d["extrait"])
            if meilleur:
                d["voie"] = l["voie"]
                d["extrait"] = extrait
                d["ad_id"] = l.get("ad_id", "")
                d["date"] = l.get("debut_diffusion", "")

    # echantillon equilibre : les trois voies doivent etre mesurables
    par_voie = defaultdict(list)
    for d in par_createur.values():
        par_voie[d["voie"]].append(d)
    lignes = []
    for voie in sorted(par_voie, key=lambda v: RANG.get(v, 9)):
        lot = sorted(par_voie[voie], key=lambda d: -d["n"])[:PAR_VOIE]
        lignes.extend(lot)

    wb = Workbook()
    ws = wb.active
    ws.title = "annonces"

    intro = [
        "CE QUE TU AS SOUS LES YEUX",
        "",
        "Des createurs nommes dans des PUBLICITES PAYEES par la filiere.",
        "L'annonceur a paye Meta pour diffuser un contenu qui porte ce nom : "
        "c'est la preuve la plus forte du projet.",
        "",
        "POURQUOI CE CLASSEUR EXISTE",
        "",
        "Ce canal fournit la plus grosse part du jeu de donnees, et c'est le "
        "SEUL des trois dont la precision n'a jamais ete mesuree.",
        "Tant qu'elle ne l'est pas, le jeu de donnees n'est pas solide.",
        "",
        "CE QUI A ETE CORRIGE DEPUIS TA DERNIERE LECTURE",
        "",
        "  Les liens : ils pointaient vers une page qui exige le jeton d'acces, "
        "expire au bout de deux heures. Tous morts.",
        "     Ils utilisent maintenant la BIBLIOTHEQUE PUBLICITAIRE PUBLIQUE de "
        "Meta — aucun jeton, consultable par tous.",
        "  Les marques : @justinbridou_fr, @legaulois_officiel et @regilaitfr "
        "sont ecartes. Le test ne regardait que dans un sens.",
        "",
        "CE QU'ON TE DEMANDE",
        "",
        "Une question par ligne. Les lignes sont groupees par METHODE de "
        "detection, de la plus sure a la plus douteuse.",
        "",
        "IMPORTANT — CE QUI A CHANGE DEPUIS TES 60 PREMIERS JUGEMENTS",
        "",
        "L'extrait montrait les 300 premiers caracteres de l'annonce. Le pseudo "
        "du createur, lui, apparait plus loin — souvent en fin de texte, dans "
        "une ligne de credit du type « recette et photo @xxx ».",
        "Tu as donc juge 60 lignes en voyant du texte publicitaire SANS AUCUN "
        "nom visible, et tu as repondu « c'est la marque ». C'etait la seule "
        "reponse possible.",
        "L'extrait est desormais CENTRE sur le nom detecte. Ces 60 jugements "
        "sont a refaire, et j'en suis desole.",
        "Juger les 30 premieres de chaque groupe suffit a mesurer les trois.",
        "Le fond gris signale la methode la plus douteuse.",
        "",
    ]
    for i, l in enumerate(intro, 1):
        c = ws.cell(row=i, column=1, value=l)
        c.font = Font(bold=bool(l) and l.isupper(), size=11)
    depart = len(intro) + 2

    colonnes = [("N", 5), ("Createur trouve", 28), ("Annonceur(s)", 30),
                ("Methode de detection", 26), ("Annonces", 9), ("Date", 11),
                ("CE QUE DIT L'ANNONCE", 74), ("Voir l'annonce", 16),
                ("TON VERDICT", 40), ("Ton commentaire", 34)]
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

    for i, d in enumerate(lignes, 1):
        r = depart + i
        douteux = d["voie"] == "vocabulaire de collaboration"
        valeurs = [i, d["nom"], ", ".join(sorted(d["pages"]))[:90], d["voie"],
                   d["n"], d["date"], d["extrait"][:400], "", "", ""]
        for j, v in enumerate(valeurs, 1):
            c = ws.cell(row=r, column=j, value=v)
            c.alignment = Alignment(vertical="top", wrap_text=(j in (2, 3, 7)))
            if j in (9, 10):
                c.fill = VERT
            elif douteux:
                c.fill = GRIS
        lien = ws.cell(row=r, column=8, value="ouvrir")
        if d["ad_id"]:
            # Bibliotheque publicitaire PUBLIQUE : pas de jeton, pas
            # d'expiration, et c'est la page qu'un journaliste citerait.
            lien.hyperlink = f"https://www.facebook.com/ads/library/?id={d['ad_id']}"
            lien.font = Font(color="1155CC", underline="single")
        dv.add(ws.cell(row=r, column=9))
        ws.row_dimensions[r].height = 74

    ws.freeze_panes = ws.cell(row=depart + 1, column=1)

    lg = wb.create_sheet("d'ou ca vient")
    compte = defaultdict(int)
    for d in lignes:
        compte[d["voie"]] += 1
    provenance = [
        f"Source : {fichiers[-1].name}",
        f"Genere le {date.today().isoformat()}",
        "",
        f"Createurs proposes : {len(lignes)}, repartis par methode :",
    ] + [f"   {n:>3d}  {v}" for v, n in sorted(compte.items(),
                                               key=lambda x: RANG.get(x[0], 9))] + [
        "",
        f"Sur {len(par_createur)} createurs distincts au total dans les annonces.",
        "L'echantillon est EQUILIBRE entre les methodes, pas proportionnel :",
        "on veut mesurer chacune, pas refleter leur volume.",
        "",
        "Deja ecartes sans te les montrer :",
        "  - les commanditaires eux-memes, via outils/createurs.py ;",
        "  - les medias et emissions ;",
        "  - les noms cites par plus de six annonceurs concurrents.",
    ]
    for i, l in enumerate(provenance, 1):
        lg.cell(row=i, column=1, value=l)
    lg.column_dimensions["A"].width = 78

    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"{len(lignes)} createurs a juger, sur {len(par_createur)} au total")
    for v, n in sorted(compte.items(), key=lambda x: RANG.get(x[0], 9)):
        print(f"   {n:>3d}  {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
