"""Base vectorielle : embeddings locaux + ChromaDB persistant.

Le modèle d'embedding tourne en local (sentence-transformers), donc l'indexation
ne coûte rien et ne sort pas de la machine. Seule la génération de la réponse
appelle un modèle distant.
"""
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "vector_db"
COLLECTION = "epita_courses"
MODELE = "all-MiniLM-L6-v2"

_client = chromadb.PersistentClient(path=DB_PATH)
_collection = _client.get_or_create_collection(COLLECTION)
_modele = None


def modele():
    """Chargé à la demande : l'import est lent, et l'ingestion n'en a pas
    toujours besoin (ex. `--reset`)."""
    global _modele
    if _modele is None:
        _modele = SentenceTransformer(MODELE)
    return _modele


def identifiant(source, index, texte):
    """Identifiant stable : réindexer le même fichier remplace ses passages au
    lieu d'en créer des doublons."""
    empreinte = hashlib.sha1(texte.encode()).hexdigest()[:8]
    return f"{source}:{index}:{empreinte}"


def ajouter(passages, source):
    """Indexe les passages d'un document. -> nombre de passages ajoutés."""
    if not passages:
        return 0
    embeddings = modele().encode(passages).tolist()
    _collection.upsert(
        documents=passages,
        embeddings=embeddings,
        ids=[identifiant(source, i, p) for i, p in enumerate(passages)],
        metadatas=[{"source": source, "passage": i} for i in range(len(passages))],
    )
    return len(passages)


def chercher(question, n=4):
    """-> liste de {texte, source, distance}, du plus proche au plus lointain."""
    if compter() == 0:
        return []
    embedding = modele().encode(question).tolist()
    brut = _collection.query(query_embeddings=[embedding], n_results=n)
    resultats = []
    for texte, meta, distance in zip(
        brut["documents"][0], brut["metadatas"][0], brut["distances"][0]
    ):
        resultats.append({
            "texte": texte,
            "source": (meta or {}).get("source", "?"),
            "distance": distance,
        })
    return resultats


def compter():
    return _collection.count()


def vider():
    global _collection
    _client.delete_collection(COLLECTION)
    _collection = _client.get_or_create_collection(COLLECTION)
