"""Gemeinsamer Druckstil für Klausurdiagramme.

Regeln: Linien immer schwarz (Unterscheidung über Linienstil + direkte Beschriftung),
Graustufen nur für Flächen und Balken, dichtes Ablese-Gitter, Dezimalkomma.
"""

from __future__ import annotations

import functools
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

LINIE = "black"
LINIENBREITE = 2.0
# Reihenfolge = automatische Zuordnung bei mehreren Graphen (durchgezogen, gestrichelt, gepunktet, Strich-Punkt, kurz gestrichelt)
LINIENSTILE = ["-", (0, (7, 3)), (0, (1.2, 2.4)), (0, (8, 2.5, 1.5, 2.5)), (0, (3, 2))]
FLAECHE_HELL = "0.85"
FLAECHE_DUNKEL = "0.6"
GITTER_HAUPT = {"color": "0.55", "linewidth": 0.8}
GITTER_NEBEN = {"color": "0.83", "linewidth": 0.5}
NULLACHSE = {"color": "black", "linewidth": 1.6}
DPI = 200

RC = {
    "font.size": 12,
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "mathtext.fontset": "dejavusans",
    "axes.edgecolor": "black",
    "axes.linewidth": 1.0,
    "text.color": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "axes.unicode_minus": True,
    "hatch.color": "0.3",
    "hatch.linewidth": 0.8,
    "lines.solid_capstyle": "butt",
}


def druckstil(func):
    """Führt die Diagrammfunktion im einheitlichen rcParams-Kontext aus."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with plt.rc_context(RC):
            return func(*args, **kwargs)

    return wrapper


def linienstil(index: int, vorgabe=None):
    return vorgabe if vorgabe is not None else LINIENSTILE[index % len(LINIENSTILE)]


def zahl(wert: float, stellen: int | None = None) -> str:
    """Zahl in deutscher Schreibweise (Dezimalkomma, echtes Minuszeichen), ohne überflüssige Nullen."""
    if stellen is None:
        text = f"{wert:.10g}"
        if "e" in text:
            text = f"{wert:.10f}"
    else:
        text = f"{wert:.{stellen}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in ("-0", ""):
        text = "0"
    return text.replace("-", "\u2212").replace(".", ",")


def _nachkommastellen(schritt: float) -> int:
    for d in range(0, 8):
        if abs(round(schritt, d) - schritt) < 1e-9 * max(1.0, abs(schritt)):
            return d
    return 8


def tick_formatter(schritt: float) -> FuncFormatter:
    d = _nachkommastellen(schritt)

    def fmt(wert, _pos):
        return zahl(round(wert, d), d)

    return FuncFormatter(fmt)


def schoene_schritte(spanne: float, ziel: int = 8) -> tuple[float, float]:
    """Haupt- und Nebenschrittweite, sodass etwa `ziel` Hauptintervalle entstehen."""
    roh = spanne / max(ziel, 1)
    if roh <= 0:
        return 1.0, 0.5
    groesse = 10 ** math.floor(math.log10(roh))
    for faktor in (1, 2, 2.5, 5, 10):
        if faktor * groesse >= roh * 0.999:
            break
    haupt = faktor * groesse
    neben = haupt / (4 if faktor == 2 else 5)
    return haupt, neben


def achsenteilung(achse, lo: float, hi: float, haupt=None, neben=None, ziel: int = 8) -> float:
    auto_haupt, auto_neben = schoene_schritte(hi - lo, ziel)
    if haupt is None:
        haupt = auto_haupt
        if neben is None:
            neben = auto_neben
    if neben is None:
        neben = haupt / 5
    achse.set_major_locator(MultipleLocator(haupt))
    achse.set_minor_locator(MultipleLocator(neben))
    achse.set_major_formatter(tick_formatter(haupt))
    return haupt


def gitter(ax, achse: str = "both", neben: bool = True) -> None:
    ax.set_axisbelow(True)
    ax.grid(which="major", axis=achse, **GITTER_HAUPT)
    if neben:
        ax.grid(which="minor", axis=achse, **GITTER_NEBEN)


def nullachsen(ax, xlim, ylim) -> None:
    if ylim[0] <= 0 <= ylim[1]:
        ax.axhline(0, zorder=1.5, **NULLACHSE)
    if xlim[0] <= 0 <= xlim[1]:
        ax.axvline(0, zorder=1.5, **NULLACHSE)


def speichern(fig, pfad) -> Path:
    pfad = Path(pfad)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pfad, dpi=DPI, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)
    return pfad


def mathe_name(name: str) -> str:
    """Bezeichner für die Verwendung innerhalb einer Mathtext-Formel (ohne äußere $)."""
    if name.startswith("$") and name.endswith("$"):
        return name[1:-1]
    if len(name) == 1:
        return name
    return r"\mathrm{" + name.replace(" ", r"\ ") + "}"
