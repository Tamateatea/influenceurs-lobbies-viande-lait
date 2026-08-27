"""
Moissonne le catalogue complet des chaines surveillees et y cherche la filiere.

CE QUE CA DEBLOQUE

Jusqu'ici le projet ne voyait que les **15 dernieres videos** d'une chaine,
limite du flux RSS (hypothese YT-03, refutee le 24/08). Aucune recherche
retroactive n'etait possible : les collaborations documentees par la presse —
la Tomme de Savoie d'Inoxtag avec le Cniel, la video Cniel de Squeezie —
etaient hors de portee.

`playlistItems.list` renvoie **50 videos avec leur description complete pour
1 unite de quota**. Le catalogue entier d'une chaine de 1 000 videos coute
donc 20 unites, sur ~10 000 par jour.

C'est 50 fois moins cher que de telecharger les pages une par une, et sans la
limitation opaque qui a bloque la journee du 24/08 (JOURNAL 28).

CE QUE CA NE DONNE PAS

- La case de declaration « communication commerciale » : absente de l'API,
  elle n'existe que dans la page publique. Il faudra y retourner, mais
  seulement sur les videos deja signalees — donc en tres petit nombre.
- Les segments SponsorBlock : service tiers, interroge separement.

Autrement dit cette moisson sert a **reduire l'espace de recherche** : sur des
dizaines de milliers de videos, elle designe les quelques dizaines qui citent
la filiere. Les signaux couteux ne s'appliquent qu'a celles-la.

REPRISE APRES INTERRUPTION

Le travail est enregistre en continu dans `donnees/moisson_videos.json`. Une
interruption ne perd rien : relancer reprend ou on s'est arrete. Concu pour ca,
parce qu'une session peut se fermer en cours de route.

Usage :
    python outils/moissonner_videos.py
    python outils/moissonner_videos.py --budget 7000 --max-videos 1200
"""

import argparse
import csv
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ecriture_sure import ecrire_sur
import table_alias

RACINE = Path(__file__).resolve().parent.parent
SECRETS = RACINE / "SECRETS.txt"
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"
ETAT = RACINE / "donnees" / "moisson_videos.json"
API = "https://www.googleapis.com/youtube/v3/"

ARTICLES = ("les", "le", "la", "l", "des", "de", "du")

# Indices commerciaux, identiques a ceux de surveiller_youtube.py (YT-14).
INDICES = {
    "mention_legale": [r"collaboration commerciale", r"communication commerciale",
                       r"en partenariat avec", r"sponsoris[ée]e? par", r"#ad\b"],
    "code_promo": [r"avec le code\s+\S+", r"\bcode\s+promo\b",
                   r"le code\s+[A-Z][A-Z0-9]{2,}", r"-\s?\d{1,2}\s?%"],
    "lien_affilie": [r"mon lien\b", r"lien en description"],
    "remerciement": [r"\bmerci\s+(?:a|aux|à)\s+\S+", r"avec le soutien de"],
}


def lire_cle():
    if not SECRETS.exists():
        return None
    m = re.search(r"YOUTUBE_API_KEY\s*=\s*(\S+)",
                  SECRETS.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m and not m.group(1).startswith("colle") else None


def aplatir(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def sans_accent(t):
    t = unicodedata.normalize("NFKD", str(t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def charger_alias():
    """La table d'alias, via le chargeur partage `table_alias.py`.

    Deux choix explicites, la ou ils etaient implicites avant :

    **Seuil 5, pas 8.** Passer a 8 retirerait 43 formes, dont de vraies
    marques — Actimel, Activia, Babybel, Boursin, Bridel, Candia, Aoste. La
    regle des huit caracteres etait un pis-aller contre les artefacts
    d'aplatissement ; c'est le garde-fou de frontiere de mot d'`appariement.py`
    qui les traite vraiment, et il permet de garder les noms courts.

    **Hors perimetre inclus.** La moisson collecte large, le nettoyage filtre.
    Ainsi, changer le perimetre — la question du CNPO est ouverte — ne demande
    pas de re-moissonner 307 000 videos.
    """
    return table_alias.charger(seuil=5, avec_marques=True,
                               avec_hors_perimetre=True)


def appel(endpoint, params, cle):
    params = dict(params, key=cle)
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    for essai in range(3):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return json.loads(r.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            corps = e.read().decode("utf-8", "replace")
            try:
                msg = json.loads(corps)["error"]["message"]
            except Exception:
                msg = corps[:150]
            if e.code in (403,) and "quota" in msg.lower():
                return None, "QUOTA:" + msg
            if e.code >= 500 and essai < 2:
                time.sleep(2 * (essai + 1))
                continue
            return None, f"HTTP {e.code} — {msg}"
        except Exception as e:
            if essai < 2:
                time.sleep(2)
                continue
            return None, type(e).__name__
    return None, "epuise"


def chaines_a_moissonner():
    """Les chaines YouTube du registre consolide, les plus suivies d'abord."""
    f = sorted(RECHERCHE.glob("comptes_consolides_*.csv"))
    if not f:
        return []
    out = {}
    with f[-1].open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            if l["plateforme"] != "youtube":
                continue
            cid = l["identifiant"]
            if not cid.startswith("UC"):
                continue
            ab = int(l["audience"]) if str(l["audience"]).isdigit() else 0
            out[cid] = (ab, l.get("nom_affiche", "") or l.get("pseudo", ""))
    return [(cid, nom, ab) for cid, (ab, nom) in
            sorted(out.items(), key=lambda x: -x[1][0])]


def analyser(texte, termes):
    plat = aplatir(texte)
    alias, entites = [], []
    for forme, (lisible, entite) in termes.items():
        if forme in plat:
            alias.append(lisible)
            entites.append(entite)
    t = sans_accent(texte)
    familles = [f for f, motifs in INDICES.items()
                if any(re.search(m, t, re.I) for m in motifs)]
    formes = [f for f in termes if f in plat]
    return sorted(set(alias)), sorted(set(entites)), familles, formes


def extrait_declencheur(texte, termes_trouves, marge=260):
    """La fenetre de texte AUTOUR de la mention, prise dans le texte COMPLET.

    Defaut corrige le 27/08 : seuls les 900 premiers caracteres de la
    description etaient conserves, et **42 % des detections avaient leur alias
    declencheur au-dela**. L'extrait montre a Vincent ne pouvait donc pas
    contenir la preuve — exactement ce qu'il reprochait le 25/08 (« je ne vois
    pas le lien avec les influenceurs pour la plupart »).

    On garde toujours le debut de la description, utile pour le contexte, mais
    on y ajoute la fenetre qui entoure la mention.
    """
    if not termes_trouves:
        return ""
    plat = aplatir(texte)
    # correspondance entre position aplatie et position d'origine
    index, position = [], 0
    for c in texte:
        if aplatir(c):
            index.append(position)
        position += 1
    meilleure = None
    for forme in termes_trouves:
        i = plat.find(forme)
        if i >= 0 and (meilleure is None or i < meilleure):
            meilleure = i
    if meilleure is None or meilleure >= len(index):
        return ""
    reel = index[meilleure]
    return texte[max(0, reel - marge):reel + marge].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=7000)
    ap.add_argument("--max-videos", type=int, default=1500,
                    help="plafond par chaine, pour qu'une seule n'avale pas tout")
    args = ap.parse_args()

    cle = lire_cle()
    if not cle:
        print("YOUTUBE_API_KEY absente de SECRETS.txt.", file=sys.stderr)
        return 1

    ETAT.parent.mkdir(parents=True, exist_ok=True)
    etat = json.loads(ETAT.read_text(encoding="utf-8")) if ETAT.exists() else {
        "faites": {}, "touchees": []}
    termes = charger_alias()
    chaines = chaines_a_moissonner()
    print(f"{len(termes)} formes d'alias | {len(chaines)} chaines a moissonner",
          file=sys.stderr)
    print(f"{len(etat['faites'])} deja faites lors d'un lancement precedent",
          file=sys.stderr)

    depense, total_videos, arret = 0, 0, None

    for i, (cid, nom, ab) in enumerate(chaines, 1):
        if cid in etat["faites"]:
            total_videos += etat["faites"][cid].get("videos", 0)
            continue
        if depense >= args.budget:
            arret = f"budget de {args.budget} unites atteint"
            break

        d, err = appel("channels", {"part": "contentDetails", "id": cid}, cle)
        depense += 1
        if err or not d.get("items"):
            if err and err.startswith("QUOTA"):
                arret = err
                break
            etat["faites"][cid] = {"videos": 0, "erreur": err or "introuvable"}
            continue
        up = d["items"][0]["contentDetails"]["relatedPlaylists"].get("uploads")
        if not up:
            etat["faites"][cid] = {"videos": 0, "erreur": "pas de playlist"}
            continue

        page, n_chaine, touchees_ici = None, 0, 0
        while n_chaine < args.max_videos:
            p = {"part": "snippet", "playlistId": up, "maxResults": 50}
            if page:
                p["pageToken"] = page
            d, err = appel("playlistItems", p, cle)
            depense += 1
            if err:
                if err.startswith("QUOTA"):
                    arret = err
                break
            for it in d.get("items", []):
                s = it["snippet"]
                vid = s.get("resourceId", {}).get("videoId", "")
                if not vid:
                    continue
                n_chaine += 1
                desc = s.get("description", "") or ""
                texte_complet = s.get("title", "") + " " + desc
                alias, entites, familles, formes = analyser(texte_complet, termes)
                if entites or familles:
                    touchees_ici += 1
                    etat["touchees"].append({
                        "channel_id": cid, "chaine": nom, "abonnes": ab,
                        "video_id": vid, "titre": s.get("title", "")[:150],
                        "publiee": (s.get("publishedAt") or "")[:10],
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "entites_filiere": " | ".join(entites),
                        "alias_reconnus": " | ".join(alias),
                        "indices": " | ".join(familles),
                        "description": desc.replace("\n", " ⏎ ")[:900],
                    })
            page = d.get("nextPageToken")
            if not page or arret:
                break

        etat["faites"][cid] = {"videos": n_chaine, "touchees": touchees_ici}
        total_videos += n_chaine
        marque = f"  <-- {touchees_ici} video(s) citant la filiere" if touchees_ici else ""
        print(f"  {i:>3d}/{len(chaines)} {nom[:26]:28s} {n_chaine:>5d} videos "
              f"| quota {depense:>5d}{marque}", file=sys.stderr)
        ecrire_sur(ETAT, json.dumps(etat, ensure_ascii=False))
        if arret:
            break

    ecrire_sur(ETAT, json.dumps(etat, ensure_ascii=False))

    # --- sorties ---
    aujourdhui = date.today().isoformat()
    touchees = etat["touchees"]
    filiere = [t for t in touchees if t["entites_filiere"]]

    if touchees:
        csv_path = RECHERCHE / f"moisson_videos_{aujourdhui}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(touchees[0].keys()))
            w.writeheader()
            w.writerows(touchees)

    md = [f"# Moisson des catalogues YouTube — {aujourdhui}", "",
          "Produit par `outils/moissonner_videos.py`, via l'API officielle.", "",
          "Le flux RSS ne donnait que les 15 dernieres videos d'une chaine.",
          "L'API rend le catalogue complet, descriptions comprises, pour",
          "1 unite de quota par tranche de 50 videos.", "",
          f"- Chaines moissonnees : **{len(etat['faites'])}** sur {len(chaines)}",
          f"- Videos examinees : **{total_videos:,}**".replace(",", " "),
          f"- Quota depense ce lancement : **{depense} unites**",
          f"- Videos portant un signal commercial : **{len(touchees)}**",
          f"- **Videos citant la filiere viande/lait : {len(filiere)}**",
          "", f"Arret : {arret}" if arret else "", ""]

    if filiere:
        md += ["## VIDEOS CITANT LA FILIERE VIANDE / LAIT", "",
               "**A verifier a la main. Une citation n'est pas une collaboration.**", "",
               "| Chaine | Abonnes | Entite | Publiee | Titre | URL |",
               "|---|---:|---|---|---|---|"]
        for t in sorted(filiere, key=lambda x: -x["abonnes"]):
            md += [f"| {t['chaine'][:22]} | {t['abonnes']:,} | **{t['entites_filiere']}** "
                   f"| {t['publiee']} | {t['titre'][:48]} | {t['url']} |".replace(",", " ")]
        md += [""]
    else:
        md += ["## Videos citant la filiere viande/lait", "",
               "Aucune pour l'instant. **C'est une mesure, pas un echec** — mais",
               "verifier le nombre de chaines effectivement moissonnees.", ""]

    md_path = RECHERCHE / f"moisson_videos_{aujourdhui}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print("\n".join(md[:16]))
    print(f"\nEcrit : {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
