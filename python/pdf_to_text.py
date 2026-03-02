"""PDF zu Markdown (mit LaTeX-Formeln) konvertieren.

Verwendung:
    python python/pdf_to_text.py

Fragt nach dem PDF-Pfad und exportiert Markdown + eingebettete Bilder.
Nutzt pymupdf4llm für LLM-freundliche Markdown-Ausgabe.
"""

import sys
from pathlib import Path

try:
    import pymupdf4llm
    import fitz  # PyMuPDF
except ImportError:
    print("Benötigte Pakete fehlen. Bitte installieren mit:")
    print("  pip install pymupdf pymupdf4llm")
    sys.exit(1)


def pdf_to_markdown(pdf_path: str, output_path: str | None = None) -> str:
    """Konvertiert PDF → Markdown mit LaTeX-Formeln und extrahierten Bildern."""
    pdf = Path(pdf_path)
    if not pdf.exists():
        print(f"Datei nicht gefunden: {pdf}")
        sys.exit(1)

    # Ausgabeverzeichnis
    output_dir = pdf.parent / pdf.stem
    output_dir.mkdir(exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    # Markdown extrahieren
    md_text = pymupdf4llm.to_markdown(
        str(pdf),
        write_images=True,
        image_path=str(images_dir),
    )

    # Markdown-Datei speichern
    if output_path is None:
        md_file = output_dir / f"{pdf.stem}.md"
    else:
        md_file = Path(output_path)

    md_file.write_text(md_text, encoding="utf-8")
    print(f"\nGespeichert: {md_file} ({len(md_text)} Zeichen)")

    # Bilder zählen
    images = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
    if images:
        print(f"Bilder: {len(images)} extrahiert in {images_dir}")
    else:
        # Leeren Ordner entfernen
        images_dir.rmdir()

    return md_text


def pdf_to_text(pdf_path: str, output_path: str | None = None) -> str:
    """Einfacher Text-Export (ohne Formelerkennung)."""
    pdf = Path(pdf_path)
    if not pdf.exists():
        print(f"Datei nicht gefunden: {pdf}")
        sys.exit(1)

    doc = fitz.open(str(pdf))
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    if output_path is None:
        output_path = pdf.with_suffix(".txt")
    else:
        output_path = Path(output_path)

    output_path.write_text(text, encoding="utf-8")
    print(f"Gespeichert: {output_path} ({len(text)} Zeichen)")
    return text


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("PDF-Pfad eingeben: ").strip().strip('"').strip("'")

    print("\nExport-Modus:")
    print("  [1] Markdown + Bilder (empfohlen)")
    print("  [2] Nur Text (.txt)")
    print("  [3] Beides")
    modus = input("Auswahl (1/2/3): ").strip()

    if modus in ("1", "3"):
        pdf_to_markdown(pdf_path)
    if modus in ("2", "3"):
        pdf_to_text(pdf_path)
    if modus not in ("1", "2", "3"):
        print("Ungültige Auswahl.")
        sys.exit(1)
