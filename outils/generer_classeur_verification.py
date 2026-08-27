"""
Fabrique cartographie/A_VERIFIER.xlsx — les candidats a instruire par Vincent.

REGLE POSEE LE 25 AOUT 2026

Tout ce qu'on demande a Vincent arrive en **classeur Excel mis en forme**,
jamais en CSV ni en Markdown. Trois fois de suite un fichier lui a ete remis
illisible : colonnes nommees pour la conversation, URL sans rapport avec la
question, puis format brut. Le travail de mise en forme est a la charge de
l'outil.

Et surtout : **on montre l'extrait de description qui a declenche la
detection**, pas la description entiere. C'est ce qui permet de juger d'un coup
d'oeil au lieu de lire mille caracteres.

Colonnes vertes = a remplir. Tout le reste ne se touche pas.
Aucun script n'ecrase ce fichier : celui-ci refuse si le classeur existe.

Usage :  python outils/generer_classeur_verification.py
"""

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CIBLE = RACINE / "cartographie" / "A_VERIFIER.xlsx"
DEJA = RACINE / "cartographie" / "A_VERIFIER.xlsx"

VERT = PatternFill("solid", fgColor="D9EAD3")
GRIS = PatternFill("solid", fgColor="F3F3F3")
JAUNE = PatternFill("solid", fgColor="FFF2CC")
ENTETE = PatternFill("solid", fgColor="38761D")
BORD = Border(*[Side(style="thin", color="CCCCCC")] * 4)
HAUT = Alignment(vertical="top", wrap_text=True)

# ATTENTION AUX VIRGULES : Excel s'en sert comme separateur dans une liste
# deroulante ecrite en ligne. Les intitules n'en contiennent donc aucune, et la
# liste est rangee dans une feuille masquee puis referencee par plage — voir
# generer_classeur_lobbies.py pour le detail du defaut signale le 27/08.
VERDICTS = [
    "collaboration remuneree",
    "mention sans collaboration",
    "hors sujet",
    "je ne sais pas",
]


def sans_accent(t):
    t = unicodedata.normalize("NFKD", str(t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def aplatir_avec_index(texte):
    """Renvoie (texte aplati, index de chaque caractere dans l'original).

    L'appariement se fait sur une forme aplatie — minuscules, sans accents,
    sans espaces ni ponctuation — pour que « @lesproduitslaitiers » rencontre
    « Les Produits Laitiers ». Mais l'extrait doit etre decoupe dans le texte
    ORIGINAL, lisible. Il faut donc garder la correspondance entre les deux.

    Sans cette correspondance, l'extrait retombait sur le debut de la
    description dans 3 cas sur 4 — constate le 25/08/2026.
    """
    plat, index = [], []
    for i, c in enumerate(texte):
        d = unicodedata.normalize("NFKD", c)
        d = "".join(x for x in d if not unicodedata.combining(x)).lower()
        for x in d:
            if x.isalnum():
                plat.append(x)
                index.append(i)
    return "".join(plat), index


def extrait(description, alias_reconnus, extrait_pret=""):
    """Le passage qui a declenche la detection.

    Si la moisson a deja taille l'extrait dans le texte COMPLET — colonne
    `extrait_declencheur`, apparue le 27/08 — on l'utilise tel quel : c'est le
    seul cas ou la preuve est garantie visible. Sinon on la cherche dans les
    900 caracteres conservees, et on previent quand elle n'y est pas.
    """
    if extrait_pret and extrait_pret.strip():
        return extrait_pret.replace(" ⏎ ", chr(10)).strip()
    return _extrait_dans_le_tronque(description, alias_reconnus)


def _extrait_dans_le_tronque(description, alias_reconnus):
    """Le passage du texte original autour de la premiere mention trouvee."""
    d = description.replace(" ⏎ ", chr(10)).strip()
    if not d:
        return ""
    plat, index = aplatir_avec_index(d)

    formes = []
    for a in [x.strip() for x in alias_reconnus.split("|") if x.strip()]:
        base = "".join(c for c in unicodedata.normalize("NFKD", a.lower())
                       if c.isalnum())
        if len(base) >= 5:
            formes.append(base)
            # « lesproduitslaitiers » apparait souvent sans son article
            for art in ("les", "le", "la", "des", "du", "de"):
                if base.startswith(art) and len(base) - len(art) >= 5:
                    formes.append(base[len(art):])
    formes.sort(key=len, reverse=True)

    for forme in formes:
        i = plat.find(forme)
        if i == -1:
            continue
        debut_reel = index[i]
        fin_reel = index[min(i + len(forme) - 1, len(index) - 1)]
        # fenetre courte avant, longue apres : ce qui suit la mention dit
        # generalement de quoi il s'agit (« ... de nous avoir accompagnes »)
        avant = d[max(0, debut_reel - 90):debut_reel]
        apres = d[debut_reel:fin_reel + 330]
        return ("..." if debut_reel > 90 else "") + (avant + apres).strip()

    # La moisson n'a conserve que les 900 premiers caracteres de chaque
    # description. Quand la mention est au-dela, mieux vaut le DIRE que
    # d'afficher un debut de texte sans rapport : Vincent jugerait sur le
    # mauvais passage.
    avertissement = ("[La mention est au-dela de ce qui a ete enregistre. "
                    "Ouvrir la video pour lire la description complete.]")
    return avertissement + chr(10) + chr(10) + d[:260].strip()


def deja_juges():
    """Ce que Vincent a deja tranche : on ne le lui redemande pas.

    Parcourt TOUS les classeurs de verification, pas seulement le premier.
    Corrige le 27/08 : la version precedente ne lisait que `A_VERIFIER.xlsx`
    et aurait redemande les 33 cas tranches dans `A_VERIFIER_2.xlsx`.

    La colonne du verdict est reperee par son EN-TETE, jamais par son rang :
    les deux classeurs ne l'ont pas au meme endroit (colonne 8 dans le premier,
    9 dans le second, qui a gagne une colonne « Retenu par la regle D »).
    """
    import openpyxl
    out = set()
    for f in sorted((RACINE / "cartographie").glob("A_VERIFIER*.xlsx")):
        try:
            wb = openpyxl.load_workbook(f, data_only=True)
            ws = wb["a verifier"]
        except Exception as e:
            print(f"  {f.name} illisible ({type(e).__name__}) — ignore",
                  file=sys.stderr)
            continue
        entetes = [str(c.value or "") for c in ws[1]]
        try:
            col = next(i for i, h in enumerate(entetes)
                       if "VERDICT" in h.upper())
        except StopIteration:
            print(f"  {f.name} : pas de colonne de verdict — ignore",
                  file=sys.stderr)
            wb.close()
            continue
        n = 0
        for r in ws.iter_rows(min_row=2, values_only=True):
            if col < len(r) and r[col]:
                out.add((str(r[1]), str(r[5])[:40]))
                n += 1
        print(f"  {f.name} : {n} cas deja tranches", file=sys.stderr)
        wb.close()
    return out


def passe_regle_d(ligne, descriptions):
    """La regle D, mesuree a 83 % de precision (JOURNAL 38.3).

    Reprend la logique de evaluer_detection.py : vocabulaire de collaboration
    pres de la mention, et alias generique ecarte s'il est seul.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ev", Path(__file__).resolve().parent / "evaluer_detection.py")
    global _EV
    try:
        _EV
    except NameError:
        _EV = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_EV)
    desc = descriptions.get(ligne["video_id"]) or ligne.get("description", "")
    alias = ligne.get("alias_reconnus", "")
    if not _EV.voisinage_proche(desc, alias):
        return "non"
    if _EV.est_generique(alias) and "@" not in alias:
        return "non"
    return "OUI"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", default=None,
                    help="chemin du classeur ; par defaut A_VERIFIER.xlsx")
    ap.add_argument("--nouveaux-seulement", action="store_true",
                    help="exclut ce que Vincent a deja juge")
    args = ap.parse_args()

    global CIBLE
    if args.sortie:
        CIBLE = RACINE / "cartographie" / args.sortie

    if CIBLE.exists():
        print(f"REFUS : {CIBLE.name} existe deja et contient peut-etre tes reponses.",
              file=sys.stderr)
        print("Renomme-le d'abord si tu veux le regenerer.", file=sys.stderr)
        return 1

    sources = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))
    if not sources:
        print("Lance d'abord outils/nettoyer_detections.py", file=sys.stderr)
        return 1
    with sources[-1].open(encoding="utf-8") as f:
        lignes = [l for l in csv.DictReader(f)
                  if l.get("force", "").startswith("ALIAS")]
    if args.nouveaux_seulement:
        vus = deja_juges()
        avant = len(lignes)
        lignes = [l for l in lignes if (l["chaine"], l["titre"][:40]) not in vus]
        print(f"{avant - len(lignes)} deja jugees, ecartees", file=sys.stderr)

    cache = RACINE / "donnees" / "descriptions_completes.json"
    descriptions = (json.loads(cache.read_text(encoding="utf-8"))
                    if cache.exists() else {})
    lignes.sort(key=lambda l: -(int(l["abonnes"] or 0)))

    wb = Workbook()
    ws = wb.active
    ws.title = "a verifier"
    ws.append(["N", "Chaine", "Abonnes", "Date", "Entite citee",
               "Titre de la video", "Regarder", "Ce qui est ecrit dans la description",
               "Retenu par la regle D", "TON VERDICT", "Ton commentaire"])

    lst = wb.create_sheet("listes")
    for _i, _v in enumerate(VERDICTS, 1):
        lst.cell(row=_i, column=1, value=_v)
    lst.sheet_state = "hidden"
    dv = DataValidation(type="list", allow_blank=True,
                        formula1=f"=listes!$A$1:$A${len(VERDICTS)}")
    ws.add_data_validation(dv)

    for n, l in enumerate(lignes, 1):
        ab = int(l["abonnes"] or 0)
        desc = descriptions.get(l["video_id"]) or l.get("description", "")
        ws.append([n, l["chaine"], ab, l["publiee"], l["entites_retenues"],
                   l["titre"], "ouvrir",
                   extrait(desc, l.get("alias_reconnus", "") or l["entites_retenues"],
                           l.get("extrait_declencheur", "")),
                   passe_regle_d(l, descriptions), "", ""])
        r = ws.max_row
        c = ws.cell(row=r, column=7, value="ouvrir")
        c.hyperlink = l["url"]
        c.font = Font(color="0563C1", underline="single")
        ws.cell(row=r, column=3).number_format = "# ##0"
        dv.add(ws.cell(row=r, column=10))
        for col in range(1, 12):
            cel = ws.cell(row=r, column=col)
            cel.alignment = HAUT
            cel.border = BORD
            if col in (10, 11):
                cel.fill = VERT
            elif col == 8:
                cel.fill = JAUNE          # l'extrait : c'est ce qu'on lit
            else:
                cel.fill = GRIS
        ws.row_dimensions[r].height = 108

    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = ENTETE
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 34
    for i, w in enumerate([4, 17, 11, 11, 17, 38, 9, 70, 12, 24, 30], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    # --- mode d'emploi, en tete de classeur ---
    aide = wb.create_sheet("COMMENT FAIRE", 0)
    aide.column_dimensions["A"].width = 104
    textes = [
        ("Comment remplir ce classeur", True),
        ("", False),
        ("Une video par ligne. Tu ne remplis que les deux colonnes VERTES.", False),
        ("", False),
        ("La colonne JAUNE contient le passage exact de la description qui a", False),
        ("declenche la detection. Dans la plupart des cas, il suffit a juger :", False),
        ("tu n'as pas besoin d'ouvrir la video.", False),
        ("", False),
        ("Si le passage ne suffit pas, la colonne « Regarder » ouvre la video.", False),
        ("", False),
        ("Les verdicts proposes", True),
        ("", False),
        ("collaboration remuneree     le createur est paye par la filiere", False),
        ("mention sans collaboration  il en parle sans etre paye", False),
        ("auto-promotion              il fait la promo de ses propres projets", False),
        ("je ne sais pas              le passage ne permet pas de trancher", False),
        ("hors sujet                  faux positif, rien a voir", False),
        ("", False),
        ("« Je ne sais pas » est une reponse utile : elle dit que la detection", False),
        ("seule ne suffit pas, ce qui est une information sur l'outil.", False),
        ("", False),
        ("A quoi servent tes reponses", True),
        ("", False),
        ("Elles ne servent pas qu'a valider ces videos-la. Elles constituent le", False),
        ("JEU DE REFERENCE : une fois une centaine de cas juges, on fait tourner", False),
        ("la detection automatique sur les memes cas et on compare. C'est la", False),
        ("seule facon de mesurer le taux d'erreur — et donc de savoir quand on", False),
        ("peut arreter de verifier a la main.", False),
        ("", False),
        ("Autrement dit : annoter maintenant, c'est ce qui permettra de ne plus", False),
        ("annoter plus tard.", False),
        ("", False),
        ("Le classeur est trie par audience decroissante : les premieres lignes", False),
        ("sont les plus utiles au plaidoyer.", False),
    ]
    for i, (t, gras) in enumerate(textes, start=1):
        c = aide.cell(row=i, column=1, value=t)
        c.font = Font(bold=gras, size=13 if gras else 11)
        c.alignment = HAUT

    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"{len(lignes)} videos a verifier, triees par audience decroissante")
    return 0


if __name__ == "__main__":
    sys.exit(main())
