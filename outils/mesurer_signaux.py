"""
Mesure chaque signal separement contre le jeu de reference de Vincent.

CE QU'ON IGNORE ENCORE

Le projet a quatre signaux, et **un seul a ete evalue** : la description
(83 % de precision avec la regle D, JOURNAL 38). La case de declaration
YouTube, les segments SponsorBlock et la transcription n'ont jamais ete
confrontes aux 271 jugements de Vincent.

Sans cette mesure on ne sait pas :

- lequel des signaux merite d'etre le premier filtre ;
- si les combiner fait mieux que le meilleur pris seul ;
- lesquels sont assez independants pour la capture-recapture
  (METHODOLOGIE section 9.3), qui exige justement des methodes qui ne se
  trompent pas sur les memes contenus.

CE QUE CE SCRIPT MESURE, ET SUR QUOI

SponsorBlock, interroge video par video sur les 271 candidats deja juges.
C'est un service tiers, gratuit, sans quota et servi par un autre serveur que
YouTube : il ne consomme ni la cle API ni le budget de pages.

Limite a garder en tete : les 271 candidats viennent tous du canal
« description ». Un signal peut donc paraitre mauvais ici simplement parce
qu'on ne le mesure que la ou l'autre a deja trouve quelque chose. Ces chiffres
disent comment les signaux se comportent **sur ce sous-ensemble**, pas dans
l'absolu.

Usage :  python outils/mesurer_signaux.py
"""

import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"
CACHE = RACINE / "donnees" / "sponsorblock_271.json"

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def sponsorblock(vid):
    """Segments « sponsor » signales par les benevoles. Gratuit, sans quota."""
    url = (f"https://sponsor.ajay.app/api/skipSegments?videoID={vid}"
           f"&category=sponsor")
    for essai in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return len(json.loads(r.read().decode("utf-8"))), None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 0, None          # aucun segment : reponse valide
            if e.code == 429 and essai < 2:
                time.sleep(3 * (essai + 1))
                continue
            return None, f"HTTP {e.code}"
        except Exception as e:
            if essai < 2:
                time.sleep(2)
                continue
            return None, type(e).__name__
    return None, "epuise"


def charger_juges():
    """Les 271 candidats avec le verdict de Vincent."""
    import openpyxl
    wb = openpyxl.load_workbook(CARTO / "A_VERIFIER.xlsx", data_only=True)
    ws = wb["a verifier"]
    juges = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[8]:
            juges[(str(r[1]), str(r[5])[:40])] = str(r[8])
    wb.close()

    f = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))[-1]
    out = []
    with f.open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            if not l.get("force", "").startswith("ALIAS"):
                continue
            v = juges.get((l["chaine"], l["titre"][:40]))
            if v:
                out.append({
                    "video_id": l["video_id"], "chaine": l["chaine"],
                    "titre": l["titre"], "url": l["url"],
                    "abonnes": int(l["abonnes"] or 0), "publiee": l["publiee"],
                    "verdict": v, "vrai": v == "collaboration remuneree",
                    "indices": l.get("indices", ""),
                    "entite": l["entites_retenues"],
                })
    return out


def main():
    lignes = charger_juges()
    print(f"{len(lignes)} candidats juges par Vincent", file=sys.stderr)
    if not lignes:
        return 1

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    a_faire = [l["video_id"] for l in lignes if l["video_id"] not in cache]
    print(f"{len(a_faire)} a interroger sur SponsorBlock "
          f"({len(cache)} en cache)", file=sys.stderr)

    if a_faire:
        with ThreadPoolExecutor(4) as ex:
            for vid, (n, err) in zip(a_faire, ex.map(sponsorblock, a_faire)):
                cache[vid] = {"segments": n, "erreur": err}
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    erreurs = sum(1 for v in cache.values() if v.get("erreur"))
    print(f"{erreurs} interrogations en erreur", file=sys.stderr)

    for l in lignes:
        d = cache.get(l["video_id"], {})
        l["segments_sb"] = d.get("segments")
        l["sb_ok"] = d.get("erreur") is None

    mesurables = [l for l in lignes if l["sb_ok"]]
    total_vrais = sum(1 for l in mesurables if l["vrai"])

    def eval_signal(nom, garde):
        retenus = [l for l in mesurables if garde(l)]
        vp = sum(1 for l in retenus if l["vrai"])
        prec = 100 * vp / len(retenus) if retenus else 0
        rapp = 100 * vp / total_vrais if total_vrais else 0
        return nom, len(retenus), vp, len(retenus) - vp, prec, rapp

    signaux = [
        ("SponsorBlock : au moins un segment",
         lambda l: (l["segments_sb"] or 0) > 0),
        ("Indice commercial en description",
         lambda l: bool(l["indices"].strip())),
        ("Mention legale en description",
         lambda l: "mention_legale" in l["indices"]),
        ("Code promo en description",
         lambda l: "code_promo" in l["indices"]),
        ("SponsorBlock OU indice commercial",
         lambda l: (l["segments_sb"] or 0) > 0 or bool(l["indices"].strip())),
        ("SponsorBlock ET indice commercial",
         lambda l: (l["segments_sb"] or 0) > 0 and bool(l["indices"].strip())),
    ]

    print()
    print(f"{'SIGNAL':44s} {'retenus':>8s} {'vrais':>6s} {'faux':>5s} "
          f"{'precis.':>8s} {'rappel':>7s}")
    resultats = []
    for nom, garde in signaux:
        r = eval_signal(nom, garde)
        resultats.append(r)
        print(f"{r[0]:44s} {r[1]:>8d} {r[2]:>6d} {r[3]:>5d} "
              f"{r[4]:>7.0f} % {r[5]:>6.0f} %")

    # --- desaccord entre signaux : le materiau de la capture-recapture ---
    sb = {l["video_id"] for l in mesurables if (l["segments_sb"] or 0) > 0}
    desc = {l["video_id"] for l in mesurables if l["indices"].strip()}
    vrais = {l["video_id"] for l in mesurables if l["vrai"]}
    a, b = len(sb & vrais), len(desc & vrais)
    m = len(sb & desc & vrais)
    estimation = (a * b / m) if m else None

    aujourdhui = date.today().isoformat()
    md = [f"# Mesure des signaux contre le jeu de reference — {aujourdhui}", "",
          "Produit par `outils/mesurer_signaux.py`.", "",
          f"- Candidats juges par Vincent : **{len(lignes)}**",
          f"- Interrogations SponsorBlock exploitables : **{len(mesurables)}**",
          f"- Vraies collaborations dans cet ensemble : **{total_vrais}**", "",
          "| Signal | Retenus | Vrais | Faux | Precision | Rappel |",
          "|---|---:|---:|---:|---:|---:|"]
    for nom, n, vp, fp, prec, rapp in resultats:
        md += [f"| {nom} | {n} | {vp} | {fp} | {prec:.0f} % | {rapp:.0f} % |"]

    md += ["", "## Capture-recapture entre SponsorBlock et la description", "",
           "METHODOLOGIE section 9.3 : deux methodes independantes appliquees au",
           "meme echantillon permettent d'estimer ce que **les deux** ratent.", "",
           f"- Vraies collaborations vues par SponsorBlock : **{a}**",
           f"- Vues par la description : **{b}**",
           f"- Vues par les deux : **{m}**", ""]
    if estimation:
        md += [f"- Estimation de la population totale (a x b / m) : "
               f"**{estimation:.0f}** collaborations",
               f"- Soit **{estimation - total_vrais:.0f}** que les deux methodes "
               f"manquent ensemble", ""]
    else:
        md += ["- Recouvrement nul : l'estimation est impossible. C'est en soi",
               "  une information — les deux signaux ne voient pas les memes",
               "  videos du tout.", ""]

    md += ["## Limite de cette mesure", "",
           "Les 271 candidats viennent tous du canal « description ». Un signal",
           "peut donc paraitre faible ici simplement parce qu'on ne le mesure",
           "que la ou l'autre a deja trouve quelque chose. **Ces chiffres",
           "decrivent le comportement des signaux sur ce sous-ensemble, pas",
           "dans l'absolu.** Seul le tirage aleatoire y remediera.", ""]

    chemin = RECHERCHE / f"mesure_signaux_{aujourdhui}.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print()
    print(f"capture-recapture : SB={a} desc={b} communs={m} "
          f"-> estimation {estimation:.0f}" if estimation
          else "capture-recapture : recouvrement nul")
    print(f"Ecrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
