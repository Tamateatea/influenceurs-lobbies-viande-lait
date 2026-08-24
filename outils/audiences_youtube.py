"""
Releve l'audience des chaines YouTube via l'API officielle YouTube Data v3.

POURQUOI CETTE COUCHE EXISTE

Deux raisons, dans l'ordre d'importance.

1. **L'audience manquait.** Le critere de priorite du projet est « les
   createurs les plus vus du public » (METHODOLOGIE section 8), et pourtant
   seuls 3 % des 605 comptes du registre avaient un nombre d'abonnes connu —
   tous releves a la main. On priorisait sur une mesure qu'on n'avait pas.

2. **La lecture directe a une limite opaque.** Mesure du 24/08 : YouTube
   refuse les pages au-dela d'un budget quotidien non documente, et ralentir
   n'y change rien (JOURNAL 28). L'API, elle, a un quota **compte et connu
   d'avance**. C'est ce qui rend une surveillance continue planifiable.

Cette couche s'AJOUTE, elle ne remplace pas (arbitrage de Vincent, JOURNAL 23).
La case de declaration « communication commerciale » n'existe que dans la page
publique et continue d'etre lue la-bas.

COUT EN QUOTA — a surveiller, c'est la ressource rare

    channels.list        1 unite     pour 50 chaines a la fois
    search.list        100 unites    par appel !
    playlistItems.list   1 unite     pour 50 videos

Quota gratuit : 10 000 unites par jour (RAPPORTE, a verifier a l'usage).
Une recherche coute donc autant que 100 relevés d'audience. Le script met en
cache les identifiants de chaine resolus dans `donnees/chaines_youtube.json`
pour ne jamais payer deux fois la meme resolution.

La cle se lit dans SECRETS.txt :  YOUTUBE_API_KEY = ...

Usage :
    python outils/audiences_youtube.py              chaines deja connues
    python outils/audiences_youtube.py --resoudre   + resout les noms manquants
"""

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
CACHE = RACINE / "donnees" / "chaines_youtube.json"
API = "https://www.googleapis.com/youtube/v3/"

COUT = {"channels": 1, "search": 100, "playlistItems": 1}


class Quota:
    """Compte ce qu'on depense. Le quota est la ressource rare, pas le temps."""

    def __init__(self):
        self.depense = 0

    def payer(self, endpoint):
        self.depense += COUT.get(endpoint, 1)


def lire_cle():
    if not SECRETS.exists():
        return None
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m and not m.group(1).startswith("colle") else None


def appel(endpoint, params, cle, quota):
    params = dict(params, key=cle)
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            quota.payer(endpoint)
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        corps = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(corps)["error"]["message"]
        except Exception:
            msg = corps[:200]
        return None, f"HTTP {e.code} — {msg}"
    except Exception as e:
        return None, f"{type(e).__name__} : {e}"


def charger_cache():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def enregistrer_cache(d):
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def chaines_connues():
    """Identifiants de chaine deja presents dans nos relevés."""
    ids = {}
    for f in sorted(RECHERCHE.glob("surveillance_youtube_*.csv")):
        with f.open(encoding="utf-8") as fh:
            for l in csv.DictReader(fh):
                cid = l.get("channel_id", "")
                if cid:
                    ids.setdefault(cid, l.get("chaine_demandee", ""))
    return ids


def details(ids, cle, quota):
    """channels.list par paquets de 50 — 1 unite le paquet."""
    out = {}
    ids = list(ids)
    for i in range(0, len(ids), 50):
        lot = ids[i:i + 50]
        d, err = appel("channels", {"part": "snippet,statistics",
                                    "id": ",".join(lot), "maxResults": 50}, cle, quota)
        if err:
            print(f"  erreur sur un lot de {len(lot)} : {err}", file=sys.stderr)
            continue
        for it in d.get("items", []):
            s, st = it["snippet"], it.get("statistics", {})
            out[it["id"]] = {
                "titre": s.get("title", ""),
                "pseudo": s.get("customUrl", ""),
                "pays": s.get("country", ""),
                "creee_le": (s.get("publishedAt") or "")[:10],
                "abonnes": st.get("subscriberCount", ""),
                "abonnes_caches": st.get("hiddenSubscriberCount", False),
                "videos": st.get("videoCount", ""),
                "vues": st.get("viewCount", ""),
            }
    return out


def resoudre_par_pseudo(pseudo, cle, quota):
    """channels.list?forHandle — 1 UNITE au lieu de 100.

    Decouvert le 24/08 : quand on connait le @pseudo, l'API le resout
    directement pour 1 unite. Une recherche en coute 100. Toujours essayer
    par pseudo d'abord — cent fois moins cher, et sans ambiguite : un pseudo
    designe une seule chaine, alors qu'une recherche par nom ramene des
    homonymes et des chaines de fans.
    """
    d, err = appel("channels", {"part": "snippet,statistics",
                                "forHandle": pseudo.lstrip("@")}, cle, quota)
    if err or not d.get("items"):
        return None, err
    it = d["items"][0]
    return (it["id"], it["snippet"]["title"]), None


def resoudre(nom, cle, quota):
    """search.list — 100 unites. En dernier recours seulement.

    Ramene aussi des chaines de fans et des homonymes : le releve du 24/08 a
    ainsi attrape une fausse chaine « seb la frite » a 1 630 abonnes au lieu
    de la vraie a 5,85 M. L'audience a servi de detecteur d'erreur.
    """
    d, err = appel("search", {"part": "snippet", "q": nom, "type": "channel",
                              "maxResults": 5, "regionCode": "FR"}, cle, quota)
    if err:
        return [], err
    return [(it["snippet"]["channelId"], it["snippet"]["title"])
            for it in d.get("items", [])], None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resoudre", action="store_true",
                    help="resout les noms absents du cache (100 unites chacun)")
    ap.add_argument("--noms", nargs="*", default=[],
                    help="noms de chaines a resoudre (search, 100 unites)")
    ap.add_argument("--pseudos", nargs="*", default=[],
                    help="@pseudos a resoudre (1 unite chacun — a preferer)")
    ap.add_argument("--oublier", nargs="*", default=[],
                    help="identifiants de chaine a retirer du cache")
    args = ap.parse_args()

    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente de SECRETS.txt.", file=sys.stderr)
        return 1
    quota = Quota()
    cache = charger_cache()

    ids = dict(chaines_connues())
    for cid, nom in cache.get("resolus", {}).items():
        ids.setdefault(cid, nom)
    for cid in cache.get("ecartes", {}):
        ids.pop(cid, None)
    print(f"{len(ids)} chaines connues (relevés + cache)", file=sys.stderr)

    for cid in args.oublier:
        ids.pop(cid, None)
        cache.get("resolus", {}).pop(cid, None)
        cache.setdefault("ecartes", {})[cid] = "retire a la main"
        print(f"  {cid} retire du cache", file=sys.stderr)

    for pseudo in args.pseudos:
        r, err = resoudre_par_pseudo(pseudo, cle, quota)
        if not r:
            print(f"  @{pseudo} : introuvable {err or ''}", file=sys.stderr)
            continue
        cid, titre = r
        ids[cid] = pseudo
        cache.setdefault("resolus", {})[cid] = pseudo
        print(f"  @{pseudo} -> {cid} {titre}  (1 unite)", file=sys.stderr)

    if args.resoudre and args.noms:
        deja = {v.lower() for v in ids.values()}
        for nom in args.noms:
            if nom.lower() in deja:
                print(f"  {nom} : deja connu, 0 unite", file=sys.stderr)
                continue
            trouves, err = resoudre(nom, cle, quota)
            if err:
                print(f"  {nom} : {err}", file=sys.stderr)
                continue
            for cid, titre in trouves:
                ids[cid] = nom
                cache.setdefault("resolus", {})[cid] = nom
                print(f"  {nom} -> {cid} {titre}", file=sys.stderr)

    if not ids:
        print("Aucune chaine a interroger.", file=sys.stderr)
        return 1

    infos = details(ids, cle, quota)
    enregistrer_cache(cache)

    aujourdhui = date.today().isoformat()
    lignes = []
    for cid, d in infos.items():
        lignes.append({
            "plateforme": "youtube",
            "channel_id": cid,
            "pseudo": d["pseudo"],
            "titre": d["titre"],
            "personne_demandee": ids.get(cid, ""),
            "abonnes": d["abonnes"],
            "abonnes_caches": "oui" if d["abonnes_caches"] else "non",
            "videos": d["videos"],
            "vues_totales": d["vues"],
            "pays_declare": d["pays"],
            "chaine_creee_le": d["creee_le"],
            "url": f"https://www.youtube.com/channel/{cid}",
            "releve_le": aujourdhui,
        })
    lignes.sort(key=lambda l: -(int(l["abonnes"]) if str(l["abonnes"]).isdigit() else 0))

    RECHERCHE.mkdir(exist_ok=True)
    csv_path = RECHERCHE / f"audiences_youtube_{aujourdhui}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
        w.writeheader()
        w.writerows(lignes)

    manquantes = set(ids) - set(infos)
    md = [f"# Audiences YouTube — {aujourdhui}", "",
          "Produit par `outils/audiences_youtube.py`, via l'API officielle.", "",
          f"- Chaines interrogees : **{len(ids)}**",
          f"- Chaines trouvees : **{len(infos)}**"
          + (f" — **{len(manquantes)} introuvables**" if manquantes else ""),
          f"- Quota depense : **{quota.depense} unites** sur ~10 000 par jour",
          "", "| Chaine | Pseudo | Abonnes | Videos | Vues totales | Creee le |",
          "|---|---|---|---:|---:|---:|---|"]
    for l in lignes:
        ab = int(l["abonnes"]) if str(l["abonnes"]).isdigit() else 0
        md += [f"| {l['titre']} | {l['pseudo']} | {ab:,} | {l['videos']} "
               f"| {l['vues_totales']} | {l['chaine_creee_le']} |".replace(",", " ")]
    md += ["", "## A retenir", "",
           "L'audience est le critere de priorite du projet. Elle etait connue",
           "pour 3 % des comptes avant ce releve ; elle l'est desormais pour",
           "toutes les chaines YouTube surveillees.", "",
           "`consolider_comptes.py` reprend ce fichier automatiquement.", ""]
    md_path = RECHERCHE / f"audiences_youtube_{aujourdhui}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\n".join(md))
    print(f"\nEcrit : {csv_path}\nEcrit : {md_path}")
    print(f"Quota depense : {quota.depense} unites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
