"""
Interroge la Commercial Content Library de TikTok.

POURQUOI C'EST LA SOURCE LA PLUS PROMETTEUSE DU PROJET

Toutes les autres sources demandent de deviner QUI surveiller, puis de chercher
un annonceur dans le contenu. Celle-ci rend directement, pour l'Union
europeenne, des objets qui contiennent DEJA :

    creator.username   le createur
    brand_names        la ou les marques qui le remunerent
    label              le label de partenariat
    create_date        la date

C'est exactement le modele de donnees du registre, deja constitue et declare
par la plateforme elle-meme. Pas d'inference, pas de table d'alias a appliquer
sur du texte libre, pas de faux positif de type « blague sur un sponsor ».

Perimetre : contenus dont l'auteur est dans l'EEE, depuis le 1er octobre 2022.
Le Royaume-Uni et la Suisse sont exclus. La France est couverte.

ACCES : demande une candidature approuvee (~2 jours ouvres, gratuit), qui
donne une cle client et un secret. **Contrairement au programme chercheurs de
TikTok et a la Meta Content Library, la Commercial Content API n'exige PAS
d'affiliation universitaire** : elle est ouverte au public, aux journalistes
et aux associations. C'est ce qui la rend accessible a ce projet.

Les identifiants se lisent dans SECRETS.txt :

    TIKTOK_CLIENT_KEY = ...
    TIKTOK_CLIENT_SECRET = ...

Usage :  python outils/tester_tiktok_commercial.py
"""

import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
SORTIE = RACINE / "recherche"

JETON_URL = "https://open.tiktokapis.com/v2/oauth/token/"
BASE = "https://open.tiktokapis.com/v2/research/adlib/"

# Noms de champs verifies contre l'API le 25/08/2026. Attention : c'est
# « creator » et non « creator.username » — l'API refuse la notation pointee
# et renvoie un objet imbrique {"username": ...}.
CHAMPS = "id,create_date,brand_names,creator,label,videos"

DEBUT = "20221001"          # borne minimale imposee par TikTok
# La borne haute doit etre STRICTEMENT anterieure a aujourd'hui : l'API refuse
# la date du jour (« Please provide a value before today's date »). Verifie le
# 25/08/2026.
FIN = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")


def lire_secret(nom):
    if not SECRETS.exists():
        return None
    for ligne in SECRETS.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(rf"\s*{nom}\s*=\s*(\S+)", ligne)
        if m and not m.group(1).startswith("colle"):
            return m.group(1)
    return None


def obtenir_jeton(cle, secret):
    """Jeton d'application OAuth2, valable ~2 h."""
    corps = urllib.parse.urlencode({
        "client_key": cle,
        "client_secret": secret,
        "grant_type": "client_credentials",
    }).encode()
    req = urllib.request.Request(
        JETON_URL, data=corps,
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
        return d.get("access_token"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code} — {e.read()[:300].decode('utf-8', 'replace')}"
    except Exception as e:
        return None, f"{type(e).__name__} : {e}"


def appel(jeton, chemin, corps, champs=None):
    url = BASE + chemin
    if champs:
        url += "?fields=" + urllib.parse.quote(champs, safe=".,")
    req = urllib.request.Request(
        url, data=json.dumps(corps).encode(),
        headers={"Authorization": f"Bearer {jeton}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code} — {e.read()[:400].decode('utf-8', 'replace')}"
    except Exception as e:
        return None, f"{type(e).__name__} : {e}"


def main():
    cle = lire_secret("TIKTOK_CLIENT_KEY")
    secret = lire_secret("TIKTOK_CLIENT_SECRET")
    if not cle or not secret:
        print("Identifiants TikTok absents de SECRETS.txt.", file=sys.stderr)
        print("Attendu :", file=sys.stderr)
        print("    TIKTOK_CLIENT_KEY = ...", file=sys.stderr)
        print("    TIKTOK_CLIENT_SECRET = ...", file=sys.stderr)
        print("Candidature : developers.tiktok.com/application/commercial-content-api",
              file=sys.stderr)
        return 1

    jeton, err = obtenir_jeton(cle, secret)
    if not jeton:
        print(f"Impossible d'obtenir un jeton : {err}", file=sys.stderr)
        return 1
    print("jeton obtenu", file=sys.stderr)

    SORTIE.mkdir(exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    date_lisible = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lignes, journal = [], []
    curseur, page = None, 0

    # Tout le contenu commercial francais de la periode. Le filtrage sur la
    # filiere viande/lait se fait chez nous, sur brand_names : c'est plus sur
    # que d'esperer que TikTok comprenne « Cniel ».
    while page < 400:
        page += 1
        corps = {
            "filters": {
                "content_published_date_range": {"min": DEBUT, "max": FIN},
                "creator_country_code": "FR",
            },
            "max_count": 50,
        }
        if curseur:
            corps["search_id"] = curseur
        donnees, err = appel(jeton, "commercial_content/query/", corps, CHAMPS)
        if err:
            journal.append(("commercial_content/query", f"page {page}", "ERREUR", err))
            print(f"  page {page} : ERREUR {err}", file=sys.stderr)
            break
        d = donnees.get("data", {})
        lot = d.get("commercial_contents", []) or d.get("materials", []) or []
        journal.append(("commercial_content/query", f"page {page}",
                        f"{len(lot)} contenus", ""))
        print(f"  page {page} : {len(lot)} contenus", file=sys.stderr)
        for c in lot:
            createur = c.get("creator") or {}
            lignes.append({
                "id": c.get("id", ""),
                "date": c.get("create_date", ""),
                "createur": createur.get("username", ""),
                "pays_createur": createur.get("country_code", ""),
                "marques": " | ".join(c.get("brand_names", []) or []),
                "label": c.get("label", ""),
                "video": json.dumps(c.get("videos", []), ensure_ascii=False)[:300],
                "releve_le": date_lisible,
            })
        if not d.get("has_more"):
            break
        curseur = d.get("search_id")
        if not curseur:
            break

    md = [f"# Commercial Content Library TikTok — {date_lisible}", "",
          "Produit par `outils/tester_tiktok_commercial.py`.",
          "Hypotheses testees : **TT-02** (les publications organiques a label de",
          "partenariat y figurent) et **TT-03** (interrogeable par annonceur).", "",
          "| Appel | Page | Resultat | Erreur |", "|---|---|---|---|"]
    for a, p, r, e in journal:
        md += [f"| `{a}` | {p} | {r} | {e[:160]} |"]

    if lignes:
        csv_path = SORTIE / f"tiktok_commercial_{horodatage}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)
        marques = {}
        for l in lignes:
            for m in l["marques"].split(" | "):
                if m:
                    marques[m] = marques.get(m, 0) + 1
        createurs = {l["createur"] for l in lignes if l["createur"]}
        md += ["", f"## {len(lignes)} contenus, {len(createurs)} createurs, "
               f"{len(marques)} marques", "",
               f"Detail : `{csv_path.name}`.", "",
               "### Les 40 marques les plus presentes", "",
               "| Marque | Contenus |", "|---|---|"]
        for m, n in sorted(marques.items(), key=lambda x: -x[1])[:40]:
            md += [f"| {m} | {n} |"]
        md += ["", "### A faire ensuite", "",
               "Croiser la colonne `marques` avec la feuille Alias du classeur",
               "et avec HATVP_organisations. Toute marque de la filiere",
               "viande/lait qui apparait ici est **une collaboration declaree",
               "par la plateforme**, pas une inference.", ""]
    else:
        md += ["", "## Aucun contenu retourne", "",
               "Lire la colonne Erreur. Un refus d'authentification et un",
               "resultat vide ne disent pas la meme chose.", ""]

    md_path = SORTIE / f"tiktok_commercial_{horodatage}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nEcrit : {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
