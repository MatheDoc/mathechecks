"""Gemeinsame Bibliothek der MatheChecks-Videos."""
import logging

# SoX wird nur für ein verändertes Sprechtempo gebraucht; ohne diese Zeile warnt jeder Lauf.
logging.getLogger("sox").setLevel(logging.ERROR)

from . import theme  # noqa: E402
from .bausteine import (  # noqa: E402
    Dezimalzahl,
    einpassen,
    formel,
    logo,
    nummer,
    rezept,
    schritt,
    stolperstein,
    text,
    ueberschrift,
)
from .szene import MCSzene  # noqa: E402

__all__ = [
    "Dezimalzahl",
    "MCSzene",
    "einpassen",
    "formel",
    "logo",
    "nummer",
    "rezept",
    "schritt",
    "stolperstein",
    "text",
    "theme",
    "ueberschrift",
]
