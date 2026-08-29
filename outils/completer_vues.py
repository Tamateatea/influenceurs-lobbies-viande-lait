"""
Complete le jeu de donnees avec le nombre de vues des videos YouTube.

POURQUOI C'EST DANS LE SCHEMA

Vincent l'a demande le 29/08 : le nombre de vues fait partie des colonnes du
jeu de donnees final. C'est ce qui donne la mesure de la **portee** d'une
collaboration — une video vue 33 millions de fois et une vue 3 000 fois ne
disent pas la meme chose du contrat, ni de son effet.

CE QUE CA COUTE

`videos.list` rend jusqu'a 50 videos pour **1 unite de quota**. Les 381 videos
du jeu de donnees coutent donc 8 unites, sur 10 000 par jour. C'est negligeable,
et cela peut tourner a chaque assemblage.

CE QUE LE CHIFFRE VAUT, ET SES LIMITES

Le nombre de vues est celui du jour du releve, pas de la publication. Il monte
avec le temps. La colonne porte donc aussi la date du releve : sans elle, le
chiffre serait ininterpretable dans six mois.

Et il ne vaut que pour YouTube. Instagram, TikTok et Facebook n'exposent pas la
portee d'un contenu par leur API publique — les lignes de ces plateformes
restent vides, et c'est une absence de source, pas un oubli.

Une video supprimee ou passee en prive ne rend rien : sa case reste vide et une
ligne de plus est comptee dans « introuvables ». C'est en soi une information —
un contenu commercial retire est un fait a noter.

Usage :  python outils/completer_vues.py
"""

import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
CACHE = RACINE / "donnees" / "vues_youtube.json"
API = "https://www.googleapis.com/youtube/v3/videos"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ecriture_sure import ecrire_sur

VIDEO = re.compile(r"v=([A-Za-z0-9_-]{11})")


def lire_cle():
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def appel(ids, cle):
    url = API + "?" + urllib.parse.urlencode({
        "part": "statistics", "id": ",".join(ids), "key": cle})
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return None, e.read().decode("utf-8", "replace")[:120]
    except Exception as e:
        return None, type(e).__name__


def main():
    fichiers = sorted(RECHERCHE.glob("dataset_*.csv"))
    if not fichiers:
        print("Aucun dataset_*.csv.", file=sys.stderr)
        return 1
    source = fichiers[-1]
    with source.open(encoding="utf-8") as fh:
        lignes = list(csv.DictReader(fh))
        colonnes = list(lignes[0].keys()) if lignes else []

    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente.", file=sys.stderr)
        return 1

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    ids = {m.group(1) for l in lignes
           if (m := VIDEO.search(l.get("contenu_url", "")))}
    manquants = sorted(ids - set(cache))
    print(f"{len(ids)} videos | {len(manquants)} a interroger", file=sys.stderr)

    depense, introuvables = 0, 0
    for i in range(0, len(manquants), 50):
        lot = manquants[i:i + 50]
        d, err = appel(lot, cle)
        depense += 1
        if err:
            print(f"  arret : {err[:90]}", file=sys.stderr)
            break
        rendus = set()
        for it in d.get("items", []):
            rendus.add(it["id"])
            cache[it["id"]] = it.get("statistics", {}).get("viewCount", "")
        # une video absente de la reponse est supprimee, privee ou geobloquee
        for v in lot:
            if v not in rendus:
                cache[v] = ""
                introuvables += 1
        if i % 500 == 0:
            ecrire_sur(CACHE, json.dumps(cache, ensure_ascii=False))
    ecrire_sur(CACHE, json.dumps(cache, ensure_ascii=False))

    aujourdhui = date.today().isoformat()
    if "date_releve_des_vues" not in colonnes:
        colonnes.insert(colonnes.index("nombre_de_vues") + 1,
                        "date_releve_des_vues")

    remplies = 0
    for l in lignes:
        m = VIDEO.search(l.get("contenu_url", ""))
        vues = cache.get(m.group(1), "") if m else ""
        l["nombre_de_vues"] = vues
        # La date du releve accompagne toujours le chiffre : un nombre de vues
        # sans sa date est ininterpretable, il monte avec le temps.
        l["date_releve_des_vues"] = aujourdhui if vues else ""
        if vues:
            remplies += 1

    with source.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=colonnes)
        w.writeheader()
        w.writerows(lignes)

    chiffres = sorted((int(l["nombre_de_vues"]) for l in lignes
                       if l["nombre_de_vues"].isdigit()), reverse=True)
    md = [f"# Vues des contenus — {aujourdhui}", "",
          "Produit par `outils/completer_vues.py`.", "",
          f"- Videos YouTube du jeu de donnees : **{len(ids)}**",
          f"- Lignes dont les vues sont connues : **{remplies}** sur {len(lignes)}",
          f"- Videos introuvables (supprimees, privees ou geobloquees) : "
          f"**{introuvables}**",
          f"- Quota depense : {depense} unites", "",
          "Les lignes Instagram, TikTok et Facebook restent vides : ces",
          "plateformes n'exposent pas la portee d'un contenu par leur API",
          "publique. C'est une absence de source, pas un oubli.", ""]
    if chiffres:
        total = sum(chiffres)
        md += [f"- **Vues cumulees : {total:,}**".replace(",", " "),
               f"- Mediane : {chiffres[len(chiffres)//2]:,}".replace(",", " "),
               f"- Contenu le plus vu : {chiffres[0]:,}".replace(",", " "), "",
               "Une video vue 33 millions de fois et une vue 3 000 fois ne",
               "disent pas la meme chose du contrat, ni de son effet. C'est",
               "pour ca que la colonne existe.", ""]

    chemin = RECHERCHE / f"vues_{aujourdhui}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
