"""
Cherche la chaine YouTube de chacun des createurs TikTok a partenariat declare.

POURQUOI C'EST LA MEILLEURE SEMENCE DISPONIBLE

Les 185 chaines surveillees viennent des abonnements Instagram des vitrines.
Or **etre suivi par un lobby ne prouve rien** (JOURNAL 19) : ce vivier est une
hypothese de ciblage.

Les 8 061 createurs francais de la Commercial Content Library sont d'une autre
nature : **TikTok declare qu'ils ont fait du partenariat remunere.** Ce sont
des createurs commerciaux averes. Comme semence d'une liste de surveillance,
c'est strictement meilleur.

`channels.list?forHandle` coute **1 unite** et repond « existe-t-il une chaine
YouTube portant ce pseudo ? ». Beaucoup de createurs emploient le meme pseudo
sur les deux plateformes.

CE QUE CE N'EST PAS

Un meme pseudo sur TikTok et YouTube ne prouve pas la meme personne. Le
rattachement est une **hypothese**, inscrite comme telle dans la sortie
(METHODOLOGIE section 8 : le rattachement compte → personne est un jugement
humain explicite, jamais une deduction par le nom).

Et un createur commercial sur TikTok n'a evidemment aucun lien etabli avec la
filiere viande/lait. Ce croisement elargit la population a SURVEILLER.

REPRISE : l'etat est enregistre en continu dans
`donnees/croisement_tt_yt.json`. Une interruption ne perd rien.

Usage :
    python outils/croiser_tiktok_youtube.py --budget 7000
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
from collections import defaultdict
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
ETAT = RACINE / "donnees" / "croisement_tt_yt.json"
API = "https://www.googleapis.com/youtube/v3/channels"

# Un pseudo YouTube valide. Les pseudos TikTok qui n'ont pas cette forme
# ne peuvent pas correspondre a une chaine : inutile de depenser une unite.
PSEUDO_VALIDE = re.compile(r"^[A-Za-z0-9._-]{3,30}$")


def lire_cle():
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def par_pseudo(pseudo, cle):
    url = API + "?" + urllib.parse.urlencode({
        "part": "snippet,statistics", "forHandle": pseudo.lstrip("@"), "key": cle})
    for essai in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                d = json.loads(r.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            corps = e.read().decode("utf-8", "replace")
            try:
                msg = json.loads(corps)["error"]["message"]
            except Exception:
                msg = corps[:120]
            if "quota" in msg.lower():
                return None, "QUOTA"
            if e.code >= 500 and essai < 2:
                time.sleep(2 * (essai + 1))
                continue
            return None, f"HTTP {e.code}"
        except Exception as e:
            if essai < 2:
                time.sleep(2)
                continue
            return None, type(e).__name__
    else:
        return None, "epuise"

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
    }, None


def createurs_tiktok():
    f = sorted(RECHERCHE.glob("tiktok_commercial_*.csv"))
    if not f:
        return {}
    out = defaultdict(lambda: {"contenus": 0, "labels": set()})
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            u = (l.get("createur") or "").strip()
            if u:
                out[u]["contenus"] += 1
                out[u]["labels"].add(l.get("label", ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=7000)
    args = ap.parse_args()

    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente.", file=sys.stderr)
        return 1

    ETAT.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(ETAT.read_text(encoding="utf-8")) if ETAT.exists() else {}
    createurs = createurs_tiktok()

    # les plus actifs d'abord : un createur avec 16 contenus commerciaux est
    # plus interessant qu'un createur avec un seul
    ordre = sorted(createurs.items(), key=lambda x: -x[1]["contenus"])
    print(f"{len(createurs)} createurs TikTok | {len(cache)} deja essayes",
          file=sys.stderr)

    depense, trouves, arret = 0, 0, None
    for i, (pseudo, info) in enumerate(ordre, 1):
        if pseudo in cache:
            continue
        if not PSEUDO_VALIDE.match(pseudo):
            cache[pseudo] = {"ignore": "pseudo non compatible YouTube"}
            continue
        if depense >= args.budget:
            arret = f"budget de {args.budget} unites atteint"
            break

        r, err = par_pseudo(pseudo, cle)
        depense += 1
        if err == "QUOTA":
            arret = "quota YouTube epuise"
            break
        if err:
            cache[pseudo] = {"erreur": err}
        else:
            cache[pseudo] = r or {}
            if r:
                trouves += 1
                ab = int(r["abonnes"]) if str(r["abonnes"]).isdigit() else 0
                if ab >= 100_000:
                    print(f"  {i:>5d} @{pseudo:26s} -> {r['titre'][:26]:28s} "
                          f"{ab:>10,d} abonnes".replace(",", " "), file=sys.stderr)
        if depense % 200 == 0:
            ETAT.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            print(f"  ... {depense} unites, {trouves} chaines trouvees",
                  file=sys.stderr)

    ETAT.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    lignes = []
    for pseudo, r in cache.items():
        if not r or "erreur" in r or "ignore" in r or not r.get("channel_id"):
            continue
        info = createurs.get(pseudo, {"contenus": 0, "labels": set()})
        lignes.append({
            "pseudo_commun": pseudo,
            "contenus_commerciaux_tiktok": info["contenus"],
            "labels_tiktok": " | ".join(sorted(filter(None, info["labels"]))),
            "channel_id": r["channel_id"],
            "titre_youtube": r["titre"],
            "pseudo_youtube": r["pseudo_youtube"],
            "abonnes_youtube": r["abonnes"],
            "videos": r["videos"],
            "pays_declare": r["pays"],
            "url": f"https://www.youtube.com/channel/{r['channel_id']}",
            "rattachement": "HYPOTHESE — meme pseudo, personne non verifiee",
            "releve_le": date.today().isoformat(),
        })
    lignes.sort(key=lambda l: -(int(l["abonnes_youtube"])
                                if str(l["abonnes_youtube"]).isdigit() else 0))

    aujourdhui = date.today().isoformat()
    if lignes:
        chemin = RECHERCHE / f"croisement_tt_yt_{aujourdhui}.csv"
        with chemin.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)

    gros = [l for l in lignes if str(l["abonnes_youtube"]).isdigit()
            and int(l["abonnes_youtube"]) >= 100_000]
    essayes = sum(1 for v in cache.values() if "ignore" not in (v or {}))
    md = [f"# Createurs TikTok retrouves sur YouTube — {aujourdhui}", "",
          "Produit par `outils/croiser_tiktok_youtube.py`.", "",
          "Les createurs de la Commercial Content Library sont des createurs",
          "**commerciaux averes** : TikTok declare leur partenariat remunere.",
          "C'est une meilleure semence que les abonnements des vitrines, qui ne",
          "prouvent rien.", "",
          f"- Createurs TikTok essayes : **{essayes}** sur {len(createurs)}",
          f"- **Chaines YouTube trouvees : {len(lignes)}**",
          f"- dont au moins 100 000 abonnes : **{len(gros)}**",
          f"- Quota depense ce lancement : **{depense} unites**",
          "", f"Arret : {arret}" if arret else "", "",
          "**Le rattachement est une HYPOTHESE** : un meme pseudo sur deux",
          "plateformes ne prouve pas la meme personne.", "",
          "| Pseudo | Chaine YouTube | Abonnes | Contenus TikTok |",
          "|---|---|---:|---:|"]
    for l in gros[:150]:
        ab = int(l["abonnes_youtube"])
        md += [f"| @{l['pseudo_commun']} | {l['titre_youtube'][:32]} | {ab:,} "
               f"| {l['contenus_commerciaux_tiktok']} |".replace(",", " ")]

    chemin_md = RECHERCHE / f"croisement_tt_yt_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:14]))
    print(f"\nEcrit : {chemin_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
