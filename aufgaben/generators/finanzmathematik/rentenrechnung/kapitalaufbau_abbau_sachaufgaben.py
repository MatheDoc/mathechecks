"""Check 06 – Kapitalauf- und -abbau im Sachkontext (vier Teilfragen, zufällige Reihenfolge)."""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_finanz_geld, numerical_finanz_laufzeit
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.finanzmathematik.shared import (
    geld,
    kapital_en,
    kapital_n,
    mische_teilfragen,
    prozent,
    q_of,
    renten_faktor,
    sample_kapital,
    sample_rate,
    sample_zinssatz,
    schoen,
    zeitpunkt_phrase,
)
from aufgaben.generators.finanzmathematik.szenarien import Szenario, szenario_folge

_T_EN_AUF = (
    "{S} hat bereits {k0} angespart und zahlt weitere {n} Jahre lang {zp} {r} auf dasselbe Konto ein. Das Guthaben wird mit {p} verzinst. Wie hoch ist es am Ende der Laufzeit?",
)
_T_EN_AB = (
    "{S} verfügt über {k0}, die zu {p} angelegt sind, und entnimmt {n} Jahre lang {zp} {r}. Welcher Betrag ist danach noch vorhanden?",
)
_T_K0_AUF = (
    "{S} möchte in {n} Jahren über {en} verfügen und wird dafür {zp} {r} einzahlen ({p}). Welcher Betrag muss zusätzlich heute einmalig angelegt werden?",
)
_T_K0_AB = (
    "{S} möchte {n} Jahre lang {zp} {r} entnehmen und am Ende noch über {en} verfügen. Welcher Betrag muss dafür heute zu {p} angelegt werden?",
)
_T_R_AUF = (
    "{S} legt heute {k0} zu {p} an und möchte in {n} Jahren über {en} verfügen. Welcher Betrag muss dafür zusätzlich {zp} eingezahlt werden?",
)
_T_R_AB = (
    "{S} hat {k0} zu {p} angelegt. Nach {n} Jahren soll noch ein Restbetrag von {en} vorhanden sein. Welchen Betrag kann {pron} {zp} entnehmen?",
)
_T_N_AB = (
    "{S} hat {k0} zu {p} angelegt und entnimmt {zp} {r}. Nach wie vielen Jahren ist das Kapital vollständig aufgebraucht?",
    "{S} hat {k0} zu {p} angelegt und entnimmt {zp} {r}. Nach wie vielen Jahren ist das Guthaben auf {en} gesunken?",
)
_T_N_AUF = (
    "{S} hat {k0} zu {p} angelegt und zahlt zusätzlich {zp} {r} ein. Nach wie vielen Jahren ist ein Guthaben von {en} erreicht?",
)


def _fill(template: str, sz: Szenario, **werte) -> str:
    return template.format(S=sz.subjekt, pron=sz.pron, **werte)


class KapitalaufbauAbbauSachaufgabenGenerator(TaskGenerator):
    generator_key = "finanzmathematik.rentenrechnung.kapitalaufbau_abbau_sachaufgaben"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for sz in szenario_folge(rng, count):
            stufe = sz.stufe
            paare: list[tuple[str, str]] = []

            def sample() -> tuple[float, float, float, int, bool]:
                return (
                    sample_kapital(rng, stufe),
                    sample_rate(rng, stufe),
                    sample_zinssatz(rng),
                    rng.randint(3, 20),
                    rng.random() < 0.5,
                )

            # E_n gesucht
            while True:
                k0, r, p, n, vor = sample()
                aufbau = rng.random() < 0.5
                en = kapital_en(k0, r, q_of(p), n, vor, aufbau)
                if en > 0:
                    break
            paare.append((
                _fill(rng.choice(_T_EN_AUF if aufbau else _T_EN_AB), sz, k0=geld(k0), n=n, zp=zeitpunkt_phrase(rng, vor), r=geld(r), p=prozent(p)),
                numerical_finanz_geld(en),
            ))

            # K_0 gesucht
            while True:
                k0, r, p, n, vor = sample()
                aufbau = rng.random() < 0.5
                q = q_of(p)
                en = kapital_en(k0, r, q, n, vor, aufbau)
                if en <= 0:
                    continue
                en = schoen(en, stufe)
                rn = r * renten_faktor(q, n, vor)
                k0_antwort = (en - rn) / q**n if aufbau else (en + rn) / q**n
                if k0_antwort > 0:
                    break
            paare.append((
                _fill(rng.choice(_T_K0_AUF if aufbau else _T_K0_AB), sz, n=n, en=geld(en), zp=zeitpunkt_phrase(rng, vor), r=geld(r), p=prozent(p)),
                numerical_finanz_geld(k0_antwort),
            ))

            # r gesucht
            while True:
                k0, r, p, n, vor = sample()
                aufbau = rng.random() < 0.5
                q = q_of(p)
                en = kapital_en(k0, r, q, n, vor, aufbau)
                if en <= 0:
                    continue
                en = schoen(en, stufe)
                faktor = renten_faktor(q, n, vor)
                r_antwort = (en - k0 * q**n) / faktor if aufbau else (k0 * q**n - en) / faktor
                if r_antwort > 0:
                    break
            paare.append((
                _fill(rng.choice(_T_R_AUF if aufbau else _T_R_AB), sz, k0=geld(k0), p=prozent(p), n=n, en=geld(en), zp=zeitpunkt_phrase(rng, vor)),
                numerical_finanz_geld(r_antwort),
            ))

            # n gesucht
            while True:
                k0, r, p, n, vor = sample()
                aufbau = rng.random() < 0.3
                q = q_of(p)
                if aufbau:
                    en = schoen(kapital_en(k0, r, q, n, vor, True), stufe)
                    template = _T_N_AUF[0]
                else:
                    komplett = rng.random() < 0.5
                    if komplett:
                        en = 0.0
                        template = _T_N_AB[0]
                    else:
                        en_roh = kapital_en(k0, r, q, n, vor, False)
                        if en_roh <= 0:
                            continue
                        en = schoen(en_roh, stufe)
                        template = _T_N_AB[1]
                n_antwort = kapital_n(k0, r, q, en, vor, aufbau)
                if n_antwort is not None and n_antwort > 1.0:
                    break
            paare.append((
                _fill(template, sz, k0=geld(k0), p=prozent(p), zp=zeitpunkt_phrase(rng, vor), r=geld(r), en=geld(en)),
                numerical_finanz_laufzeit(n_antwort),
            ))

            fragen, antworten = mische_teilfragen(rng, paare)
            tasks.append(Task(einleitung=sz.intro_anlage, fragen=fragen, antworten=antworten))

        return tasks
