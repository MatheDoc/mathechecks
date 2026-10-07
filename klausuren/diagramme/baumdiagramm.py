"""Baumdiagramme (beliebig viele Stufen und Äste)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import matplotlib.pyplot as plt

from ._stil import druckstil, mathe_name, speichern, zahl

LUECKE = None  # Platzhalter für Wahrscheinlichkeiten/Ereignisse, die die Schüler eintragen sollen


def quer(name: str) -> str:
    """Gegenereignis als Mathtext, z. B. quer("A") → $\\overline{A}$."""
    return rf"$\overline{{{name}}}$"


def _fmt(name: str) -> str:
    return name if name.startswith("$") or len(name) > 1 else f"${name}$"


@dataclass
class _Knoten:
    name: str | None
    p: float | str | None
    kinder: list["_Knoten"] = field(default_factory=list)
    x: float = 0.0
    tiefe: int = 0


def _baue(aeste, tiefe: int) -> list[_Knoten]:
    knoten = []
    for ast in aeste:
        name, p, *rest = ast
        kinder = _baue(rest[0], tiefe + 1) if rest and rest[0] else []
        knoten.append(_Knoten(name, p, kinder, tiefe=tiefe))
    return knoten


def _layout(knoten: list[_Knoten], zaehler: list[int]) -> None:
    for k in knoten:
        if k.kinder:
            _layout(k.kinder, zaehler)
            k.x = sum(c.x for c in k.kinder) / len(k.kinder)
        else:
            k.x = zaehler[0]
            zaehler[0] += 1


def _tiefe(knoten: list[_Knoten]) -> int:
    return max((1 + _tiefe(k.kinder) for k in knoten), default=0)


def baum_zweistufig(p_a: float | None, p_b_a: float | None, p_b_na: float | None, a: str = "A", b: str = "B"):
    """Äste für den Standardbaum A/Ā → B/B̄. Gegenwahrscheinlichkeiten werden ergänzt (None → Lücke)."""

    def gegen(p):
        return None if p is None or isinstance(p, str) else 1 - p

    return [
        (a, p_a, [(b, p_b_a), (quer(b), gegen(p_b_a))]),
        (quer(a), gegen(p_a), [(b, p_b_na), (quer(b), gegen(p_b_na))]),
    ]


def baum_bernoulli(n: int, p: float | str, treffer: str = "T", niete: str = "N"):
    """Äste einer Bernoulli-Kette der Länge n (Trefferwahrscheinlichkeit p)."""
    q = 1 - p if isinstance(p, (int, float)) else (f"$1-{mathe_name(p)}$" if p else None)
    if n == 0:
        return []
    unten = baum_bernoulli(n - 1, p, treffer, niete)
    return [(treffer, p, unten), (niete, q, unten)]


@druckstil
def baumdiagramm(
    pfad,
    aeste: Sequence,
    *,
    richtung: str = "unten",
    pfadwahrscheinlichkeiten: bool = False,
    stellen: int = 4,
    wurzel: str = "",
    groesse: tuple[float, float] | None = None,
):
    """Zeichnet ein Baumdiagramm.

    aeste: Liste von (Ereignis, Wahrscheinlichkeit[, Unteräste]). Wahrscheinlichkeit als Zahl
           (→ Dezimalkomma, `stellen` Nachkommastellen) oder Mathtext-String; `None` → leeres Kästchen.
    richtung: "unten" (Wurzel oben) oder "rechts" (Wurzel links, besser bei vielen Blättern).
    pfadwahrscheinlichkeiten: Pfadwahrscheinlichkeit an jedes Blatt (nur wenn alle Äste numerisch).
    """
    wurzel_knoten = _Knoten(wurzel or "", 1.0, _baue(aeste, 1), tiefe=0)
    _layout(wurzel_knoten.kinder, [0])
    wurzel_knoten.x = sum(c.x for c in wurzel_knoten.kinder) / len(wurzel_knoten.kinder)
    blaetter = _blaetter(wurzel_knoten)
    stufen = _tiefe(wurzel_knoten.kinder)

    vertikal = richtung == "unten"
    blattabstand, stufenabstand = (1.35, 1.7) if vertikal else (0.85, 2.6)

    def pos(k: _Knoten):
        if vertikal:
            return k.x * blattabstand, -k.tiefe * stufenabstand
        return k.tiefe * stufenabstand, -k.x * blattabstand

    if groesse is None:
        breite_einh = (len(blaetter) - 1) * blattabstand
        tiefe_einh = stufen * stufenabstand
        if vertikal:
            groesse = (max(4.5, 0.95 * breite_einh + 2), 0.95 * tiefe_einh + (2.0 if pfadwahrscheinlichkeiten else 1.0))
        else:
            groesse = (0.95 * tiefe_einh + (3.2 if pfadwahrscheinlichkeiten else 1.5), max(3, 0.95 * breite_einh + 1))
    fig, ax = plt.subplots(figsize=groesse)
    ax.axis("off")

    kasten = {"boxstyle": "square,pad=0.35", "facecolor": "white", "edgecolor": "black", "linewidth": 0.9}

    def zeichne(k: _Knoten, pfad_namen: list[str], pfad_p: float | None):
        x0, y0 = pos(k)
        for c in k.kinder:
            x1, y1 = pos(c)
            ax.plot([x0, x1], [y0, y1], color="black", linewidth=1.2, zorder=1)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            # Normale zum Ast, nach außen (vom Geschwisterast weg) gerichtet
            nx, ny = -(y1 - y0), (x1 - x0)
            laenge = (nx**2 + ny**2) ** 0.5
            nx, ny = nx / laenge, ny / laenge
            aussen = (x1 - x0) if vertikal else (y1 - y0)
            if (nx if vertikal else ny) * (aussen if abs(aussen) > 1e-9 else 1) < 0:
                nx, ny = -nx, -ny
            versatz = (9 * nx, 9 * ny)
            ausricht = {
                "ha": "left" if nx > 0.3 else "right" if nx < -0.3 else "center",
                "va": "bottom" if ny > 0.3 else "top" if ny < -0.3 else "center",
            }
            if c.p is None:
                ax.annotate("\u2003\u2003", (mx, my), xytext=versatz, textcoords="offset points",
                            bbox=kasten, fontsize=11, zorder=3, **ausricht)
            else:
                text = zahl(c.p, stellen) if isinstance(c.p, (int, float)) else c.p
                ax.annotate(text, (mx, my), xytext=versatz, textcoords="offset points", fontsize=13, zorder=3,
                            **ausricht)
            neu_p = pfad_p * c.p if (pfad_p is not None and isinstance(c.p, (int, float))) else None
            zeichne(c, pfad_namen + [c.name or "?"], neu_p)

        if k.tiefe > 0 or k.name:
            text = "\u2003" if k.name is None else _fmt(k.name)
            ax.text(x0, y0, text, ha="center", va="center", fontsize=14, bbox=kasten, zorder=4)

        if not k.kinder and pfadwahrscheinlichkeiten:
            ereignis = r"$P(" + r"\cap ".join(mathe_name(_fmt(n)) for n in pfad_namen) + ")$"
            wert = zahl(pfad_p, stellen) if pfad_p is not None else ""
            if vertikal:
                ax.text(x0, y0 - 0.65, ereignis, ha="center", va="top", fontsize=12)
                ax.text(x0, y0 - 1.05, wert, ha="center", va="top", fontsize=12)
            else:
                text = f"{ereignis} = {wert}" if wert else ereignis
                ax.text(x0 + 0.45, y0, text, ha="left", va="center", fontsize=12)

    zeichne(wurzel_knoten, [], 1.0)

    xs, ys = zip(*(pos(k) for k in _alle(wurzel_knoten)))
    rand = 0.6
    if vertikal:
        ax.set_xlim(min(xs) - rand, max(xs) + rand)
        ax.set_ylim(min(ys) - (1.4 if pfadwahrscheinlichkeiten else rand), max(ys) + 0.3)
    else:
        ax.set_xlim(min(xs) - 0.3, max(xs) + (3.0 if pfadwahrscheinlichkeiten else rand))
        ax.set_ylim(min(ys) - rand, max(ys) + rand)
    fig.tight_layout()
    return speichern(fig, pfad)


def _alle(k: _Knoten):
    yield k
    for c in k.kinder:
        yield from _alle(c)


def _blaetter(k: _Knoten):
    return [n for n in _alle(k) if not n.kinder]
