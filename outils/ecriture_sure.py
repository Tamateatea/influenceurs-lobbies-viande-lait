"""
Ecriture d'un fichier d'etat qui ne peut ni corrompre ni faire planter.

POURQUOI

Le 27/08, la moisson s'est arretee a la 381e chaine sur une
`OSError: [Errno 22]` en ecrivant son fichier de reprise — 24 Mo reecrits
apres chaque chaine, dans un dossier synchronise par OneDrive. Le fichier
etait intact, mais le travail s'est arrete net.

Deux defauts a la fois :

1. **Ecriture directe** : une interruption au mauvais moment laisse un fichier
   tronque, donc un etat de reprise inutilisable.
2. **Aucune tolerance** : un verrou transitoire de synchronisation tue le
   processus entier.

CE QUE FAIT CETTE FONCTION

Elle ecrit dans un fichier temporaire du meme dossier, puis le renomme sur
la cible. Le renommage est atomique : la cible est soit l'ancienne version
complete, soit la nouvelle, jamais un melange.

Et elle reessaie quelques fois avant d'abandonner — un verrou OneDrive dure
rarement plus de quelques secondes. Si elle echoue quand meme, elle le SIGNALE
et rend False, au lieu de lever : c'est a l'appelant de decider si c'est fatal.
"""

import os
import sys
import time
from pathlib import Path


def ecrire_sur(chemin, contenu, essais=4, attente=2.0):
    """Ecrit `contenu` dans `chemin` de facon atomique. Rend True si reussi."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
    for essai in range(essais):
        try:
            temporaire.write_text(contenu, encoding="utf-8")
            os.replace(temporaire, chemin)      # atomique sur Windows aussi
            return True
        except OSError as e:
            if essai < essais - 1:
                time.sleep(attente * (essai + 1))
                continue
            print(f"  ATTENTION : impossible d'ecrire {chemin.name} "
                  f"apres {essais} essais ({e}). Le travail continue, mais la "
                  f"reprise sera plus ancienne.", file=sys.stderr)
            try:
                temporaire.unlink(missing_ok=True)
            except OSError:
                pass
            return False
    return False
