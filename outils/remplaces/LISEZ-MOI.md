# Outils remplaces

Ces scripts ne servent plus. Ils sont **conserves, pas supprimes**, parce que
des entrees du JOURNAL citent leurs resultats : effacer l'outil qui a produit
une mesure rend cette mesure invérifiable, et la regle du projet est qu'une
mesure doit pouvoir etre refaite.

| Outil | Remplace par | Pourquoi |
|---|---|---|
| `extraire_descriptions_youtube.py` | `moissonner_videos.py` | Telechargeait les pages une par une. L'API rend 50 videos avec leurs descriptions pour 1 unite de quota — 50 fois moins cher, et sans la limitation HTTP 429 qui a bloque la journee du 24/08. |
| `test_croise_youtube.py` | `surveiller_youtube.py` | Premier test des quatre signaux, ecrit avant que la chaine ne soit consolidee. |

**Ne pas les relancer.** Ils lisent des chemins et des formats qui ont change.
