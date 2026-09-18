"""Check 01 – Zinseszinsformel umformen (innermathematisch, vier Teilfragen)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import (
    numerical_finanz_geld,
    numerical_finanz_laufzeit,
    numerical_finanz_zinssatz,
)
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    STUFEN,
    g_geld,
    g_n,
    g_prozent,
    q_of,
    sample_kapital,
    sample_laufzeit,
    sample_zinssatz,
    schoen,
    zinseszins_k0,
    zinseszins_kn,
    zinseszins_n,
    zinseszins_p,
)

_INTRO = (
    "Ein Kapital $K_0$ wird $n$ Jahre lang jährlich mit dem Zinssatz $p$ verzinst. "
    "Die Zinsen verbleiben auf dem Konto. Es gilt $K_n = K_0 \\cdot q^n$ mit $q = 1 + \\frac{p}{100}$."
)


class ZinseszinsformelUmformenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.zinseszinsrechnung.zinseszinsformel_umformen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        stufen = list(STUFEN.values())
        tasks: list[Task] = []

        for index in range(count):
            stufe = stufen[index % len(stufen)]
            fragen: list[str] = []
            antworten: list[str] = []

            # a) K_n gesucht
            k0 = sample_kapital(rng, stufe)
            p = sample_zinssatz(rng)
            n = sample_laufzeit(rng)
            kn = zinseszins_kn(k0, q_of(p), n)
            fragen.append(
                f"Gegeben: {g_geld('K_0', k0)}, {g_prozent(p)}, {g_n(n)}. Gesucht: $K_n$."
            )
            antworten.append(numerical_finanz_geld(kn))

            # b) K_0 gesucht
            k0 = sample_kapital(rng, stufe)
            p = sample_zinssatz(rng)
            n = sample_laufzeit(rng)
            kn = schoen(zinseszins_kn(k0, q_of(p), n), stufe)
            fragen.append(
                f"Gegeben: {g_geld('K_n', kn)}, {g_prozent(p)}, {g_n(n)}. Gesucht: $K_0$."
            )
            antworten.append(numerical_finanz_geld(zinseszins_k0(kn, q_of(p), n)))

            # c) p gesucht
            k0 = sample_kapital(rng, stufe)
            p = sample_zinssatz(rng)
            n = sample_laufzeit(rng)
            kn = schoen(zinseszins_kn(k0, q_of(p), n), stufe)
            fragen.append(
                f"Gegeben: {g_geld('K_0', k0)}, {g_geld('K_n', kn)}, {g_n(n)}. Gesucht: $p$ (in %)."
            )
            antworten.append(numerical_finanz_zinssatz(zinseszins_p(k0, kn, n)))

            # d) n gesucht
            k0 = sample_kapital(rng, stufe)
            p = sample_zinssatz(rng)
            n = sample_laufzeit(rng)
            kn = schoen(zinseszins_kn(k0, q_of(p), n), stufe)
            fragen.append(
                f"Gegeben: {g_geld('K_0', k0)}, {g_geld('K_n', kn)}, {g_prozent(p)}. Gesucht: $n$ (in Jahren)."
            )
            antworten.append(numerical_finanz_laufzeit(zinseszins_n(k0, kn, q_of(p))))

            tasks.append(Task(einleitung=_INTRO, fragen=fragen, antworten=antworten))

        return tasks
