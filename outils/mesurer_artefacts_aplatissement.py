"""
Combien des detections du projet sont des artefacts d'aplatissement ?

LA QUESTION

L'appariement se fait sur du texte aplati, ce qui colle les mots voisins et
fabrique des chaines absentes du texte reel. Trois faux positifs ont ete
trouves un par un — « noclippant », « clippara », « la viande frerot ».

Un par un ne dit rien de l'ampleur. Ce script la mesure sur l'ensemble du
corpus moissonne, avec le garde-fou de frontiere de mot d'`appariement.py`.

CE QU'IL PEUT ET NE PEUT PAS VOIR

La moisson ne conserve que les 900 premiers caracteres de chaque description,
alors que l'appariement a travaille sur le texte complet. **Pour 42 % des
detections, le terme declencheur n'est donc pas dans le texte disponible** et
la frontiere de mot n'y est pas verifiable.

Ces lignes sont comptees a part, sous « invérifiable ». Les confondre avec les
artefacts gonflerait le chiffre d'un facteur quatre — c'est exactement le genre
de raccourci que le projet s'interdit.

Aucun reseau, aucun quota.

Usage :  python outils/mesurer_artefacts_aplatissement.py
"""

import csv
import sys
from collections import Counter
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir, aplatir_avec_index, coupe_un_mot

ARTICLES = ("les", "le", "la", "l", "des", "de", "du")


def formes_de(alias):
    """Les formes aplaties sous lesquelles un alias peut se presenter."""
    base = aplatir(alias)
    if len(base) < 5:
        return []
    formes = [base]
    for art in ARTICLES:
        if base.startswith(art) and len(base) - len(art) >= 5:
            formes.append(base[len(art):])
    return formes


def main():
    fichiers = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))
    if not fichiers:
        print("Aucun detections_nettoyees_*.csv.", file=sys.stderr)
        return 1
    source = fichiers[-1]

    with source.open(encoding="utf-8") as fh:
        lignes = list(csv.DictReader(fh))

    propres, artefacts, invisibles = [], [], []
    par_forme = Counter()

    for l in lignes:
        texte = (l.get("titre", "") + " "
                 + l.get("description", "").replace(" ⏎ ", "\n"))
        plat, index = aplatir_avec_index(texte)
        alias = [a.strip() for a in l.get("alias_reconnus", "").split("|")
                 if a.strip()]

        vu, propre = False, False
        for a in alias:
            for forme in formes_de(a):
                depart = plat.find(forme)
                while depart >= 0:
                    vu = True
                    if not coupe_un_mot(texte, index, depart, len(forme)):
                        propre = True
                        break
                    par_forme[forme] += 1
                    depart = plat.find(forme, depart + 1)
                if propre:
                    break
            if propre:
                break

        if propre:
            propres.append(l)
        elif vu:
            artefacts.append(l)
        else:
            invisibles.append(l)

    n = len(lignes)
    md = [f"# Les artefacts d'aplatissement, mesures — {date.today().isoformat()}",
          "", "Produit par `outils/mesurer_artefacts_aplatissement.py`. "
          "Aucun reseau.", "",
          "L'appariement compare des chaines aplaties — sans accents, sans",
          "espaces. Cela colle les mots voisins et fabrique des chaines absentes",
          "du texte reel : « de la viande frerot » contient « laviandefr ».", "",
          f"- Detections examinees : **{n}**",
          f"- Terme retrouve, **frontiere de mot respectee : {len(propres)}** "
          f"({100*len(propres)/n:.0f} %)",
          f"- Terme retrouve, **a cheval sur un mot — ARTEFACT : "
          f"{len(artefacts)}** ({100*len(artefacts)/n:.0f} %)",
          f"- Terme absent du texte conserve, **inverifiable : "
          f"{len(invisibles)}** ({100*len(invisibles)/n:.0f} %)", "",
          "## Pourquoi « inverifiable » n'est pas « artefact »", "",
          "La moisson ne garde que les 900 premiers caracteres de chaque",
          "description, alors que l'appariement a travaille sur le texte",
          "complet. Quand le terme est au-dela, son absence ici ne prouve rien.",
          "Les compter comme des artefacts multiplierait le chiffre par quatre.",
          ""]

    if artefacts:
        md += ["## Les artefacts trouves", "",
               "| Chaine | Entite | Alias | Titre |", "|---|---|---|---|"]
        for l in artefacts[:60]:
            md += [f"| {l.get('chaine','')[:22]} "
                   f"| {l.get('entites_retenues','')[:22]} "
                   f"| {l.get('alias_reconnus','')[:26]} "
                   f"| {l.get('titre','')[:40]} |"]
        md += ["", "### Formes fautives, par frequence", "",
               "| Forme aplatie | Occurrences |", "|---|---:|"]
        for forme, k in par_forme.most_common(20):
            md += [f"| `{forme}` | {k} |"]
        md += [""]
    else:
        md += ["## Aucun artefact", "",
               "Sur les detections dont le terme est visible, aucune ne mord sur",
               "un mot voisin. **C'est une mesure, pas une garantie** : le",
               "garde-fou reste utile la ou le texte complet est disponible,",
               "comme dans les transcriptions.", ""]

    chemin = RECHERCHE / f"artefacts_aplatissement_{date.today().isoformat()}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:14]))
    print(f"\nEcrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
