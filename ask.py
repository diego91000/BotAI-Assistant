#!/usr/bin/env python3
"""Pose une question à l'assistant.

    python ask.py "c'est quoi un graphe biparti ?"
    python ask.py            # mode interactif
"""
import sys

from agents.assistant import repondre


def poser(question, sources=False):
    reponse, passages = repondre(question)
    print(f"\n{reponse}\n")
    if sources and passages:
        print("Sources :", ", ".join(sorted({p["source"] for p in passages})))


def main():
    if len(sys.argv) > 1:
        poser(" ".join(sys.argv[1:]), sources=True)
        return 0

    print("Assistant de cours — Ctrl-C ou ligne vide pour quitter.")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not question:
            return 0
        poser(question, sources=True)


if __name__ == "__main__":
    sys.exit(main())
