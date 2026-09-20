"""Check 03 – Zinssatzwechsel mit zwei Zinsphasen.

Sechs Größen K_0, K_n (n = n_1 + n_2), p_1, p_2, n_1, n_2; fünf gegeben, eine gesucht.
Teilfrage 1 fragt stets nach dem Zwischenwert K_{n_1} (vorwärts aus K_0 oder rückwärts aus K_n),
Teilfrage 2 nach der gesuchten Größe.
"""

from __future__ import annotations

import math
import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import (
    numerical_finanz_geld,
    numerical_finanz_laufzeit,
    numerical_finanz_zinssatz,
)
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    geld,
    p_of,
    prozent,
    q_of,
    sample_kapital,
    sample_zinssatz,
    schoen,
)
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge

_TYPEN = ("kn", "k0", "p1", "p2", "n1", "n2")
_Q_ZWISCHEN = "Wie hoch ist das Guthaben am Ende der ersten Zinsphase?"


class ZinssatzwechselGenerator(TaskGenerator):
    generator_key = "finanzmathematik.zinseszinsrechnung.zinssatzwechsel"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        for index, sz in enumerate(szenario_folge(rng, count)):
            typ = _TYPEN[index % len(_TYPEN)]
            task = None
            while task is None:
                task = self._build(rng, sz, typ)
            tasks.append(task)
        return tasks

    def _build(self, rng: random.Random, sz: Szenario, typ: str) -> Task | None:
        stufe = sz.stufe
        k0 = sample_kapital(rng, stufe)
        p1 = sample_zinssatz(rng)
        p2 = sample_zinssatz(rng, ohne=p1)
        n1 = rng.randint(2, 8)
        n2 = rng.choice([n for n in range(2, 9) if n != n1])
        q1, q2 = q_of(p1), q_of(p2)
        gesamt = n1 + n2
        S, pron, zweck = sz.subjekt, sz.pron, sz.zweck_anlage

        if typ == "kn":
            k1 = k0 * q1**n1
            intro = (
                f"{S} legt {geld(k0)} {zweck} an. In den ersten {n1} Jahren wird das Kapital mit {prozent(p1)} "
                f"verzinst, anschließend {n2} Jahre lang mit {prozent(p2)}."
            )
            return Task(
                einleitung=intro,
                fragen=[_Q_ZWISCHEN, f"Über welchen Betrag kann {pron} nach insgesamt {gesamt} Jahren verfügen?"],
                antworten=[numerical_finanz_geld(k1), numerical_finanz_geld(k1 * q2**n2)],
            )

        kn = schoen(k0 * q1**n1 * q2**n2, stufe)

        if typ == "k0":
            k1 = kn / q2**n2
            intro = (
                f"{S} hat vor {gesamt} Jahren einen Betrag {zweck} angelegt. In den ersten {n1} Jahren wurde das "
                f"Kapital mit {prozent(p1)} verzinst, anschließend {n2} Jahre lang mit {prozent(p2)}. "
                f"Heute beträgt das Guthaben {geld(kn)}."
            )
            return Task(
                einleitung=intro,
                fragen=["Wie hoch war das Guthaben am Ende der ersten Zinsphase?", "Welcher Betrag wurde ursprünglich angelegt?"],
                antworten=[numerical_finanz_geld(k1), numerical_finanz_geld(k1 / q1**n1)],
            )

        if typ == "p1":
            k1 = kn / q2**n2
            if k1 <= k0:
                return None
            intro = (
                f"{S} legt {geld(k0)} {zweck} an. In den ersten {n1} Jahren wird das Kapital mit einem zunächst "
                f"unbekannten Zinssatz verzinst, anschließend {n2} Jahre lang mit {prozent(p2)}. "
                f"Nach insgesamt {gesamt} Jahren beträgt das Guthaben {geld(kn)}."
            )
            return Task(
                einleitung=intro,
                fragen=[_Q_ZWISCHEN, "Mit welchem Zinssatz wurde das Kapital in der ersten Zinsphase verzinst?"],
                antworten=[numerical_finanz_geld(k1), numerical_finanz_zinssatz(p_of((k1 / k0) ** (1.0 / n1)))],
            )

        if typ == "p2":
            k1 = k0 * q1**n1
            if kn <= k1:
                return None
            intro = (
                f"{S} legt {geld(k0)} {zweck} an. In den ersten {n1} Jahren wird das Kapital mit {prozent(p1)} "
                f"verzinst, anschließend {n2} Jahre lang mit einem anderen Zinssatz. "
                f"Nach insgesamt {gesamt} Jahren beträgt das Guthaben {geld(kn)}."
            )
            return Task(
                einleitung=intro,
                fragen=[_Q_ZWISCHEN, "Mit welchem Zinssatz wurde das Kapital in der zweiten Zinsphase verzinst?"],
                antworten=[numerical_finanz_geld(k1), numerical_finanz_zinssatz(p_of((kn / k1) ** (1.0 / n2)))],
            )

        if typ == "n1":
            k1 = kn / q2**n2
            if k1 <= k0:
                return None
            n1_antwort = math.log(k1 / k0) / math.log(q1)
            if n1_antwort < 1.0:
                return None
            intro = (
                f"{S} legt {geld(k0)} {zweck} an. Zunächst wird das Kapital mit {prozent(p1)} verzinst, "
                f"anschließend {n2} Jahre lang mit {prozent(p2)}. Am Ende beträgt das Guthaben {geld(kn)}."
            )
            return Task(
                einleitung=intro,
                fragen=[_Q_ZWISCHEN, "Wie viele Jahre dauerte die erste Zinsphase?"],
                antworten=[numerical_finanz_geld(k1), numerical_finanz_laufzeit(n1_antwort)],
            )

        # typ == "n2"
        k1 = k0 * q1**n1
        if kn <= k1:
            return None
        n2_antwort = math.log(kn / k1) / math.log(q2)
        if n2_antwort < 1.0:
            return None
        intro = (
            f"{S} legt {geld(k0)} {zweck} an. In den ersten {n1} Jahren wird das Kapital mit {prozent(p1)} "
            f"verzinst, danach mit {prozent(p2)}, bis das Guthaben {geld(kn)} erreicht hat."
        )
        return Task(
            einleitung=intro,
            fragen=[_Q_ZWISCHEN, "Wie viele Jahre dauert die zweite Zinsphase?"],
            antworten=[numerical_finanz_geld(k1), numerical_finanz_laufzeit(n2_antwort)],
        )
