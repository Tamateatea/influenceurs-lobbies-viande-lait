"""
L'experience que la premiere mesure ne pouvait pas faire.

LE PROBLEME DE PROTOCOLE

`mesurer_transcriptions.py` a compare la transcription et la description sur
les videos jugees par Vincent. Resultat : zero vraie collaboration vue par la
transcription seule.

**Ce zero ne prouve rien.** L'echantillon est fait de videos trouvees PAR la
description : une collaboration annoncee uniquement a l'oral n'avait aucune
chance d'y figurer. Le protocole ne pouvait pas repondre a la question.

L'EXPERIENCE CORRECTE

On prend des videos **sans aucun signal en description**, sur des chaines dont
on SAIT qu'elles travaillent avec la filiere. Si l'oral y trouve des mentions,
la transcription voit ce que rien d'autre ne voit. Sinon, elle est redondante
et son cout — plusieurs secondes par video — n'est pas justifie a grande
echelle.

Le choix des chaines n'est pas neutre et c'est assume : on cherche ou il y a
le plus de chances de trouver. Un resultat positif prouvera que le signal
existe ; il ne mesurera pas sa frequence, ce que seul un tirage aleatoire
ferait.

Usage :  python outils/experience_transcription.py --videos 40
"""

import argparse
import importlib.util
import json
import random
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
CACHE = RACINE / "donnees" / "transcriptions_temoins.json"
API = "https://www.googleapis.com/youtube/v3/"

# Chaines dont une collaboration filiere est etablie. C'est la qu'une mention
# orale non ecrite a le plus de chances d'exister.
CIBLES = {
    "UCo6Z9cEI8Hf3nyrLUfDITtA": "Inoxtag 2.0",
    "UCL9aTJb0ur4sovxcppAopEw": "Inoxtag",
    "UCo3i0nUzZjjLuM7VjAVz4zA": "Michou",
    "UC8Q0SLrZLiTj5s4qc9aad-w": "Mister V",
    "UCNGq4mP3Ds5OUGjPo8IJOcw": "Valouzz",
    "UCww2zZWg4Cf5xcRKG-ThmXQ": "Norman",
}


def lire_cle():
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", type=int, default=40)
    args = ap.parse_args()

    spec = importlib.util.spec_from_file_location(
        "mt", RACINE / "outils" / "mesurer_transcriptions.py")
    mt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mt)
    termes = mt.charger_alias()
    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente.", file=sys.stderr)
        return 1

    # --- 1) lister des videos SANS signal en description ---
    temoins, depense = [], 0
    for cid, nom in CIBLES.items():
        d, err = appel("channels", {"part": "contentDetails", "id": cid}, cle)
        depense += 1
        if err or not d.get("items"):
            continue
        up = d["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        d, err = appel("playlistItems", {"part": "snippet", "playlistId": up,
                                         "maxResults": 50}, cle)
        depense += 1
        if err:
            continue
        for it in d.get("items", []):
            s = it["snippet"]
            vid = s.get("resourceId", {}).get("videoId", "")
            texte = (s.get("title", "") + " " + (s.get("description", "") or ""))
            plat = mt.aplatir(texte)
            if any(f in plat for f in termes):
                continue            # la description parle deja : hors experience
            temoins.append({"video_id": vid, "chaine": nom,
                            "titre": s.get("title", "")[:90]})

    random.seed(20260827)
    random.shuffle(temoins)
    temoins = temoins[:args.videos]
    print(f"{len(temoins)} videos temoins, sans signal en description "
          f"({depense} unites de quota)", file=sys.stderr)

    # --- 2) transcrire et chercher ---
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    trouves = []
    for i, t in enumerate(temoins, 1):
        if t["video_id"] not in cache:
            texte = mt.transcription(t["video_id"])
            cache[t["video_id"]] = texte or ""
            if i % 10 == 0:
                CACHE.parent.mkdir(parents=True, exist_ok=True)
                CACHE.write_text(json.dumps(cache, ensure_ascii=False),
                                 encoding="utf-8")
                print(f"  {i}/{len(temoins)}", file=sys.stderr)
        texte = cache[t["video_id"]]
        if not texte:
            continue
        plat = mt.aplatir(texte)
        ent = {e for f, (_a, e) in termes.items() if f in plat}
        if ent:
            i0 = 0
            for f, (_a, e) in termes.items():
                if f in plat:
                    i0 = plat.find(f)
                    break
            trouves.append(dict(t, entites=" | ".join(sorted(ent)),
                                extrait=texte[max(0, i0 - 150):i0 + 250]))
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    avec = sum(1 for t in temoins if cache.get(t["video_id"]))
    md = [f"# La transcription voit-elle ce que la description tait ? — "
          f"{date.today().isoformat()}", "",
          "Produit par `outils/experience_transcription.py`.", "",
          "## Protocole", "",
          "Videos **sans aucun signal en description**, tirees de chaines dont",
          "une collaboration filiere est etablie. Si l'oral y trouve des",
          "mentions, la transcription voit ce que rien d'autre ne voit.", "",
          f"- Videos temoins : **{len(temoins)}**",
          f"- Transcriptions obtenues : **{avec}**",
          f"- **Videos ou l'oral cite la filiere : {len(trouves)}**", ""]

    if trouves:
        md += ["## Ce que seule la transcription voit", "",
               "**A verifier a la main** : une mention orale peut etre une",
               "blague, une recette ou un commentaire — voir JOURNAL 20.4.", "",
               "| Chaine | Entite | Titre | Extrait |", "|---|---|---|---|"]
        for t in trouves:
            md += [f"| {t['chaine']} | **{t['entites']}** | {t['titre'][:40]} "
                   f"| {t['extrait'][:180].replace('|', ' ')} |"]
    else:
        md += ["## Aucune", "",
               "Sur cet echantillon, l'oral ne cite jamais la filiere quand la",
               "description se tait. **La transcription est donc redondante**,",
               "et son cout — plusieurs secondes par video — ne se justifie pas",
               "a grande echelle.", "",
               "Reserve : l'echantillon est petit et les chaines choisies, pas",
               "tirees au sort. Un resultat nul ici n'exclut pas le phenomene,",
               "il indique qu'il n'est pas frequent la ou on le cherchait.", ""]

    chemin = RECHERCHE / f"experience_transcription_{date.today().isoformat()}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nEcrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
