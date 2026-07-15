"""Generatoren für Checks 09-10 (Sachsituationen).

09  Sachsituation - eine Funktion  (sachsituation-eine-funktion)
10  Sachsituation - Vergleich      (sachsituation-vergleich)
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc, mc
from aufgaben.generators.base import TaskGenerator


# ---------------------------------------------------------------------------
# Helfer
# ---------------------------------------------------------------------------

def _fmt_dez(value: float) -> str:
    """Zahl mit deutschem Komma für Fließtext."""
    if abs(value) < 1e-9:
        value = 0
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".").replace(".", ",")


# Einheiten-Kürzel, die in Fließtext ausgeschrieben werden (Singular, Plural).
_UNIT_LANGFORM = {
    "h": ("Stunde", "Stunden"),
    "t": ("Tonne", "Tonnen"),
    "$": ("US-Dollar", "US-Dollar"),
}


def _fmt_wert(value: float, unit: str) -> str:
    # In Fließtext unschöne Einheiten-Kürzel ausschreiben; konventionelle
    # Einheiten (km, kg, cm, m³, kWh, GB, %, °C, °F, €) bleiben unverändert.
    if unit in _UNIT_LANGFORM:
        singular, plural = _UNIT_LANGFORM[unit]
        unit = singular if value == 1 else plural
    return f"{_fmt_dez(value)} {unit}".strip()


def _r(low: float, high: float, step: float) -> list[float]:
    """Wertebereich [low, high] in Schritten von step (auf 2 Nachkommastellen).

    Erzeugt szenariospezifische Zufallspools mit ganzen Zahlen oder Dezimalzahlen
    (eine/zwei Nachkommastellen); es müssen keine „runden" Werte sein.
    """
    count = int(round((high - low) / step))
    return [round(low + i * step, 2) for i in range(count + 1)]


def _scenario_order(rng: random.Random, count: int, scenario_count: int) -> list[int]:
    order: list[int] = []
    while len(order) < count:
        block = list(range(scenario_count))
        rng.shuffle(block)
        order.extend(block)
    return order[:count]


def _valid_y(value: float, minimum: float | None = None, maximum: float | None = None) -> bool:
    if minimum is not None and value < minimum - 1e-9:
        return False
    if maximum is not None and value > maximum + 1e-9:
        return False
    return True


def _choose_x(
    rng: random.Random,
    choices: list[float],
    m: float,
    b: float,
    y_min: float | None,
    y_max: float | None,
    exclude: set[float] | None = None,
) -> float:
    exclude = exclude or set()
    candidates = [
        x
        for x in choices
        if x not in exclude and _valid_y(m * x + b, y_min, y_max)
    ]
    if not candidates:
        raise ValueError("Keine plausible x-Auswahl für das Sachszenario gefunden.")
    return rng.choice(candidates)


def _choose_two_points(
    rng: random.Random,
    choices: list[float],
    m: float,
    b: float,
    y_min: float | None,
    y_max: float | None,
) -> tuple[float, float, float, float] | None:
    """Zwei plausible, sauber darstellbare Punkte (x1<x2) für die Modellierung."""
    valid = [
        x
        for x in choices
        if _valid_y(m * x + b, y_min, y_max)
        and abs(m * x + b) > 1e-6
        and abs(round((m * x + b) * 100) - (m * x + b) * 100) < 1e-6
    ]
    if len(valid) < 2:
        return None
    x1, x2 = sorted(rng.sample(valid, 2))
    return x1, m * x1 + b, x2, m * x2 + b


def _format_template(template: str, **values: object) -> str:
    return template.format(**values)


def _equation_question(sz: dict, fn: str, var: str) -> str:
    return (
        f"Bestimmen Sie die Gleichung der Funktion ${fn}({var})$, die "
        f"{sz['y_beschreibung']} in Abhängigkeit von {sz['x_beschreibung']} angibt."
    )


def _model_answer(fn: str, var: str, m: float, b: float) -> str:
    return (
        f"$ {fn}({var}) = ${numerical_analysis_calc(m)}$ \\cdot {var} "
        f"+ ${numerical_analysis_calc(b)}"
    )


# ---------------------------------------------------------------------------
# Szenario-Vorlagen - eine Funktion (Check 09)
# ---------------------------------------------------------------------------

_SZENARIEN_EINZELN: list[dict] = [
    {
        "kontext": (
            "Ein Taxiunternehmen kalkuliert Stadtfahrten mit einem festen Grundpreis "
            "von {b} € und einem kilometerabhängigen Preis von {m} € pro gefahrenem "
            "Kilometer. Die Kundschaft soll vor der Fahrt eine verlässliche "
            "Kostenschätzung erhalten."
        ),
        "var": "x",
        "func_name": "K",
        "x_beschreibung": "der Fahrstrecke $x$ in Kilometern",
        "y_beschreibung": "die Fahrtkosten in Euro",
        "x_unit": "km",
        "y_unit": "€",
        "m_choices": _r(1.2, 2.8, 0.1),
        "b_choices": _r(2.5, 6.0, 0.5),
        "m_sign": 1,
        "x_choices": _r(3, 20, 1),
        "inverse_choices": _r(4, 25, 1),
        "fw_frage": "Berechnen Sie die Fahrtkosten für eine Strecke von {x_text}.",
        "uw_frage": "Bestimmen Sie die Fahrstrecke, bei der die Fahrt {y_text} kostet.",
        "punkte": {
            "intro": "Für die Preisgestaltung eines Taxiunternehmens sind zwei abgerechnete Fahrten bekannt:",
            "satz": "Eine Fahrt über {x1_text} kostet {y1_text}, eine Fahrt über {x2_text} kostet {y2_text}.",
        },
    },
    {
        "kontext": (
            "Bei der Umrechnung von Temperaturen gilt: 0 °C entsprechen 32 °F, "
            "und 20 °C entsprechen 68 °F. Zwischen Celsius- und Fahrenheitwerten "
            "besteht ein linearer Zusammenhang."
        ),
        "var": "C",
        "func_name": "F",
        "x_beschreibung": "der Temperatur $C$ in Grad Celsius",
        "y_beschreibung": "die Temperatur in Grad Fahrenheit",
        "x_unit": "°C",
        "y_unit": "°F",
        "m_choices": [1.8],
        "b_choices": [32.0],
        "m_sign": 1,
        "x_choices": _r(-15, 35, 5),
        "inverse_choices": _r(-10, 40, 5),
        "fw_frage": "Berechnen Sie die Temperatur in Fahrenheit für {x_text}.",
        "uw_frage": "Bestimmen Sie die Celsius-Temperatur, bei der das Thermometer {y_text} anzeigt.",
    },
    {
        "kontext": (
            "Ein Schwimmbecken wird für Wartungsarbeiten entleert. Zu Beginn "
            "befinden sich {b} m³ Wasser im Becken; die Pumpe fördert gleichmäßig "
            "{m_abs} m³ pro Stunde ab."
        ),
        "var": "t",
        "func_name": "W",
        "x_beschreibung": "der Zeit $t$ in Stunden",
        "y_beschreibung": "das Wasservolumen in Kubikmetern",
        "x_unit": "h",
        "y_unit": "m³",
        "m_choices": _r(3, 11, 0.5),
        "b_choices": _r(70, 160, 5),
        "m_sign": -1,
        "y_min": 0,
        "x_choices": _r(2, 14, 1),
        "inverse_choices": _r(1, 20, 1),
        "fw_frage": "Berechnen Sie das Wasservolumen nach {x_text}.",
        "uw_frage": "Bestimmen Sie den Zeitpunkt, zu dem sich noch {y_text} im Becken befinden.",
        "null_frage": "Bestimmen Sie, nach wie vielen Stunden das Becken vollständig entleert ist.",
        "punkte": {
            "intro": "Ein Schwimmbecken wird für Wartungsarbeiten gleichmäßig entleert. Bei zwei Kontrollen wird der Füllstand notiert:",
            "satz": "Nach {x1_text} befinden sich noch {y1_text} im Becken, nach {x2_text} nur noch {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Regenrückhaltebecken enthält zu Beginn einer Messung {b} m³ Wasser. "
            "Durch einen konstanten Zufluss steigt das Volumen um {m} m³ pro Stunde."
        ),
        "var": "t",
        "func_name": "V",
        "x_beschreibung": "der Zeit $t$ in Stunden",
        "y_beschreibung": "das Wasservolumen in Kubikmetern",
        "x_unit": "h",
        "y_unit": "m³",
        "m_choices": _r(4, 14, 0.5),
        "b_choices": _r(0, 40, 5),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(2, 14, 1),
        "inverse_choices": _r(3, 18, 1),
        "fw_frage": "Berechnen Sie das Wasservolumen nach {x_text}.",
        "uw_frage": "Bestimmen Sie, nach wie vielen Stunden das Becken {y_text} enthält.",
        "punkte": {
            "intro": "Ein Regenrückhaltebecken füllt sich bei konstantem Zufluss gleichmäßig. Zwei Messungen liegen vor:",
            "satz": "Nach {x1_text} enthält es {y1_text}, nach {x2_text} bereits {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Laptop-Akku hat zu Beginn einer Arbeitsphase einen Ladestand von {b} %. "
            "Bei normaler Nutzung sinkt der Ladestand gleichmäßig um {m_abs} "
            "Prozentpunkte pro Stunde."
        ),
        "var": "t",
        "func_name": "L",
        "x_beschreibung": "der Nutzungsdauer $t$ in Stunden",
        "y_beschreibung": "den Ladestand in Prozent",
        "x_unit": "h",
        "y_unit": "%",
        "m_choices": _r(4, 13, 0.5),
        "b_choices": _r(75, 100, 5),
        "m_sign": -1,
        "y_min": 0,
        "y_max": 100,
        "x_choices": _r(2, 11, 1),
        "inverse_choices": _r(1, 15, 1),
        "fw_frage": "Berechnen Sie den Ladestand nach {x_text}.",
        "uw_frage": "Bestimmen Sie die Nutzungsdauer, nach der der Ladestand {y_text} beträgt.",
        "null_frage": "Bestimmen Sie, nach wie vielen Stunden der Akku rechnerisch leer ist.",
        "punkte": {
            "intro": "Der Ladestand eines Laptop-Akkus nimmt bei gleichmäßiger Nutzung linear ab. Zwei Ablesungen sind bekannt:",
            "satz": "Nach {x1_text} beträgt der Ladestand {y1_text}, nach {x2_text} nur noch {y2_text}.",
        },
    },
    {
        "kontext": (
            "Eine zylindrische Kerze ist zu Beginn {b} cm hoch. Beim Abbrennen nimmt "
            "ihre Höhe unter gleichbleibenden Bedingungen pro Stunde um {m_abs} cm ab."
        ),
        "var": "t",
        "func_name": "h",
        "x_beschreibung": "der Brenndauer $t$ in Stunden",
        "y_beschreibung": "die Kerzenhöhe in Zentimetern",
        "x_unit": "h",
        "y_unit": "cm",
        "m_choices": _r(1.5, 3, 0.5),
        "b_choices": _r(18, 34, 1),
        "m_sign": -1,
        "y_min": 0,
        "x_choices": _r(2, 9, 1),
        "inverse_choices": _r(1, 13, 1),
        "fw_frage": "Berechnen Sie die Höhe der Kerze nach {x_text}.",
        "uw_frage": "Bestimmen Sie die Brenndauer, bei der die Kerze noch {y_text} hoch ist.",
        "null_frage": "Bestimmen Sie, nach wie vielen Stunden die Kerze rechnerisch abgebrannt ist.",
        "punkte": {
            "intro": "Eine zylindrische Kerze brennt unter gleichbleibenden Bedingungen gleichmäßig ab. Zwei Höhen wurden gemessen:",
            "satz": "Nach {x1_text} ist sie noch {y1_text} hoch, nach {x2_text} nur noch {y2_text}.",
        },
    },
    {
        "kontext": (
            "In einer Baumschule wird das Wachstum einer jungen Linde dokumentiert. "
            "Zu Beginn der Beobachtung ist sie {b} cm hoch; in den folgenden Jahren "
            "wächst sie näherungsweise um {m} cm pro Jahr."
        ),
        "var": "t",
        "func_name": "h",
        "x_beschreibung": "der Zeit $t$ in Jahren",
        "y_beschreibung": "die Baumhöhe in Zentimetern",
        "x_unit": "Jahren",
        "y_unit": "cm",
        "m_choices": _r(6, 18, 1),
        "b_choices": _r(30, 110, 5),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(2, 12, 1),
        "inverse_choices": _r(3, 15, 1),
        "fw_frage": "Berechnen Sie die Höhe der Linde nach {x_text}.",
        "uw_frage": "Bestimmen Sie, nach wie vielen Jahren die Linde eine Höhe von {y_text} erreicht.",
        "punkte": {
            "intro": "In einer Baumschule wird das annähernd gleichmäßige Wachstum einer jungen Linde dokumentiert. Zwei Messungen liegen vor:",
            "satz": "Nach {x1_text} ist sie {y1_text} hoch, nach {x2_text} bereits {y2_text} hoch.",
        },
    },
    {
        "kontext": (
            "Eine Manufaktur produziert handgefertigte Vasen. Die monatlichen Fixkosten "
            "betragen {b} €; für jede Vase fallen zusätzlich {m} € Material- und "
            "Fertigungskosten an."
        ),
        "var": "x",
        "func_name": "K",
        "x_beschreibung": "der Anzahl $x$ produzierter Vasen",
        "y_beschreibung": "die Gesamtkosten in Euro",
        "x_unit": "Vasen",
        "y_unit": "€",
        "m_choices": _r(1.5, 8, 0.5),
        "b_choices": _r(60, 220, 10),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(5, 30, 1),
        "inverse_choices": _r(6, 35, 1),
        "fw_frage": "Berechnen Sie die Gesamtkosten für {x_text}.",
        "uw_frage": "Bestimmen Sie, wie viele Vasen mit einem Budget von {y_text} produziert werden können.",
        "punkte": {
            "intro": "Für die Kostenstruktur einer Vasen-Manufaktur sind zwei Produktionsmengen mit ihren Gesamtkosten bekannt:",
            "satz": "Bei {x1_text} entstehen Gesamtkosten von {y1_text}, bei {x2_text} Gesamtkosten von {y2_text}.",
        },
    },
    {
        "kontext": (
            "Eine Druckerei berechnet für eine Broschüre eine Einrichtungspauschale "
            "von {b} € und anschließend {m} € pro gedruckter Seite."
        ),
        "var": "s",
        "func_name": "K",
        "x_beschreibung": "der Seitenzahl $s$",
        "y_beschreibung": "die Druckkosten in Euro",
        "x_unit": "Seiten",
        "y_unit": "€",
        "m_choices": _r(0.03, 0.12, 0.01),
        "b_choices": _r(8, 22, 1),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(100, 500, 20),
        "inverse_choices": _r(120, 600, 20),
        "fw_frage": "Berechnen Sie die Druckkosten für {x_text}.",
        "uw_frage": "Bestimmen Sie die Seitenzahl, bei der die Druckkosten {y_text} betragen.",
        "punkte": {
            "intro": "Für die Druckkosten einer Broschüre liegen zwei Auflagen mit unterschiedlichem Umfang vor:",
            "satz": "Bei {x1_text} betragen die Druckkosten {y1_text}, bei {x2_text} betragen sie {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Parkhaus erhebt beim Einfahren eine Startgebühr von {b} € und berechnet "
            "danach {m} € pro angefangener Stunde im linearen Modell."
        ),
        "var": "t",
        "func_name": "K",
        "x_beschreibung": "der Parkdauer $t$ in Stunden",
        "y_beschreibung": "die Parkkosten in Euro",
        "x_unit": "h",
        "y_unit": "€",
        "m_choices": _r(1.5, 3.5, 0.5),
        "b_choices": _r(1, 4, 0.5),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(2, 9, 1),
        "inverse_choices": _r(1, 10, 1),
        "fw_frage": "Berechnen Sie die Parkkosten für eine Parkdauer von {x_text}.",
        "uw_frage": "Bestimmen Sie die Parkdauer, bei der {y_text} zu zahlen sind.",
        "punkte": {
            "intro": "Für die Gebühren eines Parkhauses sind zwei Parkvorgänge bekannt:",
            "satz": "Bei {x1_text} sind {y1_text} zu zahlen, bei {x2_text} sind es {y2_text}.",
        },
    },
    {
        "kontext": (
            "Eine Autovermietung verlangt für einen Tagesmietwagen eine feste Pauschale "
            "von {b} € und zusätzlich {m} € pro gefahrenem Kilometer."
        ),
        "var": "x",
        "func_name": "K",
        "x_beschreibung": "der gefahrenen Strecke $x$ in Kilometern",
        "y_beschreibung": "die Mietkosten in Euro",
        "x_unit": "km",
        "y_unit": "€",
        "m_choices": _r(0.2, 0.6, 0.05),
        "b_choices": _r(30, 90, 5),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(50, 250, 10),
        "inverse_choices": _r(60, 280, 10),
        "fw_frage": "Berechnen Sie die Mietkosten für eine Fahrtstrecke von {x_text}.",
        "uw_frage": "Bestimmen Sie die Fahrtstrecke, bei der die Mietkosten {y_text} betragen.",
        "punkte": {
            "intro": "Für die Kosten eines Tagesmietwagens liegen zwei Abrechnungen vor:",
            "satz": "Bei {x1_text} Fahrleistung entstehen Kosten von {y1_text}, bei {x2_text} Kosten von {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Mobilfunktarif besteht aus einer monatlichen Grundgebühr von {b} € "
            "und einem Preis von {m} € pro Gigabyte Datenvolumen."
        ),
        "var": "x",
        "func_name": "K",
        "x_beschreibung": "der Datenmenge $x$ in Gigabyte",
        "y_beschreibung": "die monatlichen Kosten in Euro",
        "x_unit": "GB",
        "y_unit": "€",
        "m_choices": _r(1.5, 5, 0.5),
        "b_choices": _r(6, 22, 1),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(2, 20, 1),
        "inverse_choices": _r(3, 24, 1),
        "fw_frage": "Berechnen Sie die monatlichen Kosten bei einem Datenvolumen von {x_text}.",
        "uw_frage": "Bestimmen Sie das Datenvolumen, bei dem monatlich {y_text} anfallen.",
        "punkte": {
            "intro": "Für einen Mobilfunktarif liegen zwei Monatsabrechnungen mit unterschiedlichem Datenverbrauch vor:",
            "satz": "Bei einem Verbrauch von {x1_text} fallen {y1_text} an, bei {x2_text} sind es {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Stromtarif hat einen monatlichen Grundpreis von {b} €. Der Arbeitspreis "
            "beträgt {m_cent} Cent pro verbrauchter Kilowattstunde."
        ),
        "var": "x",
        "func_name": "K",
        "x_beschreibung": "dem Stromverbrauch $x$ in Kilowattstunden",
        "y_beschreibung": "die monatlichen Stromkosten in Euro",
        "x_unit": "kWh",
        "y_unit": "€",
        "m_choices": _r(0.25, 0.45, 0.01),
        "b_choices": _r(5, 15, 1),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(100, 450, 10),
        "inverse_choices": _r(120, 500, 10),
        "fw_frage": "Berechnen Sie die monatlichen Stromkosten bei einem Verbrauch von {x_text}.",
        "uw_frage": "Bestimmen Sie den Stromverbrauch, bei dem monatliche Kosten von {y_text} entstehen.",
        "punkte": {
            "intro": "Für einen Stromtarif liegen zwei Monatsabrechnungen vor:",
            "satz": "Bei einem Verbrauch von {x1_text} betragen die Kosten {y1_text}, bei {x2_text} betragen sie {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Veranstaltungsbüro tauscht US-Dollar in Euro um. Es rechnet mit "
            "{m} € pro Dollar und erhebt zusätzlich eine Bearbeitungsgebühr von {b} €."
        ),
        "var": "x",
        "func_name": "K",
        "x_beschreibung": "dem umzutauschenden Betrag $x$ in US-Dollar",
        "y_beschreibung": "die Kosten in Euro",
        "x_unit": "$",
        "y_unit": "€",
        "m_choices": _r(0.85, 1.10, 0.01),
        "b_choices": _r(3, 10, 1),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(50, 500, 10),
        "inverse_choices": _r(80, 600, 10),
        "fw_frage": "Berechnen Sie die Kosten für einen Umtauschbetrag von {x_text}.",
        "uw_frage": "Bestimmen Sie den Dollarbetrag, bei dem Kosten von {y_text} entstehen.",
        "punkte": {
            "intro": "Ein Veranstaltungsbüro tauscht US-Dollar in Euro um. Zwei Umtauschvorgänge sind bekannt:",
            "satz": "Für {x1_text} ergeben sich Kosten von {y1_text}, für {x2_text} Kosten von {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Betrieb schreibt eine Maschine linear ab. Der Anschaffungswert beträgt "
            "{b} €; pro Jahr sinkt der Buchwert um {m_abs} €."
        ),
        "var": "t",
        "func_name": "B",
        "x_beschreibung": "der Nutzungsdauer $t$ in Jahren",
        "y_beschreibung": "den Buchwert in Euro",
        "x_unit": "Jahren",
        "y_unit": "€",
        "m_choices": _r(60, 180, 10),
        "b_choices": _r(900, 2200, 100),
        "m_sign": -1,
        "y_min": 0,
        "x_choices": _r(2, 12, 1),
        "inverse_choices": _r(1, 18, 1),
        "fw_frage": "Berechnen Sie den Buchwert der Maschine nach {x_text}.",
        "uw_frage": "Bestimmen Sie die Nutzungsdauer, nach der der Buchwert {y_text} beträgt.",
        "null_frage": "Bestimmen Sie, nach wie vielen Jahren der Buchwert rechnerisch auf 0 € sinkt.",
        "punkte": {
            "intro": "Für die lineare Abschreibung einer Maschine sind zwei Buchwerte bekannt:",
            "satz": "Nach {x1_text} beträgt der Buchwert {y1_text}, nach {x2_text} nur noch {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Lieferfahrzeug startet bereits {b} km vom Lager entfernt und fährt "
            "anschließend mit konstanter Geschwindigkeit weiter. Pro Stunde legt es "
            "{m} km zurück."
        ),
        "var": "t",
        "func_name": "s",
        "x_beschreibung": "der Fahrzeit $t$ in Stunden",
        "y_beschreibung": "die Entfernung vom Lager in Kilometern",
        "x_unit": "h",
        "y_unit": "km",
        "m_choices": _r(50, 100, 5),
        "b_choices": _r(10, 120, 10),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(1, 6, 1),
        "inverse_choices": _r(1, 7, 1),
        "fw_frage": "Berechnen Sie die Entfernung vom Lager nach {x_text}.",
        "uw_frage": "Bestimmen Sie die Fahrzeit, nach der das Fahrzeug {y_text} vom Lager entfernt ist.",
        "punkte": {
            "intro": "Ein Lieferfahrzeug entfernt sich mit konstanter Geschwindigkeit vom Lager. Zwei Positionen wurden erfasst:",
            "satz": "Nach {x1_text} ist es {y1_text} vom Lager entfernt, nach {x2_text} bereits {y2_text}.",
        },
    },
    {
        "kontext": (
            "In einem Silo lagern zu Beginn {b} Tonnen Getreide. Für die Produktion "
            "werden gleichmäßig {m_abs} Tonnen pro Tag entnommen."
        ),
        "var": "t",
        "func_name": "G",
        "x_beschreibung": "der Zeit $t$ in Tagen",
        "y_beschreibung": "die gelagerte Getreidemenge in Tonnen",
        "x_unit": "Tagen",
        "y_unit": "t",
        "m_choices": _r(4, 15, 1),
        "b_choices": _r(80, 220, 10),
        "m_sign": -1,
        "y_min": 0,
        "x_choices": _r(2, 13, 1),
        "inverse_choices": _r(1, 20, 1),
        "fw_frage": "Berechnen Sie die Getreidemenge im Silo nach {x_text}.",
        "uw_frage": "Bestimmen Sie den Tag, an dem noch {y_text} Getreide im Silo lagern.",
        "null_frage": "Bestimmen Sie, nach wie vielen Tagen das Silo rechnerisch leer ist.",
        "punkte": {
            "intro": "Aus einem Getreidesilo wird täglich eine gleichbleibende Menge entnommen. Zwei Kontrollen liegen vor:",
            "satz": "Nach {x1_text} lagern noch {y1_text}, nach {x2_text} nur noch {y2_text}.",
        },
    },
    {
        "kontext": (
            "In einem Kühlraum beträgt die Temperatur zu Beginn {b} °C. Nach dem "
            "Einschalten der Anlage sinkt sie näherungsweise gleichmäßig um {m_abs} °C pro Stunde."
        ),
        "var": "t",
        "func_name": "T",
        "x_beschreibung": "der Laufzeit $t$ in Stunden",
        "y_beschreibung": "die Temperatur in Grad Celsius",
        "x_unit": "h",
        "y_unit": "°C",
        "m_choices": _r(1.5, 3.5, 0.5),
        "b_choices": _r(16, 24, 1),
        "m_sign": -1,
        "y_min": -5,
        "x_choices": _r(2, 8, 1),
        "inverse_choices": _r(2, 10, 1),
        "fw_frage": "Berechnen Sie die Temperatur im Kühlraum nach {x_text}.",
        "uw_frage": "Bestimmen Sie die Laufzeit, nach der die Temperatur {y_text} beträgt.",
        "null_frage": "Bestimmen Sie, nach wie vielen Stunden die Temperatur rechnerisch 0 °C erreicht.",
        "punkte": {
            "intro": "Nach dem Einschalten sinkt die Temperatur in einem Kühlraum näherungsweise gleichmäßig. Zwei Messungen liegen vor:",
            "satz": "Nach {x1_text} beträgt die Temperatur {y1_text}, nach {x2_text} nur noch {y2_text}.",
        },
    },
    {
        "kontext": (
            "Eine Aushilfe erhält für einen Einsatz eine feste Anfahrtspauschale von "
            "{b} € und zusätzlich {m} € pro geleisteter Arbeitsstunde."
        ),
        "var": "t",
        "func_name": "L",
        "x_beschreibung": "der Arbeitszeit $t$ in Stunden",
        "y_beschreibung": "den Lohn in Euro",
        "x_unit": "h",
        "y_unit": "€",
        "m_choices": _r(11, 22, 1),
        "b_choices": _r(20, 60, 5),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(2, 11, 1),
        "inverse_choices": _r(3, 13, 1),
        "fw_frage": "Berechnen Sie den Lohn für {x_text} Arbeitszeit.",
        "uw_frage": "Bestimmen Sie die Arbeitszeit, bei der ein Lohn von {y_text} erreicht wird.",
        "punkte": {
            "intro": "Für die Vergütung einer Aushilfe sind zwei Einsätze mit unterschiedlicher Dauer bekannt:",
            "satz": "Für {x1_text} wird ein Lohn von {y1_text} gezahlt, für {x2_text} ein Lohn von {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Paketdienst berechnet für ein Standardpaket eine Grundpauschale von "
            "{b} € und zusätzlich {m} € pro Kilogramm Paketgewicht."
        ),
        "var": "x",
        "func_name": "K",
        "x_beschreibung": "dem Paketgewicht $x$ in Kilogramm",
        "y_beschreibung": "die Versandkosten in Euro",
        "x_unit": "kg",
        "y_unit": "€",
        "m_choices": _r(1.0, 2.8, 0.1),
        "b_choices": _r(3, 9, 0.5),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(2, 18, 1),
        "inverse_choices": _r(3, 20, 1),
        "fw_frage": "Berechnen Sie die Versandkosten für ein Paket mit {x_text} Gewicht.",
        "uw_frage": "Bestimmen Sie das Paketgewicht, bei dem Versandkosten von {y_text} entstehen.",
        "punkte": {
            "intro": "Für die Versandkosten eines Paketdienstes sind zwei Pakete bekannt:",
            "satz": "Ein Paket mit {x1_text} kostet {y1_text}, ein Paket mit {x2_text} kostet {y2_text}.",
        },
    },
    {
        "kontext": (
            "Ein Kopiergerät wird geleast. Der Vertrag enthält eine monatliche "
            "Grundrate von {b} € und Kosten von {m} € pro gedruckter Farbseite."
        ),
        "var": "x",
        "func_name": "K",
        "x_beschreibung": "der Anzahl $x$ gedruckter Farbseiten",
        "y_beschreibung": "die monatlichen Leasingkosten in Euro",
        "x_unit": "Farbseiten",
        "y_unit": "€",
        "m_choices": _r(0.06, 0.16, 0.01),
        "b_choices": _r(20, 55, 5),
        "m_sign": 1,
        "y_min": 0,
        "x_choices": _r(100, 700, 50),
        "inverse_choices": _r(150, 800, 50),
        "fw_frage": "Berechnen Sie die Leasingkosten bei {x_text}.",
        "uw_frage": "Bestimmen Sie die Anzahl gedruckter Farbseiten, bei der monatlich {y_text} anfallen.",
        "punkte": {
            "intro": "Für einen Kopierer-Leasingvertrag liegen zwei Monatsabrechnungen vor:",
            "satz": "Bei {x1_text} betragen die Kosten {y1_text}, bei {x2_text} betragen sie {y2_text}.",
        },
    },
]


# ---------------------------------------------------------------------------
# Szenario-Vorlagen - Vergleich (Check 10)
# ---------------------------------------------------------------------------

_SZENARIEN_VERGLEICH: list[dict] = [
    {
        "kontext": "Zwei Energieversorger bieten Tarife für Privathaushalte an:",
        "items": [
            "GrünStrom verlangt {b1} € Grundpreis pro Monat und {m1_cent} Cent pro kWh.",
            "Bei StadtEnergie ist der monatliche Grundpreis um {b_diff} € höher als bei GrünStrom, der Arbeitspreis dafür um {m_diff_cent} Cent niedriger.",
        ],
        "variants": [(0.36, 6.0, 0.30, 18.0, 150, 300)],
        "var": "x",
        "x_beschreibung": "dem monatlichen Stromverbrauch $x$ in Kilowattstunden",
        "y_beschreibung1": "die monatlichen Stromkosten bei GrünStrom in Euro",
        "y_beschreibung2": "die monatlichen Stromkosten bei StadtEnergie in Euro",
        "name1": "GrünStrom",
        "name2": "StadtEnergie",
        "func_name1": "K_G",
        "func_name2": "K_S",
        "breakeven_frage": "Bestimmen Sie den Stromverbrauch, bei dem beide Tarife gleich hohe monatliche Kosten verursachen.",
        "links_frage": "Ein Haushalt verbraucht monatlich {x_left_text}. Entscheiden Sie, welcher Tarif günstiger ist.",
        "rechts_frage": "Ein Haushalt verbraucht monatlich {x_right_text}. Entscheiden Sie, welcher Tarif günstiger ist.",
        "x_unit": "kWh",
    },
    {
        "kontext": "Zwei Mobilfunkanbieter werben mit unterschiedlichen Datentarifen:",
        "items": [
            "Connect S kostet {b1} € Grundgebühr und {m1} € pro Gigabyte.",
            "Bei Connect L ist die Grundgebühr um {b_diff} € höher als bei Connect S, jedes Gigabyte kostet dafür {m_diff} € weniger.",
        ],
        "variants": [(4.0, 8.0, 1.5, 28.0, 4, 12)],
        "var": "x",
        "x_beschreibung": "der Datenmenge $x$ in Gigabyte",
        "y_beschreibung1": "die monatlichen Kosten bei Connect S in Euro",
        "y_beschreibung2": "die monatlichen Kosten bei Connect L in Euro",
        "name1": "Connect S",
        "name2": "Connect L",
        "func_name1": "K_S",
        "func_name2": "K_L",
        "breakeven_frage": "Bestimmen Sie die Datenmenge, bei der beide Mobilfunktarife gleich teuer sind.",
        "links_frage": "Eine Kundin benötigt monatlich {x_left_text} Datenvolumen. Entscheiden Sie, welcher Tarif für sie günstiger ist.",
        "rechts_frage": "Ein Kunde benötigt monatlich {x_right_text} Datenvolumen. Entscheiden Sie, welcher Tarif für ihn günstiger ist.",
        "x_unit": "GB",
    },
    {
        "kontext": "Für einen Tagesausflug werden zwei Mietwagenangebote verglichen:",
        "items": [
            "CityCar verlangt {b1} € Tagespauschale und {m1} € pro gefahrenem Kilometer.",
            "Bei TourMobil ist die Tagespauschale um {b_diff} € höher als bei CityCar, der Kilometerpreis dafür um {m_diff} € niedriger.",
        ],
        "variants": [(0.45, 35.0, 0.25, 55.0, 60, 140)],
        "var": "x",
        "x_beschreibung": "der gefahrenen Strecke $x$ in Kilometern",
        "y_beschreibung1": "die Mietkosten bei CityCar in Euro",
        "y_beschreibung2": "die Mietkosten bei TourMobil in Euro",
        "name1": "CityCar",
        "name2": "TourMobil",
        "func_name1": "K_C",
        "func_name2": "K_T",
        "breakeven_frage": "Bestimmen Sie die Fahrtstrecke, bei der beide Mietwagenangebote gleich teuer sind.",
        "links_frage": "Die geplante Route ist {x_left_text} lang. Entscheiden Sie, welches Mietwagenangebot günstiger ist.",
        "rechts_frage": "Die geplante Route ist {x_right_text} lang. Entscheiden Sie, welches Mietwagenangebot günstiger ist.",
        "x_unit": "km",
    },
    {
        "kontext": "Zwei Parkhäuser in der Innenstadt verwenden unterschiedliche Preisstrukturen:",
        "items": [
            "Parkhaus Mitte berechnet {b1} € beim Einfahren und {m1} € pro Stunde.",
            "Parkhaus Galerie berechnet {b2} € beim Einfahren und {m2} € pro Stunde.",
        ],
        "variants": [(3.0, 2.0, 2.0, 8.0, 3, 8)],
        "var": "t",
        "x_beschreibung": "der Parkdauer $t$ in Stunden",
        "y_beschreibung1": "die Parkkosten im Parkhaus Mitte in Euro",
        "y_beschreibung2": "die Parkkosten im Parkhaus Galerie in Euro",
        "name1": "Parkhaus Mitte",
        "name2": "Parkhaus Galerie",
        "func_name1": "K_M",
        "func_name2": "K_G",
        "breakeven_frage": "Bestimmen Sie die Parkdauer, bei der beide Parkhäuser gleich teuer sind.",
        "links_frage": "Ein Auto soll {x_left_text} geparkt werden. Entscheiden Sie, welches Parkhaus günstiger ist.",
        "rechts_frage": "Ein Auto soll {x_right_text} geparkt werden. Entscheiden Sie, welches Parkhaus günstiger ist.",
        "x_unit": "h",
    },
    {
        "kontext": "Zwei Fitnessstudios bieten Monatsmodelle für Kurse an:",
        "items": [
            "FitActive verlangt {b1} € Monatsbeitrag und {m1} € pro Kursbesuch.",
            "Der Monatsbeitrag bei SportPlus ist um {b_diff} € höher als bei FitActive, ein Kursbesuch kostet dafür {m_diff} € weniger.",
        ],
        "variants": [(5.0, 20.0, 2.5, 40.0, 4, 12)],
        "var": "x",
        "x_beschreibung": "der Anzahl $x$ besuchter Kurse pro Monat",
        "y_beschreibung1": "die monatlichen Kosten bei FitActive in Euro",
        "y_beschreibung2": "die monatlichen Kosten bei SportPlus in Euro",
        "name1": "FitActive",
        "name2": "SportPlus",
        "func_name1": "K_F",
        "func_name2": "K_S",
        "breakeven_frage": "Bestimmen Sie die Kursanzahl, bei der beide Studios gleich teuer sind.",
        "links_frage": "Eine Person besucht monatlich {x_left_text}. Entscheiden Sie, welches Studio günstiger ist.",
        "rechts_frage": "Eine Person besucht monatlich {x_right_text}. Entscheiden Sie, welches Studio günstiger ist.",
        "x_unit": "Kurse",
    },
    {
        "kontext": "Zwei Druckereien erstellen Flyer für eine Schulveranstaltung:",
        "items": [
            "DruckExpress berechnet {b1} € Einrichtungspauschale und {m1} € pro 100 Flyer.",
            "PrintProfi berechnet {b2} € Einrichtungspauschale und {m2} € pro 100 Flyer.",
        ],
        "variants": [(6.0, 20.0, 3.0, 80.0, 10, 30)],
        "var": "x",
        "x_beschreibung": "der Bestellmenge $x$ in Einheiten zu je 100 Flyern",
        "y_beschreibung1": "die Druckkosten bei DruckExpress in Euro",
        "y_beschreibung2": "die Druckkosten bei PrintProfi in Euro",
        "name1": "DruckExpress",
        "name2": "PrintProfi",
        "func_name1": "K_D",
        "func_name2": "K_P",
        "breakeven_frage": "Bestimmen Sie die Bestellmenge, bei der beide Druckereien gleich teuer sind.",
        "links_frage": "Die Schule bestellt {x_left_text}. Entscheiden Sie, welche Druckerei günstiger ist.",
        "rechts_frage": "Die Schule bestellt {x_right_text}. Entscheiden Sie, welche Druckerei günstiger ist.",
        "x_unit": "Hunderterpakete",
    },
    {
        "kontext": "Ein Streamingdienst stellt zwei Download-Abos zur Wahl:",
        "items": [
            "Abo Basis kostet {b1} € im Monat und {m1} € pro heruntergeladenem Film.",
            "Beim Abo Premium ist die monatliche Grundgebühr um {b_diff} € höher als beim Abo Basis, jeder Film kostet dafür {m_diff} € weniger.",
        ],
        "variants": [(4.0, 12.0, 2.0, 28.0, 5, 12)],
        "var": "x",
        "x_beschreibung": "der Anzahl $x$ heruntergeladener Filme pro Monat",
        "y_beschreibung1": "die monatlichen Kosten im Abo Basis in Euro",
        "y_beschreibung2": "die monatlichen Kosten im Abo Premium in Euro",
        "name1": "Basis",
        "name2": "Premium",
        "func_name1": "K_B",
        "func_name2": "K_P",
        "breakeven_frage": "Bestimmen Sie die Filmzahl, bei der beide Abos gleich teuer sind.",
        "links_frage": "In einem Monat werden {x_left_text} heruntergeladen. Entscheiden Sie, welches Abo günstiger ist.",
        "rechts_frage": "In einem Monat werden {x_right_text} heruntergeladen. Entscheiden Sie, welches Abo günstiger ist.",
        "x_unit": "Filme",
    },
    {
        "kontext": "Ein Betrieb vergleicht zwei Maschinen für eine geplante Produktion:",
        "items": [
            "Maschine A kostet in der Anschaffung {b1} € und verursacht {m1} € Betriebskosten pro Stunde.",
            "Maschine B kostet in der Anschaffung {b2} € und verursacht {m2} € Betriebskosten pro Stunde.",
        ],
        "variants": [(9.0, 120.0, 4.0, 220.0, 10, 30)],
        "var": "t",
        "x_beschreibung": "der Nutzungsdauer $t$ in Betriebsstunden",
        "y_beschreibung1": "die Gesamtkosten von Maschine A in Euro",
        "y_beschreibung2": "die Gesamtkosten von Maschine B in Euro",
        "name1": "Maschine A",
        "name2": "Maschine B",
        "func_name1": "K_A",
        "func_name2": "K_B",
        "breakeven_frage": "Bestimmen Sie die Nutzungsdauer, bei der beide Maschinen gleich hohe Gesamtkosten haben.",
        "links_frage": "Die Maschine soll {x_left_text} laufen. Entscheiden Sie, welche Maschine kostengünstiger ist.",
        "rechts_frage": "Die Maschine soll {x_right_text} laufen. Entscheiden Sie, welche Maschine kostengünstiger ist.",
        "x_unit": "h",
    },
    {
        "kontext": "Zwei Paketdienste bieten Versandpreise für schwere Pakete an:",
        "items": [
            "PaketFix verlangt {b1} € Grundpauschale und {m1} € pro Kilogramm.",
            "Bei CargoPlus ist die Grundpauschale um {b_diff} € höher als bei PaketFix, der Preis pro Kilogramm dafür um {m_diff} € niedriger.",
        ],
        "variants": [(2.0, 4.0, 1.2, 12.0, 5, 15)],
        "var": "x",
        "x_beschreibung": "dem Paketgewicht $x$ in Kilogramm",
        "y_beschreibung1": "die Versandkosten bei PaketFix in Euro",
        "y_beschreibung2": "die Versandkosten bei CargoPlus in Euro",
        "name1": "PaketFix",
        "name2": "CargoPlus",
        "func_name1": "K_F",
        "func_name2": "K_C",
        "breakeven_frage": "Bestimmen Sie das Paketgewicht, bei dem beide Versanddienste gleich teuer sind.",
        "links_frage": "Ein Paket wiegt {x_left_text}. Entscheiden Sie, welcher Versanddienst günstiger ist.",
        "rechts_frage": "Ein Paket wiegt {x_right_text}. Entscheiden Sie, welcher Versanddienst günstiger ist.",
        "x_unit": "kg",
    },
    {
        "kontext": "Für ein Schulfest werden zwei Cateringangebote verglichen:",
        "items": [
            "Catering Klassik verlangt {b1} € Organisationspauschale und {m1} € pro Person.",
            "Catering Direkt verlangt {b2} € Organisationspauschale und {m2} € pro Person.",
        ],
        "variants": [(8.0, 120.0, 11.0, 30.0, 20, 50)],
        "var": "x",
        "x_beschreibung": "der Anzahl $x$ angemeldeter Personen",
        "y_beschreibung1": "die Cateringkosten bei Catering Klassik in Euro",
        "y_beschreibung2": "die Cateringkosten bei Catering Direkt in Euro",
        "name1": "Catering Klassik",
        "name2": "Catering Direkt",
        "func_name1": "K_K",
        "func_name2": "K_D",
        "breakeven_frage": "Bestimmen Sie die Personenzahl, bei der beide Caterer gleich teuer sind.",
        "links_frage": "Zum Schulfest werden {x_left_text} erwartet. Entscheiden Sie, welches Cateringangebot günstiger ist.",
        "rechts_frage": "Zum Schulfest werden {x_right_text} erwartet. Entscheiden Sie, welches Cateringangebot günstiger ist.",
        "x_unit": "Personen",
    },
    {
        "kontext": "Zwei Veranstaltungsräume stehen für eine Feier zur Auswahl:",
        "items": [
            "Raum Loft kostet {b1} € Grundmiete und {m1} € pro Nutzungsstunde.",
            "Raum Saal kostet {b2} € Grundmiete und {m2} € pro Nutzungsstunde.",
        ],
        "variants": [(45.0, 80.0, 30.0, 170.0, 4, 8)],
        "var": "t",
        "x_beschreibung": "der Mietdauer $t$ in Stunden",
        "y_beschreibung1": "die Mietkosten für Raum Loft in Euro",
        "y_beschreibung2": "die Mietkosten für Raum Saal in Euro",
        "name1": "Raum Loft",
        "name2": "Raum Saal",
        "func_name1": "K_L",
        "func_name2": "K_S",
        "breakeven_frage": "Bestimmen Sie die Mietdauer, bei der beide Räume gleich teuer sind.",
        "links_frage": "Die Feier dauert {x_left_text}. Entscheiden Sie, welcher Raum günstiger ist.",
        "rechts_frage": "Die Feier dauert {x_right_text}. Entscheiden Sie, welcher Raum günstiger ist.",
        "x_unit": "h",
    },
    {
        "kontext": "Zwei Fahrradverleihe bieten Preise für Ausflüge an:",
        "items": [
            "RadPunkt verlangt {b1} € Servicepauschale und {m1} € pro Stunde.",
            "BikeHafen verlangt {b2} € Servicepauschale und {m2} € pro Stunde.",
        ],
        "variants": [(6.0, 4.0, 4.0, 12.0, 2, 6)],
        "var": "t",
        "x_beschreibung": "der Ausleihdauer $t$ in Stunden",
        "y_beschreibung1": "die Ausleihkosten bei RadPunkt in Euro",
        "y_beschreibung2": "die Ausleihkosten bei BikeHafen in Euro",
        "name1": "RadPunkt",
        "name2": "BikeHafen",
        "func_name1": "K_R",
        "func_name2": "K_B",
        "breakeven_frage": "Bestimmen Sie die Ausleihdauer, bei der beide Fahrradverleihe gleich teuer sind.",
        "links_frage": "Ein Fahrrad wird für {x_left_text} ausgeliehen. Entscheiden Sie, welcher Verleih günstiger ist.",
        "rechts_frage": "Ein Fahrrad wird für {x_right_text} ausgeliehen. Entscheiden Sie, welcher Verleih günstiger ist.",
        "x_unit": "h",
    },
    {
        "kontext": "Zwei Copyshops bieten Tarife für Farbkopien an:",
        "items": [
            "Copy Schnell verlangt {b1} € Auftragspauschale und {m1} € pro Farbkopie.",
            "Copy Groß verlangt {b2} € Auftragspauschale und {m2} € pro Farbkopie.",
        ],
        "variants": [(0.18, 2.0, 0.10, 10.0, 50, 150)],
        "var": "x",
        "x_beschreibung": "der Anzahl $x$ angefertigter Farbkopien",
        "y_beschreibung1": "die Kopierkosten bei Copy Schnell in Euro",
        "y_beschreibung2": "die Kopierkosten bei Copy Groß in Euro",
        "name1": "Copy Schnell",
        "name2": "Copy Groß",
        "func_name1": "K_S",
        "func_name2": "K_G",
        "breakeven_frage": "Bestimmen Sie die Kopienzahl, bei der beide Copyshops gleich teuer sind.",
        "links_frage": "Ein Auftrag umfasst {x_left_text}. Entscheiden Sie, welcher Copyshop günstiger ist.",
        "rechts_frage": "Ein Auftrag umfasst {x_right_text}. Entscheiden Sie, welcher Copyshop günstiger ist.",
        "x_unit": "Farbkopien",
    },
    {
        "kontext": "Zwei Cloudspeicher-Anbieter rechnen Speicherplatz unterschiedlich ab:",
        "items": [
            "CloudStart verlangt {b1} € Grundpreis und {m1} € pro 100 GB Speicherplatz.",
            "CloudPro verlangt {b2} € Grundpreis und {m2} € pro 100 GB Speicherplatz.",
        ],
        "variants": [(5.0, 4.0, 2.0, 28.0, 4, 12)],
        "var": "x",
        "x_beschreibung": "dem gebuchten Speicherplatz $x$ in Blöcken zu je 100 GB",
        "y_beschreibung1": "die monatlichen Kosten bei CloudStart in Euro",
        "y_beschreibung2": "die monatlichen Kosten bei CloudPro in Euro",
        "name1": "CloudStart",
        "name2": "CloudPro",
        "func_name1": "K_S",
        "func_name2": "K_P",
        "breakeven_frage": "Bestimmen Sie die Speichermenge, bei der beide Cloudtarife gleich teuer sind.",
        "links_frage": "Ein Softwareprojekt belegt {x_left_text}. Entscheiden Sie, welcher Cloudtarif günstiger ist.",
        "rechts_frage": "Ein Softwareprojekt belegt {x_right_text}. Entscheiden Sie, welcher Cloudtarif günstiger ist.",
        "x_unit": "Blöcke à 100 GB",
    },
    {
        "kontext": "Zwei Nachhilfeangebote unterscheiden sich bei Anfahrt und Stundenpreis:",
        "items": [
            "LernMobil verlangt {b1} € Anfahrtspauschale und {m1} € pro Unterrichtsstunde.",
            "LernStudio verlangt {b2} € Anfahrtspauschale und {m2} € pro Unterrichtsstunde.",
        ],
        "variants": [(28.0, 10.0, 22.0, 40.0, 3, 8)],
        "var": "t",
        "x_beschreibung": "der Unterrichtszeit $t$ in Stunden",
        "y_beschreibung1": "die Kosten bei LernMobil in Euro",
        "y_beschreibung2": "die Kosten bei LernStudio in Euro",
        "name1": "LernMobil",
        "name2": "LernStudio",
        "func_name1": "K_M",
        "func_name2": "K_S",
        "breakeven_frage": "Bestimmen Sie die Unterrichtszeit, bei der beide Nachhilfeangebote gleich teuer sind.",
        "links_frage": "Geplant sind {x_left_text} Nachhilfe. Entscheiden Sie, welches Angebot günstiger ist.",
        "rechts_frage": "Geplant sind {x_right_text} Nachhilfe. Entscheiden Sie, welches Angebot günstiger ist.",
        "x_unit": "h",
    },
    {
        "kontext": "Zwei Lieferdienste bieten Mitgliedschaften für Essensbestellungen an:",
        "items": [
            "MealBasic verlangt {b1} € Monatsgebühr und {m1} € Lieferkosten pro Bestellung.",
            "Die Monatsgebühr bei MealPlus ist um {b_diff} € höher als bei MealBasic, pro Bestellung fallen dafür {m_diff} € weniger an.",
        ],
        "variants": [(3.0, 4.0, 1.0, 18.0, 4, 10)],
        "var": "x",
        "x_beschreibung": "der Anzahl $x$ Bestellungen pro Monat",
        "y_beschreibung1": "die monatlichen Kosten bei MealBasic in Euro",
        "y_beschreibung2": "die monatlichen Kosten bei MealPlus in Euro",
        "name1": "MealBasic",
        "name2": "MealPlus",
        "func_name1": "K_B",
        "func_name2": "K_P",
        "breakeven_frage": "Bestimmen Sie die Bestellanzahl, bei der beide Lieferdienstmodelle gleich teuer sind.",
        "links_frage": "In einem Monat werden {x_left_text} aufgegeben. Entscheiden Sie, welches Modell günstiger ist.",
        "rechts_frage": "In einem Monat werden {x_right_text} aufgegeben. Entscheiden Sie, welches Modell günstiger ist.",
        "x_unit": "Bestellungen",
    },
    {
        "kontext": "Für regelmäßige Bahnfahrten werden zwei Ticketmodelle betrachtet:",
        "items": [
            "Einzelticket-Modell: keine Monatsgebühr und {m1} € pro Fahrt.",
            "Pendlerkarte: {b2} € Monatsgebühr, dafür kostet jede Fahrt {m_diff} € weniger als im Einzelticket-Modell.",
        ],
        "variants": [(4.0, 0.0, 1.5, 50.0, 12, 30)],
        "var": "x",
        "x_beschreibung": "der Anzahl $x$ Fahrten pro Monat",
        "y_beschreibung1": "die monatlichen Kosten beim Einzelticket-Modell in Euro",
        "y_beschreibung2": "die monatlichen Kosten mit Pendlerkarte in Euro",
        "name1": "Einzeltickets",
        "name2": "Pendlerkarte",
        "func_name1": "K_E",
        "func_name2": "K_P",
        "breakeven_frage": "Bestimmen Sie die Fahrtenzahl, bei der beide Ticketmodelle gleich teuer sind.",
        "links_frage": "Eine Person fährt monatlich {x_left_text}. Entscheiden Sie, welches Ticketmodell günstiger ist.",
        "rechts_frage": "Eine Person fährt monatlich {x_right_text}. Entscheiden Sie, welches Ticketmodell günstiger ist.",
        "x_unit": "Fahrten",
    },
    {
        "kontext": "Zwei Softwarelizenzen werden für ein Team verglichen:",
        "items": [
            "Team Basic kostet {b1} € Grundgebühr und {m1} € pro Nutzerlizenz.",
            "Bei Team Pro ist die Grundgebühr um {b_diff} € höher als bei Team Basic, jede Nutzerlizenz kostet dafür {m_diff} € weniger.",
        ],
        "variants": [(14.0, 20.0, 9.0, 70.0, 5, 15)],
        "var": "x",
        "x_beschreibung": "der Anzahl $x$ benötigter Nutzerlizenzen",
        "y_beschreibung1": "die monatlichen Lizenzkosten für Team Basic in Euro",
        "y_beschreibung2": "die monatlichen Lizenzkosten für Team Pro in Euro",
        "name1": "Team Basic",
        "name2": "Team Pro",
        "func_name1": "K_B",
        "func_name2": "K_P",
        "breakeven_frage": "Bestimmen Sie die Nutzerzahl, bei der beide Softwarelizenzen gleich teuer sind.",
        "links_frage": "Das Team benötigt {x_left_text}. Entscheiden Sie, welche Lizenz günstiger ist.",
        "rechts_frage": "Das Team benötigt {x_right_text}. Entscheiden Sie, welche Lizenz günstiger ist.",
        "x_unit": "Lizenzen",
    },
    {
        "kontext": "Zwei Umzugsunternehmen geben Angebote für einen Transport ab:",
        "items": [
            "MoveDirekt verlangt {b1} € Bereitstellungspauschale und {m1} € pro Kilometer.",
            "Bei StadtUmzug ist die Bereitstellungspauschale um {b_diff} € höher als bei MoveDirekt, der Kilometerpreis dafür um {m_diff} € niedriger.",
        ],
        "variants": [(2.2, 60.0, 1.4, 140.0, 50, 150)],
        "var": "x",
        "x_beschreibung": "der Transportstrecke $x$ in Kilometern",
        "y_beschreibung1": "die Umzugskosten bei MoveDirekt in Euro",
        "y_beschreibung2": "die Umzugskosten bei StadtUmzug in Euro",
        "name1": "MoveDirekt",
        "name2": "StadtUmzug",
        "func_name1": "K_M",
        "func_name2": "K_S",
        "breakeven_frage": "Bestimmen Sie die Transportstrecke, bei der beide Umzugsunternehmen gleich teuer sind.",
        "links_frage": "Der Transportweg beträgt {x_left_text}. Entscheiden Sie, welches Unternehmen günstiger ist.",
        "rechts_frage": "Der Transportweg beträgt {x_right_text}. Entscheiden Sie, welches Unternehmen günstiger ist.",
        "x_unit": "km",
    },
    {
        "kontext": "Zwei Wartungsverträge für eine Heizungsanlage werden verglichen:",
        "items": [
            "Vertrag Standard kostet {b1} € Grundpauschale und {m1} € pro Einsatzstunde.",
            "Beim Vertrag Komfort ist die Grundpauschale um {b_diff} € höher als beim Vertrag Standard, jede Einsatzstunde kostet dafür {m_diff} € weniger.",
        ],
        "variants": [(55.0, 30.0, 35.0, 110.0, 2, 6)],
        "var": "t",
        "x_beschreibung": "der Einsatzzeit $t$ in Stunden pro Jahr",
        "y_beschreibung1": "die jährlichen Wartungskosten im Vertrag Standard in Euro",
        "y_beschreibung2": "die jährlichen Wartungskosten im Vertrag Komfort in Euro",
        "name1": "Standard",
        "name2": "Komfort",
        "func_name1": "K_S",
        "func_name2": "K_K",
        "breakeven_frage": "Bestimmen Sie die Einsatzzeit, bei der beide Wartungsverträge gleich teuer sind.",
        "links_frage": "Im Jahr werden {x_left_text} Einsatzzeit erwartet. Entscheiden Sie, welcher Vertrag günstiger ist.",
        "rechts_frage": "Im Jahr werden {x_right_text} Einsatzzeit erwartet. Entscheiden Sie, welcher Vertrag günstiger ist.",
        "x_unit": "h",
    },
    {
        "kontext": "Zwei Schwimmbadpumpen können ein Becken mit Wasser füllen:",
        "items": [
            "Pumpe A ist bereits mit {b1} m³ Vorfüllung verbunden und fördert {m1} m³ pro Stunde.",
            "Pumpe B startet bei {b2} m³ Vorfüllung und fördert {m2} m³ pro Stunde.",
        ],
        "variants": [(8.0, 20.0, 12.0, 0.0, 3, 8)],
        "var": "t",
        "x_beschreibung": "der Füllzeit $t$ in Stunden",
        "y_beschreibung1": "das erreichte Wasservolumen mit Pumpe A in Kubikmetern",
        "y_beschreibung2": "das erreichte Wasservolumen mit Pumpe B in Kubikmetern",
        "name1": "Pumpe A",
        "name2": "Pumpe B",
        "func_name1": "W_A",
        "func_name2": "W_B",
        "breakeven_frage": "Bestimmen Sie die Füllzeit, nach der beide Pumpenmodelle dasselbe Wasservolumen ergeben.",
        "links_frage": "Das Becken soll nach {x_left_text} möglichst viel Wasser enthalten. Entscheiden Sie, welche Pumpe vorteilhafter ist.",
        "rechts_frage": "Das Becken soll nach {x_right_text} möglichst viel Wasser enthalten. Entscheiden Sie, welche Pumpe vorteilhafter ist.",
        "x_unit": "h",
    },
]


# ===================================================================
# Check 09 - Sachsituation (eine Funktion)
# ===================================================================

class SachsituationEineFunktionGenerator(TaskGenerator):
    """Sachsituation modellieren und auswerten (inkl. Umkehrwert)."""

    generator_key = "analysis.lineare_funktionen.sachsituation_eine_funktion"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for idx in _scenario_order(rng, count, len(_SZENARIEN_EINZELN)):
            sz = _SZENARIEN_EINZELN[idx]

            m_abs = rng.choice(sz["m_choices"])
            b = rng.choice(sz["b_choices"])
            m = sz["m_sign"] * m_abs
            y_min = sz.get("y_min")
            y_max = sz.get("y_max")

            var = sz["var"]
            fn = sz["func_name"]

            # Funktionsgleichung immer aus zwei kontextbezogenen Punkten
            # aufstellen (keine explizite Nennung von Steigung/y-Achsenabschnitt).
            points = None
            if "punkte" in sz:
                points = _choose_two_points(rng, sz["x_choices"], m, b, y_min, y_max)

            used_x: set[float] = set()
            if points is not None:
                x1, y1, x2, y2 = points
                used_x = {x1, x2}
                text = (
                    sz["punkte"]["intro"]
                    + "\n\n"
                    + sz["punkte"]["satz"].format(
                        x1_text=_fmt_wert(x1, sz["x_unit"]),
                        y1_text=_fmt_wert(y1, sz["y_unit"]),
                        x2_text=_fmt_wert(x2, sz["x_unit"]),
                        y2_text=_fmt_wert(y2, sz["y_unit"]),
                    )
                )
            else:
                text = sz["kontext"].format(
                    m=_fmt_dez(m_abs),
                    m_abs=_fmt_dez(m_abs),
                    m_cent=_fmt_dez(m_abs * 100),
                    b=_fmt_dez(b),
                )

            x0 = (-b / m) if m != 0 else None

            try:
                x_fw = _choose_x(rng, sz["x_choices"], m, b, y_min, y_max, exclude=used_x)
            except ValueError:
                x_fw = _choose_x(rng, sz["x_choices"], m, b, y_min, y_max)
            y_fw = m * x_fw + b

            uw_exclude = set(used_x) | {x_fw}
            if x0 is not None:
                uw_exclude.add(x0)
            try:
                x_inv = _choose_x(
                    rng, sz["inverse_choices"], m, b, y_min, y_max, exclude=uw_exclude
                )
            except ValueError:
                x_inv = _choose_x(
                    rng, sz["inverse_choices"], m, b, y_min, y_max, exclude={x_fw}
                )
            y_inv = m * x_inv + b

            fragen = [
                _equation_question(sz, fn, var),
                _format_template(
                    sz["fw_frage"],
                    x_text=_fmt_wert(x_fw, sz["x_unit"]),
                    y_text=_fmt_wert(y_fw, sz["y_unit"]),
                ),
                _format_template(
                    sz["uw_frage"],
                    x_text=_fmt_wert(x_inv, sz["x_unit"]),
                    y_text=_fmt_wert(y_inv, sz["y_unit"]),
                ),
            ]
            antworten = [
                _model_answer(fn, var, m, b),
                f"$ {fn}({_fmt_dez(x_fw)}) = ${numerical_analysis_calc(y_fw)}",
                f"$ {var} = ${numerical_analysis_calc(x_inv)}",
            ]

            if m != 0:
                null_frage = sz.get("null_frage")
                if (
                    null_frage
                    and x0 is not None
                    and x0 > 0
                    and _valid_y(0, y_min, y_max)
                    and abs(round(x0 * 100) - x0 * 100) < 1e-6
                ):
                    fragen.append(null_frage)
                    antworten.append(f"$ {var} = ${numerical_analysis_calc(x0)}")

            tasks.append(Task(
                einleitung=text,
                fragen=fragen,
                antworten=antworten,
            ))

        return tasks


# ===================================================================
# Check 10 - Sachsituation Vergleich (Break-Even)
# ===================================================================

class SachsituationVergleichGenerator(TaskGenerator):
    """Zwei Modelle vergleichen, Break-Even-Punkt bestimmen."""

    generator_key = "analysis.lineare_funktionen.sachsituation_vergleich"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for idx in _scenario_order(rng, count, len(_SZENARIEN_VERGLEICH)):
            sz = _SZENARIEN_VERGLEICH[idx]
            m1, b1, m2, b2, x_left, x_right = rng.choice(sz["variants"])

            if m1 == m2:
                raise ValueError("Vergleichsszenario benötigt verschiedene Steigungen.")

            x_s = (b2 - b1) / (m1 - m2)
            y_s = m1 * x_s + b1
            if x_s <= 0 or y_s < 0:
                raise ValueError("Vergleichsszenario erzeugt keinen sinnvollen Schnittpunkt.")

            if not (x_left < x_s < x_right):
                raise ValueError("Konkrete Vergleichswerte müssen links und rechts des Schnittpunkts liegen.")

            format_values = {
                "m1": _fmt_dez(m1),
                "b1": _fmt_dez(b1),
                "m2": _fmt_dez(m2),
                "b2": _fmt_dez(b2),
                "m1_cent": _fmt_dez(m1 * 100),
                "m2_cent": _fmt_dez(m2 * 100),
                "b_diff": _fmt_dez(abs(b2 - b1)),
                "m_diff": _fmt_dez(abs(m1 - m2)),
                "m_diff_cent": _fmt_dez(abs(m1 - m2) * 100),
            }

            items_html = "\n".join(
                f"<li>{item.format(**format_values)}</li>"
                for item in sz["items"]
            )
            text = f"{sz['kontext']}\n\n<ul>\n{items_html}\n</ul>"

            fn1 = sz["func_name1"]
            fn2 = sz["func_name2"]
            name1 = sz["name1"]
            name2 = sz["name2"]
            var = sz["var"]
            options_wer = [name1, name2]

            def cheaper_index(x_value: float) -> int:
                y1 = m1 * x_value + b1
                y2 = m2 * x_value + b2
                if y1 == y2:
                    raise ValueError("Konkreter Vergleichswert darf nicht am Schnittpunkt liegen.")
                return 0 if y1 < y2 else 1

            # Nur eine Entscheidungsfrage: mal links, mal rechts vom Schnittpunkt,
            # damit die richtige Wahl zwischen beiden Angeboten wechselt.
            if rng.random() < 0.5:
                dec_frage = sz["links_frage"].format(
                    x_left_text=_fmt_wert(x_left, sz["x_unit"])
                )
                dec_x = x_left
            else:
                dec_frage = sz["rechts_frage"].format(
                    x_right_text=_fmt_wert(x_right, sz["x_unit"])
                )
                dec_x = x_right

            fragen = [
                (
                    f"Bestimmen Sie die Gleichung der Funktion ${fn1}({var})$, die "
                    f"{sz['y_beschreibung1']} in Abhängigkeit von {sz['x_beschreibung']} angibt."
                ),
                (
                    f"Bestimmen Sie die Gleichung der Funktion ${fn2}({var})$, die "
                    f"{sz['y_beschreibung2']} in Abhängigkeit von {sz['x_beschreibung']} angibt."
                ),
                sz["breakeven_frage"],
                dec_frage,
            ]
            antworten = [
                _model_answer(fn1, var, m1, b1),
                _model_answer(fn2, var, m2, b2),
                f"$ {var} = ${numerical_analysis_calc(x_s)}",
                mc(options_wer, cheaper_index(dec_x)),
            ]

            tasks.append(Task(
                einleitung=text,
                fragen=fragen,
                antworten=antworten,
            ))

        return tasks