"""
Fabrique cartographie/A_FAIRE.xlsx — LE classeur de Vincent. Un seul.

POURQUOI UN SEUL

Le 28/08 Vincent a demande : « je ne comprends pas pourquoi tu as cree un
nouveau classeur. N'y a-t-il pas moyen de compiler les deux (avec
MES_TACHES) ? »

Il avait raison. Le projet avait produit `MES_TACHES.xlsx`, puis `A_FAIRE.xlsx`,
plus quatre classeurs de verification — et ses reponses etaient eparpillees
entre eux. Deux consequences reelles :

- **des questions qu'il m'avait posees sont restees sans reponse pendant deux
  jours**, parce que je lisais la colonne « statut » et pas la colonne
  « commentaire » du classeur precedent ;
- il ne savait plus lequel ouvrir.

Ce fichier est desormais **le seul point d'entree**. Les classeurs de
verification restent separes — ce sont des jeux de donnees a annoter, pas des
listes de taches — mais ils sont listes ici, avec leur avancement.

CE QU'IL CONTIENT

  1. **LIS-MOI** — ou en est le projet, en dix lignes.
  2. **A FAIRE** — les taches, triees par ce qu'elles debloquent. Colonnes
     vertes : ou tu en es, et ton commentaire.
  3. **CLASSEURS A JUGER** — les jeux a annoter, avec le nombre de lignes
     restantes.
  4. **DECISIONS** — ce que Claude ne peut pas trancher, avec sa recommandation.
  5. **DEJA FAIT** — l'archive, pour ne pas redemander.

CE QUI EST PRESERVE

Le generateur **relit les reponses precedentes** dans `A_FAIRE.xlsx` et
`MES_TACHES.xlsx` et les recopie. Regenerer ne perd rien. C'est la condition
pour qu'un seul fichier puisse remplacer les deux.

Usage :  python outils/generer_a_faire.py
"""

import sys
from datetime import date
from pathlib import Path

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

RACINE = Path(__file__).resolve().parent.parent
CARTO = RACINE / "cartographie"
CIBLE = CARTO / "A_FAIRE.xlsx"

ENTETE = PatternFill("solid", fgColor="434343")
ROUGE = PatternFill("solid", fgColor="F4CCCC")
JAUNE = PatternFill("solid", fgColor="FFF2CC")
VERT = PatternFill("solid", fgColor="D9EAD3")
GRIS = PatternFill("solid", fgColor="EFEFEF")

REPONSES_CONNUES = {
    "lobbies": ("fait", ""),
    # A_VERIFIER_4 contient 9 cas NEUFS : c'est _3 qui a ete juge.
    "verif": ("pas encore", "Tes 78 jugements du 27/08 portaient sur "
              "A_VERIFIER_3, deja integres. Ces 9-ci sont nouveaux."),
    # Tache RECURRENTE : le jeton expire en 1 a 2 heures.
    "meta_jeton": ("pas encore", "Le chemin est etabli : ajouter le use case "
                   "Marketing API a l'app fait apparaitre ads_read. C'est TOI "
                   "qui l'as trouve le 27/08. A refaire a chaque session Meta."),
    "marques": ("fait", "Comptes confirmes un par un. IMPORTANT : il n'existe "
                "ni compte Danone France, ni Lactalis, ni Bel francais. "
                "@lifeatdanone existe mais n'est peut-etre pas francais."),
    "vitrines_tt_yt": ("pas encore", "Tu veux que je t'envoie ca dans le CLI "
                       "aussi et tu ranges toi ? — OUI, en vrac, l'outil qui "
                       "lit les copier-coller existe."),
    "l214": ("en cours", "Je demanderai a la responsable de Paye Ton Influence "
             "si c'est une bonne idee d'abord. Appel prevu cette semaine."),
    "arpp": ("en cours", "Pas sur de l'aspect officiel, ca ressemble a un "
             "potentiel meta-lobby. Je demande l'avis a un collegue."),
    "onedrive": ("pas encore", ""),
    "twitch": ("", ""),
    "annonces": ("pas encore", ""),
    "laitflix": ("pas encore", "produits-laitiers.com/laitflix/divertissement "
                 "est une mine d'or. Je peux lister les creatures des series "
                 "si tu n'y arrives pas."),
}

DECISIONS_REPONDUES = {
    "regle": "Discutons-en",
    "depot": "Je n'en sais rien, discutons-en. Je ne sais pas si 40 Mo est "
             "beaucoup",
    "cnpo": "Je ne sais pas. Discutons-en",
    "methodo92": "Je ne sais pas ce que tu demandes ici",
    "publication": "On est a l'etape de creer une methode de scrapping robuste "
                   "et resiliente. Le but est de creer un dataset solide avec "
                   "nom des influenceurs, lobby/vitrine/marque qui remunere, "
                   "date de la collaboration, eventuellement le montant, la "
                   "forme (type et nombre de contenus), les plateformes. Une "
                   "fois ce dataset obtenu et une methode pour le mettre a "
                   "jour, on reflechira a la forme du site, a l'extension de "
                   "navigateur, au bouton de signalement, et a quoi faire de "
                   "ces donnees.",
}

STATUTS = ["pas encore", "en cours", "fait", "abandonne", "je ne sais pas"]

# (cle, priorite, tache, ou, duree, pourquoi)
# La cle sert a retrouver la reponse de Vincent d'une generation a l'autre.
TACHES = [
    ("lobbies", "1 — le plus utile",
     "Trancher CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx",
     "cartographie/CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx",
     "20 min pour les 60 premieres lignes",
     "218 noms tires des videos publiees par les lobbies EUX-MEMES. Deux "
     "questions, deux mesures independantes : (1) createur ou nom de serie ? "
     "cela mesure la voie « motif dans le titre », 176 noms dont on ignore ce "
     "qu'elle vaut. (2) quel TYPE de personne ? cela tranche la couverture du "
     "projet — nos deux methodes trouvent 36 et 42 createurs et n'ont qu'UN "
     "nom en commun."),

    ("annonces", "2 — le plus neuf",
     "Trancher CREATEURS_DANS_LES_ANNONCES.xlsx",
     "cartographie/CREATEURS_DANS_LES_ANNONCES.xlsx",
     "20 min pour les 80 premieres lignes",
     "617 createurs nommes dans des PUBLICITES PAYEES par la filiere, sorties "
     "de la Meta Ad Library le 27/08. C'est la preuve la plus forte du projet : "
     "l'annonceur a paye pour diffuser. Trois voies de detection a mesurer."),

    ("laitflix", "3",
     "Verifier les createurs nommes sur les sites des lobbies",
     "cartographie/CREATEURS_SUR_LES_SITES.xlsx",
     "20 min",
     "Quatre sources relevees le 28/08 : le catalogue LAIT'FLIX du CNIEL "
     "(107 videos, 12 series — la page que TU avais signalee), la-viande.fr "
     "pour INTERBEV (Cyril Lignac, Loic Ballet), et les publicites Facebook "
     "payees par le CIFOG et ANVOL. Neuf des douze series LAIT'FLIX sont "
     "ABSENTES de la chaine YouTube du CNIEL : moissonner la chaine officielle "
     "d'un lobby ne suffit pas. Liste issue d'une lecture automatique, a "
     "verifier."),

    ("meta_jeton", "4 — a refaire chaque fois",
     "Regenerer le jeton Meta",
     "developers.facebook.com/tools/explorer — app, User Token, ads_read, "
     "Generate. Coller dans SECRETS.txt",
     "5 min",
     "Le jeton expire en 1 a 2 heures. Sans lui, aucune moisson Instagram. "
     "Le chemin est maintenant connu et teste."),

    ("verif", "5",
     "Juger A_VERIFIER_4.xlsx",
     "cartographie/A_VERIFIER_4.xlsx",
     "5 min",
     "9 nouveaux candidats seulement — tes 78 jugements du 27/08 ont ete "
     "integres. Le jeu de reference atteint 382 videos jugees."),

    ("onedrive", "6 — quand rien ne tourne",
     "Sortir le projet de OneDrive et retirer le « & » du nom",
     "Couper-coller le dossier vers C:\\Users\\Vincent\\veille-filiere",
     "5 min",
     "Deux problemes d'un geste. OneDrive : un verrou de synchronisation a "
     "interrompu une moisson. Le « & » : cmd.exe le lit comme un separateur de "
     "commandes, il a fait echouer la tache planifiee au premier essai. "
     "APRES le deplacement il faut recreer la tache planifiee — dis-le moi, "
     "c'est une commande."),

    ("marques", "7",
     "Relever les abonnements des GRANDES MARQUES sur INSTAGRAM",
     "@nestleenfrance, @savencia_groupe, @herta_france, @legaulois_officiel, "
     "@charal_officiel, @fleurymichon — les pseudos que tu as deja confirmes",
     "30 min",
     "MESURE : cette semence produit 2,12 vraies pistes par chaine, contre "
     "0,16 pour la semence TikTok. Treize fois mieux. Envoie en vrac dans le "
     "CLI, je range — tu me l'avais propose et je n'avais pas repondu."),

    ("vitrines_tt_yt", "8",
     "Relever les abonnements des vitrines sur TIKTOK et YOUTUBE",
     "@lesproduitslaitiers, @la_viande_fr, @naturellementflexitariens, "
     "@volaillefrancaise, @lefoiegras — sur ces deux plateformes-la",
     "20 min",
     "Les abonnements different d'une plateforme a l'autre. Meme rendement "
     "attendu que la semence Instagram."),

    ("l214", "9 — en cours",
     "Demander a L214 et Foodwatch si le registre existe deja",
     "Un courriel — ou via la responsable de Paye Ton Influence",
     "10 min",
     "Si quelqu'un l'a deja construit, autant le savoir. Tu as un appel prevu "
     "avec Paye Ton Influence : la question peut passer par la."),

    ("arpp", "10 — en cours",
     "Demander a l'ARPP les donnees brutes de son Observatoire",
     "Un courriel",
     "10 min",
     "Source officielle sur les communications commerciales des influenceurs. "
     "Ta reserve est notee : l'ARPP est un organisme d'autoregulation de la "
     "publicite, pas un regulateur public. Un refus est documentable."),
]

DECISIONS = [
    ("regle", "Quelle regle de detection garder ?",
     "La regle B — un alias de la filiere ET du vocabulaire commercial dans la "
     "description.",
     "MESURE du 27/08 sur 240 candidats : B fait 85 % de precision et 90 % de "
     "rappel. C, D et F font 85 % aussi, avec un rappel EGAL ou PIRE, et leurs "
     "intervalles de confiance se recouvrent entierement. A performance egale, "
     "B est la seule sans liste ecrite a la main : elle ne peut pas se perimer "
     "quand un commanditaire nouveau arrive. La liste GENERIQUES disparaitrait "
     "au lieu d'etre corrigee. JOURNAL 61."),

    ("depot", "Faut-il continuer a versionner le fichier de reprise ?",
     "Le compresser plutot que choisir entre le garder et le perdre.",
     "Tu demandes si 40 Mo c'est beaucoup : non, pas en soi. Le probleme est "
     "que git garde une copie ENTIERE a chaque commit, et le fichier grossit. "
     "Compresse en .json.gz il ferait environ 4 Mo et resterait une sauvegarde "
     "de trois jours de quota d'API. Sans urgence."),

    ("cnpo", "Le CNPO (oeufs) est-il dans le perimetre ?",
     "A toi de trancher — le classeur et la conversation se contredisent.",
     "cartographie_filiere.xlsx marque le CNPO « HORS PERIMETRE », alors que tu "
     "avais confirme « Oeufs de France » le 25/08. Aucun CNPO n'est retenu en "
     "pratique, donc rien n'est casse. Mais METHODOLOGIE 1 exclut l'oeuf « pour "
     "l'instant » : c'est cette phrase-la qu'il faut confirmer ou lever."),

    ("methodo92", "METHODOLOGIE 9.2 prescrit une mesure impossible. La reecrire ?",
     "Oui — remplacer le tirage aleatoire par la capture-recapture.",
     "Ce que je demande, concretement : la section dit de tirer des createurs "
     "au hasard et de les annoter exhaustivement, pour savoir ce que le projet "
     "RATE. MESURE : il faudrait en annoter 739 A LA MAIN pour en obtenir dix "
     "qui portent une preuve, soit 28 % du registre. Ce n'est pas un manque de "
     "temps, c'est arithmetiquement impossible. La question est : "
     "m'autorises-tu a reecrire cette section pour y mettre la "
     "capture-recapture a la place ? JOURNAL 62."),

    ("twitch", "Faut-il couvrir Twitch ?",
     "Oui, mais en dernier — apres les classeurs a juger.",
     "MESURE du 29/08, qui tranche une question ouverte depuis le 24. On "
     "croyait Twitch couvert indirectement, parce que l'INAPORC ecrit sur son "
     "site que les best-of de ses lives migrent vers YouTube. Verification sur "
     "le catalogue COMPLET de Lebouseuh (1 773 videos) et 300 de Gastronogeek : "
     "ZERO mention d'INAPORC ou du Porc Francais. Les best-of n'y sont pas. "
     "Twitch est donc un angle mort reel. Ce que ca coute : l'API Twitch est "
     "gratuite et expose les CLIPS, qui sont permanents. Les VOD expirent en 14 "
     "a 60 jours — on verrait le present, jamais l'archive. Il faudrait creer "
     "un compte developpeur Twitch, comme pour Meta. JOURNAL 70."),

    ("publication", "Qui publie le registre, et sous quel nom ?",
     "Sans urgence — tu as deja repondu et j'ai note.",
     "Ta reponse du 27/08 : « On est a l'etape de creer une methode de "
     "scrapping robuste et resiliente. Le but est de creer un dataset solide "
     "[...] Une fois qu'on aura ce dataset, on reflechira a la forme du site. » "
     "C'est enregistre. La question ne se rouvre qu'au moment de publier."),
]


def reponses_precedentes():
    """Relit les reponses de Vincent, pour ne rien perdre en regenerant.

    Les colonnes sont reperees par leur EN-TETE, jamais par leur rang. Une
    premiere version prenait « tout ce qui suit les deux premieres cellules »,
    et recopiait donc mes propres colonnes — « Comment », « Ce que ca
    debloque » — a la place de ses reponses.
    """
    reponses = {}
    entetes_reponse = ("OU EN ES-TU", "TON COMMENTAIRE", "TA REPONSE",
                       "STATUT", "LISTE RELEVEE", "PSEUDO EXACT",
                       "NOMS TROUVES")
    for nom in ("A_FAIRE.xlsx", "MES_TACHES.xlsx"):
        f = CARTO / nom
        if not f.exists():
            continue
        try:
            wb = openpyxl.load_workbook(f, data_only=True)
        except Exception:
            continue
        for s in wb.sheetnames:
            ws = wb[s]
            # la ligne d'en-tete est la premiere qui porte une colonne connue
            entete, colonnes = None, {}
            for r in range(1, 40):
                for c in range(1, 20):
                    v = str(ws.cell(row=r, column=c).value or "").strip().upper()
                    if any(e in v for e in entetes_reponse):
                        entete = r
                        colonnes[c] = v
                if entete:
                    break
            if not entete:
                continue
            for r in range(entete + 1, ws.max_row + 1):
                libelle = ""
                for c in range(1, 6):
                    v = str(ws.cell(row=r, column=c).value or "").strip()
                    if len(v) > len(libelle) and c not in colonnes:
                        libelle = v
                if not libelle:
                    continue
                notes = []
                for c in colonnes:
                    v = str(ws.cell(row=r, column=c).value or "").strip()
                    if v:
                        notes.append(v)
                if notes:
                    reponses.setdefault(libelle.lower(), []).extend(notes)
        wb.close()
    return reponses


def retrouver(reponses, tache):
    """Retrouve statut et commentaire d'une tache, par correspondance de mots."""
    mots = {m for m in tache.lower().split() if len(m) > 4}
    meilleur, score = None, 0
    for libelle, notes in reponses.items():
        commun = len(mots & {m for m in libelle.split() if len(m) > 4})
        if commun > score:
            meilleur, score = notes, commun
    if score < 2:
        return "", ""
    statut = next((n for n in meilleur if n.lower() in
                   [s.lower() for s in STATUTS]), "")
    commentaire = " · ".join(n for n in meilleur
                             if n.lower() not in [s.lower() for s in STATUTS]
                             and len(n) > 20)[:600]
    return statut, commentaire


def lignes_restantes(nom, colonne_verdict="VERDICT"):
    """Combien de lignes restent a juger dans un classeur de verification.

    La colonne a remplir est reperee par son en-tete en MAJUSCULES : c'est la
    convention de tous les classeurs du projet. On compte une ligne des qu'une
    de ses cellules porte du texte, plutot que de dependre d'une colonne
    precise — les classeurs n'ont pas tous la meme structure.
    """
    f = CARTO / nom
    if not f.exists():
        return None, None
    try:
        wb = openpyxl.load_workbook(f, data_only=True)
    except Exception:
        return None, None

    # La premiere feuille n'est pas toujours celle des donnees : certains
    # classeurs ouvrent sur un mode d'emploi. On prend la premiere qui porte
    # une colonne a remplir.
    entete = col = None
    ws = None
    for nom_feuille in wb.sheetnames:
        if nom_feuille == "listes":
            continue
        candidate = wb[nom_feuille]
        for r in range(1, 60):
            for c in range(1, 20):
                v = str(candidate.cell(row=r, column=c).value or "").strip()
                if v.isupper() and len(v) > 8 and ("?" in v or "VERDICT" in v):
                    ws, entete, col = candidate, r, c
                    break
            if entete:
                break
        if entete:
            break
    if ws is None:
        wb.close()
        return None, None
    _inutilise = None
    total = faits = 0
    for r in range(entete + 1, ws.max_row + 1):
        # une ligne existe si l'une de ses trois premieres cellules est remplie
        if any(ws.cell(row=r, column=c).value for c in (1, 2, 3)):
            total += 1
            if ws.cell(row=r, column=col).value:
                faits += 1
    wb.close()
    return total, faits


def feuille(wb, titre, colonnes, lignes, couleur=None, validation=None):
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
            if couleur:
                f = couleur(i - 2, j)
                if f:
                    c.fill = f
        ws.row_dimensions[i].height = 84
    if validation:
        col, choix = validation
        lst = wb["listes"] if "listes" in wb.sheetnames else wb.create_sheet("listes")
        for i, v in enumerate(choix, 1):
            lst.cell(row=i, column=1, value=v)
        lst.sheet_state = "hidden"
        dv = DataValidation(type="list", allow_blank=True,
                            formula1=f"=listes!$A$1:$A${len(choix)}")
        ws.add_data_validation(dv)
        for i in range(2, len(lignes) + 2):
            dv.add(ws.cell(row=i, column=col))
    ws.freeze_panes = ws.cell(row=2, column=1)
    return ws


def main():
    reponses = reponses_precedentes()
    print(f"{len(reponses)} reponses precedentes relues", file=sys.stderr)

    wb = Workbook()
    wb.remove(wb.active)

    lignes_taches, faites = [], []
    for cle, prio, tache, ou, duree, pourquoi in TACHES:
        statut, commentaire = retrouver(reponses, tache)
        connu_s, connu_c = REPONSES_CONNUES.get(cle, ("", ""))
        statut = connu_s or statut
        commentaire = connu_c or commentaire
        ligne = [prio, tache, ou, duree, pourquoi, statut, commentaire]
        if statut.lower() in ("fait", "abandonne"):
            faites.append([tache, statut, commentaire])
        else:
            lignes_taches.append(ligne)

    def couleur_taches(i, j):
        if j != 1:
            return None
        return ROUGE if i < 3 else (JAUNE if i < 6 else GRIS)

    feuille(wb, "A FAIRE",
            [("Priorite", 20), ("Tache", 40), ("Ou", 34), ("Temps", 16),
             ("Pourquoi, et ce que ca debloque", 68), ("OU EN ES-TU ?", 16),
             ("Ton commentaire", 40)],
            lignes_taches, couleur_taches, validation=(6, STATUTS))

    # --- classeurs a juger ---
    classeurs = []
    for nom, quoi in [
            ("CREATEURS_NOMMES_PAR_LES_LOBBIES.xlsx",
             "Createurs nommes par les chaines des lobbies"),
            ("CREATEURS_DANS_LES_ANNONCES.xlsx",
             "Createurs nommes dans les publicites payees"),
            ("A_VERIFIER_4.xlsx", "Candidats issus de la moisson YouTube"),
            ("CREATEURS_SUR_LES_SITES.xlsx", "Createurs nommes sur les sites et dans les pubs des lobbies")]:
        total, faits = lignes_restantes(nom)
        if total is None:
            classeurs.append([nom, quoi, "pas encore genere", "", ""])
        else:
            classeurs.append([nom, quoi, f"{total} lignes",
                              f"{faits} jugees", f"{total - faits} restantes"])
    feuille(wb, "CLASSEURS A JUGER",
            [("Fichier", 46), ("Ce que c'est", 46), ("Taille", 18),
             ("Avancement", 16), ("Reste", 16)], classeurs)

    # --- decisions ---
    lignes_dec = []
    for cle, question, reco, fonde in DECISIONS:
        _s, commentaire = retrouver(reponses, question)
        lignes_dec.append([question, reco, fonde,
                           DECISIONS_REPONDUES.get(cle, commentaire)])
    feuille(wb, "DECISIONS",
            [("La question", 40), ("Ce que je recommande", 42),
             ("Sur quoi je me fonde", 76), ("TA REPONSE", 34)],
            lignes_dec, lambda i, j: VERT if j == 4 else None)

    if faites:
        feuille(wb, "DEJA FAIT",
                [("Tache", 46), ("Statut", 16), ("Ton commentaire", 76)], faites)

    # --- lis-moi, en premier ---
    ws = wb.create_sheet("LIS-MOI", 0)
    texte = [
        f"OU EN EST LE PROJET — {date.today().strftime('%d/%m/%Y')}",
        "",
        "CE FICHIER EST LE SEUL A OUVRIR.",
        "Il remplace MES_TACHES.xlsx, conserve seulement comme archive. Tes "
        "reponses precedentes y ont ete recopiees.",
        "",
        "QUATRE ONGLETS",
        "",
        "  A FAIRE            ce qui t'attend, trie par ce que ca debloque",
        "  CLASSEURS A JUGER  les jeux a annoter, avec ce qu'il reste",
        "  DECISIONS          ce que je ne peux pas trancher a ta place",
        "  DEJA FAIT          l'archive, pour ne pas te redemander",
        "",
        "SI TU N'AS QUE VINGT MINUTES",
        "",
        "Onglet CLASSEURS A JUGER, premiere ligne. Chaque jugement que tu "
        "donnes mesure une methode qu'on ne peut pas mesurer sans toi.",
        "",
        "CE QUI A CHANGE DEPUIS HIER",
        "",
        "Instagram est debloque. 7 148 publicites de la filiere moissonnees, "
        "617 createurs nommes dedans. C'est la preuve la plus forte du projet : "
        "l'annonceur a paye pour diffuser.",
        "",
        "Tes notes sur LAIT'FLIX ont rapporte 149 videos CNIEL de plus. Neuf "
        "des douze series n'etaient sur AUCUNE chaine YouTube de lobby : "
        "moissonner la chaine officielle ne suffit pas.",
        "",
        "La tache planifiee a tourne cette nuit, neuf etapes, sans "
        "intervention. Deux mois de TikTok de plus.",
    ]
    for i, l in enumerate(texte, 1):
        c = ws.cell(row=i, column=1, value=l)
        c.font = Font(bold=bool(l) and l.isupper(), size=11)
    ws.column_dimensions["A"].width = 104

    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(CIBLE)
    print(f"Ecrit : {CIBLE}")
    print(f"{len(lignes_taches)} taches actives, {len(faites)} archivees, "
          f"{len(DECISIONS)} decisions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
