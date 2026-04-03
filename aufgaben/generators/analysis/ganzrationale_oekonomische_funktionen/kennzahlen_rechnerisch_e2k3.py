import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _align_equations,
    _e2k3_kennzahlen_items,
    _erlös_quadratic_latex,
    _poly3_latex,
    _preis_linear_latex,
    _sample_e2k3_parameters,
)


class EconomicPolynomialKennzahlenRechnerischE2K3Generator(TaskGenerator):
    """Erzeugt E2K3-Kennzahlenaufgaben im JSON-Format wie in den Bestandsdateien."""

    generator_key = "analysis.ganzrationale_oekonomische_funktionen.kennzahlen_rechnerisch_e2k3"

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
                ) = _sample_e2k3_parameters(rng, for_graph=False)

                key = (a2, a1, k3, k2, k1, k0)
                if key in used_params:
                    continue
                used_params.add(key)
                break

            intro = (
                "Es liegen folgende Informationen vor:"
                f"{_align_equations([
                    _erlös_quadratic_latex(a2, a1),
                    _poly3_latex('K', k3, k2, k1, k0),
                    _poly3_latex('G', -k3, a2 - k2, a1 - k1, -k0),
                    _preis_linear_latex(a2, a1),
                ])}"
                "Bestimmen Sie (auf 2 NKS gerundet)"
            )

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

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=[question for question, _ in items],
                    antworten=[answer for _, answer in items],
                )
            )

        return tasks
