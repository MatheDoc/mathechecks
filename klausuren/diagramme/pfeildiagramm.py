"""Pfeildiagramme: Übergangsgraphen (Markov-Ketten) und Verflechtungsdiagramme (Gozinto-Graphen)."""

from __future__ import annotations

import math
from typing import Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.path import Path as MplPath

from ._stil import druckstil, speichern, zahl

Kanten = Mapping[tuple[str, str], "float | str | None"]


def kanten_aus_matrix(von: Sequence[str], nach: Sequence[str], matrix, weglassen=(0,)) -> dict:
    """Kanten aus einer Matrix, deren Eintrag in Zeile i, Spalte j die Kante von[i] → nach[j] beschreibt.

    Liegt eine Übergangsmatrix spaltenweise vor (Spalte = von), vorher transponieren.
    """
    kanten = {}
    for i, v in enumerate(von):
        for j, n in enumerate(nach):
            wert = matrix[i][j]
            if wert in weglassen:
                continue
            kanten[(v, n)] = wert
    return kanten


def _text(wert, stellen):
    if wert is None:
        return "\u2003\u2003"
    return zahl(wert, stellen) if isinstance(wert, (int, float)) else wert


def _einheit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else np.array([0.0, 1.0])


@druckstil
def pfeildiagramm(
    pfad,
    positionen: Mapping[str, tuple[float, float]],
    kanten: Kanten,
    *,
    radius: float = 0.45,
    kruemmung: float = 0.0,
    beschriftung_t: float | None = None,
    stellen: int = 4,
    groesse: tuple[float, float] | None = None,
    massstab: float = 1.0,
):
    """Gerichteter Graph mit kreisförmigen Knoten und beschrifteten Pfeilen.

    positionen: Knotenname → (x, y). kanten: (von, nach) → Wert (Zahl, Mathtext oder None = leeres Kästchen).
    Gegenläufige Kanten werden automatisch gebogen, Schleifen (von == nach) außen angesetzt.
    beschriftung_t: feste Lage der Beschriftung entlang der Kante (0 = Start, 1 = Ziel);
                    None → automatisch zwischen 0,25 und 0,75 mit größtmöglichem Abstand zu anderen Kanten.
    """
    P = {k: np.array(v, dtype=float) for k, v in positionen.items()}
    zentrum = np.mean(list(P.values()), axis=0)

    xs = [p[0] for p in P.values()]
    ys = [p[1] for p in P.values()]
    hat_schleifen = any(a == b for a, b in kanten)
    rand = radius * (3.6 if hat_schleifen else 1.6)
    xlim = (min(xs) - rand, max(xs) + rand)
    ylim = (min(ys) - rand, max(ys) + rand)
    if groesse is None:
        groesse = ((xlim[1] - xlim[0]) * 1.15 * massstab, (ylim[1] - ylim[0]) * 1.15 * massstab)
    fig, ax = plt.subplots(figsize=groesse)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")

    pfeil = {"arrowstyle": "-|>,head_length=0.55,head_width=0.3", "mutation_scale": 16, "color": "black",
             "linewidth": 1.3, "zorder": 2}
    etikett = {"ha": "center", "va": "center", "fontsize": 12, "zorder": 4,
               "bbox": {"boxstyle": "round,pad=0.12", "facecolor": "white", "edgecolor": "none"}}
    luecke = {**etikett, "bbox": {"boxstyle": "square,pad=0.25", "facecolor": "white", "edgecolor": "black",
                                  "linewidth": 0.9}}

    kurven: list = []
    belegt: list = []
    for (a, b), wert in kanten.items():
        stil = luecke if wert is None else etikett
        if a == b:
            c = P[a]
            d = _einheit(c - zentrum)
            phi = math.atan2(d[1], d[0])
            richtung = lambda w: np.array([math.cos(phi + w), math.sin(phi + w)])
            s = c + radius * richtung(0.55)
            e = c + radius * richtung(-0.55)
            c1 = c + radius * 2.6 * richtung(0.75)
            c2 = c + radius * 2.6 * richtung(-0.75)
            pfad_ = MplPath([s, c1, c2, e], [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4])
            ax.add_patch(FancyArrowPatch(path=pfad_, **pfeil))
            spitze = (s + 3 * c1 + 3 * c2 + e) / 8
            schleifen_punkt = spitze + d * radius * 0.45
            ax.text(*schleifen_punkt, _text(wert, stellen), **stil)
            belegt.append(np.repeat(schleifen_punkt[None, :], 5, axis=0))
            continue

        p, q = P[a], P[b]
        f = kruemmung if (b, a) not in kanten else max(kruemmung, 0.18)
        mitte = (p + q) / 2
        dxy = q - p
        kontroll = mitte + f * np.array([dxy[1], -dxy[0]])
        s = p + radius * _einheit(kontroll - p)
        e = q + radius * _einheit(kontroll - q)
        if abs(f) < 1e-9:
            pfad_ = MplPath([s, e], [MplPath.MOVETO, MplPath.LINETO])
        else:
            pfad_ = MplPath([s, kontroll, e], [MplPath.MOVETO, MplPath.CURVE3, MplPath.CURVE3])
        ax.add_patch(FancyArrowPatch(path=pfad_, **pfeil))
        kurven.append((s, kontroll if abs(f) >= 1e-9 else (s + e) / 2, e, wert, stil))

    # Beschriftungen entlang der Kanten so legen, dass sie Kreuzungen und anderen Beschriftungen ausweichen
    def bezier(k, t):
        s, c, e = k[:3]
        return (1 - t) ** 2 * s + 2 * (1 - t) * t * c + t**2 * e

    proben = [np.array([bezier(k, t) for t in np.linspace(0, 1, 60)]) for k in kurven]
    ts = np.array([beschriftung_t]) if beschriftung_t is not None else np.linspace(0.25, 0.75, 21)
    for i, k in enumerate(kurven):
        hindernisse = np.vstack([proben[j] for j in range(len(kurven)) if j != i] + belegt + [np.zeros((0, 2))])
        kandidaten = np.array([bezier(k, t) for t in ts])
        if len(hindernisse):
            d = np.linalg.norm(kandidaten[:, None, :] - hindernisse[None, :, :], axis=2).min(axis=1)
        else:
            d = np.zeros(len(ts))
        score = np.minimum(d, radius * 1.5) - 0.02 * np.abs(ts - 0.5)
        punkt = kandidaten[int(np.argmax(score))]
        ax.text(*punkt, _text(k[3], stellen), **k[4])
        belegt.append(np.repeat(punkt[None, :], 5, axis=0))

    for name, c in P.items():
        ax.add_patch(Circle(c, radius, facecolor="white", edgecolor="black", linewidth=1.3, zorder=3))
        ax.text(*c, name, ha="center", va="center", fontsize=13, zorder=4)

    fig.tight_layout()
    return speichern(fig, pfad)


def _standardpositionen(namen: Sequence[str], abstand: float) -> dict:
    n = len(namen)
    if n == 2:
        punkte = [(0, 0), (abstand, 0)]
    elif n == 3:
        h = abstand * math.sqrt(3) / 2
        punkte = [(0, h), (abstand, h), (abstand / 2, 0)]
    elif n == 4:
        punkte = [(0, abstand), (abstand, abstand), (abstand, 0), (0, 0)]
    else:
        r = abstand / (2 * math.sin(math.pi / n))
        punkte = [(r * math.sin(2 * math.pi * i / n), r * math.cos(2 * math.pi * i / n)) for i in range(n)]
    return dict(zip(namen, punkte))


def uebergangsgraph(
    pfad,
    zustaende: Sequence[str],
    kanten: Kanten,
    *,
    positionen: Mapping[str, tuple[float, float]] | None = None,
    abstand: float = 3.2,
    **kwargs,
):
    """Übergangsgraph einer Markov-Kette. Kanten (von, nach) → Übergangswahrscheinlichkeit.

    Standardanordnung: 2 nebeneinander, 3 im Dreieck, 4 im Quadrat, sonst im Kreis.
    Weitere Parameter (radius, stellen, groesse, …) wie `pfeildiagramm`.
    """
    positionen = positionen or _standardpositionen(zustaende, abstand)
    return pfeildiagramm(pfad, positionen, kanten, **kwargs)


def verflechtungsdiagramm(
    pfad,
    stufen: Sequence[Sequence[str]],
    kanten: Kanten,
    *,
    abstand_x: float = 3.2,
    abstand_y: float = 1.6,
    **kwargs,
):
    """Verflechtungsdiagramm (z. B. Rohstoffe → Zwischenprodukte → Endprodukte), Stufen von links nach rechts.

    Kanten (von, nach) → Mengeneinheiten; mit `kanten_aus_matrix` direkt aus RZ, ZE, … erzeugbar.
    """
    positionen = {}
    for i, stufe in enumerate(stufen):
        for j, name in enumerate(stufe):
            positionen[name] = (i * abstand_x, ((len(stufe) - 1) / 2 - j) * abstand_y)
    kwargs.setdefault("radius", 0.38)
    return pfeildiagramm(pfad, positionen, kanten, **kwargs)
