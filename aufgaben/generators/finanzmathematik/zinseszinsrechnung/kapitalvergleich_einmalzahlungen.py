"""Check 04 – Kapitalvergleich mit Einmalzahlungen (Barwerte, Entscheidung per MC)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical_finanz_geld
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    finanz_geld_tolerance_for,
    geld,
    jahren,
    prozent,
    q_of,
    sample_kapital,
    sample_zinssatz,
    schoen,
)
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge


def _barwert(zahlungen: list[tuple[float, int]], q: float) -> float:
    return sum(betrag / q**k for betrag, k in zahlungen)


def _angebot_text(zahlungen: list[tuple[float, int]]) -> str:
    teile = []
    for betrag, k in zahlungen:
        teile.append(f"{geld(betrag)} sofort" if k == 0 else f"{geld(betrag)} in {jahren(k)}")
    if len(teile) == 1:
        return teile[0]
    return ", ".join(teile[:-1]) + " und " + teile[-1]


class KapitalvergleichEinmalzahlungenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.zinseszinsrechnung.kapitalvergleich_einmalzahlungen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        for index, sz in enumerate(szenario_folge(rng, count)):
            verkauf = index % 2 == 0
            task = None
            while task is None:
                task = self._build(rng, sz, verkauf)
            tasks.append(task)
        return tasks

    def _build(self, rng: random.Random, sz: Szenario, verkauf: bool) -> Task | None:
        stufe = sz.stufe
        p = sample_zinssatz(rng)
        q = q_of(p)
        basis = sample_kapital(rng, stufe)

        # Angebot A: sofort. B: Anzahlung + Rest später. C: eine oder zwei spätere Zahlungen.
        a = [(basis, 0)]
        ziel_b = basis * rng.uniform(0.94, 1.06)
        anteil_b = rng.choice((0.25, 0.3, 0.4, 0.5))
        k_b = rng.randint(2, 6)
        b1 = schoen(ziel_b * anteil_b, stufe)
        b2 = schoen((ziel_b - b1) * q**k_b, stufe)
        b = [(b1, 0), (b2, k_b)]

        ziel_c = basis * rng.uniform(0.94, 1.06)
        if rng.random() < 0.5:
            k_c = rng.randint(2, 7)
            c = [(schoen(ziel_c * q**k_c, stufe), k_c)]
        else:
            k_c1 = rng.randint(1, 3)
            k_c2 = k_c1 + rng.randint(2, 5)
            anteil_c = rng.choice((0.4, 0.5, 0.6))
            c1 = schoen(ziel_c * anteil_c * q**k_c1, stufe)
            c2 = schoen((ziel_c - c1 / q**k_c1) * q**k_c2, stufe)
            c = [(c1, k_c1), (c2, k_c2)]

        if any(betrag <= 0 for angebot in (b, c) for betrag, _ in angebot):
            return None

        barwerte = [_barwert(a, q), _barwert(b, q), _barwert(c, q)]
        mindestabstand = max(0.01 * basis, 3 * finanz_geld_tolerance_for(basis))
        sortiert = sorted(barwerte)
        if any(sortiert[i + 1] - sortiert[i] < mindestabstand for i in range(2)):
            return None

        bestes = barwerte.index(max(barwerte) if verkauf else min(barwerte))
        labels = ("Angebot A", "Angebot B", "Angebot C")

        if verkauf:
            intro = (
                f"{sz.subjekt} verkauft {sz.verkauf_akk}. Drei Interessenten machen folgende Angebote:<br>"
                f"Angebot A: {_angebot_text(a)}.<br>"
                f"Angebot B: {_angebot_text(b)}.<br>"
                f"Angebot C: {_angebot_text(c)}.<br>"
                f"Für den Vergleich wird ein Zinssatz von {prozent(p)} zugrunde gelegt."
            )
            entscheidung = f"Für welches Angebot sollte sich {sz.subjekt} aus finanzmathematischer Sicht entscheiden?"
        else:
            intro = (
                f"{sz.subjekt} kauft {sz.kauf_akk}. Der Verkäufer bietet drei Zahlungsvarianten an:<br>"
                f"Angebot A: {_angebot_text(a)}.<br>"
                f"Angebot B: {_angebot_text(b)}.<br>"
                f"Angebot C: {_angebot_text(c)}.<br>"
                f"Für den Vergleich wird ein Zinssatz von {prozent(p)} zugrunde gelegt."
            )
            entscheidung = f"Welche Zahlungsvariante ist für {sz.subjekt} aus finanzmathematischer Sicht am günstigsten?"

        return Task(
            einleitung=intro,
            fragen=[
                "Bestimmen Sie den Barwert von Angebot B.",
                "Bestimmen Sie den Barwert von Angebot C.",
                entscheidung,
            ],
            antworten=[
                numerical_finanz_geld(barwerte[1]),
                numerical_finanz_geld(barwerte[2]),
                mc(list(labels), bestes),
            ],
        )
