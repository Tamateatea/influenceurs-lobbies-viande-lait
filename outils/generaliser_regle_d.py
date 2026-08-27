"""
La regle D tient-elle sur une interprofession qu'on n'avait jamais vue ?

LA QUESTION

La regle D est mesuree a 83 % de precision (JOURNAL 38.3), et c'est sur ce
chiffre que repose le filtrage du projet. Mais elle contient une liste ecrite
a la main :

    GENERIQUES = ["le foie gras", "produits laitiers", "le porc francais",
                  "volaille francaise", "oeufs de france", "la viande", ...]

Chacun de ces termes a ete ajoute **apres avoir vu** les cas de
l'interprofession correspondante. Les 83 % sont donc mesures sur les entites
qui ont servi a la construire.

C'est le defaut classique : un chiffre obtenu sur les donnees d'apprentissage
ne dit rien de ce qui arrivera sur une entite nouvelle. Or le projet doit
resister a l'arrivee de commanditaires qu'on ne connait pas encore —
METHODOLOGIE 14, l'outil re-derive, il ne fige pas.

LE PROTOCOLE : RETIRER UNE ENTITE, PUIS LA TESTER

Pour chaque interprofession E :

  1. on retire de GENERIQUES tous les termes qui designent E ;
  2. on evalue la regle D **uniquement sur les cas de E**.

C'est la situation reelle d'une entite decouverte demain : la liste ne la
connait pas. L'ecart entre ce chiffre et les 83 % annonces est la part de
sur-ajustement.

CE QUI EST PREDIT AVANT DE MESURER

Le rappel ne bougera pas : `est_generique` ne fait qu'ECARTER des cas, donc
retirer des termes ne peut qu'en garder plus. C'est la **precision** qui
tombera, et l'ampleur de la chute dira si la liste est indispensable ou
accessoire.

CE QUI S'EST PASSE — LES DEUX MOITIES DE LA PREDICTION SONT FAUSSES

Le raisonnement sur le rappel etait incoherent avec lui-meme : si retirer un
terme garde plus de cas, le rappel ne peut que monter. Il est passe de 0 a
100 % sur INAPORC.

Et la precision n'est pas tombee, elle est montee : 0 -> 100 % sur INAPORC.
Le terme « le porc francais » n'est pas du bruit, c'est la signature de
campagne d'INAPORC — la liste retirait le seul vrai cas.

La prediction est conservee telle qu'elle a ete ecrite. C'est ce qui rend la
mesure utile : elle avait quelque chose a dementir.

Aucun reseau, aucun quota : tout est deja sur le disque.

Usage :  python outils/generaliser_regle_d.py
"""

import importlib.util
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"


def charger_module():
    spec = importlib.util.spec_from_file_location(
        "ed", RACINE / "outils" / "evaluer_detection.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def lignes_jugees(ed):
    """Les candidats tranches par Vincent, avec leur description."""
    import json
    jugements = ed.charger_jugements()
    candidats = ed.charger_candidats()
    descriptions = {}
    if ed.CACHE.exists():
        descriptions = json.loads(ed.CACHE.read_text(encoding="utf-8"))

    out = []
    for l in candidats:
        verdict = jugements.get((l["chaine"], l["titre"][:40]))
        if not verdict:
            continue
        desc = descriptions.get(l["video_id"]) or l.get("description", "").replace(
            " ⏎ ", "\n")
        out.append({"vrai": verdict == "collaboration remuneree",
                    "entite": l["entites_retenues"], "alias": l["alias_reconnus"],
                    "description": desc, "chaine": l["chaine"],
                    "titre": l["titre"], "url": l["url"]})
    return out


def regle_d(ligne, ed, generiques):
    """Regle D, mais avec la liste de generiques qu'on lui donne."""
    if not ed.voisinage_proche(ligne["description"], ligne["alias"]):
        return False
    a = ed.sans_accent(ligne["alias"]).lstrip("@").replace("_", " ").strip()
    est_gen = any(a == g for g in generiques)
    return not (est_gen and "@" not in ligne["alias"])


def scores(lignes, ed, generiques):
    retenus = [l for l in lignes if regle_d(l, ed, generiques)]
    vp = sum(1 for l in retenus if l["vrai"])
    total = sum(1 for l in lignes if l["vrai"])
    return (len(retenus), vp,
            100 * vp / len(retenus) if retenus else 0.0,
            100 * vp / total if total else 0.0, total)


def entite_principale(brut):
    """Une detection peut citer plusieurs entites ; on prend la premiere."""
    return (brut or "").split(" | ")[0].strip() or "(sans entite)"


def main():
    ed = charger_module()
    lignes = lignes_jugees(ed)
    if not lignes:
        print("Aucune ligne jugee.", file=sys.stderr)
        return 1
    print(f"{len(lignes)} lignes jugees | GENERIQUES : {len(ed.GENERIQUES)} termes",
          file=sys.stderr)

    par_entite = defaultdict(list)
    for l in lignes:
        par_entite[entite_principale(l["entite"])].append(l)

    # Quels termes de GENERIQUES appartiennent a quelle entite ? On le deduit
    # des donnees plutot que de le re-ecrire a la main : un terme appartient a
    # l'entite dont il etiquette les alias.
    terme_de = defaultdict(set)
    for l in lignes:
        a = ed.sans_accent(l["alias"]).lstrip("@").replace("_", " ").strip()
        for g in ed.GENERIQUES:
            if a == g:
                terme_de[g].add(entite_principale(l["entite"]))

    resultats = []
    for entite, cas in sorted(par_entite.items(), key=lambda x: -len(x[1])):
        vrais = sum(1 for l in cas if l["vrai"])
        if vrais == 0:
            continue
        sans = [g for g in ed.GENERIQUES if entite not in terme_de.get(g, set())]
        retires = [g for g in ed.GENERIQUES if entite in terme_de.get(g, set())]
        av = scores(cas, ed, ed.GENERIQUES)
        ap = scores(cas, ed, sans)
        resultats.append({"entite": entite, "cas": len(cas), "vrais": vrais,
                          "retires": retires, "avant": av, "apres": ap})

    md = [f"# La regle D tient-elle sur une entite jamais vue ? — "
          f"{date.today().isoformat()}", "",
          "Produit par `outils/generaliser_regle_d.py`. Aucun reseau.", "",
          "La regle D contient une liste d'alias « generiques » ecrite a la main,",
          "terme par terme, **apres** avoir vu les cas de chaque interprofession.",
          "Les 83 % annonces sont donc mesures sur ce qui a servi a la construire.",
          "",
          "Ici, pour chaque entite, on retire de la liste les termes qui la",
          "designent, puis on la teste. C'est la situation d'un commanditaire",
          "decouvert demain.", "",
          "| Entite | Cas | Vrais | Termes retires | Precision avec | sans | Rappel avec | sans |",
          "|---|---:|---:|---|---:|---:|---:|---:|"]
    for r in resultats:
        av, ap = r["avant"], r["apres"]
        md += [f"| **{r['entite'][:26]}** | {r['cas']} | {r['vrais']} "
               f"| {', '.join(r['retires']) or '—'} "
               f"| {av[2]:.0f} % | {ap[2]:.0f} % | {av[3]:.0f} % | {ap[3]:.0f} % |"]

    concernes = [r for r in resultats if r["retires"]]
    md += ["", "## Ce que ca dit", ""]
    if not concernes:
        md += ["Aucune entite du jeu juge n'est designee par un terme de la liste.",
               "**La mesure ne peut donc pas conclure** : il faudrait des cas",
               "portant precisement ces alias generiques. C'est un resultat nul",
               "de protocole, pas un blanc-seing pour la regle D.", ""]
    else:
        # Le signe n'est pas suppose : on le lit. Une premiere version de ce
        # rapport annoncait « chute de precision » quel que soit le resultat,
        # et affirmait donc le contraire de ses propres chiffres.
        ecarts = {r["entite"]: r["apres"][2] - r["avant"][2] for r in concernes}
        gagnantes = [e for e, d in ecarts.items() if d > 0.5]
        perdantes = [e for e, d in ecarts.items() if d < -0.5]
        plus_grand = max(concernes, key=lambda r: abs(ecarts[r["entite"]]))
        d = ecarts[plus_grand["entite"]]

        md += [f"{len(concernes)} entites du jeu juge sont designees par un terme",
               "de la liste. Retirer ce terme — c'est-a-dire faire comme si on",
               "n'avait jamais vu l'entite — donne :", "",
               f"- precision **amelioree** pour : {', '.join(gagnantes) or 'aucune'}",
               f"- precision **degradee** pour : {', '.join(perdantes) or 'aucune'}",
               "", f"Ecart le plus fort : **{plus_grand['entite']}**, "
               f"{plus_grand['avant'][2]:.0f} % -> {plus_grand['apres'][2]:.0f} % "
               f"de precision et {plus_grand['avant'][3]:.0f} % -> "
               f"{plus_grand['apres'][3]:.0f} % de rappel.", ""]

        if gagnantes and not perdantes:
            md += ["**Le resultat va dans le sens inverse de ce qui etait predit**,",
                   "et c'est le fait marquant de cette mesure.", "",
                   "La liste des generiques a ete concue pour retirer du bruit. Sur",
                   "les entites autres que le CNIEL, elle retire du **signal** : le",
                   "terme dit « generique » y est precisement l'alias sous lequel",
                   "l'interprofession fait campagne. « Le Porc Francais » n'est pas",
                   "une categorie alimentaire qui traine dans une description, c'est",
                   "la signature d'INAPORC.", "",
                   "Ce n'est donc pas que la regle D **generalise mal** faute d'avoir",
                   "vu l'entite. C'est qu'elle generalise mieux quand on ne lui a",
                   "rien appris de l'entite. La liste, ecrite en regardant le CNIEL,",
                   "**nuit** ailleurs.", "",
                   "Ce que ca implique, et qui reste a trancher par Vincent : soit on",
                   "restreint `est_generique` au CNIEL, soit on l'abandonne au profit",
                   "de la regle F, qui exige un @pseudo ecrit tel quel et ne depend",
                   "d'aucune liste manuelle.", ""]
        elif perdantes and not gagnantes:
            md += ["Le sens predit est confirme : sans ses termes, la regle D perd",
                   "de la precision sur une entite nouvelle. **C'est le prix a payer",
                   "a chaque nouveau commanditaire**, jusqu'a ce que quelqu'un ajoute",
                   "ses termes a la main.", "",
                   "Cette liste est donc une dette : tant qu'elle est ecrite a la",
                   "main, l'outil ne « re-derive » pas au sens de METHODOLOGIE 14,",
                   "il attend qu'on le mette a jour.", ""]
        else:
            md += ["Le resultat est mixte : la liste aide certaines entites et en",
                   "penalise d'autres. Sur un jeu aussi petit, **cela ne tranche",
                   "rien** — il faut plus de cas juges hors CNIEL avant de decider.",
                   ""]

    md += ["## Limite de cette mesure", "",
           "Le jeu juge est petit et tres deseque vers le CNIEL. Les entites a",
           "deux ou trois cas donnent des pourcentages qu'il ne faut pas lire",
           "comme des taux. Ce tableau montre un SENS, pas des valeurs.", ""]

    chemin = RECHERCHE / f"generalisation_regle_d_{date.today().isoformat()}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nEcrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
