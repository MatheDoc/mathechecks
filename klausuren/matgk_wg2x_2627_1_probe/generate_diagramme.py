"""Erzeugt die Diagramme für klausur.md (nur Kurven, Achsen und Gitter, keine Lösungspunkte)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diagramme import Kurve, funktionsgraph  # noqa: E402

OUT = Path(__file__).parent
ACHSEN = dict(xachse="Menge $x$ in ME", xhaupt=2, xneben=1)

# Aufgabe 1: Polypol, p = 15, Kapazitätsgrenze 20 ME
K1 = lambda x: 0.1 * x**3 - 2.4 * x**2 + 19.5 * x + 95
funktionsgraph(
    OUT / "diagramm-aufgabe1.png",
    [
        Kurve(lambda x: 15 * x, "$E$"),
        Kurve(K1, "$K$"),
        Kurve(lambda x: 15 * x - K1(x), "$G$"),
    ],
    xlim=(0, 20), ylim=(-100, 350), yhaupt=50, yneben=10, yachse="Betrag in GE", **ACHSEN,
)

# Aufgabe 2: Monopol, p(x) = -4x + 64
K2 = lambda x: 0.25 * x**3 - 3.75 * x**2 + 34 * x + 45
p2 = lambda x: -4 * x + 64
funktionsgraph(
    OUT / "diagramm-aufgabe2.png",
    [
        Kurve(p2, "$p$"),
        Kurve(lambda x: p2(x) * x, "$E$"),
        Kurve(K2, "$K$"),
        Kurve(lambda x: p2(x) * x - K2(x), "$G$"),
    ],
    xlim=(0, 16), ylim=(-100, 300), yhaupt=50, yneben=10, yachse="Betrag in GE bzw. GE/ME", **ACHSEN,
)

# Aufgabe 3: K(x) = 0,5x^3 - 6x^2 + 28x + 128
funktionsgraph(
    OUT / "diagramm-aufgabe3.png",
    [
        Kurve(lambda x: 1.5 * x**2 - 12 * x + 28, "$K'$"),
        Kurve(lambda x: 0.5 * x**2 - 6 * x + 28 + 128 / x, "$k$"),
        Kurve(lambda x: 0.5 * x**2 - 6 * x + 28, "$k_v$"),
    ],
    xlim=(0, 12), ylim=(0, 60), yhaupt=10, yneben=2, yachse="Betrag in GE/ME", **ACHSEN,
)
