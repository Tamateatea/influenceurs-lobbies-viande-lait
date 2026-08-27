"""
Extrait des listes d'abonnements Instagram depuis un copier-coller brut.

POURQUOI CE FORMAT

Vincent releve les listes a la main et les colle sans mise en forme — c'est
ce qui a ete convenu : le travail de rangement revient a l'outil, pas a lui.
Un fichier peut donc contenir plusieurs comptes sources a la suite, des
commentaires libres, et des noms affiches contenant n'importe quoi.

STRUCTURE ATTENDUE

    @lecomptesource

    pseudo1
    Nom affiche 1

    pseudo2
    Nom affiche 2
    ...
    From <https://www.instagram.com/lecomptesource/>

Les lignes `From <...>` sont les delimiteurs fiables : elles nomment le compte
source sans ambiguite. Les lignes commencant par `@` ne le sont pas — un nom
affiche peut commencer par `@` (constate le 26/08 avec
« @lespetitestrouvaillesdeludi »).

REGLE DE NON-PERTE

Toute ligne ayant la forme d'un pseudo devient un compte. La ligne suivante
est son nom affiche seulement si elle n'a PAS cette forme. Le script verifie
que comptes + noms + commentaires = nombre de lignes lues, et le dit.
Voir METHODOLOGIE 13.3.

Usage :
    python outils/extraire_abonnements_brut.py <fichier.txt>
"""

import csv
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DEPOT = RACINE / "donnees" / "comptes_vitrines"
SORTIE = RACINE / "recherche"

PSEUDO = re.compile(r"^[a-z0-9._]{1,30}$")
DELIMITEUR = re.compile(r"From\s*<https://www\.instagram\.com/([^/>]+)/?>")

# Un compte source qui se suit lui-meme n'apprend rien.
def aplatir(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def decouper(lignes):
    """Rend [(compte_source, [lignes du bloc])], grace aux delimiteurs From."""
    blocs, courant = [], []
    for l in lignes:
        m = DELIMITEUR.search(l)
        if m:
            blocs.append((m.group(1).strip(), courant))
            courant = []
        else:
            courant.append(l)
    if courant:
        blocs.append((None, courant))       # queue sans delimiteur
    return blocs


def parser(bloc, source):
    """Comptes suivis, noms affiches, et ce qui n'est ni l'un ni l'autre."""
    lignes = [l.strip() for l in bloc if l.strip()]
    comptes, noms, autres = {}, 0, []
    for i, l in enumerate(lignes):
        if l.startswith("@") and PSEUDO.match(l[1:]):
            continue                        # rappel du compte source en tete
        if not PSEUDO.match(l):
            autres.append(l)
            continue
        suivante = lignes[i + 1] if i + 1 < len(lignes) else ""
        nom = suivante if suivante and not PSEUDO.match(suivante) else ""
        if nom:
            noms += 1
        if l != aplatir(source) and (l not in comptes or not comptes[l]):
            comptes[l] = nom
    return comptes, noms, autres


def main():
    if len(sys.argv) < 2:
        print("Usage : python outils/extraire_abonnements_brut.py <fichier.txt>",
              file=sys.stderr)
        return 1
    source_fichier = Path(sys.argv[1])
    if not source_fichier.exists():
        print(f"{source_fichier} introuvable.", file=sys.stderr)
        return 1

    lignes = source_fichier.read_text(encoding="utf-8", errors="replace").splitlines()
    blocs = decouper(lignes)
    DEPOT.mkdir(parents=True, exist_ok=True)
    aujourdhui = date.today().isoformat()

    total_lignes, resume, tout = 0, [], []
    commentaires = []
    for compte, bloc in blocs:
        if not compte:
            commentaires += [l.strip() for l in bloc if l.strip()]
            continue
        comptes, noms, autres = parser(bloc, compte)
        n_lignes = len([l for l in bloc if l.strip()])
        total_lignes += n_lignes
        # les « autres » longs sont des noms affiches, les autres des remarques
        remarques = [a for a in autres if len(a) > 60 or a.startswith(">>")]
        commentaires += remarques

        if comptes:
            chemin = DEPOT / f"{compte}.txt"
            entete = [f"# releve : {aujourdhui}",
                      "# plateforme : instagram",
                      f"# compte vitrine : @{compte}",
                      "# nature : liste des comptes SUIVIS par ce compte",
                      "# origine : copier-coller manuel de Vincent",
                      f"# comptes : {len(comptes)}", ""]
            chemin.write_text(
                "\n".join(entete + [f"{p}\t{n}" for p, n in comptes.items()]) + "\n",
                encoding="utf-8")
        for p, n in comptes.items():
            tout.append({"plateforme": "instagram", "compte_vitrine": compte,
                         "entite_vitrine": "", "compte_suivi": p,
                         "nom_affiche": n, "releve_le": aujourdhui})
        resume.append((compte, n_lignes, len(comptes), noms, len(autres)))

    # --- fusion avec les relevés precedents ---
    anciens = sorted(SORTIE.glob("comptes_suivis_*.csv"))
    deja = []
    if anciens:
        with anciens[-1].open(encoding="utf-8") as f:
            deja = list(csv.DictReader(f))
    cles = {(l["compte_vitrine"], l["compte_suivi"]) for l in deja}
    ajoutes = [l for l in tout if (l["compte_vitrine"], l["compte_suivi"]) not in cles]
    fusion = deja + ajoutes

    chemin = SORTIE / f"comptes_suivis_{aujourdhui}.csv"
    with chemin.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fusion[0].keys()))
        w.writeheader()
        w.writerows(fusion)

    print(f"{'COMPTE SOURCE':28s} {'lignes':>7s} {'comptes':>8s} {'noms':>6s} "
          f"{'autres':>7s}  controle")
    for c, nl, nc, nn, na in resume:
        # « autres » contient deja les noms affiches : les additionner aux
        # deux serait un double comptage. Le controle valide est
        # comptes + autres ~= lignes lues.
        somme = nc + na
        etat = "ok" if abs(somme - nl) <= 6 else f"ECART {somme - nl}"
        print(f"{c[:28]:28s} {nl:>7d} {nc:>8d} {nn:>6d} {na:>7d}  {etat}")
    print()
    print(f"{len(tout)} liens releves | {len(ajoutes)} nouveaux | "
          f"{len(fusion)} au total apres fusion")
    print(f"{len({l['compte_suivi'] for l in fusion})} comptes distincts")
    print(f"Ecrit : {chemin}")
    print(f"Ecrit : {DEPOT}\\<compte>.txt")

    if commentaires:
        print()
        print("=== REMARQUES DE VINCENT DANS LE FICHIER ===")
        for c in commentaires:
            print("  ", c[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
