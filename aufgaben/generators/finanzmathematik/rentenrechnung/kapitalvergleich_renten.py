"""Check 07 – Kapitalvergleich mit Einmalzahlungen und Renten (Barwerte, Entscheidung per MC)."""

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
    rentenbarwert,
    sample_kapital,
    sample_zinssatz,
    schoen,
)
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge


class KapitalvergleichRentenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.rentenrechnung.kapitalvergleich_renten"

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

        # A: sofort
        text_a = f"{geld(basis)} sofort"
        barwert_a = basis

        # B: Anzahlung + Einmalzahlung später
        ziel_b = basis * rng.uniform(0.94, 1.06)
        anteil_b = rng.choice((0.3, 0.4, 0.5))
        k_b = rng.randint(2, 6)
        b1 = schoen(ziel_b * anteil_b, stufe)
        b2 = schoen((ziel_b - b1) * q**k_b, stufe)
        if b2 <= 0:
            return None
        text_b = f"{geld(b1)} sofort und {geld(b2)} in {jahren(k_b)}"
        barwert_b = b1 + b2 / q**k_b

        # C: Rente (sofort beginnend vorschüssig, nachschüssig ab Ende des 1. Jahres oder aufgeschoben)
        ziel_c = basis * rng.uniform(0.94, 1.06)
        n_c = rng.randint(3, 10)
        variante = rng.choice(("nach", "vor", "aufgeschoben"))
        if variante == "aufgeschoben":
            k_c = rng.randint(2, 4)
            faktor = rentenbarwert(1.0, q, n_c, False) / q**k_c
            r_c = schoen(ziel_c / faktor, stufe)
            barwert_c = r_c * faktor
            text_c = (
                f"{n_c} Jahreszahlungen von je {geld(r_c)}, die erste Zahlung am Ende des {k_c + 1}. Jahres"
            )
        else:
            vor = variante == "vor"
            faktor = rentenbarwert(1.0, q, n_c, vor)
            r_c = schoen(ziel_c / faktor, stufe)
            barwert_c = r_c * faktor
            text_c = (
                f"{n_c} Jahreszahlungen von je {geld(r_c)}, "
                + ("die erste Zahlung sofort" if vor else "die erste Zahlung in einem Jahr")
            )
        if r_c <= 0:
            return None

        barwerte = [barwert_a, barwert_b, barwert_c]
        mindestabstand = max(0.01 * basis, 3 * finanz_geld_tolerance_for(basis))
        sortiert = sorted(barwerte)
        if any(sortiert[i + 1] - sortiert[i] < mindestabstand for i in range(2)):
            return None

        bestes = barwerte.index(max(barwerte) if verkauf else min(barwerte))
        labels = ["Angebot A", "Angebot B", "Angebot C"]

        if verkauf:
            kopf = f"{sz.subjekt} verkauft {sz.verkauf_akk}. Drei Interessenten machen folgende Angebote:<br>"
            entscheidung = f"Für welches Angebot sollte sich {sz.subjekt} aus finanzmathematischer Sicht entscheiden?"
        else:
            kopf = f"{sz.subjekt} kauft {sz.kauf_akk}. Der Verkäufer bietet drei Zahlungsvarianten an:<br>"
            entscheidung = f"Welche Zahlungsvariante ist für {sz.subjekt} aus finanzmathematischer Sicht am günstigsten?"

        intro = (
            kopf
            + f"Angebot A: {text_a}.<br>"
            + f"Angebot B: {text_b}.<br>"
            + f"Angebot C: {text_c}.<br>"
            + f"Für den Vergleich wird ein Zinssatz von {prozent(p)} zugrunde gelegt."
        )

        return Task(
            einleitung=intro,
            fragen=[
                "Bestimmen Sie den Barwert von Angebot B.",
                "Bestimmen Sie den Barwert von Angebot C.",
                entscheidung,
            ],
            antworten=[
                numerical_finanz_geld(barwert_b),
                numerical_finanz_geld(barwert_c),
                mc(labels, bestes),
            ],
        )
