"""
Fabrique cartographie/DATASET.xlsx — le jeu de donnees, lisible.

POURQUOI CE FICHIER EXISTE

Le 29/08, apres avoir construit le jeu de donnees, je l'ai livre en CSV. Vincent
a demande son chemin, ne le trouvait pas — et c'etait la quatrieme fois qu'un
CSV lui etait remis alors qu'il a dit trois fois qu'il ne peut pas les lire.

METHODOLOGIE 13.4 le dit depuis le 25/08 : **tout ce qu'on remet a Vincent
arrive en classeur Excel mis en forme.** Le CSV reste, pour les outils.

CE QUE LE CLASSEUR AJOUTE AU CSV

- les colonnes rangees dans l'ordre de lecture, du commanditaire au createur ;
- un filtre automatique sur chaque colonne ;
- les liens cliquables ;
- une feuille de synthese qui dit ce que le jeu contient et ce qui lui manque ;
- les lignes non verifiees par un humain sur fond gris — pour qu'on ne les
  confonde jamais avec les autres.

Usage :  python outils/generer_classeur_dataset.py
"""

import csv
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CIBLE = RACINE / "cartographie" / "DATASET.xlsx"

ENTETE = PatternFill("solid", fgColor="434343")
GRIS = PatternFill("solid", fgColor="F3F3F3")
VERT = PatternFill("solid", fgColor="D9EAD3")
JAUNE = PatternFill("solid", fgColor="FFF2CC")

# (colonne du CSV, intitule lisible, largeur)
COLONNES = [
    ("commanditaire", "Commanditaire", 22),
    ("type_de_commanditaire", "Type", 15),
    ("secteur", "Secteur", 10),
    ("groupe_parent", "Groupe parent", 18),
    ("vitrine", "Vitrine", 22),
    ("alias_observe", "Alias observe", 24),
    ("contenu_url", "Contenu", 11),
    ("titre_du_contenu", "Titre du contenu", 44),
    ("date_publication", "Date", 11),
    ("nombre_de_vues", "Vues", 12),
    ("date_releve_des_vues", "Vues relevees le", 14),
    ("statut_collaboration", "Statut", 11),
    ("nom_influenceur", "Influenceur", 24),
    ("plateforme", "Plateforme", 12),
    ("alias_influenceur", "Son pseudo", 22),
    ("nombre_abonnes", "Abonnes", 10),
    ("type_de_createur", "Type de createur", 26),
    ("canal_de_detection", "Comment on l'a trouve", 24),
    ("degre_de_certitude", "Degre de certitude", 26),
    ("verifie_par_humain", "Verifie ?", 10),
]


def main():
    fichiers = sorted(RECHERCHE.glob("dataset_*.csv"))
    if not fichiers:
        print("Aucun dataset_*.csv — lancer d'abord construire_dataset.py",
              file=sys.stderr)
        return 1
    source = fichiers[-1]
    with source.open(encoding="utf-8") as fh:
        lignes = list(csv.DictReader(fh))
    if not lignes:
        print("Jeu de donnees vide.", file=sys.stderr)
        return 1

    # les lignes verifiees d'abord, puis les plus recentes
    lignes.sort(key=lambda l: (l.get("verifie_par_humain") != "oui",
                               l.get("date_publication", "")), reverse=False)
    lignes.sort(key=lambda l: (l.get("verifie_par_humain") != "oui",
                               -_annee(l.get("date_publication", ""))))

    wb = Workbook()
    ws = wb.active
    ws.title = "donnees"

    for j, (_cle, titre, largeur) in enumerate(COLONNES, 1):
        c = ws.cell(row=1, column=j, value=titre)
        c.fill = ENTETE
        c.font = Font(bold=True, color="FFFFFF", size=11)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = largeur
    ws.row_dimensions[1].height = 34

    for i, l in enumerate(lignes, 2):
        verifie = l.get("verifie_par_humain") == "oui"
        for j, (cle, _t, _w) in enumerate(COLONNES, 1):
            valeur = l.get(cle, "")
            if cle == "contenu_url":
                c = ws.cell(row=i, column=j, value="ouvrir" if valeur else "")
                if valeur:
                    c.hyperlink = valeur
                    c.font = Font(color="1155CC", underline="single")
            elif cle == "nombre_de_vues" and str(valeur).isdigit():
                # en nombre, pas en texte : sinon le tri d'Excel est alphabetique
                # et 9 000 passe devant 34 000 000
                c = ws.cell(row=i, column=j, value=int(valeur))
                c.number_format = "# ##0"
            else:
                c = ws.cell(row=i, column=j, value=valeur)
                c.alignment = Alignment(vertical="top",
                                        wrap_text=(cle == "titre_du_contenu"))
            if not verifie:
                c.fill = GRIS
            elif cle == "verifie_par_humain":
                c.fill = VERT
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLONNES))}{len(lignes)+1}"

    # --- feuille de synthese ---
    sy = wb.create_sheet("CE QUE C'EST", 0)
    canaux = Counter(l["canal_de_detection"] for l in lignes)
    types = Counter(l["type_de_commanditaire"] for l in lignes)
    commanditaires = Counter(l["commanditaire"] for l in lignes)
    createurs = len({l["nom_influenceur"].lower() for l in lignes})
    verifies = sum(1 for l in lignes if l.get("verifie_par_humain") == "oui")

    texte = [
        f"LE JEU DE DONNEES — {date.today().strftime('%d/%m/%Y')}",
        "",
        "UNE LIGNE PAR CONTENU, pas par createur.",
        "Une collaboration n'est pas un fait abstrait : c'est une video ou une "
        "annonce, datee et consultable.",
        "Un createur qui a fait cinq videos occupe cinq lignes, et chacune peut "
        "etre contestee separement.",
        "",
        f"Lignes : {len(lignes)}",
        f"Createurs distincts : {createurs}",
        f"Lignes dont le createur a une fiche que TU as etablie : {verifies}",
        "",
        "D'OU VIENNENT LES LIGNES",
        "",
    ]
    for c, n in canaux.most_common():
        texte.append(f"   {n:>5d}   {c}")
    texte += ["", "QUI PAIE", ""]
    for c, n in types.most_common():
        texte.append(f"   {n:>5d}   {c}")
    texte += ["", "LES DIX PREMIERS COMMANDITAIRES", ""]
    for c, n in commanditaires.most_common(10):
        texte.append(f"   {n:>5d}   {c}")
    texte += [
        "",
        "CE QUI MANQUE ENCORE",
        "",
        "  - Le NOMBRE DE VUES est vide. Recuperable sur YouTube pour 1 unite "
        "de quota par tranche de 50 videos.",
        "  - Le MONTANT est volontairement ABSENT, pas vide. Aucune source ne "
        "le donne au niveau du createur.",
        "    Une colonne vide donnerait l'illusion qu'elle pourrait etre "
        "remplie. Les budgets connus sont ceux des lobbies, pas des contrats.",
        "  - Les PSEUDOS et AUDIENCES viennent de ton travail manuel. Les "
        "lignes sur fond gris n'en ont pas.",
        "",
        "CE QUE CE FICHIER N'EST PAS",
        "",
        "  Ce n'est PAS un registre publiable.",
        "  Chaque ligne porte son degre de certitude. Rien ne se publie sans "
        "verification humaine — METHODOLOGIE section 9.",
        "",
        "  Reserve principale : le canal « publicite payee » fournit la plus "
        "grosse part des lignes,",
        "  et c'est le SEUL des trois dont la precision n'a jamais ete mesuree.",
        "",
        "LEGENDE",
        "",
        "  Fond gris  = le createur n'a pas de fiche verifiee par toi.",
        "  Fond vert  = tu as etabli son pseudo, son audience ou son type.",
    ]
    for i, l in enumerate(texte, 1):
        c = sy.cell(row=i, column=1, value=l)
        c.font = Font(bold=bool(l) and l.isupper(), size=11)
    sy.column_dimensions["A"].width = 104

    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"{len(lignes)} lignes, {createurs} createurs, source {source.name}")
    return 0


def _annee(d):
    try:
        return int(str(d)[:4])
    except (ValueError, TypeError):
        return 0


if __name__ == "__main__":
    sys.exit(main())
