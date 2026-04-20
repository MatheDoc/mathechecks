"""Gemeinsame Hilfsfunktionen für Lineare-Funktionen-Generatoren."""

from __future__ import annotations

import math
import random

from aufgaben.core.latex import coeff_latex, const_latex, fmt, display_eq, inline
from aufgaben.core.tolerances import nice_axis_max, graph_read_tolerance_from_span

# Rückwärtskompatibel: einige Module importieren ``fmt_number``
fmt_number = fmt


# ---------------------------------------------------------------------------
# LaTeX-Formatierung
# ---------------------------------------------------------------------------

def linear_latex(m: float, b: float, var: str = "x", name: str = "f") -> str:
    """Erzeugt z. B. ``f(x)=2x+3`` oder ``g(x)=-0,5x-1``."""
    m_str = coeff_latex(m, var, leading=True)
    b_str = const_latex(b)
    return f"{name}({var})={m_str}{b_str}"


def fmt_int_or_frac(value: float) -> str:
    """Gibt eine Zahl als Ganzzahl oder als Bruch zurück (wenn halbe/drittel etc.)."""
    if value == int(value):
        return str(int(value))
    return fmt(value, 2)


# ---------------------------------------------------------------------------
# Zufallsparameter
# ---------------------------------------------------------------------------

# Steigungen: ganzzahlig oder halbe Werte, kein 0, gemäßigt für [-8,8]-Bereich
SLOPES = [v / 2 for v in range(-8, 9) if v != 0]
# y-Achsenabschnitte: ganzzahlig
INTERCEPTS = list(range(-6, 7))


def sample_linear(rng: random.Random) -> tuple[float, float]:
    """Zufällige Steigung und y-Achsenabschnitt.

    Stellt sicher, dass Nullstelle und y-Abschnitt im Bereich [-8, 8] liegen.
    """
    while True:
        m = rng.choice(SLOPES)
        b = rng.choice(INTERCEPTS)
        # Nullstelle x0 = -b/m muss im Sichtbereich liegen
        x0 = -b / m
        if abs(x0) > 8:
            continue
        return m, b


def sample_linear_nice_null(rng: random.Random) -> tuple[float, float]:
    """Lineare Funktion mit ganzzahliger Nullstelle (≠ 0)."""
    while True:
        m = rng.choice(SLOPES)
        # Nullstelle x0 = -b/m soll ganzzahlig sein
        x0 = rng.choice([v for v in range(-10, 11) if v != 0])
        b = -m * x0
        if b == int(b) and abs(b) <= 15:
            return m, float(int(b))


def sample_two_linear_intersecting(
    rng: random.Random,
) -> tuple[float, float, float, float]:
    """Zwei lineare Funktionen mit ganzzahligem Schnittpunkt."""
    while True:
        m1 = rng.choice(SLOPES)
        m2 = rng.choice(SLOPES)
        if m1 == m2:
            continue
        x_s = rng.randint(-8, 8)
        y_s = rng.randint(-8, 8)
        b1 = y_s - m1 * x_s
        b2 = y_s - m2 * x_s
        if b1 != int(b1) or b2 != int(b2):
            continue
        if abs(b1) > 12 or abs(b2) > 12:
            continue
        return m1, float(int(b1)), m2, float(int(b2))


# ---------------------------------------------------------------------------
# Visual-Builder (Plotly-Traces via Fallback-Renderer)
# ---------------------------------------------------------------------------

def build_linear_visual(
    m: float,
    b: float,
    *,
    name: str = "f",
    x_range: tuple[float, float] = (-8, 8),
    color: str = "#1f77b4",
    extra_traces: list[dict] | None = None,
    extra_points: list[tuple[float, float, str]] | None = None,
    title: str = "",
) -> dict:
    """Plotly-Visual für eine oder mehrere lineare Funktionen."""
    x_min, x_max = x_range
    axis_max_x = nice_axis_max(max(abs(x_min), abs(x_max)))
    y_lo = m * x_min + b if m > 0 else m * x_max + b
    y_hi = m * x_max + b if m > 0 else m * x_min + b
    axis_max_y = nice_axis_max(max(abs(y_lo), abs(y_hi)) * 1.15)

    step = (x_max - x_min) / 200
    xs_set = {round(x_min + i * step, 10) for i in range(201)}
    for ix in range(math.ceil(x_min), math.floor(x_max) + 1):
        xs_set.add(float(ix))
    xs = sorted(xs_set)
    ys = [m * x + b for x in xs]

    traces = [
        {
            "x": [round(v, 4) for v in xs],
            "y": [round(v, 4) for v in ys],
            "mode": "lines",
            "name": f"{name}(x)",
            "line": {"color": color, "width": 2.5},
        }
    ]

    if extra_traces:
        traces.extend(extra_traces)

    if extra_points:
        px = [p[0] for p in extra_points]
        py = [p[1] for p in extra_points]
        labels = [p[2] for p in extra_points]
        traces.append({
            "x": px,
            "y": py,
            "mode": "markers+text",
            "name": "Punkte",
            "text": labels,
            "textposition": "top center",
            "marker": {"size": 8, "color": "#333"},
            "showlegend": False,
        })

    return {
        "type": "plot",
        "spec": {
            "type": "linear-function",
            "traces": traces,
            "layout": {
                "title": title,
                "xaxis": {
                    "title": "x",
                    "range": [-8, 8],
                    "dtick": 1,
                    "zeroline": True,
                },
                "yaxis": {
                    "title": "y",
                    "range": [-8, 8],
                    "dtick": 1,
                    "zeroline": True,
                },
            },
            "width": 700,
            "height": 500,
            "scale": 1,
        },
    }


def build_two_linear_visual(
    m1: float, b1: float, m2: float, b2: float,
    *,
    name1: str = "f",
    name2: str = "g",
    x_range: tuple[float, float] = (-8, 8),
) -> dict:
    """Visual mit zwei linearen Funktionen."""
    x_min, x_max = x_range
    step = (x_max - x_min) / 200
    xs_set = {round(x_min + i * step, 10) for i in range(201)}
    for ix in range(math.ceil(x_min), math.floor(x_max) + 1):
        xs_set.add(float(ix))
    xs = sorted(xs_set)
    ys2 = [m2 * x + b2 for x in xs]

    extra_trace = {
        "x": [round(v, 4) for v in xs],
        "y": [round(v, 4) for v in ys2],
        "mode": "lines",
        "name": f"{name2}(x)",
        "line": {"color": "#d62728", "width": 2.5},
    }

    return build_linear_visual(
        m1, b1,
        name=name1,
        x_range=x_range,
        extra_traces=[extra_trace],
    )
