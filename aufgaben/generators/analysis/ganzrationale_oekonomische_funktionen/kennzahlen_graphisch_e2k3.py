import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _e2k3_graph_y_range,
    _e2k3_kennzahlen_items,
    _sample_e2k3_parameters,
)


class EconomicPolynomialKennzahlenGraphischE2K3Generator(TaskGenerator):
    """Erzeugt graphische E2K3-Kennzahlenaufgaben mit visual.spec (Plotly-Traces)."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.kennzahlen_graphisch_e2k3"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[float, float, float, float, float, float]] = set()

        for _ in range(count):
            while True:
                (
                    a2,
                    a1,
                    k3,
                    k2,
                    k1,
                    k0,
                    x_break_even_low,
                    x_break_even_high,
                    x_gain_max,
                ) = _sample_e2k3_parameters(rng, for_graph=True)

                key = (a2, a1, k3, k2, k1, k0)
                if key in used_params:
                    continue
                used_params.add(key)
                break

            x_sättigung = -a1 / a2
            max_x = x_sättigung * rng.uniform(1.04, 1.14)
            y_min, y_max = _e2k3_graph_y_range(
                a2=a2,
                a1=a1,
                k3=k3,
                k2=k2,
                k1=k1,
                k0=k0,
                x_max=max_x,
            )
            points = 280
            x_values = [max_x * index / (points - 1) for index in range(points)]
            p_values = [a2 * x + a1 for x in x_values]
            e_values = [a2 * (x ** 2) + a1 * x for x in x_values]
            k_values = [k3 * (x ** 3) + k2 * (x ** 2) + k1 * x + k0 for x in x_values]
            g_values = [e - k for e, k in zip(e_values, k_values)]

            items = _e2k3_kennzahlen_items(
                rng=rng,
                a2=a2,
                a1=a1,
                k3=k3,
                k2=k2,
                k1=k1,
                k0=k0,
                x_break_even_low=x_break_even_low,
                x_break_even_high=x_break_even_high,
                x_gain_max=x_gain_max,
            )

            intro = (
                "Das Diagramm zeigt die Preis-Absatz-, Erlös-, Kosten- und Gewinnfunktion "
                "eines Unternehmens. Bestimmen Sie"
            )

            visual = {
                "type": "plot",
                "spec": {
                    "type": "plotly",
                    "traces": [
                        {
                            "kind": "scatter",
                            "x": x_values,
                            "y": p_values,
                            "mode": "lines",
                            "name": "p(x)",
                            "line": {"color": "#ff7f0e"},
                        },
                        {
                            "kind": "scatter",
                            "x": x_values,
                            "y": e_values,
                            "mode": "lines",
                            "name": "E(x)",
                            "line": {"color": "#2ca02c"},
                        },
                        {
                            "kind": "scatter",
                            "x": x_values,
                            "y": k_values,
                            "mode": "lines",
                            "name": "K(x)",
                            "line": {"color": "#d62728"},
                        },
                        {
                            "kind": "scatter",
                            "x": x_values,
                            "y": g_values,
                            "mode": "lines",
                            "name": "G(x)",
                            "line": {"color": "#1f77b4"},
                        },
                    ],
                    "layout": {
                        "title": "Preis-Absatz-, Erlös-, Kosten- und Gewinnfunktion",
                        "xaxis": {"title": "Menge x"},
                        "yaxis": {"title": "Wert", "range": [y_min, y_max]},
                    },
                    "width": 900,
                    "height": 520,
                    "scale": 1,
                },
            }

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=[question for question, _ in items],
                    antworten=[answer for _, answer in items],
                    visual=visual,
                )
            )

        return tasks
