# Les artefacts d'aplatissement, mesures — 2026-08-27

Produit par `outils/mesurer_artefacts_aplatissement.py`. Aucun reseau.

L'appariement compare des chaines aplaties — sans accents, sans
espaces. Cela colle les mots voisins et fabrique des chaines absentes
du texte reel : « de la viande frerot » contient « laviandefr ».

- Detections examinees : **385**
- Terme retrouve, **frontiere de mot respectee : 284** (74 %)
- Terme retrouve, **a cheval sur un mot — ARTEFACT : 38** (10 %)
- Terme absent du texte conserve, **inverifiable : 63** (16 %)

## Pourquoi « inverifiable » n'est pas « artefact »

La moisson ne garde que les 900 premiers caracteres de chaque
description, alors que l'appariement a travaille sur le texte
complet. Quand le terme est au-dela, son absence ici ne prouve rien.
Les compter comme des artefacts multiplierait le chiffre par quatre.

## Les artefacts trouves

| Chaine | Entite | Alias | Titre |
|---|---|---|---|
| FlorianOnAir | INTERBEV | @la_viande_fr | LE KEBAB LE PLUS MAISON DE FRANCE ? 😳 |
| FlorianOnAir | INTERBEV | @la_viande_fr | CES 2 FAST-FOODS DU 93 JOUENT EN LIGUE D |
| FlorianOnAir | INTERBEV | @la_viande_fr | Un FAST FOOD SOCIAL dans un ANCIEN MC DO |
| FlorianOnAir | INTERBEV | @la_viande_fr | Elle veut RÉVOLUTIONNER le FAST FOOD ave |
| FlorianOnAir | INTERBEV | @la_viande_fr | MEILLEUR SNACK : GROSSES BARQUETTES de V |
| Bonne Pitance | INTERBEV | @la_viande_fr | Épisode 23 : Coq au Vin Jaune ! Partie 2 |
| Bonne Pitance | INTERBEV | @la_viande_fr | Épisode 23 : Coq au Vin Jaune ! Partie 1 |
| C'est meilleur quand c | INTERBEV | @la_viande_fr | Une boucherie bar discothèque |
| C'est meilleur quand c | INTERBEV | @la_viande_fr | Tartare | Burgers au boeuf d'Aubrac |
| Le Paris d'Alexis | INTERBEV | @la_viande_fr | Ce smash burger dont tout le monde parle |
| Madrange | INAPORC | Le Porc Francais | MADRANGE Les stars du quotidien 2021 - L |
| Madrange | INAPORC | Le Porc Francais | MADRANGE Mon jambon blanc Conservation s |
| Anne Dubndidu | ANVOL | ANVOL | Entremont | L'île de la Réunion, entre montagne et o |
| My Boucherie | INTERBEV | @la_viande_fr | Rumsteck persillé 😍 #legrascestlavie #ja |
| Toscane Lucas | INTERBEV | @la_viande_fr | Babe veut une côte de veau à la Milanais |
| Toscane Lucas | INTERBEV | @la_viande_fr | Babe veut une côte de veau à la Milanais |
| Toscane Lucas | INTERBEV | @la_viande_fr | Soignon | Babe veut des tacos 🌮🇲🇽🪅 Yessss chef ! @ |
| Nota Bene | President (Lactalis) | President | Les présidents des USA et le Groenland # |
| YanissaXoxo | President (Lactalis) | President | J'AI TUÉ MES CHEVEUX ? LE LISSAGE BRESIL |
| FlorianOnAir | Leerdammer (Groupe Bel | Leerdammer | Un REPAS INDONESIEN à AMSTERDAM  - VLOG |
| FlorianOnAir | Leerdammer (Groupe Bel | Leerdammer | Un BURGER en AVOCAT à AMSTERDAM - VLOG # |
| FlorianOnAir | Leerdammer (Groupe Bel | Leerdammer | Une enseigne FAST FOOD de WOK à AMSTERD |
| FlorianOnAir | Leerdammer (Groupe Bel | Leerdammer | AMSTERDAM : Des DISTRIBUTEURS de NOURRIT |
| Bonne Pitance | President (Lactalis) | President | Faire son Pâté (en) Croûte Maison ? Que  |
| Check | President (Lactalis) | | President | Societe | Krisy, Darrell Cole, K1D & Saskia - El P |
| Studio Danielle | President (Lactalis) | President | UNE NUIT DANS LA SUITE LA PLUS CHÈRE DE  |
| AVRE (Explore Media) | President (Lactalis) | President | Un historien de la Seconde Guerre mondia |
| Romain Lanéry | President (Lactalis) | President | "Notre système de santé va bientôt mouri |
| Romain Lanéry | President (Lactalis) | President | Il a racheté le nom Entrepreneurs.com !  |
| Romain Lanéry | President (Lactalis) | President | "99% des crypto vont s'effondrer" | 20 m |
| Romain Lanéry | President (Lactalis) | President | "On ne peut plus prévoir le monde" | 20  |
| Romain Lanéry | President (Lactalis) | President | "Mon job tient sur ce post-it" | 20 minu |
| Bruno Maltor | Entremont (Sodiaal) | Entremont | Ce pays incroyable que les Français évit |
| Amixem | President (Lactalis) | President | ON VIT 24H COMME DES PRÉSIDENTS |
| Aypierre | President (Lactalis) | President | Un débat présidentiel explosif - QSMP #3 |
| Aypierre | President (Lactalis) | President | L'enveloppe des présidentielles - QSMP # |
| Anne Dubndidu | Entremont (Sodiaal) | Entremont | Vlog cosy : dans les coulisses du lancem |
| Ariana | President (Lactalis) | President | MADAME LA PRESIDENTE : MON AVIS SUR LEUR |

### Formes fautives, par frequence

| Forme aplatie | Occurrences |
|---|---:|
| `president` | 23 |
| `viandefr` | 20 |
| `laviandefr` | 5 |
| `aviandefr` | 5 |
| `entremont` | 4 |
| `erdammer` | 4 |
| `porcfrancais` | 2 |
| `eporcfrancais` | 2 |
| `tartare` | 1 |
| `anvol` | 1 |
| `soignon` | 1 |
| `marie` | 1 |

