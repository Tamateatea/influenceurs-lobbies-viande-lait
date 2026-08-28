"""
Assemble le registre : un createur, ses commanditaires, et ce qui l'atteste.

CE QUE C'EST

La livraison du projet. Jusqu'ici on a produit des **candidats par canal** —
descriptions, chaines des lobbies, publicites payees, sites — sans jamais les
croiser entre eux. Ce script les reunit en **une ligne par createur**, avec le
ou les commanditaires qui le remunerent et la liste des canaux qui l'attestent.

POURQUOI LE CROISEMENT CHANGE TOUT

Les quatre canaux sont **independants par construction** : ils lisent des
sources differentes, ecrites par des gens differents.

    description          le createur ecrit qu'il a un partenaire
    chaines des lobbies  le commanditaire publie une video le nommant
    publicites payees    le commanditaire a paye Meta pour le diffuser
    sites des lobbies    le commanditaire l'affiche sur son propre site

Un nom trouve par **un seul** canal peut etre un artefact d'appariement — le
projet en a produit beaucoup, et les a mesures. Un nom trouve par **trois**
canaux distincts ne peut pas etre un artefact : il faudrait que trois erreurs
independantes tombent sur le meme nom.

Le nombre de canaux devient donc un **degre de confiance**, et il se calcule
sans jugement humain. C'est ce qui permet de dire a Vincent quelles lignes
meritent son temps.

CE QUE CE SCRIPT NE FAIT PAS

Il ne decide pas qu'une ligne est publiable. METHODOLOGIE section 9 est
formelle : rien ne se publie sans verification humaine, et a faible prevalence
meme un excellent detecteur produit majoritairement des faux positifs.

Ce classement ne remplace pas le jugement de Vincent — il lui dit par quoi
commencer.

Aucun reseau, aucun quota.

Usage :  python outils/assembler_registre.py
"""

import csv
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir
from medias import est_media

# Un nom plus court n'est pas apparie de facon fiable entre canaux : c'est la
# regle du projet depuis JOURNAL 60.
LONGUEUR_MINIMALE = 6


def commanditaires_connus():
    """Les entites de la table d'alias, pour ecarter les faux commanditaires.

    La moisson des publicites remonte la page qui a paye. Beaucoup de ces
    pages n'ont rien a voir avec la filiere — « Time Out Paris » est ressorti
    34 fois. Une page ne compte comme commanditaire que si la table la connait.
    """
    import table_alias
    termes = table_alias.charger(seuil=5, avec_marques=True,
                                 avec_hors_perimetre=True)
    return {aplatir(e.split(" (")[0]) for _f, (_a, e) in termes.items()}


def ajouter(registre, createur, entite, canal, detail, date_vue="", connus=None):
    """Enregistre une attestation, en gardant la trace de sa provenance.

    LA CLE EST LE CREATEUR SEUL, pas le couple (createur, commanditaire).

    Premiere version le 29/08 : la cle etait le couple, et seuls 6 couples sur
    519 etaient attestes par plus d'un canal. Cause : **les canaux ne nomment
    pas le commanditaire de la meme facon**. Les publicites rendent la page qui
    a paye — « Charal », « Regilait » — quand les autres canaux rendent
    l'interprofession — « CNIEL », « INTERBEV ». La jointure echouait
    mecaniquement, et faisait croire que les canaux voyaient des mondes
    differents.

    Le createur, lui, s'ecrit pareil partout. Les commanditaires deviennent un
    attribut — ce qui correspond d'ailleurs au schema voulu par Vincent
    (METHODOLOGIE 1bis) : un influenceur, et le ou les commanditaires qui le
    remunerent.
    """
    nom = str(createur or "").strip()
    ent = str(entite or "").strip()
    if len(aplatir(nom)) < LONGUEUR_MINIMALE or not ent or est_media(nom):
        return
    if connus is not None and aplatir(ent.split(" (")[0]) not in connus:
        return
    d = registre.setdefault(aplatir(nom), {
        "createur": nom, "commanditaires": set(), "canaux": {},
        "premiere_date": "", "derniere_date": ""})
    d["commanditaires"].add(ent)
    d["canaux"].setdefault(canal, []).append(detail)
    if date_vue:
        if not d["premiere_date"] or date_vue < d["premiere_date"]:
            d["premiere_date"] = date_vue
        if date_vue > d["derniere_date"]:
            d["derniere_date"] = date_vue


def canal_description(registre, connus):
    """Le createur ecrit lui-meme qu'il a un partenaire."""
    f = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))
    if not f:
        return
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            if not l.get("force", "").startswith("ALIAS"):
                continue
            for e in l.get("entites_retenues", "").split(" | "):
                ajouter(registre, l["chaine"], e, "description",
                        l.get("titre", "")[:70], l.get("publiee", ""), connus)


def canal_chaines_lobbies(registre, connus):
    """Le commanditaire publie une video nommant le createur."""
    f = sorted(RECHERCHE.glob("chaines_lobbies_*.csv"))
    if not f:
        return
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            noms = l.get("createurs_nommes", "").split(" | ")
            vias = l.get("reconnu_par", "").split(" | ")
            for i, nom in enumerate(noms):
                # la voie « motif dans le titre » n'est pas mesuree : elle
                # remonte surtout des noms de series (JOURNAL 55.4). On ne
                # retient ici que la voie fiable.
                if i < len(vias) and vias[i].startswith("compte connu"):
                    ajouter(registre, nom, l["entite"], "chaine du lobby",
                            l.get("titre", "")[:70], l.get("publiee", ""), connus)


def canal_publicites(registre, connus):
    """Le commanditaire a paye Meta pour diffuser un contenu le nommant."""
    f = sorted(RECHERCHE.glob("createurs_annonces_*.csv"))
    if not f:
        return
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            # meme prudence : la voie « vocabulaire de collaboration » attrape
            # des mots courants (JOURNAL, createurs_dans_annonces).
            if l.get("voie") == "vocabulaire de collaboration":
                continue
            ajouter(registre, l["createur"], l.get("page_annonceuse", ""),
                    "publicite payee", l.get("extrait", "")[:70],
                    l.get("debut_diffusion", ""), connus)


def canal_sites(registre, connus):
    """Le commanditaire l'affiche sur son propre site."""
    f = RACINE / "donnees" / "sources" / "laitflix" / "laitflix_series.md"
    if not f.exists():
        return
    entite, serie = "CNIEL", ""
    for ligne in f.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("### "):
            serie = ligne[4:].split(" — ")[0].strip()
            continue
        if not serie or ligne.startswith(("#", ">", "|", "*", "-")) or not ligne.strip():
            continue
        # les lignes de createurs sont separees par des points medians
        for nom in re.split(r"\s+·\s+", ligne.strip()):
            nom = re.sub(r"\s*\(.*?\)", "", nom).strip(" .·")
            if nom:
                ajouter(registre, nom, entite, "site du lobby", serie, "", connus)


def main():
    registre = {}
    connus = commanditaires_connus()
    print(f"{len(connus)} entites reconnues comme commanditaires", file=sys.stderr)
    canal_description(registre, connus)
    canal_chaines_lobbies(registre, connus)
    canal_publicites(registre, connus)
    canal_sites(registre, connus)

    if not registre:
        print("Aucune attestation trouvee.", file=sys.stderr)
        return 1

    lignes = sorted(registre.values(),
                    key=lambda d: (-len(d["canaux"]), d["createur"].lower()))

    par_nombre = defaultdict(int)
    for d in lignes:
        par_nombre[len(d["canaux"])] += 1

    aujourdhui = date.today().isoformat()
    chemin = RECHERCHE / f"registre_{aujourdhui}.csv"
    with chemin.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["createur", "commanditaires", "nombre_de_canaux", "canaux",
                    "premiere_trace", "derniere_trace", "attestations"])
        for d in lignes:
            w.writerow([d["createur"], " | ".join(sorted(d["commanditaires"])),
                        len(d["canaux"]),
                        " | ".join(sorted(d["canaux"])), d["premiere_date"],
                        d["derniere_date"],
                        " ⏎ ".join(f"[{c}] {v[0]}" for c, v in
                                   sorted(d["canaux"].items()))[:600]])

    md = [f"# Registre assemble — {aujourdhui}", "",
          "Produit par `outils/assembler_registre.py`. Aucun reseau.", "",
          "Une ligne par **createur**, avec le ou les commanditaires qui le",
          "remunerent et les canaux qui l'attestent — c'est le schema voulu",
          "par Vincent (METHODOLOGIE 1bis).", "",
          "Les quatre canaux sont independants par construction : ils lisent",
          "des sources ecrites par des gens differents.", "",
          f"- Createurs distincts : **{len(lignes)}**", "",
          "| Atteste par | Createurs | Ce que ca vaut |", "|---:|---:|---|"]
    valeur = {
        4: "**quatre canaux independants** — un artefact est exclu",
        3: "**trois canaux independants** — un artefact est exclu",
        2: "deux canaux — solide, verification rapide",
        1: "un seul canal — a verifier entierement",
    }
    for n in sorted(par_nombre, reverse=True):
        md += [f"| {n} canaux | {par_nombre[n]} | {valeur.get(n, '')} |"]

    md += ["", "**Ce classement ne remplace pas le jugement humain.**",
           "METHODOLOGIE 9 est formelle : rien ne se publie sans verification.",
           "Il dit seulement par quoi commencer.", "",
           "## Les couples attestes par plusieurs canaux", "",
           "| Createur | Commanditaire | Canaux | Traces |",
           "|---|---|---|---|"]
    multi = [d for d in lignes if len(d["canaux"]) >= 2]
    for d in multi[:60]:
        md += [f"| **{d['createur'][:30]}** | "
               f"{', '.join(sorted(d['commanditaires']))[:34]} "
               f"| {len(d['canaux'])} — {', '.join(sorted(d['canaux']))} "
               f"| {d['premiere_date']} … {d['derniere_date']} |"]
    if not multi:
        md += ["| — | aucun couple atteste par plus d'un canal | | |"]

    chemin_md = RECHERCHE / f"registre_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:16]))
    print(f"\nEcrit : {chemin.name} et {chemin_md.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
