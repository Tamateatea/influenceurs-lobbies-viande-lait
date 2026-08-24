"""
Cherche des noms de createurs dans les sites web des commanditaires eux-memes.

NOUVELLE PISTE, formulee et testee le 24 aout 2026.

Toutes les methodes precedentes partent du CONTENU du createur et essaient d'y
reconnaitre un annonceur. Celle-ci fait l'inverse : elle part du site de
l'interprofession et y cherche des noms de createurs.

Interet : ce sont des **sources primaires**, publiees par le commanditaire
lui-meme. Un lobby qui ecrit sur son propre site « en partenariat avec X » est
la meilleure preuve possible — meilleure qu'une inference sur une description
de video. Et ces sites sont publics, sans authentification, avec des plans de
site qui listent leurs pages.

Limite connue d'avance : un lobby n'a aucune obligation de publier la liste de
ses partenaires, et les campagnes d'influence sont justement ce qu'il met le
moins en avant (voir METHODOLOGIE.md section 2 : sur la campagne Interbev de
2025, le commanditaire n'etait jamais nomme). Un resultat vide serait donc
informatif, pas surprenant.

Ce que le script cherche, deux choses independantes :

  1. les **noms de createurs** connus — tires des listes d'abonnements
     Instagram relevees par Vincent, et de la liste de surveillance YouTube ;
  2. le **vocabulaire de l'influence** — « influenceur », « createur de
     contenu », « ambassadeur », « partenariat »... qui signale les pages a
     lire meme quand aucun nom connu n'y figure.

Ecrit ses resultats dans recherche/, horodates.

Usage :
    python outils/fouiller_sites_lobbies.py
    python outils/fouiller_sites_lobbies.py --pages 200
"""

import argparse
import csv
import html
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "recherche"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Accept-Language": "fr-FR,fr;q=0.9"}

SITES = {
    "CNIEL": "https://www.produits-laitiers.com",
    "CNIEL (institutionnel)": "https://www.filiere-laitiere.fr",
    "INTERBEV": "https://www.interbev.fr",
    "INTERBEV (grand public)": "https://www.la-viande.fr",
    "INAPORC": "https://www.leporc.com",
}

# Vocabulaire de l'influence. Signale une page a lire meme sans nom connu.
VOCABULAIRE = [
    "influenceur", "influenceuse", "influence marketing",
    "createur de contenu", "creatrice de contenu", "createurs de contenu",
    "ambassadeur", "ambassadrice", "youtubeur", "youtubeuse",
    "tiktokeur", "instagrameur", "partenariat", "collaboration",
    "campagne digitale", "reseaux sociaux",
]

# Un @pseudo publie par le site du commanditaire lui-meme. C'est la trouvaille
# du 24/08 : leporc.com (INAPORC) credite ses recettes a des createurs nommes,
# « pizza tomate jambon cru par @pepites2noisette ». Recolter ces pseudos
# trouve des createurs qu'on ne connaissait pas, au lieu de se limiter a
# verifier ceux qu'on connait deja.
ARROBASE = re.compile(r"(?<![\w@.])@([a-z0-9](?:[a-z0-9._]{3,28})[a-z0-9])(?![\w.])")

# Pseudos appartenant aux lobbies eux-memes : ce sont leurs propres marques,
# omnipresentes dans leurs menus. Les compter serait un faux positif garanti.
PSEUDOS_MAISON = {
    "lesproduitslaitiers", "laitflix", "produitstripiers", "la_viande_fr",
    "leporcfrancais", "volaillefrancaise", "naturellementflexitariens",
    "interbev", "cniel", "inaporc", "anvol", "lescharcuteries",
    "label_rouge_quality", "oeufsdefrance", "ouefsdefrance",
}

# Un pseudo n'existe QUE sur une plateforme. Constate le 24/08 : le site du
# CNIEL ecrit « leur compte Twitter @LesProLaitiers » — Vincent a cherche ce
# compte sur Instagram, ne l'a pas trouve, et a conclu a tort qu'il n'existait
# pas. Recolter un pseudo sans sa plateforme produit des fantomes.
PLATEFORMES = {
    "instagram": ["instagram", "insta "], "twitter": ["twitter", " x ", "tweet"],
    "tiktok": ["tiktok"], "youtube": ["youtube", "chaine youtube"],
    "facebook": ["facebook"], "twitch": ["twitch"], "linkedin": ["linkedin"],
}

PAUSE = 0.3
FILS = 4


def plateforme_probable(texte, position, fenetre=220):
    """La plateforme nommee le plus pres du pseudo, ou vide."""
    autour = texte[max(0, position - fenetre):position + fenetre].lower()
    trouvees = [nom for nom, mots in PLATEFORMES.items()
                if any(m in autour for m in mots)]
    return " | ".join(trouvees)


def get(url, timeout=30, essais=2):
    attente = 2.0
    for essai in range(essais):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                time.sleep(PAUSE)
                return r.read().decode("utf-8", "replace"), None
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and essai < essais - 1:
                time.sleep(attente)
                attente *= 3
                continue
            return "", f"HTTP {e.code}"
        except Exception as e:
            if essai < essais - 1:
                time.sleep(attente)
                continue
            return "", type(e).__name__
    return "", "epuise"


def sans_accent(t):
    t = unicodedata.normalize("NFKD", str(t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def texte_visible(page):
    """Retire scripts, styles et balises. Suffisant pour chercher des noms."""
    p = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", page)
    p = re.sub(r"(?s)<[^>]+>", " ", p)
    return re.sub(r"\s+", " ", html.unescape(p))


def urls_du_site(base, plafond):
    """Toutes les URL declarees par les plans de site, avec un plafond."""
    robots, _ = get(base + "/robots.txt", 20)
    plans = re.findall(r"(?i)sitemap:\s*(\S+)", robots) or [base + "/sitemap.xml"]
    vus, urls = set(), []
    a_lire = list(plans[:4])
    while a_lire and len(urls) < plafond:
        plan = a_lire.pop(0)
        if plan in vus:
            continue
        vus.add(plan)
        contenu, _ = get(plan, 30)
        trouves = re.findall(r"<loc>\s*(.*?)\s*</loc>", contenu)
        for u in trouves:
            u = html.unescape(u)
            if u.endswith(".xml"):
                if len(vus) < 25:
                    a_lire.append(u)
            elif re.search(r"\.(jpg|jpeg|png|gif|pdf|svg|webp|mp4|zip)$", u, re.I):
                continue
            elif u not in urls:
                urls.append(u)
    return urls[:plafond]


def charger_createurs():
    """Noms et pseudos de createurs connus, tires de nos propres relevés."""
    noms = {}

    releves = sorted(SORTIE.glob("comptes_suivis_*.csv"))
    if releves:
        with releves[-1].open(encoding="utf-8") as f:
            for l in csv.DictReader(f):
                for candidat in (l.get("compte_suivi", ""), l.get("nom_affiche", "")):
                    c = sans_accent(candidat).strip()
                    # au moins 6 caracteres et pas un mot courant : sinon
                    # « seb » ou « papilles » declencheraient partout
                    if len(c) >= 6 and re.fullmatch(r"[a-z0-9 ._-]+", c):
                        noms.setdefault(c, l.get("compte_suivi", candidat))

    surveillance = sorted(SORTIE.glob("surveillance_youtube_*.csv"))
    if surveillance:
        with surveillance[-1].open(encoding="utf-8") as f:
            for l in csv.DictReader(f):
                c = sans_accent(l.get("chaine_demandee", "")).strip()
                if len(c) >= 6:
                    noms.setdefault(c, l.get("chaine_demandee", ""))
    return noms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=150,
                    help="pages maximum par site")
    args = ap.parse_args()

    SORTIE.mkdir(exist_ok=True)
    createurs = charger_createurs()
    print(f"{len(createurs)} noms de createurs charges depuis recherche/",
          file=sys.stderr)
    if not createurs:
        print("Aucun releve de createurs trouve — lance d'abord "
              "extraire_comptes_suivis.py", file=sys.stderr)

    lignes, resume = [], []

    for entite, base in SITES.items():
        urls = urls_du_site(base, args.pages)
        print(f"\n{entite:26s} {base}", file=sys.stderr)
        print(f"  {len(urls)} pages listees par le plan de site", file=sys.stderr)
        if not urls:
            resume.append((entite, base, 0, 0, 0, "aucun plan de site exploitable"))
            continue

        with ThreadPoolExecutor(FILS) as ex:
            pages = list(ex.map(lambda u: get(u, 25), urls))

        echecs = sum(1 for _c, e in pages if e)
        n_vocab, n_noms = 0, 0
        for url, (contenu, err) in zip(urls, pages):
            if err or not contenu:
                continue
            txt = sans_accent(texte_visible(contenu))
            mots = [v for v in VOCABULAIRE if v in txt]
            trouves = []
            for forme, lisible in createurs.items():
                if re.search(r"(?<![a-z0-9])" + re.escape(forme) + r"(?![a-z0-9])", txt):
                    trouves.append(lisible)
            brut = texte_visible(contenu)
            # Un « @quelquechose.com » est un domaine de courriel, pas un
            # pseudo. Les reglements de jeu-concours en listent des dizaines
            # (jetable.com, yopmail.com...) : sans ce filtre, ils polluent
            # la recolte.
            trouves_pseudos = {}
            for m in ARROBASE.finditer(brut.lower()):
                ps = m.group(1)
                if ps in PSEUDOS_MAISON:
                    continue
                # « @quelquechose.com » est un domaine de courriel, pas un pseudo
                if re.search(r"\.(com|net|org|fr|io|us|eu|co)$", ps):
                    continue
                plat = plateforme_probable(brut.lower(), m.start())
                if ps not in trouves_pseudos or (plat and not trouves_pseudos[ps]):
                    trouves_pseudos[ps] = plat
            pseudos = sorted(trouves_pseudos)
            if not mots and not trouves and not pseudos:
                continue
            if mots:
                n_vocab += 1
            if trouves:
                n_noms += 1
            extrait = ""
            if trouves:
                m = re.search(r".{0,150}" + re.escape(sans_accent(trouves[0]))
                              + r".{0,150}", txt)
                extrait = m.group(0) if m else ""
            lignes.append({
                "entite": entite,
                "site": base,
                "url": url,
                "pseudos_publies": " | ".join(pseudos[:15]),
                "plateformes_probables": " ; ".join(
                    f"{ps}={trouves_pseudos[ps] or '?'}" for ps in pseudos[:15]),
                "createurs_trouves": " | ".join(sorted(set(trouves))[:8]),
                "vocabulaire_influence": " | ".join(mots[:8]),
                "extrait": extrait[:400],
            })
        resume.append((entite, base, len(urls), n_vocab, n_noms,
                       f"{echecs} page(s) non lue(s)" if echecs else "ok"))
        print(f"  {n_vocab} pages au vocabulaire d'influence, "
              f"{n_noms} pages citant un createur connu", file=sys.stderr)

    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    date_lisible = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    csv_path = SORTIE / f"sites_lobbies_{horodatage}.csv"
    if lignes:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)

    avec_nom = [l for l in lignes if l["createurs_trouves"]]
    md = [f"# Fouille des sites des commanditaires — {date_lisible}", "",
          "Produit par `outils/fouiller_sites_lobbies.py`.",
          "Piste : chercher les createurs dans les sites des lobbies eux-memes,",
          "plutot que chercher les lobbies dans le contenu des createurs.", "",
          f"Noms de createurs deja connus, cherches : **{len(createurs)}**", "",
          "| Entite | Pages lues | Vocabulaire d'influence | Createur cite | Etat |",
          "|---|---|---|---|---|"]
    for e, _b, n, v, c, etat in resume:
        md += [f"| {e} | {n} | {v} | **{c}** | {etat} |"]

    recolte = {}
    for l in lignes:
        for p in l["pseudos_publies"].split(" | "):
            if p:
                recolte.setdefault(p, {"entites": set(), "pages": 0, "url": l["url"]})
                recolte[p]["entites"].add(l["entite"])
                recolte[p]["pages"] += 1

    md += ["", "## PSEUDOS PUBLIES PAR LES SITES DES COMMANDITAIRES", ""]
    if recolte:
        md += [f"**{len(recolte)} pseudos distincts**, credites par les lobbies",
               "eux-memes sur leurs propres sites.", "",
               "C'est la source la plus directe du projet : c'est le commanditaire",
               "qui nomme le createur, pas nous qui l'inferons.", "",
               "**Reserve : un credit n'est pas une preuve de remuneration.** Une",
               "recette creditee etablit une relation de travail documentee, pas",
               "son caractere onereux. A verifier au cas par cas.", "",
               "| Pseudo | Commanditaire(s) | Pages | Exemple |", "|---|---|---|---|"]
        for p, d in sorted(recolte.items(), key=lambda x: -x[1]["pages"]):
            md += [f"| **@{p}** | {', '.join(sorted(d['entites']))} "
                   f"| {d['pages']} | {d['url']} |"]
        md += [""]
    else:
        md += ["Aucun pseudo publie. C'est une mesure.", ""]

    md += ["", "## Pages citant un createur deja connu de nos relevés", ""]
    if avec_nom:
        md += ["**A verifier a la main : une citation n'est pas une collaboration.**",
               "Un lobby peut nommer un createur sans l'avoir remunere.", "",
               "| Entite | Createur(s) | URL |", "|---|---|---|"]
        for l in avec_nom:
            md += [f"| {l['entite']} | **{l['createurs_trouves']}** | {l['url']} |"]
        md += [""]
        for l in avec_nom[:15]:
            md += [f"### {l['entite']} — {l['createurs_trouves']}", "",
                   l["url"], "", "> " + l["extrait"], ""]
    else:
        md += ["Aucune. **C'est une mesure, et elle etait previsible** :",
               "les interprofessions ne publient pas la liste des createurs",
               "qu'elles remunerent. C'est precisement le brouillage du donneur",
               "d'ordre decrit en METHODOLOGIE.md section 2.", "",
               "Consequence : cette piste ne remplace pas la detection dans le",
               "contenu. Elle reste utile en veille, a relancer periodiquement.", ""]

    md_path = SORTIE / f"sites_lobbies_{horodatage}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md))
    print(f"\nEcrit : {md_path}")
    if lignes:
        print(f"Ecrit : {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
