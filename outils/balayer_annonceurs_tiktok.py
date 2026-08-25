"""
Balaye la bibliotheque publicitaire de TikTok sur tous les termes de la filiere.

POURQUOI CET ENDPOINT ET PAS L'AUTRE

TikTok expose deux points d'acces qui ne se joignent pas (JOURNAL 34) :

  commercial_content/query  le createur et le label, mais PAS la marque,
                            et son `search_term` est silencieusement ignore
  ad/query                  la marque et l'agence, mais PAS le createur,
                            et son `search_term` FONCTIONNE

Celui-ci exploite le second. Il ne trouvera donc pas de createurs : il
etablit **quelles entreprises de la filiere achetent de la publicite en
France, et par quelle agence**. C'est de la cartographie de commanditaires,
pas de la detection de collaboration — mais avec des sources primaires, ce qui
manquait cruellement a la feuille `Agences` (quatre lignes, dont deux vides).

VALIDATION DE LA RECHERCHE

Le script commence par interroger un terme absurde. Si ce terme rend des
resultats, c'est que le filtre ne fonctionne pas et le script **s'arrete** :
mieux vaut ne rien rendre qu'un balayage silencieusement vide de sens.
C'est la lecon du 25/08 sur `commercial_content/query`.

Usage :  python outils/balayer_annonceurs_tiktok.py
"""

import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"

JETON_URL = "https://open.tiktokapis.com/v2/oauth/token/"
BASE = "https://open.tiktokapis.com/v2/research/adlib/ad/query/"
CHAMPS = ("ad.id,ad.first_shown_date,ad.last_shown_date,ad.status,ad.reach,"
          "advertiser.business_name,advertiser.paid_for_by")

DEBUT = "20221001"
FIN = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")
TERME_ABSURDE = "zzqqxxwwvvkk"


def lire_secret(nom):
    if not SECRETS.exists():
        return None
    m = re.search(rf"{nom}\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m and not m.group(1).startswith("colle") else None


def jeton():
    corps = urllib.parse.urlencode({
        "client_key": lire_secret("TIKTOK_CLIENT_KEY"),
        "client_secret": lire_secret("TIKTOK_CLIENT_SECRET"),
        "grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(
        JETON_URL, data=corps,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))["access_token"]


def chercher(tok, terme, max_pages=6):
    """Toutes les pubs francaises correspondant a un terme."""
    ads, curseur = [], None
    for _ in range(max_pages):
        corps = {"filters": {"ad_published_date_range": {"min": DEBUT, "max": FIN},
                             "country_code": "FR"},
                 "search_term": terme, "max_count": 50}
        if curseur:
            corps["search_id"] = curseur
        req = urllib.request.Request(
            BASE + "?fields=" + urllib.parse.quote(CHAMPS, safe=".,"),
            data=json.dumps(corps).encode(),
            headers={"Authorization": f"Bearer {tok}",
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read().decode("utf-8")).get("data", {})
        except urllib.error.HTTPError as e:
            return ads, f"HTTP {e.code} — {e.read()[:150].decode('utf-8', 'replace')}"
        except Exception as e:
            return ads, type(e).__name__
        ads += d.get("ads", [])
        if not d.get("has_more"):
            break
        curseur = d.get("search_id")
        if not curseur:
            break
        time.sleep(0.2)
    return ads, None


def termes_filiere():
    """Marques + alias d'interprofession, depuis le classeur."""
    import openpyxl
    wb = openpyxl.load_workbook(CARTO / "cartographie_filiere.xlsx",
                                read_only=True, data_only=True)
    termes = {}
    for l in wb["Marques"].iter_rows(min_row=2, values_only=True):
        if l[0] and len(str(l[0]).strip()) >= 4:
            termes[str(l[0]).strip()] = f"marque ({l[1]})" if l[1] else "marque"
    for l in wb["Alias"].iter_rows(min_row=2, values_only=True):
        if l[0] and len(str(l[0]).strip()) >= 5:
            termes[str(l[0]).strip().lstrip("@")] = f"alias de {l[2]}"
    for l in wb["Interprofessions"].iter_rows(min_row=2, values_only=True):
        if l[0]:
            termes[str(l[0]).strip()] = "interprofession"
    wb.close()
    # quelques termes generiques de la filiere, qui ne sont pas des marques
    for t in ["lait", "fromage", "yaourt", "beurre", "viande", "boeuf", "porc",
              "jambon", "charcuterie", "volaille", "steak", "creme fraiche"]:
        termes.setdefault(t, "terme generique de la filiere")
    return termes


def main():
    if not lire_secret("TIKTOK_CLIENT_KEY"):
        print("Identifiants TikTok absents de SECRETS.txt.", file=sys.stderr)
        return 1
    tok = jeton()

    # --- garde-fou : la recherche filtre-t-elle vraiment ? ---
    bidon, err = chercher(tok, TERME_ABSURDE, max_pages=1)
    if err:
        print(f"Erreur des le controle : {err}", file=sys.stderr)
        return 1
    if bidon:
        print(f"ARRET : le terme absurde « {TERME_ABSURDE} » rend "
              f"{len(bidon)} resultats.", file=sys.stderr)
        print("Le filtre ne fonctionne pas ; un balayage n'aurait aucun sens.",
              file=sys.stderr)
        return 2
    print(f"controle passe : « {TERME_ABSURDE} » rend 0 resultat", file=sys.stderr)

    termes = termes_filiere()
    print(f"{len(termes)} termes a balayer", file=sys.stderr)

    lignes, journal = [], []
    for i, (terme, nature) in enumerate(sorted(termes.items()), 1):
        ads, err = chercher(tok, terme)
        journal.append((terme, nature, len(ads), err or ""))
        if err:
            print(f"  {i:>3d}/{len(termes)} {terme[:28]:30s} ERREUR {err[:60]}",
                  file=sys.stderr)
            continue
        annonceurs = set()
        for a in ads:
            ad, ann = a.get("ad", {}), a.get("advertiser", {})
            nom = ann.get("business_name", "")
            annonceurs.add(nom)
            lignes.append({
                "terme_cherche": terme,
                "nature_du_terme": nature,
                "annonceur": nom,
                "paye_par": ann.get("paid_for_by", ""),
                "ad_id": ad.get("id", ""),
                "premiere_diffusion": ad.get("first_shown_date", ""),
                "derniere_diffusion": ad.get("last_shown_date", ""),
                "statut": ad.get("status", ""),
                "audience": (ad.get("reach") or {}).get("unique_users_seen", ""),
                "releve_le": date.today().isoformat(),
            })
        if ads:
            print(f"  {i:>3d}/{len(termes)} {terme[:28]:30s} {len(ads):>4d} pubs "
                  f"| {len(annonceurs)} annonceur(s)", file=sys.stderr)

    aujourdhui = date.today().isoformat()
    if lignes:
        chemin = RECHERCHE / f"tiktok_annonceurs_{aujourdhui}.csv"
        with chemin.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)

    par_annonceur = {}
    for l in lignes:
        d = par_annonceur.setdefault(l["annonceur"], {"pubs": 0, "termes": set(),
                                                      "agences": set()})
        d["pubs"] += 1
        d["termes"].add(l["terme_cherche"])
        if l["paye_par"]:
            d["agences"].add(l["paye_par"])

    md = [f"# Annonceurs TikTok de la filiere — {aujourdhui}", "",
          "Produit par `outils/balayer_annonceurs_tiktok.py`.", "",
          "Endpoint `ad/query` : **publicites achetees**, pas partenariats de",
          "createurs. Donne l'annonceur et l'agence, jamais le createur",
          "(JOURNAL 34.4).", "",
          f"- Termes balayes : **{len(termes)}**",
          f"- Publicites trouvees : **{len(lignes)}**",
          f"- Annonceurs distincts : **{len(par_annonceur)}**",
          f"- Controle du terme absurde : **passe** (0 resultat)", "",
          "## Annonceurs, par volume", "",
          "| Annonceur | Pubs | Agence(s) declaree(s) | Termes qui l'ont fait sortir |",
          "|---|---:|---|---|"]
    for nom, d in sorted(par_annonceur.items(), key=lambda x: -x[1]["pubs"])[:80]:
        md += [f"| **{nom}** | {d['pubs']} | {' | '.join(sorted(d['agences']))[:60]} "
               f"| {', '.join(sorted(d['termes']))[:70]} |"]

    agences = {}
    for l in lignes:
        if l["paye_par"]:
            agences.setdefault(l["paye_par"], set()).add(l["annonceur"])
    if agences:
        md += ["", "## Agences declarees (`paid_for_by`)", "",
               "A reporter dans la feuille `Agences` du classeur, avec cette",
               "source primaire.", "",
               "| Agence | Annonceurs |", "|---|---|"]
        for a, anns in sorted(agences.items(), key=lambda x: -len(x[1])):
            md += [f"| **{a}** | {', '.join(sorted(anns))[:90]} |"]

    chemin_md = RECHERCHE / f"tiktok_annonceurs_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:14]))
    print(f"\nEcrit : {chemin_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
