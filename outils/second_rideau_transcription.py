"""
Applique la transcription aux chaines dont une collaboration est deja etablie.

D'OU VIENT CETTE STRATEGIE

Mesure du 27/08 (JOURNAL 53) : sur 37 videos **sans aucun signal en
description**, prises sur des chaines connues pour collaborer, une porte une
mention orale que rien d'autre ne voyait — Inoxtag 2.0, « comme d'habitude les
produits laitiers qui nous accompagnent partout ».

La transcription voit donc ce que la description tait. Mais elle coute
plusieurs secondes par video : sur 2 600 chaines et 300 000 videos, c'est hors
de portee.

D'ou le **second rideau** : on ne transcrit pas au hasard, on transcrit les
chaines ou l'on sait deja qu'il y a quelque chose. Une collaboration est
rarement unique — « comme d'habitude » le dit assez — et c'est la que le
rendement est le meilleur.

CE QUE CA COUTE

Quota d'API : une unite par tranche de 50 videos, pour lister les catalogues.
Quelques dizaines d'unites en tout.

Temps : quelques secondes par video, sans quota. C'est la contrainte reelle.

CE QUE CA NE PROUVE PAS

Une mention orale n'etablit pas la remuneration. « Les produits laitiers qui
nous accompagnent » peut designer un partenariat, une dotation en produits ou
une simple habitude. Tout ce qui sort d'ici va en verification humaine avec le
degre « lien commercial documente », jamais « remuneration confirmee ».

Et le faux positif oral existe : « cette video est sponsorisee par Odica »
etait une blague sur des appareils auditifs (JOURNAL 20.4).

Usage :
    python outils/second_rideau_transcription.py --videos 250
"""

import argparse
import csv
import importlib.util
import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"
CACHE = RACINE / "donnees" / "transcriptions_second_rideau.json"
API = "https://www.googleapis.com/youtube/v3/"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ecriture_sure import ecrire_sur
from perimetre import entites_hors_perimetre


def charger(nom):
    spec = importlib.util.spec_from_file_location(
        nom, RACINE / "outils" / f"{nom}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def lire_cle():
    import re
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def appel(endpoint, params, cle):
    url = API + endpoint + "?" + urllib.parse.urlencode(dict(params, key=cle))
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            return json.loads(r.read().decode("utf-8")), None
    except Exception as e:
        return None, str(e)[:120]


def chaines_confirmees():
    """Les chaines ou Vincent a confirme au moins une collaboration remuneree."""
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

    fichiers = sorted(RECHERCHE.glob("moisson_videos_*.csv"))
    if not fichiers:
        return {}
    out = {}
    with fichiers[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            if juges.get((l["chaine"], l["titre"][:40])) == "collaboration remuneree":
                out[l["channel_id"]] = l["chaine"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", type=int, default=250,
                    help="plafond de videos a transcrire ; c'est le temps qui")
    ap.add_argument("--par-chaine", type=int, default=100)
    args = ap.parse_args()

    mt = charger("mesurer_transcriptions")
    termes = mt.charger_alias()

    # Le classeur porte des entites deliberement hors sujet — Intercereales est
    # un groupe temoin. Le premier essai du 27/08 a remonte une conversation
    # sur du fromage blanc comme « detection Intercereales ». On les retire.
    hors = entites_hors_perimetre()
    avant = len(termes)
    termes = {f: v for f, v in termes.items() if v[1].split(" (")[0].strip()
              not in hors}
    if avant != len(termes):
        print(f"{avant - len(termes)} formes retirees : entites hors perimetre "
              f"({', '.join(sorted(hors))})", file=sys.stderr)
    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente.", file=sys.stderr)
        return 1

    cibles = chaines_confirmees()
    if not cibles:
        print("Aucune chaine confirmee — rien a faire.", file=sys.stderr)
        return 1
    print(f"{len(cibles)} chaines avec une collaboration confirmee | "
          f"{len(termes)} formes d'alias", file=sys.stderr)

    # --- 1) lister leurs videos SANS signal en description ---
    temoins, depense = [], 0
    for cid, nom in cibles.items():
        d, err = appel("channels", {"part": "contentDetails", "id": cid}, cle)
        depense += 1
        if err or not d.get("items"):
            print(f"  {nom} : catalogue introuvable ({err})", file=sys.stderr)
            continue
        up = d["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        page, pris = None, 0
        while pris < args.par_chaine:
            p = {"part": "snippet", "playlistId": up, "maxResults": 50}
            if page:
                p["pageToken"] = page
            d, err = appel("playlistItems", p, cle)
            depense += 1
            if err:
                break
            for it in d.get("items", []):
                s = it["snippet"]
                vid = s.get("resourceId", {}).get("videoId", "")
                texte = s.get("title", "") + " " + (s.get("description", "") or "")
                if not vid or any(f in mt.aplatir(texte) for f in termes):
                    continue        # la description parle deja : rien a gagner
                temoins.append({"video_id": vid, "chaine": nom,
                                "titre": s.get("title", "")[:120],
                                "publiee": (s.get("publishedAt") or "")[:10]})
                pris += 1
            page = d.get("nextPageToken")
            if not page:
                break
        print(f"  {nom[:26]:28s} {pris:>4d} videos sans signal", file=sys.stderr)

    temoins = temoins[:args.videos]
    print(f"\n{len(temoins)} videos a transcrire | {depense} unites de quota",
          file=sys.stderr)

    # --- 2) transcrire et chercher ---
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    trouves = []
    for i, t in enumerate(temoins, 1):
        if t["video_id"] not in cache:
            cache[t["video_id"]] = mt.transcription(t["video_id"]) or ""
            if i % 10 == 0:
                ecrire_sur(CACHE, json.dumps(cache, ensure_ascii=False))
                print(f"  {i}/{len(temoins)} — {len(trouves)} trouvees",
                      file=sys.stderr)
        texte = cache[t["video_id"]]
        if not texte:
            continue
        plat = mt.aplatir(texte)
        # On cherche la position de CHAQUE forme reconnue, pas de la premiere
        # de la table : l'erreur du 27/08 affichait un extrait sans rapport.
        touches = [(plat.find(f), f, e) for f, (_a, e) in termes.items()
                   if f in plat]
        if not touches:
            continue
        touches.sort()
        i0 = touches[0][0]
        entites = sorted({e for _i, _f, e in touches})
        trouves.append(dict(t, entites=" | ".join(entites),
                            extrait=texte[max(0, i0 - 200):i0 + 300].strip()))
    ecrire_sur(CACHE, json.dumps(cache, ensure_ascii=False))

    avec = sum(1 for t in temoins if cache.get(t["video_id"]))
    aujourdhui = date.today().isoformat()

    if trouves:
        chemin_csv = RECHERCHE / f"second_rideau_{aujourdhui}.csv"
        with chemin_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(trouves[0].keys()))
            w.writeheader()
            w.writerows(trouves)

    md = [f"# Transcription en second rideau — {aujourdhui}", "",
          "Produit par `outils/second_rideau_transcription.py`.", "",
          "Videos **sans aucun signal en description**, prises sur les chaines",
          "ou une collaboration est deja confirmee. Ce que trouve la",
          "transcription ici, rien d'autre ne le voyait.", "",
          f"- Chaines examinees : **{len(cibles)}**",
          f"- Videos temoins : **{len(temoins)}**",
          f"- Transcriptions obtenues : **{avec}**",
          f"- **Videos citant la filiere : {len(trouves)}**",
          f"- Quota depense : {depense} unites", "",
          "**Une mention orale n'etablit pas la remuneration.** Degre de",
          "certitude au plus « lien commercial documente ». Et le faux positif",
          "oral existe : une blague, une recette, un commentaire.", ""]

    if trouves:
        md += ["| Chaine | Entite | Publiee | Titre | Ce qui est dit |",
               "|---|---|---|---|---|"]
        for t in sorted(trouves, key=lambda x: x["chaine"]):
            md += [f"| {t['chaine'][:20]} | **{t['entites'][:26]}** | "
                   f"{t['publiee']} | {t['titre'][:34]} | "
                   f"{t['extrait'][:200].replace('|', ' ')} |"]
    else:
        md += ["## Aucune", "",
               "Sur cet echantillon, l'oral ne cite jamais la filiere quand la",
               "description se tait. Cela ne contredit pas le cas Inoxtag 2.0 du",
               "27/08 : un phenomene rare reste rare. Cela borne son rendement.", ""]

    chemin = RECHERCHE / f"second_rideau_{aujourdhui}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:14]))
    print(f"\nEcrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
