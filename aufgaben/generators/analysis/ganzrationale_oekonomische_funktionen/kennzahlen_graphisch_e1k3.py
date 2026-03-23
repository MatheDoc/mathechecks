import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _axis_tick_step,
    _kennzahlen_items,
    _sample_kennzahlen_parameters,
)
from aufgaben.generators.analysis.shared_numbers import uniform_sig


class EconomicPolynomialKennzahlenGraphischGenerator(TaskGenerator):
    """Erzeugt graphische Kennzahlen-Aufgaben mit visual.spec (ohne Base64 im JSON)."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.kennzahlen_graphisch"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used_params: set[tuple[float, float, float, float, float, int]] = set()

        for _ in range(count):
            while True:
                (
                    k3,
                    k2,
                    k1,
                    k0,
                    price,
                    x_break_even_low,
                    x_break_even_high,
                    x_gain_max,
                    capacity,
                ) = _sample_kennzahlen_parameters(rng, for_graph=True)

                key = (k3, k2, k1, k0, price, capacity)
                if key in used_params:
                    continue
                used_params.add(key)
                break

            x_axis_max = float(capacity) * uniform_sig(rng, 1.04, 1.16)
            plot_points = 300
            y_values: list[float] = []
            for index in range(plot_points + 1):
                x_value = (capacity * index) / plot_points
                e_value = price * x_value
                k_value = k3 * (x_value ** 3) + k2 * (x_value ** 2) + k1 * x_value + k0
                g_value = e_value - k_value
                y_values.extend((e_value, k_value, g_value))

            y_span = max(1.0, max(y_values) - min(y_values))
            x_tolerance = _axis_tick_step(x_axis_max) / 4.0
            y_tolerance = _axis_tick_step(y_span) / 4.0

            items = _kennzahlen_items(
                rng=rng,
                k3=k3,
                k2=k2,
                k1=k1,
                k0=k0,
                price=price,
                x_break_even_low=x_break_even_low,
                x_break_even_high=x_break_even_high,
                x_gain_max=x_gain_max,
                capacity=capacity,
                x_tolerance=x_tolerance,
                y_tolerance=y_tolerance,
            )

            intro = (
                "Das Diagramm zeigt die Erlös-, Kosten- und Gewinnfunktion eines Unternehmens. "
                f"Die Kapazitätsgrenze beträgt {capacity} Mengeneinheiten. "
                "Bestimmen Sie"
            )

            visual = {
                "type": "plot",
                "spec": {
                    "type": "economic-curves",
                    "params": {
                        "k3": k3,
                        "k2": k2,
                        "k1": k1,
                        "k0": k0,
                        "price": price,
                        "capacity": capacity,
                    },
                    "layout": {
                        "title": "Erlös-, Kosten- und Gewinnfunktion",
                        "xaxis": {
                            "title": "Menge x",
                            "range": [0.0, x_axis_max],
                        },
                        "yaxis": {"title": "Wert"},
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
