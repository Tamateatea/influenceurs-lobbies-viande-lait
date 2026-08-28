"""
Applique la transcription aux chaines dont une collaboration est deja etablie.

D'OU VIENT CETTE STRATEGIE

Mesure du 27/08 (JOURNAL 53) : sur 37 videos **sans aucun signal en
description**, prises sur des chaines connues pour collaborer, une porte une
mention orale que rien d'autre ne voyait — Inoxtag 2.0, « comme d'habitude les
produits laitiers qui nous accompagnent partout ».

La transcription voit donc ce que la description tait. Mais elle coute
plusieurs secondes par video : sur 2 600 chaines et 300 000 videos, c'est hors
de portee.

D'ou le **second rideau** : on ne transcrit pas au hasard, on transcrit les
chaines ou l'on sait deja qu'il y a quelque chose. Une collaboration est
rarement unique — « comme d'habitude » le dit assez — et c'est la que le
rendement est le meilleur.

CE QUE CA COUTE

Quota d'API : une unite par tranche de 50 videos, pour lister les catalogues.
Quelques dizaines d'unites en tout.

Temps : quelques secondes par video, sans quota. C'est la contrainte reelle.

CE QUE CA NE PROUVE PAS

Une mention orale n'etablit pas la remuneration. « Les produits laitiers qui
nous accompagnent » peut designer un partenariat, une dotation en produits ou
une simple habitude. Tout ce qui sort d'ici va en verification humaine avec le
degre « lien commercial documente », jamais « remuneration confirmee ».

Et le faux positif oral existe : « cette video est sponsorisee par Odica »
etait une blague sur des appareils auditifs (JOURNAL 20.4).

Usage :
    python outils/second_rideau_transcription.py --videos 250
"""

import argparse
import csv
import importlib.util
import json
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"
CACHE = RACINE / "donnees" / "transcriptions_second_rideau.json"
# La liste des videos a transcrire est elle aussi mise en cache. Voir
# `liste_temoins` : sans cela, ce script ne peut rien faire quand le quota
# YouTube est epuise, alors que transcrire n'en consomme aucun.
TEMOINS = RACINE / "donnees" / "temoins_second_rideau.json"
API = "https://www.googleapis.com/youtube/v3/"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ecriture_sure import ecrire_sur
import table_alias


def aplatir_avec_index(texte):
    """Texte aplati, et la correspondance vers les positions d'origine.

    `aplatir` supprime accents, espaces et ponctuation. Une position dans le
    texte aplati ne designe donc PAS la meme chose dans le texte d'origine, et
    l'ecart grandit a mesure qu'on avance. Couper l'extrait a la position
    aplatie affiche un passage sans rapport — fait deux fois le 27/08, dont une
    fois en presentant le resultat a Vincent.
    """
    import unicodedata
    plat, index = [], []
    for position, caractere in enumerate(texte):
        c = unicodedata.normalize("NFKD", caractere)
        c = "".join(x for x in c if not unicodedata.combining(x)).lower()
        for lettre in c:
            if lettre.isalnum():
                plat.append(lettre)
                index.append(position)
    return "".join(plat), index


def coupe_un_mot(texte, index, debut_plat, longueur):
    """La correspondance s'arrete-t-elle au milieu d'un mot du texte d'origine ?

    MESURE du 27/08 : « je te ramene du charbon et de **la viande frerot** »
    a declenche l'alias `laviandefr` — l'aplatissement colle les mots, et
    « la viande frerot » devient « laviandefrerot », qui contient « laviandefr ».

    Le texte aplati a perdu les espaces, donc on ne peut pas y voir la coupure.
    Mais l'index rend les positions d'origine : il suffit de regarder le
    caractere qui suit immediatement la correspondance dans le texte VRAI. S'il
    est alphanumerique, la correspondance mord sur le mot suivant, et c'est un
    artefact.

    Meme raisonnement en amont, pour un alias qui commencerait au milieu d'un
    mot.
    """
    if debut_plat >= len(index):
        return True
    fin_plat = debut_plat + longueur - 1
    if fin_plat >= len(index):
        return True
    apres = index[fin_plat] + 1
    if apres < len(texte) and texte[apres].isalnum():
        return True
    avant = index[debut_plat] - 1
    if avant >= 0 and texte[avant].isalnum():
        return True
    return False


def charger(nom):
    spec = importlib.util.spec_from_file_location(
        nom, RACINE / "outils" / f"{nom}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def lire_cle():
    import re
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def appel(endpoint, params, cle):
    url = API + endpoint + "?" + urllib.parse.urlencode(dict(params, key=cle))
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            return json.loads(r.read().decode("utf-8")), None
    except Exception as e:
        return None, str(e)[:120]


def chaines_confirmees(inclure_preuves_fortes=False):
    """Les chaines ou une collaboration est etablie.

    Par defaut : celles ou Vincent a confirme une collaboration remuneree —
    11 chaines, le noyau le plus sur.

    Avec `inclure_preuves_fortes` : on y ajoute les chaines portant une preuve
    forte non encore jugee — 36 en tout. Moins sur, mais c'est le bon reglage
    pour un tour de nuit : la transcription ne coute que du temps, et une nuit
    entiere sur 11 chaines serait du gachis.
    """
    import openpyxl
    juges = {}
    for f in sorted(CARTO.glob("A_VERIFIER*.xlsx")):
        try:
            ws = openpyxl.load_workbook(f, data_only=True)["a verifier"]
        except Exception:
            continue
        entetes = [str(c.value or "") for c in ws[1]]
        col = next((i for i, h in enumerate(entetes) if "VERDICT" in h.upper()),
                   None)
        if col is None:
            continue
        for r in ws.iter_rows(min_row=2, values_only=True):
            if col < len(r) and r[col]:
                juges[(str(r[1]), str(r[5])[:40])] = str(r[col])

    fichiers = sorted(RECHERCHE.glob("moisson_videos_*.csv"))
    if not fichiers:
        return {}
    fortes = set()
    if inclure_preuves_fortes:
        nettoyees = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))
        if nettoyees:
            with nettoyees[-1].open(encoding="utf-8") as fh:
                fortes = {l["chaine"] for l in csv.DictReader(fh)
                          if l.get("force", "").startswith("ALIAS")}
    out = {}
    with fichiers[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            confirmee = juges.get((l["chaine"], l["titre"][:40])) ==                 "collaboration remuneree"
            if confirmee or l["chaine"] in fortes:
                out[l["channel_id"]] = l["chaine"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", type=int, default=250,
                    help="plafond de videos a transcrire ; c'est le temps qui")
    ap.add_argument("--par-chaine", type=int, default=100)
    ap.add_argument("--preuves-fortes", action="store_true",
                    help="elargir aux chaines a preuve forte non encore jugees ; "
                         "reglage du tour de nuit")
    args = ap.parse_args()

    mt = charger("mesurer_transcriptions")

    # PAS DE MARQUES ICI — et c'est desormais un choix mesure.
    #
    # Le chargeur herite jusqu'au 27/08 ne lisait pas la feuille `Marques`, sans
    # que personne ne l'ait decide. En centralisant les chargeurs, les marques
    # ont ete ajoutees ici : cela paraissait une correction.
    #
    # MESURE, sur les 236 memes transcriptions : **5 detections deviennent 57**,
    # et la quasi-totalite du surplus porte sur « marie », « societe »,
    # « president », « gaulois », « veloute », « tartare ». Ce sont des mots
    # ordinaires du francais parle, pas des mentions de marque.
    #
    # La frontiere de mot n'y peut rien : ce SONT des mots entiers. Et le
    # garde-fou qui protege les descriptions — exiger un indice commercial a
    # cote de la marque — n'existe pas pour l'oral, ou personne ne dit
    # « communication commerciale ».
    #
    # Les interprofessions, elles, ont des noms qu'on ne prononce pas par
    # hasard : « les produits laitiers », « le porc francais ».
    termes = table_alias.charger(seuil=8, avec_marques=False,
                                 avec_hors_perimetre=False)
    print(f"{len(termes)} formes d'alias, interprofessions seules",
          file=sys.stderr)
    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente.", file=sys.stderr)
        return 1

    cibles = chaines_confirmees(args.preuves_fortes)
    if not cibles:
        print("Aucune chaine confirmee — rien a faire.", file=sys.stderr)
        return 1
    print(f"{len(cibles)} chaines avec une collaboration confirmee | "
          f"{len(termes)} formes d'alias", file=sys.stderr)

    # --- 1) lister leurs videos SANS signal en description ---
    #
    # DEFAUT CORRIGE LE 28/08. Lister un catalogue coute du quota, alors que
    # transcrire n'en coute aucun. La nuit du 27 au 28, la moisson avait epuise
    # le quota avant que ce script ne tourne : il n'a pu lister aucune chaine,
    # donc n'a transcrit aucune video. Le travail de nuit le plus utile — le
    # seul gratuit — n'a rien produit.
    #
    # La liste est desormais conservee. Une fois etablie, les nuits suivantes
    # transcrivent sans toucher a l'API.
    deja = json.loads(TEMOINS.read_text(encoding="utf-8")) if TEMOINS.exists() else []
    cache_liste = {t["video_id"]: t for t in deja}

    temoins, depense = list(deja), 0
    for cid, nom in cibles.items():
        d, err = appel("channels", {"part": "contentDetails", "id": cid}, cle)
        depense += 1
        if err or not d.get("items"):
            # Quota epuise : on continue avec la liste deja connue plutot que
            # de ne rien faire. C'est tout l'interet de l'avoir conservee.
            print(f"  {nom} : catalogue non liste ({str(err)[:50]})",
                  file=sys.stderr)
            continue
        up = d["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        page, pris = None, 0
        while pris < args.par_chaine:
            p = {"part": "snippet", "playlistId": up, "maxResults": 50}
            if page:
                p["pageToken"] = page
            d, err = appel("playlistItems", p, cle)
            depense += 1
            if err:
                break
            for it in d.get("items", []):
                s = it["snippet"]
                vid = s.get("resourceId", {}).get("videoId", "")
                texte = s.get("title", "") + " " + (s.get("description", "") or "")
                if not vid or any(f in mt.aplatir(texte) for f in termes):
                    continue        # la description parle deja : rien a gagner
                if vid not in cache_liste:
                    fiche = {"video_id": vid, "chaine": nom,
                             "titre": s.get("title", "")[:120],
                             "publiee": (s.get("publishedAt") or "")[:10]}
                    temoins.append(fiche)
                    cache_liste[vid] = fiche
                pris += 1
            page = d.get("nextPageToken")
            if not page:
                break
        print(f"  {nom[:26]:28s} {pris:>4d} videos sans signal", file=sys.stderr)

    temoins = temoins[:args.videos]
    print(f"\n{len(temoins)} videos a transcrire | {depense} unites de quota",
          file=sys.stderr)

    # --- 2) transcrire et chercher ---
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    trouves = []
    for i, t in enumerate(temoins, 1):
        if t["video_id"] not in cache:
            cache[t["video_id"]] = mt.transcription(t["video_id"]) or ""
            if i % 10 == 0:
                ecrire_sur(CACHE, json.dumps(cache, ensure_ascii=False))
                print(f"  {i}/{len(temoins)} — {len(trouves)} trouvees",
                      file=sys.stderr)
        texte = cache[t["video_id"]]
        if not texte:
            continue
        plat, index = aplatir_avec_index(texte)
        # On cherche la position de CHAQUE forme reconnue, pas de la premiere
        # de la table : l'erreur du 27/08 affichait un extrait sans rapport.
        touches = []
        for f, (_a, e) in termes.items():
            depart = plat.find(f)
            while depart >= 0:
                if not coupe_un_mot(texte, index, depart, len(f)):
                    touches.append((depart, f, e))
                    break
                depart = plat.find(f, depart + 1)
        if not touches:
            continue
        touches.sort()
        i0, forme, _e = touches[0]
        # La position est celle du texte APLATI. Le convertir avant de couper :
        # l'aplatissement supprime des caracteres, donc les deux index divergent
        # d'autant plus qu'on avance. Sans cette conversion, l'extrait affiche
        # un passage sans rapport — l'erreur commise deux fois le 27/08.
        reel = index[i0] if i0 < len(index) else 0
        fin = index[min(i0 + len(forme), len(index) - 1)]
        entites = sorted({e for _i, _f, e in touches})
        trouves.append(dict(t, entites=" | ".join(entites),
                            forme_reconnue=forme,
                            extrait=texte[max(0, reel - 220):fin + 260].strip()))
    ecrire_sur(CACHE, json.dumps(cache, ensure_ascii=False))

    avec = sum(1 for t in temoins if cache.get(t["video_id"]))
    aujourdhui = date.today().isoformat()

    if trouves:
        chemin_csv = RECHERCHE / f"second_rideau_{aujourdhui}.csv"
        with chemin_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(trouves[0].keys()))
            w.writeheader()
            w.writerows(trouves)

    md = [f"# Transcription en second rideau — {aujourdhui}", "",
          "Produit par `outils/second_rideau_transcription.py`.", "",
          "Videos **sans aucun signal en description**, prises sur les chaines",
          "ou une collaboration est deja confirmee. Ce que trouve la",
          "transcription ici, rien d'autre ne le voyait.", "",
          f"- Chaines examinees : **{len(cibles)}**",
          f"- Videos temoins : **{len(temoins)}**",
          f"- Transcriptions obtenues : **{avec}**",
          f"- **Videos citant la filiere : {len(trouves)}**",
          f"- Quota depense : {depense} unites", "",
          "**Une mention orale n'etablit pas la remuneration.** Degre de",
          "certitude au plus « lien commercial documente ». Et le faux positif",
          "oral existe : une blague, une recette, un commentaire.", ""]

    if trouves:
        md += ["| Chaine | Entite | Publiee | Titre | Ce qui est dit |",
               "|---|---|---|---|---|"]
        for t in sorted(trouves, key=lambda x: x["chaine"]):
            md += [f"| {t['chaine'][:20]} | **{t['entites'][:26]}** | "
                   f"{t['publiee']} | {t['titre'][:34]} | "
                   f"{t['extrait'][:260].replace('|', ' ')} |"]
    else:
        md += ["## Aucune", "",
               "Sur cet echantillon, l'oral ne cite jamais la filiere quand la",
               "description se tait. Cela ne contredit pas le cas Inoxtag 2.0 du",
               "27/08 : un phenomene rare reste rare. Cela borne son rendement.", ""]

    chemin = RECHERCHE / f"second_rideau_{aujourdhui}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:14]))
    print(f"\nEcrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
