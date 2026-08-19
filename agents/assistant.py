"""L'assistant : retrouve les passages pertinents, puis fait rédiger la réponse.

La règle qui compte est dans le prompt système : le modèle répond à partir des
passages fournis, et dit qu'il ne sait pas quand ils ne suffisent pas. C'est ce
qui sépare un assistant de cours d'un modèle qui invente une réponse plausible.
"""
import anthropic

from memory import vector_store

MODELE = "claude-opus-5"

SYSTEME = """Tu es un assistant qui aide un étudiant à réviser ses cours.

Tu réponds UNIQUEMENT à partir des extraits de cours fournis dans le message.
Si les extraits ne contiennent pas la réponse, dis-le franchement : « Ce n'est
pas dans les cours que tu m'as donnés. » N'invente jamais une définition ni un
exemple qui ne s'y trouve pas.

Réponds en français, de façon directe et pédagogique. Cite la source entre
parenthèses quand tu t'appuies sur un extrait précis."""


def construire_message(question, passages):
    extraits = "\n\n".join(
        f"--- extrait {i} (source : {p['source']}) ---\n{p['texte']}"
        for i, p in enumerate(passages, 1)
    )
    return f"Extraits de cours :\n\n{extraits}\n\nQuestion de l'étudiant : {question}"


def repondre(question, n=4):
    """-> (réponse, passages utilisés).

    Sans identifiants Anthropic, renvoie les passages retrouvés sans les faire
    rédiger : la recherche sémantique reste utilisable seule.
    """
    passages = vector_store.chercher(question, n=n)
    if not passages:
        return ("Aucun cours n'est indexé. Lance d'abord : python ingest.py <dossier>",
                [])

    try:
        client = anthropic.Anthropic()
    except TypeError:
        return (_sans_modele(passages, "aucun identifiant Anthropic trouvé"), passages)

    try:
        reponse = client.messages.create(
            model=MODELE,
            max_tokens=4096,
            system=SYSTEME,
            messages=[{"role": "user", "content": construire_message(question, passages)}],
        )
        texte = "".join(b.text for b in reponse.content if b.type == "text")
        return texte, passages
    except TypeError:
        # le SDK ne lève pas AuthenticationError quand *aucun* identifiant n'est
        # résolvable : il échoue en construisant les en-têtes de la requête
        return (_sans_modele(passages, "aucun identifiant Anthropic trouvé"), passages)
    except anthropic.AuthenticationError:
        return (_sans_modele(passages, "aucun identifiant Anthropic trouvé"), passages)
    except anthropic.APIConnectionError:
        return (_sans_modele(passages, "pas de connexion à l'API"), passages)
    except anthropic.RateLimitError:
        return (_sans_modele(passages, "quota dépassé"), passages)
    except anthropic.APIStatusError as e:
        return (_sans_modele(passages, f"erreur API {e.status_code}"), passages)


def _sans_modele(passages, raison):
    lignes = [f"[mode recherche seule — {raison}]",
              "Voici les passages les plus proches de ta question :", ""]
    for i, p in enumerate(passages, 1):
        lignes.append(f"{i}. ({p['source']}) {p['texte'][:300]}...")
    return "\n".join(lignes)
