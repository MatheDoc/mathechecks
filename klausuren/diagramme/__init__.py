"""Einheitliche Diagramme für Klausuren (PDF-Druck, schwarz-weiß).

Verwendung im `generate_diagramme.py` eines Klausur-Ordners:

    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from diagramme import *

    OUT = Path(__file__).parent
    funktionsgraph(OUT / "diagramm-aufgabe1.png", [Kurve("15*x", "$E$")], xlim=(0, 20), ylim=(0, 300))

Dokumentation: klausuren/README.md, Abschnitt „Diagramme“. Beispiele: `python klausuren/diagramme/galerie.py`.
"""

from ._elemente import Flaeche, Hilfslinie, Punkt
from ._stil import zahl
from .baumdiagramm import LUECKE, baum_bernoulli, baum_zweistufig, baumdiagramm, quer
from .funktionsgraph import Kurve, funktionsgraph
from .histogramm import binomial_werte, histogramm, histogramm_binomial
from .lineare_optimierung import Restriktion, Zielgerade, lineare_optimierung, zulaessiger_bereich
from .pfeildiagramm import kanten_aus_matrix, pfeildiagramm, uebergangsgraph, verflechtungsdiagramm

__all__ = [
    "Flaeche",
    "Hilfslinie",
    "Kurve",
    "LUECKE",
    "Punkt",
    "Restriktion",
    "Zielgerade",
    "baum_bernoulli",
    "baum_zweistufig",
    "baumdiagramm",
    "binomial_werte",
    "funktionsgraph",
    "histogramm",
    "histogramm_binomial",
    "kanten_aus_matrix",
    "lineare_optimierung",
    "pfeildiagramm",
    "quer",
    "uebergangsgraph",
    "verflechtungsdiagramm",
    "zahl",
    "zulaessiger_bereich",
]
