#!/usr/bin/env python3
"""
Extrait le sous-graphe viande/lait du repertoire HATVP des representants
d'interets, et ecrit trois CSV dans donnees/sources/hatvp/extraits/.

Source : archive "Vues separees CSV" telechargee sur
https://www.hatvp.fr/le-repertoire/#open-data-repertoire
Licence Etalab. Mise a jour quotidienne cote HATVP.

CE QUE CETTE SOURCE DONNE : le graphe du LOBBYING INSTITUTIONNEL.
Qui defend les interets de qui aupres des pouvoirs publics, depuis quand,
pour quel budget declare, sur quels sujets.

CE QU'ELLE NE DONNE PAS : les collaborations avec des influenceurs.
Le marketing d'influence n'est pas juridiquement une activite de
"representation d'interets", donc Ogilvy, Herezie et Shokola n'y figurent
pas au titre de leurs campagnes. Ne pas confondre les deux graphes.

Lancer :  python outils/extraire_hatvp.py
"""

import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(2**31 - 1)

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "donnees" / "sources" / "hatvp" / "Vues_Separees"
SORTIE = RACINE / "donnees" / "sources" / "hatvp" / "extraits"

# Acteurs de la filiere viande/lait, reperes sur leur denomination HATVP.
# Volontairement large : on filtre ensuite les faux positifs ci-dessous.
MOTS_FILIERE = (
    r"VIANDE|LAIT|BOVIN|PORC|VOLAILLE|FROMAG|CHARCUT|BETAIL|BÉTAIL|OEUF|ŒUF"
    r"|FOIE GRAS|ELEVAGE|ÉLEVAGE|LAPIN|ABATT|CANARD|BOUCHER|PALMIPEDE"
    r"|CAPRIN|OVIN|RUMINANT"
)
NOMS_GROUPES = (
    r"INTERBEV|CNIEL|INAPORC|ANVOL|CIFOG|CNPO|CLIPP|LACTALIS|DANONE|SAVENCIA"
    r"|SODIAAL|BIGARD|COOPERL|TERRENA|FLEURY MICHON|AGRIAL|LAITA|EURIAL"
    r"|SOCOPA|CHARAL|HERTA|BABYBEL|YOPLAIT|ENTREMONT|ISIGNY|SICAREV|ELIVIA"
    r"|GASTRONOME|CULTURE VIANDE|SYNDILAIT|SYNDIFRAIS"
)
PAT_FILIERE = re.compile(MOTS_FILIERE + "|" + NOMS_GROUPES, re.I)

# Faux positifs : "elevages marins" (peche), HLM du Limousin, mutuelles, etc.
PAT_EXCLUS = re.compile(
    r"PECHE|PÊCHE|ELEVAGES MARINS|ÉLEVAGES MARINS|HLM|MUTUAL|MUT FRANCAISE"
    r"|MOVIN|LAIT CONTAMINE|CHEVAL FRANCAIS",
    re.I,
)


def lire(nom):
    chemin = SOURCE / nom
    if not chemin.exists():
        sys.exit(
            f"Fichier absent : {chemin}\n"
            "Decompresse d'abord Vues_Separees_CSV.zip dans donnees/sources/hatvp/."
        )
    with open(chemin, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def pertinent(*champs):
    texte = " ".join(c or "" for c in champs)
    return bool(PAT_FILIERE.search(texte)) and not PAT_EXCLUS.search(texte)


def ecrire(nom, entetes, lignes):
    SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = SORTIE / nom
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(entetes)
        w.writerows(lignes)
    print(f"  {chemin.relative_to(RACINE)}  ({len(lignes)} lignes)")
    return lignes


def main():
    infos = lire("1_informations_generales.csv")
    index = {r["representants_id"]: r for r in infos}

    cibles = {
        r["representants_id"]: r
        for r in infos
        if pertinent(r["denomination"], r["sigle_HATVP"], r["nom_usage_HATVP"])
    }

    # Depenses de lobbying declarees, par exercice.
    depenses = {}
    for e in lire("15_exercices.csv"):
        if e["representants_id"] in cibles:
            depenses.setdefault(e["representants_id"], []).append(e)

    print("Ecriture des extraits :")

    # ---- 1. les organisations de la filiere -----------------------------
    lignes = []
    for rid, r in sorted(cibles.items(), key=lambda x: x[1]["denomination"]):
        # L'exercice le plus recent est souvent l'exercice en cours, non encore
        # declare : tout y est a zero. On retient le dernier exercice REELLEMENT
        # renseigne, et a defaut le plus recent.
        exos = sorted(depenses.get(rid, []), key=lambda e: e["annee_fin"] or "")
        declares = [
            e for e in exos
            if (e["nombre_activites"] or "0") not in ("", "0")
            or (e["montant_depense_sup"] or "0") not in ("", "0", "0.0")
        ]
        dernier = (declares or exos or [{}])[-1]
        lignes.append([
            rid,
            r["denomination"],
            r["sigle_HATVP"],
            r["label_categorie_organisation"],
            r["identifiant_national"],
            r["ville"],
            r["site_web"],
            r["page_twitter"],
            r["page_linkedin"],
            dernier.get("annee_fin", ""),
            dernier.get("montant_depense_inf", ""),
            dernier.get("montant_depense_sup", ""),
            dernier.get("nombre_salaries", ""),
            dernier.get("nombre_activites", ""),
            "OUI" if r["dateCessation"] else "",
        ])
    ecrire(
        "organisations_filiere.csv",
        ["id_hatvp", "denomination", "sigle", "categorie", "siren_ou_rna", "ville",
         "site_web", "twitter", "linkedin", "dernier_exercice", "depense_min_eur",
         "depense_max_eur", "salaries_lobbying", "nb_activites", "cesse"],
        lignes,
    )

    # ---- 2. les mandats : qui travaille pour qui ------------------------
    lignes = []
    for c in lire("4_clients.csv"):
        client = c["denomination_client"] or ""
        if not pertinent(client):
            continue
        prestataire = index.get(c["representants_id"], {})
        lignes.append([
            prestataire.get("denomination", "?"),
            prestataire.get("label_categorie_organisation", ""),
            client,
            c["identifiant_national_client"],
            "ancien" if c["ancienClient"] == "true" else "actif",
            c["dateAjout"],
            c["dateCessation"],
        ])
    lignes.sort(key=lambda x: (x[0], x[2]))
    ecrire(
        "mandats.csv",
        ["prestataire", "categorie_prestataire", "client", "siren_client",
         "statut", "date_debut", "date_fin"],
        lignes,
    )

    # ---- 3. les affiliations : qui est membre de qui --------------------
    lignes = []
    for a in lire("5_affiliations.csv"):
        cible = a["denomination_affiliation"] or ""
        if not pertinent(cible):
            continue
        membre = index.get(a["representants_id"], {})
        lignes.append([
            membre.get("denomination", "?"),
            membre.get("label_categorie_organisation", ""),
            cible,
            a["identifiant_national_affiliation"],
            a["dateCessation"],
        ])
    lignes.sort(key=lambda x: (x[2], x[0]))
    ecrire(
        "affiliations.csv",
        ["membre", "categorie_membre", "affilie_a", "siren_affiliation", "date_fin"],
        lignes,
    )

    print(f"\n{len(cibles)} organisations de la filiere retenues.")


if __name__ == "__main__":
    main()
