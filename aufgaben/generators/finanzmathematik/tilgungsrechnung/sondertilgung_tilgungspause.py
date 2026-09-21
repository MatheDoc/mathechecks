"""Check 07 – Sondertilgung und Tilgungspause."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_finanz_geld, numerical_finanz_laufzeit
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    annuitaet,
    annuitaet_n,
    geld,
    prozent,
    q_of,
    restschuld,
    rund2,
    sample_darlehen,
    sample_zinssatz,
    schoen,
)
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge


class SondertilgungTilgungspauseGenerator(TaskGenerator):
    generator_key = "finanzmathematik.tilgungsrechnung.sondertilgung_tilgungspause"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        for index, sz in enumerate(szenario_folge(rng, count)):
            pause = index % 2 == 1
            task = None
            while task is None:
                task = self._build(rng, sz, pause)
            tasks.append(task)
        return tasks

    def _build(self, rng: random.Random, sz: Szenario, pause: bool) -> Task | None:
        k0 = sample_darlehen(rng, sz.stufe)
        p = sample_zinssatz(rng)
        n = rng.randint(8, 25)
        k = rng.randint(3, n - 4)
        q = q_of(p)
        a = rund2(annuitaet(k0, q, n))
        rk = restschuld(k0, a, q, k)
        basis = (
            f"{sz.subjekt} nimmt {sz.zweck_darlehen} ein Annuitätendarlehen über {geld(k0)} zu {prozent(p)} "
            f"mit einer Laufzeit von {n} Jahren auf; die Annuität beträgt {geld(a, cents=True)}."
        )

        if pause:
            zinsen_pause = rk * (q - 1.0)
            a_neu = annuitaet(rk, q, n - k - 1)
            # bei unveränderter Annuität verschiebt die Pause den Plan um genau ein Jahr
            n_rest = annuitaet_n(rk, a, q)
            if n_rest is None:
                return None
            intro = basis + f" Im {k + 1}. Jahr setzt {sz.pron} die Tilgung aus und zahlt nur die Zinsen."
            return Task(
                einleitung=intro,
                fragen=[
                    f"Wie hoch ist die Restschuld nach {k} Jahren?",
                    f"Welche Zahlung ist im {k + 1}. Jahr zu leisten?",
                    f"Die Gesamtlaufzeit von {n} Jahren soll unverändert bleiben. Wie hoch ist die Annuität für die verbleibenden {n - k - 1} Jahre?",
                    f"Stattdessen bleibt die Annuität unverändert. Wie viele Jahre dauert die Rückzahlung nach dem {k + 1}. Jahr noch?",
                ],
                antworten=[
                    numerical_finanz_geld(rk),
                    numerical_finanz_geld(zinsen_pause),
                    numerical_finanz_geld(a_neu),
                    numerical_finanz_laufzeit(n_rest),
                ],
            )

        sonder = schoen(rk * rng.choice((0.2, 0.25, 0.3, 0.4, 0.5)), sz.stufe)
        if sonder <= 0 or sonder >= rk:
            return None
        rk_neu = rk - sonder
        a_neu = annuitaet(rk_neu, q, n - k)
        n_rest = annuitaet_n(rk_neu, a, q)
        if n_rest is None or n_rest < 1.0:
            return None
        intro = basis + f" Zusammen mit der {k}. Annuität leistet {sz.pron} eine Sondertilgung von {geld(sonder)}."
        return Task(
            einleitung=intro,
            fragen=[
                f"Wie hoch ist die Restschuld nach {k} Jahren vor der Sondertilgung?",
                "Wie hoch ist die Restschuld nach der Sondertilgung?",
                f"Die Gesamtlaufzeit von {n} Jahren soll unverändert bleiben. Wie hoch ist die neue Annuität für die verbleibenden {n - k} Jahre?",
                "Stattdessen bleibt die Annuität unverändert. Wie viele Jahre dauert die Rückzahlung ab der Sondertilgung noch?",
            ],
            antworten=[
                numerical_finanz_geld(rk),
                numerical_finanz_geld(rk_neu),
                numerical_finanz_geld(a_neu),
                numerical_finanz_laufzeit(n_rest),
            ],
        )
