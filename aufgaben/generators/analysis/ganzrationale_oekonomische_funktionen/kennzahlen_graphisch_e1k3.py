import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _kennzahlen_items,
    _sample_kennzahlen_parameters,
)


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
                            "range": [0.0, float(capacity) * rng.uniform(1.04, 1.16)],
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
