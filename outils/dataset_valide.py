"""
Le jeu de donnees restreint aux createurs que Vincent a valides lui-meme.

POURQUOI CETTE VERSION EXISTE

Vincent, 29/08 : « une colonne influenceurs qui ne soit pas autant polluee de
lobbies et de marques elles-memes ».

Les versions precedentes partaient de la detection et essayaient de retirer le
bruit apres coup. Chaque filtre en laissait passer, et il en a fallu quatre.
Celle-ci fait l'inverse : **elle part de la liste des createurs qu'un humain a
valides**, et ne garde que leurs contenus.

C'est plus petit et c'est plus sur. Un jeu de donnees de plaidoyer se juge a ce
qu'il peut soutenir, pas a son nombre de lignes.

D'OU VIENT LA LISTE BLANCHE

Trois sources, toutes issues du travail de Vincent :

    A_VERIFIER*.xlsx                  verdict « collaboration remuneree »
    CREATEURS_SUR_LES_SITES.xlsx      verdict commencant par « oui »
    CREATEURS_NOMMES_PAR_LES_LOBBIES  verdict « c'est un createur »

Un nom reconnu comme commanditaire par `createurs.py` est ecarte meme s'il
figure dans ces listes : Vincent a pu valider « La Volaille Francaise » comme
« marque ou label », et ce n'est pas un createur.

CE QUE CE FICHIER N'EST TOUJOURS PAS

Un registre publiable. Le createur est confirme ; le caractere remunere de
chaque contenu ne l'est pas toujours. Mais c'est le premier fichier du projet
dont **la colonne influenceur ne contient que des personnes**.

Usage :  python outils/dataset_valide.py
"""

import csv
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import openpyxl

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir
from createurs import est_un_commanditaire
from medias import est_media

AUDIENCE = re.compile(r"([\d]+(?:[,.]\d+)?)\s*([kKmM])\s*"
                      r"(?:followers|subscribers|subscriver|subscibers|abonnes)")
PSEUDO = re.compile(r"@+([A-Za-z0-9_.\-]{3,40})")


def liste_blanche():
    """Les createurs valides par Vincent, avec leur fiche."""
    valides = {}

    def poser(nom, typ="", com="", source=""):
        nom = str(nom or "").strip()
        if not nom or est_un_commanditaire(nom) or est_media(nom):
            return
        com = com or ""
        pseudo = PSEUDO.search(com)
        aud = AUDIENCE.search(com)
        plat = ("Instagram" if "insta" in com.lower()
                else "YouTube" if "youtube" in com.lower()
                else "TikTok" if "tiktok" in com.lower() else "")
        d = valides.setdefault(aplatir(nom), {
            "nom": nom, "pseudo": "", "abonnes": "", "plateforme": "",
            "type": "", "sources": set()})
        d["sources"].add(source)
        if pseudo and not d["pseudo"]:
            d["pseudo"] = "@" + pseudo.group(1)
        if aud and not d["abonnes"]:
            d["abonnes"] = aud.group(1).replace(",", ".") + aud.group(2).upper()
        if plat and not d["plateforme"]:
            d["plateforme"] = plat
        if typ and not d["type"]:
            d["type"] = (typ.replace("oui — ", "").replace("non — ", "")
                         .replace("c'est un ", "").strip())

    # --- 1) les videos jugees « collaboration remuneree » ---
    juges = {}
    for f in sorted(CARTO.glob("A_VERIFIER*.xlsx")):
        try:
            ws = openpyxl.load_workbook(f, data_only=True)["a verifier"]
        except Exception:
            continue
        entetes = [str(c.value or "") for c in ws[1]]
        col = next((i for i, x in enumerate(entetes) if "VERDICT" in x.upper()),
                   None)
        if col is None:
            continue
        for r in ws.iter_rows(min_row=2, values_only=True):
            if col < len(r) and r[col]:
                juges[(str(r[1]), str(r[5])[:40])] = str(r[col])
    fichiers = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))
    if fichiers:
        with fichiers[-1].open(encoding="utf-8") as fh:
            for l in csv.DictReader(fh):
                if juges.get((l["chaine"], l["titre"][:40])) == \
                        "collaboration remuneree":
                    poser(l["chaine"], source="description YouTube")

    # --- 2) et 3) les deux classeurs de createurs ---
    for nom_f, depart, col_nom, col_verdict, col_com, mot in [
            ("CREATEURS_SUR_LES_SITES.xlsx", 25, 2, 5, 6, "oui"),
            ("CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx", 35, 2, 9, 11, "createur")]:
        f = CARTO / nom_f
        if not f.exists():
            continue
        try:
            ws = openpyxl.load_workbook(f, data_only=True)["createurs"]
        except Exception:
            continue
        for r in range(depart, ws.max_row + 1):
            v = str(ws.cell(row=r, column=col_verdict).value or "")
            if mot not in v or any(x in v for x in ("serie", "marque", "media")):
                continue
            typ = v if nom_f.startswith("CREATEURS_SUR") else str(
                ws.cell(row=r, column=10).value or "")
            poser(ws.cell(row=r, column=col_nom).value, typ,
                  str(ws.cell(row=r, column=col_com).value or ""),
                  "site du lobby" if nom_f.startswith("CREATEURS_SUR")
                  else "chaine du lobby")
    return valides


def main():
    valides = liste_blanche()
    print(f"{len(valides)} createurs valides par Vincent", file=sys.stderr)
    if not valides:
        return 1

    fichiers = sorted(RECHERCHE.glob("dataset_2*.csv"))
    if not fichiers:
        print("Aucun dataset_*.csv.", file=sys.stderr)
        return 1
    with fichiers[-1].open(encoding="utf-8") as fh:
        toutes = list(csv.DictReader(fh))
    if not toutes:
        return 1
    colonnes = list(toutes[0].keys())

    lignes = []
    for l in toutes:
        cle = aplatir(l["nom_influenceur"])
        if cle not in valides:
            continue
        fiche = valides[cle]
        l = dict(l)
        l["nom_influenceur"] = fiche["nom"]
        l["alias_influenceur"] = fiche["pseudo"] or l.get("alias_influenceur", "")
        l["nombre_abonnes"] = fiche["abonnes"] or l.get("nombre_abonnes", "")
        l["type_de_createur"] = fiche["type"] or l.get("type_de_createur", "")
        if fiche["plateforme"] and not l.get("plateforme"):
            l["plateforme"] = fiche["plateforme"]
        l["verifie_par_humain"] = "oui"
        lignes.append(l)

    # Les createurs valides dont aucun contenu n'est encore rattache restent
    # dans le fichier, en ligne « sans contenu ». Les omettre ferait disparaitre
    # une partie du travail de Vincent, et c'est justement ce qu'il reproche
    # aux versions precedentes.
    presents = {aplatir(l["nom_influenceur"]) for l in lignes}
    for cle, f in valides.items():
        if cle in presents:
            continue
        vide = {c: "" for c in colonnes}
        vide.update({
            "nom_influenceur": f["nom"], "alias_influenceur": f["pseudo"],
            "nombre_abonnes": f["abonnes"], "plateforme": f["plateforme"],
            "type_de_createur": f["type"], "verifie_par_humain": "oui",
            "canal_de_detection": " | ".join(sorted(x for x in f["sources"] if x)),
            "degre_de_certitude": "createur valide, contenu a rattacher",
            "nature_de_la_ligne": "collaboration avec un tiers"})
        lignes.append(vide)

    aujourdhui = date.today().isoformat()
    chemin = RECHERCHE / f"dataset_valide_{aujourdhui}.csv"
    with chemin.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=colonnes)
        w.writeheader()
        w.writerows(lignes)

    createurs = len({aplatir(l["nom_influenceur"]) for l in lignes})
    avec = sum(1 for l in lignes if l.get("contenu_url"))
    md = [f"# Jeu de donnees valide — {aujourdhui}", "",
          "Produit par `outils/dataset_valide.py`.", "",
          "**Ne contient que des createurs valides par Vincent.** Les versions",
          "precedentes partaient de la detection et retiraient le bruit apres",
          "coup ; il a fallu quatre filtres et il en passait encore. Celle-ci",
          "part de la liste des personnes qu'un humain a confirmees.", "",
          f"- Createurs : **{createurs}**",
          f"- Lignes : **{len(lignes)}**, dont **{avec}** avec un contenu date",
          f"- Createurs confirmes sans contenu encore rattache : "
          f"{len(lignes) - avec}", "",
          "| Commanditaire | Lignes |", "|---|---:|"]
    for c, n in Counter(l["commanditaire"] for l in lignes
                        if l["commanditaire"]).most_common(12):
        md += [f"| {c} | {n} |"]
    md += ["", "**Aucune ligne n'est publiable sans verification "
           "supplementaire** : le createur est confirme, le caractere remunere",
           "de chaque contenu ne l'est pas toujours.", ""]
    (RECHERCHE / f"dataset_valide_{aujourdhui}.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:13]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
