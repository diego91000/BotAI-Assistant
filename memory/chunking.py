"""Découpage de documents en passages indexables.

Le découpage est la décision qui pèse le plus sur la qualité des réponses :
trop court, le passage perd son contexte et l'embedding devient vague ; trop
long, il mélange plusieurs idées et la recherche remonte du bruit. On coupe donc
sur les frontières de paragraphes quand c'est possible, et on garde un
chevauchement pour ne pas couper une explication en deux.
"""

TAILLE = 800        # caractères visés par passage
CHEVAUCHEMENT = 150  # report sur le passage suivant


def decouper(texte, taille=TAILLE, chevauchement=CHEVAUCHEMENT):
    """-> liste de passages, coupés en priorité sur les fins de paragraphe."""
    texte = "\n".join(ligne.rstrip() for ligne in texte.splitlines())
    texte = texte.strip()
    if not texte:
        return []

    passages, debut = [], 0
    while debut < len(texte):
        fin = debut + taille
        if fin >= len(texte):
            passages.append(texte[debut:].strip())
            break

        # on recule jusqu'à une frontière lisible plutôt que couper un mot
        coupe = texte.rfind("\n\n", debut, fin)
        if coupe == -1 or coupe <= debut:
            coupe = texte.rfind(". ", debut, fin)
        if coupe == -1 or coupe <= debut:
            coupe = texte.rfind(" ", debut, fin)
        if coupe == -1 or coupe <= debut:
            coupe = fin

        passages.append(texte[debut:coupe].strip())
        debut = max(coupe - chevauchement, debut + 1)

    return [p for p in passages if p]
