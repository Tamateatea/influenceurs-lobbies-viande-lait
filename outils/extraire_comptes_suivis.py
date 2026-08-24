"""
Sort les listes d'abonnements Instagram du classeur A_COMPLETER.xlsx.

Vincent colle les listes dans une cellule du classeur, parce que c'est ce qui
est le plus simple pour lui. Ce script fait la conversion vers des fichiers
propres : ce travail est a la charge de l'outil, pas a la sienne.

Produit :
  donnees/comptes_vitrines/<pseudo>.txt   le collage brut, date, avec entete
  recherche/comptes_suivis_<date>.csv     une ligne par compte suivi

Format attendu du collage : la liste « following » d'Instagram, qui alterne
une ligne de pseudo et une ligne de nom affiche.

PLATEFORME : ces listes viennent d'INSTAGRAM. La colonne plateforme est
obligatoire — la meme entite a des comptes differents selon la plateforme, et
une donnee sans sa plateforme n'est pas exploitable.

Usage :  python outils/extraire_comptes_suivis.py
"""

import csv
import re
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CLASSEUR = RACINE / "cartographie" / "A_COMPLETER.xlsx"
DEPOT = RACINE / "donnees" / "comptes_vitrines"
SORTIE = RACINE / "recherche"

PLATEFORME = "instagram"
# Un pseudo Instagram : minuscules, chiffres, point, tiret bas. Rien d'autre.
PSEUDO = re.compile(r"^[a-z0-9._]{1,30}$")


def lire_classeur():
    import openpyxl
    wb = openpyxl.load_workbook(CLASSEUR, data_only=True)
    ws = wb["2. COMPTES VITRINES"]
    entetes = [c.value for c in ws[1]]

    def col(motif):
        for i, e in enumerate(entetes):
            if e and motif.lower() in str(e).lower():
                return i
        return None

    # « pseudo exact » et non « pseudo » : la colonne « Etat du pseudo »
    # arrive avant et serait capturee a sa place.
    i_ent, i_pseudo, i_suivis = col("entite"), col("pseudo exact"), col("suivis")
    if i_suivis is None:
        print("Colonne des comptes suivis introuvable. Entetes : " + str(entetes),
              file=sys.stderr)
        sys.exit(1)

    lignes = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        lignes.append({
            "entite": (r[i_ent] or "").strip(),
            "pseudo_brut": str(r[i_pseudo] or "").strip(),
            "suivis_brut": str(r[i_suivis] or "").strip(),
        })
    wb.close()
    return lignes


def pseudo_vitrine(brut):
    """La cellule contient le pseudo puis le nom affiche. On prend la 1re ligne."""
    if not brut:
        return None, ""
    parts = [l.strip() for l in brut.splitlines() if l.strip()]
    if not parts:
        return None, ""
    premier = parts[0]
    if not PSEUDO.match(premier):
        # Vincent a repondu en toutes lettres (ex : « Aucun compte trouve »).
        return None, brut
    return premier, " / ".join(parts[1:])


def parser_liste(brut):
    """Extrait les comptes suivis d'un collage Instagram.

    La liste alterne normalement pseudo / nom affiche, mais un compte sans nom
    affiche decale toute la suite. Un parcours par paires fixes perdrait alors
    la moitie des comptes — constate le 24/08/2026 : 92 lignes perdues sur 295.

    Regle retenue, qui ne peut rien perdre : TOUTE ligne ayant la forme d'un
    pseudo est un compte. La ligne suivante est son nom affiche seulement si
    elle n'a PAS la forme d'un pseudo. Les doublons sont fusionnes.
    """
    lignes = [l.strip() for l in brut.splitlines() if l.strip()]
    if len(lignes) <= 1:
        return [], lignes  # trop court pour etre une liste

    trouves, orphelines = {}, []
    for i, ligne in enumerate(lignes):
        if not PSEUDO.match(ligne):
            orphelines.append(ligne)
            continue
        suivante = lignes[i + 1] if i + 1 < len(lignes) else ""
        nom = suivante if suivante and not PSEUDO.match(suivante) else ""
        if ligne not in trouves or (nom and not trouves[ligne]):
            trouves[ligne] = nom
    return list(trouves.items()), orphelines


def main():
    if not CLASSEUR.exists():
        print(f"{CLASSEUR} introuvable.", file=sys.stderr)
        return 1
    DEPOT.mkdir(parents=True, exist_ok=True)
    SORTIE.mkdir(exist_ok=True)
    aujourdhui = date.today().isoformat()

    lignes_csv = []
    resume = []

    for ligne in lire_classeur():
        entite = ligne["entite"]
        pseudo, note = pseudo_vitrine(ligne["pseudo_brut"])
        paires, anomalies = parser_liste(ligne["suivis_brut"])

        if not entite:
            continue
        if not pseudo:
            resume.append((entite, "—", 0, note or "pas de compte vitrine"))
            continue
        if not paires:
            resume.append((entite, pseudo, 0,
                           ligne["suivis_brut"][:70] or "liste non fournie"))
            continue

        chemin = DEPOT / f"{pseudo}.txt"
        entete = [
            f"# releve : {aujourdhui}",
            f"# plateforme : {PLATEFORME}",
            f"# compte vitrine : @{pseudo}",
            f"# entite : {entite}",
            f"# nature : liste des comptes SUIVIS par ce compte (following)",
            f"# origine : copier-coller manuel de Vincent, via A_COMPLETER.xlsx",
            f"# comptes : {len(paires)}",
            "",
        ]
        corps = [f"{p}\t{nom}" for p, nom in paires]
        chemin.write_text("\n".join(entete + corps) + "\n", encoding="utf-8")

        for p, nom in paires:
            lignes_csv.append({
                "plateforme": PLATEFORME,
                "compte_vitrine": pseudo,
                "entite_vitrine": entite,
                "compte_suivi": p,
                "nom_affiche": nom,
                "releve_le": aujourdhui,
            })
        resume.append((entite, pseudo, len(paires),
                       f"{len(anomalies)} nom(s) affiche(s)" if anomalies else "ok"))

    if not lignes_csv:
        print("Aucune liste exploitable trouvee dans le classeur.", file=sys.stderr)
        return 1

    csv_path = SORTIE / f"comptes_suivis_{aujourdhui}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes_csv[0].keys()))
        w.writeheader()
        w.writerows(lignes_csv)

    uniques = {l["compte_suivi"] for l in lignes_csv}
    print(f"{'ENTITE':16s} {'COMPTE VITRINE':22s} {'SUIVIS':>7s}  REMARQUE")
    for e, p, n, rem in resume:
        print(f"{e:16s} {p:22s} {n:>7d}  {rem}")
    print()
    print(f"{len(lignes_csv)} liens au total, {len(uniques)} comptes distincts")
    print(f"Ecrit : {csv_path}")
    print(f"Ecrit : {DEPOT}\\<pseudo>.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
