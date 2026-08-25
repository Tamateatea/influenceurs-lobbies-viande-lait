"""
Decouvre les annonceurs que la table d'alias ne connait pas encore.

LE RENVERSEMENT

Toute la detection actuelle cherche des alias CONNUS. Elle ne peut donc, par
construction, rien trouver de nouveau : si l'industrie cree une marque demain,
l'outil sera aveugle jusqu'a ce qu'un humain l'ajoute a la main.

Orientation posee par Vincent le 25/08 (METHODOLOGIE 14bis.1) : « l'industrie
va toujours creer de nouvelles marques, de nouveaux alias ».

Ce script fait l'inverse du reste du projet. Il cherche la **forme** du
remerciement commercial — « merci a X », « en partenariat avec X », « avec le
soutien de X » — et recolte le X, **quel qu'il soit**. Les X deja connus sont
ecartes ; les autres deviennent des candidats a examiner.

Le mecanisme est stable meme quand les chaines changent : un createur remercie
toujours son financeur. C'est la forme qu'on surveille, pas le vocabulaire de
l'industrie.

CE QUE CE N'EST PAS

Un annonceur decouvert ici n'est pas de la filiere viande/lait. La plupart
seront des marques de telephones, de VPN ou de jeux. **Le tri appartient a un
humain** : le script rend une liste ordonnee par frequence, pas un verdict.

Aucun jugement automatique n'est porte sur le secteur d'un annonceur : ce
serait exactement le genre d'inference dont ce projet se mefie.

Usage :
    python outils/decouvrir_alias.py
    python outils/decouvrir_alias.py --budget 2500 --max-videos 400
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
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"
ETAT = RACINE / "donnees" / "decouverte_alias.json"
API = "https://www.googleapis.com/youtube/v3/"

# La FORME du remerciement commercial. Le groupe capture ce qui suit.
# On s'arrete a la ponctuation, au retour a la ligne ou a un mot de liaison :
# « merci a air up : mon code... » doit rendre « air up », pas la phrase.
FORMES = [
    r"merci\s+(?:a|aux|à)\s+([A-Za-zÀ-ÿ0-9][\w'’.\- &]{2,38})",
    r"remercie(?:r|nt|ons)?\s+(?:a\s+)?([A-Za-zÀ-ÿ0-9][\w'’.\- &]{2,38})",
    r"thanks?\s+to\s+([A-Za-zÀ-ÿ0-9][\w'’.\- &]{2,38})",
    r"en\s+partenariat\s+avec\s+([A-Za-zÀ-ÿ0-9][\w'’.\- &]{2,38})",
    r"avec\s+le\s+soutien\s+de\s+([A-Za-zÀ-ÿ0-9][\w'’.\- &]{2,38})",
    r"sponsoris[ée]e?\s+par\s+([A-Za-zÀ-ÿ0-9][\w'’.\- &]{2,38})",
    r"(?:presente|proposee?)\s+par\s+([A-Za-zÀ-ÿ0-9][\w'’.\- &]{2,38})",
    r"collaboration\s+avec\s+([A-Za-zÀ-ÿ0-9][\w'’.\- &]{2,38})",
]

# Ce qui suit un remerciement sans etre un annonceur.
BRUIT = {
    "vous", "toi", "tous", "toutes", "eux", "elle", "lui", "moi", "nous",
    "mon", "ma", "mes", "ce", "cette", "ces", "la", "le", "les", "des", "du",
    "toute", "tout", "chacun", "abonnes", "abonnes pour", "vos", "votre",
    "mate", "mon pote", "mes potes", "ma famille", "mon equipe", "toute",
    "l equipe", "lequipe", "team", "toi qui", "vous tous", "vous davoir",
    "vous d avoir", "davoir", "d avoir", "tout le monde", "everyone", "all",
    "you", "watching", "my", "the", "for", "toi davoir", "ceux",
    # une URL capturee par le motif n'est pas un annonceur
    "https", "http", "www", "bit", "youtu", "equipes", "artistes",
}


def aplatir(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def nettoyer(capture):
    """Reduit une capture a un nom d'annonceur plausible."""
    c = capture.strip()
    # on coupe aux liaisons qui commencent une subordonnee
    c = re.split(r"\s+(?:pour|de\s+m|d[ae]\s+nous|qui|que|dans|sur|et\s+a|"
                 r"ainsi\s+que|davoir|d’avoir|d'avoir)\b", c, maxsplit=1)[0]
    c = c.strip(" .,:;!?-–—'’\"()")
    # au plus quatre mots : « air up », « Fitness Park », pas une phrase
    mots = c.split()
    if len(mots) > 4:
        c = " ".join(mots[:4])
    return c.strip()


def lire_cle():
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def appel(endpoint, params, cle):
    url = API + endpoint + "?" + urllib.parse.urlencode(dict(params, key=cle))
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        corps = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(corps)["error"]["message"]
        except Exception:
            msg = corps[:150]
        return None, ("QUOTA:" + msg if "quota" in msg.lower()
                      else f"HTTP {e.code} — {msg}")
    except Exception as e:
        return None, type(e).__name__


def alias_connus():
    """Tout ce que la table d'alias connait deja, sous forme aplatie."""
    import openpyxl
    wb = openpyxl.load_workbook(CARTO / "cartographie_filiere.xlsx",
                                read_only=True, data_only=True)
    connus = set()
    for feuille, colonnes in [("Alias", (0, 2)), ("Interprofessions", (0, 1, 3)),
                              ("Marques", (0, 1)), ("Agences", (0,))]:
        for l in wb[feuille].iter_rows(min_row=2, values_only=True):
            for i in colonnes:
                if i < len(l) and l[i]:
                    a = aplatir(l[i])
                    if len(a) >= 4:
                        connus.add(a)
                        # « @lesproduitslaitiers » et « Produits Laitiers »
                        # doivent se reconnaitre : on ajoute la forme sans
                        # article. Sans cela le script a redecouvert le CNIEL
                        # comme un annonceur inconnu — ce qui etait a la fois
                        # un bug et une validation du mecanisme (JOURNAL 41).
                        for art in ("les", "le", "la", "des", "du", "de", "l"):
                            if a.startswith(art) and len(a) - len(art) >= 4:
                                connus.add(a[len(art):])
    wb.close()
    return connus


def chaines():
    f = sorted(RECHERCHE.glob("comptes_consolides_*.csv"))
    if not f:
        return []
    out = {}
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            if l["plateforme"] == "youtube" and l["identifiant"].startswith("UC"):
                ab = int(l["audience"]) if str(l["audience"]).isdigit() else 0
                out[l["identifiant"]] = (ab, l.get("nom_affiche", ""))
    return [(c, n, a) for c, (a, n) in sorted(out.items(), key=lambda x: -x[1][0])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=2500)
    ap.add_argument("--max-videos", type=int, default=400)
    args = ap.parse_args()

    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente.", file=sys.stderr)
        return 1

    ETAT.parent.mkdir(parents=True, exist_ok=True)
    etat = (json.loads(ETAT.read_text(encoding="utf-8")) if ETAT.exists()
            else {"faites": {}, "captures": []})
    connus = alias_connus()
    liste = chaines()
    print(f"{len(connus)} formes deja connues | {len(liste)} chaines | "
          f"{len(etat['faites'])} deja faites", file=sys.stderr)

    depense, videos_vues, arret = 0, 0, None
    for i, (cid, nom, ab) in enumerate(liste, 1):
        if cid in etat["faites"]:
            videos_vues += etat["faites"][cid]
            continue
        if depense >= args.budget:
            arret = f"budget de {args.budget} unites atteint"
            break

        d, err = appel("channels", {"part": "contentDetails", "id": cid}, cle)
        depense += 1
        if err or not d.get("items"):
            if err and err.startswith("QUOTA"):
                arret = err
                break
            etat["faites"][cid] = 0
            continue
        up = d["items"][0]["contentDetails"]["relatedPlaylists"].get("uploads")
        if not up:
            etat["faites"][cid] = 0
            continue

        page, n = None, 0
        while n < args.max_videos:
            p = {"part": "snippet", "playlistId": up, "maxResults": 50}
            if page:
                p["pageToken"] = page
            d, err = appel("playlistItems", p, cle)
            depense += 1
            if err:
                if err.startswith("QUOTA"):
                    arret = err
                break
            for it in d.get("items", []):
                s = it["snippet"]
                n += 1
                texte = (s.get("title", "") or "") + "\n" + (s.get("description", "") or "")
                for forme in FORMES:
                    for m in re.finditer(forme, texte, re.I):
                        capture = nettoyer(m.group(1))
                        plat = aplatir(capture)
                        if len(plat) < 3 or plat in BRUIT:
                            continue
                        if aplatir(capture) in {aplatir(b) for b in BRUIT}:
                            continue
                        etat["captures"].append({
                            "annonceur": capture,
                            "connu": plat in connus,
                            "chaine": nom,
                            "abonnes": ab,
                            "video_id": s.get("resourceId", {}).get("videoId", ""),
                            "publiee": (s.get("publishedAt") or "")[:10],
                        })
            page = d.get("nextPageToken")
            if not page or arret:
                break

        etat["faites"][cid] = n
        videos_vues += n
        print(f"  {i:>3d}/{len(liste)} {nom[:26]:28s} {n:>4d} videos | "
              f"quota {depense:>5d} | {len(etat['captures'])} captures",
              file=sys.stderr)
        ETAT.write_text(json.dumps(etat, ensure_ascii=False), encoding="utf-8")
        if arret:
            break

    ETAT.write_text(json.dumps(etat, ensure_ascii=False), encoding="utf-8")

    # --- agregation ---
    par_nom = defaultdict(lambda: {"n": 0, "chaines": set(), "connu": False,
                                   "exemple": "", "abonnes": 0})
    for c in etat["captures"]:
        plat = aplatir(c["annonceur"])
        d = par_nom[plat]
        d["n"] += 1
        d["chaines"].add(c["chaine"])
        # « connu » est RECALCULE ici, pas repris du cache : la table d'alias
        # evolue, et un candidat d'hier peut etre un alias connu aujourd'hui.
        # Fige au moment de la capture, il aurait fallu tout re-moissonner.
        d["connu"] = plat in connus or any(
            plat.startswith(k) and len(k) >= 8 for k in connus)
        d["abonnes"] = max(d["abonnes"], c["abonnes"])
        if not d["exemple"]:
            d["exemple"] = c["annonceur"]
            d["video"] = c["video_id"]

    inconnus = [(k, v) for k, v in par_nom.items() if not v["connu"] and v["n"] >= 2]
    inconnus.sort(key=lambda x: (-len(x[1]["chaines"]), -x[1]["n"]))

    aujourdhui = date.today().isoformat()
    chemin = RECHERCHE / f"alias_candidats_{aujourdhui}.csv"
    with chemin.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["annonceur", "occurrences", "chaines_distinctes",
                    "plus_grosse_audience", "exemple_video", "deja_connu"])
        for k, v in inconnus:
            w.writerow([v["exemple"], v["n"], len(v["chaines"]), v["abonnes"],
                        f"https://www.youtube.com/watch?v={v.get('video', '')}", "non"])

    md = [f"# Annonceurs decouverts — {aujourdhui}", "",
          "Produit par `outils/decouvrir_alias.py`.", "",
          "Ce script ne cherche pas des alias connus : il cherche la **forme**",
          "du remerciement commercial et recolte ce qui suit, quel qu'il soit.",
          "C'est ce qui rend la detection robuste aux marques nouvelles.", "",
          f"- Chaines parcourues : **{len(etat['faites'])}**",
          f"- Videos examinees : **{videos_vues:,}**".replace(",", " "),
          f"- Quota depense : **{depense} unites**",
          f"- Mentions capturees : **{len(etat['captures'])}**",
          f"- **Annonceurs inconnus de la table d'alias : {len(inconnus)}**",
          "", f"Arret : {arret}" if arret else "", "",
          "**A trier par un humain.** La plupart seront hors filiere — VPN,",
          "telephones, jeux. Aucun jugement automatique n'est porte sur le",
          "secteur d'un annonceur.", "",
          "| Annonceur | Chaines | Mentions | Plus grosse audience | Exemple |",
          "|---|---:|---:|---:|---|"]
    for k, v in inconnus[:120]:
        md += [f"| **{v['exemple']}** | {len(v['chaines'])} | {v['n']} "
               f"| {v['abonnes']:,} "
               f"| https://www.youtube.com/watch?v={v.get('video', '')} |".replace(",", " ")]

    chemin_md = RECHERCHE / f"alias_candidats_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:14]))
    print(f"\nEcrit : {chemin_md}\nEcrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
