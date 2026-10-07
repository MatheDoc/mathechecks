"""Gemeinsame Diagrammelemente: Terme, Punkte, Hilfslinien, Flächen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Union

import numpy as np

from ._stil import FLAECHE_HELL

Term = Union[Callable, str, float, int]

_NAMESPACE = {
    "exp": np.exp,
    "ln": np.log,
    "log": np.log,  # wie math.js auf der Website: log = natürlicher Logarithmus
    "log10": np.log10,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "e": np.e,
    "pi": np.pi,
}


def auswerten(term: Term, xs: np.ndarray) -> np.ndarray:
    """Wertet Callable, Zahl oder Term-String (Syntax wie in den Website-Includes, `^` erlaubt) aus."""
    with np.errstate(all="ignore"):
        if callable(term):
            ys = term(xs)
        elif isinstance(term, str):
            ys = eval(term.replace("^", "**"), {"__builtins__": {}}, {**_NAMESPACE, "x": xs})
        else:
            ys = float(term)
    ys = np.asarray(ys, dtype=float)
    if ys.ndim == 0:
        ys = np.full_like(xs, float(ys), dtype=float)
    return ys


@dataclass
class Punkt:
    """Markierter Punkt. Nur in Lösungen oder wenn der Punkt Teil der Aufgabenstellung ist."""

    x: float
    y: float
    name: str = ""
    position: str = "oben rechts"  # Kombination aus oben/unten und links/rechts


@dataclass
class Hilfslinie:
    """Gestrichelte Hilfslinie. `x` gesetzt → senkrecht, `y` gesetzt → waagerecht; `von`/`bis` begrenzen sie."""

    x: float | None = None
    y: float | None = None
    von: float | None = None
    bis: float | None = None


@dataclass
class Flaeche:
    """Fläche zwischen `oben` und `unten` auf [von, bis]; grau gefüllt oder schraffiert."""

    oben: Term
    unten: Term = 0
    von: float | None = None
    bis: float | None = None
    schraffur: bool = False
    grau: str = FLAECHE_HELL
    name: str = ""


def zeichne_flaechen(ax, flaechen, xlim) -> None:
    for fl in flaechen:
        von = xlim[0] if fl.von is None else fl.von
        bis = xlim[1] if fl.bis is None else fl.bis
        xs = np.linspace(von, bis, 600)
        y1 = auswerten(fl.oben, xs)
        y2 = auswerten(fl.unten, xs)
        if fl.schraffur:
            ax.fill_between(xs, y1, y2, facecolor="none", edgecolor="0.3", hatch="///", linewidth=0, zorder=1.2)
        else:
            ax.fill_between(xs, y1, y2, facecolor=fl.grau, edgecolor="none", zorder=1.2)
        if fl.name:
            mitte = len(xs) // 2
            ax.text(xs[mitte], (y1[mitte] + y2[mitte]) / 2, fl.name, ha="center", va="center", fontsize=13,
                    fontweight="bold", zorder=6)


def zeichne_hilfslinien(ax, hilfslinien, xlim, ylim) -> None:
    for h in hilfslinien:
        stil = {"color": "black", "linewidth": 1.0, "linestyle": (0, (4, 3)), "zorder": 2.5}
        if h.x is not None:
            ax.plot([h.x, h.x], [ylim[0] if h.von is None else h.von, ylim[1] if h.bis is None else h.bis], **stil)
        if h.y is not None:
            ax.plot([xlim[0] if h.von is None else h.von, xlim[1] if h.bis is None else h.bis], [h.y, h.y], **stil)


def zeichne_punkte(ax, punkte) -> None:
    for p in punkte:
        ax.plot(p.x, p.y, "o", color="black", markersize=6, zorder=5)
        if p.name:
            dx = -8 if "links" in p.position else 8
            dy = -8 if "unten" in p.position else 8
            ax.annotate(
                p.name, (p.x, p.y), xytext=(dx, dy), textcoords="offset points",
                ha="right" if dx < 0 else "left", va="top" if dy < 0 else "bottom", fontsize=13, zorder=6,
                bbox={"boxstyle": "round,pad=0.1", "facecolor": "white", "edgecolor": "none", "alpha": 0.85},
            )
