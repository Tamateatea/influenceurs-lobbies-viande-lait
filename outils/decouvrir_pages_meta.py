"""
Trouve les pages Facebook des commanditaires, puis moissonne toutes leurs annonces.

POURQUOI CE DETOUR PAR LES PAGES

La recherche par mot-cle dans l'Ad Library ramene surtout du bruit : le premier
essai du 27/08 a remonte « Edarcyishop studio » et « Lignosus » autant que
« Bretons et Engages ». Un mot-cle ne distingue pas l'annonceur du sujet.

Interroger une **page precise** ne ment pas : ce sont ses annonces, payees par
elle. C'est le mode A de METHODOLOGIE section 12, et c'est la premiere fois du
projet qu'il est possible — sur YouTube il ne l'a jamais ete.

Ce script fait les deux temps :

  1. **Decouverte** — cherche chaque alias comme mot-cle, et retient les pages
     dont le NOM correspond a l'entite. Le bruit est ecarte par cette
     correspondance : une page qui parle de foie gras n'est pas la page du
     CIFOG.
  2. **Moisson** — interroge chaque page trouvee et prend toutes ses annonces.

POURQUOI LES MARQUES AUTANT QUE LES INTERPROFESSIONS

Mesure du 27/08 (JOURNAL 64) : en 2026, les descriptions YouTube portent 60
citations d'interprofession contre **1 635 citations de marques**. Le gisement
est du cote des marques, et il n'a jamais ete instruit.

Or une marque qui paie de la publicite Meta est un commanditaire au sens du
projet, exactement comme une interprofession. Ce script les traite ensemble.

CE QUE LA CORRESPONDANCE DE NOM PEUT RATER

Une page peut porter un nom de campagne sans rapport avec l'entite — « En Mode
Actif » ne contient pas « CNIEL ». Ces pages-la echappent a la decouverte
automatique et devront etre ajoutees a la main. C'est une limite assumee, pas
un oubli.

Usage :
    python outils/decouvrir_pages_meta.py --decouvrir
    python outils/decouvrir_pages_meta.py --moissonner
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
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
PAGES = RACINE / "donnees" / "pages_meta.json"
BASE = "https://graph.facebook.com/v21.0/ads_archive"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import table_alias
from appariement import aplatir
from ecriture_sure import ecrire_sur

CHAMPS = ",".join([
    "id", "ad_creation_time", "ad_delivery_start_time", "ad_delivery_stop_time",
    "ad_snapshot_url", "page_id", "page_name", "publisher_platforms",
    "ad_creative_bodies", "ad_creative_link_titles", "languages",
])


def sans_jeton(url):
    """Retire le jeton d'acces d'une URL avant de l'ecrire sur le disque.

    DEFAUT CORRIGE LE 29/08. `ad_snapshot_url` renvoye par l'API contient le
    jeton d'acces complet en clair. Ces URL ont ete ecrites dans sept CSV, tous
    versionnes et **pousses sur GitHub**.

    Le jeton avait expire depuis (une a deux heures de duree de vie), donc
    aucune consequence — mais c'est un identifiant publie, et ce n'est pas au
    hasard de l'expiration de nous proteger.

    Consequence secondaire, signalee par Vincent : les liens etaient **tous
    morts** dans son classeur, puisqu'ils portaient un jeton expire. Une URL
    d'apercu Meta n'est de toute facon consultable que par le detenteur du
    jeton — elle ne sert donc a rien dans un classeur destine a un humain.
    """
    import re as _re
    return _re.sub(r"access_token=[^&]*", "access_token=JETON_RETIRE", url or "")


def lire_jeton():
    m = re.search(r"META_AD_LIBRARY_TOKEN\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m and not m.group(1).startswith("colle") else None


def appel(params, jeton):
    url = BASE + "?" + urllib.parse.urlencode(dict(params, access_token=jeton))
    for essai in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            corps = e.read().decode("utf-8", "replace")
            try:
                msg = json.loads(corps)["error"]["message"]
            except Exception:
                msg = corps[:150]
            if ("limit" in msg.lower() or e.code == 429) and essai < 2:
                time.sleep(25 * (essai + 1))
                continue
            return None, f"HTTP {e.code} — {msg}"
        except Exception as e:
            if essai < 2:
                time.sleep(4)
                continue
            return None, type(e).__name__
    return None, "epuise"


def entites_a_chercher():
    """Alias et marques, chacun avec l'entite qu'il designe."""
    termes = table_alias.charger(seuil=5, avec_marques=True)
    vus, out = set(), []
    for _f, (lisible, entite) in termes.items():
        t = lisible.lstrip("@").replace("_", " ").replace(".", " ").strip()
        if len(t) >= 5 and t.lower() not in vus:
            vus.add(t.lower())
            out.append((t, entite))
    return out


def decouvrir(jeton, plafond_par_terme=200):
    """Cherche chaque terme, retient les pages dont le NOM correspond."""
    etat = json.loads(PAGES.read_text(encoding="utf-8")) if PAGES.exists() else {}
    requetes = entites_a_chercher()
    print(f"{len(requetes)} termes | {len(etat)} pages deja connues",
          file=sys.stderr)

    for i, (terme, entite) in enumerate(requetes, 1):
        if f"fait:{terme}" in etat:
            continue
        plat_terme = aplatir(terme)
        params = {"search_terms": terme, "ad_reached_countries": '["FR"]',
                  "ad_type": "ALL", "fields": "page_id,page_name", "limit": 100}
        pris, apres, nouvelles = 0, None, 0
        while pris < plafond_par_terme:
            if apres:
                params["after"] = apres
            d, err = appel(params, jeton)
            if err:
                print(f"  {terme[:30]:<32s} ERREUR {err[:60]}", file=sys.stderr)
                if "limit" in err.lower():
                    return etat, True          # quota : on s'arrete proprement
                break
            for a in d.get("data", []):
                pris += 1
                nom, pid = a.get("page_name", ""), a.get("page_id", "")
                if not pid or pid in etat:
                    continue
                # La page ne compte que si SON NOM porte le terme cherche.
                # C'est ce qui separe l'annonceur du simple sujet.
                if plat_terme and plat_terme in aplatir(nom):
                    etat[pid] = {"nom": nom, "entite": entite, "trouve_par": terme}
                    nouvelles += 1
            apres = d.get("paging", {}).get("cursors", {}).get("after")
            if not apres or not d.get("data"):
                break
            time.sleep(0.6)
        etat[f"fait:{terme}"] = True
        if nouvelles:
            print(f"  {terme[:30]:<32s} {nouvelles} page(s)", file=sys.stderr)
        if i % 10 == 0:
            ecrire_sur(PAGES, json.dumps(etat, ensure_ascii=False))
    ecrire_sur(PAGES, json.dumps(etat, ensure_ascii=False))
    return etat, False


def moissonner_pages(jeton, plafond=500):
    """Toutes les annonces de chaque page connue."""
    etat = json.loads(PAGES.read_text(encoding="utf-8")) if PAGES.exists() else {}
    pages = {k: v for k, v in etat.items() if not k.startswith("fait:")}
    if not pages:
        print("Aucune page connue — lancer d'abord --decouvrir.", file=sys.stderr)
        return []
    print(f"{len(pages)} pages a moissonner", file=sys.stderr)

    lignes = []
    for pid, info in pages.items():
        params = {"search_page_ids": f'["{pid}"]', "ad_reached_countries": '["FR"]',
                  "ad_type": "ALL", "fields": CHAMPS, "limit": 100}
        pris, apres = 0, None
        while pris < plafond:
            if apres:
                params["after"] = apres
            d, err = appel(params, jeton)
            if err:
                if "limit" in err.lower():
                    print("  quota atteint, arret propre", file=sys.stderr)
                    return lignes
                break
            for a in d.get("data", []):
                pris += 1
                lignes.append({
                    "entite": info["entite"], "page_nom": info["nom"],
                    "page_id": pid, "ad_id": a.get("id", ""),
                    "debut": a.get("ad_delivery_start_time", "")[:10],
                    "fin": (a.get("ad_delivery_stop_time") or "")[:10],
                    "plateformes": " | ".join(a.get("publisher_platforms", [])),
                    "texte": " ⏎ ".join(a.get("ad_creative_bodies", []) or [])[:1200],
                    "titres": " | ".join(a.get("ad_creative_link_titles", []) or [])[:300],
                    "url_apercu": sans_jeton(a.get("ad_snapshot_url", "")),
                })
            apres = d.get("paging", {}).get("cursors", {}).get("after")
            if not apres or not d.get("data"):
                break
            time.sleep(0.6)
        if pris:
            print(f"  {info['nom'][:34]:<36s} {pris:>4d}", file=sys.stderr)
    return lignes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--decouvrir", action="store_true")
    ap.add_argument("--moissonner", action="store_true")
    args = ap.parse_args()

    jeton = lire_jeton()
    if not jeton:
        print("META_AD_LIBRARY_TOKEN absent.", file=sys.stderr)
        return 1

    if args.decouvrir:
        etat, quota = decouvrir(jeton)
        pages = {k: v for k, v in etat.items() if not k.startswith("fait:")}
        print(f"\n{len(pages)} pages de commanditaires connues", file=sys.stderr)
        par_entite = defaultdict(list)
        for pid, v in pages.items():
            par_entite[v["entite"]].append(v["nom"])
        for e, noms in sorted(par_entite.items(), key=lambda x: -len(x[1]))[:25]:
            print(f"   {len(noms):>3d}  {e[:40]:<42s} {noms[0][:34]}",
                  file=sys.stderr)

    if args.moissonner:
        lignes = moissonner_pages(jeton)
        if not lignes:
            return 0
        h = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
        RECHERCHE.mkdir(parents=True, exist_ok=True)
        chemin = RECHERCHE / f"meta_pages_{h}.csv"
        with chemin.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)
        uniques = {l["ad_id"] for l in lignes}
        print(f"\n{len(lignes)} annonces, {len(uniques)} distinctes",
              file=sys.stderr)
        print(f"Ecrit : {chemin.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
