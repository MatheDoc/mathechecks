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
        varianten = ("sonder_annuitaet", "pause", "sonder_laufzeit")
        for index, sz in enumerate(szenario_folge(rng, count)):
            variante = varianten[index % len(varianten)]
            task = None
            while task is None:
                task = self._build(rng, sz, variante)
            tasks.append(task)
        return tasks

    def _build(self, rng: random.Random, sz: Szenario, variante: str) -> Task | None:
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

        if variante == "pause":
            zinsen_pause = rk * (q - 1.0)
            a_neu = annuitaet(rk, q, n - k - 1)
            intro = (
                basis
                + f" Im {k + 1}. Jahr setzt {sz.pron} die Tilgung aus und zahlt nur die Zinsen. "
                f"Die Gesamtlaufzeit bleibt unverändert."
            )
            return Task(
                einleitung=intro,
                fragen=[
                    f"Wie hoch ist die Restschuld nach {k} Jahren?",
                    f"Welche Zahlung ist im {k + 1}. Jahr zu leisten?",
                    f"Wie hoch ist die Restschuld am Ende des {k + 1}. Jahres?",
                    f"Wie hoch ist die Annuität für die verbleibenden {n - k - 1} Jahre?",
                ],
                antworten=[
                    numerical_finanz_geld(rk),
                    numerical_finanz_geld(zinsen_pause),
                    numerical_finanz_geld(rk),
                    numerical_finanz_geld(a_neu),
                ],
            )

        sonder = schoen(rk * rng.choice((0.2, 0.25, 0.3, 0.4, 0.5)), sz.stufe)
        if sonder <= 0 or sonder >= rk:
            return None
        rk_neu = rk - sonder
        intro = (
            basis
            + f" Zusammen mit der {k}. Annuität leistet {sz.pron} eine Sondertilgung von {geld(sonder)}."
        )

        if variante == "sonder_annuitaet":
            a_neu = annuitaet(rk_neu, q, n - k)
            return Task(
                einleitung=intro + " Die Gesamtlaufzeit bleibt unverändert.",
                fragen=[
                    f"Wie hoch ist die Restschuld nach {k} Jahren vor der Sondertilgung?",
                    "Wie hoch ist die Restschuld nach der Sondertilgung?",
                    f"Wie hoch ist die neue Annuität für die verbleibenden {n - k} Jahre?",
                ],
                antworten=[
                    numerical_finanz_geld(rk),
                    numerical_finanz_geld(rk_neu),
                    numerical_finanz_geld(a_neu),
                ],
            )

        # sonder_laufzeit: Annuität bleibt, Restlaufzeit verkürzt sich
        n_rest = annuitaet_n(rk_neu, a, q)
        if n_rest is None or n_rest < 1.0:
            return None
        return Task(
            einleitung=intro + " Die Annuität bleibt unverändert.",
            fragen=[
                f"Wie hoch ist die Restschuld nach {k} Jahren vor der Sondertilgung?",
                "Wie hoch ist die Restschuld nach der Sondertilgung?",
                "Wie viele Jahre dauert die Rückzahlung ab der Sondertilgung noch?",
                "Um wie viele Jahre verkürzt sich die Laufzeit gegenüber dem ursprünglichen Plan?",
            ],
            antworten=[
                numerical_finanz_geld(rk),
                numerical_finanz_geld(rk_neu),
                numerical_finanz_laufzeit(n_rest),
                numerical_finanz_laufzeit((n - k) - n_rest),
            ],
        )
