# Test API Meta Ad Library — 2026-08-24 16:34 UTC

Produit par `outils/tester_meta_adlibrary.py`.
Hypothese testee : **IG-02** — l'API expose-t-elle les contenus de marque ?

## Ce que chaque requete a rendu

| Entite | Terme | ad_type | Resultat | Erreur |
|---|---|---|---|---|
| CNIEL | produits laitiers | `ALL` | ERREUR | HTTP 400 — Application does not have permission for this action |
| CNIEL | produits laitiers | `POLITICAL_AND_ISSUE_ADS` | ERREUR | HTTP 400 — Application does not have permission for this action |
| CNIEL | cniel | `ALL` | ERREUR | HTTP 400 — Application does not have permission for this action |
| CNIEL | cniel | `POLITICAL_AND_ISSUE_ADS` | ERREUR | HTTP 400 — Application does not have permission for this action |
| INTERBEV | interbev | `ALL` | ERREUR | HTTP 400 — Application does not have permission for this action |
| INTERBEV | interbev | `POLITICAL_AND_ISSUE_ADS` | ERREUR | HTTP 400 — Application does not have permission for this action |
| INTERBEV | aimez la viande | `ALL` | ERREUR | HTTP 400 — Application does not have permission for this action |
| INTERBEV | aimez la viande | `POLITICAL_AND_ISSUE_ADS` | ERREUR | HTTP 400 — Application does not have permission for this action |
| INAPORC | le porc francais | `ALL` | ERREUR | HTTP 400 — Application does not have permission for this action |
| INAPORC | le porc francais | `POLITICAL_AND_ISSUE_ADS` | ERREUR | HTTP 400 — Application does not have permission for this action |
| ANVOL | volaille francaise | `ALL` | ERREUR | HTTP 400 — Application does not have permission for this action |
| ANVOL | volaille francaise | `POLITICAL_AND_ISSUE_ADS` | ERREUR | HTTP 400 — Application does not have permission for this action |

## Aucune annonce retournee

Ce n'est pas forcement un echec : lire la colonne Erreur ci-dessus.
Un refus d'authentification et un resultat vide ne disent pas la
meme chose.

