# Commercial Content Library TikTok — 2026-08-25 05:38 UTC

Produit par `outils/tester_tiktok_commercial.py`.
Hypotheses testees : **TT-02** (les publications organiques a label de
partenariat y figurent) et **TT-03** (interrogeable par annonceur).

| Appel | Page | Resultat | Erreur |
|---|---|---|---|
| `commercial_content/query` | page 1 | ERREUR | HTTP 400 — {"error":{"code":"invalid_params","message":"`filters.content_published_date_range.max: 20260825` is invalid. Please provide a value before today's d |

## Aucun contenu retourne

Lire la colonne Erreur. Un refus d'authentification et un
resultat vide ne disent pas la meme chose.

