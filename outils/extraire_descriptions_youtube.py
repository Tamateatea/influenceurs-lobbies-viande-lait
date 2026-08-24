"""
Lit la description publique des videos d'un releve et y cherche les alias
de la filiere viande/lait.

Idee testee : observation de Vincent, 24 aout 2026 — « les collaborations
commerciales sont visibles en description, il n'y a peut-etre pas besoin de
regarder les videos ». Ce script transforme cette observation en mesure.

Chaine testee :
    releve de test croise  ->  description publique  ->  table d'alias  ->  entite

La table d'alias est lue dans cartographie_filiere.xlsx (feuilles Alias et
Interprofessions) : c'est elle la source de verite, pas ce script.

Ecrit ses resultats dans recherche/, horodates. Voir LISEZ-MOI.md,
« Une mesure non ecrite n'existe pas ».

Usage :  python outils/extraire_descriptions_youtube.py
"""

import csv
import json
import re
import sys
import unicodedata
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "recherche"
CLASSEUR = RACINE / "cartographie" / "cartographie_filiere.xlsx"

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

ARTICLES = ("les", "le", "la", "l", "des", "de", "du")

# Formules qui signalent une communication commerciale sans nommer la marque.
# Volontairement larges : on mesure d'abord, on affine ensuite.
FORMULES = [
    "collaboration commerciale", "en partenariat avec", "partenariat remunere",
    "sponsorise par", "vous est propose par", "vous est proposee par",
    "merci a", "merci aux", "grace a nos partenaires", "#ad", "#sponsorise",
    "#publicite", "code promo", "lien affilie",
]


def get(url, timeout=30):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    except Exception:
        return ""


def aplatir(texte):
    """Minuscules, sans accents, sans ponctuation ni espaces.

    Permet a « Produits Laitiers » de rencontrer « @lesproduitslaitiers » :
    les deux deviennent la meme suite de lettres.
    """
    t = unicodedata.normalize("NFKD", str(texte or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def variantes(alias):
    """Formes aplaties d'un alias, avec et sans article de tete."""
    base = aplatir(alias)
    if len(base) < 5:
        return set()
    formes = {base}
    for art in ARTICLES:
        if base.startswith(art) and len(base) - len(art) >= 5:
            formes.add(base[len(art):])
    return formes


def charger_alias():
    """Construit la liste (forme_aplatie, alias_lisible, entite) depuis le classeur."""
    try:
        import openpyxl
    except ImportError:
        print("openpyxl manquant : pip install openpyxl", file=sys.stderr)
        raise
    wb = openpyxl.load_workbook(CLASSEUR, read_only=True, data_only=True)
    termes = {}

    def ajouter(alias, entite):
        if not alias or not entite:
            return
        for f in variantes(alias):
            termes.setdefault(f, (str(alias).strip(), str(entite).strip()))

    for ligne in wb["Alias"].iter_rows(min_row=2, values_only=True):
        ajouter(ligne[0], ligne[2])
    for ligne in wb["Interprofessions"].iter_rows(min_row=2, values_only=True):
        sigle, nom, _fil, vitrine = ligne[0], ligne[1], ligne[2], ligne[3]
        ajouter(sigle, sigle)
        ajouter(nom, sigle)
        ajouter(vitrine, sigle)
    wb.close()
    return termes


def description_et_soustitres(vid):
    """Renvoie (description, sous_titres_annonces, sous_titres_telechargeables)."""
    page = get(f"https://www.youtube.com/watch?v={vid}")
    if not page:
        return None, False, False

    desc = ""
    m = re.search(r'"shortDescription":"(.*?)","isCrawlable"', page, re.S)
    if m:
        try:
            desc = json.loads('"' + m.group(1) + '"')
        except Exception:
            desc = m.group(1)

    annonces, telechargeables = False, False
    c = re.search(r'"captionTracks":(\[.*?\])', page, re.S)
    if c:
        try:
            pistes = json.loads(c.group(1))
            annonces = bool(pistes)
            if pistes:
                url = pistes[0]["baseUrl"].encode().decode("unicode_escape")
                telechargeables = len(get(url, 20).strip()) > 0
        except Exception:
            pass
    return desc, annonces, telechargeables


def analyser(desc, termes):
    """Cherche les alias et les formules commerciales dans une description."""
    plat = aplatir(desc)
    sans_accent = unicodedata.normalize("NFKD", desc.lower())
    sans_accent = "".join(c for c in sans_accent if not unicodedata.combining(c))

    trouves, entites = [], []
    for forme, (lisible, entite) in termes.items():
        if forme in plat:
            trouves.append(lisible)
            entites.append(entite)
    formules = [f for f in FORMULES if f in sans_accent]
    return sorted(set(trouves)), sorted(set(entites)), formules


def dernier_releve():
    fichiers = sorted(SORTIE.glob("test_croise_youtube_*.csv"))
    return fichiers[-1] if fichiers else None


def main():
    releve = dernier_releve()
    if not releve:
        print("Aucun releve de test croise dans recherche/. Lance d'abord "
              "outils/test_croise_youtube.py", file=sys.stderr)
        return 1

    with releve.open(encoding="utf-8") as fh:
        videos = list(csv.DictReader(fh))
    termes = charger_alias()
    print(f"{len(termes)} formes d'alias chargees depuis {CLASSEUR.name}", file=sys.stderr)
    print(f"{len(videos)} videos reprises de {releve.name}", file=sys.stderr)

    with ThreadPoolExecutor(6) as ex:
        resultats = list(ex.map(lambda v: description_et_soustitres(v["video_id"]), videos))

    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    date_lisible = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lignes = []
    for v, (desc, st_annonces, st_dispo) in zip(videos, resultats):
        if desc is None:
            desc, st_annonces, st_dispo = "", False, False
        alias, entites, formules = analyser(desc, termes)
        lignes.append({
            "chaine": v["chaine"],
            "video_id": v["video_id"],
            "url": v["url"],
            "titre": v["titre"],
            "cas_signal": v["cas"],
            "declaree_youtube": v["declaree"],
            "segments_sponsorblock": v["segments_sponsorblock"],
            "alias_trouves": " | ".join(alias),
            "entites_filiere": " | ".join(entites),
            "formules_commerciales": " | ".join(formules),
            "description_longueur": len(desc),
            "soustitres_annonces": "oui" if st_annonces else "non",
            "soustitres_telechargeables": "oui" if st_dispo else "non",
            "description": desc.replace("\n", " ⏎ ")[:1500],
            "releve_le": date_lisible,
        })

    csv_path = SORTIE / f"descriptions_youtube_{horodatage}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
        w.writeheader()
        w.writerows(lignes)

    touches = [l for l in lignes if l["entites_filiere"]]
    avec_formule = [l for l in lignes if l["formules_commerciales"]]
    st_ok = sum(1 for l in lignes if l["soustitres_telechargeables"] == "oui")
    st_annonces = sum(1 for l in lignes if l["soustitres_annonces"] == "oui")

    md = [
        f"# Descriptions YouTube et table d'alias — {date_lisible}",
        "",
        f"Produit par `outils/extraire_descriptions_youtube.py`.",
        f"Videos reprises de `{releve.name}`. Detail : `{csv_path.name}`.",
        "",
        "## Ce qui est mesure",
        "",
        f"- Videos examinees : **{len(lignes)}**",
        f"- Descriptions recuperees : **{sum(1 for l in lignes if l['description_longueur'] > 0)}**",
        f"- Videos citant une entite de la filiere viande/lait : **{len(touches)}**",
        f"- Videos portant une formule commerciale generique : **{len(avec_formule)}**",
        f"- Videos annoncant des sous-titres : **{st_annonces}**",
        f"- Videos dont les sous-titres sont **telechargeables** : **{st_ok}**",
        "",
    ]
    if touches:
        md += ["## Entites de la filiere trouvees en description", "",
               "| Chaine | Entite | Alias reconnu | Declaree YouTube | Segments SB | URL |",
               "|---|---|---|---|---|---|"]
        for l in touches:
            md += [f"| {l['chaine']} | **{l['entites_filiere']}** | {l['alias_trouves']} "
                   f"| {l['declaree_youtube']} | {l['segments_sponsorblock']} | {l['url']} |"]
        md += [""]
    else:
        md += ["## Entites de la filiere trouvees en description", "",
               "Aucune. Ce n'est pas un echec du script : c'est une mesure.", ""]

    md += ["## Videos a formule commerciale mais sans entite de la filiere", "",
           "Ce sont des collaborations d'un autre secteur. Utile pour mesurer la",
           "prevalence generale du sponsoring, pas pour le registre.", "",
           "| Chaine | Formules | Declaree | Segments SB |", "|---|---|---|---|"]
    for l in avec_formule:
        if not l["entites_filiere"]:
            md += [f"| {l['chaine']} | {l['formules_commerciales'][:60]} "
                   f"| {l['declaree_youtube']} | {l['segments_sponsorblock']} |"]

    md_path = SORTIE / f"descriptions_youtube_{horodatage}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\n".join(md))
    print(f"\nEcrit : {csv_path}\nEcrit : {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
