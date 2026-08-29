"""
Trouve les createurs nommes dans les annonces payees par les commanditaires.

POURQUOI C'EST LA MEILLEURE PREUVE DU PROJET

Une annonce de la Meta Ad Library etablit que **l'annonceur a paye Meta pour la
diffuser**. Quand cette annonce nomme un createur, c'est le commanditaire
lui-meme qui publie le lien, et il l'a paye.

C'est un cran au-dessus de tout le reste :

    description YouTube   le createur dit qu'il a un partenaire
    chaine du lobby       le commanditaire nomme le createur
    annonce payee         le commanditaire nomme le createur ET a paye pour

Ce que ca n'etablit toujours pas : que l'argent soit alle **au createur**. Une
marque peut promouvoir un contenu sans avoir remunere celui qui y figure.
Degre de certitude : « lien commercial documente », jamais plus, sauf mention
explicite de partenariat dans le texte.

CE QUE CE SCRIPT CHERCHE

  1. les `@pseudo` ecrits tels quels — le signal le plus sur ;
  2. le vocabulaire de collaboration (« avec », « en partenariat avec »,
     « merci a ») suivi d'un nom propre ;
  3. les comptes deja connus du registre, reconnus dans le texte.

Les trois voies sont **etiquetees separement** : on ne saura ce que chacune
vaut qu'en les faisant juger, comme pour les chaines de lobbies (JOURNAL 55).

Aucun reseau, aucun jeton : relit les CSV deja moissonnes.

Usage :  python outils/createurs_dans_annonces.py
"""

import csv
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir
from medias import est_media

# Un @pseudo credible : au moins 4 caracteres, pas seulement des chiffres.
PSEUDO = re.compile(r"@([A-Za-z][A-Za-z0-9_.]{3,29})")

# Suffixes que les marques ajoutent a leur propre pseudo. Sans eux, le test
# d'auto-mention echoue : « @regilaitfr » n'est pas contenu dans « Regilait »,
# alors que c'est bien la marque qui se cite elle-meme.
SUFFIXES = ("fr", "france", "officiel", "official", "off", "cuisine", "pro",
            "professionnel", "shop", "store", "paris")


def est_l_annonceur(pseudo, page):
    """Le pseudo designe-t-il l'annonceur lui-meme, plutot qu'un createur ?

    DEFAUT CORRIGE LE 29/08, signale par Vincent : « il y a des pseudos comme
    @justinbridou_fr et @legaulois_officiel ou @regilaitfr qui sont clairement
    des marques et pas des createurs ».

    Le test d'origine etait `aplatir(pseudo) in aplatir(page)` — une seule
    direction. « regilaitfr » n'est pas dans « regilait », donc le pseudo
    passait. Il fallait tester les DEUX sens, et retirer les suffixes que les
    marques ajoutent a leur nom.
    """
    p, g = aplatir(pseudo), aplatir(page)
    if not p or not g:
        return False
    for forme in (p, *(p[:-len(s)] for s in SUFFIXES if p.endswith(s) and len(p) > len(s) + 3)):
        if forme and (forme in g or g in forme):
            return True
    return False

COLLABORATION = [
    r"en partenariat avec\s+([A-ZÉÈÀÇ][\wÀ-ÿ'’\-]{2,28})",
    r"avec\s+@?([A-ZÉÈÀÇ][\wÀ-ÿ'’\-]{2,28})",
    r"merci\s+(?:a|à)\s+@?([A-ZÉÈÀÇ][\wÀ-ÿ'’\-]{2,28})",
    r"(?:par|signée?)\s+@?([A-ZÉÈÀÇ][\wÀ-ÿ'’\-]{2,28})",
    r"recette de\s+@?([A-ZÉÈÀÇ][\wÀ-ÿ'’\-]{2,28})",
]

# Mots qui suivent ces motifs sans etre des createurs.
BRUIT = {
    "le", "la", "les", "un", "une", "des", "du", "de", "nos", "notre", "votre",
    "vous", "nous", "france", "noel", "paques", "carrefour", "leclerc",
    "intermarche", "auchan", "lidl", "monoprix", "casino", "super", "hyper",
    "produits", "recette", "recettes", "jeu", "concours", "offre", "promo",
    "nouveau", "nouvelle", "decouvrez", "profitez", "gagnez", "amour",
    # Ajoutes le 27/08 apres mesure : le motif « avec X » attrape des mots
    # courants en debut de phrase. « jour » ressortait 369 fois.
    "jour", "jours", "cette", "cet", "semaine", "semaines", "mois", "annee",
    "matin", "soir", "midi", "entraineur", "chef", "famille", "enfants",
    "amis", "plaisir", "gout", "saveur", "qualite", "origine", "tradition",
    "ete", "hiver", "printemps", "automne", "toute", "tout", "tous", "toutes",
    "plus", "moins", "bien", "beau", "belle", "grand", "grande", "petit",
    "meilleur", "meilleure", "vrai", "vraie", "bon", "bonne", "suzanne",
}

# Le nombre de commanditaires distincts au-dela duquel un « createur » est
# presque surement un mot courant : personne ne travaille pour vingt marques
# concurrentes. Seuil pose apres avoir vu « jour » cite par Activia, Babybel,
# Boursin et Bretons et Engages a la fois.
MAX_COMMANDITAIRES = 6


def comptes_connus():
    """Les comptes du registre, pour reconnaitre un createur deja repere.

    Meme discipline que `moissonner_chaines_lobbies` : on jette toute forme
    revendiquee par plusieurs comptes, sinon on attribue a la mauvaise
    personne (JOURNAL 55).
    """
    f = sorted(RECHERCHE.glob("comptes_consolides_*.csv"))
    if not f:
        return {}
    revendications = defaultdict(dict)
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            ident = l.get("identifiant", "")
            nom = l.get("nom_affiche", "") or l.get("pseudo", "") or ident
            for cle in (l.get("nom_affiche", ""), l.get("pseudo", "")):
                a = aplatir(cle)
                if len(a) >= 8:
                    revendications[a][ident] = nom
    return {a: next(iter(c.values())) for a, c in revendications.items()
            if len(c) == 1}


def main():
    fichiers = sorted(RECHERCHE.glob("meta_pages_*.csv")) + \
        sorted(RECHERCHE.glob("meta_annonces_*.csv"))
    if not fichiers:
        print("Aucun CSV d'annonces Meta.", file=sys.stderr)
        return 1

    connus = comptes_connus()
    print(f"{len(connus)} formes de comptes connus sans ambiguite",
          file=sys.stderr)

    annonces, vus = [], set()
    for f in fichiers:
        with f.open(encoding="utf-8") as fh:
            for l in csv.DictReader(fh):
                aid = l.get("ad_id", "")
                if aid and aid not in vus:
                    vus.add(aid)
                    annonces.append(l)
    print(f"{len(annonces)} annonces distinctes lues dans {len(fichiers)} fichiers",
          file=sys.stderr)

    trouves = []
    for a in annonces:
        texte = (a.get("texte", "") + " " + a.get("titres", "")).replace(" ⏎ ", "\n")
        page = a.get("page_nom") or a.get("page_name", "")
        entite = a.get("entite") or a.get("recherche", "")
        noms = {}

        for m in PSEUDO.finditer(texte):
            p = m.group(1)
            if aplatir(p) in {aplatir(b) for b in BRUIT} or est_media(p):
                continue
            # une page ne se cite pas elle-meme comme createur
            if est_l_annonceur(p, page):
                continue
            noms.setdefault(aplatir(p), ("@" + p, "pseudo ecrit tel quel"))

        for motif in COLLABORATION:
            for m in re.finditer(motif, texte, re.I):
                n = m.group(1).strip(" -–—:|")
                if len(n) < 4 or aplatir(n) in {aplatir(b) for b in BRUIT}:
                    continue
                if est_media(n) or est_l_annonceur(n, page):
                    continue
                noms.setdefault(aplatir(n), (n, "vocabulaire de collaboration"))

        plat = aplatir(texte)
        for forme, nom in connus.items():
            if forme in plat and not est_media(nom):
                noms.setdefault(forme, (nom, "compte connu du registre"))

        def extrait_autour_du_nom(nom_trouve):
            """La fenetre de texte AUTOUR du nom, pas le debut de l'annonce.

            DEFAUT CORRIGE LE 29/08, ET C'EST LE PLUS COUTEUX DU PROJET.

            L'extrait montre a Vincent etait les 300 premiers caracteres de
            l'annonce. Le pseudo du createur, lui, apparait plus loin. Il a donc
            juge 60 lignes en voyant du texte publicitaire de marque SANS AUCUN
            nom de createur visible — et a repondu, logiquement, « c'est la
            marque ».

            J'en ai conclu que le canal avait 0 % de precision et qu'il fallait
            le retirer. **La mesure ne mesurait que ma presentation.**

            @rougemadamestudio est Rouge Madame, alias Alice Bertho, creditee
            par Regilait sur son propre site. @sophiecuisine est dans le
            registre et Vincent l'avait lui-meme arbitree. Ce sont de vraies
            creatrices, jugees « marque » parce qu'on ne les voyait pas.

            C'est la quatrieme fois que ce defaut apparait — extrait qui ne
            contient pas ce qui a declenche la detection. Corrige trois fois
            ailleurs, jamais ici, et ici il a fausse la seule mesure qui
            comptait.
            """
            i = texte.find(nom_trouve)
            if i < 0:
                i = texte.lower().find(nom_trouve.lower().lstrip("@"))
            if i < 0:
                return texte.replace(chr(10), " ")[:400]
            debut = max(0, i - 220)
            return (("..." if debut > 0 else "")
                    + texte[debut:i + 320].replace(chr(10), " ").strip())

        for _cle, (nom, voie) in noms.items():
            trouves.append({
                "createur": nom, "voie": voie, "commanditaire": entite,
                "page_annonceuse": page, "debut_diffusion": a.get("debut", ""),
                "plateformes": a.get("plateformes", ""),
                "ad_id": a.get("ad_id", ""),
                "extrait": extrait_autour_du_nom(nom),
                # L'URL d'apercu Meta n'est consultable que par le detenteur du
                # jeton, et le jeton expire en deux heures : dans un classeur
                # destine a un humain, elle est toujours morte. On donne plutot
                # la page annonceuse, qui elle est publique.
                "page_facebook": f"https://www.facebook.com/{a.get('page_id','')}"
                                 if a.get("page_id") else "",
            })

    aujourdhui = date.today().isoformat()

    par_createur = defaultdict(lambda: {"n": 0, "voies": set(), "pages": set()})
    for t in trouves:
        d = par_createur[t["createur"]]
        d["n"] += 1
        d["voies"].add(t["voie"])
        d["pages"].add(t["page_annonceuse"])

    # Un nom cite par trop de commanditaires differents est un mot courant.
    trop_repandus = {c for c, d in par_createur.items()
                     if len(d["pages"]) > MAX_COMMANDITAIRES
                     and "pseudo ecrit tel quel" not in d["voies"]}
    if trop_repandus:
        print(f"{len(trop_repandus)} noms ecartes : cites par plus de "
              f"{MAX_COMMANDITAIRES} commanditaires, donc mots courants — "
              f"{', '.join(sorted(trop_repandus)[:8])}", file=sys.stderr)
        trouves = [t for t in trouves if t["createur"] not in trop_repandus]
        for c in trop_repandus:
            del par_createur[c]

    # Le CSV s'ecrit APRES le filtrage, sinon il conserve le bruit que le
    # rapport ecarte — et c'est le CSV qui alimente le classeur de Vincent.
    if trouves:
        chemin = RECHERCHE / f"createurs_annonces_{aujourdhui}.csv"
        with chemin.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(trouves[0].keys()))
            w.writeheader()
            w.writerows(trouves)

    voies = defaultdict(int)
    for t in trouves:
        voies[t["voie"]] += 1

    md = [f"# Createurs nommes dans des annonces payees — {aujourdhui}", "",
          "Produit par `outils/createurs_dans_annonces.py`. Aucun reseau.", "",
          "**Une annonce etablit que l'annonceur a paye Meta pour la diffuser.**",
          "Quand elle nomme un createur, le commanditaire publie le lien et l'a",
          "paye. C'est un cran au-dessus d'une mention en description.", "",
          "Ce que ca n'etablit pas : que l'argent soit alle AU CREATEUR. Degre",
          "de certitude « lien commercial documente », pas davantage.", "",
          f"- Annonces examinees : **{len(annonces)}**",
          f"- Mentions de createurs : **{len(trouves)}**",
          f"- Createurs distincts : **{len(par_createur)}**", "",
          "| Voie de detection | Mentions |", "|---|---:|"]
    for v, n in sorted(voies.items(), key=lambda x: -x[1]):
        md += [f"| {v} | {n} |"]
    md += ["", "## Createurs les plus souvent nommes", "",
           "| Createur | Mentions | Commanditaire(s) | Voie |",
           "|---|---:|---|---|"]
    for c, d in sorted(par_createur.items(), key=lambda x: -x[1]["n"])[:60]:
        md += [f"| **{c}** | {d['n']} | {', '.join(sorted(d['pages']))[:52]} "
               f"| {', '.join(sorted(d['voies']))[:40]} |"]

    chemin_md = RECHERCHE / f"createurs_annonces_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:16]))
    print(f"\nEcrit : {chemin_md.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
