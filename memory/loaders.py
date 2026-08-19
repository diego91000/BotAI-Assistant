"""Lecture des fichiers de cours : texte, markdown et PDF."""
from pathlib import Path

EXTENSIONS = {".txt", ".md", ".pdf"}


def lire_pdf(chemin):
    from pypdf import PdfReader

    pages = []
    for numero, page in enumerate(PdfReader(str(chemin)).pages, 1):
        contenu = (page.extract_text() or "").strip()
        if contenu:
            pages.append(f"[page {numero}]\n{contenu}")
    return "\n\n".join(pages)


def lire(chemin):
    """-> le texte d'un fichier, ou '' si l'extension n'est pas gérée."""
    chemin = Path(chemin)
    if chemin.suffix.lower() == ".pdf":
        return lire_pdf(chemin)
    if chemin.suffix.lower() in EXTENSIONS:
        return chemin.read_text(encoding="utf-8", errors="replace")
    return ""


def parcourir(dossier):
    """-> les fichiers lisibles d'un dossier, récursivement, triés."""
    return sorted(
        c for c in Path(dossier).rglob("*")
        if c.is_file() and c.suffix.lower() in EXTENSIONS
    )
