#!/usr/bin/env python3
"""
Genere cartographie/cartographie_filiere.xlsx a partir des donnees ci-dessous.

Pourquoi un script plutot qu'un fichier Excel ecrit a la main :
tout le contenu du classeur est lisible ici, en texte, versionnable dans git.
Si tu modifies le .xlsx a la main, tes modifications seront ECRASEES au
prochain lancement du script. Voir LISEZ-MOI.md, section "Qui edite quoi".

Lancer :  python outils/generer_cartographie.py
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "cartographie" / "cartographie_filiere.xlsx"

# --------------------------------------------------------------------------
# Conventions de remplissage
#
# statut      : CONFIRME  = verifie sur une source primaire citee
#               A VERIFIER = repris d'une source secondaire ou de memoire
#               HYPOTHESE  = suppose, pas encore cherche
# source      : d'ou vient l'information. Jamais vide pour un statut CONFIRME.
# --------------------------------------------------------------------------

FEUILLES = {}

# ---------------------------------------------------------------- LISEZ-MOI
FEUILLES["LISEZ-MOI"] = {
    "largeurs": [26, 90],
    "entetes": ["Feuille", "A quoi elle sert"],
    "lignes": [
        ["Interprofessions",
         "Les organismes de filiere finances par cotisation obligatoire. Ce sont les principaux "
         "donneurs d'ordre des campagnes d'influence. Cible prioritaire du projet."],
        ["Industriels",
         "Les groupes prives et cooperatifs. Second cercle de donneurs d'ordre. Ils communiquent "
         "sous leurs marques, pas sous leur raison sociale."],
        ["Marques",
         "Table de correspondance marque -> groupe. Indispensable : une collaboration mentionne "
         "'President', jamais 'Lactalis'."],
        ["Alias",
         "LE COEUR DE L'OUTIL. Toute chaine de caracteres qui peut apparaitre dans un post "
         "(pseudo, hashtag, nom de campagne, faux collectif) et l'entite reelle derriere. "
         "C'est ce que ni Paye Ton Influence ni l'Observatoire Citoyen ne font."],
        ["Agences",
         "Les intermediaires. Elles publient leurs case studies avec la liste des createurs : "
         "meilleur rapport temps investi / entrees obtenues."],
        ["Influenceurs",
         "Collaborations deja documentees par des sources publiees. Sert de jeu de test : si notre "
         "methode ne les retrouve pas, elle ne marche pas."],
        ["Sources_de_donnees",
         "Toutes les sources exploitables, leur cout, leur statut de test et ce qu'elles donnent "
         "reellement. A tenir a jour au fur et a mesure des tests."],
        ["Journal",
         "Qui a change quoi, quand. A remplir a la main."],
        ["", ""],
        ["CONVENTIONS", ""],
        ["Colonne statut",
         "CONFIRME = verifie sur source primaire citee. A VERIFIER = source secondaire ou de "
         "memoire. HYPOTHESE = suppose, pas encore cherche. Rien de statut 'A VERIFIER' ne doit "
         "etre publie."],
        ["Colonne source",
         "Ne doit jamais etre vide quand le statut est CONFIRME."],
        ["Regeneration",
         "Ce fichier est produit par outils/generer_cartographie.py. Une modification faite "
         "directement dans Excel sera ecrasee au prochain lancement du script. Voir LISEZ-MOI.md."],
    ],
}

# ---------------------------------------------------------- Interprofessions
FEUILLES["Interprofessions"] = {
    "largeurs": [14, 40, 26, 30, 20, 46, 14, 34],
    "entetes": ["sigle", "nom_complet", "filiere", "vitrine_grand_public",
                "budget_connu", "notes", "statut", "source"],
    "lignes": [
        ["INTERBEV", "Association Nationale Interprofessionnelle du Betail et des Viandes",
         "Bovins, veaux, ovins, equins, caprins", "@la_viande_fr",
         "~30 M EUR communication",
         "20 organisations membres. Campagnes : Aimez la viande mangez-en mieux ; "
         "Naturellement Flexitariens (2019) ; Celles et ceux qui font la viande (2025).",
         "A VERIFIER", "Chiffre issu d'une critique Confederation paysanne"],
        ["INTERBEV", "", "", "", "75-100 k EUR lobbying declare (2024, 2025)",
         "1 salarie ETP declare. President Jean-Francois Guihard, DG Marc Pages, "
         "affaires publiques Louison Camus. Inscrit le 03/04/2018.",
         "CONFIRME", "HATVP, fiche organisation 378355929"],
        ["CNIEL", "Centre National Interprofessionnel de l'Economie Laitiere", "Lait de vache",
         "@lesproduitslaitiers", "44,4 M EUR ressources totales (2024)",
         "~90 salaries. 4 departements dont communication et affaires publiques. "
         "Slogans : Nos amis pour la vie ; Des sensations pures.",
         "CONFIRME", "Rapport d'activite CNIEL 2024"],
        ["CNIEL", "", "", "", "6,2 M EUR de subventions UE fléchees communication (2024)",
         "Argent public europeen finançant la promotion laitiere.",
         "CONFIRME", "Rapport d'activite CNIEL 2024"],
        ["CNIEL", "", "", "", "1,5 M EUR campagnes d'influence reseaux sociaux (2023)",
         "Cible declaree : 15-35 ans.",
         "CONFIRME", "France Culture, Un monde connecte"],
        ["CNIEL", "", "", "", "CVO 1,22 EUR/1000 L producteur ; 0,442 EUR/1000 L transformateur",
         "Taux etendus par arrete, donc publies au Journal officiel.",
         "CONFIRME", "Sources publiques filiere"],
        ["INAPORC", "Interprofession Nationale Porcine", "Porc", "Le Porc Francais", "",
         "Une des cinq interprofessions viandes blanches.", "A VERIFIER",
         "Vitrine a confirmer compte par compte"],
        ["ANVOL", "Interprofession de la Volaille de chair", "Volaille de chair",
         "Volaille Francaise", "", "Issue de la fusion des anciennes interprofessions volaille.",
         "A VERIFIER", "Vitrine a confirmer"],
        ["CNPO", "Comite National pour la Promotion de l'Oeuf", "Oeufs", "Oeufs de France", "",
         "Hors perimetre strict viande/lait : inclusion a trancher.", "A VERIFIER",
         "Vitrine a confirmer"],
        ["CIFOG", "Comite Interprofessionnel des palmipedes a Foie Gras",
         "Palmipedes a foie gras", "Le Foie Gras", "",
         "Forte activite d'influence saisonniere en decembre. Cible historique des campagnes "
         "animalistes.", "A VERIFIER", "Vitrine a confirmer"],
        ["CLIPP", "Comite Lapin Interprofessionnel pour la Promotion des Produits", "Lapin", "",
         "", "Petite structure, activite d'influence probablement marginale.", "HYPOTHESE", ""],
        ["Intercereales", "Intercereales", "Cereales", "@lescereales", "",
         "HORS PERIMETRE. Meme dispositif de vitrine : sert de groupe temoin pour tester la "
         "methode de detection sans toucher a notre sujet.", "CONFIRME",
         "Paye Ton Influence, LinkedIn"],
        ["FNPSMS", "Fed. Nat. de la Production de Semences de Mais et de Sorgho", "Mais",
         "@cetepimepate", "", "HORS PERIMETRE. Groupe temoin.", "CONFIRME",
         "Paye Ton Influence, LinkedIn"],
    ],
}

# --------------------------------------------------------------- Industriels
FEUILLES["Industriels"] = {
    "largeurs": [26, 12, 16, 22, 52, 14, 30],
    "entetes": ["groupe", "secteur", "type", "taille", "notes", "statut", "source"],
    "lignes": [
        ["Lactalis", "Lait", "Prive", "30,3 Md EUR CA laitier 2024",
         "Premier groupe laitier mondial.", "CONFIRME", "Reussir, classement mondial"],
        ["Danone", "Lait", "Cote", "13,5 Md EUR CA laitier 2024", "", "CONFIRME", "Reussir"],
        ["Savencia", "Lait", "Cote", "7,1 Md EUR CA laitier 2024", "Ex-Bongrain.", "CONFIRME",
         "Reussir"],
        ["Sodiaal", "Lait", "Cooperative", "5,8 Md EUR CA laitier 2024", "", "CONFIRME",
         "Reussir"],
        ["Groupe Bel", "Lait", "Prive", "", "", "A VERIFIER", ""],
        ["Eurial / Agrial", "Lait", "Cooperative", "", "", "A VERIFIER", ""],
        ["Laita", "Lait", "Cooperative", "", "Groupe Even.", "A VERIFIER", ""],
        ["Bigard", "Viande", "Prive", "23 % de part de marche (2023)",
         "Premier groupe francais de viande bovine.", "CONFIRME", "Etudes secteur viande bovine"],
        ["Van Drie", "Viande", "Prive", "15 % de part de marche", "Groupe neerlandais.",
         "A VERIFIER", ""],
        ["T'Rhea", "Viande", "Prive", "12 % de part de marche", "", "A VERIFIER", ""],
        ["LDC", "Viande", "Cote", "Top 3 agroalimentaire francais", "Volaille.", "CONFIRME",
         "Classement LSA"],
        ["Cooperl", "Viande", "Cooperative", "", "Porc.", "A VERIFIER", ""],
        ["Terrena", "Viande", "Cooperative", "", "Bovin et volaille via Elivia et Gastronome.",
         "A VERIFIER", ""],
        ["Fleury Michon", "Viande", "Cote", "", "Charcuterie.", "A VERIFIER", ""],
        ["Groupe Aoste", "Viande", "Prive", "", "Charcuterie.", "A VERIFIER", ""],
        ["SVA Jean Roze", "Viande", "Distributeur", "", "Abattage integre Intermarche.",
         "A VERIFIER", ""],
        ["Kermene", "Viande", "Distributeur", "", "Abattage integre E. Leclerc.", "A VERIFIER",
         ""],
        ["Sicarev", "Viande", "Cooperative", "", "Marque Tradival.", "A VERIFIER", ""],
        ["Pilgrim's", "Viande", "Prive", "", "Moy Park Beef Orleans.", "A VERIFIER", ""],
    ],
}

# ------------------------------------------------------------------ Marques
FEUILLES["Marques"] = {
    "largeurs": [24, 22, 12, 14, 30],
    "entetes": ["marque", "groupe_parent", "secteur", "statut", "source"],
    "lignes": [
        [m, g, s, "A VERIFIER", "Liste etablie de memoire, a confirmer marque par marque"]
        for m, g, s in [
            ("President", "Lactalis", "Lait"),
            ("Lactel", "Lactalis", "Lait"),
            ("Bridel", "Lactalis", "Lait"),
            ("Galbani", "Lactalis", "Lait"),
            ("Societe", "Lactalis", "Lait"),
            ("Salakis", "Lactalis", "Lait"),
            ("La Laitiere", "Lactalis (licence Nestle)", "Lait"),
            ("Activia", "Danone", "Lait"),
            ("Actimel", "Danone", "Lait"),
            ("Danette", "Danone", "Lait"),
            ("Danonino", "Danone", "Lait"),
            ("Veloute", "Danone", "Lait"),
            ("Taillefine", "Danone", "Lait"),
            ("Gervais", "Danone", "Lait"),
            ("Elle & Vire", "Savencia", "Lait"),
            ("Caprice des Dieux", "Savencia", "Lait"),
            ("Saint Moret", "Savencia", "Lait"),
            ("Coeur de Lion", "Savencia", "Lait"),
            ("Tartare", "Savencia", "Lait"),
            ("Saint Agur", "Savencia", "Lait"),
            ("Chaumes", "Savencia", "Lait"),
            ("Candia", "Sodiaal", "Lait"),
            ("Yoplait", "Sodiaal", "Lait"),
            ("Entremont", "Sodiaal", "Lait"),
            ("Regilait", "Sodiaal", "Lait"),
            ("Babybel", "Groupe Bel", "Lait"),
            ("Kiri", "Groupe Bel", "Lait"),
            ("La Vache qui rit", "Groupe Bel", "Lait"),
            ("Boursin", "Groupe Bel", "Lait"),
            ("Leerdammer", "Groupe Bel", "Lait"),
            ("Soignon", "Eurial / Agrial", "Lait"),
            ("Grand Fermage", "Eurial / Agrial", "Lait"),
            ("Paysan Breton", "Laita", "Lait"),
            ("Mamie Nova", "Laita", "Lait"),
            ("Charal", "Bigard", "Viande"),
            ("Socopa", "Bigard", "Viande"),
            ("Tendriade", "Bigard / Van Drie", "Viande"),
            ("Le Gaulois", "LDC", "Viande"),
            ("Loue", "LDC", "Viande"),
            ("Maitre Coq", "LDC", "Viande"),
            ("Marie", "LDC", "Viande"),
            ("Broceliande", "Cooperl", "Viande"),
            ("Elivia", "Terrena", "Viande"),
            ("Pere Dodu", "Terrena", "Viande"),
            ("Gastronome", "Terrena", "Viande"),
            ("Aoste", "Groupe Aoste", "Viande"),
            ("Cochonou", "Groupe Aoste", "Viande"),
            ("Justin Bridou", "Groupe Aoste", "Viande"),
            ("Tradival", "Sicarev", "Viande"),
            ("Sabeval", "Van Drie", "Viande"),
            ("Herta", "Nestle / Casa Tarradellas", "Viande"),
            ("Fleury Michon", "Fleury Michon", "Viande"),
        ]
    ],
}

# -------------------------------------------------------------------- Alias
FEUILLES["Alias"] = {
    "largeurs": [34, 18, 24, 12, 56],
    "entetes": ["alias_observe", "type_alias", "entite_reelle", "statut", "pourquoi_ca_compte"],
    "lignes": [
        ["@la_viande_fr", "compte vitrine", "INTERBEV", "CONFIRME",
         "Seul tag de partenaire commercial apparu sur la campagne 2025, et seulement sur 1 "
         "publication sur 3."],
        ["Celles et ceux qui font la viande", "nom de campagne", "INTERBEV", "CONFIRME",
         "Presente dans une video comme un 'collectif' d'eleveurs independant. C'est le nom de "
         "la campagne Interbev, pas un collectif."],
        ["Naturellement Flexitariens", "nom de campagne", "INTERBEV", "CONFIRME",
         "Recuperation du mot flexitarien en 2019, vide de son sens de reduction."],
        ["Aimez la viande, mangez-en mieux", "slogan", "INTERBEV", "CONFIRME", ""],
        ["@lesproduitslaitiers", "compte vitrine", "CNIEL", "CONFIRME",
         "Le sigle CNIEL n'apparait jamais dans les contenus."],
        ["Les produits laitiers, nos amis pour la vie", "slogan", "CNIEL", "CONFIRME", ""],
        ["Des sensations pures", "slogan", "CNIEL", "CONFIRME", ""],
        ["En Mode Actif", "nom de campagne", "CNIEL", "CONFIRME",
         "Campagne COFINANCEE PAR L'UNION EUROPEENNE, contre la sedentarite. "
         "Nommee par Studio Danielle (1,74 M d'abonnes) dans deux descriptions : "
         "« en partenariat avec Les Produits Laitiers et leur campagne En Mode "
         "Actif cofinancee par l'UE ». Decouverte le 26/08/2026, absente de la "
         "table jusque-la. Le cofinancement europeen relie au dossier AGRIP."],
        ["Le Porc Francais", "marque filiere", "INAPORC", "A VERIFIER", ""],
        ["Volaille Francaise", "marque filiere", "ANVOL", "A VERIFIER", ""],
        ["Oeufs de France", "marque filiere", "CNPO", "A VERIFIER", ""],
        ["@lescereales", "compte vitrine", "Intercereales", "CONFIRME",
         "HORS PERIMETRE. Groupe temoin pour tester la detection."],
        ["@cetepimepate", "compte vitrine", "FNPSMS", "CONFIRME", "HORS PERIMETRE. Groupe temoin."],
    ],
}

# ------------------------------------------------------------------ Agences
FEUILLES["Agences"] = {
    "largeurs": [18, 20, 34, 46, 14, 26],
    "entetes": ["agence", "client", "campagne", "createurs_identifies", "statut", "source"],
    "lignes": [
        ["Ogilvy Paris", "INTERBEV", "Naturellement Flexitariens",
         "Valouzz (1,7 M Instagram, 3,2 M YouTube). Valorisation media annoncee 3,6 M EUR - "
         "ATTENTION : chiffre de communication, PAS un montant verse au createur.",
         "CONFIRME", "L'ADN"],
        ["Herezie", "INTERBEV", "Celles et ceux qui font la viande (2025)",
         "Volet influence important, createurs a identifier. 12 photographies d'Aurelien "
         "Chauvaud, production Henry.",
         "CONFIRME", "CB News, Adforum, Paye Ton Influence"],
        ["Shokola", "CNIEL", "Campagne digitale globale", "A identifier.", "CONFIRME",
         "Site Shokola, page realisations"],
        ["", "CNIEL", "Partenariat application YouMiam",
         "Pool de 10 influenceurs mobilises. Noms a identifier.", "A VERIFIER", "Presse filiere"],
        ["Webedia", "INAPORC", "Lives Twitch sur le metier d'eleveur de porcs",
         "Gastronogeek (live cuisine, best-of sur sa chaine YouTube) et LeBouseuh "
         "(defi Minecraft sur l'elevage porcin, best-of egalement). Cible declaree : "
         "18-30 ans. Deux createurs generalistes.",
         "CONFIRME",
         "leporc.com/le-porc-en-france/le-metier-d-eleveur-de-porcs-mis-en-lumiere-sur-twitch"],
        ["iProspect Conseil France", "INTERBEV", "Publicite TikTok (26 annonces)",
         "Agence declaree par TikTok comme payeur des annonces INTERBEV. "
         "Aucun createur associe : l'API ne relie pas annonceur et createur.",
         "CONFIRME", "API TikTok ad/query, champ advertiser.paid_for_by, 25/08/2026"],
        ["Publicis Media - Starcom", "Groupe Bel", "Publicite TikTok (56 annonces)",
         "Babybel, Kiri, La Vache qui rit. Agence declaree payeur.",
         "CONFIRME", "API TikTok ad/query, 25/08/2026"],
        ["WPP MEDIA FRANCE", "Danone / Yoplait / Nestle", "Publicite TikTok",
         "Meme agence declaree pour Danone Produits Frais (17), Yoplait (60) "
         "et Nestle France. Actimel, Activia.",
         "CONFIRME", "API TikTok ad/query, 25/08/2026"],
        ["VMLY&R France", "Nestle France", "Publicite TikTok (38 annonces)",
         "Sort sur les termes « lait », « viande » et « Charal ».",
         "CONFIRME", "API TikTok ad/query, 25/08/2026"],
        ["Havas Media France", "Lactalis", "Publicite TikTok",
         "Marque Lactel.", "CONFIRME", "API TikTok ad/query, 25/08/2026"],
        ["Publicis Media - Blue449", "Savencia", "Publicite TikTok",
         "Caprice des Dieux.", "CONFIRME", "API TikTok ad/query, 25/08/2026"],
        ["Vanksen", "Candia (Sodiaal)", "Publicite TikTok (8 annonces)",
         "", "CONFIRME", "API TikTok ad/query, 25/08/2026"],
        ["", "INAPORC", "Les recettes des influenceurs (programme suivi)",
         "Au moins 92 recettes creditees a des createurs nommes, avec notice "
         "biographique publiee par INAPORC : Mercotte, pepites2noisette (32 recettes), "
         "olivier.moulin (19), juliamaufay (13), mummyfast (12), menthe_banane, "
         "sophiecuisine, julienduboue, woodmoodfood, florianonair, chateau.leg0, "
         "agatheduchesne_, Dorian, Audrey.",
         "CONFIRME", "leporc.com/recettes/la-cuisine-des-influenceurs"],
    ],
}

# -------------------------------------------------------------- Influenceurs
FEUILLES["Influenceurs"] = {
    "largeurs": [24, 16, 18, 46, 12, 22],
    "entetes": ["createur", "commanditaire", "annee", "nature_de_la_collaboration",
                "statut", "source"],
    "lignes": [
        ["Squeezie", "CNIEL", "", "Video avec McFly & Carlito, plus de 22 M de vues. A "
         "publiquement declare regretter : 'j'ai vante un lobby'.", "CONFIRME",
         "StreetPress ; Society"],
        ["Inoxtag", "CNIEL", "2024", "Creation d'une Tomme de Savoie avec un MOF, Salon de "
         "l'Agriculture.", "CONFIRME", "France Culture"],
        ["Mister V", "CNIEL", "", "Placement / video.", "CONFIRME", "StreetPress"],
        ["McFly & Carlito", "CNIEL", "", "Video.", "CONFIRME", "StreetPress"],
        ["Valouzz", "INTERBEV", "", "Serie cuisine / gaming, via Ogilvy.", "CONFIRME", "L'ADN"],
        ["Kameto", "CNIEL", "", "Emission Radio Sexe, voyage sponsorise.", "CONFIRME",
         "StreetPress"],
        ["Zack Nani", "CNIEL", "", "Emission Radio Sexe, voyage sponsorise.", "CONFIRME",
         "StreetPress"],
        ["Morgan VS", "CNIEL", "", "Serie recettes.", "CONFIRME", "StreetPress"],
        ["Myriam Manhattan", "CNIEL", "", "Serie 'Myriam met du beurre dans tes epinards'.",
         "CONFIRME", "StreetPress"],
        ["Manais World", "CNIEL", "", "", "CONFIRME", "StreetPress"],
        ["Alkpote", "CNIEL", "", "Placement musical.", "CONFIRME", "StreetPress"],
        ["Jok'Air", "CNIEL", "", "Placement musical.", "CONFIRME", "StreetPress"],
        ["Loris Giuliano", "CNIEL", "", "Nature a qualifier.", "A VERIFIER",
         "Observation directe Vincent"],
        ["Ragnar le Breton", "CNIEL", "", "Nature a qualifier.", "A VERIFIER",
         "Observation directe Vincent"],
    ],
}

# -------------------------------------------------------- Sources de donnees
FEUILLES["Sources_de_donnees"] = {
    "largeurs": [30, 44, 14, 16, 44, 46],
    "entetes": ["source", "ce_qu_elle_donne", "cout", "statut_test", "limite_connue", "acces"],
    "lignes": [
        ["SponsorBlock",
         "Segments sponsorises horodates dans les videos YouTube. Base complete telechargeable.",
         "Gratuit", "A TESTER",
         "Ne donne PAS la marque, seulement l'emplacement du segment. Couverture orientee tech "
         "et gaming, et anglophone : a mesurer sur le contenu francais.",
         "https://sponsor.ajay.app/database"],
        ["HATVP open data",
         "Registre des representants d'interets : organisations, budgets declares, actions.",
         "Gratuit", "A TESTER",
         "Ne capte quasiment rien du marketing d'influence : Interbev y declare 75-100 k EUR "
         "contre ~30 M EUR de communication. Utile pour le recit, pas pour la detection.",
         "https://www.hatvp.fr/open-data-repertoire/"],
        ["Meta Ad Library",
         "Contenus de marque etiquetes partenariat remunere sur Facebook et Instagram.",
         "Gratuit", "A TESTER",
         "API soumise a validation. Ne couvre pas les collaborations non etiquetees.",
         "https://www.facebook.com/ads/library/"],
        ["TikTok Commercial Content Library",
         "Publications organiques etiquetees partenariat, perimetre EEE.",
         "Gratuit", "A TESTER",
         "API reservee aux chercheurs valides, 1000 requetes/jour. Interface web publique.",
         "https://library.tiktok.com/"],
        ["DGCCRF - injonctions et sanctions",
         "Decisions publiees contre des professionnels, dont mesures de publicite nominatives.",
         "Gratuit", "A EXPLORER",
         "Non structure, pagine. Plus de 300 influenceurs controles en 2022-2023, 280 en 2025 "
         "dont 46 % avec mesure.",
         "https://www.economie.gouv.fr/dgccrf/laction-de-la-dgccrf/injonctions-et-sanctions"],
        ["Legifrance / Journal officiel",
         "Arretes d'extension des cotisations interprofessionnelles : taux, assiette, duree.",
         "Gratuit", "A EXPLORER", "Preuve du financement, pas des collaborations.",
         "https://www.legifrance.gouv.fr/"],
        ["Portail UE Funding & Tenders",
         "Beneficiaires et montants des programmes de promotion agricole AGRIP.",
         "Gratuit", "A EXPLORER",
         "Le CNIEL a recu 6,2 M EUR de subventions UE communication en 2024.",
         "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/programmes/agrip2027"],
        ["Rapports annuels des interprofessions",
         "Budgets reels, postes de depense, campagnes de l'annee.",
         "Gratuit", "A EXPLORER",
         "PDF, non structures. Indispensable pour remplacer le chiffre de 30 M EUR d'Interbev "
         "par une source primaire.",
         "https://www.interbev.fr/interbev/linterprofession/bilans-annuels/"],
        ["Comptes suivis par les vitrines",
         "Liste des comptes suivis par @lesproduitslaitiers, @la_viande_fr, etc.",
         "Gratuit", "A FAIRE - VINCENT",
         "Recuperation manuelle. Chargement paresseux sur Instagram : derouler jusqu'en bas.",
         "Manuel, dans le navigateur"],
        ["ARPP Observatoire de l'Influence Responsable",
         "13 356 contenus analyses au S1 2024, taux de conformite par taille de createur.",
         "Gratuit", "FIABILITE LIMITEE",
         "L'ARPP est l'organe d'autoregulation DES ANNONCEURS. Juge et partie. Ne publie que des "
         "agregats, jamais les donnees sous-jacentes. A citer comme position d'acteur, pas comme "
         "mesure independante.",
         "https://www.arpp.org/"],
        ["Observatoire Paye Ton Influence",
         "1 147 comptes, 185 425 posts, 7 518 collaborations, 1 308 marques.",
         "Gratuit", "TESTE - EXPORT INSUFFISANT",
         "Le bouton d'export des tuiles ne renvoie que la valeur agregee, pas la table. "
         "Il faut demander l'export du tableau lui-meme, ou contacter l'association.",
         "https://observatoire.payetoninfluence.org/"],
        ["Observatoire Citoyen de la Publicite (code)",
         "Code source Rails. Modele de donnees signalement -> cas publie avec workflow.",
         "Gratuit", "LU",
         "Pas de jeu de donnees exportable. Le champ marque est une chaine libre, sans table "
         "d'entites : meme angle mort que Paye Ton Influence.",
         "https://github.com/communication-democratie/observatoire"],
        ["Google Ads Transparency Center",
         "Publicites payantes diffusees sur YouTube et le reseau Google.",
         "Gratuit", "A EXPLORER",
         "Couvre l'achat d'espace, pas les integrations sponsorisees dans les videos.",
         "https://adstransparency.google.com/"],
        ["Registres publicitaires DSA (X, LinkedIn, Snapchat)",
         "Depots publicitaires imposes aux tres grandes plateformes.",
         "Gratuit", "A EXPLORER",
         "Peu utile ici : couvre l'achat d'espace, pas les collaborations organiques.",
         "Portails respectifs des plateformes"],
    ],
}

# ------------------------------------------------------------------ Journal
FEUILLES["Journal"] = {
    "largeurs": [14, 16, 70],
    "entetes": ["date", "qui", "ce_qui_a_change"],
    "lignes": [
        ["2026-08-22", "Claude", "Creation du classeur. Contenu issu de la recherche de "
         "faisabilite du 22 aout 2026."],
    ],
}


# --------------------------------------------------------------------------
# Mise en forme
# --------------------------------------------------------------------------

ENCRE = "1F2733"
FOND_ENTETE = "E8EBF1"
FOND_ALERTE = "FBEFD6"

BORDURE = Border(bottom=Side(style="thin", color="D5DAE3"))


def charger_extraits_hatvp():
    """Ajoute les feuilles issues de outils/extraire_hatvp.py si elles existent.

    Ces feuilles sont ENTIEREMENT derivees de l'open data HATVP : elles n'ont
    pas de colonne statut, puisque leur source est primaire par construction.
    """
    import csv

    dossier = RACINE / "donnees" / "sources" / "hatvp" / "extraits"
    fichiers = [
        ("HATVP_organisations", "organisations_filiere.csv",
         [10, 46, 12, 30, 14, 16, 30, 26, 26, 12, 14, 14, 10, 8, 8]),
        ("HATVP_mandats", "mandats.csv", [42, 30, 42, 14, 10, 14, 14]),
        ("HATVP_affiliations", "affiliations.csv", [46, 30, 46, 14, 14]),
    ]
    autres = [
        ("Meta_annonceurs", RACINE / "donnees" / "sources" / "meta"
         / "annonceurs_filiere.csv", [40, 34, 14, 12, 22, 20]),
    ]
    for nom, fichier, largeurs in fichiers:
        chemin = dossier / fichier
        if not chemin.exists():
            continue
        with open(chemin, encoding="utf-8", newline="") as f:
            lignes = list(csv.reader(f, delimiter=";"))
        if not lignes:
            continue
        FEUILLES[nom] = {
            "largeurs": largeurs,
            "entetes": lignes[0],
            "lignes": lignes[1:],
        }

    for nom, chemin, largeurs in autres:
        if not chemin.exists():
            continue
        with open(chemin, encoding="utf-8", newline="") as f:
            lignes = list(csv.reader(f, delimiter=";"))
        if lignes:
            FEUILLES[nom] = {
                "largeurs": largeurs,
                "entetes": lignes[0],
                "lignes": lignes[1:],
            }


def construire():
    charger_extraits_hatvp()

    wb = Workbook()
    wb.remove(wb.active)

    for nom, spec in FEUILLES.items():
        ws = wb.create_sheet(nom)
        ws.append(spec["entetes"])

        for cellule in ws[1]:
            cellule.font = Font(bold=True, size=10, color=ENCRE)
            cellule.fill = PatternFill("solid", fgColor=FOND_ENTETE)
            cellule.alignment = Alignment(vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 26

        for ligne in spec["lignes"]:
            ws.append(ligne)

        for i, largeur in enumerate(spec["largeurs"], start=1):
            ws.column_dimensions[get_column_letter(i)].width = largeur

        # Surligne les lignes non confirmees pour qu'elles sautent aux yeux.
        try:
            col_statut = spec["entetes"].index("statut") + 1
        except ValueError:
            col_statut = None

        for ligne in ws.iter_rows(min_row=2):
            for cellule in ligne:
                cellule.alignment = Alignment(vertical="top", wrap_text=True)
                cellule.border = BORDURE
                cellule.font = Font(size=10)
            if col_statut and ws.cell(row=ligne[0].row, column=col_statut).value in (
                "A VERIFIER", "HYPOTHESE"
            ):
                for cellule in ligne:
                    cellule.fill = PatternFill("solid", fgColor=FOND_ALERTE)

        ws.freeze_panes = "A2"
        if len(spec["lignes"]) > 1:
            ws.auto_filter.ref = ws.dimensions

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    wb.save(SORTIE)
    return SORTIE


if __name__ == "__main__":
    chemin = construire()
    total = sum(len(s["lignes"]) for s in FEUILLES.values())
    print(f"Ecrit : {chemin}")
    print(f"{len(FEUILLES)} feuilles, {total} lignes.")
