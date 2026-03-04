"""Generatoren für den Lernbereich Binomialverteilung."""

from aufgaben.generators.stochastik.binomialverteilung.textbausteine import SCENARIOS, ScenarioTemplate
from aufgaben.generators.stochastik.binomialverteilung.shared import (
	violates_probability_rounding_policy,
)

__all__ = ["SCENARIOS", "ScenarioTemplate", "violates_probability_rounding_policy"]
