# Le signal « transcription », mesure — mesurer_transcriptions

Produit par `outils/mesurer_transcriptions.py`. Aucun quota d'API.

- Videos jugees par Vincent : **175**
- Transcriptions obtenues : **78**
- Vraies collaborations dans cet ensemble : **61**

| Signal | Retenus | Vrais | Precision | Rappel |
|---|---:|---:|---:|---:|
| Transcription | 37 | 30 | 81 % | 49 % |
| Description | 78 | 61 | 78 % | 100 % |

## Ce que la transcription apporte en plus

- Vraies collaborations vues par les deux : **30**
- **Vues par la transcription SEULE : 0**

**Aucune.** Sur cet echantillon, la transcription ne voit rien
que la description ne voyait deja. C'est une mesure, et elle
pese sur la decision de l'appliquer a grande echelle : elle
coute plusieurs secondes par video.


## Limite

Les videos jugees viennent toutes du canal « description ». Une
collaboration annoncee UNIQUEMENT a l'oral n'a jamais eu de raison
d'entrer dans cet echantillon. **Le rappel de la transcription est
donc structurellement sous-estime ici** — seul un tirage aleatoire
le mesurerait honnetement.

