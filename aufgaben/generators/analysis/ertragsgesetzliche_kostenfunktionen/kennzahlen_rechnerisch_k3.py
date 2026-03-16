import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _num_tol,
    _poly3_latex,
    _sample_k3_cost_coefficients_from_exact_kennzahlen,
)


class ErtragsgesetzlicheKostenKennzahlenRechnerischK3Generator(TaskGenerator):
    """Erzeugt rechnerische K3-Kennzahlenaufgaben für ertragsgesetzliche Kostenfunktionen."""

    generator_key = "analysis.ertragsgesetzliche_kostenfunktionen.kennzahlen_rechnerisch_k3"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[float, float, float, float]] = set()

        for _ in range(count):
            while True:
                (
                    k3,
                    k2,
                    k1,
                    k0,
                    x_wende,
                    x_betriebsminimum,
                    x_betriebsoptimum,
                    kurzfristige_preisuntergrenze,
                    langfristige_preisuntergrenze,
                ) = _sample_k3_cost_coefficients_from_exact_kennzahlen(rng)

                key = (k3, k2, k1, k0)
                if key in used:
                    continue
                used.add(key)
                break

            intro = (
                "Die Kostenfunktion eines Unternehmens lautet"
                f"</p> <p>{_poly3_latex('K', k3, k2, k1, k0)}."
                "</p> <p>Bestimmen Sie (auf 2 NKS gerundet)"
            )

            items = [
                ("die kurzfristige Preisuntergrenze.", _num_tol(kurzfristige_preisuntergrenze, 0.1)),
                ("das Betriebsminimum.", _num_tol(x_betriebsminimum, 0.1)),
                ("die langfristige Preisuntergrenze.", _num_tol(langfristige_preisuntergrenze, 0.1)),
                ("das Betriebsoptimum.", _num_tol(x_betriebsoptimum, 0.1)),
                (
                    "die Menge beim Übergang vom degressiven zum progressiven Kostenwachstum.",
                    _num_tol(x_wende, 0.1),
                ),
            ]

            tasks.append(
                Task(
                    einleitung=intro,
                    fragen=[question for question, _ in items],
                    antworten=[answer for _, answer in items],
                )
            )

        return tasks
