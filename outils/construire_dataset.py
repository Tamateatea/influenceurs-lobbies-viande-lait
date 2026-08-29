"""
Construit le jeu de donnees final, dans le format demande par Vincent.

LE FORMAT, TEL QU'IL L'A ECRIT LE 29/08

> Commencer par le lobby : Lobby institutionnel / vitrine / alias / contenu
> identifie comme etant de la pub finançant un influenceur (lien url) / date de
> publication / nombre de vues / statut de la collaboration (en cours, finie,
> inconnu) > Nom de l'influenceur / plateforme / alias / nombre d'abonnes

Plus une colonne **type de createur**, qu'il a demandee ensuite.

UNE LIGNE PAR CONTENU, PAS PAR CREATEUR

C'est le choix structurant de ce format, et il est juste : une collaboration
n'est pas un fait abstrait, c'est une video, un post, une annonce — datee,
consultable, verifiable. Un createur qui a fait cinq videos pour le CNIEL
occupe cinq lignes, et chacune peut etre contestee separement.

CE QUI VIENT D'OU

    lobby institutionnel   la table d'alias : quelle interprofession
    vitrine                le nom sous lequel elle communique
    alias                  la chaine de caracteres reellement observee
    contenu                l'URL, quand on l'a
    date                   la date de publication du contenu
    vues                   YouTube seulement, et seulement si demande
    statut                 deduit des dates — voir `statut_collaboration`
    influenceur            le nom, tel qu'observe
    plateforme             YouTube, Instagram, TikTok, Facebook
    alias influenceur      son @pseudo, quand Vincent l'a etabli
    abonnes                son audience, quand Vincent l'a etablie
    type                   sa categorie, telle que Vincent l'a jugee

CE QUE CE FICHIER N'EST PAS

**Ce n'est pas un registre publiable.** Chaque ligne porte une colonne
`degre_de_certitude` et une colonne `verifie_par_humain`. METHODOLOGIE 9 est
formelle : rien ne se publie sans verification, et a faible prevalence un bon
detecteur produit surtout des faux positifs.

Le champ **montant** est volontairement absent : aucune source ne le donne au
niveau du createur (METHODOLOGIE 1bis). L'ajouter vide donnerait l'illusion
qu'il pourrait etre rempli.

Usage :  python outils/construire_dataset.py
"""

import csv
import re
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir
from medias import est_media

COLONNES = [
    "commanditaire", "type_de_commanditaire", "secteur", "groupe_parent",
    "vitrine", "alias_observe",
    "contenu_url", "date_publication", "nombre_de_vues",
    "statut_collaboration",
    "nom_influenceur", "plateforme", "alias_influenceur",
    "nombre_abonnes", "type_de_createur",
    "canal_de_detection", "degre_de_certitude", "verifie_par_humain",
    "titre_du_contenu",
]

# Les interprofessions, pour remonter d'une vitrine ou d'une marque au lobby.
LOBBIES = {
    "CNIEL": "CNIEL", "INTERBEV": "INTERBEV", "INAPORC": "INAPORC",
    "ANVOL": "ANVOL", "CIFOG": "CIFOG", "CNPO": "CNPO", "FICT": "FICT",
}


def marques_connues():
    """marque aplatie -> (secteur, groupe parent), depuis la feuille Marques."""
    import openpyxl
    f = CARTO / "cartographie_filiere.xlsx"
    if not f.exists():
        return {}
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    out = {}
    if "Marques" in wb.sheetnames:
        for r in wb["Marques"].iter_rows(min_row=2, values_only=True):
            if r[0]:
                out[aplatir(r[0])] = (str(r[2] or ""), str(r[1] or ""))
    wb.close()
    return out


def qualifier(entite, table, marques):
    """Qui est ce commanditaire : interprofession ou marque, et de quel secteur ?

    ON N'ECRIT PAS « lobby = INTERBEV » QUAND C'EST CHARAL QUI PAIE. Une marque
    est un commanditaire a part entiere — precision de Vincent le 24/08 — et
    lui attribuer l'interprofession de son secteur serait une inference fausse :
    Charal ne paie pas au nom d'INTERBEV.

    Le secteur est donne separement, comme contexte, sans jamais se substituer
    a l'identite du payeur.

    Rend (nom, type, secteur, groupe parent).
    """
    base = str(entite or "").split(" (")[0].strip()
    if not base:
        return "", "", "", ""
    if base in LOBBIES:
        return base, "interprofession", "", ""
    plat = aplatir(base)
    if plat in marques:
        secteur, groupe = marques[plat]
        return base, "marque", secteur, groupe
    # certaines vitrines portent le nom du groupe entre parentheses
    dedans = re.search(r"\(([^)]+)\)", str(entite or ""))
    if dedans and aplatir(dedans.group(1)) in marques:
        secteur, groupe = marques[aplatir(dedans.group(1))]
        return base, "marque", secteur, groupe
    rattache = table.get(plat, "")
    if rattache:
        return base, "vitrine", "", rattache
    return base, "non qualifie", "", ""


def table_des_entites():
    """vitrine aplatie -> lobby institutionnel, depuis le classeur."""
    import openpyxl
    f = CARTO / "cartographie_filiere.xlsx"
    if not f.exists():
        return {}
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    out = {}
    if "Alias" in wb.sheetnames:
        for r in wb["Alias"].iter_rows(min_row=2, values_only=True):
            if r[0] and len(r) > 2 and r[2]:
                cible = str(r[2]).split(" (")[0].strip()
                out[aplatir(r[0])] = cible if cible in LOBBIES else ""
                out[aplatir(cible)] = cible if cible in LOBBIES else ""
    wb.close()
    return out


def fiches_createurs():
    """Ce que Vincent a etabli a la main : pseudo, audience, type.

    C'est du travail humain irremplacable — aucune source automatique ne donne
    le nombre d'abonnes d'un createur nomme par son prenom sur un site de
    lobby. Il est lu ici, jamais recalcule.
    """
    import openpyxl
    fiches = {}
    for nom_fichier, ligne_entete, col_nom, col_type, col_com in [
            ("CREATEURS_SUR_LES_SITES.xlsx", 24, 2, 5, 6),
            ("CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx", 34, 2, 10, 11)]:
        f = CARTO / nom_fichier
        if not f.exists():
            continue
        try:
            ws = openpyxl.load_workbook(f, data_only=True)["createurs"]
        except Exception:
            continue
        for r in range(ligne_entete + 1, ws.max_row + 1):
            nom = ws.cell(row=r, column=col_nom).value
            if not nom:
                continue
            com = str(ws.cell(row=r, column=col_com).value or "")
            typ = str(ws.cell(row=r, column=col_type).value or "")
            pseudo = re.search(r"@+([A-Za-z0-9_.\-]{3,40})", com)
            audience = re.search(
                r"([\d]+(?:[,\.]\d+)?)\s*([kKmM])\s*"
                r"(?:followers|subscribers|subscriver|subscibers|abonnes)", com)
            plateforme = ("Instagram" if "insta" in com.lower()
                          else "YouTube" if "youtube" in com.lower()
                          else "TikTok" if "tiktok" in com.lower() else "")
            if pseudo or audience or typ:
                fiches[aplatir(nom)] = {
                    "pseudo": "@" + pseudo.group(1) if pseudo else "",
                    "abonnes": (audience.group(1).replace(",", ".")
                                + audience.group(2).upper()) if audience else "",
                    "plateforme": plateforme,
                    "type": typ.replace("oui — ", "").replace("non — ", ""),
                }
    return fiches


def statut_collaboration(date_debut, date_fin=""):
    """En cours, finie, ou inconnu — deduit des dates disponibles.

    Regle : un contenu publie il y a moins de six mois est dit « recent »
    plutot qu'« en cours ». Une video ne s'arrete pas, elle reste en ligne :
    parler de collaboration « en cours » supposerait de savoir si le contrat
    court encore, ce qu'aucune source ne dit.
    """
    if not date_debut:
        return "inconnu"
    if date_fin:
        return "finie"
    try:
        annee = int(str(date_debut)[:4])
    except ValueError:
        return "inconnu"
    return "recent" if annee >= date.today().year - 1 else "ancien"


def main():
    table = table_des_entites()
    marques = marques_connues()
    fiches = fiches_createurs()
    print(f"{len(marques)} marques rattachees a un secteur", file=sys.stderr)
    print(f"{len(fiches)} fiches de createurs etablies par Vincent",
          file=sys.stderr)

    lignes = []

    def ajouter(entite, vitrine, alias, url, date_pub, nom, plateforme,
                canal, certitude, titre="", fin=""):
        if not nom or est_media(nom):
            return
        commanditaire, type_c, secteur, groupe = qualifier(entite, table, marques)
        # Un commanditaire qu'on ne sait pas qualifier n'entre pas : c'est ce
        # qui laissait « Time Out Paris » et « Stardusttv » dans le jeu.
        if type_c == "non qualifie":
            return
        fiche = fiches.get(aplatir(nom), {})
        lignes.append({
            "commanditaire": commanditaire,
            "type_de_commanditaire": type_c,
            "secteur": secteur,
            "groupe_parent": groupe,
            "vitrine": vitrine or "",
            "alias_observe": alias or "",
            "contenu_url": url or "",
            "date_publication": date_pub or "",
            "nombre_de_vues": "",
            "statut_collaboration": statut_collaboration(date_pub, fin),
            "nom_influenceur": nom,
            "plateforme": plateforme or fiche.get("plateforme", ""),
            "alias_influenceur": fiche.get("pseudo", ""),
            "nombre_abonnes": fiche.get("abonnes", ""),
            "type_de_createur": fiche.get("type", ""),
            "canal_de_detection": canal,
            "degre_de_certitude": certitude,
            "verifie_par_humain": "oui" if fiche else "non",
            "titre_du_contenu": (titre or "")[:120],
        })

    # --- canal 1 : le createur ecrit lui-meme le nom du commanditaire ---
    f = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))
    if f:
        with f[-1].open(encoding="utf-8") as fh:
            for l in csv.DictReader(fh):
                if not l.get("force", "").startswith("ALIAS"):
                    continue
                for e in l.get("entites_retenues", "").split(" | "):
                    if not e:
                        continue
                    ajouter(e, e, l.get("alias_reconnus", ""),
                            l.get("url", ""), l.get("publiee", ""),
                            l.get("chaine", ""), "YouTube",
                            "description du createur",
                            "lien commercial soupconne", l.get("titre", ""))

    # --- canal 2 : le commanditaire publie une video nommant le createur ---
    f = sorted(RECHERCHE.glob("chaines_lobbies_*.csv"))
    if f:
        with f[-1].open(encoding="utf-8") as fh:
            for l in csv.DictReader(fh):
                noms = l.get("createurs_nommes", "").split(" | ")
                vias = l.get("reconnu_par", "").split(" | ")
                for i, nom in enumerate(noms):
                    if i >= len(vias) or not vias[i].startswith("compte connu"):
                        continue
                    ajouter(l["entite"], l.get("chaine_lobby", ""),
                            "", l.get("url", ""), l.get("publiee", ""),
                            nom, "YouTube", "chaine du commanditaire",
                            "lien commercial documente", l.get("titre", ""))

    # --- canal 3 : le commanditaire a paye pour diffuser ---
    f = sorted(RECHERCHE.glob("createurs_annonces_*.csv"))
    if f:
        with f[-1].open(encoding="utf-8") as fh:
            for l in csv.DictReader(fh):
                if l.get("voie") == "vocabulaire de collaboration":
                    continue
                plateformes = l.get("plateformes", "")
                plat = ("Instagram" if "instagram" in plateformes.lower()
                        else "Facebook" if "facebook" in plateformes.lower()
                        else "")
                ajouter(l.get("page_annonceuse", ""),
                        l.get("page_annonceuse", ""), "",
                        l.get("page_facebook", ""), l.get("debut_diffusion", ""),
                        l["createur"], plat, "publicite payee",
                        "lien commercial documente", l.get("extrait", ""))

    if not lignes:
        print("Aucune ligne produite.", file=sys.stderr)
        return 1

    # Les lignes dont le lobby est inconnu ne sont pas jetees : elles portent
    # une marque dont le rattachement n'est pas encore etabli. C'est une
    # information, pas un dechet.
    aujourdhui = date.today().isoformat()
    chemin = RECHERCHE / f"dataset_{aujourdhui}.csv"
    with chemin.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLONNES)
        w.writeheader()
        w.writerows(lignes)

    from collections import Counter
    par_canal = Counter(l["canal_de_detection"] for l in lignes)
    par_lobby = Counter(f"{l['commanditaire']} ({l['type_de_commanditaire']})"
                        for l in lignes)
    avec_fiche = sum(1 for l in lignes if l["verifie_par_humain"] == "oui")
    createurs = len({aplatir(l["nom_influenceur"]) for l in lignes})

    md = [f"# Jeu de donnees — {aujourdhui}", "",
          "Produit par `outils/construire_dataset.py`, au format demande par",
          "Vincent le 29/08. **Une ligne par contenu**, pas par createur : une",
          "collaboration est une video ou une annonce, datee et consultable.", "",
          f"- Lignes : **{len(lignes)}**",
          f"- Createurs distincts : **{createurs}**",
          f"- Lignes dont le createur a une fiche etablie par Vincent : "
          f"**{avec_fiche}**", "",
          "| Canal de detection | Lignes |", "|---|---:|"]
    for c, n in par_canal.most_common():
        md += [f"| {c} | {n} |"]
    md += ["", "| Commanditaire | Lignes |", "|---|---:|"]
    for c, n in par_lobby.most_common(12):
        md += [f"| {c} | {n} |"]
    md += ["", "## Ce qui manque encore", "",
           "- **Le nombre de vues** : recuperable sur YouTube pour 1 unite de",
           "  quota par tranche de 50 videos. Pas encore fait.",
           "- **Le montant** : aucune source au niveau du createur. La colonne",
           "  est volontairement absente plutot que vide (METHODOLOGIE 1bis).",
           "- **Les pseudos et audiences** : etablis a la main par Vincent pour",
           f"  {len(fiches)} createurs. Les autres lignes ont ces cases vides.", "",
           "**Aucune ligne n'est publiable en l'etat.** Chacune porte son degre",
           "de certitude et l'indication qu'un humain l'a verifiee ou non.", ""]

    chemin_md = RECHERCHE / f"dataset_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:14]))
    print(f"\nEcrit : {chemin.name} et {chemin_md.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
