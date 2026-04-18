"""Gemeinsame Hilfsfunktionen für Quadratische-Funktionen-Generatoren."""

from __future__ import annotations

import math
import random

from aufgaben.core.latex import (
    coeff_latex,
    const_latex,
    fmt,
    display_eq,
    inline,
    signed_number,
)
from aufgaben.core.tolerances import nice_axis_max

# Rückwärtskompatible Aliase (intern verwendet)
_coeff = coeff_latex
_const = const_latex
_signed = signed_number


def nf_latex(a: float, b: float, c: float, name: str = "f", var: str = "x") -> str:
    """Normalform f(x) = ax² + bx + c."""
    a_str = _coeff(a, f"{var}^2", leading=True)
    b_str = _coeff(b, var)
    c_str = _const(c)
    return f"{name}({var})={a_str}{b_str}{c_str}"


def spf_latex(a: float, d: float, e: float, name: str = "f") -> str:
    """Scheitelpunktform f(x) = a(x-d)² + e."""
    a_str = fmt(a) if a != 1 else ""
    if a == -1:
        a_str = "-"
    # (x - d)²
    if d == 0:
        core = "x^2"
    elif d > 0:
        core = f"(x-{fmt(d)})^2"
    else:
        core = f"(x+{fmt(abs(d))})^2"
    e_str = _const(e)
    return f"{name}(x)={a_str}{core}{e_str}"


def ff_latex(a: float, x1: float, x2: float, name: str = "f") -> str:
    """Faktorisierte Form f(x) = a(x-x1)(x-x2)."""
    a_str = fmt(a) if a != 1 else ""
    if a == -1:
        a_str = "-"

    def _factor(xn: float) -> str:
        if xn == 0:
            return "x"
        if xn > 0:
            return f"(x-{fmt(xn)})"
        return f"(x+{fmt(abs(xn))})"

    return f"{name}(x)={a_str}{_factor(x1)}{_factor(x2)}"


# ---------------------------------------------------------------------------
# Umrechnungen
# ---------------------------------------------------------------------------

def nf_to_spf(a: float, b: float, c: float) -> tuple[float, float, float]:
    """NF → SPF: (a, d, e)."""
    d = -b / (2 * a)
    e = c - b**2 / (4 * a)
    return a, d, e


def nf_to_ff(a: float, b: float, c: float) -> tuple[float, float, float] | None:
    """NF → FF: (a, x1, x2) oder None wenn D < 0."""
    D = b**2 - 4 * a * c
    if D < 0:
        return None
    sq = math.sqrt(D)
    x1 = (-b - sq) / (2 * a)
    x2 = (-b + sq) / (2 * a)
    return a, x1, x2


def spf_to_nf(a: float, d: float, e: float) -> tuple[float, float, float]:
    """SPF → NF: (a, b, c)."""
    b = -2 * a * d
    c = a * d**2 + e
    return a, b, c


def ff_to_nf(a: float, x1: float, x2: float) -> tuple[float, float, float]:
    """FF → NF: (a, b, c)."""
    b = -a * (x1 + x2)
    c = a * x1 * x2
    return a, b, c


# ---------------------------------------------------------------------------
# Zufallsparameter
# ---------------------------------------------------------------------------

A_VALUES = [-2, -1, -0.5, 0.5, 1, 2]
A_VALUES_INT = [-2, -1, 1, 2]


def sample_nf_nice(rng: random.Random) -> tuple[float, float, float, float, float]:
    """NF mit ganzzahligen Nullstellen. Gibt (a, b, c, x1, x2) zurück."""
    while True:
        a = rng.choice(A_VALUES_INT)
        x1 = rng.randint(-5, 5)
        x2 = rng.randint(-5, 5)
        if x1 == x2:
            continue
        b = -a * (x1 + x2)
        c = a * x1 * x2
        if abs(b) > 20 or abs(c) > 30:
            continue
        return float(a), float(b), float(c), float(min(x1, x2)), float(max(x1, x2))


def sample_spf(rng: random.Random) -> tuple[float, float, float]:
    """SPF mit einfachen Werten: (a, d, e)."""
    a = rng.choice(A_VALUES)
    d = rng.randint(-4, 4)
    e = rng.randint(-6, 6)
    return a, float(d), float(e)


def sample_spf_nice_ns(rng: random.Random) -> tuple[float, float, float] | None:
    """SPF mit ganzzahligen Nullstellen. Gibt (a, d, e) zurück oder None."""
    a = rng.choice(A_VALUES)
    d = rng.randint(-4, 4)
    # e muss so sein, dass -e/a >= 0 und sqrt(-e/a) ganzzahlig
    k = rng.randint(0, 5)
    e = -a * k**2
    if e == 0 and k == 0:
        # Doppelte Nullstelle – erlaubt
        pass
    if abs(e) > 30:
        return None
    return a, float(d), float(e)


# ---------------------------------------------------------------------------
# Visual-Builder
# ---------------------------------------------------------------------------

def build_quadratic_visual(
    a: float, b: float, c: float,
    *,
    name: str = "f",
    x_range: tuple[float, float] | None = None,
    color: str = "#1f77b4",
    title: str = "",
    extra_traces: list[dict] | None = None,
) -> dict:
    """Plotly-basiertes Visual für eine quadratische Funktion."""
    d = -b / (2 * a)
    if x_range is None:
        span = max(6, abs(d) + 5)
        x_min = d - span
        x_max = d + span
    else:
        x_min, x_max = x_range

    n_pts = 201
    xs = [x_min + i * (x_max - x_min) / (n_pts - 1) for i in range(n_pts)]
    ys = [a * x**2 + b * x + c for x in xs]

    traces = [
        {
            "x": [round(x, 4) for x in xs],
            "y": [round(y, 4) for y in ys],
            "mode": "lines",
            "name": f"{name}(x)",
            "line": {"color": color, "width": 2.5},
        }
    ]
    if extra_traces:
        traces.extend(extra_traces)

    y_abs = [abs(y) for y in ys]
    axis_y = nice_axis_max(max(y_abs) * 1.1) if y_abs else 10
    axis_x = nice_axis_max(max(abs(x_min), abs(x_max)))

    return {
        "type": "plot",
        "spec": {
            "type": "plotly",
            "traces": traces,
            "layout": {
                "title": title,
                "xaxis": {"range": [-axis_x, axis_x], "dtick": 1},
                "yaxis": {"range": [-axis_y, axis_y], "dtick": 1 if axis_y <= 10 else 2},
            },
        },
    }
