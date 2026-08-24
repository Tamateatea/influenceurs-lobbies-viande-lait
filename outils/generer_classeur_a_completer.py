"""
Fabrique cartographie/A_COMPLETER.xlsx — le classeur que Vincent remplit.

Principe : ce classeur ne contient QUE des questions auxquelles seul un humain
peut repondre. Une question par ligne. Une seule colonne a remplir, en vert.
Tout le reste est en gris et ne se touche pas.

SECURITE : ce script REFUSE d'ecraser un classeur existant, parce qu'il
contiendrait des reponses. Pour le regenerer, renommer l'ancien d'abord.

Usage :  python outils/generer_classeur_a_completer.py
"""

import csv
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

RACINE = Path(__file__).resolve().parent.parent
CIBLE = RACINE / "cartographie" / "A_COMPLETER.xlsx"

VERT = PatternFill("solid", fgColor="D9EAD3")      # a toi de remplir
GRIS = PatternFill("solid", fgColor="EFEFEF")      # ne pas toucher
ENTETE = PatternFill("solid", fgColor="38761D")
JAUNE = PatternFill("solid", fgColor="FFF2CC")     # priorite 1
BLANC_GRAS = Font(bold=True, color="FFFFFF", size=11)
LIEN = Font(color="0563C1", underline="single")
BORD = Border(*[Side(style="thin", color="BBBBBB")] * 4)
HAUT_GAUCHE = Alignment(vertical="top", wrap_text=True)

ROLE_VITRINE = (
    "On recupere la liste des comptes que CE compte SUIT. C'est le lobby "
    "lui-meme qui designe les createurs qui l'interessent : signal non "
    "circulaire, contrairement a une liste qu'on aurait devinee."
)
ROLE_TEMOIN = (
    "HORS PERIMETRE viande/lait. Sert de GROUPE TEMOIN : meme dispositif de "
    "communication, autre filiere. Permet de verifier qu'une methode trouve "
    "bien ce qu'elle doit trouver, et pas n'importe quoi."
)


def dernier_releve():
    """Le CSV de test croise le plus recent, ou None."""
    fichiers = sorted((RACINE / "recherche").glob("test_croise_youtube_*.csv"))
    return fichiers[-1] if fichiers else None


def videos_a_arbitrer():
    f = dernier_releve()
    if not f:
        return [], "(aucun releve trouve)"
    with f.open(encoding="utf-8") as fh:
        lignes = [x for x in csv.DictReader(fh) if x["cas"] == "sponsorblock_seul"]
    return lignes, f.name


def mise_en_forme(ws, largeurs):
    for i, l in enumerate(largeurs, start=1):
        ws.column_dimensions[get_column_letter(i)].width = l
    for c in ws[1]:
        c.fill, c.font = ENTETE, BLANC_GRAS
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 32
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def texte_simple(ws, lignes, largeur=100):
    ws.column_dimensions["A"].width = largeur
    for i, (t, gras) in enumerate(lignes, start=1):
        c = ws.cell(row=i, column=1, value=t)
        c.font = Font(bold=gras, size=13 if gras else 11)
        c.alignment = HAUT_GAUCHE


def feuille_commencer_ici(wb):
    ws = wb.create_sheet("COMMENCER ICI")
    texte_simple(ws, [
        ("Comment marche ce classeur", True),
        ("", False),
        ("Une question par ligne. Tu ne remplis QUE les colonnes VERTES.", False),
        ("Les colonnes grises sont la pour t'expliquer : ne les modifie pas.", False),
        ("Les liens bleus sont cliquables : un clic ouvre la page.", False),
        ("La colonne Prio surlignee en jaune = a faire en premier.", False),
        ("", False),
        ("Quand tu as fini une session de remplissage, dis-le a Claude :", False),
        ("il relit ce fichier et reporte tes reponses dans le projet.", False),
        ("", False),
        ("Si tu ne sais pas repondre, ecris « je ne sais pas ». C'est une", False),
        ("reponse utile : elle dit qu'il faut chercher autrement.", False),
        ("", False),
        ("Trois astuces Excel qui rendent n'importe quel tableau lisible", True),
        ("", False),
        ("1. FIGER LES TITRES — onglet Affichage > Figer les volets.", False),
        ("   Les titres restent visibles quand tu descends. (Deja fait ici.)", False),
        ("", False),
        ("2. FILTRER — onglet Donnees > Filtrer. De petites fleches apparaissent", False),
        ("   sur les titres : tu peux n'afficher que la priorite 1, par exemple.", False),
        ("   (Deja fait ici.)", False),
        ("", False),
        ("3. RENVOYER A LA LIGNE — selectionne tout (Ctrl+A), puis onglet", False),
        ("   Accueil > Renvoyer a la ligne automatiquement. Le texte long", False),
        ("   s'affiche en entier au lieu d'etre coupe. C'est exactement ce qui", False),
        ("   rendait la cartographie penible a lire : essaie-le dessus.", False),
    ])


def feuille_a_faire(wb, videos, nom_releve):
    ws = wb.create_sheet("1. A FAIRE")
    ws.append(["N", "Prio", "Ce que tu dois faire", "Ou regarder",
               "TA REPONSE  (a remplir)", "Ton commentaire libre",
               "Pourquoi ca compte"])

    dv_video = DataValidation(
        type="list",
        formula1='"vrai sponsor exterieur,auto-promotion Inoxtag,je ne sais pas"',
        allow_blank=True)
    dv_etat = DataValidation(
        type="list", formula1='"fait,pas encore,bloque"', allow_blank=True)
    ws.add_data_validation(dv_video)
    ws.add_data_validation(dv_etat)

    n = 0
    prio1 = []

    pourquoi_video = (
        "« Segment SponsorBlock sans declaration » ne veut rien dire tant qu'on "
        "n'a pas verifie que ce n'est pas Inoxtag faisant la promotion de ses "
        "propres projets. Releve : " + nom_releve
    )
    for v in videos:
        n += 1
        ws.append([n, 1,
                   "Ouvrir cette video, aller au segment marque « sponsor », et "
                   "dire ce que c'est",
                   "", "", "", pourquoi_video])
        r = ws.max_row
        c = ws.cell(row=r, column=4, value=(v["titre"][:50] or v["video_id"]))
        c.hyperlink = v["url"]
        c.font = LIEN
        dv_video.add(ws.cell(row=r, column=5))
        prio1.append(r)

    autres = [
        (1, "Confirmer le compte Instagram officiel d'INAPORC (filiere porc)",
         "https://www.instagram.com/", True,
         "La table d'alias est le coeur du projet : sans le pseudo exact, on ne "
         "peut pas relier une publication au lobby qui la finance."),
        (1, "Confirmer le compte Instagram officiel d'ANVOL (volaille)",
         "https://www.instagram.com/", True, "Idem."),
        (1, "Confirmer le compte Instagram officiel de CIFOG (foie gras)",
         "https://www.instagram.com/", True,
         "Idem. Forte activite saisonniere : utile en fin d'annee."),
        (2, "Confirmer le compte Instagram officiel de CNPO (oeufs)",
         "https://www.instagram.com/", True,
         "Hors perimetre strict, mais meme dispositif : utile en comparaison."),
        (2, "Chercher si CLIPP (filiere lapin) a un compte vitrine",
         "https://www.instagram.com/", True,
         "Petite structure. Si elle n'a rien, c'est aussi une information."),
        (1, "Coller le jeton d'acces Meta dans SECRETS.txt, a la racine du "
            "projet. PAS dans ce classeur : il peut finir sur GitHub.",
         "https://developers.facebook.com/tools/explorer/", False,
         "Sans jeton, impossible de tester si l'API Ad Library expose les "
         "contenus de marque pour la France."),
        (2, "Creer le depot GitHub prive et donner l'URL a Claude",
         "https://github.com/new", False,
         "Aujourd'hui le projet n'existe qu'a un seul endroit."),
        (3, "Contacter Paye Ton Influence — partenariat de diffusion",
         "", False,
         "Ils travaillent deja Interbev et Cniel. Partenaire naturel."),
        (3, "Demander a L214 et Foodwatch si quelqu'un tient deja ce registre",
         "", False, "Eviter de refaire un travail qui existe."),
    ]
    for prio, quoi, lien, libre, pourquoi in autres:
        n += 1
        ws.append([n, prio, quoi, "", "", "", pourquoi])
        r = ws.max_row
        if lien:
            c = ws.cell(row=r, column=4, value="ouvrir")
            c.hyperlink = lien
            c.font = LIEN
        else:
            ws.cell(row=r, column=4, value="—")
        if not libre:
            dv_etat.add(ws.cell(row=r, column=5))
        if prio == 1:
            prio1.append(r)

    for r in range(2, ws.max_row + 1):
        for col in range(1, 8):
            c = ws.cell(row=r, column=col)
            c.alignment = HAUT_GAUCHE
            c.border = BORD
            if col in (5, 6):
                c.fill = VERT
            elif col in (3, 7):
                c.fill = GRIS
        ws.row_dimensions[r].height = 46
        if r in prio1:
            ws.cell(row=r, column=2).fill = JAUNE
            ws.cell(row=r, column=2).font = Font(bold=True)

    mise_en_forme(ws, [5, 6, 46, 30, 30, 30, 52])


def feuille_comptes(wb):
    ws = wb.create_sheet("2. COMPTES VITRINES")
    ws.append(["Prio", "Entite", "Filiere", "Compte vitrine connu",
               "Etat du pseudo", "PSEUDO EXACT (a remplir)",
               "LISTE RECUPEREE ? (a remplir)", "A quoi ca sert"])

    donnees = [
        (1, "CNIEL", "Lait de vache", "@lesproduitslaitiers", "CONFIRME", ROLE_VITRINE),
        (1, "INTERBEV", "Viandes (bovin, ovin, veau, equin, caprin)",
            "@la_viande_fr", "CONFIRME", ROLE_VITRINE),
        (2, "INAPORC", "Porc", "« Le Porc Francais » — pseudo inconnu",
            "A CONFIRMER", ROLE_VITRINE),
        (2, "ANVOL", "Volaille de chair", "« Volaille Francaise » — pseudo inconnu",
            "A CONFIRMER", ROLE_VITRINE),
        (2, "CIFOG", "Palmipedes a foie gras", "« Le Foie Gras » — pseudo inconnu",
            "A CONFIRMER", ROLE_VITRINE),
        (3, "CNPO", "Oeufs", "« Oeufs de France » — pseudo inconnu", "A CONFIRMER",
            "Hors perimetre strict. " + ROLE_VITRINE),
        (3, "CLIPP", "Lapin", "inconnu", "A CHERCHER",
            "Petite structure. " + ROLE_VITRINE),
        (3, "Intercereales", "Cereales", "@lescereales", "CONFIRME", ROLE_TEMOIN),
        (3, "FNPSMS", "Mais", "@cetepimepate", "CONFIRME", ROLE_TEMOIN),
    ]
    dv = DataValidation(type="list",
                        formula1='"oui,pas encore,compte introuvable"',
                        allow_blank=True)
    ws.add_data_validation(dv)

    for prio, ent, fil, compte, etat, sert in donnees:
        ws.append([prio, ent, fil, compte, etat, "", "", sert])
        r = ws.max_row
        dv.add(ws.cell(row=r, column=7))
        for col in range(1, 9):
            c = ws.cell(row=r, column=col)
            c.alignment = HAUT_GAUCHE
            c.border = BORD
            c.fill = VERT if col in (6, 7) else GRIS
        ws.row_dimensions[r].height = 50
        if prio == 1:
            ws.cell(row=r, column=1).fill = JAUNE
            ws.cell(row=r, column=1).font = Font(bold=True)

    mise_en_forme(ws, [7, 15, 26, 34, 16, 26, 24, 58])


def feuille_ou_coller(wb):
    ws = wb.create_sheet("2b. OU COLLER LES LISTES")
    texte_simple(ws, [
        ("Ou coller les listes d'abonnements", True),
        ("", False),
        ("PAS dans ce classeur. Dans le dossier :", False),
        ("      donnees/comptes_vitrines/", False),
        ("", False),
        ("Un fichier texte par compte, nomme d'apres le compte :", False),
        ("      lesproduitslaitiers.txt", False),
        ("      la_viande_fr.txt", False),
        ("", False),
        ("Colle le copier-coller brut, sans le nettoyer : Claude s'en charge.", False),
        ("Ecris en premiere ligne la date du jour — une liste d'abonnements", False),
        ("change dans le temps, et on doit savoir de quand elle date.", False),
        ("", False),
        ("Le dossier contient un LISEZ-MOI.txt qui redit tout ceci.", False),
    ])


def main():
    if CIBLE.exists():
        print(f"REFUS : {CIBLE.name} existe deja et contient peut-etre tes reponses.")
        print("Renomme-le d'abord si tu veux vraiment le regenerer.")
        return 1

    videos, nom_releve = videos_a_arbitrer()
    wb = Workbook()
    wb.remove(wb.active)
    feuille_commencer_ici(wb)
    feuille_a_faire(wb, videos, nom_releve)
    feuille_comptes(wb)
    feuille_ou_coller(wb)
    CIBLE.parent.mkdir(exist_ok=True)
    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"  {len(videos)} videos a arbitrer, reprises de {nom_releve}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
