# BotAI-Assistant

Un assistant de révision qui répond à des questions **à partir de mes propres
cours**, et non de ce qu'un modèle de langage croit savoir.

C'est un projet personnel : je voulais comprendre ce qui se passe réellement dans
un système RAG en le construisant de bout en bout, plutôt qu'en assemblant un
framework qui cache les décisions intéressantes.

## Ce que ça fait

```bash
python ingest.py mes_cours/          # indexe des .md, .txt et .pdf
python ask.py "c'est quoi un graphe biparti ?"
```

```
Un graphe est biparti si l'on peut partitionner ses sommets en deux ensembles
disjoints U et W tels que toute arête relie un sommet de U à un sommet de W
(graphes.md). Le critère pratique pour le vérifier : il est biparti si et
seulement s'il ne contient aucun cycle de longueur impaire.

Sources : graphes.md
```

Sans identifiants, le programme ne s'arrête pas : il bascule en **mode recherche
seule** et affiche les passages retrouvés. La partie coûteuse — l'indexation et
la recherche — tourne entièrement en local.

## Comment c'est fait

```
ingest.py            indexation : dossier -> passages -> base vectorielle
ask.py               interrogation (une question ou mode interactif)
memory/loaders.py    lecture .txt / .md / .pdf (par page)
memory/chunking.py   découpage en passages avec chevauchement
memory/vector_store.py  embeddings locaux + ChromaDB persistant
agents/assistant.py  recherche + rédaction de la réponse par le modèle
```

Le flux est volontairement linéaire : on découpe les documents en passages, on
calcule un embedding par passage avec `all-MiniLM-L6-v2` (en local, donc gratuit
et hors ligne), on les stocke dans ChromaDB. À la question, on embarque la
question dans le même espace vectoriel, on récupère les 4 passages les plus
proches, et on demande au modèle de rédiger une réponse **en n'utilisant que
ces passages**.

## Les trois décisions qui comptent

**Le découpage prime sur le choix du modèle.** Un passage trop court perd son
contexte et son embedding devient vague ; trop long, il mélange plusieurs idées
et la recherche remonte du bruit. `chunking.py` coupe donc en priorité sur les
frontières de paragraphes, puis de phrases, et garde 150 caractères de
chevauchement pour ne pas trancher une explication en deux.

**Les hallucinations se contiennent par le contexte, pas par la politesse.** Le
prompt système impose de répondre uniquement à partir des extraits fournis et de
répondre « ce n'est pas dans les cours que tu m'as donnés » quand ils ne
suffisent pas. Demander gentiment à un modèle de ne pas inventer ne marche pas ;
lui retirer la latitude de le faire, si.

**Les identifiants stables évitent les doublons.** Chaque passage a un
identifiant dérivé du nom de fichier, de sa position et d'une empreinte de son
contenu. Réindexer un cours modifié remplace ses passages au lieu d'empiler des
copies.

## Installation

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

L'authentification passe par le profil OAuth local de la CLI Anthropic, ce qui
évite de manipuler une clé :

```bash
ant auth login
```

Un client `Anthropic()` sans argument lit ce profil automatiquement. Si tu
préfères une clé d'API, pose `ANTHROPIC_API_KEY` dans ton environnement (voir
`.env.example`) — elle a priorité sur le profil.

## État du projet

Ce qui marche :

- indexation de `.txt`, `.md` et `.pdf` (extraction page par page)
- découpage avec chevauchement sur frontières lisibles
- embeddings locaux et base ChromaDB persistante
- recherche sémantique avec attribution des sources
- réindexation idempotente
- mode dégradé sans identifiants

Ce qui n'y est pas encore, et que je sais manquant :

- **pas d'évaluation** — aucune mesure de la pertinence des passages retrouvés,
  c'est la prochaine chose à construire et la plus importante
- **pas de vraie orchestration d'agents** : un seul appel, pas de routage vers
  des outils spécialisés
- pas de découpage adapté à la structure (un titre de section ne pèse pas plus
  qu'une phrase de corps de texte)
- pas de reranking des passages après la recherche vectorielle

## Pourquoi ce projet

Construire la chaîne complète apprend des choses qu'aucun tutoriel ne dit :
que la qualité du découpage décide de la pertinence bien plus que le modèle
choisi, qu'un système qu'on n'évalue pas ne mérite pas la confiance qu'on lui
accorde, et qu'un assistant qui impressionne en démonstration mais que personne
n'utilise trois mois plus tard n'a rien résolu.
