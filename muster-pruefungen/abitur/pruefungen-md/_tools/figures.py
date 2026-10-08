"""PDF-Werkzeuge fuer die Konvertierung von Abitur-Pruefungen (PDF -> Markdown).

Aufrufe (vom Repo-Root; <pdf> = Pfad oder nur Dateiname, wird unter
muster-pruefungen/abitur/pruefungen/ gesucht; Seiten 1-basiert wie "Seite x von y"):

  python muster-pruefungen/abitur/pruefungen-md/_tools/figures.py render <pdf> [--seiten 3-5] [--dpi 150]
      Rendert Seiten als PNG in einen Temp-Ordner (zum Lesen von Formeln/Grafiken) und
      gibt die Pfade sowie die Seitengroesse in pt aus.

  python muster-pruefungen/abitur/pruefungen-md/_tools/figures.py crop <pdf> <seite> <ziel.png> [--clip x0 y0 x1 y1]
      Schneidet eine Abbildung aus. Ohne --clip wird die Bounding-Box aus Rasterbildern und
      Vektorpfaden automatisch bestimmt; mit --clip (in pt, Ursprung oben links) manuell.
      Der verwendete Ausschnitt wird ausgegeben, damit er bei Bedarf nachjustiert werden kann.

extract_figure() bleibt fuer aeltere, pruefungsspezifische extract_figures.py-Skripte erhalten.
"""
import argparse
import pathlib
import sys
import tempfile

import pymupdf

PDF_ROOT = pathlib.Path(__file__).resolve().parents[2] / "pruefungen"


def filtered_drawing_rects(page, header_y_threshold: float = 100, min_height: float = 3):
    """Vektor-Rechtecke einer Seite ohne Kopf-/Trennlinien und Kopf-Logos."""
    rects = []
    for d in page.get_drawings():
        r = d["rect"]
        if r.height < min_height:
            continue  # Kopf-/Trennlinie (auch segmentiert, unabhaengig von Breite)
        if r.y0 < header_y_threshold:
            continue  # Logo/Linie im Kopfbereich
        rects.append(r)
    return rects


def figure_bbox(page, pad: float = 10):
    """Bounding-Box (mit Padding) aus Bildern + gefilterten Vektorpfaden einer Seite."""
    image_rects = []
    for im in page.get_images(full=True):
        for r in page.get_image_rects(im[0]):
            image_rects.append(r)

    all_rects = image_rects + filtered_drawing_rects(page)
    if not all_rects:
        return page.rect

    x0 = min(r.x0 for r in all_rects)
    y0 = min(r.y0 for r in all_rects)
    x1 = max(r.x1 for r in all_rects)
    y1 = max(r.y1 for r in all_rects)
    return pymupdf.Rect(x0 - pad, y0 - pad, x1 + pad, y1 + pad) & page.rect


def extract_figure(pdf_path, page_index: int, out_path, dpi: int = 200, pad: float = 10, clip=None):
    """Schneidet die Abbildung(en) einer PDF-Seite (0-basierter Index) aus und speichert sie als PNG."""
    doc = pymupdf.open(str(pdf_path))
    page = doc[page_index]
    clip = pymupdf.Rect(*clip) if clip else figure_bbox(page, pad=pad)
    page.get_pixmap(dpi=dpi, clip=clip).save(str(out_path))
    doc.close()
    return clip


def find_pdf(name: str) -> pathlib.Path:
    p = pathlib.Path(name)
    if p.is_file():
        return p
    treffer = [t for t in PDF_ROOT.rglob("*.pdf") if t.name.lower() == p.name.lower()]
    if len(treffer) != 1:
        sys.exit(f"PDF '{name}' nicht eindeutig gefunden ({len(treffer)} Treffer unter {PDF_ROOT})")
    return treffer[0]


def parse_seiten(spec: str, anzahl: int):
    if not spec:
        return list(range(1, anzahl + 1))
    seiten = []
    for teil in spec.split(","):
        a, _, b = teil.partition("-")
        seiten.extend(range(int(a), int(b or a) + 1))
    return seiten


def cmd_render(args):
    pdf = find_pdf(args.pdf)
    out = pathlib.Path(tempfile.gettempdir()) / "pruefungen-render" / pdf.stem
    out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(pdf))
    print(f"{pdf.name}: {len(doc)} Seiten, Seitengroesse {doc[0].rect.width:.0f} x {doc[0].rect.height:.0f} pt")
    for s in parse_seiten(args.seiten, len(doc)):
        ziel = out / f"seite-{s:02d}.png"
        doc[s - 1].get_pixmap(dpi=args.dpi).save(str(ziel))
        print(ziel)
    doc.close()


def cmd_crop(args):
    pdf = find_pdf(args.pdf)
    ziel = pathlib.Path(args.ziel)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    clip = extract_figure(pdf, args.seite - 1, ziel, dpi=args.dpi, clip=args.clip)
    print(f"{ziel}  (Seite {args.seite}, clip {clip.x0:.0f} {clip.y0:.0f} {clip.x1:.0f} {clip.y1:.0f})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="Seiten als PNG in einen Temp-Ordner rendern")
    r.add_argument("pdf")
    r.add_argument("--seiten", default="", help="z. B. 3-5 oder 2,4,7 (Standard: alle)")
    r.add_argument("--dpi", type=int, default=150)
    r.set_defaults(func=cmd_render)

    c = sub.add_parser("crop", help="Abbildung einer Seite als PNG ausschneiden")
    c.add_argument("pdf")
    c.add_argument("seite", type=int, help="1-basiert")
    c.add_argument("ziel", help="z. B. <pruefung-ordner>/_assets/a2-4-abb1.png")
    c.add_argument("--clip", type=float, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    c.add_argument("--dpi", type=int, default=200)
    c.set_defaults(func=cmd_crop)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
