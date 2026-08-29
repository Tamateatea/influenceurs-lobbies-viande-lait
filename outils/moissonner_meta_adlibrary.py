"""
Moissonne la Meta Ad Library pour la filiere viande/lait — Instagram et Facebook.

CE QUE CA DEBLOQUE

Instagram etait bloque depuis le debut du projet. Le 27/08 au soir, Vincent a
obtenu un jeton UTILISATEUR avec la permission `ads_read`, en ajoutant un use
case Marketing API a son application. L'API repond enfin.

Ce que dit le premier test (`tester_meta_adlibrary.py`, 27/08 21h31) :

    ad_type=ALL                       -> 50 annonces par requete, plafond atteint
    ad_type=POLITICAL_AND_ISSUE_ADS   -> refuse : « Political ad searches for
                                         countries in the European Union aren't
                                         available »

Autrement dit **c'est `ALL` qu'il faut**, et le refus sur les publicites
politiques n'a aucune importance ici : au titre du DSA, l'UE expose TOUTES les
publicites, commerciales comprises. C'est la confirmation pratique de IG-01,
qui n'etait etablie que par la documentation.

DEUX MODES, ET POURQUOI LE SECOND EST MEILLEUR

`--par-termes` cherche des mots-cles. Ca marche, mais ca ramene surtout du
bruit : le premier essai a remonte « Edarcyishop studio » et « Lignosus »
autant que « Bretons et Engages ». Un mot-cle ne distingue pas l'annonceur du
sujet.

`--par-pages` interroge des identifiants de page precis. C'est le **mode A** de
METHODOLOGIE section 12 — partir du commanditaire, pas du contenu. Aucun bruit
possible : ce sont les annonces de cette page-la.

Les identifiants de page se decouvrent avec `--par-termes`, puis se rangent
dans la feuille `Alias` du classeur. Les deux modes s'alimentent.

CE QUE CETTE SOURCE ETABLIT

Une annonce prouve que **l'annonceur a paye Meta pour diffuser**. Elle ne dit
pas qu'un createur a ete remunere. Mais si l'annonce montre un createur, ou si
son texte le nomme, alors le commanditaire publie lui-meme le lien — meme
statut de preuve que les chaines YouTube des lobbies.

Usage :
    python outils/moissonner_meta_adlibrary.py --par-termes
    python outils/moissonner_meta_adlibrary.py --par-pages 123456,789012
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
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
BASE = "https://graph.facebook.com/v21.0/ads_archive"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import table_alias

CHAMPS = ",".join([
    "id", "ad_creation_time", "ad_delivery_start_time", "ad_delivery_stop_time",
    "ad_snapshot_url", "page_id", "page_name", "publisher_platforms",
    "ad_creative_bodies", "ad_creative_link_titles", "ad_creative_link_captions",
    "languages", "target_locations",
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
    if not SECRETS.exists():
        return None
    m = re.search(r"META_AD_LIBRARY_TOKEN\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return None
    j = m.group(1)
    return None if j.startswith("colle") else j


def appel(params, jeton, essais=3):
    """Rend (donnees, erreur). Une erreur n'est jamais un resultat vide."""
    url = BASE + "?" + urllib.parse.urlencode(dict(params, access_token=jeton))
    for essai in range(essais):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            corps = e.read().decode("utf-8", "replace")
            try:
                msg = json.loads(corps)["error"]["message"]
            except Exception:
                msg = corps[:160]
            # 4 et 17 : limitation de debit. ~200 appels/heure d'apres les
            # sources secondaires — a confirmer, c'est IG-09.
            if ("limit" in msg.lower() or e.code == 429) and essai < essais - 1:
                time.sleep(30 * (essai + 1))
                continue
            return None, f"HTTP {e.code} — {msg}"
        except Exception as e:
            if essai < essais - 1:
                time.sleep(5)
                continue
            return None, type(e).__name__
    return None, "epuise"


def moissonner(params_base, jeton, plafond, etiquette, lignes, erreurs):
    """Pagine une requete jusqu'au plafond. Ajoute a `lignes` sur place."""
    params = dict(params_base, fields=CHAMPS, limit=100,
                  ad_reached_countries='["FR"]', ad_type="ALL")
    apres, pris = None, 0
    while pris < plafond:
        if apres:
            params["after"] = apres
        d, err = appel(params, jeton)
        if err:
            erreurs.append((etiquette, err))
            return pris
        for a in d.get("data", []):
            lignes.append({
                "recherche": etiquette,
                "ad_id": a.get("id", ""),
                "page_id": a.get("page_id", ""),
                "page_name": a.get("page_name", ""),
                "debut": a.get("ad_delivery_start_time", "")[:10],
                "fin": (a.get("ad_delivery_stop_time") or "")[:10],
                "plateformes": " | ".join(a.get("publisher_platforms", [])),
                "texte": " ⏎ ".join(a.get("ad_creative_bodies", []) or [])[:900],
                "titres": " | ".join(a.get("ad_creative_link_titles", []) or [])[:300],
                "url_apercu": sans_jeton(a.get("ad_snapshot_url", "")),
                "releve_le": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            })
            pris += 1
        apres = d.get("paging", {}).get("cursors", {}).get("after")
        if not apres or not d.get("data"):
            break
        time.sleep(1)
    return pris


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--par-termes", action="store_true",
                    help="chercher les alias de la filiere comme mots-cles")
    ap.add_argument("--par-pages", default="",
                    help="identifiants de pages, separes par des virgules")
    ap.add_argument("--plafond", type=int, default=400,
                    help="annonces maximum par requete")
    args = ap.parse_args()

    jeton = lire_jeton()
    if not jeton:
        print("META_AD_LIBRARY_TOKEN absent de SECRETS.txt.", file=sys.stderr)
        return 1
    if not args.par_termes and not args.par_pages:
        print("Choisir --par-termes ou --par-pages.", file=sys.stderr)
        return 1

    lignes, erreurs = [], []

    if args.par_pages:
        pages = [p.strip() for p in args.par_pages.split(",") if p.strip()]
        print(f"{len(pages)} pages a interroger", file=sys.stderr)
        for p in pages:
            n = moissonner({"search_page_ids": f'["{p}"]'}, jeton,
                           args.plafond, f"page:{p}", lignes, erreurs)
            print(f"  page {p:<20s} {n:>4d} annonces", file=sys.stderr)

    if args.par_termes:
        # Les alias d'interprofession seulement : les noms de marque comme
        # « Marie » ou « President » noieraient tout, comme sur YouTube.
        termes = table_alias.charger(seuil=8, avec_marques=False)
        vus, requetes = set(), []
        for _forme, (lisible, entite) in termes.items():
            t = lisible.lstrip("@").replace("_", " ").replace(".", " ").strip()
            if len(t) >= 6 and t.lower() not in vus:
                vus.add(t.lower())
                requetes.append((t, entite))
        print(f"{len(requetes)} termes a chercher", file=sys.stderr)
        for t, entite in requetes:
            n = moissonner({"search_terms": t}, jeton, args.plafond,
                           f"{entite} — {t}", lignes, erreurs)
            print(f"  {t[:34]:<36s} {n:>4d} annonces", file=sys.stderr)

    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    RECHERCHE.mkdir(parents=True, exist_ok=True)
    if lignes:
        chemin = RECHERCHE / f"meta_annonces_{horodatage}.csv"
        with chemin.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)

    uniques = {l["ad_id"]: l for l in lignes}
    pages = Counter(l["page_name"] for l in uniques.values())
    md = [f"# Moisson Meta Ad Library — {horodatage} UTC", "",
          "Produit par `outils/moissonner_meta_adlibrary.py`.", "",
          f"- Annonces relevees : **{len(lignes)}**",
          f"- Annonces distinctes : **{len(uniques)}**",
          f"- Pages annonceuses distinctes : **{len(pages)}**",
          f"- Requetes en erreur : {len(erreurs)}", "",
          "**Une annonce prouve que l'annonceur a paye Meta pour diffuser.**",
          "Elle ne prouve pas qu'un createur a ete remunere. Mais si elle montre",
          "ou nomme un createur, c'est le commanditaire qui publie le lien.", "",
          "## Pages annonceuses les plus frequentes", "",
          "| Page | Annonces |", "|---|---:|"]
    for p, n in pages.most_common(50):
        md += [f"| {p[:60]} | {n} |"]
    if erreurs:
        md += ["", "## Requetes en erreur", "", "| Requete | Erreur |", "|---|---|"]
        for e, m in erreurs[:20]:
            md += [f"| {e[:40]} | {m[:90]} |"]

    chemin_md = RECHERCHE / f"meta_annonces_{horodatage}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:10]))
    print(f"\nEcrit : {chemin_md.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
