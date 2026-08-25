"""
Moissonne la Commercial Content Library de TikTok, mois par mois.

POURQUOI MOIS PAR MOIS

Le premier passage (25/08) a bute sur un plafond : la pagination s'arrete
autour de 20 000 contenus pour une seule requete, quelle que soit la periode
demandee. On ne savait donc pas combien il y en a reellement.

Decouper la periode en fenetres mensuelles contourne le plafond : chaque mois
est une requete distincte avec sa propre pagination. La couverture devient
complete de octobre 2022 a aujourd'hui.

CE QUE CETTE MOISSON PRODUIT

La **population de reference** du projet : tous les createurs francais dont
TikTok declare qu'ils ont publie du contenu commercial. C'est ce qui manquait
a METHODOLOGIE section 9.2 pour tirer un echantillon aleatoire et enfin
mesurer le rappel absolu.

Rappel de la limite etablie en JOURNAL 34 : `brand_names` est vide dans
99,99 % des cas. On obtient le createur, le label et la date — jamais la
marque. Cette moisson ne dit donc pas qui travaille pour la filiere ; elle dit
qui fait du commercial declare.

REPRISE : l'etat est enregistre apres chaque mois. Une interruption ne perd
que le mois en cours.

Usage :  python outils/moissonner_tiktok.py
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
ETAT = RACINE / "donnees" / "moisson_tiktok.json"

JETON_URL = "https://open.tiktokapis.com/v2/oauth/token/"
BASE = "https://open.tiktokapis.com/v2/research/adlib/commercial_content/query/"
CHAMPS = "id,create_date,brand_names,creator,label"

DEBUT = date(2022, 10, 1)


def lire_secret(nom):
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


def mois(debut, fin):
    """Fenetres mensuelles [premier jour, dernier jour] de debut a fin."""
    cur = date(debut.year, debut.month, 1)
    out = []
    while cur <= fin:
        suivant = date(cur.year + (cur.month == 12),
                       cur.month % 12 + 1, 1)
        dernier = min(suivant - timedelta(days=1), fin)
        out.append((cur.strftime("%Y%m%d"), dernier.strftime("%Y%m%d")))
        cur = suivant
    return out


def interroger(tok, dmin, dmax, curseur=None):
    corps = {
        "filters": {"content_published_date_range": {"min": dmin, "max": dmax},
                    "creator_country_code": "FR"},
        "max_count": 50,
    }
    if curseur:
        corps["search_id"] = curseur
    req = urllib.request.Request(
        BASE + "?fields=" + urllib.parse.quote(CHAMPS, safe=".,"),
        data=json.dumps(corps).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8")).get("data", {}), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code} — {e.read()[:180].decode('utf-8', 'replace')}"
    except Exception as e:
        return None, type(e).__name__


def main():
    if not lire_secret("TIKTOK_CLIENT_KEY"):
        print("Identifiants TikTok absents.", file=sys.stderr)
        return 1
    tok = jeton()
    ETAT.parent.mkdir(parents=True, exist_ok=True)
    etat = (json.loads(ETAT.read_text(encoding="utf-8")) if ETAT.exists()
            else {"mois_faits": {}, "contenus": {}})

    hier = (datetime.now(timezone.utc) - timedelta(days=1)).date()
    fenetres = mois(DEBUT, hier)
    print(f"{len(fenetres)} mois a couvrir | {len(etat['mois_faits'])} deja faits "
          f"| {len(etat['contenus'])} contenus en cache", file=sys.stderr)

    for dmin, dmax in fenetres:
        if dmin in etat["mois_faits"]:
            continue
        curseur, n, pages, echec = None, 0, 0, None
        while pages < 500:
            pages += 1
            d, err = interroger(tok, dmin, dmax, curseur)
            if err:
                if "401" in err or "invalid_token" in err.lower():
                    tok = jeton()          # le jeton expire au bout de 2 h
                    continue
                echec = err
                print(f"  {dmin} : ERREUR {err[:90]}", file=sys.stderr)
                break
            for c in d.get("commercial_contents", []) or []:
                cid = c.get("id")
                if not cid:
                    continue
                cr = c.get("creator") or {}
                etat["contenus"][cid] = {
                    "date": c.get("create_date", ""),
                    "createur": cr.get("username", ""),
                    "label": c.get("label", ""),
                    "marques": " | ".join(filter(None, c.get("brand_names") or [])),
                }
                n += 1
            if not d.get("has_more"):
                break
            curseur = d.get("search_id")
            if not curseur:
                break
            time.sleep(0.15)
        # Un mois qui a echoue ne doit PAS etre marque comme fait : une
        # reprise le sauterait et le trou serait definitif et invisible.
        # C'est la regle METHODOLOGIE 13.3 — distinguer l'absence de resultat
        # de l'absence de mesure — appliquee a la reprise.
        if echec:
            if "quota" in echec.lower():
                print(f"  quota TikTok epuise pour aujourd'hui, arret propre "
                      f"a {dmin[:4]}-{dmin[4:6]}", file=sys.stderr)
                ETAT.write_text(json.dumps(etat, ensure_ascii=False),
                                encoding="utf-8")
                break
            continue
        etat["mois_faits"][dmin] = n
        print(f"  {dmin[:4]}-{dmin[4:6]} : {n:>6d} contenus "
              f"| total {len(etat['contenus']):>7d}", file=sys.stderr)
        ETAT.write_text(json.dumps(etat, ensure_ascii=False), encoding="utf-8")

    ETAT.write_text(json.dumps(etat, ensure_ascii=False), encoding="utf-8")

    contenus = etat["contenus"]
    createurs = {}
    for c in contenus.values():
        u = c["createur"]
        if not u:
            continue
        d = createurs.setdefault(u, {"n": 0, "labels": set(), "dates": []})
        d["n"] += 1
        d["labels"].add(c["label"])
        d["dates"].append(c["date"])

    aujourdhui = date.today().isoformat()
    chemin = RECHERCHE / f"tiktok_population_{aujourdhui}.csv"
    with chemin.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["createur", "contenus_commerciaux", "labels",
                    "premiere_date", "derniere_date", "releve_le"])
        for u, d in sorted(createurs.items(), key=lambda x: -x[1]["n"]):
            w.writerow([u, d["n"], " | ".join(sorted(filter(None, d["labels"]))),
                        min(d["dates"]), max(d["dates"]), aujourdhui])

    avec_marque = sum(1 for c in contenus.values() if c["marques"])
    md = [f"# Population commerciale TikTok France — {aujourdhui}", "",
          "Produit par `outils/moissonner_tiktok.py`, mois par mois pour",
          "contourner le plafond de pagination.", "",
          f"- Mois couverts : **{len(etat['mois_faits'])}** sur {len(fenetres)}",
          f"- Contenus commerciaux : **{len(contenus):,}**".replace(",", " "),
          f"- **Createurs francais distincts : {len(createurs):,}**".replace(",", " "),
          f"- Contenus avec `brand_names` renseigne : **{avec_marque}** "
          f"({100*avec_marque/max(len(contenus),1):.2f} %)", "",
          "**C'est la population de reference du projet** : tous les createurs",
          "francais dont TikTok declare le contenu commercial. Elle permet le",
          "tirage aleatoire de METHODOLOGIE section 9.2, jamais possible",
          "jusqu'ici faute de population definie.", "",
          "Rappel : `brand_names` etant vide, cette moisson dit qui fait du",
          "commercial declare, jamais pour qui.", "",
          "## Les 40 createurs les plus actifs", "",
          "| Createur | Contenus | Periode |", "|---|---:|---|"]
    for u, d in sorted(createurs.items(), key=lambda x: -x[1]["n"])[:40]:
        md += [f"| @{u} | {d['n']} | {min(d['dates'])[:6]} – {max(d['dates'])[:6]} |"]

    md += ["", "## Contenus par mois", "", "| Mois | Contenus |", "|---|---:|"]
    for m, n in sorted(etat["mois_faits"].items()):
        md += [f"| {m[:4]}-{m[4:6]} | {n} |"]

    chemin_md = RECHERCHE / f"tiktok_population_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:12]))
    print(f"\nEcrit : {chemin_md}\nEcrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
