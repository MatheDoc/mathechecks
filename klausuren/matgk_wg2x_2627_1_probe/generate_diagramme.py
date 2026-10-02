"""Erzeugt die Diagramme für klausur.md (nur Kurven, Achsen und Gitter, keine Lösungspunkte)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

OUT = Path(__file__).parent


def plot(name, kurven, xlim, ylim, xmajor, xminor, ymajor, yminor, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(9, 6))
    xs = np.linspace(xlim[0], xlim[1], 1200)
    for label, f, farbe, stil in kurven:
        with np.errstate(divide="ignore", invalid="ignore"):
            ys = f(xs)
        ys = np.where((ys >= ylim[0]) & (ys <= ylim[1]), ys, np.nan)
        ax.plot(xs, ys, label=label, color=farbe, linestyle=stil, linewidth=2.2)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.xaxis.set_major_locator(MultipleLocator(xmajor))
    ax.xaxis.set_minor_locator(MultipleLocator(xminor))
    ax.yaxis.set_major_locator(MultipleLocator(ymajor))
    ax.yaxis.set_minor_locator(MultipleLocator(yminor))
    ax.grid(which="major", color="#808080", linewidth=0.8)
    ax.grid(which="minor", color="#d0d0d0", linewidth=0.5)
    ax.axhline(0, color="black", linewidth=1.8)
    ax.axvline(0, color="black", linewidth=1.8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc="upper left", fontsize=11, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)


# Aufgabe 1: Polypol, p = 15, Kapazitätsgrenze 20 ME
K1 = lambda x: 0.1 * x**3 - 2.4 * x**2 + 19.5 * x + 95
plot(
    "diagramm-aufgabe1.png",
    [
        ("E(x)", lambda x: 15 * x, "tab:blue", "-"),
        ("K(x)", K1, "tab:red", "--"),
        ("G(x)", lambda x: 15 * x - K1(x), "tab:green", "-"),
    ],
    xlim=(0, 20),
    ylim=(-100, 350),
    xmajor=2,
    xminor=1,
    ymajor=50,
    yminor=10,
    xlabel="Menge $x$ in ME",
    ylabel="Betrag in GE",
)

# Aufgabe 2: Monopol, p(x) = -4x + 64
K2 = lambda x: 0.25 * x**3 - 3.75 * x**2 + 34 * x + 45
p2 = lambda x: -4 * x + 64
plot(
    "diagramm-aufgabe2.png",
    [
        ("p(x)", p2, "tab:orange", "-"),
        ("E(x)", lambda x: p2(x) * x, "tab:blue", "-"),
        ("K(x)", K2, "tab:red", "--"),
        ("G(x)", lambda x: p2(x) * x - K2(x), "tab:green", "-"),
    ],
    xlim=(0, 16),
    ylim=(-100, 300),
    xmajor=2,
    xminor=1,
    ymajor=50,
    yminor=10,
    xlabel="Menge $x$ in ME",
    ylabel="Betrag in GE bzw. GE/ME",
)

# Aufgabe 3: K(x) = 0,5x^3 - 6x^2 + 28x + 128
plot(
    "diagramm-aufgabe3.png",
    [
        ("$K'(x)$", lambda x: 1.5 * x**2 - 12 * x + 28, "tab:purple", "-"),
        ("$k(x)$", lambda x: 0.5 * x**2 - 6 * x + 28 + 128 / x, "tab:red", "-"),
        ("$k_v(x)$", lambda x: 0.5 * x**2 - 6 * x + 28, "tab:blue", "--"),
    ],
    xlim=(0, 12),
    ylim=(0, 60),
    xmajor=2,
    xminor=1,
    ymajor=10,
    yminor=2,
    xlabel="Menge $x$ in ME",
    ylabel="Betrag in GE bzw. GE/ME",
)
