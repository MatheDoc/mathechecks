"""Gemeinsame Hilfsfunktionen für Lineare-Funktionen-Generatoren."""

from __future__ import annotations

import random

from aufgaben.core.tolerances import nice_axis_max, graph_read_tolerance_from_span


# ---------------------------------------------------------------------------
# LaTeX-Formatierung
# ---------------------------------------------------------------------------

def linear_latex(m: float, b: float, var: str = "x", name: str = "f") -> str:
    """Erzeugt z. B. ``f(x)=2x+3`` oder ``g(x)=-0,5x-1``."""
    m_str = _coeff_str(m, is_leading=True, with_var=True, var=var)
    b_str = _const_str(b)
    return f"{name}({var})={m_str}{b_str}"


def display_eq(expression: str) -> str:
    return f"$$ {expression} $$"


def inline(expression: str) -> str:
    return f"$ {expression} $"


def fmt_number(value: float, max_decimals: int = 4) -> str:
    """Zahl mit deutschem Komma, ohne trailing zeros."""
    rounded = round(float(value), max_decimals)
    text = f"{rounded:.{max_decimals}f}".rstrip("0").rstrip(".")
    if text in {"-0", ""}:
        text = "0"
    return text.replace(".", ",")


def fmt_int_or_frac(value: float) -> str:
    """Gibt eine Zahl als Ganzzahl oder als Bruch zurück (wenn halbe/drittel etc.)."""
    if value == int(value):
        return str(int(value))
    return fmt_number(value, 2)


# ---------------------------------------------------------------------------
# Interne LaTeX-Helfer
# ---------------------------------------------------------------------------

def _coeff_str(c: float, *, is_leading: bool, with_var: bool, var: str = "x") -> str:
    """Koeffizient vor einer Variablen formatieren."""
    if c == 0:
        return "0" if is_leading and not with_var else ""
    sign = "" if (is_leading and c > 0) else ("+" if c > 0 else "-")
    abs_c = abs(c)
    if with_var:
        if abs_c == 1:
            num = ""
        else:
            num = fmt_number(abs_c)
        return f"{sign}{num}{var}"
    return f"{sign}{fmt_number(abs_c)}"


def _const_str(b: float) -> str:
    """Konstanten-Term (z. B. ``+3`` oder ``-1``)."""
    if b == 0:
        return ""
    sign = "+" if b > 0 else "-"
    return f"{sign}{fmt_number(abs(b))}"


# ---------------------------------------------------------------------------
# Zufallsparameter
# ---------------------------------------------------------------------------

# Steigungen: ganzzahlig oder halbe Werte, kein 0
SLOPES = [v / 2 for v in range(-12, 13) if v != 0]
# y-Achsenabschnitte: ganzzahlig
INTERCEPTS = list(range(-8, 9))


def sample_linear(rng: random.Random) -> tuple[float, float]:
    """Zufällige Steigung und y-Achsenabschnitt."""
    m = rng.choice(SLOPES)
    b = rng.choice(INTERCEPTS)
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

    xs = [x_min + i * (x_max - x_min) / 200 for i in range(201)]
    ys = [m * x + b for x in xs]

    traces = [
        {
            "x": xs,
            "y": ys,
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
                    "range": [-axis_max_x, axis_max_x],
                    "zeroline": True,
                },
                "yaxis": {
                    "title": "y",
                    "range": [-axis_max_y, axis_max_y],
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
    xs = [x_min + i * (x_max - x_min) / 200 for i in range(201)]
    ys2 = [m2 * x + b2 for x in xs]

    extra_trace = {
        "x": xs,
        "y": ys2,
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
