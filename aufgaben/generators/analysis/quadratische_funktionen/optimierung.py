"""Generator 11 – Optimierung (quadratisch).

Zielfunktion → Scheitel → Max/Min → Interpretation. Gruppiert/sequential.
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc, mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    A_VALUES_INT,
    display_eq,
    fmt,
    nf_latex,
)


_SZENARIEN: list[dict] = [
    {
        "kontext": (
            "Ein Unternehmen verkauft ein Produkt zum Preis von $ p $ Euro. "
            "Der Gewinn in Abhängigkeit vom Verkaufspreis wird beschrieben durch:"
        ),
        "var": "p",
        "einheit_x": "€",
        "einheit_y": "€",
        "func_name": "G",
        "extremum": "Maximum",
        "frage_x": "Bei welchem Preis wird der Gewinn maximal?",
        "frage_y": "Wie hoch ist der maximale Gewinn?",
        "frage_interpret": "optimaler Verkaufspreis",
    },
    {
        "kontext": (
            "Die Produktionskosten eines Betriebs hängen von der "
            "Produktionsmenge $ x $ (in Tausend Stück) ab:"
        ),
        "var": "x",
        "einheit_x": "Tsd. Stück",
        "einheit_y": "€",
        "func_name": "K",
        "extremum": "Minimum",
        "frage_x": "Bei welcher Menge sind die Kosten minimal?",
        "frage_y": "Wie hoch sind die minimalen Kosten?",
        "frage_interpret": "optimale Produktionsmenge",
    },
    {
        "kontext": (
            "Die Besucherzahl eines Freizeitparks hängt vom "
            "Eintrittspreis $ p $ (in Euro) ab:"
        ),
        "var": "p",
        "einheit_x": "€",
        "einheit_y": "Besucher",
        "func_name": "B",
        "extremum": "Maximum",
        "frage_x": "Bei welchem Eintrittspreis ist die Besucherzahl maximal?",
        "frage_y": "Wie hoch ist die maximale Besucherzahl?",
        "frage_interpret": "optimaler Eintrittspreis",
    },
    {
        "kontext": (
            "Ein Landwirt möchte eine rechteckige Fläche mit einem "
            "Zaun einzäunen. Der Umfang ist fest, die Fläche $ A $ "
            "hängt von der Seitenlänge $ x $ ab:"
        ),
        "var": "x",
        "einheit_x": "m",
        "einheit_y": "m²",
        "func_name": "A",
        "extremum": "Maximum",
        "frage_x": "Welche Seitenlänge maximiert die Fläche?",
        "frage_y": "Wie groß ist die maximale Fläche?",
        "frage_interpret": "optimale Seitenlänge",
    },
]


class OptimierungQuadGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.optimierung_quad"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        while len(tasks) < count:
            task = self._build(rng)
            if task is not None:
                tasks.append(task)

        return tasks

    def _build(self, rng: random.Random) -> Task | None:
        sz = rng.choice(_SZENARIEN)
        is_max = sz["extremum"] == "Maximum"

        # a < 0 für Max, a > 0 für Min
        if is_max:
            a = rng.choice([-2, -1])
        else:
            a = rng.choice([1, 2])

        # Scheitelpunkt bei ganzzahligen Koordinaten
        d = rng.randint(2, 8)  # immer positiv (Sachkontext)
        e = rng.randint(5, 30) if is_max else rng.randint(5, 20)

        b = -2 * a * d
        c = a * d**2 + e

        if abs(b) > 40 or abs(c) > 80:
            return None

        fn = sz["func_name"]
        var = sz["var"]
        eq = nf_latex(float(a), float(b), float(c), name=fn, var=var)

        art_options = ["Maximum", "Minimum"]
        correct_idx = 0 if is_max else 1

        fragen = [
            f"Hat $ {fn} $ ein Maximum oder Minimum?",
            sz["frage_x"],
            sz["frage_y"],
        ]
        antworten = [
            mc(art_options, correct_idx),
            numerical_analysis_calc(d),
            numerical_analysis_calc(e),
        ]

        kontext = sz["kontext"] + display_eq(eq)

        return Task(
            einleitung=kontext,
            fragen=fragen,
            antworten=antworten,
        )
