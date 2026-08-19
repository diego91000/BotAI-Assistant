#!/usr/bin/env python3
"""Indexe un dossier de cours dans la base vectorielle.

    python ingest.py mes_cours/
    python ingest.py mes_cours/ --reset
"""
import argparse
import sys

from memory import chunking, loaders, vector_store


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dossier", help="dossier contenant les .txt, .md ou .pdf")
    ap.add_argument("--reset", action="store_true", help="vide l'index avant d'indexer")
    args = ap.parse_args()

    if args.reset:
        vector_store.vider()
        print("index vidé")

    fichiers = loaders.parcourir(args.dossier)
    if not fichiers:
        print(f"aucun .txt, .md ou .pdf trouvé dans {args.dossier}")
        return 1

    total = 0
    for chemin in fichiers:
        texte = loaders.lire(chemin)
        if not texte.strip():
            print(f"  {chemin.name} : vide ou illisible, ignoré")
            continue
        passages = chunking.decouper(texte)
        n = vector_store.ajouter(passages, source=chemin.name)
        total += n
        print(f"  {chemin.name} : {n} passages")

    print(f"\n{total} passages indexés — {vector_store.compter()} au total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
