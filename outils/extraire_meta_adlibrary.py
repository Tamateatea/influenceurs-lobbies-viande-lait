#!/usr/bin/env python3
"""
Extrait les annonceurs viande/lait du rapport public Meta Ad Library France.

Source : FacebookAdLibraryReport_<date>_FR_lifelong.zip, telecharge sur
https://www.facebook.com/ads/library/report/

PERIMETRE DE CETTE SOURCE — a lire avant d'utiliser les chiffres.
Ce rapport ne couvre QUE les publicites relatives a des enjeux sociaux,
electoraux ou politiques. Il ne contient ni les publicites commerciales
ordinaires, ni les contenus de marque. Le fait qu'Interbev et le Cniel y
figurent signifie que Meta classe leur communication comme publicite a
caractere politique.

Les montants sont des paliers, pas des valeurs exactes ("<=100" notamment).

Lancer :  python outils/extraire_meta_adlibrary.py
"""

import csv
import io
import re
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "donnees" / "sources" / "meta" / "annonceurs_filiere.csv"

# Termes de la filiere. Volontairement large, filtre ensuite.
PAT_FILIERE = re.compile(
    r"INTERBEV|CNIEL|LAITIER|VIANDE|LACTALIS|DANONE|CHARAL|BIGARD|SODIAAL"
    r"|SAVENCIA|ELEVAGE|ÉLEVAGE|\bPORC\b|VOLAILLE|FROMAG|BOEUF|BŒUF|\bLAIT\b"
    r"|INAPORC|ANVOL|CIFOG|FOIE GRAS|CHARCUT|BOUCHERIE",
    re.I,
)

# Faux positifs massifs : patronymes (Boucher, Porcher, Cordeboeuf), toponymes
# (Bouches-du-Rhone, Bouchain, Tresboeuf), porcelaine, moules de bouchot.
PAT_EXCLUS = re.compile(
    r"BOUCHES?-DU-RHONE|BOUCHES DU RHONE|PORCELAIN|PORCELLANE|BOUCHOT"
    r"|BOUCHAIN|BOUCHEZ|BOUCHARD|BOUCHER LEGACY|PORCHER|CORDEBOEUF"
    r"|TRESBŒUF|TRESBOEUF|BOUCHONS|BOUCHON|LAIT MATERNEL|LAIT UP"
    r"|PORCELANOSA|SAUVIGNOIS|PLESSIS",
    re.I,
)


def montant(v):
    """'<=100' et '' -> 0. Sert uniquement au tri, jamais a un total publie."""
    v = (v or "").replace("≤", "").replace("<", "").replace("=", "").strip()
    return int(v) if v.isdigit() else 0


def main():
    archives = sorted(RACINE.glob("FacebookAdLibraryReport_*_FR_lifelong.zip"))
    archives += sorted((RACINE / "donnees" / "sources" / "meta").glob("*.zip"))
    if not archives:
        raise SystemExit(
            "Archive introuvable. Telecharge le rapport France sur "
            "https://www.facebook.com/ads/library/report/ et place le .zip "
            "a la racine du projet ou dans donnees/sources/meta/."
        )
    archive = archives[0]

    with zipfile.ZipFile(archive) as z:
        nom = next(n for n in z.namelist() if n.endswith("_advertisers.csv"))
        texte = z.read(nom).decode("utf-8-sig", "replace")

    rows = list(csv.DictReader(io.StringIO(texte)))

    retenus = []
    for r in rows:
        champ = (r["Page name"] or "") + " " + (r["Disclaimer"] or "")
        if PAT_FILIERE.search(champ) and not PAT_EXCLUS.search(champ):
            retenus.append(r)

    retenus.sort(key=lambda r: -montant(r["Amount spent (EUR)"]))

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["page", "financeur_declare", "montant_eur", "nb_annonces",
                    "page_id", "sans_financeur_declare"])
        for r in retenus:
            sans = "OUI" if "without a disclaimer" in (r["Disclaimer"] or "") else ""
            w.writerow([r["Page name"], r["Disclaimer"], r["Amount spent (EUR)"],
                        r["Number of ads in Library"], r["Page ID"], sans])

    print(f"Source   : {archive.name}")
    print(f"Analyse  : {len(rows)} annonceurs")
    print(f"Retenus  : {len(retenus)} pages de la filiere")
    print(f"Ecrit    : {SORTIE.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
