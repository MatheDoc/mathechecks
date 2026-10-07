import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diagramme import *  # noqa: F403

OUT = Path(__file__).parent

# Aufgabe 4: Verflechtung Zwischenprodukte -> Endprodukte
verflechtungsdiagramm(
    OUT / "diagramm-aufgabe4.png",
    [["Z1", "Z2"], ["E1", "E2"]],
    kanten_aus_matrix(["Z1", "Z2"], ["E1", "E2"], [[2, 1], [1, 3]]),
)

# Aufgabe 8: Planungsbereich (x: Soundbars, y: Subwoofer)
lineare_optimierung(
    OUT / "diagramm-aufgabe8.png",
    [
        Restriktion(1, 1, 10, name="$g_1$"),
        Restriktion(1, 3, 18, name="$g_2$"),
        Restriktion(1, 0, 8, name="$g_3$"),
    ],
    xlim=(0, 12), ylim=(0, 12), xhaupt=2, xneben=1, yhaupt=2, yneben=1,
    xachse="Soundbars $x$ in ME", yachse="Subwoofer $y$ in ME",
    zulaessig_markieren=True, groesse=(7, 6),
)

# Aufgabe 10: Histogramm der Anzahl undichter Kopfhörer, E3 hervorgehoben
histogramm_binomial(
    OUT / "diagramm-aufgabe10.png", 50, 0.08, kmin=0, kmax=12, hervorheben=(3, 5),
    ymax=0.25, yhaupt=0.05, yneben=0.01, groesse=(8, 4.5),
)

# Aufgabe 11: Übergangsgraph (Schleifen bewusst nicht eingezeichnet)
uebergangsgraph(
    OUT / "diagramm-aufgabe11-graph.png",
    ["K", "R", "S"],
    {
        ("K", "R"): 0.10, ("K", "S"): 0.10,
        ("R", "K"): 0.20, ("R", "S"): 0.15,
        ("S", "K"): 0.10, ("S", "R"): 0.20,
    },
)

# Aufgabe 11: leeres Koordinatensystem für das grafische Verfahren
funktionsgraph(
    OUT / "diagramm-aufgabe11-koordinatensystem.png", [],
    xlim=(0, 40), ylim=(0, 64), xhaupt=5, xneben=1, yhaupt=10, yneben=2,
    xachse="Kopfhörer $x$ in ME", yachse="Lautsprecher $y$ in ME", groesse=(8, 6.5),
)
