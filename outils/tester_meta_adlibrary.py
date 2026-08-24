"""
Teste l'API Meta Ad Library sur les entites de la filiere viande/lait.

LA QUESTION A TRANCHER (hypothese IG-02 de HYPOTHESES.md) :
l'API expose-t-elle les CONTENUS DE MARQUE — le post d'un createur etiquete
« partenariat remunere » — ou seulement les publicites achetees par
l'annonceur ? Si oui, Instagram devient interrogeable PAR COMMANDITAIRE
(mode A, METHODOLOGIE.md section 12) et les noms de createurs tombent sans
liste prealable. C'est le plus gros deblocage possible apres YouTube.

Le jeton se lit dans SECRETS.txt, jamais en dur, jamais en argument de ligne
de commande (il resterait dans l'historique du terminal).

Ecrit ses resultats dans recherche/, horodates.

Usage :  python outils/tester_meta_adlibrary.py
"""

import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
SORTIE = RACINE / "recherche"
BASE = "https://graph.facebook.com/v21.0/ads_archive"

# Termes de recherche, tires de la filiere. Volontairement larges : on mesure
# d'abord ce que l'API rend, on affine ensuite.
REQUETES = [
    ("CNIEL", "produits laitiers"),
    ("CNIEL", "cniel"),
    ("INTERBEV", "interbev"),
    ("INTERBEV", "aimez la viande"),
    ("INAPORC", "le porc francais"),
    ("ANVOL", "volaille francaise"),
]

CHAMPS = [
    "id", "ad_creation_time", "ad_delivery_start_time", "ad_snapshot_url",
    "page_id", "page_name", "publisher_platforms", "ad_creative_bodies",
    "ad_creative_link_titles", "ad_creative_link_captions",
    "target_locations", "languages",
]


def lire_jeton():
    if not SECRETS.exists():
        print(f"{SECRETS.name} introuvable.", file=sys.stderr)
        return None
    for ligne in SECRETS.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\s*META_AD_LIBRARY_TOKEN\s*=\s*(\S+)", ligne)
        if m and m.group(1) not in ("colle_ici", ""):
            return m.group(1)
    print("Aucun jeton trouve dans SECRETS.txt.", file=sys.stderr)
    print("Attendu une ligne :  META_AD_LIBRARY_TOKEN = <le jeton>", file=sys.stderr)
    return None


def appel(jeton, terme, ad_type, pays="FR", limite=50):
    params = {
        "access_token": jeton,
        "search_terms": terme,
        "ad_reached_countries": json.dumps([pays]),
        "ad_type": ad_type,
        "fields": ",".join(CHAMPS),
        "limit": str(limite),
    }
    url = BASE + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        corps = e.read().decode("utf-8", "replace")
        try:
            err = json.loads(corps).get("error", {})
            return None, f"HTTP {e.code} — {err.get('message', corps[:200])}"
        except Exception:
            return None, f"HTTP {e.code} — {corps[:200]}"
    except Exception as e:
        return None, f"{type(e).__name__} : {e}"


def main():
    jeton = lire_jeton()
    if not jeton:
        return 1
    SORTIE.mkdir(exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    date_lisible = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lignes, journal = [], []

    for entite, terme in REQUETES:
        for ad_type in ("ALL", "POLITICAL_AND_ISSUE_ADS"):
            donnees, erreur = appel(jeton, terme, ad_type)
            if erreur:
                journal.append((entite, terme, ad_type, "ERREUR", erreur))
                print(f"  {entite:10s} {terme:22s} {ad_type:24s} ERREUR : {erreur}",
                      file=sys.stderr)
                continue
            annonces = donnees.get("data", [])
            journal.append((entite, terme, ad_type, f"{len(annonces)} annonce(s)", ""))
            print(f"  {entite:10s} {terme:22s} {ad_type:24s} {len(annonces)} annonce(s)",
                  file=sys.stderr)
            for a in annonces:
                lignes.append({
                    "entite_recherchee": entite,
                    "terme": terme,
                    "ad_type": ad_type,
                    "ad_id": a.get("id", ""),
                    "page_id": a.get("page_id", ""),
                    "page_name": a.get("page_name", ""),
                    "plateformes": " | ".join(a.get("publisher_platforms", []) or []),
                    "debut_diffusion": a.get("ad_delivery_start_time", ""),
                    "texte": " ⏎ ".join(a.get("ad_creative_bodies", []) or [])[:800],
                    "titres": " | ".join(a.get("ad_creative_link_titles", []) or [])[:300],
                    "url_apercu": a.get("ad_snapshot_url", ""),
                    "releve_le": date_lisible,
                })

    csv_path = SORTIE / f"meta_adlibrary_{horodatage}.csv"
    if lignes:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)

    md = [f"# Test API Meta Ad Library — {date_lisible}", "",
          "Produit par `outils/tester_meta_adlibrary.py`.",
          "Hypothese testee : **IG-02** — l'API expose-t-elle les contenus de marque ?",
          "", "## Ce que chaque requete a rendu", "",
          "| Entite | Terme | ad_type | Resultat | Erreur |", "|---|---|---|---|---|"]
    for e, t, at, res, err in journal:
        md += [f"| {e} | {t} | `{at}` | {res} | {err} |"]

    if lignes:
        pages = {}
        for l in lignes:
            pages.setdefault((l["page_id"], l["page_name"]), 0)
            pages[(l["page_id"], l["page_name"])] += 1
        md += ["", f"## Pages annonceuses trouvees ({len(pages)})", "",
               "| Page | page_id | Annonces |", "|---|---|---|"]
        for (pid, nom), n in sorted(pages.items(), key=lambda x: -x[1]):
            md += [f"| {nom} | {pid} | {n} |"]
        md += ["", f"Detail complet : `{csv_path.name}` ({len(lignes)} annonces).", ""]
        md += ["## A regarder a la main", "",
               "Les colonnes `page_name` et `texte` disent-elles qu'il s'agit d'une",
               "publicite achetee par le lobby, ou d'un post de createur etiquete",
               "partenariat ? C'est cette lecture qui tranche IG-02, pas le nombre",
               "de resultats.", ""]
    else:
        md += ["", "## Aucune annonce retournee", "",
               "Ce n'est pas forcement un echec : lire la colonne Erreur ci-dessus.",
               "Un refus d'authentification et un resultat vide ne disent pas la",
               "meme chose.", ""]

    md_path = SORTIE / f"meta_adlibrary_{horodatage}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nEcrit : {md_path}")
    if lignes:
        print(f"Ecrit : {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
