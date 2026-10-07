"""Koordinatensystem mit einem oder mehreren Funktionsgraphen."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np

from ._beschriftung import beschrifte_linien
from ._elemente import Flaeche, Hilfslinie, Punkt, Term, auswerten, zeichne_flaechen, zeichne_hilfslinien, zeichne_punkte
from ._stil import LINIE, LINIENBREITE, achsenteilung, druckstil, gitter, linienstil, nullachsen, speichern


@dataclass
class Kurve:
    """Ein Funktionsgraph.

    term:   Callable `f(x)` (numpy-fähig) oder String wie in den Website-Includes, z. B. "0.1*x^3 - 2*x + 5".
    name:   Beschriftung direkt am Graphen (Mathtext erlaubt, z. B. "$K'$"). Leer → keine Beschriftung.
    stil:   Matplotlib-Linienstil; None → automatisch (durchgezogen, gestrichelt, gepunktet, …).
    von/bis: Definitionsbereich (z. B. ökonomischer Definitionsbereich).
    bei_x:  feste x-Position der Beschriftung; None → automatisch freie Stelle.
    """

    term: Term
    name: str = ""
    stil: object = None
    von: float | None = None
    bis: float | None = None
    bei_x: float | None = None
    breite: float = LINIENBREITE
    extra: dict = field(default_factory=dict)


@druckstil
def funktionsgraph(
    pfad,
    kurven: Sequence[Kurve] = (),
    *,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    xachse: str = "",
    yachse: str = "",
    xhaupt: float | None = None,
    xneben: float | None = None,
    yhaupt: float | None = None,
    yneben: float | None = None,
    flaechen: Sequence[Flaeche] = (),
    hilfslinien: Sequence[Hilfslinie] = (),
    punkte: Sequence[Punkt] = (),
    skizze: bool = False,
    legende: bool = False,
    groesse: tuple[float, float] = (9, 6),
):
    """Zeichnet Funktionsgraphen in Schwarz-Weiß und speichert sie als PNG.

    Ohne `kurven` entsteht ein leeres Koordinatensystem (z. B. zum Einzeichnen).
    `skizze=True`: qualitative Skizze ohne Gitter und Zahlen (nur Achsen).
    `legende=True`: zusätzlich schwarze Legende mit Linienstilen (Standard: direkte Beschriftung).
    """
    fig, ax = plt.subplots(figsize=groesse)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    zeichne_flaechen(ax, flaechen, xlim)

    spanne = ylim[1] - ylim[0]
    linien = []
    for i, k in enumerate(kurven):
        von = xlim[0] if k.von is None else max(k.von, xlim[0])
        bis = xlim[1] if k.bis is None else min(k.bis, xlim[1])
        xs = np.linspace(von, bis, 2000)
        ys = auswerten(k.term, xs)
        # weit außerhalb liegende Werte (Polstellen) nicht verbinden, Rand aber erreichen
        ys = np.where(np.abs(ys - (ylim[0] + ylim[1]) / 2) > 1.5 * spanne, np.nan, ys)
        ax.plot(xs, ys, color=LINIE, linestyle=linienstil(i, k.stil), linewidth=k.breite, label=k.name or None,
                zorder=3, **k.extra)
        linien.append({"x": xs, "y": ys, "name": None if legende else k.name, "bei_x": k.bei_x})

    zeichne_hilfslinien(ax, hilfslinien, xlim, ylim)
    zeichne_punkte(ax, punkte)

    if skizze:
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        x0 = 0 if xlim[0] <= 0 <= xlim[1] else xlim[0]
        y0 = 0 if ylim[0] <= 0 <= ylim[1] else ylim[0]
        pfeil = {"arrowstyle": "-|>", "color": "black", "linewidth": 1.3, "mutation_scale": 16}
        ax.annotate("", xy=(xlim[1], y0), xytext=(xlim[0], y0), arrowprops=pfeil, annotation_clip=False, zorder=2)
        ax.annotate("", xy=(x0, ylim[1]), xytext=(x0, ylim[0]), arrowprops=pfeil, annotation_clip=False, zorder=2)
        hintergrund = {"boxstyle": "round,pad=0.15", "facecolor": "white", "edgecolor": "none"}
        ax.annotate(xachse, (xlim[1], y0), xytext=(-4, 6), textcoords="offset points", ha="right", va="bottom",
                    fontsize=13, bbox=hintergrund, zorder=6)
        ax.annotate(yachse, (x0, ylim[1]), xytext=(8, -2), textcoords="offset points", ha="left", va="top",
                    fontsize=13, bbox=hintergrund, zorder=6)
    else:
        achsenteilung(ax.xaxis, *xlim, xhaupt, xneben)
        achsenteilung(ax.yaxis, *ylim, yhaupt, yneben)
        gitter(ax)
        nullachsen(ax, xlim, ylim)
        ax.set_xlabel(xachse)
        ax.set_ylabel(yachse)

    hindernisse = [(p.x, p.y) for p in punkte]
    if skizze:
        breite, hoehe = xlim[1] - xlim[0], ylim[1] - ylim[0]
        hindernisse += [(xlim[1] - f * breite, y0 + 0.03 * hoehe) for f in (0.03, 0.1, 0.17)]
        hindernisse += [(x0 + f * breite, ylim[1] - 0.04 * hoehe) for f in (0.03, 0.1, 0.17)]
    beschrifte_linien(ax, linien, xlim, ylim, hindernisse_xy=hindernisse)
    if legende and any(k.name for k in kurven):
        leg = ax.legend(loc="best", fontsize=12, framealpha=1, edgecolor="black", handlelength=3.5)
        leg.get_frame().set_linewidth(0.8)

    fig.tight_layout()
    return speichern(fig, pfad)
