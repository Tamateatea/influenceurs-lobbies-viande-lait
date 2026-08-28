"""
Re-applique la table d'alias aux videos deja moissonnees, sans quota.

POURQUOI

Quand un alias est ajoute — une campagne trouvee sur un site, un compte
confirme a la main — les videos deja moissonnees ne le connaissent pas : leur
champ `entites_filiere` a ete calcule avec l'ancienne table.

Ce script relit les textes conserves et refait l'appariement avec la table
courante. Aucun appel reseau, aucun quota.

CE QU'IL NE PEUT PAS RATTRAPER, ET C'EST IMPORTANT

La moisson n'enregistre que les videos **portant deja un signal**. Une video
qui n'en portait aucun n'est pas dans le fichier de reprise : un alias nouveau
ne peut donc pas la faire apparaitre.

Autrement dit ce script rattrape les **entites** manquantes sur des videos
deja reperees, pas les **videos** manquantes. Pour celles-la il faut
re-moissonner — environ 5 500 unites de quota sur 2 714 chaines, soit deux
jours.

Et les descriptions conservees sont tronquees a 900 caracteres : un alias
au-dela reste invisible ici.

Usage :  python outils/rescanner_moisson.py
"""

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ETAT = RACINE / "donnees" / "moisson_videos.json"
RECHERCHE = RACINE / "recherche"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import table_alias
from appariement import aplatir_avec_index, coupe_un_mot
from ecriture_sure import ecrire_sur


def main():
    if not ETAT.exists():
        print("Fichier de reprise absent.", file=sys.stderr)
        return 1
    etat = json.loads(ETAT.read_text(encoding="utf-8"))
    termes = table_alias.charger(seuil=5, avec_marques=True,
                                 avec_hors_perimetre=True)
    print(f"{len(termes)} formes d'alias | {len(etat['touchees'])} videos",
          file=sys.stderr)

    nouveaux, par_entite = 0, Counter()
    for v in etat["touchees"]:
        texte = v.get("titre", "") + " " + v.get("description", "").replace(
            " ⏎ ", "\n")
        plat, index = aplatir_avec_index(texte)
        alias, entites = set(), set()
        for forme, (lisible, entite) in termes.items():
            depart = plat.find(forme)
            while depart >= 0:
                # meme garde-fou que partout : une correspondance ne doit pas
                # mordre sur le mot voisin (JOURNAL 60)
                if not coupe_un_mot(texte, index, depart, len(forme)):
                    alias.add(lisible)
                    entites.add(entite)
                    break
                depart = plat.find(forme, depart + 1)
        avant = set(e for e in v.get("entites_filiere", "").split(" | ") if e)
        alias_avant = set(a for a in v.get("alias_reconnus", "").split(" | ") if a)
        if entites - avant:
            nouveaux += 1
            for e in entites - avant:
                par_entite[e] += 1

        # UNION, jamais remplacement. La detection d'origine a travaille sur la
        # description COMPLETE ; ce script ne voit que les 900 premiers
        # caracteres conserves. Remplacer effacerait donc tout ce qui a ete
        # trouve au-dela de la troncature — 42 % des detections (JOURNAL 57.4).
        #
        # Fait une fois le 28/08 : les preuves faibles etaient tombees de 107 a
        # 56 avant que la version precedente ne soit restauree depuis git.
        v["entites_filiere"] = " | ".join(sorted(entites | avant))
        v["alias_reconnus"] = " | ".join(sorted(alias | alias_avant))

    ecrire_sur(ETAT, json.dumps(etat, ensure_ascii=False))

    md = [f"# Re-application de la table d'alias — {date.today().isoformat()}",
          "", "Produit par `outils/rescanner_moisson.py`. Aucun quota.", "",
          f"- Videos relues : **{len(etat['touchees'])}**",
          f"- Videos gagnant une entite : **{nouveaux}**", "",
          "**Limite :** seules les videos portant deja un signal sont dans le",
          "fichier de reprise. Un alias nouveau ne peut pas faire apparaitre une",
          "video qui n'en portait aucun — il faudrait re-moissonner.", "",
          "| Entite gagnee | Videos |", "|---|---:|"]
    for e, n in par_entite.most_common(40):
        md += [f"| {e} | {n} |"]
    chemin = RECHERCHE / f"rescan_alias_{date.today().isoformat()}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:8]))
    print(f"\nEcrit : {chemin.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
