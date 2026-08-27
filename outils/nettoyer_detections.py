"""
Retrie les detections de la moisson en separant les preuves fortes du bruit.

LE PROBLEME

La moisson du 24/08 a rendu 1 574 videos « citant la filiere » sur 35 612
examinees. La majorite sont fausses, et la cause est identifiee (JOURNAL 33.4) :
la feuille `Marques` contient des marques dont le nom est un **mot courant du
francais**.

    « Marie » (LDC)          308 detections   le prenom
    « Societe » (Lactalis)   228 detections   le mot
    « President » (Lactalis) 162 detections   le mot
    « Le Foie Gras » (CIFOG)  91 detections   l'aliment

LA REGLE RETENUE

Les deux familles de termes ne se valent pas et ne doivent pas etre traitees
pareil :

  ALIAS D'INTERPROFESSION — `@lesproduitslaitiers`, `@la_viande_fr`, « CNIEL »,
  « Aimez la viande »... Ces chaines sont **specifiques** : elles ne ressemblent
  a rien d'autre en francais. Une occurrence suffit.

  NOMS DE MARQUE — « Herta », « Danone », mais aussi « Marie » et « Societe ».
  Ces chaines peuvent apparaitre par hasard. On exige donc qu'elles
  **co-occurrent avec un indice commercial** : code promo, mention legale,
  lien d'affiliation ou remerciement.

Le raisonnement : une vraie collaboration commerciale laisse presque toujours
une trace commerciale a cote du nom de la marque. Un prenom dans un titre, non.

CE QUE CETTE REGLE COUTE

Elle perd les mentions de marque sans indice commercial — par exemple un
createur qui citerait Danone sans code promo ni lien. Ces cas sont de toute
facon des preuves faibles : ils ne sont pas perdus, ils sont classes a part
et restent consultables dans le fichier de sortie.

Aucun appel reseau : ce script retraite un releve deja enregistre.

Usage :  python outils/nettoyer_detections.py
"""

import csv
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"

# Une entite est une interprofession si elle figure ici. Tout le reste vient
# de la feuille Marques et subit la regle de co-occurrence.
INTERPROFESSIONS = {"CNIEL", "INTERBEV", "INAPORC", "ANVOL", "CNPO", "CIFOG",
                    "CLIPP", "Intercereales", "FNPSMS"}

# Termes hors perimetre viande/lait : gardes pour le groupe temoin, mais
# jamais comptes comme detection de la filiere.
# Ecrite ici comme filet de securite, mais la source de verite est le classeur :
# `perimetre.py` lit les lignes annotees « HORS PERIMETRE » et l'union des deux
# est utilisee. Sans cela, une entite ajoutee au classeur par Vincent resterait
# invisible du code — c'etait deja le cas du CNPO, marque hors perimetre dans
# `cartographie_filiere.xlsx` et absent de cette liste.
ARTICLES_ALIAS = ("les", "le", "la", "l", "des", "de", "du")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from appariement import aplatir_avec_index, coupe_un_mot

HORS_PERIMETRE = {"Intercereales", "FNPSMS"}

try:
    from perimetre import entites_hors_perimetre
    HORS_PERIMETRE = HORS_PERIMETRE | entites_hors_perimetre()
except Exception as _e:          # classeur absent ou illisible : on garde le filet
    print(f"  perimetre.py indisponible ({type(_e).__name__}), "
          f"liste codee en dur utilisee", file=sys.stderr)

# Alias trop courts pour etre apparies sur une forme aplatie.
#
# L'appariement supprime les espaces, ce qui fabrique des mots qui n'existent
# pas : « Clip para » devient « clippara », qui contient « clipp ». Et un sigle
# court se retrouve a l'interieur de mots ordinaires : « noclippant ».
#
# MESURE du 27/08 : l'alias « CLIPP » a produit **31 candidats, zero vrai** —
# pres d'un candidat sur dix de tout le projet. Vincent n'a d'ailleurs trouve
# aucun compte vitrine pour cette interprofession.
#
# Regle : un alias de moins de 8 caracteres n'est pas exploitable par
# appariement aplati. Il faut son compte reel, specifique, pour le detecter.
LONGUEUR_MINIMALE = 8

# Alias generiques dont on sait qu'ils ne designent pas la marque.
# « Le Foie Gras » fait 12 caracteres mais designe l'aliment : 91 candidats,
# zero vrai (JOURNAL 38.2).
ALIAS_ECARTES = {"le foie gras", "foie gras", "clipp", "cnpo", "anvol", "cifog"}


def alias_fiable(alias):
    """Un alias est-il assez specifique pour etre apparie sur forme aplatie ?

    On ECARTE l'ALIAS, jamais l'entite : « ANVOL » est trop court, mais
    « Volaille Francaise » de la meme entite reste exploitable. Premiere
    version de ce correctif : elle excluait l'entite entiere et perdait des
    cas legitimes.
    """
    a = aplatir(alias)
    if a in {aplatir(x) for x in ALIAS_ECARTES}:
        return False
    return len(a) >= LONGUEUR_MINIMALE


# Comptes qui ne sont pas des createurs au sens du projet.
#
# METHODOLOGIE section 8 definit l'influenceur comme « une personne, pas un
# compte de marque ni un media ». Ces comptes etaient pourtant entres dans la
# liste de surveillance par les croisements automatiques : une vitrine de lobby
# suit Le Monde ou Wimbledon comme n'importe quel compte institutionnel.
#
# Ils produisent un bruit massif parce qu'ils parlent legitimement de viande et
# de lait : Le Monde a rendu 92 detections, Le Parisien 52, sur un seul
# passage. Ce ne sont pas des faux positifs de l'appariement — ce sont des
# comptes hors perimetre.
#
# Le tri reste imparfait : un media peut aussi etre remunere par un lobby, et
# ce serait un fait interessant. Mais ce n'est pas la meme enquete, et la
# melanger a celle des createurs noierait les deux.
MEDIAS = {
    "le monde", "le parisien", "le figaro", "liberation", "franceinfo",
    "france 24", "bfmtv", "cnews", "lci", "tf1", "m6", "canal+", "arte",
    "konbini", "brut", "vice", "l'equipe", "lequipe", "20 minutes",
    "ouest-france", "sud ouest", "la depeche", "huffpost", "slate",
    "national geographic", "wimbledon", "olympic games", "olympics",
    "minecraft", "amazon prime video france", "netflix france", "disney+",
    "prime video france", "youtube", "spotify", "deezer",
}


def est_media(nom):
    """Le compte est-il un media ou une plateforme, plutot qu'un createur ?"""
    n = unicodedata.normalize("NFKD", str(nom or "").lower())
    n = "".join(c for c in n if not unicodedata.combining(c)).strip()
    return n in MEDIAS


def aplatir(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def marques_connues():
    """Les noms de marque, pour distinguer ce qui vient de la feuille Marques."""
    import openpyxl
    wb = openpyxl.load_workbook(CARTO / "cartographie_filiere.xlsx",
                                read_only=True, data_only=True)
    noms = set()
    for l in wb["Marques"].iter_rows(min_row=2, values_only=True):
        if l[0]:
            noms.add(str(l[0]).strip())
    wb.close()
    return noms


def artefact_partout(ligne, alias_ok):
    """Toutes les occurrences visibles mordent-elles sur un mot voisin ?

    Rend False si le terme n'est pas visible dans le texte conserve : une
    absence n'est pas une preuve. Voir `appariement.py` pour le detail.
    """
    texte = (ligne.get("titre", "") + " "
             + ligne.get("description", "").replace(" ⏎ ", chr(10)))
    plat, index = aplatir_avec_index(texte)
    vu = False
    for a in alias_ok:
        base = aplatir(a)
        if len(base) < 5:
            continue
        formes = [base]
        for art in ARTICLES_ALIAS:
            if base.startswith(art) and len(base) - len(art) >= 5:
                formes.append(base[len(art):])
        for forme in formes:
            depart = plat.find(forme)
            while depart >= 0:
                vu = True
                if not coupe_un_mot(texte, index, depart, len(forme)):
                    return False          # une occurrence propre suffit
                depart = plat.find(forme, depart + 1)
    return vu


def famille(entite, marques):
    """« interprofession », « marque », ou « hors perimetre »."""
    base = entite.split(" (")[0].strip()
    if base in HORS_PERIMETRE:
        return "hors perimetre"
    if base in INTERPROFESSIONS:
        return "interprofession"
    if base in marques or "(" in entite:
        return "marque"
    return "marque"


def main():
    releves = sorted(RECHERCHE.glob("moisson_videos_*.csv"))
    if not releves:
        print("Aucune moisson trouvee dans recherche/.", file=sys.stderr)
        return 1
    source = releves[-1]
    marques = marques_connues()

    with source.open(encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    print(f"{len(lignes)} detections lues dans {source.name}", file=sys.stderr)

    fortes, faibles, ecartees = [], [], []
    n_artefacts = 0
    for l in lignes:
        entites = [e for e in l["entites_filiere"].split(" | ") if e]
        if not entites:
            continue
        a_un_indice = bool(l.get("indices", "").strip())

        if est_media(l.get("chaine", "")):
            ecartees.append(l)
            continue

        # on ne garde que les alias assez specifiques pour etre fiables
        alias_ok = [a for a in l.get("alias_reconnus", "").split(" | ")
                    if a.strip() and alias_fiable(a)]
        if not alias_ok:
            ecartees.append(l)
            continue

        # Frontiere de mot. L'appariement aplati colle les mots voisins :
        # « viande, frites » devient « viandefr » et declenche @la_viande_fr.
        #
        # MESURE du 27/08 sur les 175 videos jugees : le garde-fou retire
        # 12 candidats, **tous juges « hors sujet » par Vincent, aucun vrai**.
        #
        # On n'ecarte que si le terme est VISIBLE et mord partout sur un mot.
        # La description conservee est tronquee a 900 caracteres : quand le
        # terme est au-dela, son absence ne prouve rien et la ligne passe.
        if artefact_partout(l, alias_ok):
            n_artefacts += 1
            ecartees.append(l)
            continue

        retenues_fortes, retenues_faibles = [], []
        for e in entites:
            f = famille(e, marques)
            if f == "hors perimetre":
                continue

            if f == "interprofession":
                retenues_fortes.append(e)
            elif a_un_indice:
                retenues_faibles.append(e)

        ligne = dict(l)
        if retenues_fortes:
            ligne["entites_retenues"] = " | ".join(sorted(set(retenues_fortes)))
            ligne["force"] = "ALIAS D'INTERPROFESSION"
            fortes.append(ligne)
        elif retenues_faibles:
            ligne["entites_retenues"] = " | ".join(sorted(set(retenues_faibles)))
            ligne["force"] = "marque + indice commercial"
            faibles.append(ligne)
        else:
            ecartees.append(l)

    aujourdhui = date.today().isoformat()
    retenues = fortes + faibles
    if retenues:
        chemin = RECHERCHE / f"detections_nettoyees_{aujourdhui}.csv"
        colonnes = [c for c in retenues[0].keys()]
        with chemin.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=colonnes)
            w.writeheader()
            w.writerows(retenues)

    def par_chaine(groupe):
        d = {}
        for l in groupe:
            cle = (l["chaine"], int(l["abonnes"] or 0))
            d.setdefault(cle, []).append(l)
        return sorted(d.items(), key=lambda x: -x[0][1])

    md = [f"# Detections nettoyees — {aujourdhui}", "",
          "Produit par `outils/nettoyer_detections.py`, sans aucun appel reseau.",
          f"Source : `{source.name}`.", "",
          "## Regle appliquee", "",
          "| Famille | Exigence | Pourquoi |",
          "|---|---|---|",
          "| Alias d'interprofession | une occurrence suffit | `@lesproduitslaitiers` ne ressemble a rien d'autre |",
          "| Nom de marque | **+ un indice commercial** | « Marie » et « Societe » sont des mots courants |",
          "", "## Resultat", "",
          f"- Detections lues : **{len(lignes)}**",
          f"- **Preuves fortes (alias d'interprofession) : {len(fortes)}**",
          f"- Preuves faibles (marque + indice) : {len(faibles)}",
          f"- **Ecartees comme bruit : {len(ecartees)}**",
          f"  - dont artefacts d'aplatissement (« viande, frites » -> "
          f"`viandefr`) : **{n_artefacts}**",
          "", ]
    if lignes:
        md += [f"Le bruit representait **{100*len(ecartees)/len(lignes):.0f} %** "
               f"des detections brutes.", ""]

    md += ["## PREUVES FORTES — par chaine, audience decroissante", "",
           "**A verifier a la main. Une citation n'est pas une collaboration.**", ""]
    for (chaine, ab), vids in par_chaine(fortes):
        md += [f"### {chaine} — {ab:,} abonnes — {len(vids)} video(s)".replace(",", " "),
               "", "| Date | Entite | Titre | URL |", "|---|---|---|---|"]
        for v in sorted(vids, key=lambda x: x["publiee"], reverse=True)[:12]:
            md += [f"| {v['publiee']} | **{v['entites_retenues']}** "
                   f"| {v['titre'][:52]} | {v['url']} |"]
        if len(vids) > 12:
            md += [f"| … | | {len(vids) - 12} autres dans le CSV | |"]
        md += [""]

    if faibles:
        md += ["## PREUVES FAIBLES — marque citee avec un indice commercial", "",
               "| Chaine | Abonnes | Marque | Titre | URL |", "|---|---:|---|---|---|"]
        for l in sorted(faibles, key=lambda x: -int(x["abonnes"] or 0))[:60]:
            md += [f"| {l['chaine'][:20]} | {int(l['abonnes'] or 0):,} "
                   f"| {l['entites_retenues'][:34]} | {l['titre'][:40]} "
                   f"| {l['url']} |".replace(",", " ")]
        md += [""]

    chemin_md = RECHERCHE / f"detections_nettoyees_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:26]))
    print(f"\nEcrit : {chemin_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
