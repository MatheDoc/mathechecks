import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _erlös_latex,
    _kennzahlen_items,
    _poly3_latex,
    _preis_latex,
    _sample_kennzahlen_parameters,
)


class EconomicPolynomialKennzahlenGenerator(TaskGenerator):
    """Erzeugt Kennzahlen-Aufgaben zu ganzrationalen ökonomischen Funktionen."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.kennzahlen_rechnerisch"

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
                ) = _sample_kennzahlen_parameters(rng, for_graph=False)

                key = (k3, k2, k1, k0, price, capacity)
                if key in used_params:
                    continue
                used_params.add(key)
                break

            intro = (
                "Es liegen folgende Informationen vor:"
                f"</p> <p>{_erlös_latex(price)}"
                f"</p> <p>{_poly3_latex('K', k3, k2, k1, k0)}"
                f"</p> <p>{_poly3_latex('G', -k3, -k2, price - k1, -k0)}"
                f"</p> <p>{_preis_latex(price)}"
                f"</p> <p>Die Kapazitätsgrenze beträgt {capacity} Mengeneinheiten."
                "</p> <p>Bestimmen Sie (auf 2 NKS gerundet)"
            )

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

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=[question for question, _ in items],
                    antworten=[answer for _, answer in items],
                )
            )

        return tasks
