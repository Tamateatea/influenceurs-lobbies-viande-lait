"""
Fabrique cartographie/MES_TACHES.xlsx — tout ce qui bloque Claude, en un fichier.

POURQUOI

Vincent, 26 aout 2026 : « j'ai parfois peur que tu n'oses pas me demander de
faire des taches qui te bloquent ». C'etait fonde : les listes de taches
donnees jusqu'ici etaient partielles, deux ou trois points a la fois, alors
que dix choses attendaient.

Ce classeur les rassemble toutes, avec pour chacune ce qu'il faut faire, ou,
combien de temps, et **ce que ca debloque**. Il remplace les listes envoyees
dans la conversation, qui se perdent.

Regle METHODOLOGIE 13.4 : classeur Excel mis en forme, colonnes a remplir en
vert, jamais de CSV ni de Markdown.

SECURITE : refuse d'ecraser un classeur existant, qui contiendrait des reponses.

Usage :  python outils/generer_mes_taches.py
"""

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

RACINE = Path(__file__).resolve().parent.parent
CIBLE = RACINE / "cartographie" / "MES_TACHES.xlsx"

VERT = PatternFill("solid", fgColor="D9EAD3")
GRIS = PatternFill("solid", fgColor="F3F3F3")
JAUNE = PatternFill("solid", fgColor="FFF2CC")
ROUGE = PatternFill("solid", fgColor="F4CCCC")
ENTETE = PatternFill("solid", fgColor="38761D")
BORD = Border(*[Side(style="thin", color="CCCCCC")] * 4)
HAUT = Alignment(vertical="top", wrap_text=True)
LIEN = Font(color="0563C1", underline="single")

FAIT = DataValidation(type="list", formula1='"fait,en cours,pas encore,bloque"',
                      allow_blank=True)

# --- Les taches, par ordre de ce qu'elles debloquent -------------------------
TACHES = [
    (1, "Relever les abonnements des GRANDES MARQUES sur Instagram",
     "Onglet « 2. COMPTES A RELEVER ». Pour chaque compte : ouvrir, aller dans "
     "« abonnements » (les comptes que LUI suit), derouler jusqu'en bas, tout "
     "copier, coller dans un fichier texte du dossier donnees/comptes_vitrines/",
     "~1 h pour les 10",
     "MESURE : cette semence produit 2,12 vraies pistes par chaine surveillee, "
     "contre 0,16 pour les createurs TikTok. C'est treize fois plus rentable "
     "que tout le reste. Et les marques n'ont JAMAIS ete relevees, alors que "
     "ce sont des commanditaires directs — ta remarque du 24/08."),

    (2, "Chercher les NOMS DE CAMPAGNE des lobbies",
     "Onglet « 3. ALIAS A CHERCHER ». Parcourir les sites listes et noter tout "
     "nom de campagne, slogan, hashtag ou site dedie.",
     "~30 min",
     "C'est le point faible identifie ce matin. Deux campagnes ont ete trouvees "
     "par hasard aujourd'hui — « En Mode Actif » (CNIEL) et « Made in Viande » "
     "(INTERBEV) — toutes deux dans des donnees deja collectees. Ameliorer le "
     "filtre ne sert plus a rien ; completer la table d'alias, si."),

    (3, "Juger les 5 candidats retenus par la regle D",
     "Fichier cartographie/A_VERIFIER_2.xlsx, filtrer sur « Retenu par la "
     "regle D » = OUI. Quatre sont des videos Studio Danielle quasi certaines.",
     "~10 min",
     "Ces jugements servent de jeu de reference sur des entites jamais testees. "
     "Sans eux on ne sait pas si la regle tient hors du CNIEL."),

    (4, "Confirmer les pseudos Instagram des marques",
     "Onglet « 2. COMPTES A RELEVER », colonne verte « pseudo exact ». Si tu ne "
     "trouves pas un compte, ecris « aucun trouve » — c'est une reponse utile.",
     "inclus dans la tache 1",
     "Un pseudo sans sa plateforme n'est pas une donnee (METHODOLOGIE 8). "
     "Trois pseudos supposes se sont reveles faux ou sur une autre plateforme."),

    (5, "Meta : obtenir un jeton UTILISATEUR",
     "Le jeton d'application est refuse par l'API (« Application does not have "
     "permission »). Il faut : 1) verifier ton identite sur facebook.com/ID "
     "(piece d'identite, 1 a 2 jours) ; 2) dans developers.facebook.com > "
     "Tools > Graph API Explorer, choisir « User token » et non « App token », "
     "ajouter la permission ads_read, generer.",
     "~15 min + 1 a 2 j d'attente",
     "Debloque l'hypothese IG-02 : l'API Ad Library expose-t-elle les contenus "
     "de marque ? Si oui, Instagram devient interrogeable par commanditaire. "
     "ATTENTION : elle ne donnera PAS les nombres d'abonnes."),

    (6, "Relever les abonnements des vitrines sur TIKTOK et YOUTUBE",
     "Les memes comptes qu'Instagram — @lesproduitslaitiers, @la_viande_fr, "
     "@leporcfrancais, @volaillefrancaise — mais sur TikTok et YouTube. Leurs "
     "abonnements y sont differents.",
     "~30 min",
     "Meme rendement attendu que la semence Instagram, sur une population de "
     "createurs differente."),

    (7, "Chercher les comptes REGIONAUX d'INTERBEV",
     "interbev.fr mentionne des structures regionales (INTERBEV Occitanie, "
     "InterbevGrandEst deja reperes). Chercher leurs comptes sociaux.",
     "~20 min",
     "Les campagnes regionales touchent des createurs locaux, invisibles depuis "
     "les comptes nationaux."),

    (8, "Verifier l'orthographe de @ouefsdefrance",
     "Le pseudo releve le 24/08 semble avoir un « e » inverse. Verifier sur "
     "Instagram et corriger si besoin.",
     "2 min",
     "Detail, mais un identifiant faux dans le registre est un identifiant "
     "inutilisable."),

    (9, "Decider : faut-il ecrire aux createurs ?",
     "Proposition que TU as faite le 25/08 : contacter le createur avant "
     "publication vaut verification et droit de reponse. A trancher : le "
     "fait-on, a partir de quand, et sous quelle signature ?",
     "reflexion",
     "Determine la posture du projet et une partie de sa protection juridique. "
     "Aucune urgence, mais rien ne peut se publier sans que ce soit tranche."),

    (10, "Decider : qui publie le registre ?",
     "Toi en nom propre, une association existante, une nouvelle structure ? "
     "Question ouverte depuis la premiere session.",
     "reflexion",
     "Determine la posture juridique. Bloque toute publication."),
]

# --- Les comptes dont il faut relever les abonnements ------------------------
COMPTES = [
    # priorite, entite, groupe, pseudo suppose, pourquoi
    (1, "Danone", "7 marques au classeur : Actimel, Activia, Danette, Gervais, "
        "Velouté, Danio, Danonino", "@danone.france ?",
        "Le plus gros portefeuille laitier du classeur. Annonceur TikTok confirme "
        "(17 pubs via WPP Media France)."),
    (1, "Lactalis", "6 marques : Président, Lactel, Galbani, Bridel, Société, "
        "La Laitière", "@lactalis ?",
        "Deuxieme portefeuille. Annonceur TikTok confirme via Havas Media."),
    (1, "Groupe Bel", "5 marques : Babybel, La Vache qui rit, Kiri, Boursin, Leerdammer",
        "@bel_group ?",
        "56 publicites TikTok via Publicis Media - Starcom. Le plus actif des "
        "annonceurs laitiers sur TikTok."),
    (1, "Nestlé France", "La Laitière (licence), Herta (co-detenue)", "@nestlefrance ?",
        "38 publicites TikTok. Sort sur les termes « lait », « viande » et « Charal »."),
    (2, "Savencia", "7 marques : Caprice des Dieux, Tartare, Saint Morêt, Elle & Vire",
        "@savencia ?", "Publicites TikTok via Publicis Media - Blue449."),
    (2, "Sodiaal / Candia", "4 marques : Candia, Yoplait, Entremont, Regilait",
        "@candia_officiel ?", "8 publicites TikTok via Vanksen."),
    (2, "Fleury Michon", "charcuterie", "@fleurymichon ?",
        "60 publicites TikTok, en regie propre."),
    (2, "Herta", "charcuterie", "@herta_france",
        "Pseudo DEJA CONFIRME : il apparait dans les abonnements d'INAPORC et "
        "a 13 contenus commerciaux TikTok."),
    (3, "LDC", "4 marques : Le Gaulois, Maître Coq, Marie, Loué", "@legaulois ?",
        "Volaille et plats prepares. « Marie » et « Maître Coq » ont produit "
        "beaucoup de faux positifs : leurs comptes aideront a les distinguer."),
    (3, "Bigard", "Charal, Socopa", "@charal_officiel ?",
        "Premier groupe de viande francais. Socopa a 5 publicites TikTok."),
    (2, "Naturellement Flexitariens", "campagne INTERBEV", "@naturellementflexitariens ?",
        "Campagne citee par Valouzz dans une collaboration confirmee. Site dedie : "
        "naturellement-flexitariens.fr"),
    (2, "En Mode Actif", "campagne CNIEL, cofinancee par l'UE", "?",
        "Trouvee ce matin dans les descriptions de Studio Danielle. Chercher si "
        "elle a un compte propre."),
    (3, "Made in Viande", "operation INTERBEV, portes ouvertes", "?",
        "Trouvee ce matin dans les descriptions de FlorianOnAir."),
]

# --- Ou chercher des noms de campagne ----------------------------------------
ALIAS = [
    ("produits-laitiers.com", "https://www.produits-laitiers.com", "CNIEL",
     "Site grand public. Chercher les rubriques campagne, les hashtags, les "
     "operations nommees. « En Mode Actif » en venait."),
    ("filiere-laitiere.fr", "https://www.filiere-laitiere.fr", "CNIEL",
     "Site institutionnel. Les rapports d'activite nomment les campagnes."),
    ("la-viande.fr", "https://www.la-viande.fr", "INTERBEV",
     "Site grand public. « Aimez la viande, mangez-en mieux » en vient."),
    ("interbev.fr", "https://www.interbev.fr", "INTERBEV",
     "Site institutionnel. Chercher aussi les structures regionales."),
    ("naturellement-flexitariens.fr", "https://naturellement-flexitariens.fr",
     "INTERBEV", "Site dedie a une campagne. Cite par Valouzz."),
    ("leporc.com", "https://www.leporc.com", "INAPORC",
     "A deja donne la rubrique « Les recettes des influenceurs ». Chercher "
     "d'autres operations nommees."),
    ("volaille-francaise.fr", "https://www.volaille-francaise.fr", "ANVOL",
     "Jamais explore."),
    ("lefoiegras.fr", "https://www.lefoiegras.fr", "CIFOG",
     "Jamais explore. CIFOG a produit 91 faux positifs faute de bon alias."),
]


def mise_en_forme(ws, largeurs, hauteur=1):
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = ENTETE
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 32
    for i, w in enumerate(largeurs, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = HAUT
            c.border = BORD
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def main():
    if CIBLE.exists():
        print(f"REFUS : {CIBLE.name} existe deja.", file=sys.stderr)
        print("Renomme-le d'abord si tu veux le regenerer.", file=sys.stderr)
        return 1

    wb = Workbook()

    # ---------- onglet 0 : comment faire ----------
    aide = wb.active
    aide.title = "COMMENCER ICI"
    aide.column_dimensions["A"].width = 104
    textes = [
        ("Tout ce qui bloque Claude, en un seul fichier", True),
        ("", False),
        ("Quatre onglets :", False),
        ("", False),
        ("  1. MES TACHES          la liste complete, par ordre de rendement", False),
        ("  2. COMPTES A RELEVER   les comptes dont copier les abonnements", False),
        ("  3. ALIAS A CHERCHER    ou trouver des noms de campagne", False),
        ("", False),
        ("Tu ne remplis que les colonnes VERTES.", False),
        ("Les liens bleus sont cliquables.", False),
        ("", False),
        ("Si tu ne fais qu'une chose ce soir", True),
        ("", False),
        ("La tache 1 : relever les abonnements des grandes marques.", False),
        ("", False),
        ("Mesure du 26/08 : cette source produit 2,12 vraies pistes par chaine", False),
        ("surveillee, contre 0,16 pour les createurs TikTok. Treize fois plus.", False),
        ("Et aucune marque n'a jamais ete relevee, alors que ce sont des", False),
        ("commanditaires directs — c'est toi qui l'avais signale le 24/08.", False),
        ("", False),
        ("Comment relever une liste d'abonnements", True),
        ("", False),
        ("1. Ouvrir le compte sur Instagram", False),
        ("2. Cliquer sur « abonnements » — les comptes que LUI suit,", False),
        ("   PAS ses abonnes", False),
        ("3. DEROULER JUSQU'EN BAS avant de selectionner : la liste se charge", False),
        ("   par paquets, une selection prematuree ne prend que le premier", False),
        ("4. Tout copier, coller dans un fichier .txt nomme d'apres le compte,", False),
        ("   dans donnees/comptes_vitrines/", False),
        ("5. Mettre la date du jour en premiere ligne du fichier", False),
        ("", False),
        ("Pas besoin de nettoyer : le script s'en charge.", False),
    ]
    for i, (t, gras) in enumerate(textes, start=1):
        c = aide.cell(row=i, column=1, value=t)
        c.font = Font(bold=gras, size=13 if gras else 11)
        c.alignment = HAUT

    # ---------- onglet 1 : les taches ----------
    ws = wb.create_sheet("1. MES TACHES")
    ws.append(["N", "Ce qu'il faut faire", "Comment", "Temps",
               "Ce que ca debloque", "OU EN ES-TU ?", "Ton commentaire"])
    ws.add_data_validation(FAIT)
    for n, quoi, comment, temps, pourquoi in TACHES:
        ws.append([n, quoi, comment, temps, pourquoi, "", ""])
        r = ws.max_row
        FAIT.add(ws.cell(row=r, column=6))
        for col in range(1, 8):
            ws.cell(row=r, column=col).fill = VERT if col in (6, 7) else GRIS
        if n <= 3:
            ws.cell(row=r, column=1).fill = JAUNE
            ws.cell(row=r, column=1).font = Font(bold=True)
        ws.row_dimensions[r].height = 96
    mise_en_forme(ws, [4, 34, 46, 13, 52, 16, 26])

    # ---------- onglet 2 : les comptes ----------
    ws = wb.create_sheet("2. COMPTES A RELEVER")
    ws.append(["Prio", "Entite", "Ce qu'elle possede", "Pseudo suppose",
               "Chercher", "PSEUDO EXACT", "LISTE RELEVEE ?", "Pourquoi elle compte"])
    dv2 = DataValidation(type="list",
                         formula1='"oui,pas encore,aucun compte trouve"',
                         allow_blank=True)
    ws.add_data_validation(dv2)
    for prio, entite, possede, pseudo, pourquoi in COMPTES:
        ws.append([prio, entite, possede, pseudo, "ouvrir", "", "", pourquoi])
        r = ws.max_row
        c = ws.cell(row=r, column=5, value="ouvrir")
        c.hyperlink = "https://www.instagram.com/"
        c.font = LIEN
        dv2.add(ws.cell(row=r, column=7))
        for col in range(1, 9):
            ws.cell(row=r, column=col).fill = VERT if col in (6, 7) else GRIS
        if prio == 1:
            ws.cell(row=r, column=1).fill = ROUGE
            ws.cell(row=r, column=1).font = Font(bold=True)
        ws.row_dimensions[r].height = 76
    mise_en_forme(ws, [6, 20, 40, 22, 10, 24, 18, 54])

    # ---------- onglet 3 : les alias ----------
    ws = wb.create_sheet("3. ALIAS A CHERCHER")
    ws.append(["Site", "Ouvrir", "Lobby", "Ce qu'on y cherche",
               "NOMS TROUVES", "Ton commentaire"])
    for nom, url, lobby, quoi in ALIAS:
        ws.append([nom, "ouvrir", lobby, quoi, "", ""])
        r = ws.max_row
        c = ws.cell(row=r, column=2, value="ouvrir")
        c.hyperlink = url
        c.font = LIEN
        for col in range(1, 7):
            ws.cell(row=r, column=col).fill = VERT if col in (5, 6) else GRIS
        ws.row_dimensions[r].height = 72
    mise_en_forme(ws, [30, 10, 13, 54, 34, 30])

    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"{len(TACHES)} taches, {len(COMPTES)} comptes, {len(ALIAS)} sites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
