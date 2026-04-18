"""Generator 10 – Geometrisches Szenario (quadratisch).

Sachaufgabe mit 3-4 Teilfragen, gruppiert/sequential.
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.quadratische_funktionen.shared import (
    fmt,
    nf_latex,
    display_eq,
)


_SZENARIEN: list[dict] = [
    {
        "kontext": (
            "Ein Fußball wird aus einer Höhe von {h0} m mit einem Schuss "
            "abgefeuert. Die Flughöhe des Balls wird durch die Funktion "
            "$ h(x) = {eq} $ beschrieben, wobei $ x $ die horizontale "
            "Entfernung in Metern ist."
        ),
        "var": "x",
        "einheit_x": "m",
        "einheit_y": "m",
        "func_name": "h",
        "frage_hoehe": "Welche maximale Höhe erreicht der Ball?",
        "frage_pos": "In welcher Entfernung erreicht der Ball die maximale Höhe?",
        "frage_weite": "Wie weit fliegt der Ball insgesamt?",
        "frage_eval": "Welche Höhe hat der Ball bei einer Entfernung von $ {x_eval} $ m?",
    },
    {
        "kontext": (
            "Ein Brückenbogen kann durch die Funktion "
            "$ h(x) = {eq} $ modelliert werden, wobei $ x $ die "
            "horizontale Position in Metern und $ h(x) $ die Höhe "
            "in Metern über dem Boden angibt."
        ),
        "var": "x",
        "einheit_x": "m",
        "einheit_y": "m",
        "func_name": "h",
        "frage_hoehe": "Wie hoch ist der Brückenbogen an seiner höchsten Stelle?",
        "frage_pos": "An welcher Stelle erreicht der Bogen die größte Höhe?",
        "frage_weite": "Wie breit ist der Brückenbogen?",
        "frage_eval": "Wie hoch ist der Bogen an der Stelle $ x = {x_eval} $?",
    },
    {
        "kontext": (
            "Ein Wasserstrahl aus einem Springbrunnen folgt der Bahn "
            "$ h(x) = {eq} $, wobei $ x $ die horizontale Entfernung "
            "in Metern und $ h(x) $ die Höhe in Metern ist."
        ),
        "var": "x",
        "einheit_x": "m",
        "einheit_y": "m",
        "func_name": "h",
        "frage_hoehe": "Welche maximale Höhe erreicht der Wasserstrahl?",
        "frage_pos": "In welcher Entfernung erreicht der Strahl die maximale Höhe?",
        "frage_weite": "In welcher Entfernung trifft der Strahl wieder auf dem Boden auf?",
        "frage_eval": "Welche Höhe hat der Strahl bei einer Entfernung von $ {x_eval} $ m?",
    },
    {
        "kontext": (
            "Ein Speerwurf wird modelliert durch "
            "$ h(x) = {eq} $, wobei $ x $ die horizontale "
            "Entfernung in Metern und $ h(x) $ die Flughöhe "
            "in Metern ist. Der Speer wird aus $ {h0} $ m Höhe geworfen."
        ),
        "var": "x",
        "einheit_x": "m",
        "einheit_y": "m",
        "func_name": "h",
        "frage_hoehe": "Welche maximale Höhe erreicht der Speer?",
        "frage_pos": "In welcher Entfernung erreicht der Speer die maximale Höhe?",
        "frage_weite": "Wie weit fliegt der Speer insgesamt?",
        "frage_eval": "Welche Höhe hat der Speer bei einer Entfernung von $ {x_eval} $ m?",
    },
]


class GeometrischesSzenarioQuadGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.geometrisches_szenario_quad"

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

        # Parabel: a < 0 (nach unten geöffnet), NS bei 0 und x_w > 0
        # f(x) = a·x·(x - x_w) = a·x² - a·x_w·x
        # → b = -a·x_w, c = 0 plus Starthöhe h0
        # f(x) = a(x)(x - x_w) + h0·(1 - x/x_w)  → zu komplex
        # Einfacher: f(x) = a·x² + b·x + c mit c = h0, NS bei positiven x
        # Scheitel bei x_s = -b/(2a), max_h = c - b²/(4a)

        a = rng.choice([-2, -1])
        x_w = rng.choice([6, 8, 10, 12])  # Weite (positive NS)
        h0 = rng.choice([0, 2, 4])  # Starthöhe = f(0) = c

        # f(0) = c = h0
        # f(x_w) = 0 → a·x_w² + b·x_w + h0 = 0 → b = -(a·x_w² + h0)/x_w
        b_num = -(a * x_w**2 + h0)
        if b_num % x_w != 0:
            return None
        b = b_num // x_w
        c = h0

        # Scheitel
        x_s = -b / (2 * a)
        y_s = a * x_s**2 + b * x_s + c

        if y_s <= 0:
            return None

        fn = sz["func_name"]
        eq_raw = nf_latex(float(a), float(b), float(c), name=fn)
        kontext = sz["kontext"].format(eq=eq_raw, h0=h0)

        # Nullstellen
        # f(x) = 0 → a·x² + b·x + c = 0
        D = b**2 - 4 * a * c
        if D < 0:
            return None
        import math
        sq = math.sqrt(D)
        ns1 = (-b - sq) / (2 * a)
        ns2 = (-b + sq) / (2 * a)
        ns_pos = max(ns1, ns2)

        # Funktionswert an einem bestimmten Punkt
        x_eval = rng.choice([v for v in range(1, x_w) if v != int(x_s)])
        y_eval = a * x_eval**2 + b * x_eval + c

        fragen = [
            sz["frage_hoehe"],
            sz["frage_pos"],
            sz["frage_weite"],
            sz["frage_eval"].format(x_eval=x_eval),
        ]
        antworten = [
            numerical_analysis_calc(y_s),
            numerical_analysis_calc(x_s),
            numerical_analysis_calc(ns_pos),
            numerical_analysis_calc(y_eval),
        ]

        return Task(
            einleitung=kontext,
            fragen=fragen,
            antworten=antworten,
        )
