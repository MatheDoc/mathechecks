"""Grafisches Verfahren der linearen Optimierung (zwei Variablen)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np

from ._beschriftung import beschrifte_linien
from ._elemente import Hilfslinie, Punkt, zeichne_hilfslinien, zeichne_punkte
from ._stil import FLAECHE_HELL, LINIENBREITE, achsenteilung, druckstil, gitter, linienstil, nullachsen, speichern


@dataclass
class Restriktion:
    """Nebenbedingung a·x + b·y ≤ c (bzw. ≥ c); Randgerade wird gezeichnet und mit `name` beschriftet."""

    a: float
    b: float
    c: float
    relation: str = "<="
    name: str = ""
    stil: object = None
    bei_x: float | None = None


@dataclass
class Zielgerade:
    """Gerade a·x + b·y = wert (Iso-Gewinn-/Iso-Kostenlinie), dünn gestrichelt."""

    a: float
    b: float
    wert: float
    name: str = ""
    bei_x: float | None = None


def _gerade(a, b, c, xlim, ylim):
    if abs(b) < 1e-12:
        x0 = c / a
        ys = np.linspace(ylim[0], ylim[1], 400)
        return np.full_like(ys, x0), ys
    xs = np.linspace(xlim[0] - (xlim[1] - xlim[0]), xlim[1] + (xlim[1] - xlim[0]), 1200)
    return xs, (c - a * xs) / b


def _halbebene_schneiden(polygon: list[tuple[float, float]], a, b, c) -> list[tuple[float, float]]:
    """Sutherland-Hodgman: Teil des Polygons mit a·x + b·y ≤ c."""
    ergebnis = []
    for i, p in enumerate(polygon):
        q = polygon[(i + 1) % len(polygon)]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fp <= 1e-12:
            ergebnis.append(p)
        if fp * fq < 0:
            t = fp / (fp - fq)
            ergebnis.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return ergebnis


def zulaessiger_bereich(restriktionen: Sequence[Restriktion], xlim, ylim, nichtnegativ: bool = True):
    """Eckpunkte des zulässigen Bereichs (innerhalb des Zeichenbereichs)."""
    x0, y0 = (max(0, xlim[0]), max(0, ylim[0])) if nichtnegativ else (xlim[0], ylim[0])
    polygon = [(x0, y0), (xlim[1], y0), (xlim[1], ylim[1]), (x0, ylim[1])]
    for r in restriktionen:
        vz = -1 if r.relation.strip() in (">=", "≥", ">") else 1
        polygon = _halbebene_schneiden(polygon, vz * r.a, vz * r.b, vz * r.c)
        if not polygon:
            break
    return polygon


@druckstil
def lineare_optimierung(
    pfad,
    restriktionen: Sequence[Restriktion],
    *,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    xachse: str = "$x$",
    yachse: str = "$y$",
    xhaupt: float | None = None,
    xneben: float | None = None,
    yhaupt: float | None = None,
    yneben: float | None = None,
    zulaessig_markieren: bool = False,
    nichtnegativ: bool = True,
    zielgeraden: Sequence[Zielgerade] = (),
    punkte: Sequence[Punkt] = (),
    hilfslinien: Sequence[Hilfslinie] = (),
    groesse: tuple[float, float] = (9, 7),
):
    """Koordinatensystem mit Randgeraden der Restriktionen.

    zulaessig_markieren: zulässigen Bereich grau füllen (für Lösungen; in der Aufgabe meist aus).
    zielgeraden: z. B. Iso-Gewinngerade durch das Optimum (für Lösungen).
    """
    fig, ax = plt.subplots(figsize=groesse)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    if zulaessig_markieren:
        polygon = zulaessiger_bereich(restriktionen, xlim, ylim, nichtnegativ)
        if len(polygon) >= 3:
            ax.add_patch(plt.Polygon(polygon, closed=True, facecolor=FLAECHE_HELL, edgecolor="none", zorder=1.2))

    linien = []
    for i, r in enumerate(restriktionen):
        xs, ys = _gerade(r.a, r.b, r.c, xlim, ylim)
        ax.plot(xs, ys, color="black", linestyle=linienstil(i, r.stil), linewidth=LINIENBREITE, zorder=3)
        linien.append({"x": xs, "y": ys, "name": r.name, "bei_x": r.bei_x})
    for z in zielgeraden:
        xs, ys = _gerade(z.a, z.b, z.wert, xlim, ylim)
        ax.plot(xs, ys, color="black", linestyle=(0, (2, 2)), linewidth=1.3, zorder=3)
        linien.append({"x": xs, "y": ys, "name": z.name, "bei_x": z.bei_x})

    zeichne_hilfslinien(ax, hilfslinien, xlim, ylim)
    zeichne_punkte(ax, punkte)

    achsenteilung(ax.xaxis, *xlim, xhaupt, xneben)
    achsenteilung(ax.yaxis, *ylim, yhaupt, yneben)
    gitter(ax)
    nullachsen(ax, xlim, ylim)
    ax.set_xlabel(xachse)
    ax.set_ylabel(yachse)

    beschrifte_linien(ax, linien, xlim, ylim, hindernisse_xy=[(p.x, p.y) for p in punkte])
    fig.tight_layout()
    return speichern(fig, pfad)
