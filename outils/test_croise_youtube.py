"""
OUTIL REMPLACE — conserve pour la tracabilite, ne plus lancer.

REMPLACE PAR : outils/surveiller_youtube.py, qui absorbe ses fonctions et en corrige
les defauts (resolution des chaines, detection des echecs de
telechargement, ralentissement).

Il reste ici parce que des mesures enregistrees dans recherche/ ont
ete produites par lui : le supprimer rendrait ces mesures
irreproductibles.
"""

"""
Test croise YouTube : deux signaux independants de collaboration commerciale.

  Signal 1 - DECLARATION : le createur a coche la case "communication
             commerciale" de YouTube. Visible dans la page publique de la
             video sous la cle paidContentOverlayRenderer.
  Signal 2 - SPONSORBLOCK : des benevoles ont marque un segment "sponsor"
             dans la video. Interroge via l'API publique, sans cle.

Le cas interessant est le DESACCORD : un segment sponsorise sans declaration.
Voir METHODOLOGIE.md sections 11 et 14.

IMPORTANT : ce script ECRIT ses resultats dans recherche/, un fichier par
lancement, horodate. Ne jamais revenir a une version qui n'affiche qu'a
l'ecran : sans trace ecrite, une mesure n'est pas comparable a la suivante.

Usage :  python outils/test_croise_youtube.py
"""

import csv, json, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "recherche"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Chaines surveillees pour ce test. Choisies parce qu'elles sont grandes,
# francaises, et pour certaines deja documentees comme ayant travaille avec
# les lobbies viande/lait.
HANDLES = [
    "Squeezie",
    "MisterV",
    "Inoxtag",
    "Valouzz",
    "lorisgiuliano",
    "McFlyetCarlito",
]

VIDEOS_PAR_CHAINE = 15


def get(url, timeout=30):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    except Exception:
        return ""


def channel_id(handle):
    """Resout un @pseudo en identifiant de chaine UC...

    On lit la cle "channelId" du JSON embarque plutot que de prendre la
    chaine UC la plus frequente de la page : cette derniere methode ramenait
    parfois la chaine d'une video recommandee.
    """
    page = get(f"https://www.youtube.com/@{handle}")
    if not page:
        return None
    m = re.search(r'"channelId":"(UC[A-Za-z0-9_-]{22})"', page)
    if m:
        return m.group(1)
    m = re.search(r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[A-Za-z0-9_-]{22})"', page)
    return m.group(1) if m else None


def videos(cid, n=VIDEOS_PAR_CHAINE):
    """Dernieres videos d'une chaine, via son flux RSS public (sans cle API)."""
    xml = get(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}")
    entrees = re.findall(
        r"<entry>.*?<yt:videoId>([\w-]{11})</yt:videoId>.*?<title>(.*?)</title>.*?<published>(.*?)</published>",
        xml, re.S)
    return entrees[:n]


def declaree(vid):
    """Signal 1 : la case 'communication commerciale' est-elle cochee ?"""
    return "paidContentOverlayRenderer" in get(f"https://www.youtube.com/watch?v={vid}")


def sponsorblock(vid):
    """Signal 2 : nombre de segments 'sponsor' signales par les benevoles."""
    r = get(f"https://sponsor.ajay.app/api/skipSegments?videoID={vid}&category=sponsor", 20)
    try:
        return len(json.loads(r))
    except Exception:
        return 0


def main():
    SORTIE.mkdir(exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    date_lisible = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lignes = []
    non_resolues = []

    for h in HANDLES:
        cid = channel_id(h)
        if not cid:
            non_resolues.append(h)
            print(f"  {h:16s} CHAINE NON RESOLUE", file=sys.stderr)
            continue
        vids = videos(cid)
        print(f"  {h:16s} {cid}  {len(vids)} videos", file=sys.stderr)
        with ThreadPoolExecutor(8) as ex:
            decls = list(ex.map(lambda v: declaree(v[0]), vids))
            sbs = list(ex.map(lambda v: sponsorblock(v[0]), vids))
        for (vid, titre, publie), d, s in zip(vids, decls, sbs):
            if d and s:
                cas = "declare_ET_sponsorblock"
            elif d:
                cas = "declare_seul"
            elif s:
                cas = "sponsorblock_seul"
            else:
                cas = "aucun_signal"
            lignes.append({
                "chaine": h,
                "channel_id": cid,
                "video_id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "titre": titre,
                "publiee": publie,
                "declaree": "oui" if d else "non",
                "segments_sponsorblock": s,
                "cas": cas,
                "releve_le": date_lisible,
            })

    # --- ecriture du releve complet, une ligne par video examinee ---
    csv_path = SORTIE / f"test_croise_youtube_{horodatage}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()) if lignes else ["chaine"])
        w.writeheader()
        w.writerows(lignes)

    # --- comptage ---
    tot = {c: 0 for c in ["declare_ET_sponsorblock", "declare_seul",
                          "sponsorblock_seul", "aucun_signal"]}
    for l in lignes:
        tot[l["cas"]] += 1
    n = len(lignes)

    md = [
        f"# Test croise YouTube — {date_lisible}",
        "",
        f"Releve produit par `outils/test_croise_youtube.py`.",
        f"Donnees completes : `{csv_path.name}` (une ligne par video examinee).",
        "",
        f"- Chaines demandees : {len(HANDLES)} — {', '.join(HANDLES)}",
        f"- Chaines non resolues : {', '.join(non_resolues) if non_resolues else 'aucune'}",
        f"- Videos examinees : {n} (les {VIDEOS_PAR_CHAINE} dernieres par chaine resolue)",
        "",
        "| Situation | Videos | Part |",
        "|---|---|---|",
    ]
    etiquettes = {
        "declare_ET_sponsorblock": "Declaree ET segment SponsorBlock",
        "declare_seul": "Declaree seulement",
        "sponsorblock_seul": "**Segment SponsorBlock SANS declaration**",
        "aucun_signal": "Aucun signal",
    }
    for cle, lib in etiquettes.items():
        part = f"{100*tot[cle]/n:.0f} %" if n else "—"
        md += [f"| {lib} | {tot[cle]} | {part} |"]
    signal = n - tot["aucun_signal"]
    md += [
        "",
        f"Au moins un signal commercial : **{signal} videos sur {n}**"
        + (f" ({100*signal/n:.0f} %)." if n else "."),
        "",
        "## Videos portant au moins un signal",
        "",
        "| Chaine | Declaree | Segments SB | Titre | URL |",
        "|---|---|---|---|---|",
    ]
    for l in lignes:
        if l["cas"] != "aucun_signal":
            md += [f"| {l['chaine']} | {l['declaree']} | {l['segments_sponsorblock']} "
                   f"| {l['titre'][:60]} | {l['url']} |"]
    md += [
        "",
        "## Rappel de lecture",
        "",
        "« SponsorBlock sans declaration » ne prouve pas la non-declaration :",
        "le createur a pu annoncer le partenariat oralement ou a l'ecran sans",
        "cocher la case, et un benevole a pu etiqueter une auto-promotion comme",
        "sponsor. Voir METHODOLOGIE.md section 14.",
        "",
    ]
    md_path = SORTIE / f"test_croise_youtube_{horodatage}.md"
    md_path.write_text("\n".join(md), encoding="utf-8")

    print("\n".join(md))
    print(f"\nEcrit : {csv_path}\nEcrit : {md_path}")


if __name__ == "__main__":
    main()
