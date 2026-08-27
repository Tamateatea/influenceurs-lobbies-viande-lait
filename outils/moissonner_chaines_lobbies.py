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
    """Les comptes du registre, pour reconnaitre un createur deja repere."""
    f = sorted(RECHERCHE.glob("comptes_consolides_*.csv"))
    if not f:
        return {}
    out = {}
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            for cle in (l.get("identifiant", ""), l.get("nom_affiche", ""),
                        l.get("pseudo", "")):
                a = aplatir(cle)
                if len(a) >= 5:
                    out.setdefault(a, l.get("identifiant", cle))
    return out


def createurs_du_titre(titre, connus):
    """Noms extraits par motif, plus reconnaissance des comptes connus."""
    trouves = set()
    for m in MOTIFS:
        for c in re.findall(m, titre):
            nom = c.strip(" -–—:|")
            if len(nom) < 3 or aplatir(nom) in {aplatir(b) for b in BRUIT}:
                continue
            trouves.add(nom)
    plat = aplatir(titre)
    for a, lisible in connus.items():
        if len(a) >= 6 and a in plat:
            trouves.add(lisible)
    return sorted(trouves)


def main():
    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente.", file=sys.stderr)
        return 1
    connus = comptes_connus()
    print(f"{len(connus)} formes connues du registre", file=sys.stderr)

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
                noms = createurs_du_titre(titre + " " + desc[:300], connus)
                if noms:
                    lignes.append({
                        "entite": entite,
                        "chaine_lobby": titre_chaine,
                        "abonnes_lobby": abonnes,
                        "createurs_nommes": " | ".join(noms),
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
        for c in l["createurs_nommes"].split(" | "):
            d = par_createur.setdefault(c, {"n": 0, "entites": set()})
            d["n"] += 1
            d["entites"].add(l["entite"])

    md = [f"# Createurs nommes par les chaines des lobbies — {aujourdhui}", "",
          "Produit par `outils/moissonner_chaines_lobbies.py`.", "",
          "**Ces videos sont publiees par les lobbies eux-memes.** Un createur",
          "nomme dans un titre n'est pas une inference : c'est le commanditaire",
          "qui l'annonce.", "",
          "Reserve : cela etablit une collaboration, **pas sa remuneration**.", "",
          f"- Videos nommant un createur : **{len(lignes)}**",
          f"- Createurs distincts : **{len(par_createur)}**",
          f"- Quota depense : {depense} unites", "",
          "| Createur | Videos | Commanditaire(s) |", "|---|---:|---|"]
    for c, d in sorted(par_createur.items(), key=lambda x: -x[1]["n"])[:80]:
        md += [f"| **{c}** | {d['n']} | {', '.join(sorted(d['entites']))} |"]

    chemin_md = RECHERCHE / f"chaines_lobbies_{aujourdhui}.md"
    chemin_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:12]))
    print(f"\nEcrit : {chemin_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
