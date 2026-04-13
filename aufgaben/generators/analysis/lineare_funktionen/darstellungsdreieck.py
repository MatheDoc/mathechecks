"""Generatoren für Checks 01–04 (Darstellungswechsel).

01  Graph → Gleichung                  (graph-zu-gleichung)
02  Gleichung → Wertetabelle           (gleichung-zu-tabelle)
03  Zuordnung Graphen ↔ Gleichungen    (zuordnung-graphen)
04  Punkte → Gleichung                 (gleichung-aus-punkten)
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc, mc
from aufgaben.core.tolerances import graph_read_tolerance_from_span
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.lineare_funktionen.shared import (
    build_linear_visual,
    display_eq,
    fmt_number,
    inline,
    linear_latex,
    sample_linear,
    sample_linear_nice_null,
    INTERCEPTS,
    SLOPES,
)


# Eingekreiste Zahlen (Unicode)
_CIRCLED = ["①", "②", "③", "④", "⑤"]

# Graph-Label-Farben
_GRAPH_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
_GRAPH_LABELS = ["a", "b", "c", "d", "e"]


# ===================================================================
# Check 01 – Graph → Gleichung
# ===================================================================

class GraphZuGleichungGenerator(TaskGenerator):
    """Aus einem Graph die Funktionsgleichung ablesen."""

    generator_key = "analysis.lineare_funktionen.graph_zu_gleichung"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float]] = set()

        while len(tasks) < count:
            m, b = sample_linear(rng)
            if (m, b) in used:
                continue
            used.add((m, b))

            visual = build_linear_visual(m, b, title="Graph von f")

            tasks.append(Task(
                einleitung=(
                    "Bestimmen Sie die Gleichung der linearen Funktion $ f $."
                ),
                fragen=[
                    "Gleichung",
                ],
                antworten=[
                    f"$ f(x) = ${numerical_analysis_calc(m)}$ \\cdot x + ${numerical_analysis_calc(b)}",
                ],
                visual=visual,
            ))

        return tasks


# ===================================================================
# Check 02 – Gleichung → Wertetabelle
# ===================================================================

def _make_wertetabelle_html(
    x_vals: list[int],
    y_vals: list[float],
    hidden_indices: list[int],
) -> str:
    """HTML-Wertetabelle mit eingekreisten Zahlen für fehlende Werte."""
    header_cells = "".join(f"<td>$ {x} $</td>" for x in x_vals)
    header = f"<tr><td>$ x $</td>{header_cells}</tr>"

    body_cells = []
    circle_counter = 0
    for i, y in enumerate(y_vals):
        if i in hidden_indices:
            body_cells.append(f"<td>{_CIRCLED[circle_counter]}</td>")
            circle_counter += 1
        else:
            body_cells.append(f"<td>$ {fmt_number(y)} $</td>")
    body = f'<tr><td>$ f(x) $</td>{"".join(body_cells)}</tr>'

    return f'<table class="wertetabelle">\n{header}\n{body}\n</table>'


class GleichungZuTabelleGenerator(TaskGenerator):
    """Wertetabelle vervollständigen (eingekreiste Zahlen)."""

    generator_key = "analysis.lineare_funktionen.gleichung_zu_tabelle"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float]] = set()

        while len(tasks) < count:
            m, b = sample_linear(rng)
            if (m, b) in used:
                continue
            used.add((m, b))

            x_vals = list(range(-2, 3))  # 5 x-Werte
            y_vals = [m * x + b for x in x_vals]

            # 3 Werte verbergen
            hidden_indices = sorted(rng.sample(range(len(x_vals)), 3))

            eq = linear_latex(m, b)
            table_html = _make_wertetabelle_html(x_vals, y_vals, hidden_indices)

            fragen = []
            antworten = []
            for ci, idx in enumerate(hidden_indices):
                fragen.append(f"Wert {_CIRCLED[ci]}")
                antworten.append(
                    f"$ f({x_vals[idx]}) = ${numerical_analysis_calc(y_vals[idx])}"
                )

            tasks.append(Task(
                einleitung=(
                    f"Gegeben:{display_eq(eq)}"
                    f"Vervollständigen Sie die Wertetabelle.\n\n{table_html}"
                ),
                fragen=fragen,
                antworten=antworten,
            ))

        return tasks


# ===================================================================
# Check 03 – Zuordnung Graphen ↔ Gleichungen (NEU)
# ===================================================================

class ZuordnungGraphenGenerator(TaskGenerator):
    """Mehrere Graphen gezeigt, Gleichungen per MC zuordnen."""

    generator_key = "analysis.lineare_funktionen.zuordnung_graphen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            n_graphs = 5  # 5 Funktionen im Diagramm
            n_questions = 3  # 3 per MC zuordnen

            # 5 verschiedene Funktionen erzeugen
            funcs: list[tuple[float, float]] = []
            attempts = 0
            while len(funcs) < n_graphs and attempts < 200:
                attempts += 1
                m, b = sample_linear(rng)
                # Keine zu ähnlichen Steigungen
                if any(abs(m - fm) < 0.3 and abs(b - fb) < 1.5 for fm, fb in funcs):
                    continue
                funcs.append((m, b))

            if len(funcs) < n_graphs:
                continue

            # Plotly-Traces bauen
            x_min, x_max = -6, 6
            xs = [x_min + i * (x_max - x_min) / 200 for i in range(201)]
            traces = []
            for gi, (fm, fb) in enumerate(funcs):
                ys = [fm * x + fb for x in xs]
                traces.append({
                    "x": xs,
                    "y": ys,
                    "mode": "lines",
                    "name": _GRAPH_LABELS[gi],
                    "line": {"color": _GRAPH_COLORS[gi], "width": 2.5},
                })

            from aufgaben.core.tolerances import nice_axis_max
            all_y = [fm * x + fb for fm, fb in funcs for x in [x_min, x_max]]
            axis_y = nice_axis_max(max(abs(y) for y in all_y) * 1.15)
            axis_x = nice_axis_max(max(abs(x_min), abs(x_max)))

            visual = {
                "type": "plot",
                "spec": {
                    "type": "linear-zuordnung",
                    "traces": traces,
                    "layout": {
                        "title": "",
                        "xaxis": {"title": "x", "range": [-axis_x, axis_x], "zeroline": True},
                        "yaxis": {"title": "y", "range": [-axis_y, axis_y], "zeroline": True},
                        "showlegend": True,
                    },
                    "width": 700,
                    "height": 500,
                    "scale": 1,
                },
            }

            # 3 zufällige Funktionen abfragen
            ask_indices = sorted(rng.sample(range(n_graphs), n_questions))

            fragen = []
            antworten = []
            options = [lbl for lbl in _GRAPH_LABELS[:n_graphs]]

            for qi in ask_indices:
                fm, fb = funcs[qi]
                eq_str = f"$ {linear_latex(fm, fb)} $"
                fragen.append(f"Welcher Graph gehört zu {eq_str}?")
                antworten.append(mc(options, qi))

            tasks.append(Task(
                einleitung="Ordnen Sie die Gleichungen den Graphen zu.",
                fragen=fragen,
                antworten=antworten,
                visual=visual,
            ))

        return tasks


# ===================================================================
# Check 04 – Punkte → Gleichung
# ===================================================================

class GleichungAusPunktenGenerator(TaskGenerator):
    """Aus zwei Punkten die Funktionsgleichung bestimmen."""

    generator_key = "analysis.lineare_funktionen.gleichung_aus_punkten"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[int, int, int, int]] = set()

        while len(tasks) < count:
            x1 = rng.randint(-8, 8)
            x2 = rng.randint(-8, 8)
            if x1 == x2:
                continue
            y1 = rng.randint(-8, 8)
            y2 = rng.randint(-8, 8)

            key = (x1, y1, x2, y2)
            if key in used:
                continue

            m = (y2 - y1) / (x2 - x1)
            b = y1 - m * x1

            if m == 0:
                continue
            if m * 2 != int(m * 2):
                continue
            if b != int(b):
                continue
            if abs(m) > 6 or abs(b) > 12:
                continue

            used.add(key)
            b = float(int(b))

            tasks.append(Task(
                einleitung=(
                    f"Die Punkte $ P_1({x1}|{y1}) $ und $ P_2({x2}|{y2}) $ "
                    "liegen auf dem Graphen einer linearen Funktion $ f $.\n\n"
                    "Bestimmen Sie die Gleichung."
                ),
                fragen=[
                    "Gleichung",
                ],
                antworten=[
                    f"$ f(x) = ${numerical_analysis_calc(m)}$ \\cdot x + ${numerical_analysis_calc(b)}",
                ],
            ))

        return tasks
