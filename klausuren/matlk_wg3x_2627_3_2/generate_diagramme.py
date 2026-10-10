import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diagramme import *  # noqa: F403

OUT = Path(__file__).parent

# Aufgabe 3: kumulierte Verteilung der Anzahl fehlerhafter Akkus je Sendung
histogramm_binomial(
    OUT / "diagramm-aufgabe3.png", 80, 0.04, kumuliert=True, kmin=0, kmax=12,
    ymax=1, yhaupt=0.1, yneben=0.02, groesse=(8, 5),
)

# Aufgabe 4: Übergangsgraph (Schleifen bewusst nicht eingezeichnet)
uebergangsgraph(
    OUT / "diagramm-aufgabe4-graph.png",
    ["V", "R", "N"],
    {
        ("V", "R"): 0.10, ("V", "N"): 0.10,
        ("R", "V"): 0.20, ("R", "N"): 0.10,
        ("N", "V"): 0.10, ("N", "R"): 0.30,
    },
)

# Aufgabe 4: Verflechtung Bauteile -> Endprodukte
verflechtungsdiagramm(
    OUT / "diagramm-aufgabe4-verflechtung.png",
    [["Z1", "Z2", "Z3"], ["E1", "E2", "E3"]],
    kanten_aus_matrix(["Z1", "Z2", "Z3"], ["E1", "E2", "E3"], [[1, 1, 2], [2, 1, 1], [1, 2, 1]]),
)

# Aufgabe 4: leeres Koordinatensystem für das grafische Verfahren
funktionsgraph(
    OUT / "diagramm-aufgabe4-koordinatensystem.png", [],
    xlim=(0, 32), ylim=(0, 32), xhaupt=4, xneben=1, yhaupt=4, yneben=1,
    xachse="Lastenräder $x$ in ME", yachse="E-Bikes $y$ in ME", groesse=(8, 7),
)
