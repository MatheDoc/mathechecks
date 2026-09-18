"""Check 02 – Annuitätenformeln umformen (innermathematisch, drei Teilfragen: A, K_0, n)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_finanz_geld, numerical_finanz_laufzeit
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    STUFEN,
    annuitaet,
    annuitaet_k0,
    annuitaet_n,
    g_geld,
    g_n,
    g_prozent,
    q_of,
    sample_darlehen,
    sample_zinssatz,
    schoen,
)

_INTRO = (
    "Ein Darlehen $K_0$ wird bei einem Zinssatz $p$ durch Annuitätentilgung mit der jährlichen Annuität $A$ "
    "in $n$ Jahren zurückgezahlt. Es gilt $A = \\frac{K_0 \\cdot q^n \\cdot (q-1)}{q^n - 1}$ und $A = T_1 \\cdot q^n$ "
    "mit der Tilgung $T_1$ des ersten Jahres. Bestimmen Sie jeweils die gesuchte Größe."
)


class AnnuitaetenformelnUmformenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.tilgungsrechnung.annuitaetenformeln_umformen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        stufen = list(STUFEN.values())
        tasks: list[Task] = []

        for index in range(count):
            stufe = stufen[index % len(stufen)]
            fragen: list[str] = []
            antworten: list[str] = []

            # a) A gesucht
            k0, p, n = sample_darlehen(rng, stufe), sample_zinssatz(rng), rng.randint(4, 30)
            fragen.append(f"Gegeben: {g_geld('K_0', k0)}, {g_prozent(p)}, {g_n(n)}. Gesucht: $A$.")
            antworten.append(numerical_finanz_geld(annuitaet(k0, q_of(p), n)))

            # b) K_0 gesucht
            k0, p, n = sample_darlehen(rng, stufe), sample_zinssatz(rng), rng.randint(4, 30)
            a = schoen(annuitaet(k0, q_of(p), n), stufe)
            fragen.append(f"Gegeben: {g_geld('A', a)}, {g_prozent(p)}, {g_n(n)}. Gesucht: $K_0$.")
            antworten.append(numerical_finanz_geld(annuitaet_k0(a, q_of(p), n)))

            # c) n gesucht
            while True:
                k0, p, n = sample_darlehen(rng, stufe), sample_zinssatz(rng), rng.randint(4, 30)
                a = schoen(annuitaet(k0, q_of(p), n), stufe)
                n_antwort = annuitaet_n(k0, a, q_of(p))
                if n_antwort is not None and n_antwort > 1.0:
                    break
            fragen.append(f"Gegeben: {g_geld('K_0', k0)}, {g_geld('A', a)}, {g_prozent(p)}. Gesucht: $n$ (in Jahren).")
            antworten.append(numerical_finanz_laufzeit(n_antwort))

            tasks.append(Task(einleitung=_INTRO, fragen=fragen, antworten=antworten))

        return tasks
