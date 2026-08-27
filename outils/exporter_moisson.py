"""
Sort les resultats de la moisson depuis son fichier de reprise.

POURQUOI CET OUTIL EXISTE

Le 27/08, la moisson s'est arretee a la 381e chaine du lancement. Les donnees
etaient sauves — 977 chaines, 21 911 detections dans le fichier de reprise —
mais **aucun fichier exploitable n'en etait sorti** : `moissonner_videos.py`
n'ecrit son CSV qu'apres la boucle. Le nettoyage suivant a donc relu l'ancien
export, 13 635 detections, sans que rien ne signale l'ecart.

C'est le defaut de conception, pas le plantage : le resultat ne doit pas
dependre de la fin du parcours. Un travail enregistre doit etre lisible.

Cet outil lit `donnees/moisson_videos.json` et en tire le CSV et le rapport, a
tout moment, sans reseau ni quota. Il peut tourner pendant que la moisson
tourne.

Usage :  python outils/exporter_moisson.py
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ETAT = RACINE / "donnees" / "moisson_videos.json"
RECHERCHE = RACINE / "recherche"


def main():
    if not ETAT.exists():
        print(f"{ETAT} absent — rien a exporter.", file=sys.stderr)
        return 1
    etat = json.loads(ETAT.read_text(encoding="utf-8"))
    touchees = etat.get("touchees", [])
    faites = etat.get("faites", {})
    videos = sum(f.get("videos", 0) for f in faites.values())
    filiere = [t for t in touchees if t.get("entites_filiere")]

    if not touchees:
        print("Aucune detection enregistree.", file=sys.stderr)
        return 1

    aujourdhui = date.today().isoformat()
    csv_path = RECHERCHE / f"moisson_videos_{aujourdhui}.csv"
    RECHERCHE.mkdir(parents=True, exist_ok=True)

    # Le fichier de reprise melange des lignes ecrites par plusieurs versions
    # du moissonneur : `extrait_declencheur` est apparu le 27/08 en cours de
    # parcours. On prend donc l'UNION des colonnes, et les lignes anciennes
    # laissent la case vide au lieu de faire echouer l'export.
    colonnes = []
    for ligne in touchees:
        for k in ligne:
            if k not in colonnes:
                colonnes.append(k)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colonnes, extrasaction="ignore",
                           restval="")
        w.writeheader()
        w.writerows(touchees)
    anciennes = sum(1 for l in touchees if "extrait_declencheur" not in l)
    if anciennes:
        print(f"  {anciennes} lignes sans extrait declencheur (moissonnees "
              f"avant la correction du 27/08)", file=sys.stderr)

    md = [f"# Moisson des catalogues YouTube — {aujourdhui}", "",
          "Produit par `outils/exporter_moisson.py`, depuis le fichier de",
          "reprise. Aucun quota consomme : c'est une relecture.", "",
          f"- Chaines moissonnees : **{len(faites)}**",
          f"- Videos examinees : **{videos:,}**".replace(",", " "),
          f"- Videos portant un signal commercial : **{len(touchees)}**",
          f"- **Videos citant la filiere viande/lait : {len(filiere)}**", "",
          "Une citation n'est pas une collaboration : ces lignes passent par",
          "`nettoyer_detections.py` puis par une verification humaine.", ""]

    par_chaine = {}
    for t in filiere:
        d = par_chaine.setdefault(t["chaine"], {"n": 0, "ab": t.get("abonnes", 0),
                                                "ent": set()})
        d["n"] += 1
        for e in t["entites_filiere"].split(" | "):
            d["ent"].add(e)
    md += ["## Chaines citant le plus la filiere", "",
           "| Chaine | Abonnes | Videos | Entites |", "|---|---:|---:|---|"]
    for c, d in sorted(par_chaine.items(), key=lambda x: -x[1]["n"])[:60]:
        md += [f"| {c[:26]} | {d['ab']:,} | {d['n']} | "
               f"{', '.join(sorted(d['ent']))[:70]} |".replace(",", " ")]

    md_path = RECHERCHE / f"moisson_videos_{aujourdhui}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:10]))
    print(f"\nEcrit : {csv_path.name} et {md_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
