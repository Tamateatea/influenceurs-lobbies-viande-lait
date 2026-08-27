"""
Moissonne les chaines YouTube des lobbies eux-memes.

POURQUOI C'EST LA MEILLEURE SOURCE DU PROJET

Toutes les autres methodes partent du contenu d'un createur et **inferent**
qu'un lobby l'a paye. Ici, c'est le lobby qui publie. Un createur nomme dans
le titre d'une video publiee par le CNIEL n'est pas une hypothese : c'est le
commanditaire qui l'annonce.

Trouve par Vincent le 27/08 en parcourant produits-laitiers.com : la serie
LAIT'FLIX, avec des playlists nommees « ON DEVIENT FERMIER 48H DANS LES
MONTAGNES Feat Inoxtag », « Mister V : les copains au lait », « Billy et Amine
decouvrent les specialites de nos regions ».

Sa reaction, qui dit l'enjeu : « Certaines de ces series sont des videos que je
connaissais et qui ont ete beaucoup vues, et je ne savais pas qu'elles avaient
ete financees par le lobby du lait. »

CE QUE CE SCRIPT FAIT

Il recupere le catalogue complet de chaque chaine de lobby et en extrait les
noms de createurs, par deux voies :

  1. les motifs explicites — « feat X », « avec X », « ft. X », « X : titre » ;
  2. le rapprochement avec les comptes deja connus du registre.

CE QU'IL NE FAIT PAS

Il ne dit pas si le createur a ete **remunere**. Apparaitre dans une video du
CNIEL etablit une collaboration, pas son caractere onereux — c'est le champ
`degre de certitude` de METHODOLOGIE section 1.

UNE ERREUR CORRIGEE LE 27/08 — A NE PAS REINTRODUIRE

La premiere version rapprochait un titre des comptes connus des que **six
caracteres** correspondaient, et renvoyait l'identifiant du PREMIER compte
ayant revendique cette forme. « Morgan VS » dans un titre INTERBEV etait donc
attribue a `morganabbou` — quelqu'un d'autre.

Dans un repertoire public, ce n'est pas du bruit : c'est mettre en cause la
mauvaise personne. Trois garde-fous depuis :

  1. **huit caracteres minimum**, la regle deja retenue pour les alias ;
  2. **toute forme revendiquee par plusieurs comptes est jetee** — c'est elle
     qui produisait la mauvaise attribution, pas sa longueur ;
  3. on affiche le **nom lisible** et la **chaine exacte qui a declenche**, pour
     qu'un humain puisse contredire l'outil d'un coup d'oeil.

Les comptes des lobbies eux-memes sont exclus : `volaillefrancaise` se
reconnaissait dans ses propres titres, 36 fois.

Cout : environ 3 unites de quota par chaine. Negligeable.

Usage :  python outils/moissonner_chaines_lobbies.py
"""

import csv
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
API = "https://www.googleapis.com/youtube/v3/"

# Chaines officielles des interprofessions, trouvees par Vincent le 27/08.
CHAINES = {
    "laitflixetproduitslaitiers": ("CNIEL", "lesproduitslaitiers"),
    "aimezlaviande": ("INTERBEV", "la_viande_fr"),
    "naturellementflexitariens": ("INTERBEV", "NaturellementFlexitariens"),
    "volaillefrancaise": ("ANVOL", "volaillefrancaise8086"),
    "lefoiegras": ("CIFOG", "LeFoieGrasFrance"),
    "interbevnouvelleaquitaine": ("INTERBEV", "interbevnouvelle-aquitaine7800"),
}

# Motifs qui nomment un createur dans un titre de video.
MOTIFS = [
    r"\bfeat\.?\s+([A-Z][\w'’\- ]{2,28})",
    r"\bft\.?\s+([A-Z][\w'’\- ]{2,28})",
    r"\bavec\s+([A-Z][\w'’\- ]{2,28})",
    r"^([A-Z][\w'’\- ]{2,24})\s*[:|-]\s",
    r"\bpar\s+([A-Z][\w'’\- ]{2,28})",
    r"\bx\s+([A-Z][\w'’\- ]{2,28})",
]

LONGUEUR_MINIMALE = 8      # meme regle que pour les alias (JOURNAL 27/08)

# Medias et plateformes : ils apparaissent dans ces titres sans etre des
# createurs remuneres. Meme liste que nettoyer_detections.py.
# La liste vit dans la feuille « Medias » de cartographie_filiere.xlsx depuis
# le 27/08 : Vincent doit pouvoir l'amender sans passer par le code. Elle etait
# ici en dur, et en deux copies qui avaient commence a diverger.
from medias import est_media


# Mots qui suivent ces motifs sans etre des createurs.
BRUIT = {"le", "la", "les", "un", "une", "des", "nos", "notre", "votre", "mon",
         "ma", "ce", "cette", "il", "elle", "on", "vous", "nous", "france",
         "produits", "lait", "viande", "recette", "episode", "partie", "saison"}


def aplatir(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def lire_cle():
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def appel(endpoint, params, cle):
    url = API + endpoint + "?" + urllib.parse.urlencode(dict(params, key=cle))
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code} — {e.read()[:140].decode('utf-8', 'replace')}"
    except Exception as e:
        return None, type(e).__name__


def comptes_connus():
    """Formes reconnaissables -> compte, en ne gardant que les SANS AMBIGUITE.

    Une forme revendiquee par plusieurs comptes distincts est ecartee : c'est
    elle qui faisait attribuer « Morgan VS » a `morganabbou` (voir l'en-tete).
    """
    f = sorted(RECHERCHE.glob("comptes_consolides_*.csv"))
    if not f:
        return {}
    revendications = {}
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            ident = l.get("identifiant", "")
            nom = l.get("nom_affiche", "") or l.get("pseudo", "") or ident
            for cle in (ident, l.get("nom_affiche", ""), l.get("pseudo", "")):
                a = aplatir(cle)
                if len(a) < LONGUEUR_MINIMALE:
                    continue
                revendications.setdefault(a, {})[ident] = (
                    nom, l.get("audience", ""), str(cle))

    out, jetees = {}, 0
    for a, comptes in revendications.items():
        if len(comptes) > 1:          # plusieurs personnes portent cette forme
            jetees += 1
            continue
        ident, (nom, audience, source) = next(iter(comptes.items()))
        out[a] = {"identifiant": ident, "nom": nom, "audience": audience,
                  "source": source}
    print(f"{len(out)} formes sans ambiguite, {jetees} ecartees comme partagees",
          file=sys.stderr)
    return out


def createurs_du_titre(titre, connus, comptes_lobby):
    """Createurs nommes, avec la trace de ce qui a declenche la reconnaissance.

    Rend une liste de dictionnaires : nom lisible, identifiant, et `via` — la
    chaine exacte reconnue, pour qu'un humain puisse verifier sans relire le
    code.
    """
    trouves = {}
    for m in MOTIFS:
        for c in re.findall(m, titre):
            nom = c.strip(" -–—:|")
            plat = aplatir(nom)
            if len(nom) < 3 or plat in {aplatir(b) for b in BRUIT}:
                continue
            if plat in comptes_lobby or est_media(nom):
                continue
            trouves.setdefault(plat, {"nom": nom, "identifiant": "",
                                      "via": "motif dans le titre"})

    plat_titre = aplatir(titre)
    for a, d in connus.items():
        if a in comptes_lobby or a not in plat_titre:
            continue
        if est_media(d["nom"]):
            continue
        trouves[a] = {"nom": d["nom"], "identifiant": d["identifiant"],
                      "via": f"compte connu, reconnu sur « {d['source']} »"}
    return list(trouves.values())


def main():
    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente.", file=sys.stderr)
        return 1
    connus = comptes_connus()

    # Les lobbies se reconnaissent dans leurs propres titres : `volaillefrancaise`
    # ressortait 36 fois comme « createur nomme par ANVOL ».
    comptes_lobby = set()
    for pseudo, (entite, _p) in [(v[1], (k, v)) for k, v in CHAINES.items()]:
        comptes_lobby.add(aplatir(pseudo))
    for nom_court, (entite, pseudo) in CHAINES.items():
        comptes_lobby.add(aplatir(nom_court))
        comptes_lobby.add(aplatir(pseudo))
        comptes_lobby.add(aplatir(entite))
    comptes_lobby |= {aplatir(x) for x in
                      ("laviande.fr", "la_viande_fr", "lesproduitslaitiers",
                       "produits laitiers", "Le Foie Gras", "Le Foie Gras en Reels",
                       "volaillissimes", "Naturellement Flexitariens")}
    comptes_lobby.discard("")

    lignes, depense = [], 0
    for nom_court, (entite, pseudo) in CHAINES.items():
        d, err = appel("channels", {"part": "snippet,contentDetails,statistics",
                                    "forHandle": pseudo}, cle)
        depense += 1
        if err or not d.get("items"):
            print(f"  {pseudo:34s} introuvable {err or ''}", file=sys.stderr)
            continue
        it = d["items"][0]
        up = it["contentDetails"]["relatedPlaylists"]["uploads"]
        titre_chaine = it["snippet"]["title"]
        abonnes = it.get("statistics", {}).get("subscriberCount", "")

        page, n = None, 0
        while True:
            p = {"part": "snippet", "playlistId": up, "maxResults": 50}
            if page:
                p["pageToken"] = page
            d, err = appel("playlistItems", p, cle)
            depense += 1
            if err:
                print(f"  {pseudo} : {err}", file=sys.stderr)
                break
            for item in d.get("items", []):
                s = item["snippet"]
                vid = s.get("resourceId", {}).get("videoId", "")
                if not vid:
                    continue
                n += 1
                titre = s.get("title", "")
                desc = (s.get("description", "") or "")
                noms = createurs_du_titre(titre + " " + desc[:300], connus,
                                          comptes_lobby)
                if noms:
                    lignes.append({
                        "entite": entite,
                        "chaine_lobby": titre_chaine,
                        "abonnes_lobby": abonnes,
                        "createurs_nommes": " | ".join(n["nom"] for n in noms),
                        "identifiants": " | ".join(n["identifiant"] for n in noms),
                        "reconnu_par": " | ".join(n["via"] for n in noms),
                        "titre": titre[:150],
                        "publiee": (s.get("publishedAt") or "")[:10],
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "description": desc.replace("\n", " ⏎ ")[:600],
                        "releve_le": date.today().isoformat(),
                    })
            page = d.get("nextPageToken")
            if not page:
                break
        print(f"  {titre_chaine[:30]:32s} {n:>4d} videos | "
              f"{sum(1 for l in lignes if l['chaine_lobby'] == titre_chaine)} "
              f"nommant un createur", file=sys.stderr)

    aujourdhui = date.today().isoformat()
    if lignes:
        chemin = RECHERCHE / f"chaines_lobbies_{aujourdhui}.csv"
        with chemin.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)

    par_createur = {}
    for l in lignes:
        for c, via in zip(l["createurs_nommes"].split(" | "),
                          l["reconnu_par"].split(" | ")):
            d = par_createur.setdefault(c, {"n": 0, "entites": set(), "via": via})
            d["n"] += 1
            d["entites"].add(l["entite"])

    md = [f"# Createurs nommes par les chaines des lobbies — {aujourdhui}", "",
          "Produit par `outils/moissonner_chaines_lobbies.py`.", "",
          "**Ces videos sont publiees par les lobbies eux-memes.** Un createur",
          "nomme dans un titre n'est pas une inference : c'est le commanditaire",
          "qui l'annonce.", "",
          "Reserve : cela etablit une collaboration, **pas sa remuneration**.", "",
          "Colonne « reconnu par » : ce qui a declenche la reconnaissance. Les",
          "formes de moins de huit caracteres et celles que plusieurs comptes",
          "revendiquent sont ecartees — elles attribuaient les videos a la",
          "mauvaise personne (voir l'en-tete du script).", "",
          f"- Videos nommant un createur : **{len(lignes)}**",
          f"- Createurs distincts : **{len(par_createur)}**",
          f"- Quota depense : {depense} unites", "",
          "| Createur | Videos | Commanditaire(s) | Reconnu par |",
          "|---|---:|---|---|"]
    for c, d in sorted(par_createur.items(), key=lambda x: -x[1]["n"])[:80]:
        md += [f"| **{c}** | {d['n']} | {', '.join(sorted(d['entites']))} "
               f"| {d['via'][:52]} |"]

    chemin_md = RECHERCHE / f"chaines_lobbies_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:12]))
    print(f"\nEcrit : {chemin_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
