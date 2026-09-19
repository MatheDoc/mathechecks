"""Check 05 – Kapitalauf- und -abbau umformen (innermathematisch, vier Teilfragen)."""

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
    kapital_en,
    kapital_n,
    q_of,
    rentenart,
    renten_faktor,
    sample_kapital,
    sample_rate,
    sample_zinssatz,
    schoen,
)

_INTRO = (
    "Ein Startkapital $K_0$ wird $n$ Jahre lang mit dem Zinssatz $p$ verzinst. Zusätzlich werden jährlich "
    "gleich hohe Beträge $r$ eingezahlt (Kapitalaufbau) oder entnommen (Kapitalabbau). Das Endkapital ist "
    "$E_n = K_0 \\cdot q^n \\pm R_n$ bzw. $\\overline{E}_n = K_0 \\cdot q^n \\pm \\overline{R}_n$. "
    "Bestimmen Sie jeweils die gesuchte Größe."
)


def _art(aufbau: bool, vor: bool) -> str:
    return f"Kapital{'aufbau' if aufbau else 'abbau'} mit {rentenart(vor)}n Zahlungen"


def _e_symbol(vor: bool) -> str:
    return "\\overline{E}_n" if vor else "E_n"


def _teilfragen(rng: random.Random, stufe: Stufe) -> tuple[list[str], list[str]]:
    fragen: list[str] = []
    antworten: list[str] = []

    # a) E_n gesucht
    while True:
        aufbau, vor = rng.random() < 0.5, rng.random() < 0.5
        k0, r, p, n = sample_kapital(rng, stufe), sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(3, 20)
        en = kapital_en(k0, r, q_of(p), n, vor, aufbau)
        if en > 0:
            break
    fragen.append(
        f"{_art(aufbau, vor)}. Gegeben: {g_geld('K_0', k0)}, {g_geld('r', r)}, {g_prozent(p)}, {g_n(n)}. Gesucht: ${_e_symbol(vor)}$."
    )
    antworten.append(numerical_finanz_geld(en))

    # b) K_0 gesucht
    while True:
        aufbau, vor = rng.random() < 0.5, rng.random() < 0.5
        k0, r, p, n = sample_kapital(rng, stufe), sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(3, 20)
        q = q_of(p)
        en = kapital_en(k0, r, q, n, vor, aufbau)
        if en > 0:
            break
    en = schoen(en, stufe)
    rn = r * renten_faktor(q, n, vor)
    k0_antwort = (en - rn) / q**n if aufbau else (en + rn) / q**n
    fragen.append(
        f"{_art(aufbau, vor)}. Gegeben: {g_geld(_e_symbol(vor), en)}, {g_geld('r', r)}, {g_prozent(p)}, {g_n(n)}. Gesucht: $K_0$."
    )
    antworten.append(numerical_finanz_geld(k0_antwort))

    # c) r gesucht
    while True:
        aufbau, vor = rng.random() < 0.5, rng.random() < 0.5
        k0, r, p, n = sample_kapital(rng, stufe), sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(3, 20)
        q = q_of(p)
        en = kapital_en(k0, r, q, n, vor, aufbau)
        if en > 0:
            break
    en = schoen(en, stufe)
    faktor = renten_faktor(q, n, vor)
    r_antwort = (en - k0 * q**n) / faktor if aufbau else (k0 * q**n - en) / faktor
    fragen.append(
        f"{_art(aufbau, vor)}. Gegeben: {g_geld('K_0', k0)}, {g_geld(_e_symbol(vor), en)}, {g_prozent(p)}, {g_n(n)}. Gesucht: $r$."
    )
    antworten.append(numerical_finanz_geld(r_antwort))

    # d) n gesucht
    while True:
        aufbau, vor = rng.random() < 0.5, rng.random() < 0.5
        k0, r, p, n = sample_kapital(rng, stufe), sample_rate(rng, stufe), sample_zinssatz(rng), rng.randint(3, 20)
        q = q_of(p)
        en = kapital_en(k0, r, q, n, vor, aufbau)
        if en <= 0:
            continue
        en = schoen(en, stufe)
        n_antwort = kapital_n(k0, r, q, en, vor, aufbau)
        if n_antwort is not None and n_antwort > 1.0:
            break
    fragen.append(
        f"{_art(aufbau, vor)}. Gegeben: {g_geld('K_0', k0)}, {g_geld('r', r)}, {g_geld(_e_symbol(vor), en)}, {g_prozent(p)}. Gesucht: $n$ (in Jahren)."
    )
    antworten.append(numerical_finanz_laufzeit(n_antwort))

    return fragen, antworten


class KapitalaufbauAbbauUmformenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.rentenrechnung.kapitalaufbau_abbau_umformen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        stufen = list(STUFEN.values())
        tasks: list[Task] = []
        for index in range(count):
            fragen, antworten = _teilfragen(rng, stufen[index % len(stufen)])
            tasks.append(Task(einleitung=_INTRO, fragen=fragen, antworten=antworten))
        return tasks
