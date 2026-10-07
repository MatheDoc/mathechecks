"""Erzeugt Beispielbilder aller Diagrammtypen (Smoke-Test + Vorlage).

Aufruf: python klausuren/diagramme/galerie.py [Zielordner]   (Standard: klausuren/diagramme/_galerie)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diagramme import (  # noqa: E402
    LUECKE,
    Flaeche,
    Hilfslinie,
    Kurve,
    Punkt,
    Restriktion,
    Zielgerade,
    baum_bernoulli,
    baum_zweistufig,
    baumdiagramm,
    funktionsgraph,
    histogramm_binomial,
    kanten_aus_matrix,
    lineare_optimierung,
    quer,
    uebergangsgraph,
    verflechtungsdiagramm,
)

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "_galerie"

# --- Funktionsgraphen -------------------------------------------------------
K = "0.25*x^3 - 3.75*x^2 + 34*x + 45"
funktionsgraph(
    OUT / "graph-mehrere.png",
    [
        Kurve("-4*x + 64", "$p$"),
        Kurve("(-4*x + 64)*x", "$E$"),
        Kurve(K, "$K$"),
        Kurve(f"(-4*x + 64)*x - ({K})", "$G$"),
    ],
    xlim=(0, 16), ylim=(-100, 300), xhaupt=2, xneben=1, yhaupt=50, yneben=10,
    xachse="Menge $x$ in ME", yachse="Betrag in GE bzw. GE/ME",
)

funktionsgraph(
    OUT / "graph-stueckkosten.png",
    [
        Kurve(lambda x: 1.5 * x**2 - 12 * x + 28, "$K'$"),
        Kurve(lambda x: 0.5 * x**2 - 6 * x + 28 + 128 / x, "$k$"),
        Kurve(lambda x: 0.5 * x**2 - 6 * x + 28, "$k_v$"),
    ],
    xlim=(0, 12), ylim=(0, 60), xhaupt=2, xneben=1, yhaupt=10, yneben=2,
    xachse="Menge $x$ in ME", yachse="Betrag in GE/ME",
)

pN = "13.7*exp(-0.1*x)"
funktionsgraph(
    OUT / "graph-renten.png",
    [Kurve(pN, "$p_N$"), Kurve("0.6*exp(0.155*x)", "$p_A$")],
    xlim=(0, 14.5), ylim=(0, 15), xhaupt=2, xneben=1, yhaupt=2, yneben=1,
    xachse="$x$ in ME", yachse="$y$ in GE/ME",
    flaechen=[
        Flaeche(pN, 6.8, von=0, bis=7, schraffur=True),
        Flaeche(6.8, 4, von=0, bis=7, name="$R$", grau="0.9"),
    ],
    hilfslinien=[Hilfslinie(y=6.8, von=0, bis=7), Hilfslinie(x=7, von=4, bis=6.8), Hilfslinie(y=4, von=0, bis=12.2)],
    punkte=[Punkt(7, 13.7 * 2.718281828 ** (-0.7), "$P$")],
)

funktionsgraph(
    OUT / "graph-skizze.png",
    [Kurve("-0.5*x^3 + 4*x^2 - 4*x - 6", "$G$")],
    xlim=(0, 7.5), ylim=(-10, 8), skizze=True, xachse="$x$ in ME", yachse="$G(x)$ in GE", groesse=(5, 4),
)

funktionsgraph(
    OUT / "koordinatensystem-leer.png", [], xlim=(0, 10), ylim=(0, 100), xachse="$x$ in ME", yachse="$y$ in GE",
    groesse=(8, 5),
)

# --- Histogramme ------------------------------------------------------------
histogramm_binomial(OUT / "histogramm-einzeln.png", 12, 0.42, hervorheben=(3, 6))
histogramm_binomial(OUT / "histogramm-kumuliert.png", 10, 0.6, kumuliert=True, groesse=(8, 5.5))
histogramm_binomial(OUT / "histogramm-gross.png", 100, 0.45, groesse=(10, 5))

# --- Baumdiagramme ----------------------------------------------------------
baumdiagramm(OUT / "baum-zweistufig.png", baum_zweistufig(0.04, 0.05, 0.0552, a="H", b="Z"),
             pfadwahrscheinlichkeiten=True, stellen=4)
baumdiagramm(OUT / "baum-luecken.png", [
    ("A", 0.3, [("B", LUECKE), (quer("B"), 0.8)]),
    (quer("A"), LUECKE, [("B", 0.6), (quer("B"), LUECKE)]),
])
baumdiagramm(OUT / "baum-bernoulli.png", baum_bernoulli(3, 0.2), richtung="rechts", pfadwahrscheinlichkeiten=True)

# --- Lineare Optimierung ----------------------------------------------------
# Optimum von G = 20x + 25y im Eckpunkt (160 | 120) mit G = 6200
restriktionen = [
    Restriktion(1, 2, 400, name="(I)"),
    Restriktion(3, 2, 720, name="(II)"),
    Restriktion(1, 0, 200, name="(III)"),
]
lo_achsen = dict(xlim=(0, 420), ylim=(0, 380), xhaupt=50, xneben=10, yhaupt=50, yneben=10,
                 xachse="$A$ in Stück", yachse="$B$ in Stück")
lineare_optimierung(OUT / "lo-aufgabe.png", restriktionen, **lo_achsen)
lineare_optimierung(OUT / "lo-loesung.png", restriktionen, **lo_achsen, zulaessig_markieren=True,
                    zielgeraden=[Zielgerade(20, 25, 6200, "$G$")], punkte=[Punkt(160, 120, "$P_{opt}$")])

# --- Pfeildiagramme ---------------------------------------------------------
uebergangsgraph(OUT / "uebergangsgraph.png", ["JR", "NA", "BS"], {
    ("JR", "JR"): 0.8, ("JR", "NA"): 0.15, ("JR", "BS"): 0.05,
    ("NA", "JR"): 0.1, ("NA", "NA"): 0.75, ("NA", "BS"): 0.15,
    ("BS", "JR"): 0.1, ("BS", "NA"): 0.1, ("BS", "BS"): 0.8,
})
verflechtungsdiagramm(
    OUT / "verflechtung.png",
    [["R1", "R2", "R3"], ["Z1", "Z2"], ["E1", "E2"]],
    {
        **kanten_aus_matrix(["R1", "R2", "R3"], ["Z1", "Z2"], [[2, 1], [0, 3], [4, LUECKE]]),
        **kanten_aus_matrix(["Z1", "Z2"], ["E1", "E2"], [[1, 2], [3, 1]]),
    },
)

print(f"Galerie erzeugt: {OUT}")
