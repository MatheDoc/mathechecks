"""Generates the three exam diagrams (static PNGs) for klausur matgk_wg2x_2627_1.
Curves only, no answer points marked - students read values off the grid themselves.
"""
import numpy as np
import matplotlib.pyplot as plt

OUT_DIR = r"c:\Users\fue\Meine Ablage\mathechecks\klausuren\matgk_wg2x_2627_1"


def style_axes(ax, xlabel, ylabel, xmin, xmax, ymin, ymax, xstep, ystep):
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticks(np.arange(xmin, xmax + 0.001, xstep))
    ax.set_yticks(np.arange(ymin, ymax + 0.001, ystep))
    ax.grid(True, which="major", linestyle="-", linewidth=0.5, alpha=0.6)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc="best", fontsize=9)


# ---------------------------------------------------------------
# Aufgabe 2: GOF Polypol - E, K, G, p
# ---------------------------------------------------------------
x = np.linspace(0, 22, 400)
E = 30 * x
K = 0.2 * x**3 - 4 * x**2 + 25 * x + 100
G = -0.2 * x**3 + 4 * x**2 + 5 * x - 100
p = np.full_like(x, 30)

fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(x, E, label="E(x)")
ax.plot(x, K, label="K(x)")
ax.plot(x, G, label="G(x)")
ax.plot(x, p, label="p(x)", linestyle="--")
style_axes(ax, "Menge x in ME", "Betrag y in GE", 0, 22, -120, 700, 2, 100)
ax.set_title("Ökonomische Funktionen (Angebotspolypol)")
fig.tight_layout()
fig.savefig(f"{OUT_DIR}\\diagramm-aufgabe2.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# Aufgabe 4: GOF Monopol - E, K, G, p
# ---------------------------------------------------------------
x = np.linspace(0, 10, 400)
E = -5 * x**2 + 50 * x
K = 0.5 * x**3 - 4.5 * x**2 + 20 * x + 40
G = -0.5 * x**3 - 0.5 * x**2 + 30 * x - 40
p = -5 * x + 50

fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(x, E, label="E(x)")
ax.plot(x, K, label="K(x)")
ax.plot(x, G, label="G(x)")
ax.plot(x, p, label="p(x)", linestyle="--")
style_axes(ax, "Menge x in ME", "Betrag y in GE", 0, 10, -60, 300, 1, 25)
ax.set_title("Ökonomische Funktionen (Angebotsmonopol)")
fig.tight_layout()
fig.savefig(f"{OUT_DIR}\\diagramm-aufgabe4.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# Aufgabe 7: EK graphisch - K', k, k_v
# ---------------------------------------------------------------
x = np.linspace(0.8, 10, 400)
Kp = 1.5 * x**2 - 12 * x + 28
kv = 0.5 * x**2 - 6 * x + 28
k = kv + 40 / x

fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(x, Kp, label="K'(x)")
ax.plot(x, k, label="k(x)")
ax.plot(x, kv, label="k_v(x)")
style_axes(ax, "Menge x in ME", "Betrag y in GE", 0, 10, 0, 70, 1, 5)
ax.set_title("Kostenfunktionen (ertragsgesetzlicher Kostenverlauf)")
fig.tight_layout()
fig.savefig(f"{OUT_DIR}\\diagramm-aufgabe7.png", dpi=150)
plt.close(fig)

print("done")
