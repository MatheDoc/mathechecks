"""Generator 11 – Geometrisches Szenario (quadratisch).

Sachaufgabe: Flugbahn oder Bogen. Die Funktionsgleichung wird aus drei
kontextbezogenen Punkten aufgestellt; Scheitel und Nullstellen werden
bewusst nicht in der Einleitung verraten.
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator


def _fmt_dez(value: float) -> str:
    """Zahl mit deutschem Komma für Fließtext."""
    if abs(value) < 1e-9:
        value = 0
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def _scenario_order(rng: random.Random, count: int, scenario_count: int) -> list[int]:
    order: list[int] = []
    while len(order) < count:
        block = list(range(scenario_count))
        rng.shuffle(block)
        order.extend(block)
    return order[:count]


# ---------------------------------------------------------------------------
# Szenarien
#
# typ "wurf":  Nullstellen x1 < 0 < x2; erster gegebener Punkt ist (0 | Starthöhe).
# typ "bogen": Nullstellen 0 und 2w (Breite); drei innere Messpunkte gegeben.
#
# a_choices / w_choices / d_choices sind so gewählt, dass Höhen und Weiten
# im Sachkontext plausibel bleiben und alle Werte höchstens 2 Nachkommastellen haben.
# ---------------------------------------------------------------------------

_SZENARIEN: list[dict] = [
    {
        "typ": "wurf",
        "intro": (
            "Bei einem Abstoß schlägt ein Torwart den Fußball weit in die "
            "gegnerische Hälfte. Eine Videoanalyse liefert drei Messwerte der Flugbahn:"
        ),
        "punkte_satz": "Beim Abschlagpunkt (Entfernung 0 m) liegt der Ball {y1} m über dem Boden, in {x2} m Entfernung beträgt die Höhe {y2} m und in {x3} m Entfernung noch {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Balls in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Ball seine größte Höhe erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Balls.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung der Ball auf dem Boden aufkommt.",
        "frage_eval": "Bestimmen Sie die Höhe des Balls in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Ball ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.25, -0.1],
        "w_choices": [6, 7, 8],
        "d_choices": [3, 4, 5],
        "start_height_range": [0.5, 2.5],
    },
    {
        "typ": "wurf",
        "intro": (
            "Beim Training wirft eine Basketballspielerin den Ball aus dem Stand "
            "in Richtung Korb. Drei Punkte der Flugbahn wurden vermessen:"
        ),
        "punkte_satz": "Beim Abwurf (Entfernung 0 m) befindet sich der Ball {y1} m über dem Boden, nach {x2} m beträgt die Höhe {y2} m und nach {x3} m sind es {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Balls in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Ball den höchsten Punkt erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Balls.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung der Ball auf dem Boden aufkommen würde.",
        "frage_eval": "Bestimmen Sie die Höhe des Balls in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Ball ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.25, -0.5],
        "w_choices": [4, 5],
        "d_choices": [1, 2, 3],
        "start_height_range": [1.5, 2.5],
    },
    {
        "typ": "wurf",
        "intro": (
            "Bei einem Leichtathletik-Wettkampf wird die Flugbahn eines Speers "
            "mit einer Kamera erfasst. Die Auswertung ergibt folgende Werte:"
        ),
        "punkte_satz": "Beim Abwurf (Entfernung 0 m) liegt der Speer {y1} m über dem Boden, in {x2} m Entfernung beträgt die Höhe {y2} m und in {x3} m Entfernung {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Speers in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Speer seine größte Höhe erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Speers.",
        "frage_ns": "Bestimmen Sie die Wurfweite, also die Entfernung, in der der Speer im Boden landet.",
        "frage_eval": "Bestimmen Sie die Höhe des Speers in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Speer ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.05, -0.04],
        "w_choices": [12, 14, 15, 16],
        "d_choices": [8, 9, 10, 11],
        "start_height_range": [1.5, 2.5],
    },
    {
        "typ": "wurf",
        "intro": (
            "Ein Golfball wird vom Abschlagpunkt über eine leichte Anhöhe "
            "geschlagen. Ein Tracking-System zeichnet drei Bahnpunkte auf:"
        ),
        "punkte_satz": "Beim Abschlag (Entfernung 0 m) liegt der Ball {y1} m über der Ebene, nach {x2} m beträgt die Höhe {y2} m und nach {x3} m noch {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Balls in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Ball den höchsten Punkt seiner Flugbahn erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Balls.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung der Ball auf der Ebene aufkommt.",
        "frage_eval": "Bestimmen Sie die Höhe des Balls in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Ball ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.01],
        "w_choices": [20, 25, 30],
        "d_choices": [10, 15],
        "start_height_range": [0.5, 2.5],
    },
    {
        "typ": "wurf",
        "intro": (
            "Beim Handballtraining wirft ein Spieler den Ball aus dem Sprung "
            "auf das Tor. Die Flugbahn wurde an drei Stellen vermessen:"
        ),
        "punkte_satz": "Beim Abwurf (Entfernung 0 m) befindet sich der Ball {y1} m über dem Hallenboden, nach {x2} m beträgt die Höhe {y2} m und nach {x3} m sind es {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Balls in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Ball am höchsten fliegt.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Balls.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung der Ball ohne Hindernis auf dem Boden aufkommen würde.",
        "frage_eval": "Bestimmen Sie die Höhe des Balls in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Ball ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.2, -0.1],
        "w_choices": [5, 6],
        "d_choices": [1, 2, 3],
        "start_height_range": [1.5, 2.5],
    },
    {
        "typ": "wurf",
        "intro": (
            "Die Fontäne eines Springbrunnens tritt schräg aus einer Düse aus "
            "und beschreibt einen Bogen über das Wasserbecken. Drei Messwerte liegen vor:"
        ),
        "punkte_satz": "An der Düse (Entfernung 0 m) liegt der Strahl {y1} m über der Wasseroberfläche, in {x2} m Entfernung beträgt die Höhe {y2} m und in {x3} m Entfernung {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Wasserstrahls in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Strahl seine größte Höhe erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Wasserstrahls.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung der Strahl auf die Wasseroberfläche trifft.",
        "frage_eval": "Bestimmen Sie die Höhe des Strahls in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Strahl ebenfalls {y_text} m über der Wasseroberfläche liegt.",
        "a_choices": [-0.5, -0.25, -0.2],
        "w_choices": [3, 4, 5],
        "d_choices": [1, 2],
        "start_height_range": [0.5, 2.0],
    },
    {
        "typ": "wurf",
        "intro": (
            "Bei einer Übung richtet die Feuerwehr einen Löschstrahl auf ein "
            "brennendes Objekt. Der Verlauf des Strahls wurde an drei Stellen erfasst:"
        ),
        "punkte_satz": "Am Strahlrohr (Entfernung 0 m) liegt der Strahl {y1} m über dem Boden, in {x2} m Entfernung beträgt die Höhe {y2} m und in {x3} m Entfernung {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Löschstrahls in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Löschstrahl seinen höchsten Punkt erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Löschstrahls.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung der Strahl auf dem Boden auftrifft.",
        "frage_eval": "Bestimmen Sie die Höhe des Strahls in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Strahl ebenfalls {y_text} m über dem Boden liegt.",
        "a_choices": [-0.1, -0.05],
        "w_choices": [8, 10, 12],
        "d_choices": [4, 5, 6],
        "start_height_range": [0.5, 2.0],
    },
    {
        "typ": "wurf",
        "intro": (
            "Bei einer Motocross-Show springt ein Fahrer über eine Rampe. "
            "Sensoren erfassen die Flughöhe des Motorrads an drei Stellen:"
        ),
        "punkte_satz": "An der Rampenkante (Entfernung 0 m) liegt das Motorrad {y1} m über dem Boden, nach {x2} m beträgt die Höhe {y2} m und nach {x3} m noch {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Motorrads in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der das Motorrad seinen höchsten Punkt erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Flughöhe des Motorrads.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung das Motorrad wieder auf dem Boden aufsetzt.",
        "frage_eval": "Bestimmen Sie die Flughöhe in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung das Motorrad ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.1, -0.2],
        "w_choices": [6, 8],
        "d_choices": [2, 3, 4],
        "start_height_range": [1.0, 3.0],
    },
    {
        "typ": "wurf",
        "intro": (
            "Bei einer Zirkusvorstellung wird ein Artist aus einer Kanone "
            "in ein Fangnetz geschossen. Die Flugbahn wurde an drei Punkten dokumentiert:"
        ),
        "punkte_satz": "An der Kanonenmündung (Entfernung 0 m) befindet sich der Artist {y1} m über dem Boden, nach {x2} m beträgt die Höhe {y2} m und nach {x3} m sind es {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Artisten in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Artist den höchsten Punkt erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Artisten.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung der Artist auf Bodenhöhe ankommen würde.",
        "frage_eval": "Bestimmen Sie die Höhe des Artisten in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Artist ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.25, -0.1],
        "w_choices": [8, 10],
        "d_choices": [4, 5, 6],
        "start_height_range": [1.0, 4.0],
    },
    {
        "typ": "wurf",
        "intro": (
            "Auf einem Volksfest schießt eine Konfettikanone ihre Ladung "
            "schräg über den Platz. Die Bahn des Schwerpunkts wurde vermessen:"
        ),
        "punkte_satz": "An der Mündung (Entfernung 0 m) liegt die Ladung {y1} m über dem Boden, in {x2} m Entfernung beträgt die Höhe {y2} m und in {x3} m Entfernung {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe der Konfettiladung in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der die Ladung ihre größte Höhe erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe der Ladung.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung die Ladung auf dem Boden landet.",
        "frage_eval": "Bestimmen Sie die Höhe der Ladung in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung die Ladung ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.5, -0.25],
        "w_choices": [4, 5, 6],
        "d_choices": [1, 2, 3],
        "start_height_range": [1.0, 3.0],
    },
    {
        "typ": "wurf",
        "intro": (
            "Beim Beachvolleyball spielt eine Spielerin einen hohen Ball über "
            "das Netz. Drei Punkte der Flugbahn sind bekannt:"
        ),
        "punkte_satz": "Beim Abschlag (Entfernung 0 m) befindet sich der Ball {y1} m über dem Sand, nach {x2} m beträgt die Höhe {y2} m und nach {x3} m sind es {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Balls in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Ball am höchsten fliegt.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Balls.",
        "frage_ns": "Bestimmen Sie, in welcher Entfernung der Ball im Sand landet.",
        "frage_eval": "Bestimmen Sie die Höhe des Balls in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Ball ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.25, -0.1],
        "w_choices": [4, 5],
        "d_choices": [1, 2],
        "start_height_range": [1.5, 2.5],
        "vertex_height_range": [2.5, 5.0],
    },
    {
        "typ": "wurf",
        "intro": (
            "Ein Rasensprenger wirft einen Wasserstrahl in einem Bogen über "
            "ein Beet. Der Strahlverlauf wurde an drei Stellen gemessen:"
        ),
        "punkte_satz": "An der Austrittsöffnung (Entfernung 0 m) liegt der Strahl {y1} m über dem Boden, in {x2} m Entfernung beträgt die Höhe {y2} m und in {x3} m Entfernung {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Wasserstrahls in Metern",
        "x_beschreibung": "der horizontalen Entfernung $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Entfernung, in der der Strahl seine größte Höhe erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Strahls.",
        "frage_ns": "Bestimmen Sie die Reichweite des Sprengers, also die Entfernung, in der der Strahl auf dem Boden auftrifft.",
        "frage_eval": "Bestimmen Sie die Höhe des Strahls in {x_text} m Entfernung.",
        "frage_inverse": "Bestimmen Sie, in welcher weiteren Entfernung der Strahl ebenfalls {y_text} m über dem Boden liegt.",
        "a_choices": [-0.25, -0.2],
        "w_choices": [3, 4, 5],
        "d_choices": [1, 2],
        "start_height_range": [0.5, 1.5],
    },
    {
        "typ": "bogen",
        "intro": (
            "Eine alte Steinbrücke überspannt einen Fluss mit einem "
            "parabelförmigen Bogen. Bei einer Vermessung wurden drei Höhen "
            "über der Wasseroberfläche bestimmt:"
        ),
        "punkte_satz": "In {x1} m Abstand vom linken Bogenansatz beträgt die Höhe {y1} m, in {x2} m Abstand {y2} m und in {x3} m Abstand {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Brückenbogens in Metern",
        "x_beschreibung": "dem Abstand $x$ vom linken Bogenansatz in Metern",
        "frage_xs": "Bestimmen Sie, in welchem Abstand vom linken Ansatz der Bogen seine größte Höhe erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Bogens.",
        "frage_ns": "Bestimmen Sie die Spannweite des Bogens, also den Abstand zwischen den beiden Bogenansätzen.",
        "frage_eval": "Bestimmen Sie die Höhe des Bogens in {x_text} m Abstand vom linken Ansatz.",
        "frage_inverse": "Bestimmen Sie den weiteren Abstand vom linken Ansatz, in dem der Bogen ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.25, -0.2],
        "w_choices": [5, 6, 8],
        "d_choices": [],
    },
    {
        "typ": "bogen",
        "intro": (
            "Das historische Stadttor besitzt einen parabelförmigen Torbogen. "
            "Für eine Restaurierung wurden drei Höhen des Bogens gemessen:"
        ),
        "punkte_satz": "In {x1} m Abstand vom linken Rand beträgt die Höhe {y1} m, in {x2} m Abstand {y2} m und in {x3} m Abstand {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Torbogens in Metern",
        "x_beschreibung": "dem Abstand $x$ vom linken Rand in Metern",
        "frage_xs": "Bestimmen Sie, in welchem Abstand vom linken Rand der Torbogen am höchsten ist.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Torbogens.",
        "frage_ns": "Bestimmen Sie die Breite des Torbogens am Boden.",
        "frage_eval": "Bestimmen Sie die Höhe des Bogens in {x_text} m Abstand vom linken Rand.",
        "frage_inverse": "Bestimmen Sie den weiteren Abstand vom linken Rand, in dem der Torbogen ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.5, -0.25],
        "w_choices": [3, 4],
        "d_choices": [],
    },
    {
        "typ": "bogen",
        "intro": (
            "Das Portal eines Eisenbahntunnels hat die Form einer nach unten "
            "geöffneten Parabel. Drei Messungen der Portalhöhe liegen vor:"
        ),
        "punkte_satz": "In {x1} m Abstand vom linken Portalrand beträgt die Höhe {y1} m, in {x2} m Abstand {y2} m und in {x3} m Abstand {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Tunnelportals in Metern",
        "x_beschreibung": "dem Abstand $x$ vom linken Portalrand in Metern",
        "frage_xs": "Bestimmen Sie, in welchem Abstand vom linken Rand das Portal seine größte Höhe erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Portals.",
        "frage_ns": "Bestimmen Sie die Breite des Portals am Boden.",
        "frage_eval": "Bestimmen Sie die Portalhöhe in {x_text} m Abstand vom linken Rand.",
        "frage_inverse": "Bestimmen Sie den weiteren Abstand vom linken Rand, in dem das Portal ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.25, -0.2],
        "w_choices": [4, 5],
        "d_choices": [],
    },
    {
        "typ": "bogen",
        "intro": (
            "Das Dach einer Sporthalle ist im Querschnitt parabelförmig "
            "gewölbt. Aus den Bauplänen sind drei Höhenangaben bekannt:"
        ),
        "punkte_satz": "In {x1} m Abstand vom linken Auflager beträgt die Dachhöhe {y1} m, in {x2} m Abstand {y2} m und in {x3} m Abstand {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Dachs in Metern",
        "x_beschreibung": "dem Abstand $x$ vom linken Auflager in Metern",
        "frage_xs": "Bestimmen Sie, in welchem Abstand vom linken Auflager das Dach am höchsten ist.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Dachs.",
        "frage_ns": "Bestimmen Sie die Spannweite des Dachs zwischen den beiden Auflagern.",
        "frage_eval": "Bestimmen Sie die Dachhöhe in {x_text} m Abstand vom linken Auflager.",
        "frage_inverse": "Bestimmen Sie den weiteren Abstand vom linken Auflager, in dem das Dach ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.05, -0.04],
        "w_choices": [10, 15],
        "d_choices": [],
    },
    {
        "typ": "bogen",
        "intro": (
            "Ein Folien-Gewächshaus hat einen parabelförmigen Querschnitt. "
            "Für den Zuschnitt der Folie wurden drei Höhen gemessen:"
        ),
        "punkte_satz": "In {x1} m Abstand vom linken Bodenrand beträgt die Höhe {y1} m, in {x2} m Abstand {y2} m und in {x3} m Abstand {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Gewächshauses in Metern",
        "x_beschreibung": "dem Abstand $x$ vom linken Bodenrand in Metern",
        "frage_xs": "Bestimmen Sie, in welchem Abstand vom linken Rand das Gewächshaus am höchsten ist.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Gewächshauses.",
        "frage_ns": "Bestimmen Sie die Breite des Gewächshauses am Boden.",
        "frage_eval": "Bestimmen Sie die Höhe in {x_text} m Abstand vom linken Rand.",
        "frage_inverse": "Bestimmen Sie den weiteren Abstand vom linken Rand, in dem das Gewächshaus ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.25, -0.2],
        "w_choices": [3, 4],
        "d_choices": [],
    },
    {
        "typ": "bogen",
        "intro": (
            "Ein Abschnitt einer Achterbahn führt über einen parabelförmigen "
            "Hügel. Die Schienenhöhe über dem Boden wurde an drei Stellen erfasst:"
        ),
        "punkte_satz": "In {x1} m Abstand vom Hügelanfang beträgt die Schienenhöhe {y1} m, in {x2} m Abstand {y2} m und in {x3} m Abstand {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Schienenhöhe in Metern",
        "x_beschreibung": "dem Abstand $x$ vom Hügelanfang in Metern",
        "frage_xs": "Bestimmen Sie, in welchem Abstand vom Hügelanfang die Schiene am höchsten liegt.",
        "frage_ys": "Bestimmen Sie die maximale Schienenhöhe.",
        "frage_ns": "Bestimmen Sie die Länge des Hügels am Boden, also den Abstand zwischen Anfang und Ende.",
        "frage_eval": "Bestimmen Sie die Schienenhöhe in {x_text} m Abstand vom Hügelanfang.",
        "frage_inverse": "Bestimmen Sie den weiteren Abstand vom Hügelanfang, in dem die Schiene ebenfalls {y_text} m hoch liegt.",
        "a_choices": [-0.1, -0.05],
        "w_choices": [8, 10],
        "d_choices": [],
    },
    {
        "typ": "bogen",
        "intro": (
            "Ein Festzelt hat einen parabelförmigen Querschnitt. Für die "
            "Statikprüfung wurden drei Zelthöhen bestimmt:"
        ),
        "punkte_satz": "In {x1} m Abstand vom linken Zeltrand beträgt die Höhe {y1} m, in {x2} m Abstand {y2} m und in {x3} m Abstand {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Zeltdachs in Metern",
        "x_beschreibung": "dem Abstand $x$ vom linken Zeltrand in Metern",
        "frage_xs": "Bestimmen Sie, in welchem Abstand vom linken Rand das Zelt am höchsten ist.",
        "frage_ys": "Bestimmen Sie die maximale Zelthöhe.",
        "frage_ns": "Bestimmen Sie die Breite des Zelts am Boden.",
        "frage_eval": "Bestimmen Sie die Zelthöhe in {x_text} m Abstand vom linken Rand.",
        "frage_inverse": "Bestimmen Sie den weiteren Abstand vom linken Rand, in dem das Zeltdach ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.2, -0.25],
        "w_choices": [4, 5],
        "d_choices": [],
    },
    {
        "typ": "bogen",
        "intro": (
            "Ein Viadukt einer stillgelegten Bahnstrecke ruht auf einem großen "
            "parabelförmigen Bogen. Drei Höhenmessungen über dem Talboden liegen vor:"
        ),
        "punkte_satz": "In {x1} m Abstand vom linken Bogenansatz beträgt die Höhe {y1} m, in {x2} m Abstand {y2} m und in {x3} m Abstand {y3} m.",
        "fn": "h",
        "y_beschreibung": "die Höhe des Bogens in Metern",
        "x_beschreibung": "dem Abstand $x$ vom linken Bogenansatz in Metern",
        "frage_xs": "Bestimmen Sie, in welchem Abstand vom linken Ansatz der Bogen seine größte Höhe erreicht.",
        "frage_ys": "Bestimmen Sie die maximale Höhe des Bogens.",
        "frage_ns": "Bestimmen Sie die Spannweite des Bogens.",
        "frage_eval": "Bestimmen Sie die Bogenhöhe in {x_text} m Abstand vom linken Ansatz.",
        "frage_inverse": "Bestimmen Sie den weiteren Abstand vom linken Ansatz, in dem der Bogen ebenfalls {y_text} m hoch ist.",
        "a_choices": [-0.1, -0.05],
        "w_choices": [10, 12],
        "d_choices": [],
    },
]


class GeometrischesSzenarioQuadGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.geometrisches_szenario_quad"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for idx in _scenario_order(rng, count, len(_SZENARIEN)):
            task = None
            while task is None:
                task = self._build(rng, _SZENARIEN[idx])
            tasks.append(task)

        return tasks

    def _build(self, rng: random.Random, sz: dict) -> Task | None:
        if sz["typ"] == "bogen":
            a = rng.choice(sz["a_choices"])
            w = rng.choice(sz["w_choices"])
            d = w
        else:
            start_height_range = sz.get("start_height_range")
            vertex_height_range = sz.get("vertex_height_range")
            parameter_options = []
            for candidate_a in sz["a_choices"]:
                for candidate_w in sz["w_choices"]:
                    for candidate_d in sz["d_choices"]:
                        start_height = candidate_a * (candidate_d - candidate_w) * (candidate_d + candidate_w)
                        vertex_height = -candidate_a * candidate_w**2
                        if not 0 < candidate_d < candidate_w:
                            continue
                        if start_height_range and not start_height_range[0] <= start_height <= start_height_range[1]:
                            continue
                        if vertex_height_range and not vertex_height_range[0] <= vertex_height <= vertex_height_range[1]:
                            continue
                        parameter_options.append((candidate_a, candidate_w, candidate_d))
            if not parameter_options:
                return None
            a, w, d = rng.choice(parameter_options)

        x1_ns = d - w
        x2_ns = d + w

        def f(x: float) -> float:
            return a * (x - x1_ns) * (x - x2_ns)

        def clean(v: float) -> bool:
            return abs(round(v * 100) - v * 100) < 1e-6

        b = -a * (x1_ns + x2_ns)
        c = a * x1_ns * x2_ns
        y_s = f(d)
        if not all(clean(v) for v in (a, b, c, y_s)):
            return None
        if not (1.5 <= y_s <= 60):
            return None

        # Drei gegebene Punkte: nie Nullstellen oder Scheitel.
        if sz["typ"] == "wurf":
            pool = [x for x in range(1, x2_ns) if x != d]
            if len(pool) < 2:
                return None
            others = sorted(rng.sample(pool, 2))
            px = [0, others[0], others[1]]
        else:
            pool = [x for x in range(1, 2 * w) if x != d]
            if len(pool) < 3:
                return None
            px = sorted(rng.sample(pool, 3))

        py = [f(x) for x in px]
        if not all(clean(v) and v > 0 for v in py):
            return None

        # Auswertungsstelle: keiner der gegebenen Punkte, kein Scheitel, keine Nullstelle.
        eval_pool = [
            step / 2 for step in range(1, 2 * x2_ns)
            for x in [step / 2]
            if x not in px
            and x != d
            and 2 * d - x >= 0
            and 2 * d - x not in px
        ]
        if not eval_pool:
            return None
        x_eval = rng.choice(eval_pool)
        y_eval = f(x_eval)
        x_inverse = 2 * d - x_eval
        if not clean(y_eval) or y_eval <= 0:
            return None

        einleitung = (
            sz["intro"]
            + "\n\n"
            + sz["punkte_satz"].format(
                x1=_fmt_dez(px[0]), y1=_fmt_dez(py[0]),
                x2=_fmt_dez(px[1]), y2=_fmt_dez(py[1]),
                x3=_fmt_dez(px[2]), y3=_fmt_dez(py[2]),
            )
        )

        fn = sz["fn"]
        fragen = [
            (
                f"Bestimmen Sie die Gleichung der Funktion "
                f"$ {fn}(x) = ax^2 + bx + c $, die {sz['y_beschreibung']} "
                f"in Abhängigkeit von {sz['x_beschreibung']} angibt."
            ),
            sz["frage_xs"],
            sz["frage_ys"],
            sz["frage_ns"],
            sz["frage_eval"].format(x_text=_fmt_dez(x_eval)),
            sz["frage_inverse"].format(y_text=_fmt_dez(y_eval)),
        ]
        antworten = [
            (
                f"$ {fn}(x)= ${numerical_analysis_calc(float(a))}"
                f"$ x^2+ ${numerical_analysis_calc(float(b))}"
                f"$ x+ ${numerical_analysis_calc(float(c))}"
            ),
            f"$ x = ${numerical_analysis_calc(float(d))}",
            numerical_analysis_calc(float(y_s)),
            numerical_analysis_calc(float(x2_ns)),
            numerical_analysis_calc(float(y_eval)),
            numerical_analysis_calc(float(x_inverse)),
        ]

        return Task(
            einleitung=einleitung,
            fragen=fragen,
            antworten=antworten,
        )
