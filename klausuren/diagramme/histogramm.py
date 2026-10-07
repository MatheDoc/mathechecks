"""Histogramme, insbesondere der Binomialverteilung (einzeln und kumuliert)."""

from __future__ import annotations

from math import comb
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np

from ._stil import FLAECHE_DUNKEL, FLAECHE_HELL, achsenteilung, druckstil, gitter, schoene_schritte, speichern


def binomial_werte(n: int, p: float, kumuliert: bool = False) -> np.ndarray:
    pmf = np.array([comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(n + 1)])
    return np.cumsum(pmf) if kumuliert else pmf


def _hervorgehoben(ks: np.ndarray, hervorheben) -> np.ndarray:
    if hervorheben is None:
        return np.zeros(len(ks), dtype=bool)
    if isinstance(hervorheben, tuple) and len(hervorheben) == 2:
        a, b = hervorheben
        return (ks >= a) & (ks <= b)
    return np.isin(ks, list(hervorheben))


@druckstil
def histogramm(
    pfad,
    ks: Sequence[int],
    werte: Sequence[float],
    *,
    xachse: str = "$k$",
    yachse: str = "",
    ymax: float | None = None,
    yhaupt: float | None = None,
    yneben: float | None = None,
    xhaupt: int | None = None,
    hervorheben: tuple[int, int] | Iterable[int] | None = None,
    groesse: tuple[float, float] = (9, 5.5),
):
    """Allgemeines Histogramm (Balkenbreite 1, Balken grau mit schwarzem Rand).

    hervorheben: (a, b) für a ≤ k ≤ b oder Menge einzelner k – diese Balken dunkler.
    """
    ks = np.asarray(ks)
    werte = np.asarray(werte, dtype=float)
    fig, ax = plt.subplots(figsize=groesse)

    farben = np.where(_hervorgehoben(ks, hervorheben), FLAECHE_DUNKEL, FLAECHE_HELL)
    ax.bar(ks, werte, width=1.0, color=farben, edgecolor="black", linewidth=0.9, zorder=3)

    if yhaupt is None:
        yhaupt, auto_neben = schoene_schritte(werte.max() * 1.08, 8)
        yneben = auto_neben if yneben is None else yneben
    if ymax is None:
        ymax = np.ceil(werte.max() * 1.04 / yhaupt) * yhaupt
    ax.set_ylim(0, ymax)
    ax.set_xlim(ks.min() - 0.7, ks.max() + 0.7)
    achsenteilung(ax.yaxis, 0, ymax, yhaupt, yneben)

    if xhaupt is None:
        spanne = ks.max() - ks.min()
        xhaupt = 1 if spanne <= 25 else 2 if spanne <= 50 else 5
    ax.set_xticks([k for k in ks if k % xhaupt == 0])
    ax.set_xticks(ks, minor=True)
    ax.tick_params(axis="x", which="minor", length=3)

    gitter(ax, achse="y")
    ax.set_xlabel(xachse)
    ax.set_ylabel(yachse)
    fig.tight_layout()
    return speichern(fig, pfad)


def histogramm_binomial(
    pfad,
    n: int,
    p: float,
    *,
    kumuliert: bool = False,
    kmin: int | None = None,
    kmax: int | None = None,
    yachse: str | None = None,
    **kwargs,
):
    """Histogramm der Binomialverteilung B(n; p), Einzelwahrscheinlichkeiten oder kumuliert.

    kmin/kmax: dargestellter Bereich; Standard bei n ≤ 30: 0…n, sonst der Bereich mit
    nicht vernachlässigbarer Wahrscheinlichkeit (> 0,0005).
    Weitere Parameter (ymax, yhaupt, yneben, xhaupt, hervorheben, groesse) wie `histogramm`.
    """
    pmf = binomial_werte(n, p)
    werte = np.cumsum(pmf) if kumuliert else pmf
    if kmin is None or kmax is None:
        if n <= 30:
            lo, hi = 0, n
        else:
            relevant = np.flatnonzero(pmf > 0.0005)
            lo, hi = int(relevant.min()), int(relevant.max())
            if kumuliert:
                hi = int(np.flatnonzero(np.cumsum(pmf) > 0.9995).min())
        kmin = lo if kmin is None else kmin
        kmax = hi if kmax is None else kmax
    ks = np.arange(kmin, kmax + 1)
    if yachse is None:
        yachse = r"$P(X\leq k)$" if kumuliert else r"$P(X=k)$"
    if kumuliert:
        kwargs.setdefault("ymax", 1.05)
        kwargs.setdefault("yhaupt", 0.1)
        kwargs.setdefault("yneben", 0.05)
    return histogramm(pfad, ks, werte[ks], yachse=yachse, **kwargs)
