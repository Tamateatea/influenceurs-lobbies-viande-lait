"""
Mesure la qualite de la detection contre les jugements humains de Vincent.

CE QUE CE SCRIPT PERMET, ET QUE RIEN D'AUTRE NE PERMET

Vincent a juge les 271 candidats un par un. C'est le **jeu de reference**
qui manquait au projet depuis le debut (METHODOLOGIE section 9.2). Sans lui,
on pouvait affirmer qu'une detection marche ; on ne pouvait pas le mesurer.

Avec lui, on peut essayer des regles et **chiffrer** ce qu'elles gagnent et ce
qu'elles perdent. C'est la seule facon de savoir quand l'automatisation
devient assez bonne pour que l'humain ne verifie plus que par sondage.

LE PROBLEME QU'ON CHERCHE A RESOUDRE

Mesure du 25/08 sur les jugements de Vincent : la detection actuelle a une
precision de **25 %** (67 vrais sur 271). Le detail par entite est accablant
pour certaines :

    CIFOG      0 % — l'alias est « Le Foie Gras », qui designe l'aliment
    CLIPP      0 %
    INTERBEV  23 %
    CNIEL     44 %

**Les interprofessions ont choisi des noms generiques a dessein** : « Les
Produits Laitiers », « Le Foie Gras », « Le Porc Francais ». C'est toute la
strategie de la vitrine (METHODOLOGIE section 2). Elle defait l'appariement de
chaines de caracteres **par construction**.

Ce qui distingue une vraie mention, ce n'est pas le terme : c'est ce qu'il y a
autour. « Merci aux Produits Laitiers **de nous avoir accompagnes** » n'est pas
« bien manger, avec des produits laitiers ».

Usage :
    python outils/evaluer_detection.py                    evalue les regles
    python outils/evaluer_detection.py --recuperer        recupere d'abord
                                                          les descriptions
                                                          completes par l'API
"""

import argparse
import csv
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"
SECRETS = RACINE / "SECRETS.txt"
CACHE = RACINE / "donnees" / "descriptions_completes.json"

# Vocabulaire qui accompagne une vraie collaboration. Volontairement large :
# on mesure ensuite ce qu'il gagne et ce qu'il perd.
VOISINAGE = [
    r"merci\s+(?:a|aux|à)", r"remercie", r"thanks?\s+to", r"accompagn",
    r"financ", r"soutenu", r"soutien", r"partenari?at", r"partner",
    r"collaboration", r"en collab", r"sponsor", r"presente par",
    r"offert par", r"grace a", r"avec le soutien",
]

# Alias dont la chaine designe d'abord autre chose que la marque.
# « Le Foie Gras » est un aliment, « produits laitiers » une categorie.
GENERIQUES = ["le foie gras", "foie gras", "produits laitiers", "le porc francais",
              "porc francais", "volaille francaise", "oeufs de france",
              "la viande", "clipp", "des sensations pures"]


def aplatir(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def sans_accent(t):
    t = unicodedata.normalize("NFKD", str(t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def lire_cle():
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def recuperer_descriptions(video_ids):
    """videos.list — 1 unite pour 50 videos. Descriptions COMPLETES.

    La moisson n'avait garde que 900 caracteres par description, ce qui a
    coupe la mention dans 27 cas sur 271 et rendu ces lignes injugeables.
    """
    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente.", file=sys.stderr)
        return {}
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    manquants = [v for v in video_ids if v not in cache]
    print(f"{len(manquants)} descriptions a recuperer "
          f"({len(manquants)//50 + 1} unites de quota)", file=sys.stderr)
    for i in range(0, len(manquants), 50):
        lot = manquants[i:i + 50]
        url = ("https://www.googleapis.com/youtube/v3/videos?"
               + urllib.parse.urlencode({"part": "snippet", "id": ",".join(lot),
                                         "key": cle}))
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                d = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"  erreur : {e.code}", file=sys.stderr)
            continue
        for it in d.get("items", []):
            cache[it["id"]] = it["snippet"].get("description", "")
        for v in lot:
            cache.setdefault(v, "")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return cache


def charger_jugements():
    """Les verdicts de Vincent, cle = (chaine, debut du titre)."""
    import openpyxl
    wb = openpyxl.load_workbook(CARTO / "A_VERIFIER.xlsx", data_only=True)
    ws = wb["a verifier"]
    out = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[8]:
            out[(str(r[1]), str(r[5])[:40])] = str(r[8])
    wb.close()
    return out


def charger_candidats():
    f = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))[-1]
    with f.open(encoding="utf-8") as fh:
        return [l for l in csv.DictReader(fh)
                if l.get("force", "").startswith("ALIAS")]


def positions(texte_plat, alias):
    """Positions aplaties de chaque alias reconnu."""
    out = []
    for a in [x.strip() for x in alias.split("|") if x.strip()]:
        base = aplatir(a)
        if len(base) < 5:
            continue
        formes = {base}
        for art in ("les", "le", "la", "des", "du", "de"):
            if base.startswith(art) and len(base) - len(art) >= 5:
                formes.add(base[len(art):])
        for f in formes:
            i = texte_plat.find(f)
            if i != -1:
                out.append((i, len(f), a))
    return out


def a_du_voisinage(texte, fenetre=160):
    """Un mot de collaboration est-il proche d'une mention ?"""
    t = sans_accent(texte)
    return any(re.search(m, t) for m in VOISINAGE)


def voisinage_proche(description, alias, fenetre=180):
    """Le vocabulaire de collaboration est-il PRES de la mention ?"""
    plat = aplatir(description)
    t = sans_accent(description)
    # correspondance approximative des positions : on travaille sur le texte
    # sans accents, en cherchant les memes formes mot a mot
    for a in [x.strip() for x in alias.split("|") if x.strip()]:
        motif = re.escape(sans_accent(a).lstrip("@")).replace(r"\ ", r"\s*")
        for m in re.finditer(motif, t):
            debut = max(0, m.start() - fenetre)
            zone = t[debut:m.end() + fenetre]
            if any(re.search(v, zone) for v in VOISINAGE):
                return True
        # forme sans espaces (« lesproduitslaitiers » ↔ « produits laitiers »)
        base = aplatir(a)
        for art in ("les", "le", "la"):
            if base.startswith(art):
                base = base[len(art):]
                break
        if len(base) >= 6:
            i = plat.find(base)
            if i != -1 and a_du_voisinage(description):
                return True
    return False


def est_generique(alias):
    return any(g in sans_accent(alias).lstrip("@").replace("_", " ")
               for g in GENERIQUES)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recuperer", action="store_true")
    args = ap.parse_args()

    jugements = charger_jugements()
    candidats = charger_candidats()
    print(f"{len(jugements)} jugements | {len(candidats)} candidats", file=sys.stderr)

    descriptions = {}
    if args.recuperer or CACHE.exists():
        ids = [l["video_id"] for l in candidats]
        descriptions = recuperer_descriptions(ids) if args.recuperer else \
            json.loads(CACHE.read_text(encoding="utf-8"))

    lignes = []
    for l in candidats:
        cle = (l["chaine"], l["titre"][:40])
        verdict = jugements.get(cle)
        if not verdict:
            continue
        desc = descriptions.get(l["video_id"]) or l.get("description", "").replace(
            " ⏎ ", "\n")
        lignes.append({
            "verdict": verdict,
            "vrai": verdict == "collaboration remuneree",
            "entite": l["entites_retenues"],
            "alias": l["alias_reconnus"],
            "description": desc,
            "chaine": l["chaine"],
            "titre": l["titre"],
            "url": l["url"],
            "abonnes": int(l["abonnes"] or 0),
            "publiee": l["publiee"],
        })

    def evaluer(nom, garde):
        retenus = [l for l in lignes if garde(l)]
        vp = sum(1 for l in retenus if l["vrai"])
        fp = len(retenus) - vp
        total_vrais = sum(1 for l in lignes if l["vrai"])
        prec = 100 * vp / len(retenus) if retenus else 0
        rapp = 100 * vp / total_vrais if total_vrais else 0
        return nom, len(retenus), vp, fp, prec, rapp

    regles = [
        ("A. actuelle : l'alias suffit", lambda l: True),
        ("B. + vocabulaire de collaboration dans la description",
         lambda l: a_du_voisinage(l["description"])),
        ("C. + vocabulaire PRES de la mention",
         lambda l: voisinage_proche(l["description"], l["alias"])),
        ("D. C, et alias generique exclu s'il est seul",
         lambda l: voisinage_proche(l["description"], l["alias"])
         and not (est_generique(l["alias"]) and "@" not in l["alias"])),
    ]

    print()
    print(f"{'REGLE':56s} {'retenus':>8s} {'vrais':>6s} {'faux':>5s} "
          f"{'precision':>10s} {'rappel':>8s}")
    resultats = []
    for nom, garde in regles:
        r = evaluer(nom, garde)
        resultats.append(r)
        print(f"{r[0]:56s} {r[1]:>8d} {r[2]:>6d} {r[3]:>5d} "
              f"{r[4]:>9.0f} % {r[5]:>7.0f} %")

    print()
    print("--- par entite, regle actuelle ---")
    ent = {}
    for l in lignes:
        d = ent.setdefault(l["entite"], [0, 0])
        d[0] += 1
        d[1] += 1 if l["vrai"] else 0
    for e, (t, v) in sorted(ent.items(), key=lambda x: -x[1][0]):
        print(f"   {e[:16]:18s} {v:>3d}/{t:<4d} {100*v/t:>5.0f} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
