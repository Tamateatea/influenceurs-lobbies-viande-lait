"""
Fabrique cartographie/A_FAIRE.xlsx — ce que Vincent a a faire, maintenant.

POURQUOI UN CLASSEUR ET PAS UN .md

Regle posee le 25/08 et rappelee depuis : « quand j'ouvre [le CSV], ce n'est
pas evident a lire pour moi, c'est meme illisible ». Tout ce qu'on demande a
Vincent arrive en classeur mis en forme. `TODO.md` reste pour les sessions de
Claude ; ce fichier-ci est pour lui.

CE QU'IL CONTIENT

Trois feuilles :

  1. **A FAIRE** — les taches, triees par ce qu'elles debloquent, pas par
     ordre d'arrivee. Avec, pour chacune, ce qui est bloque tant qu'elle n'est
     pas faite. Une tache dont personne n'attend rien n'a pas a etre en haut.
  2. **DECISIONS** — ce que Claude ne peut pas trancher : choix
     d'architecture, perimetre, arbitrages. Avec la recommandation et ce qui
     la fonde, pour qu'il decide vite sans avoir a relire le journal.
  3. **CE QUI TOURNE SANS TOI** — pour qu'il sache ce qu'il n'a PAS a faire.

Ce fichier est **regenere a chaque fois**. Il ne contient aucune reponse de
Vincent : les colonnes a remplir sont dans les classeurs de verification, pas
ici. On peut donc l'ecraser sans rien perdre.

Usage :  python outils/generer_a_faire.py
"""

import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

RACINE = Path(__file__).resolve().parent.parent
CIBLE = RACINE / "cartographie" / "A_FAIRE.xlsx"

ENTETE = PatternFill("solid", fgColor="434343")
ROUGE = PatternFill("solid", fgColor="F4CCCC")
JAUNE = PatternFill("solid", fgColor="FFF2CC")
VERT = PatternFill("solid", fgColor="D9EAD3")
GRIS = PatternFill("solid", fgColor="EFEFEF")

# (priorite, tache, ou, combien de temps, ce que ca debloque)
TACHES = [
    ("1 — le plus utile",
     "Trancher CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx",
     "cartographie/CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx",
     "20 min pour les 60 premieres lignes",
     "218 noms tires des videos publiees par les lobbies EUX-MEMES. DEUX "
     "questions, et elles debloquent deux mesures independantes. (1) Createur "
     "ou nom de serie ? — cela mesure la voie « motif dans le titre », 176 noms "
     "dont on ignore ce qu'elle vaut. (2) Quel TYPE de personne ? — cela "
     "tranche la question de la couverture du projet : nos deux methodes "
     "trouvent 36 et 42 createurs et n'ont qu'UN nom en commun. Soit on rate "
     "enormement, soit les deux methodes cherchent des gens differents. Si ces "
     "noms sont surtout des chefs et des eleveurs, c'est la seconde "
     "explication. Voir JOURNAL 62."),

    ("2",
     "Juger A_VERIFIER_3.xlsx",
     "cartographie/A_VERIFIER_3.xlsx",
     "30 min",
     "78 candidats jamais vus, sortis de la moisson complete (2 660 chaines, "
     "307 191 videos). Les 162 deja tranches sont ecartes automatiquement. "
     "Chaque jugement ameliore toutes les mesures de precision du projet."),

    ("3 — debloque Instagram",
     "Meta : obtenir un jeton UTILISATEUR",
     "facebook.com/ID puis Graph API Explorer, mode « User token », "
     "permission ads_read",
     "15 min une fois l'identite verifiee",
     "Instagram est entierement bloque la-dessus. Le jeton d'application est "
     "refuse. Sans ce jeton, aucune des trois plateformes n'est complete."),

    ("4",
     "Relever les abonnements des vitrines sur TikTok et YouTube",
     "Les memes comptes que sur Instagram",
     "20 min, format libre",
     "Les abonnements different d'une plateforme a l'autre. Envoie en vrac, "
     "meme mal colle : l'outil qui lit tes copier-coller existe deja."),

    ("5",
     "Relever les abonnements des GRANDES MARQUES",
     "Danone, Lactalis, Bel, Nestle France, puis Savencia, Sodiaal, "
     "Fleury Michon, Herta, LDC, Bigard",
     "30 min",
     "MESURE du 26/08 : 2,12 vraies pistes par chaine, contre 0,16 pour la "
     "semence TikTok — treize fois mieux. Jamais releves alors que ce sont "
     "des commanditaires directs."),

    ("6",
     "Chercher les noms de campagne sur les sites des lobbies",
     "produits-laitiers.com, la-viande.fr, volaille-francaise.fr, "
     "lefoiegras.fr",
     "20 min",
     "C'est le point faible identifie : completer la table d'alias rapporte "
     "plus que raffiner le filtre. Deux campagnes trouvees par hasard le "
     "26/08 — « En Mode Actif » et « Made in Viande »."),

    ("7 — a faire une fois",
     "Demander a L214 et Foodwatch si le registre existe deja",
     "Un courriel",
     "10 min",
     "Si quelqu'un l'a deja construit, autant le savoir avant d'y passer des "
     "semaines. Et si ce n'est pas le cas, ce sont des relais naturels."),

    ("8",
     "Demander a l'ARPP les donnees brutes de son Observatoire",
     "Un courriel",
     "10 min",
     "Source officielle sur les communications commerciales des influenceurs. "
     "Gratuite si elle est accordee."),

    ("9",
     "Verifier l'orthographe de @ouefsdefrance",
     "Instagram",
     "1 min",
     "Un « e » semble inverse dans la table d'alias. Si l'alias est faux, il "
     "ne peut rien trouver."),
]

# (question, recommandation, ce qui la fonde)
DECISIONS = [
    ("Quelle regle de detection garder ?",
     "La regle B — « un alias de la filiere ET du vocabulaire commercial dans "
     "la description ».",
     "MESURE du 27/08 sur 240 candidats : B fait 85 % de precision et 90 % de "
     "rappel. Les regles C, D et F font 85 % aussi, avec un rappel EGAL ou "
     "PIRE. Leurs intervalles de confiance se recouvrent entierement — on ne "
     "peut pas les departager. A performance egale, B est la seule qui n'ait "
     "ni liste ecrite a la main, ni reglage de proximite. Elle ne peut donc "
     "pas se perimer quand un nouveau commanditaire arrive. "
     "Consequence : la liste GENERIQUES disparait au lieu d'etre corrigee. "
     "Voir JOURNAL 61."),

    ("Faut-il continuer a versionner le fichier de reprise de la moisson ?",
     "Le compresser plutot que choisir entre le garder et le perdre.",
     "donnees/moisson_videos.json pese 26 Mo et git en garde une copie entiere "
     "a chaque commit ; le depot fait deja 40 Mo. Mais ce fichier vaut trois "
     "jours de quota d'API qu'on ne rachete pas. Compresse en .json.gz il "
     "ferait environ 4 Mo, et resterait une sauvegarde. Voir TODO.md."),

    ("Le CNPO (oeufs) est-il dans le perimetre ?",
     "A toi de trancher — le classeur et la conversation se contredisent.",
     "cartographie_filiere.xlsx marque le CNPO « HORS PERIMETRE », alors que "
     "tu avais confirme « Oeufs de France » le 25/08 comme une piste a suivre. "
     "Aucun CNPO n'est retenu en pratique aujourd'hui, donc rien n'est casse, "
     "mais les deux sources ne disent pas la meme chose. Voir JOURNAL 60."),

    ("METHODOLOGIE 9.2 prescrit une mesure impossible. La reecrire ?",
     "Oui — remplacer le tirage aleatoire par la capture-recapture.",
     "La section demande de tirer des createurs au hasard et de les annoter "
     "exhaustivement, pour savoir ce que le projet rate. MESURE du 27/08 : "
     "1,35 % des chaines portent une preuve forte, donc il faudrait en annoter "
     "739 A LA MAIN pour en obtenir dix, soit 28 % du registre. Et 83 % pour en "
     "obtenir trente. Ce n'est pas un manque de temps, c'est arithmetiquement "
     "impossible. La voie de rechange existe deja en section 9.3 — et les "
     "chaines des lobbies sont la seconde source independante qui manquait. "
     "Voir JOURNAL 62."),

    ("Qui publie le registre, et sous quel nom ?",
     "Question ouverte, sans urgence technique.",
     "Elle devient urgente le jour ou le premier nom sort. Rien ne se publie "
     "sans verification humaine — METHODOLOGIE section 9."),
]

FAIT_SANS_TOI = [
    ("Moisson YouTube", "TERMINEE",
     "2 660 chaines sur 2 660, 307 191 videos examinees. Premiere revue "
     "complete du registre."),
    ("Les quatre signaux YouTube", "TOUS MESURES",
     "Case de declaration 91 % / 44 %, transcription 81 % / 49 %, description "
     "78 % / 100 %, SponsorBlock 69 % / 13 %."),
    ("Transcription en second rideau", "FAITE",
     "232 videos sans signal en description, sur les chaines deja "
     "identifiees. Quatre liens Inoxtag x CNIEL trouves, dont « j'etais en "
     "tournage pour les produits laitiers »."),
    ("Artefacts d'aplatissement", "MESURES ET CORRIGES",
     "10 % des candidats etaient des mots colles a leurs voisins — « viande, "
     "frites » declenchait @la_viande_fr. 244 retires, aucun vrai cas perdu."),
    ("Le tirage aleatoire de METHODOLOGIE 9.2", "MESURE IMPOSSIBLE",
     "Il faudrait annoter 739 chaines a la main pour en obtenir dix qui portent "
     "une preuve. La prescription doit etre revue — c'est une decision de "
     "methode, elle est dans l'onglet DECISIONS."),
    ("Les six regles de detection", "REMESUREES",
     "B, C, D et F font toutes 85 % de precision. B a le meilleur rappel et "
     "n'a aucune liste ecrite a la main. Recommandation dans l'onglet "
     "DECISIONS."),
    ("Moisson TikTok", "BLOQUEE JUSQU'A DEMAIN",
     "Quota journalier epuise a 5 mois sur 47. Reprend toute seule, les 42 "
     "mois restants ne sont pas marques faits."),
    ("Instagram", "BLOQUE SUR TOI",
     "Rien ne peut avancer sans le jeton Meta — tache 3."),
]


def feuille(wb, titre, colonnes, lignes, couleurs=None):
    ws = wb.create_sheet(titre)
    for j, (nom, largeur) in enumerate(colonnes, 1):
        c = ws.cell(row=1, column=j, value=nom)
        c.fill = ENTETE
        c.font = Font(bold=True, color="FFFFFF", size=11)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = largeur
    ws.row_dimensions[1].height = 30
    for i, ligne in enumerate(lignes, 2):
        for j, v in enumerate(ligne, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.alignment = Alignment(vertical="top", wrap_text=True)
            if couleurs:
                f = couleurs(i - 2, j)
                if f:
                    c.fill = f
        ws.row_dimensions[i].height = 76
    ws.freeze_panes = ws.cell(row=2, column=1)
    return ws


def main():
    wb = Workbook()
    wb.remove(wb.active)

    def couleur_taches(i, j):
        if j != 1:
            return None
        return ROUGE if i < 3 else (JAUNE if i < 6 else GRIS)

    feuille(wb, "A FAIRE",
            [("Priorite", 20), ("Tache", 42), ("Ou", 34), ("Combien de temps", 18),
             ("Pourquoi, et ce que ca debloque", 76)],
            TACHES, couleur_taches)

    feuille(wb, "DECISIONS",
            [("La question", 40), ("Ce que je recommande", 44),
             ("Sur quoi je me fonde", 82)],
            DECISIONS, lambda i, j: VERT if j == 2 else None)

    feuille(wb, "CE QUI TOURNE SANS TOI",
            [("Chantier", 32), ("Etat", 26), ("Detail", 76)],
            FAIT_SANS_TOI,
            lambda i, j: (VERT if j == 2 and i < 4 else
                          (JAUNE if j == 2 else None)))

    ws = wb.create_sheet("LIS-MOI D'ABORD", 0)
    texte = [
        f"OU EN EST LE PROJET — {date.today().strftime('%d/%m/%Y')}",
        "",
        "Trois feuilles, dans cet ordre :",
        "",
        "  A FAIRE — ce qui t'attend, trie par ce que ca debloque. Le rouge "
        "d'abord.",
        "  DECISIONS — ce que je ne peux pas trancher a ta place. J'ai mis une "
        "recommandation et sur quoi elle se fonde.",
        "  CE QUI TOURNE SANS TOI — pour que tu saches ce que tu n'as PAS a "
        "faire.",
        "",
        "SI TU N'AS QUE VINGT MINUTES",
        "",
        "Ouvre CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx et juge les soixante "
        "premieres lignes.",
        "C'est la seule tache dont dependent DEUX mesures qu'on ne peut pas "
        "faire sans toi : ce que vaut une de nos deux methodes de detection, "
        "et quelle part des collaborations le projet voit.",
        "",
        "CE QUI A CHANGE AUJOURD'HUI",
        "",
        "La moisson YouTube est terminee : 2 660 chaines, 307 191 videos.",
        "Les quatre signaux sont mesures. 40 vraies collaborations sur 71 ne "
        "sont pas declarees — c'est le chiffre qui justifie le projet.",
        "La transcription a trouve, a l'oral et nulle part ailleurs : "
        "« j'etais en tournage pour les produits laitiers » (Inoxtag, "
        "janvier 2024).",
        "",
        "ET UNE ERREUR QUE JE DOIS SIGNALER",
        "",
        "L'outil qui lit les chaines des lobbies attribuait des videos a la "
        "mauvaise personne.",
        "« Norman, 11,2 M d'abonnes » etait en realite « e-Boucherie "
        "NORMANde ». Inoxtag et Squeezie ne resistent pas non plus a la "
        "correction. Mister V, lui, est confirme.",
        "C'etait ecrit dans ETAT.md, que toute nouvelle session lit en "
        "premier. Corrige, avec un renvoi dans le journal.",
    ]
    for i, l in enumerate(texte, 1):
        c = ws.cell(row=i, column=1, value=l)
        c.font = Font(bold=bool(l) and l.isupper(), size=11)
    ws.column_dimensions["A"].width = 104

    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"{len(TACHES)} taches, {len(DECISIONS)} decisions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
