import random

from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.ganzrationale_oekonomische_funktionen.shared import (
    _axis_tick_step,
    _num_tol,
    _sample_k3_cost_coefficients_from_exact_kennzahlen,
)


class ErtragsgesetzlicheKostenKennzahlenGraphischK3Generator(TaskGenerator):
    """Erzeugt graphische K3-Kennzahlenaufgaben für ertragsgesetzliche Kostenfunktionen."""

    generator_key = "analysis.ertragsgesetzliche_kostenfunktionen.kennzahlen_graphisch_k3"

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

            max_x = round(max(14.0, x_betriebsoptimum * 1.35, x_wende * 2.25), 1)

            # y-Achse: Bereich auf Basis der drei Tiefpunkte berechnen
            gk_at_wende = 3.0 * k3 * x_wende ** 2 + 2.0 * k2 * x_wende + k1
            min_y_values = [gk_at_wende, kurzfristige_preisuntergrenze, langfristige_preisuntergrenze]
            highest = max(min_y_values)
            lowest = min(min_y_values)
            span = max(highest - lowest, 5.0)
            y_max = round(highest + 2.5 * span, 1)
            x_tolerance = _axis_tick_step(max_x) / 4.0
            y_tolerance = _axis_tick_step(y_max) / 4.0

            items = [
                ("die kurzfristige Preisuntergrenze.", _num_tol(kurzfristige_preisuntergrenze, y_tolerance)),
                ("das Betriebsminimum.", _num_tol(x_betriebsminimum, x_tolerance)),
                ("die langfristige Preisuntergrenze.", _num_tol(langfristige_preisuntergrenze, y_tolerance)),
                ("das Betriebsoptimum.", _num_tol(x_betriebsoptimum, x_tolerance)),
                (
                    "die Menge beim Übergang vom degressiven zum progressiven Kostenwachstum.",
                    _num_tol(x_wende, x_tolerance),
                ),
            ]

            intro = (
                "Das Diagramm zeigt die Grenzkosten-, Stückkosten- und variable "
                "Stückkostenfunktion eines Unternehmens. Bestimmen Sie"
            )

            visual = {
                "type": "plot",
                "spec": {
                    "type": "cost-curves",
                    "params": {
                        "k3": k3,
                        "k2": k2,
                        "k1": k1,
                        "k0": k0,
                        "maxX": max_x,
                        "yMax": y_max,
                    },
                    "layout": {
                        "title": "Grenzkosten-, Stückkosten- und variable Stückkostenfunktion",
                        "xaxis": {"title": "Menge x", "range": [0, max_x]},
                        "yaxis": {"title": "Kosten", "range": [0, y_max]},
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
