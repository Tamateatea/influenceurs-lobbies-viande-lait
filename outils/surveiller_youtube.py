"""
Chaine de surveillance YouTube — les quatre signaux, sur une liste de chaines.

C'est l'outil central du projet cote YouTube. Il remplace et absorbe
test_croise_youtube.py et extraire_descriptions_youtube.py.

LES QUATRE SIGNAUX (voir HYPOTHESES.md, section YouTube) :

  1. DECLARATION   la case « communication commerciale » cochee par le createur
                   (cle paidContentOverlayRenderer dans la page publique)
  2. SPONSORBLOCK  segments « sponsor » signales par les benevoles
  3. DESCRIPTION   texte public : alias de la filiere + indices commerciaux
  4. TRANSCRIPTION contenu parle, via yt-dlp — coute cher, donc reserve aux
                   videos deja porteuses d'un signal

Aucun n'est suffisant seul : c'est mesure, pas suppose. La case de declaration
ne rattrape que 2 collaborations sur 14 chez Inoxtag ; le segment SponsorBlock
peut designer un tout autre annonceur que la description (JOURNAL 20.2).

RESOLUTION DES CHAINES : par recherche, jamais par pseudo. Un @pseudo devine
resout vers une chaine secondaire — @Michou donne « MichouOff », @LeBouseuh
donne « BouziTV ». Le titre resolu est ecrit dans la sortie pour que toute
erreur de ciblage se voie.

RIEN ICI N'EST UNE PREUVE DE COLLABORATION. Le script produit des candidats.
Seule une lecture humaine tranche — voir JOURNAL 20.4, ou un motif automatique
prenait une blague pour un contrat.

Usage :
    python outils/surveiller_youtube.py                  liste par defaut
    python outils/surveiller_youtube.py --videos 10      moins de videos
    python outils/surveiller_youtube.py --sans-transcription
"""

import argparse
import csv
import json
import re
import subprocess
import sys
import time
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "recherche"
CLASSEUR = RACINE / "cartographie" / "cartographie_filiere.xlsx"

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

# Createurs generalistes suivis par @lesproduitslaitiers (CNIEL), plus les
# chaines deja testees. Cette liste est une HYPOTHESE DE CIBLAGE datee, pas un
# resultat : un abonnement ne prouve aucune collaboration (JOURNAL 19).
# Elle doit etre re-derivee des sources, jamais figee (METHODOLOGIE 14).
CHAINES = [
    "Squeezie", "Inoxtag", "Valouzz", "Mister V", "Mcfly et Carlito",
    "Michou", "Domingo", "Norman", "Grimkujow", "LeBouseuh",
    "Seb la Frite", "Kameto", "Zack Nani",
]

VIDEOS_PAR_CHAINE = 15
PLAFOND_TRANSCRIPTIONS = 30

ARTICLES = ("les", "le", "la", "l", "des", "de", "du")

# --- Indices commerciaux -----------------------------------------------------
# Elargis le 24/08 (hypothese YT-14). La lecture manuelle de Vincent avait
# trouve 12 annonceurs la ou la liste « conformite legale » n'en voyait que 8 :
# le vrai signal est COMMERCIAL, pas juridique. Un code promo est ecrit pour
# etre utilise, donc il est toujours la ; la mention legale est optionnelle
# dans les faits.
INDICES = {
    "mention_legale": [
        r"collaboration commerciale", r"communication commerciale",
        r"en partenariat avec", r"partenariat r[ée]mun[ée]r[ée]",
        r"sponsoris[ée]e? par", r"#ad\b", r"#sponsoris", r"#publicit",
    ],
    "code_promo": [
        r"\bcode\s+promo\b", r"avec le code\s+\S+", r"\bcode\s*:\s*\S+",
        r"le code\s+[A-Z][A-Z0-9]{2,}", r"-\s?\d{1,2}\s?%",
        r"\d{1,2}\s?%\s+de\s+r[ée]duction", r"offerts?\s+en\s+ouvrant",
    ],
    "lien_affilie": [
        r"mon lien\b", r"mes liens\b", r"lien en description",
        r"https?://\S*(?:utm_|/inox|/\?u\b|aff|partner|link\.)\S*",
    ],
    "remerciement": [
        r"\bmerci\s+(?:a|aux|à)\s+\S+", r"avec le soutien de",
        r"nous ont? accompagn",
    ],
}


# YouTube renvoie HTTP 429 (« Too Many Requests ») au-dela d'un certain rythme.
# Constate le 24/08/2026 : un releve de 288 videos a rendu 288 descriptions
# vides, et le script les a comptees comme « aucun signal ». Un faux negatif
# total, silencieux, et parfaitement credible dans le rapport.
# Depuis : on ralentit, on reessaie, et surtout ON SAIT QUAND ON A ECHOUE.
PAUSE_ENTRE_APPELS = 0.35   # ajustable par --pause
FILS = 3                    # ajustable par --fils


def get(url, timeout=30, essais=3):
    """Renvoie (contenu, erreur). Une chaine vide n'est JAMAIS silencieuse."""
    attente = 2.0
    for essai in range(essais):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                time.sleep(PAUSE_ENTRE_APPELS)
                return r.read().decode("utf-8", "replace"), None
        except urllib.error.HTTPError as e:
            if e.code == 429 and essai < essais - 1:
                time.sleep(attente)
                attente *= 3
                continue
            return "", f"HTTP {e.code}"
        except Exception as e:
            if essai < essais - 1:
                time.sleep(attente)
                attente *= 3
                continue
            return "", type(e).__name__
    return "", "epuise"


def texte(url, timeout=30):
    """Quand seul le contenu importe et qu'un echec est tolerable."""
    return get(url, timeout)[0]


def aplatir(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def sans_accent(t):
    t = unicodedata.normalize("NFKD", str(t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def variantes(alias):
    base = aplatir(alias)
    if len(base) < 5:
        return set()
    formes = {base}
    for art in ARTICLES:
        if base.startswith(art) and len(base) - len(art) >= 5:
            formes.add(base[len(art):])
    return formes


def charger_alias():
    import openpyxl
    wb = openpyxl.load_workbook(CLASSEUR, read_only=True, data_only=True)
    termes = {}

    def ajouter(alias, entite):
        if alias and entite:
            for f in variantes(alias):
                termes.setdefault(f, (str(alias).strip(), str(entite).strip()))

    for l in wb["Alias"].iter_rows(min_row=2, values_only=True):
        ajouter(l[0], l[2])
    for l in wb["Interprofessions"].iter_rows(min_row=2, values_only=True):
        ajouter(l[0], l[0])
        ajouter(l[1], l[0])
        ajouter(l[3], l[0])
    wb.close()
    return termes


def resoudre_chaines(nom):
    """Toutes les chaines OFFICIELLES d'un createur, principale et secondaires.

    Un createur n'a PAS une seule chaine. Constate le 24/08/2026 : la
    collaboration Inoxtag x CNIEL etait sur « Inoxtag 2.0 », pas sur la chaine
    principale. Et « Inoxtag 2.0 » porte un segment sponsorise sur 14 videos
    sur 15, contre 4 sur 15 pour la principale — les chaines secondaires sont
    plus densement sponsorisees, et moins regardees par les journalistes.

    Ne surveiller que la chaine principale, c'est manquer le gisement.

    FILTRE : on ne garde que les chaines portant le BADGE DE VERIFICATION.
    Sans lui, une recherche « Squeezie » remonte 17 chaines dont la plupart
    sont des reuploads de fans — du bruit qui ferait exploser la collecte et
    attribuerait a un createur des videos qu'il n'a pas publiees.
    """
    page = texte("https://www.youtube.com/results?search_query="
                 + urllib.parse.quote(nom) + "&sp=EgIQAg%253D%253D")
    cible = aplatir(nom)
    retenues, vus = [], set()

    for bloc in page.split('"channelRenderer":')[1:]:
        bloc = bloc[:4000]
        mid = re.search(r'"channelId":"(UC[A-Za-z0-9_-]{22})"', bloc)
        mtitre = re.search(r'"title":\{"simpleText":"(.*?)"', bloc)
        if not mid or not mtitre:
            continue
        cid, titre = mid.group(1), mtitre.group(1)
        if cid in vus:
            continue
        if "VERIFIED" not in bloc and "ownerBadges" not in bloc:
            continue                                    # chaine non officielle
        plat = aplatir(titre)
        if not (plat == cible or plat.startswith(cible)):
            continue
        mhandle = re.search(r'"subscriberCountText":\{"simpleText":"(@[\w.-]+)"', bloc)
        vus.add(cid)
        retenues.append((cid, titre, "principale" if plat == cible else "secondaire",
                         mhandle.group(1) if mhandle else ""))
    return retenues


def videos(cid, n):
    xml = texte(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}")
    return re.findall(
        r"<entry>.*?<yt:videoId>([\w-]{11})</yt:videoId>.*?<title>(.*?)</title>"
        r".*?<published>(.*?)</published>", xml, re.S)[:n]


def page_video(vid):
    """Un seul telechargement de page pour les signaux 1 et 3.

    Renvoie (declaree, description, soustitres, erreur). L'erreur remonte :
    une page non telechargee ne doit JAMAIS ressembler a une video sans signal.
    """
    page, erreur = get(f"https://www.youtube.com/watch?v={vid}")
    if not page:
        return False, "", False, erreur or "vide"
    declaree = "paidContentOverlayRenderer" in page
    desc = ""
    m = re.search(r'"shortDescription":"(.*?)","isCrawlable"', page, re.S)
    if m:
        try:
            desc = json.loads('"' + m.group(1) + '"')
        except Exception:
            desc = m.group(1)
    soustitres = '"captionTracks"' in page
    return declaree, desc, soustitres, None


def sponsorblock(vid):
    r = texte(f"https://sponsor.ajay.app/api/skipSegments?videoID={vid}&category=sponsor", 20)
    try:
        segs = json.loads(r)
        return [(round(s["segment"][0]), round(s["segment"][1])) for s in segs]
    except Exception:
        return []


def chercher_alias(texte, termes):
    plat = aplatir(texte)
    alias, entites = [], []
    for forme, (lisible, entite) in termes.items():
        if forme in plat:
            alias.append(lisible)
            entites.append(entite)
    return sorted(set(alias)), sorted(set(entites))


def chercher_indices(texte):
    t = sans_accent(texte)
    trouves = {}
    for famille, motifs in INDICES.items():
        hits = []
        for m in motifs:
            hits += [h if isinstance(h, str) else h[0]
                     for h in re.findall(m, t, re.I)][:3]
        if hits:
            trouves[famille] = sorted(set(x.strip()[:40] for x in hits))[:3]
    return trouves


def transcription(vid):
    """Sous-titres automatiques francais via yt-dlp. Renvoie [(seconde, texte)]."""
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--skip-download", "--write-auto-subs",
             "--sub-langs", "fr.*", "--sub-format", "vtt", "--no-warnings",
             "-o", str(Path(d) / "s.%(ext)s"),
             f"https://www.youtube.com/watch?v={vid}"],
            capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            return []
        fichiers = sorted(Path(d).glob("*.vtt"))
        if not fichiers:
            return []
        txt = fichiers[0].read_text(encoding="utf-8", errors="replace")

    def secondes(t):
        h, m, s = t.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    lignes, vu = [], None
    for debut, corps in re.findall(
            r"(\d\d:\d\d:\d\d\.\d\d\d) --> \d\d:\d\d:\d\d\.\d\d\d[^\n]*\n(.*?)(?=\n\n|\Z)",
            txt, re.S):
        for l in re.sub(r"<[^>]+>", "", corps).strip().splitlines():
            l = l.strip()
            if l and l != vu:
                lignes.append((secondes(debut), l))
                vu = l
    return lignes


def main():
    global PAUSE_ENTRE_APPELS, FILS
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", type=int, default=VIDEOS_PAR_CHAINE)
    ap.add_argument("--sans-transcription", action="store_true")
    ap.add_argument("--pause", type=float, default=PAUSE_ENTRE_APPELS,
                    help="secondes d'attente entre deux appels ; monter en cas de HTTP 429")
    ap.add_argument("--fils", type=int, default=FILS,
                    help="telechargements simultanes ; baisser en cas de HTTP 429")
    ap.add_argument("--plafond-transcriptions", type=int, default=PLAFOND_TRANSCRIPTIONS)
    args = ap.parse_args()
    PAUSE_ENTRE_APPELS, FILS = args.pause, args.fils

    SORTIE.mkdir(exist_ok=True)
    termes = charger_alias()
    print(f"{len(termes)} formes d'alias chargees", file=sys.stderr)

    # --- resolution des chaines, principales ET secondaires ---
    resolues, echecs = [], []
    with ThreadPoolExecutor(6) as ex:
        for nom, chaines in zip(CHAINES, ex.map(resoudre_chaines, CHAINES)):
            if not chaines:
                echecs.append(nom)
                print(f"  {nom:20s} AUCUNE CHAINE VERIFIEE", file=sys.stderr)
                continue
            for cid, titre, nature, handle in chaines:
                resolues.append((nom, cid, titre, nature))
                print(f"  {nom:18s} {cid} {titre[:32]:32s} {handle:24s} ({nature})",
                      file=sys.stderr)

    # --- collecte ---
    taches = []
    for nom, cid, titre, nature in resolues:
        for vid, t, publie in videos(cid, args.videos):
            taches.append((nom, cid, titre, nature, vid, t, publie))
    print(f"\n{len(taches)} videos a examiner", file=sys.stderr)

    with ThreadPoolExecutor(args.fils) as ex:
        pages = list(ex.map(lambda t: page_video(t[4]), taches))
        segments = list(ex.map(lambda t: sponsorblock(t[4]), taches))

    echoues = [(t[4], p[3]) for t, p in zip(taches, pages) if p[3]]
    if echoues:
        motifs = {}
        for _v, e in echoues:
            motifs[e] = motifs.get(e, 0) + 1
        print("", file=sys.stderr)
        print(f"{len(echoues)} pages sur {len(taches)} non telechargees : "
              + ", ".join(f"{k} x{v}" for k, v in motifs.items()), file=sys.stderr)
    part_echec = len(echoues) / max(len(taches), 1)
    if part_echec > 0.10:
        print("", file=sys.stderr)
        print(f"ARRET : {100*part_echec:.0f} % des pages n'ont pas ete "
              "telechargees.", file=sys.stderr)
        print("Les signaux 1 et 3 seraient faussement a zero, et le rapport "
              "dirait « aucun signal » alors qu'on n'a rien lu.", file=sys.stderr)
        print("Reessayer plus tard, ou baisser --videos.", file=sys.stderr)
        return 2
        return 2

    lignes = []
    for (nom, cid, titre, nature, vid, t, publie), (decl, desc, st, err), segs in zip(
            taches, pages, segments):
        alias, entites = chercher_alias(desc, termes)
        indices = chercher_indices(desc)
        lignes.append({
            "chaine_demandee": nom,
            "chaine_resolue": titre,
            "nature_de_la_chaine": nature,
            "channel_id": cid,
            "video_id": vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "titre": t,
            "publiee": publie,
            "s1_declaree": "oui" if decl else "non",
            "s2_segments_sponsorblock": len(segs),
            "s2_positions": " | ".join(f"{a}-{b}s" for a, b in segs),
            "s3_alias_filiere": " | ".join(alias),
            "s3_entites_filiere": " | ".join(entites),
            "s3_indices": " ; ".join(f"{k}: {', '.join(v)}" for k, v in indices.items()),
            "s3_familles_indices": len(indices),
            "s4_alias_transcription": "",
            "s4_entites_transcription": "",
            "s4_extraits": "",
            "soustitres_annonces": "oui" if st else "non",
            "page_non_telechargee": err or "",
            "description": desc.replace("\n", " ⏎ ")[:1200],
        })

    # --- signal 4 : transcription, seulement la ou il y a deja un signal ---
    def a_un_signal(l):
        return (l["s1_declaree"] == "oui" or l["s2_segments_sponsorblock"] > 0
                or l["s3_entites_filiere"] or l["s3_familles_indices"] > 0)

    candidats = [l for l in lignes if a_un_signal(l)]
    # priorite absolue aux videos qui touchent deja la filiere
    candidats.sort(key=lambda l: (not l["s3_entites_filiere"], -l["s3_familles_indices"]))
    a_transcrire = [] if args.sans_transcription else candidats[:args.plafond_transcriptions]

    if a_transcrire:
        print(f"\ntranscription de {len(a_transcrire)} videos sur "
              f"{len(candidats)} candidates", file=sys.stderr)
        for i, l in enumerate(a_transcrire, 1):
            blocs = transcription(l["video_id"])
            if not blocs:
                l["s4_extraits"] = "(transcription indisponible)"
                continue
            plein = " ".join(x for _, x in blocs)
            alias, entites = chercher_alias(plein, termes)
            l["s4_alias_transcription"] = " | ".join(alias)
            l["s4_entites_transcription"] = " | ".join(entites)
            if entites:
                extraits = []
                for sec, texte in blocs:
                    if chercher_alias(texte, termes)[1]:
                        extraits.append(f"[{int(sec//60)}m{int(sec % 60):02d}] {texte}")
                l["s4_extraits"] = " ⏎ ".join(extraits[:6])[:800]
            print(f"  {i}/{len(a_transcrire)} {l['chaine_demandee']:16s} "
                  f"{l['video_id']} {'-> ' + l['s4_entites_transcription'] if entites else ''}",
                  file=sys.stderr)

    # --- ecriture ---
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    date_lisible = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    for l in lignes:
        l["releve_le"] = date_lisible

    csv_path = SORTIE / f"surveillance_youtube_{horodatage}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
        w.writeheader()
        w.writerows(lignes)

    n = len(lignes)
    s1 = sum(1 for l in lignes if l["s1_declaree"] == "oui")
    s2 = sum(1 for l in lignes if l["s2_segments_sponsorblock"] > 0)
    s3i = sum(1 for l in lignes if l["s3_familles_indices"] > 0)
    filiere = [l for l in lignes if l["s3_entites_filiere"] or l["s4_entites_transcription"]]
    au_moins_un = sum(1 for l in lignes if a_un_signal(l))

    md = [
        f"# Surveillance YouTube — {date_lisible}", "",
        "Produit par `outils/surveiller_youtube.py`.",
        f"Detail complet : `{csv_path.name}`.", "",
        "**Aucune ligne de ce document n'est une preuve de collaboration.**",
        "Ce sont des candidats a verifier a la main.", "",
        "## Couverture", "",
        f"- Chaines demandees : {len(CHAINES)}",
        f"- Chaines surveillees : {len(resolues)} (principales et secondaires)"
        + (f" — **non resolues : {', '.join(echecs)}**" if echecs else ""),
        f"- Videos examinees : **{n}**",
        f"- Pages non telechargees : {len(echoues)}"
        + ("  (signaux 1 et 3 incomplets)" if echoues else ""),
        f"- Transcriptions recuperees : {len(a_transcrire)} (sur {len(candidats)} candidates)",
        "",
        "## Ce que chaque signal rapporte", "",
        "| Signal | Videos | Part |", "|---|---|---|",
        f"| 1. Case de declaration YouTube | {s1} | {100*s1/n:.0f} % |",
        f"| 2. Segment SponsorBlock | {s2} | {100*s2/n:.0f} % |",
        f"| 3. Indice commercial en description | {s3i} | {100*s3i/n:.0f} % |",
        f"| **Au moins un signal** | **{au_moins_un}** | **{100*au_moins_un/n:.0f} %** |",
        "",
    ]

    md += ["## Chaines surveillees", "",
           "Un createur a souvent plusieurs chaines. Les secondaires sont plus",
           "densement sponsorisees et moins regardees : ne pas les surveiller,",
           "c'est manquer le gisement (JOURNAL 21).", "",
           "| Createur | Chaine | Nature | Videos | 1+ signal |", "|---|---|---|---|---|"]
    for nom, cid, titre, nature in resolues:
        v = [l for l in lignes if l["channel_id"] == cid]
        u = sum(1 for l in v if a_un_signal(l))
        md += [f"| {nom} | {titre} | {nature} | {len(v)} | {u} |"]
    md += [""]

    md += ["## ENTITES DE LA FILIERE VIANDE/LAIT TROUVEES", ""]
    if filiere:
        md += ["| Chaine | Entite | Vue en | Case YT | Segments SB | URL |",
               "|---|---|---|---|---|---|"]
        for l in filiere:
            ou = []
            if l["s3_entites_filiere"]:
                ou.append("description")
            if l["s4_entites_transcription"]:
                ou.append("transcription")
            ent = l["s3_entites_filiere"] or l["s4_entites_transcription"]
            md += [f"| {l['chaine_demandee']} | **{ent}** | {' + '.join(ou)} "
                   f"| {l['s1_declaree']} | {l['s2_segments_sponsorblock']} | {l['url']} |"]
        md += [""]
        for l in filiere:
            if l["s4_extraits"]:
                md += [f"### {l['chaine_demandee']} — {l['titre'][:60]}", "",
                       f"{l['url']}", "", "Extraits de la transcription :", "",
                       "> " + l["s4_extraits"].replace(" ⏎ ", "\n>\n> "), ""]
    else:
        md += ["Aucune. **Ce n'est pas un echec : c'est une mesure.**", ""]

    md += ["## Desaccords entre signaux", "",
           "Le desaccord est le cas interessant : un segment sponsorise sans",
           "declaration, ou une declaration sans segment. Voir METHODOLOGIE 10.", "",
           "| Situation | Videos |", "|---|---|",
           f"| Segment SponsorBlock SANS case cochee | "
           f"{sum(1 for l in lignes if l['s2_segments_sponsorblock'] > 0 and l['s1_declaree'] == 'non')} |",
           f"| Case cochee SANS segment SponsorBlock | "
           f"{sum(1 for l in lignes if l['s1_declaree'] == 'oui' and l['s2_segments_sponsorblock'] == 0)} |",
           f"| Indice en description SANS case cochee | "
           f"{sum(1 for l in lignes if l['s3_familles_indices'] > 0 and l['s1_declaree'] == 'non')} |",
           ""]

    md_path = SORTIE / f"surveillance_youtube_{horodatage}.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nEcrit : {csv_path}\nEcrit : {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
