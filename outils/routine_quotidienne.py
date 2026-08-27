"""
Enchaine la collecte quotidienne, sans intervention humaine.

POURQUOI

Vincent, 27 aout 2026 : il veut que le projet avance pendant son sommeil sans
brûler son budget de conversation. Une session Claude ne peut pas se reveiller
seule ; un script planifie, si.

Tous les outils du projet ont ete ecrits avec reprise sur interruption,
plafond de quota et enregistrement continu — precisement pour ce moment.
Cette routine ne fait que les enchainer dans le bon ordre.

CE QU'ELLE FAIT, ET CE QU'ELLE NE FAIT PAS

Elle **collecte, trie et enregistre**. Elle ne **juge** rien : decider qu'un
candidat est une vraie collaboration, reperer un alias inconnu, corriger une
regle — tout cela demande une session avec Claude. La routine prepare le
materiau, l'analyse reste humaine.

ORDRE DES ETAPES

Les etapes qui consomment du quota d'abord, tant qu'il en reste ; les etapes
locales ensuite, qui reussissent toujours. Ainsi une journee ou le quota est
epuise produit quand meme un registre a jour.

TOLERANCE AUX PANNES

Chaque etape est isolee : si l'une echoue, les suivantes tournent quand meme.
Rien n'est fatal, tout est journalise. Le journal est ecrit dans
`recherche/routine/` — un fichier par jour, lisible sans outil.

Usage :
    python outils/routine_quotidienne.py
    python outils/routine_quotidienne.py --sans-quota   etapes locales seules
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
OUTILS = RACINE / "outils"
JOURNAL = RACINE / "recherche" / "routine"

# (nom lisible, script, arguments, consomme du quota ?)
ETAPES = [
    ("Moisson YouTube — catalogues des chaines surveillees",
     "moissonner_videos.py", ["--budget", "8000", "--max-videos", "600"], True),

    ("Croisement TikTok → YouTube — createurs restants",
     "croiser_tiktok_youtube.py", ["--budget", "1500"], True),

    ("Moisson TikTok — deux mois de plus",
     "moissonner_tiktok.py", [], True),

    # Sans quota, seulement du temps : c'est le travail ideal pour la nuit.
    # La transcription trouve ce qu'aucune description ne porte — « j'etais en
    # tournage pour les produits laitiers » (JOURNAL 59).
    ("Transcription en second rideau — chaines deja identifiees",
     "second_rideau_transcription.py", ["--videos", "400", "--par-chaine", "80", "--preuves-fortes"],
     False),

    ("Export de la moisson depuis le fichier de reprise",
     "exporter_moisson.py", [], False),

    ("Consolidation du registre des comptes",
     "consolider_comptes.py", [], False),

    ("Tri des detections — preuves fortes contre bruit",
     "nettoyer_detections.py", [], False),
]

SEPARATEUR = "-" * 72


def lancer(script, arguments, minutes=90):
    """Lance un outil, rend (code, sortie). Ne leve jamais."""
    debut = time.time()
    try:
        r = subprocess.run(
            [sys.executable, str(OUTILS / script)] + arguments,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=minutes * 60, cwd=str(RACINE))
        return r.returncode, (r.stdout or "") + (r.stderr or ""), time.time() - debut
    except subprocess.TimeoutExpired:
        return 124, f"ARRET : depassement de {minutes} minutes", time.time() - debut
    except Exception as e:
        return 1, f"ECHEC : {type(e).__name__} : {e}", time.time() - debut


def resume_utile(sortie):
    """Les lignes qui disent quelque chose, pas les milliers de lignes d'avancement."""
    garde = []
    for l in sortie.splitlines():
        s = l.strip()
        if not s:
            continue
        if any(m in s.lower() for m in (
                "quota", "erreur", "arret", "echec", "refus", "ecrit :",
                "comptes distincts", "preuves fortes", "videos examinees",
                "chaines", "contenus", "trouvees", "non telechargees",
                "detections lues", "ecartees")):
            garde.append(s)
    return garde[-25:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sans-quota", action="store_true",
                    help="n'execute que les etapes locales")
    args = ap.parse_args()

    JOURNAL.mkdir(parents=True, exist_ok=True)
    debut = datetime.now()
    chemin = JOURNAL / f"routine_{debut:%Y-%m-%d_%H%M}.txt"

    lignes = [
        f"ROUTINE QUOTIDIENNE — {debut:%Y-%m-%d %H:%M}",
        "",
        "Ce fichier dit ce qui a tourne cette nuit et ce que ca a produit.",
        "Il ne contient aucun jugement : la lecture des candidats reste humaine.",
        "",
        SEPARATEUR,
    ]

    bilan = []
    for nom, script, arguments, consomme in ETAPES:
        if args.sans_quota and consomme:
            lignes += [f"[ IGNOREE ] {nom}", "            (--sans-quota)", ""]
            continue
        if not (OUTILS / script).exists():
            lignes += [f"[ ABSENTE ] {nom}", f"            {script} introuvable", ""]
            bilan.append((nom, "outil absent"))
            continue

        print(f"→ {nom}", file=sys.stderr)
        code, sortie, duree = lancer(script, arguments)
        etat = "OK" if code == 0 else f"code {code}"
        bilan.append((nom, etat))
        lignes += [f"[ {etat:^8} ] {nom}",
                   f"            {script} {' '.join(arguments)}",
                   f"            duree : {duree/60:.1f} min", ""]
        for l in resume_utile(sortie):
            lignes.append(f"    {l}")
        lignes += ["", SEPARATEUR]

    fin = datetime.now()
    lignes += ["", f"Termine a {fin:%H:%M} — duree totale "
                   f"{(fin-debut).total_seconds()/60:.0f} min", "",
               "BILAN", ""]
    for nom, etat in bilan:
        lignes.append(f"  {etat:>10s}  {nom}")
    lignes += ["", "Prochaine etape : ouvrir une session avec Claude pour lire",
               "les nouveaux candidats et decider quoi en faire."]

    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes[-len(bilan) - 8:]))
    print(f"\nJournal : {chemin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
