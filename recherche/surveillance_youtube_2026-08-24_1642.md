# ⚠ RELEVE INVALIDE — NE PAS CITER

Les signaux 1 (declaration) et 3 (description) de ce releve sont **faux**.
Les 288 pages video ont toutes ete refusees par YouTube en HTTP 429
(« Too Many Requests »), et le script de l'epoque comptait une page non
telechargee comme une video sans signal.

Seul le signal 2 (SponsorBlock, autre serveur) est exploitable ici.

Corrige le meme jour : le script detecte desormais les echecs et refuse de
produire un rapport au-dela de 10 % de pages manquantes. Voir JOURNAL 21.

---

# Surveillance YouTube — 2026-08-24 16:42 UTC

Produit par `outils/surveiller_youtube.py`.
Detail complet : `surveillance_youtube_2026-08-24_1642.csv`.

**Aucune ligne de ce document n'est une preuve de collaboration.**
Ce sont des candidats a verifier a la main.

## Couverture

- Chaines demandees : 13
- Chaines surveillees : 24 (principales et secondaires) — **non resolues : Seb la Frite, Zack Nani**
- Videos examinees : **288**
- Transcriptions recuperees : 0 (sur 26 candidates)

## Ce que chaque signal rapporte

| Signal | Videos | Part |
|---|---|---|
| 1. Case de declaration YouTube | 0 | 0 % |
| 2. Segment SponsorBlock | 26 | 9 % |
| 3. Indice commercial en description | 0 | 0 % |
| **Au moins un signal** | **26** | **9 %** |

## Chaines surveillees

Un createur a souvent plusieurs chaines. Les secondaires sont plus
densement sponsorisees et moins regardees : ne pas les surveiller,
c'est manquer le gisement (JOURNAL 21).

| Createur | Chaine | Nature | Videos | 1+ signal |
|---|---|---|---|---|
| Squeezie | SQUEEZIE | principale | 12 | 1 |
| Squeezie | SQUEEZIE GAMING | secondaire | 12 | 1 |
| Squeezie | Squeezie - Rediffusions | secondaire | 12 | 0 |
| Inoxtag | Inoxtag | principale | 12 | 3 |
| Inoxtag | Inoxtag 2.0 | secondaire | 12 | 11 |
| Valouzz | Valouzz | principale | 12 | 0 |
| Mister V | Mister V | principale | 12 | 4 |
| Mister V | Mister V Music | secondaire | 12 | 0 |
| Mcfly et Carlito | Mcfly et Carlito | principale | 12 | 2 |
| Michou | Michou | principale | 12 | 1 |
| Michou | MichouOff | secondaire | 12 | 0 |
| Michou | MichouRediff | secondaire | 12 | 0 |
| Domingo | Domingo Replay | secondaire | 12 | 0 |
| Domingo | Domingo | principale | 12 | 0 |
| Domingo | Domingo Gomes | secondaire | 12 | 0 |
| Domingo | Domingo Legal | secondaire | 12 | 0 |
| Domingo | Domingo Officiel | secondaire | 12 | 0 |
| Norman | Norman | principale | 12 | 0 |
| Norman | Norman Sann | secondaire | 12 | 0 |
| Norman | Norman Woods | secondaire | 12 | 0 |
| Grimkujow | Grimkujow | principale | 12 | 2 |
| LeBouseuh | LeBouseuh | principale | 12 | 0 |
| Kameto | Kameto - Replays et VODs | secondaire | 12 | 0 |
| Kameto | Kameto | principale | 12 | 1 |

## ENTITES DE LA FILIERE VIANDE/LAIT TROUVEES

Aucune. **Ce n'est pas un echec : c'est une mesure.**

## Desaccords entre signaux

Le desaccord est le cas interessant : un segment sponsorise sans
declaration, ou une declaration sans segment. Voir METHODOLOGIE 10.

| Situation | Videos |
|---|---|
| Segment SponsorBlock SANS case cochee | 26 |
| Case cochee SANS segment SponsorBlock | 0 |
| Indice en description SANS case cochee | 0 |

