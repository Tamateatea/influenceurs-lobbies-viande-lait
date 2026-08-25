"""
Croise les createurs TikTok a partenariat declare avec le registre des comptes.

CE QU'ON CHERCHE

TikTok nous donne 8 061 createurs francais dont la plateforme **declare**
qu'ils ont fait du partenariat remunere — sans dire pour qui (TT-08, refutee).

Le registre `COMPTES.xlsx`, lui, contient des comptes reperes par d'autres
chemins : suivis par une vitrine de lobby, publies sur le site d'une
interprofession, ou surveilles sur YouTube.

Un compte present dans les DEUX est un candidat notablement plus fort :
la plateforme atteste qu'il fait du partenariat remunere, et une source
independante l'associe deja a la filiere viande/lait.

CE QUE CE N'EST PAS

Ce croisement ne prouve **pas** que le partenariat TikTok est avec la filiere.
Un createur peut etre suivi par le CNIEL et faire du partenariat pour une
marque de telephones. Les deux faits sont vrais et independants ; leur
conjonction est une **priorite d'enquete**, pas une conclusion.

Rappel : la cle d'un compte est le couple (plateforme, identifiant). Un meme
pseudo sur TikTok et sur Instagram ne prouve pas la meme personne — c'est une
hypothese de rattachement, comme en JOURNAL 32.3.

Aucun appel reseau : les deux jeux de donnees sont deja enregistres.

Usage :  python outils/croiser_tiktok_registre.py
"""

import csv
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"


def aplatir(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def dernier(motif):
    f = sorted(RECHERCHE.glob(motif))
    return f[-1] if f else None


def main():
    f_tt = dernier("tiktok_commercial_*.csv")
    f_reg = dernier("comptes_consolides_*.csv")
    if not f_tt or not f_reg:
        print("Il manque le releve TikTok ou le registre consolide.", file=sys.stderr)
        return 1

    # --- cote TikTok : un createur peut avoir plusieurs contenus ---
    tiktok = defaultdict(lambda: {"contenus": 0, "labels": set(), "dates": []})
    with f_tt.open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            u = l.get("createur", "").strip()
            if not u:
                continue
            d = tiktok[aplatir(u)]
            d["contenus"] += 1
            d["labels"].add(l.get("label", ""))
            d["dates"].append(l.get("date", ""))
            d["pseudo"] = u
    print(f"{len(tiktok)} createurs TikTok distincts ({f_tt.name})", file=sys.stderr)

    # --- cote registre ---
    registre = defaultdict(list)
    with f_reg.open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            for cle in (l.get("identifiant", ""), l.get("pseudo", "")):
                if cle:
                    registre[aplatir(cle)].append(l)
    print(f"{len(registre)} identifiants dans le registre ({f_reg.name})",
          file=sys.stderr)

    lignes = []
    for plat, tt in tiktok.items():
        if plat not in registre:
            continue
        for compte in registre[plat]:
            # un compte TikTok qui se croise avec lui-meme n'apprend rien
            if compte.get("plateforme") == "tiktok":
                continue
            aud = compte.get("audience", "")
            lignes.append({
                "pseudo": tt["pseudo"],
                "contenus_commerciaux_tiktok": tt["contenus"],
                "labels_tiktok": " | ".join(sorted(filter(None, tt["labels"]))),
                "premiere_date": min(tt["dates"]) if tt["dates"] else "",
                "derniere_date": max(tt["dates"]) if tt["dates"] else "",
                "autre_plateforme": compte.get("plateforme", ""),
                "identifiant_registre": compte.get("identifiant", ""),
                "nom_affiche": compte.get("nom_affiche", ""),
                "audience_autre_plateforme": aud,
                "lien_avec_la_filiere": compte.get("lien_avec_la_filiere", ""),
                "entites_liees": compte.get("entites_liees", ""),
                "priorite_vincent": compte.get("priorite", ""),
                "rattachement": "HYPOTHESE — meme pseudo, personne non verifiee",
                "releve_le": date.today().isoformat(),
            })

    lignes.sort(key=lambda l: (-(int(l["audience_autre_plateforme"])
                                 if str(l["audience_autre_plateforme"]).isdigit() else 0),
                               -l["contenus_commerciaux_tiktok"]))

    aujourdhui = date.today().isoformat()
    if lignes:
        chemin = RECHERCHE / f"croisement_tiktok_registre_{aujourdhui}.csv"
        with chemin.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)

    pseudos = {l["pseudo"] for l in lignes}
    md = [f"# Createurs TikTok presents dans le registre — {aujourdhui}", "",
          "Produit par `outils/croiser_tiktok_registre.py`, sans appel reseau.", "",
          f"- Createurs TikTok a partenariat declare : **{len(tiktok)}**",
          f"- Identifiants du registre : **{len(registre)}**",
          f"- **Comptes presents dans les deux : {len(pseudos)}**", "",
          "**Ce que ce croisement dit**, et seulement cela : ces personnes font",
          "du partenariat remunere declare sur TikTok, ET une source",
          "independante les associe deja a la filiere viande/lait.",
          "",
          "**Ce qu'il ne dit pas** : que le partenariat TikTok soit avec la",
          "filiere. Un createur peut etre suivi par le CNIEL et faire du",
          "partenariat pour une marque de telephones.",
          "",
          "| Pseudo | Contenus TikTok | Periode | Autre plateforme | Audience | Lien avec la filiere |",
          "|---|---:|---|---|---:|---|"]
    for l in lignes[:80]:
        aud = int(l["audience_autre_plateforme"]) if str(
            l["audience_autre_plateforme"]).isdigit() else 0
        periode = (f"{l['premiere_date'][:6]}–{l['derniere_date'][:6]}"
                   if l["premiere_date"] else "")
        md += [f"| **@{l['pseudo']}** | {l['contenus_commerciaux_tiktok']} | {periode} "
               f"| {l['autre_plateforme']} | {aud:,} "
               f"| {l['lien_avec_la_filiere'][:44]} |".replace(",", " ")]
    if len(lignes) > 80:
        md += ["", f"({len(lignes) - 80} autres lignes dans le CSV)"]

    chemin_md = RECHERCHE / f"croisement_tiktok_registre_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:8]))
    print(f"\nEcrit : {chemin_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
