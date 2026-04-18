"""Generator 03 – Gleichung → Wertetabelle (quadratisch).

NF gegeben, 5 x-Werte, y berechnen.
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    display_eq,
    fmt,
    nf_latex,
    sample_nf_nice,
)

_CIRCLED = ["①", "②", "③", "④", "⑤"]


def _make_wertetabelle_html(
    x_vals: list[int],
    y_vals: list[float],
    hidden_indices: list[int],
) -> str:
    header_cells = "".join(f"<td>$ {x} $</td>" for x in x_vals)
    header = f"<tr><td>$ x $</td>{header_cells}</tr>"

    body_cells = []
    ci = 0
    for i, y in enumerate(y_vals):
        if i in hidden_indices:
            body_cells.append(f"<td>{_CIRCLED[ci]}</td>")
            ci += 1
        else:
            body_cells.append(f"<td>$ {fmt(y)} $</td>")
    body = f'<tr><td>$ f(x) $</td>{"".join(body_cells)}</tr>'
    return f'<table class="wertetabelle">\n{header}\n{body}\n</table>'


class GleichungZuTabelleQuadGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.gleichung_zu_tabelle_quad"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, float]] = set()

        while len(tasks) < count:
            a, b, c, _, _ = sample_nf_nice(rng)
            key = (a, b, c)
            if key in used:
                continue
            used.add(key)

            x_vals = list(range(-2, 3))
            y_vals = [a * x**2 + b * x + c for x in x_vals]

            hidden = sorted(rng.sample(range(5), 3))
            eq = nf_latex(a, b, c)
            table = _make_wertetabelle_html(x_vals, y_vals, hidden)

            fragen = []
            antworten = []
            for ci, idx in enumerate(hidden):
                fragen.append(f"Wert {_CIRCLED[ci]}")
                antworten.append(
                    f"$ f({x_vals[idx]}) = ${numerical_analysis_calc(y_vals[idx])}"
                )

            tasks.append(Task(
                einleitung=(
                    f"Gegeben:{display_eq(eq)}"
                    f"Vervollständigen Sie die Wertetabelle.\n\n{table}"
                ),
                fragen=fragen,
                antworten=antworten,
            ))

        return tasks
