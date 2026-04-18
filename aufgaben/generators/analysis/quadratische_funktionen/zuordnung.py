"""Generator 01 – Zuordnung Graphen ↔ Gleichungen (quadratisch).

4 Graphen + 4 Gleichungen (NF, SPF, FF gemischt), Zuordnung per MC.
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    A_VALUES_INT,
    display_eq,
    ff_latex,
    ff_to_nf,
    fmt,
    nf_latex,
    nf_to_ff,
    nf_to_spf,
    spf_latex,
    spf_to_nf,
)


_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
_LABELS = ["a", "b", "c", "d"]


def _random_form_latex(
    a: float, b: float, c: float, form: str, name: str = "f"
) -> str:
    if form == "nf":
        return nf_latex(a, b, c, name)
    if form == "spf":
        a2, d, e = nf_to_spf(a, b, c)
        return spf_latex(a2, d, e, name)
    # ff
    result = nf_to_ff(a, b, c)
    if result is None:
        return nf_latex(a, b, c, name)
    return ff_latex(*result, name)


class ZuordnungGraphenQuadGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.zuordnung_graphen_quad"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            n = 4
            forms = ["nf", "spf", "ff", "nf"]
            rng.shuffle(forms)

            funcs: list[tuple[float, float, float]] = []
            attempts = 0
            while len(funcs) < n and attempts < 300:
                attempts += 1
                a = rng.choice(A_VALUES_INT)
                x1 = rng.randint(-4, 4)
                x2 = rng.randint(-4, 4)
                if x1 == x2:
                    continue
                b = -a * (x1 + x2)
                c = a * x1 * x2
                if abs(b) > 16 or abs(c) > 20:
                    continue
                # Scheitel muss im sichtbaren Bereich liegen
                d_v = -b / (2 * a)
                e_v = c - b**2 / (4 * a)
                if abs(d_v) > 7 or abs(e_v) > 7:
                    continue
                # Prüfe Unterscheidbarkeit
                ok = True
                for fa, fb, fc in funcs:
                    if (a == fa and b == fb and c == fc):
                        ok = False
                        break
                    d_old = -fb / (2 * fa)
                    e_old = fc - fb**2 / (4 * fa)
                    if abs(d_v - d_old) < 1.5 and abs(e_v - e_old) < 1.5:
                        ok = False
                        break
                    # Verschiedene Öffnungsfaktoren bevorzugen
                    if a == fa and abs(d_v - d_old) < 2:
                        ok = False
                        break
                if not ok:
                    continue
                funcs.append((float(a), float(b), float(c)))

            if len(funcs) < n:
                continue

            # Traces bauen – sichtbarer Bereich [-8, 8] × [-8, 8]
            x_min, x_max = -8, 8
            xs = [x_min + i * 0.08 for i in range(201)]
            traces = []
            for gi, (fa, fb, fc) in enumerate(funcs):
                ys = [fa * x**2 + fb * x + fc for x in xs]
                traces.append({
                    "x": [round(x, 2) for x in xs],
                    "y": [round(y, 4) for y in ys],
                    "mode": "lines",
                    "name": _LABELS[gi],
                    "line": {"color": _COLORS[gi], "width": 2.5},
                })

            visual = {
                "type": "plot",
                "spec": {
                    "type": "plotly",
                    "traces": traces,
                    "layout": {
                        "xaxis": {"range": [-8, 8], "dtick": 1},
                        "yaxis": {"range": [-8, 8], "dtick": 1},
                    },
                },
            }

            # Gleichungen erzeugen
            eq_labels = [
                _random_form_latex(fa, fb, fc, forms[gi], name=_LABELS[gi])
                for gi, (fa, fb, fc) in enumerate(funcs)
            ]

            # Fragen: 4 Gleichungen zeigen, je nach Graph zuordnen
            # Permutation für MC-Optionen
            perm = list(range(n))
            rng.shuffle(perm)

            options = [f"$ {eq_labels[p]} $" for p in perm]

            fragen = []
            antworten = []
            for gi in range(n):
                fragen.append(f"Graph {_LABELS[gi]} gehört zu …")
                correct = perm.index(gi)
                antworten.append(mc(options, correct))

            tasks.append(Task(
                einleitung="Ordnen Sie jedem Graphen die passende Gleichung zu.",
                fragen=fragen,
                antworten=antworten,
                visual=visual,
            ))

        return tasks
