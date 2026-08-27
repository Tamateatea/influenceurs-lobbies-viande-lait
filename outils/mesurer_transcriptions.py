"""
Mesure le signal « transcription » contre le jeu de reference de Vincent.

LE DERNIER SIGNAL JAMAIS MESURE

Le projet a quatre signaux sur YouTube. Trois ont ete confrontes aux jugements
de Vincent :

    description        71 % de precision, 87 % de rappel  (JOURNAL 43)
    SponsorBlock       69 % / 13 %  — quasi redondant
    case de declaration  jamais mesuree
    transcription        jamais mesuree

La transcription est le seul signal qui atteigne le **contenu parle**. On sait
depuis le 24/08 qu'elle trouve des choses que la description ne montre pas :
une meme video peut porter trois annonceurs a trois endroits, dont un
uniquement a l'oral (JOURNAL 20.2). Mais on n'a jamais mesure ce que ca vaut.

On sait aussi qu'elle produit des faux positifs qu'aucun motif ne rattrape :
« la video est sponsorisee par Odica » etait une blague sur des appareils
auditifs (JOURNAL 20.4).

CE QUE CE SCRIPT MESURE

Sur les videos deja jugees par Vincent, il recupere la transcription via
yt-dlp et y cherche les alias de la filiere. Puis il compare : combien de
vraies collaborations la transcription voit-elle, que la description ne voyait
pas ? Et inversement ?

**Aucun quota d'API consomme** — yt-dlp passe par les pages publiques. Mais
c'est lent : quelques secondes par video.

Usage :
    python outils/mesurer_transcriptions.py --max 120
"""

import argparse
import csv
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RECHERCHE = RACINE / "recherche"
CARTO = RACINE / "cartographie"
CACHE = RACINE / "donnees" / "transcriptions.json"

ARTICLES = ("les", "le", "la", "des", "du", "de")


def aplatir(t):
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", t)


def charger_alias():
    import openpyxl
    wb = openpyxl.load_workbook(CARTO / "cartographie_filiere.xlsx",
                                read_only=True, data_only=True)
    termes = {}

    def ajouter(alias, entite):
        if not alias or not entite:
            return
        base = aplatir(alias)
        if len(base) < 8:          # regle du 27/08 : sous 8 caracteres, non fiable
            return
        formes = {base}
        for art in ARTICLES:
            if base.startswith(art) and len(base) - len(art) >= 8:
                formes.add(base[len(art):])
        for f in formes:
            termes.setdefault(f, (str(alias).strip(), str(entite).strip()))

    for l in wb["Alias"].iter_rows(min_row=2, values_only=True):
        ajouter(l[0], l[2])
    for l in wb["Interprofessions"].iter_rows(min_row=2, values_only=True):
        ajouter(l[1], l[0])
        ajouter(l[3], l[0])
    wb.close()
    return termes


def transcription(vid):
    """Sous-titres automatiques francais. Rend le texte, ou None."""
    with tempfile.TemporaryDirectory() as d:
        try:
            r = subprocess.run(
                [sys.executable, "-m", "yt_dlp", "--skip-download",
                 "--write-auto-subs", "--sub-langs", "fr.*", "--sub-format", "vtt",
                 "--no-warnings", "-o", str(Path(d) / "s.%(ext)s"),
                 f"https://www.youtube.com/watch?v={vid}"],
                capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            return None
        if r.returncode != 0:
            return None
        fichiers = sorted(Path(d).glob("*.vtt"))
        if not fichiers:
            return None
        txt = fichiers[0].read_text(encoding="utf-8", errors="replace")

    lignes, vu = [], None
    for corps in re.findall(
            r"\d\d:\d\d:\d\d\.\d\d\d --> \d\d:\d\d:\d\d\.\d\d\d[^\n]*\n(.*?)(?=\n\n|\Z)",
            txt, re.S):
        for l in re.sub(r"<[^>]+>", "", corps).strip().splitlines():
            l = l.strip()
            if l and l != vu:
                lignes.append(l)
                vu = l
    return " ".join(lignes)


def charger_juges():
    """Les videos jugees, avec leur verdict et ce que la description donnait."""
    import openpyxl
    juges = {}
    for nom, col in [("A_VERIFIER.xlsx", 8), ("A_VERIFIER_2.xlsx", 9)]:
        f = CARTO / nom
        if not f.exists():
            continue
        ws = openpyxl.load_workbook(f, data_only=True)["a verifier"]
        for r in ws.iter_rows(min_row=2, values_only=True):
            if r[col]:
                juges[(str(r[1]), str(r[5])[:40])] = str(r[col])

    f = sorted(RECHERCHE.glob("detections_nettoyees_*.csv"))[-1]
    out = []
    with f.open(encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            v = juges.get((l["chaine"], l["titre"][:40]))
            if v:
                out.append({"video_id": l["video_id"], "chaine": l["chaine"],
                            "titre": l["titre"], "url": l["url"],
                            "abonnes": int(l["abonnes"] or 0), "verdict": v,
                            "vrai": v == "collaboration remuneree",
                            "entite_description": l["entites_retenues"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=120)
    args = ap.parse_args()

    termes = charger_alias()
    lignes = charger_juges()
    print(f"{len(termes)} formes d'alias | {len(lignes)} videos jugees",
          file=sys.stderr)

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    # les vraies collaborations d'abord : c'est sur elles que le rappel se joue
    lignes.sort(key=lambda l: (not l["vrai"], -l["abonnes"]))

    n = 0
    for l in lignes:
        if l["video_id"] in cache:
            continue
        if n >= args.max:
            break
        t = transcription(l["video_id"])
        cache[l["video_id"]] = t if t is not None else ""
        n += 1
        if n % 10 == 0:
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            print(f"  {n} transcriptions recuperees", file=sys.stderr)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    mesurables = [l for l in lignes if cache.get(l["video_id"])]
    for l in mesurables:
        plat = aplatir(cache[l["video_id"]])
        trouves = {e for f, (_a, e) in termes.items() if f in plat}
        l["entites_transcription"] = " | ".join(sorted(trouves))

    total_vrais = sum(1 for l in mesurables if l["vrai"])
    vus_t = [l for l in mesurables if l["entites_transcription"]]
    vus_d = [l for l in mesurables if l["entite_description"]]
    vt = sum(1 for l in vus_t if l["vrai"])
    vd = sum(1 for l in vus_d if l["vrai"])
    communs = sum(1 for l in mesurables
                  if l["vrai"] and l["entites_transcription"] and l["entite_description"])
    seuls_t = [l for l in mesurables
               if l["vrai"] and l["entites_transcription"] and not l["entite_description"]]

    md = [f"# Le signal « transcription », mesure — {Path(__file__).stem}", "",
          "Produit par `outils/mesurer_transcriptions.py`. Aucun quota d'API.", "",
          f"- Videos jugees par Vincent : **{len(lignes)}**",
          f"- Transcriptions obtenues : **{len(mesurables)}**",
          f"- Vraies collaborations dans cet ensemble : **{total_vrais}**", "",
          "| Signal | Retenus | Vrais | Precision | Rappel |",
          "|---|---:|---:|---:|---:|",
          f"| Transcription | {len(vus_t)} | {vt} | "
          f"{100*vt/len(vus_t) if vus_t else 0:.0f} % | "
          f"{100*vt/total_vrais if total_vrais else 0:.0f} % |",
          f"| Description | {len(vus_d)} | {vd} | "
          f"{100*vd/len(vus_d) if vus_d else 0:.0f} % | "
          f"{100*vd/total_vrais if total_vrais else 0:.0f} % |",
          "",
          "## Ce que la transcription apporte en plus", "",
          f"- Vraies collaborations vues par les deux : **{communs}**",
          f"- **Vues par la transcription SEULE : {len(seuls_t)}**", ""]
    if seuls_t:
        md += ["Ce sont les cas ou l'annonceur n'est nomme qu'a l'oral.", "",
               "| Chaine | Abonnes | Entite | Titre |", "|---|---:|---|---|"]
        for l in seuls_t[:30]:
            md += [f"| {l['chaine'][:22]} | {l['abonnes']:,} "
                   f"| {l['entites_transcription']} | {l['titre'][:44]} |".replace(",", " ")]
    else:
        md += ["**Aucune.** Sur cet echantillon, la transcription ne voit rien",
               "que la description ne voyait deja. C'est une mesure, et elle",
               "pese sur la decision de l'appliquer a grande echelle : elle",
               "coute plusieurs secondes par video.", ""]

    md += ["", "## Limite", "",
           "Les videos jugees viennent toutes du canal « description ». Une",
           "collaboration annoncee UNIQUEMENT a l'oral n'a jamais eu de raison",
           "d'entrer dans cet echantillon. **Le rappel de la transcription est",
           "donc structurellement sous-estime ici** — seul un tirage aleatoire",
           "le mesurerait honnetement.", ""]

    chemin = RECHERCHE / "mesure_transcriptions.md"
    chemin.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:16]))
    print(f"\nEcrit : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
