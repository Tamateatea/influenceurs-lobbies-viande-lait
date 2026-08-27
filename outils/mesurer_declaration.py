"""
Mesure le signal « case de declaration » contre le jeu de reference de Vincent.

LE DERNIER DES QUATRE

Le projet a quatre signaux sur YouTube. Trois ont ete confrontes aux jugements
de Vincent, celui-ci jamais :

    description          78 % de precision, 100 % de rappel  (JOURNAL 53.1)
    transcription        81 % / 49 %                          (JOURNAL 53.1)
    SponsorBlock         69 % / 13 %  — quasi redondant        (JOURNAL 43)
    case de declaration  JAMAIS MESUREE

C'est pourtant le seul signal **declaratif** : YouTube affiche « Comprend une
communication commerciale » parce que le createur a coche une case. Quand elle
est la, il n'y a rien a interpreter.

CE QU'ON ATTEND, ET POURQUOI ON LE MESURE QUAND MEME

Prediction inscrite AVANT la mesure, pour qu'elle puisse etre dementie :

  - **precision tres haute** — une declaration est un aveu, pas un indice ;
  - **rappel faible** — le cas Inoxtag x CNIEL trouve le 24/08 n'etait pas
    declare, et c'est precisement ce qui fait l'interet du projet.

Si la precision n'est PAS tres haute, quelque chose ne va pas dans la lecture
de la page, et il faudra le comprendre avant d'utiliser ce signal.

Si le rappel est eleve, alors la filiere declare correctement et le projet
perd beaucoup de son objet — ce serait une bonne nouvelle pour tout le monde
sauf pour l'outil. Autant le savoir.

CE QUE CA COUTE

Aucun quota d'API : la case n'existe que dans la page publique. Mais une page
par video, et YouTube renvoie HTTP 429 au-dela d'un certain rythme. Le script
s'arrete au-dela de 10 % d'echecs plutot que de compter une page non lue comme
« pas de declaration » — l'erreur du 24/08, qui avait produit un rapport
affirmant « aucune entite trouvee » sur 288 videos jamais telechargees.

Usage :
    python outils/mesurer_declaration.py --max 120 --pause 1.5
"""

import argparse
import csv
import gzip
import json
import random
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"
CACHE = RACINE / "donnees" / "declarations.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ecriture_sure import ecrire_sur

NAVIGATEURS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

MARQUEUR = "paidContentOverlayRenderer"


def page(vid, pause, essais=3):
    """Rend (contenu, erreur). Une erreur n'est JAMAIS un « pas de signal »."""
    url = f"https://www.youtube.com/watch?v={vid}&hl=fr&gl=FR"
    for essai in range(essais):
        req = urllib.request.Request(url, headers={
            "User-Agent": random.choice(NAVIGATEURS),
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Accept-Encoding": "gzip",
        })
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                brut = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    brut = gzip.decompress(brut)
                return brut.decode("utf-8", "replace"), None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                if essai < essais - 1:
                    time.sleep(pause * 6 * (essai + 1))
                    continue
                return None, "HTTP 429"
            return None, f"HTTP {e.code}"
        except Exception as e:
            if essai < essais - 1:
                time.sleep(pause * 2)
                continue
            return None, type(e).__name__
    return None, "epuise"


def charger_juges():
    """Les videos tranchees par Vincent, tous classeurs confondus."""
    import openpyxl
    juges = {}
    for f in sorted(CARTO.glob("A_VERIFIER*.xlsx")):
        try:
            ws = openpyxl.load_workbook(f, data_only=True)["a verifier"]
        except Exception:
            continue
        entetes = [str(c.value or "") for c in ws[1]]
        col = next((i for i, h in enumerate(entetes) if "VERDICT" in h.upper()),
                   None)
        if col is None:
            continue
        for r in ws.iter_rows(min_row=2, values_only=True):
            if col < len(r) and r[col]:
                juges[(str(r[1]), str(r[5])[:40])] = str(r[col])

    fichiers = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))
    if not fichiers:
        return []
    out, vus = [], set()
    with fichiers[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            v = juges.get((l["chaine"], l["titre"][:40]))
            if not v or l["video_id"] in vus:
                continue
            vus.add(l["video_id"])
            out.append({"video_id": l["video_id"], "chaine": l["chaine"],
                        "titre": l["titre"], "url": l["url"],
                        "abonnes": int(l["abonnes"] or 0), "verdict": v,
                        "vrai": v == "collaboration remuneree"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=120)
    ap.add_argument("--pause", type=float, default=1.5)
    args = ap.parse_args()

    lignes = charger_juges()
    if not lignes:
        print("Aucune video jugee trouvee.", file=sys.stderr)
        return 1
    print(f"{len(lignes)} videos jugees par Vincent", file=sys.stderr)

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    # les vraies collaborations d'abord : c'est sur elles que le rappel se joue
    lignes.sort(key=lambda l: (not l["vrai"], -l["abonnes"]))

    n, echecs = 0, []
    for l in lignes:
        if l["video_id"] in cache or n >= args.max:
            continue
        contenu, err = page(l["video_id"], args.pause)
        n += 1
        if err:
            echecs.append((l["video_id"], err))
        else:
            cache[l["video_id"]] = MARQUEUR in contenu
        if n % 10 == 0:
            ecrire_sur(CACHE, json.dumps(cache, ensure_ascii=False))
            print(f"  {n} pages lues, {len(echecs)} echecs", file=sys.stderr)
        time.sleep(args.pause)
    ecrire_sur(CACHE, json.dumps(cache, ensure_ascii=False))

    part = len(echecs) / max(n, 1)
    if n and part > 0.10:
        print(f"ARRET : {100*part:.0f} % des pages n'ont pas ete lues "
              f"({len(echecs)}/{n}). Une page non lue n'est PAS une absence de "
              f"declaration — mesurer la-dessus produirait un chiffre faux.",
              file=sys.stderr)
        for vid, err in echecs[:5]:
            print(f"    {vid} : {err}", file=sys.stderr)
        return 2

    mesurables = [l for l in lignes if l["video_id"] in cache]
    for l in mesurables:
        l["declaree"] = cache[l["video_id"]]

    total_vrais = sum(1 for l in mesurables if l["vrai"])
    declarees = [l for l in mesurables if l["declaree"]]
    vrais_declares = sum(1 for l in declarees if l["vrai"])
    manquees = [l for l in mesurables if l["vrai"] and not l["declaree"]]

    precision = 100 * vrais_declares / len(declarees) if declarees else 0
    rappel = 100 * vrais_declares / total_vrais if total_vrais else 0

    md = [f"# Le signal « case de declaration », mesure — {date.today().isoformat()}",
          "", "Produit par `outils/mesurer_declaration.py`. Aucun quota d'API.", "",
          "YouTube affiche « Comprend une communication commerciale » quand le",
          "createur a coche une case. C'est le seul signal **declaratif** du",
          "projet : quand il est la, il n'y a rien a interpreter.", "",
          f"- Videos jugees et lues : **{len(mesurables)}**",
          f"- Vraies collaborations dedans : **{total_vrais}**",
          f"- Pages non lues, exclues du calcul : {len(echecs)}", "",
          "| Signal | Retenus | Vrais | Precision | Rappel |",
          "|---|---:|---:|---:|---:|",
          f"| Case de declaration | {len(declarees)} | {vrais_declares} | "
          f"{precision:.0f} % | {rappel:.0f} % |", "",
          "## Ce que ces deux nombres veulent dire", ""]

    if precision >= 90:
        md += [f"**Precision {precision:.0f} %.** Une declaration est un aveu :",
               "quand la case est cochee, le cas est bon. Ce signal peut donc",
               "alimenter le registre avec le degre de certitude le plus haut,",
               "« remuneration confirmee », sans verification supplementaire.", ""]
    else:
        md += [f"**Precision {precision:.0f} %, plus basse qu'attendu.** La",
               "prediction inscrite avant la mesure etait « tres haute ». Elle est",
               "dementie, et cela demande une explication avant tout usage : soit",
               "la case signale d'autres partenariats que ceux qui nous occupent,",
               "soit la lecture de la page est fautive.", ""]

    md += [f"**Rappel {rappel:.0f} %.** C'est la mesure qui justifie le projet.",
           f"{len(manquees)} vraies collaborations sur {total_vrais} ne sont pas",
           "declarees : sans un outil qui lit les descriptions et les",
           "transcriptions, elles resteraient invisibles.", ""]

    if manquees:
        md += ["## Vraies collaborations NON declarees", "",
               "| Chaine | Abonnes | Titre | Regarder |", "|---|---:|---|---|"]
        for l in sorted(manquees, key=lambda x: -x["abonnes"])[:40]:
            md += [f"| {l['chaine'][:24]} | {l['abonnes']:,} | "
                   f"{l['titre'][:46]} | {l['url']} |".replace(",", " ")]
        md += [""]

    md += ["## Limite", "",
           "Ces videos viennent toutes du canal « description » : elles ont ete",
           "reperees parce qu'un texte citait la filiere. Une collaboration",
           "declaree mais jamais ecrite n'avait aucune raison d'entrer ici, donc",
           "**le rappel mesure ci-dessus est un plafond, pas une estimation**.",
           "Seul un tirage aleatoire le trancherait.", ""]

    chemin = RECHERCHE / f"mesure_declaration_{date.today().isoformat()}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:16]))
    print(f"\nEcrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
