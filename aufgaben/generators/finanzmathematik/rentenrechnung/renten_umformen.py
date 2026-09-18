"""Checks 01/02 – Rentenendwert- und Rentenbarwertformel umformen (innermathematisch, drei Teilfragen)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_finanz_geld, numerical_finanz_laufzeit
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    STUFEN,
    Stufe,
    g_geld,
    g_n,
    g_prozent,
    q_of,
    rente_n_aus_barwert,
    rente_n_aus_endwert,
    rentenart,
    rentenbarwert,
    rentenendwert,
    renten_faktor,
    sample_rate,
    sample_zinssatz,
    schoen,
)

_INTRO_END = (
    "Eine Rente besteht aus $n$ gleich hohen jährlichen Zahlungen $r$, die mit dem Zinssatz $p$ verzinst werden. "
    "Der Rentenendwert ist nachschüssig $R_n = \\frac{r \\cdot (q^n - 1)}{q - 1}$ und vorschüssig "
    "$\\overline{R}_n = \\frac{r \\cdot q \\cdot (q^n - 1)}{q - 1}$. "
    "Bestimmen Sie jeweils die gesuchte Größe."
)
_INTRO_BAR = (
    "Eine Rente besteht aus $n$ gleich hohen jährlichen Zahlungen $r$, die mit dem Zinssatz $p$ verzinst werden. "
    "Der Rentenbarwert ist nachschüssig $R_0 = \\frac{r \\cdot (q^n - 1)}{q^n \\cdot (q - 1)}$ und vorschüssig "
    "$\\overline{R}_0 = \\frac{r \\cdot q \\cdot (q^n - 1)}{q^n \\cdot (q - 1)}$. "
    "Bestimmen Sie jeweils die gesuchte Größe."
)


def _symbol(barwert: bool, vor: bool) -> str:
    index = "0" if barwert else "n"
    return f"\\overline{{R}}_{index}" if vor else f"R_{index}"


def _teilfragen(rng: random.Random, stufe: Stufe, barwert: bool) -> tuple[list[str], list[str]]:
    fragen: list[str] = []
    antworten: list[str] = []
    wert = rentenbarwert if barwert else rentenendwert

    # a) Wert gesucht
    vor = rng.random() < 0.5
    r, p, n = sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(4, 25)
    fragen.append(
        f"Gegeben: {rentenart(vor)} Rente mit {g_geld('r', r)}, {g_prozent(p)}, {g_n(n)}. Gesucht: ${_symbol(barwert, vor)}$."
    )
    antworten.append(numerical_finanz_geld(wert(r, q_of(p), n, vor)))

    # b) r gesucht
    vor = rng.random() < 0.5
    r, p, n = sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(4, 25)
    q = q_of(p)
    ziel = schoen(wert(r, q, n, vor), stufe)
    faktor = renten_faktor(q, n, vor) / (q**n if barwert else 1.0)
    fragen.append(
        f"Gegeben: {rentenart(vor)} Rente mit {g_geld(_symbol(barwert, vor), ziel)}, {g_prozent(p)}, {g_n(n)}. Gesucht: $r$."
    )
    antworten.append(numerical_finanz_geld(ziel / faktor))

    # c) n gesucht
    while True:
        vor = rng.random() < 0.5
        r, p, n = sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(4, 25)
        q = q_of(p)
        ziel = schoen(wert(r, q, n, vor), stufe)
        n_antwort = rente_n_aus_barwert(r, ziel, q, vor) if barwert else rente_n_aus_endwert(r, ziel, q, vor)
        if n_antwort is not None and n_antwort > 1.0:
            break
    fragen.append(
        f"Gegeben: {rentenart(vor)} Rente mit {g_geld('r', r)}, {g_geld(_symbol(barwert, vor), ziel)}, {g_prozent(p)}. Gesucht: $n$ (in Jahren)."
    )
    antworten.append(numerical_finanz_laufzeit(n_antwort))

    return fragen, antworten


class RentenendwertUmformenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.rentenrechnung.rentenendwert_umformen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        stufen = list(STUFEN.values())
        tasks: list[Task] = []
        for index in range(count):
            fragen, antworten = _teilfragen(rng, stufen[index % len(stufen)], barwert=False)
            tasks.append(Task(einleitung=_INTRO_END, fragen=fragen, antworten=antworten))
        return tasks


class RentenbarwertUmformenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.rentenrechnung.rentenbarwert_umformen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        stufen = list(STUFEN.values())
        tasks: list[Task] = []
        for index in range(count):
            fragen, antworten = _teilfragen(rng, stufen[index % len(stufen)], barwert=True)
            tasks.append(Task(einleitung=_INTRO_BAR, fragen=fragen, antworten=antworten))
        return tasks
