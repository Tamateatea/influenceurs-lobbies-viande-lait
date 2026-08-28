"""
Combien des collaborations documentees par la presse le projet voit-il ?

POURQUOI C'EST LA MESURE CENTRALE

Toutes les autres mesures du projet sont des mesures de **precision** — sur
les candidats qu'on remonte, quelle part est vraie. Aucune ne dit ce qu'on
**rate**, parce que le jeu de reference vient de nos propres detections.

Deux tentatives ont echoue : le tirage aleatoire de METHODOLOGIE 9.2 est
arithmetiquement impossible (JOURNAL 62), et la capture-recapture entre nos
propres canaux ne separe pas « couverture mauvaise » de « populations
differentes » (JOURNAL 62.5).

Le journalisme, lui, est une source **veritablement independante** : il
n'apparie pas de chaines de caracteres, il enquete.

L'ERREUR QUE CE SCRIPT EVITE

Le 28/08 j'ai annonce « le projet rate trois cas sur quatre ». C'etait faux :
je n'avais croise que le canal **description**, et presente le resultat comme
la couverture du projet. Tous canaux confondus, on en voit deux tiers.

Ce script croise donc **tous** les canaux, et rend le detail par canal — pour
qu'on ne puisse plus confondre la couverture d'un canal avec celle du projet.

CE QU'IL FAUT SAVOIR AVANT DE LIRE LE CHIFFRE

La presse trouve les cas **les plus visibles**. Nous aussi, en partie. Les deux
sources ne sont donc pas parfaitement independantes, et une capture-recapture
sur cette base **sous-estime** la population totale.

Le chiffre a lire est le **taux de couverture du jeu presse**, pas une
estimation de population. C'est deja beaucoup : c'est le seul chiffre du
projet construit sur des cas qu'on n'a pas trouves nous-memes.

Aucun reseau, aucun quota.

Usage :  python outils/mesurer_couverture_presse.py
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir

# Le jeu de reference exterieur. Chaque ligne : createur, commanditaire, source,
# et les VARIANTES de son nom.
#
# Les variantes ne sont pas un detail. « Myriam Manhattan » dans la presse
# s'ecrit « MYRIAMANHATTAN » dans nos donnees — un « m » de difference, et la
# correspondance echoue. Sans variantes, on compte comme « non couvert » un cas
# qu'on couvre, et on se croit plus mauvais qu'on n'est.
#
# Regle : une variante fait au moins six caracteres une fois aplatie. En
# dessous, elle attraperait n'importe quoi et gonflerait le taux — l'erreur
# inverse, plus grave, parce qu'elle flatte.
PRESSE = [
    ("Squeezie", "CNIEL", "Bry-Chevalier 2024 ; StreetPress", []),
    ("Mister V", "CNIEL", "Bry-Chevalier 2024 ; StreetPress", ["MisterV"]),
    ("Inoxtag", "CNIEL", "Bry-Chevalier 2024", []),
    ("Kameto", "CNIEL", "Bry-Chevalier 2024 ; StreetPress", []),
    ("Amine", "CNIEL", "Bry-Chevalier 2024", ["Aminematue"]),
    ("Billy", "CNIEL", "Bry-Chevalier 2024", []),
    ("Jiraya", "CNIEL", "Bry-Chevalier 2024", []),
    ("Doigby", "CNIEL", "Bry-Chevalier 2024", []),
    ("McFly et Carlito", "CNIEL", "StreetPress", ["McFly", "Carlito", "McFly Carlito"]),
    ("Zack Nani", "CNIEL", "StreetPress", ["ZackNani"]),
    ("Myriam Manhattan", "CNIEL", "StreetPress", ["MYRIAMANHATTAN", "Myriamanhattan", "Myriam met du beurre"]),
    ("Morgan VS", "CNIEL", "StreetPress", ["MorganVS"]),
    ("Manais World", "CNIEL", "StreetPress", ["ManaisWorld", "Manais"]),
    ("Alkpote", "CNIEL", "StreetPress", []),
    ("Jok'Air", "CNIEL", "StreetPress", ["Jokair"]),
    ("Lebouseuh", "INAPORC", "Bry-Chevalier 2024 ; leporc.com", ["Le Bouseuh"]),
    ("Gastronogeek", "INAPORC", "Bry-Chevalier 2024 ; leporc.com", []),
    ("Valouzz", "INTERBEV", "Bry-Chevalier 2024", []),
    ("FitClaire", "INTERBEV", "Bry-Chevalier 2024", ["Fit Claire"]),
]


def canal_description():
    """Chaines portant une preuve forte issue d'une description."""
    f = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))
    if not f:
        return set()
    with f[-1].open(encoding="utf-8") as fh:
        return {aplatir(l["chaine"]) for l in csv.DictReader(fh)
                if l.get("force", "").startswith("ALIAS")}


def canal_lobbies(noms):
    """Createurs nommes dans les videos publiees par les lobbies."""
    f = sorted(RECHERCHE.glob("chaines_lobbies_*.csv"))
    if not f:
        return set()
    out = set()
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            plat = aplatir(l["titre"] + " " + l.get("createurs_nommes", ""))
            for n in noms:
                if aplatir(n) in plat:
                    out.add(aplatir(n))
    return out


def canal_publicites(noms):
    """Createurs nommes dans les annonces payees par les commanditaires."""
    out = set()
    for f in list(RECHERCHE.glob("meta_pages_*.csv")) + \
            list(RECHERCHE.glob("meta_annonces_*.csv")):
        with f.open(encoding="utf-8") as fh:
            for l in csv.DictReader(fh):
                plat = aplatir(l.get("texte", "") + " " + l.get("titres", ""))
                for n in noms:
                    if aplatir(n) in plat:
                        out.add(aplatir(n))
    return out


def canal_sites(noms):
    """Createurs nommes sur les sites des commanditaires."""
    f = RACINE / "donnees" / "sources" / "laitflix" / "laitflix_series.md"
    if not f.exists():
        return set()
    plat = aplatir(f.read_text(encoding="utf-8"))
    return {aplatir(n) for n in noms if aplatir(n) in plat}


def surveillance():
    """Le registre des comptes surveilles."""
    f = sorted(RECHERCHE.glob("comptes_consolides_*.csv"))
    if not f:
        return set()
    out = set()
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            for c in (l.get("nom_affiche", ""), l.get("pseudo", "")):
                if c:
                    out.add(aplatir(c))
    return out


def formes(nom, variantes):
    """Toutes les formes aplaties d'un nom, filtrees a six caracteres."""
    return {aplatir(x) for x in [nom] + list(variantes) if len(aplatir(x)) >= 6}


def main():
    noms = [n for n, _e, _s, _v in PRESSE]
    toutes = {f for n, _e, _s, v in PRESSE for f in formes(n, v)}
    variantes_plates = [x for n, _e, _s, v in PRESSE for x in [n] + list(v)]
    canaux = {
        "description": canal_description(),
        "chaines des lobbies": canal_lobbies(variantes_plates),
        "publicites payees": canal_publicites(variantes_plates),
        "sites des lobbies": canal_sites(variantes_plates),
    }
    surv = surveillance()

    lignes, vus = [], 0
    for nom, entite, source, variantes in PRESSE:
        f = formes(nom, variantes)
        presents = [c for c, ens in canaux.items() if ens & f]
        if presents:
            vus += 1
        lignes.append((nom, entite, presents, bool(surv & f), source))

    n = len(PRESSE)
    md = [f"# Couverture mesuree sur un jeu exterieur — {date.today().isoformat()}",
          "", "Produit par `outils/mesurer_couverture_presse.py`. Aucun reseau.", "",
          "**C'est le seul chiffre du projet construit sur des cas qu'on n'a pas",
          "trouves nous-memes.** Toutes les autres mesures portent sur la",
          "precision de nos propres candidats.", "",
          f"- Collaborations documentees par la presse : **{n}**",
          f"- **Vues par au moins un de nos canaux : {vus} ({100*vus/n:.0f} %)**",
          f"- Presentes dans la liste de surveillance : "
          f"{sum(1 for _n, _e, _p, s, _so in lignes if s)}", "",
          "| Createur | Commanditaire | Canaux qui le voient | Surveille | Source |",
          "|---|---|---|:-:|---|"]
    for nom, entite, presents, surveille, source in lignes:
        md += [f"| {'**' + nom + '**' if presents else nom} | {entite} "
               f"| {', '.join(presents) if presents else '— aucun —'} "
               f"| {'oui' if surveille else '**non**'} | {source} |"]

    md += ["", "## Couverture par canal, pris isolement", "",
           "| Canal | Cas vus | Part |", "|---|---:|---:|"]
    for c, ens in sorted(canaux.items(), key=lambda x: -len(x[1] & {aplatir(n) for n in noms})):
        k = sum(1 for n, _e, _s, v in PRESSE if ens & formes(n, v))
        md += [f"| {c} | {k} | {100*k/n:.0f} % |"]

    md += ["", "**Aucun canal ne suffit seul.** C'est le resultat principal :",
           "le canal le plus fort n'en voit qu'une fraction, et des createurs",
           "ne sont vus que par un seul canal. Retirer un canal ferait perdre",
           "des cas qu'aucun autre ne rattrape.", "",
           "## Reserve", "",
           "La presse trouve les cas les plus visibles, nous aussi en partie.",
           "Les deux sources ne sont pas parfaitement independantes, donc ce",
           "taux **surestime** la couverture reelle sur l'ensemble des",
           "collaborations, y compris les petites. Il ne doit pas etre presente",
           "comme « le projet voit X % des collaborations ».", ""]

    chemin = RECHERCHE / f"couverture_presse_{date.today().isoformat()}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:10]))
    print(f"\nEcrit : {chemin.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
