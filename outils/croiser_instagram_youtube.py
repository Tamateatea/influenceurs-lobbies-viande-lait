"""
Cherche, pour chaque compte Instagram connu, s'il existe une chaine YouTube
portant le meme pseudo.

L'IDEE

Le projet connait 552 comptes Instagram suivis par les vitrines des lobbies,
mais ne surveille que 27 chaines YouTube — celles qu'on a nommees a la main.
Or beaucoup de createurs emploient le MEME pseudo sur les deux plateformes.

`channels.list?forHandle=<pseudo>` coute **1 unite** de quota et repond
exactement a la question « existe-t-il une chaine YouTube @<pseudo> ? ».
552 essais coutent donc ~552 unites sur les ~10 000 disponibles par jour.

Ce que ca produit : une liste de chaines YouTube **derivee des sources**, et
non fournie a la main. C'est le point important — l'outil final ne doit pas
dependre du travail manuel de Vincent pour savoir qui surveiller.

CE QUE CE N'EST PAS

Un compte YouTube portant le meme pseudo qu'un compte Instagram n'est **pas**
la preuve qu'il s'agit de la meme personne. C'est une **hypothese de
rattachement**, a verifier — le registre est nominatif, une confusion
d'homonyme y serait disqualifiante (METHODOLOGIE section 8). Le script
enregistre donc le rapprochement comme candidat, jamais comme fait.

Et surtout : etre suivi par une vitrine ne prouve aucune collaboration
(JOURNAL 19). Ce croisement elargit la liste a SURVEILLER, rien de plus.

Usage :
    python outils/croiser_instagram_youtube.py
    python outils/croiser_instagram_youtube.py --budget 3000
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
CACHE = RACINE / "donnees" / "croisement_ig_yt.json"
API = "https://www.googleapis.com/youtube/v3/channels"


def lire_cle():
    if not SECRETS.exists():
        return None
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m and not m.group(1).startswith("colle") else None


def par_pseudo(pseudo, cle):
    """1 unite. Renvoie (infos, erreur). infos vaut None si pas de chaine."""
    url = API + "?" + urllib.parse.urlencode({
        "part": "snippet,statistics", "forHandle": pseudo.lstrip("@"), "key": cle})
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        corps = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(corps)["error"]["message"]
        except Exception:
            msg = corps[:150]
        return None, f"HTTP {e.code} — {msg}"
    except Exception as e:
        return None, f"{type(e).__name__}"
    items = d.get("items") or []
    if not items:
        return None, None
    it = items[0]
    s, st = it["snippet"], it.get("statistics", {})
    return {
        "channel_id": it["id"],
        "titre": s.get("title", ""),
        "pseudo_youtube": s.get("customUrl", ""),
        "pays": s.get("country", ""),
        "abonnes": st.get("subscriberCount", ""),
        "videos": st.get("videoCount", ""),
        "vues": st.get("viewCount", ""),
        "description": (s.get("description") or "").replace("\n", " ")[:400],
    }, None


def comptes_instagram():
    """Les pseudos Instagram connus, avec le lobby qui les suit."""
    f = sorted(RECHERCHE.glob("comptes_suivis_*.csv"))
    if not f:
        return {}
    out = {}
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            p = l.get("compte_suivi", "").strip()
            if not p:
                continue
            d = out.setdefault(p, {"nom": l.get("nom_affiche", ""), "vitrines": set()})
            d["vitrines"].add(l.get("entite_vitrine", ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=4000,
                    help="unites de quota maximum a depenser")
    args = ap.parse_args()

    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente de SECRETS.txt.", file=sys.stderr)
        return 1

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    comptes = comptes_instagram()
    print(f"{len(comptes)} pseudos Instagram a essayer", file=sys.stderr)

    depense, erreurs = 0, 0
    for i, (pseudo, info) in enumerate(sorted(comptes.items()), 1):
        if pseudo in cache:
            continue
        if depense >= args.budget:
            print(f"budget de {args.budget} unites atteint", file=sys.stderr)
            break
        infos, err = par_pseudo(pseudo, cle)
        depense += 1
        if err:
            erreurs += 1
            if "quota" in err.lower():
                print(f"QUOTA EPUISE apres {depense} unites : {err}", file=sys.stderr)
                break
            cache[pseudo] = {"erreur": err}
        else:
            cache[pseudo] = infos or {}
            if infos:
                ab = infos["abonnes"]
                print(f"  {i:>4d}/{len(comptes)}  @{pseudo:28s} -> "
                      f"{infos['titre'][:28]:30s} {ab:>10s} abonnes", file=sys.stderr)
        if i % 40 == 0:
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        time.sleep(0.05)

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    lignes = []
    for pseudo, infos in cache.items():
        if not infos or "erreur" in infos or not infos.get("channel_id"):
            continue
        d = comptes.get(pseudo, {"nom": "", "vitrines": set()})
        lignes.append({
            "pseudo_commun": pseudo,
            "nom_instagram": d["nom"],
            "suivi_par": " | ".join(sorted(filter(None, d["vitrines"]))),
            "channel_id": infos["channel_id"],
            "titre_youtube": infos["titre"],
            "pseudo_youtube": infos["pseudo_youtube"],
            "abonnes_youtube": infos["abonnes"],
            "videos": infos["videos"],
            "vues_totales": infos["vues"],
            "pays_declare": infos["pays"],
            "url": f"https://www.youtube.com/channel/{infos['channel_id']}",
            "rattachement": "HYPOTHESE — meme pseudo, personne non verifiee",
            "releve_le": date.today().isoformat(),
        })
    lignes.sort(key=lambda l: -(int(l["abonnes_youtube"])
                                if str(l["abonnes_youtube"]).isdigit() else 0))

    RECHERCHE.mkdir(exist_ok=True)
    aujourdhui = date.today().isoformat()
    csv_path = RECHERCHE / f"croisement_ig_yt_{aujourdhui}.csv"
    if lignes:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)

    essayes = len([1 for v in cache.values() if "erreur" not in (v or {})])
    md = [f"# Croisement Instagram → YouTube — {aujourdhui}", "",
          "Produit par `outils/croiser_instagram_youtube.py`.", "",
          "Pour chaque compte Instagram suivi par une vitrine de lobby, on demande",
          "a l'API YouTube s'il existe une chaine portant le meme pseudo.", "",
          f"- Pseudos essayes : **{essayes}** sur {len(comptes)}",
          f"- Chaines YouTube trouvees : **{len(lignes)}**",
          f"- Quota depense ce lancement : **{depense} unites**",
          f"- Erreurs : {erreurs}", "",
          "**Le rattachement est une HYPOTHESE.** Un meme pseudo sur deux",
          "plateformes ne prouve pas qu'il s'agit de la meme personne, et etre",
          "suivi par une vitrine ne prouve aucune collaboration.", "",
          "| Pseudo | Chaine YouTube | Abonnes | Suivi par | Videos |",
          "|---|---|---:|---|---:|"]
    for l in lignes[:120]:
        ab = int(l["abonnes_youtube"]) if str(l["abonnes_youtube"]).isdigit() else 0
        md += [f"| @{l['pseudo_commun']} | {l['titre_youtube'][:34]} | {ab:,} "
               f"| {l['suivi_par']} | {l['videos']} |".replace(",", " ")]
    if len(lignes) > 120:
        md += ["", f"({len(lignes) - 120} autres dans le CSV)"]
    md_path = RECHERCHE / f"croisement_ig_yt_{aujourdhui}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\n".join(md[:20]))
    print(f"\nEcrit : {md_path}")
    if lignes:
        print(f"Ecrit : {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
