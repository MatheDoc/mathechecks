"""Generator fuer Check 14 - Kubische Steckbriefaufgaben."""

from __future__ import annotations

from dataclasses import dataclass
import random

from aufgaben.core.latex import display_eq, fmt
from aufgaben.core.models import Task
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.extrem_monotonie_shared import (
    _required_decimals,
)
from aufgaben.generators.analysis.differentialrechnung_ganzrationaler_funktionen.shared import (
    PolynomialCase,
    coefficient_answer,
)


_LEADING_VALUES = (-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0)
_CENTER_VALUES = tuple(value / 2.0 for value in range(-10, 11))
_DELTA_VALUES = (-3.0, -2.5, -2.0, -1.5, -1.0, 1.0, 1.5, 2.0, 2.5, 3.0)
_Y_VALUES = tuple(float(value) for value in range(-10, 11))
_MAX_COEFF_ABS = 80.0
_MAX_POINT_Y_ABS = 120.0


@dataclass(frozen=True)
class CubicSteckbriefCase:
    function_case: PolynomialCase
    extremum_kind: str
    x_extremum: float
    y_extremum: float
    x_inflection: float
    y_inflection: float

    def signature(self) -> tuple[object, ...]:
        return (
            *self.function_case.signature(),
            self.extremum_kind,
            self.x_extremum,
            self.y_extremum,
            self.x_inflection,
            self.y_inflection,
        )


class SteckbriefGanzrationaleFunktionenGenerator(TaskGenerator):
    generator_key = "analysis.differentialrechnung_ganzrationaler_funktionen.steckbrief_ganzrationale_funktionen"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[object, ...]] = set()

        for extremum_kind in _balanced_extremum_kinds(count, rng):
            for _ in range(1200):
                case = sample_cubic_steckbrief_case(rng, extremum_kind=extremum_kind)
                if case.signature() in used:
                    continue
                used.add(case.signature())
                tasks.append(_build_task(case))
                break
            else:
                raise ValueError("Konnte nicht genug kubische Steckbriefaufgaben erzeugen.")

        return tasks


def _balanced_extremum_kinds(count: int, rng: random.Random) -> list[str]:
    kinds = ["Hochpunkt" if index % 2 == 0 else "Tiefpunkt" for index in range(count)]
    rng.shuffle(kinds)
    return kinds


def sample_cubic_steckbrief_case(
    rng: random.Random,
    *,
    extremum_kind: str,
) -> CubicSteckbriefCase:
    for _ in range(4000):
        x_inflection = float(rng.choice(_CENTER_VALUES))
        delta = float(rng.choice(_DELTA_VALUES))
        x_extremum = x_inflection + delta
        if not -7.0 <= x_extremum <= 7.0:
            continue

        leading = float(rng.choice(_LEADING_VALUES))
        if extremum_kind == "Hochpunkt" and leading * delta >= 0:
            continue
        if extremum_kind == "Tiefpunkt" and leading * delta <= 0:
            continue

        y_inflection = _clean_value(float(rng.choice(_Y_VALUES)))
        y_extremum = _clean_value(y_inflection - 2.0 * leading * (delta ** 3))
        if abs(y_extremum) > _MAX_POINT_Y_ABS:
            continue

        a3 = _clean_value(leading)
        a2 = _clean_value(-3.0 * leading * x_inflection)
        a1 = _clean_value(3.0 * leading * (x_inflection * x_inflection - delta * delta))
        a0 = _clean_value(y_inflection + leading * (-x_inflection ** 3 + 3.0 * delta * delta * x_inflection))
        coeffs = (a3, a2, a1, a0)

        if any(abs(value) > _MAX_COEFF_ABS for value in coeffs):
            continue
        if any(_required_decimals(value, max_decimals=2) is None for value in (*coeffs, y_extremum, y_inflection)):
            continue

        function_case = PolynomialCase(coeffs)
        if abs(function_case.evaluate(x_extremum) - y_extremum) > 1e-9:
            continue
        if abs(function_case.evaluate(x_inflection) - y_inflection) > 1e-9:
            continue
        if abs(function_case.derivative().evaluate(x_extremum)) > 1e-9:
            continue
        if abs(function_case.derivative(2).evaluate(x_inflection)) > 1e-9:
            continue

        second_at_extremum = function_case.derivative(2).evaluate(x_extremum)
        if extremum_kind == "Hochpunkt" and second_at_extremum >= -1e-9:
            continue
        if extremum_kind == "Tiefpunkt" and second_at_extremum <= 1e-9:
            continue

        return CubicSteckbriefCase(
            function_case=function_case,
            extremum_kind=extremum_kind,
            x_extremum=x_extremum,
            y_extremum=y_extremum,
            x_inflection=x_inflection,
            y_inflection=y_inflection,
        )

    raise ValueError("Konnte keinen geeigneten kubischen Steckbrieffall erzeugen.")


def _build_task(case: CubicSteckbriefCase) -> Task:
    intro = (
        "Gesucht ist eine kubische Funktion der Form "
        f"{display_eq('f(x)=ax^3+bx^2+cx+d')} "
        "Es gelten folgende Bedingungen:"
        "<ul>"
        f"<li>Im Punkt $E({fmt(case.x_extremum)}\\mid {fmt(case.y_extremum)})$ liegt ein {case.extremum_kind} vor.</li>"
        f"<li>Im Punkt $W({fmt(case.x_inflection)}\\mid {fmt(case.y_inflection)})$ liegt ein Wendepunkt vor.</li>"
        "</ul>"
    )
    return Task(
        einleitung=intro,
        fragen=["Bestimmen Sie die Koeffizienten $a$, $b$, $c$ und $d$ der Funktion."],
        antworten=[coefficient_answer(["a", "b", "c", "d"], list(case.function_case.coeffs))],
    )


def _clean_value(value: float) -> float:
    return 0.0 if abs(value) < 1e-9 else float(value)