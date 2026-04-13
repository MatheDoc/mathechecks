"""Generatoren für Checks 09–10 (Sachsituationen).

09  Sachsituation – eine Funktion  (sachsituation-eine-funktion)
10  Sachsituation – Vergleich      (sachsituation-vergleich)
"""

from __future__ import annotations

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc, mc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.lineare_funktionen.shared import (
    fmt_number,
)


# ---------------------------------------------------------------------------
# Szenario-Vorlagen – eine Funktion (Check 09)
# ---------------------------------------------------------------------------

_SZENARIEN_EINZELN: list[dict] = [
    {
        "kontext": (
            "Ein Taxiunternehmen in der Innenstadt berechnet für jede Fahrt "
            "einen festen Grundpreis von {b} € sowie einen Kilometerpreis von "
            "{m} € pro gefahrenem Kilometer. Eine Kundin möchte vorab die "
            "Kosten für verschiedene Fahrstrecken berechnen."
        ),
        "var": "x",
        "einheit_x": "km",
        "einheit_y": "€",
        "func_name": "K",
        "func_beschreibung": "Kosten in €",
        "m_choices": [1.2, 1.5, 1.8, 2.0, 2.5, 3.0],
        "b_choices": [2.0, 3.0, 3.5, 4.0, 5.0],
        "m_sign": 1,
        "fw_label": "Kosten",
        "uw_label": "Fahrstrecke",
        "fw_frage": "Wie hoch sind die Kosten für eine Fahrt von {x} km?",
        "uw_frage": "Für welche Fahrstrecke betragen die Kosten genau {y} €?",
    },
    {
        "kontext": (
            "Ein Wasserreservoir in einem Dorf fasst zu Beginn der Messung "
            "{b} Liter. Durch einen gleichmäßigen Abfluss verliert das "
            "Reservoir pro Stunde genau {m_abs} Liter Wasser. Die "
            "Gemeinde möchte wissen, wann das Reservoir leer sein wird."
        ),
        "var": "t",
        "einheit_x": "h",
        "einheit_y": "Liter",
        "func_name": "V",
        "func_beschreibung": "Volumen in Liter",
        "m_choices": [5.0, 8.0, 10.0, 12.0, 15.0, 20.0],
        "b_choices": [80.0, 100.0, 120.0, 150.0, 200.0],
        "m_sign": -1,
        "fw_label": "Wasserstand",
        "uw_label": "Zeitpunkt",
        "fw_frage": "Wie viel Wasser enthält das Reservoir nach {x} Stunden?",
        "uw_frage": "Nach wie vielen Stunden enthält das Reservoir noch {y} Liter?",
        "null_frage": "Nach wie vielen Stunden ist das Reservoir leer?",
    },
    {
        "kontext": (
            "Ein voll geladener Laptop-Akku zeigt zu Beginn einen "
            "Ladestand von {b} % an. Bei normaler Nutzung sinkt der "
            "Ladestand pro Stunde gleichmäßig um {m_abs} Prozentpunkte. "
            "Die Nutzerin möchte planen, wann sie das Ladegerät "
            "anschließen muss."
        ),
        "var": "t",
        "einheit_x": "h",
        "einheit_y": "%",
        "func_name": "L",
        "func_beschreibung": "Ladestand in %",
        "m_choices": [5.0, 8.0, 10.0, 12.0, 15.0],
        "b_choices": [80.0, 90.0, 100.0],
        "m_sign": -1,
        "fw_label": "Ladestand",
        "uw_label": "Zeitpunkt",
        "fw_frage": "Wie hoch ist der Ladestand nach {x} Stunden?",
        "uw_frage": "Nach wie vielen Stunden beträgt der Ladestand noch {y} %?",
        "null_frage": "Nach wie vielen Stunden ist der Akku leer?",
    },
    {
        "kontext": (
            "Eine kleine Manufaktur stellt handgefertigte Vasen her. "
            "Die monatlichen Fixkosten (Miete, Versicherung, Strom) "
            "betragen {b} €, und für jede produzierte Vase fallen "
            "zusätzlich Materialkosten von {m} € an."
        ),
        "var": "x",
        "einheit_x": "Stück",
        "einheit_y": "€",
        "func_name": "K",
        "func_beschreibung": "Kosten in €",
        "m_choices": [2.0, 3.0, 4.0, 5.0, 8.0],
        "b_choices": [50.0, 80.0, 100.0, 150.0, 200.0],
        "m_sign": 1,
        "fw_label": "Gesamtkosten",
        "uw_label": "Stückzahl",
        "fw_frage": "Wie hoch sind die Gesamtkosten bei {x} produzierten Vasen?",
        "uw_frage": "Wie viele Vasen können mit einem Budget von {y} € produziert werden?",
    },
    {
        "kontext": (
            "Ein Forstwissenschaftler beobachtet eine junge Eiche, "
            "die zu Beginn der Studie eine Höhe von {b} cm hat. "
            "Pro Jahr wächst der Baum gleichmäßig um {m} cm. "
            "Der Forstwissenschaftler möchte die Entwicklung über "
            "die nächsten Jahre vorhersagen."
        ),
        "var": "t",
        "einheit_x": "Jahre",
        "einheit_y": "cm",
        "func_name": "h",
        "func_beschreibung": "Höhe in cm",
        "m_choices": [5.0, 8.0, 10.0, 12.0, 15.0, 20.0],
        "b_choices": [30.0, 50.0, 80.0, 100.0, 120.0],
        "m_sign": 1,
        "fw_label": "Höhe",
        "uw_label": "Zeitpunkt",
        "fw_frage": "Welche Höhe hat die Eiche nach {x} Jahren?",
        "uw_frage": "Nach wie vielen Jahren erreicht die Eiche eine Höhe von {y} cm?",
    },
    {
        "kontext": (
            "Ein Schwimmbad wird für die Wintersaison geleert. "
            "Zu Beginn enthält das Becken {b} m³ Wasser. "
            "Über eine Pumpe werden pro Stunde gleichmäßig "
            "{m_abs} m³ abgepumpt."
        ),
        "var": "t",
        "einheit_x": "h",
        "einheit_y": "m³",
        "func_name": "W",
        "func_beschreibung": "Wasservolumen in m³",
        "m_choices": [4.0, 5.0, 6.0, 8.0, 10.0],
        "b_choices": [60.0, 80.0, 100.0, 120.0, 150.0],
        "m_sign": -1,
        "fw_label": "Wasservolumen",
        "uw_label": "Zeitpunkt",
        "fw_frage": "Wie viel Wasser ist nach {x} Stunden noch im Becken?",
        "uw_frage": "Nach wie vielen Stunden enthält das Becken noch {y} m³?",
        "null_frage": "Nach wie vielen Stunden ist das Becken vollständig entleert?",
    },
]


# ---------------------------------------------------------------------------
# Szenario-Vorlagen – Vergleich (Check 10)
# ---------------------------------------------------------------------------

_SZENARIEN_VERGLEICH: list[dict] = [
    {
        "kontext": (
            "Für einen Streaming-Dienst stehen zwei Abomodelle zur Auswahl:"
        ),
        "items": [
            "Abo Basis: monatliche Grundgebühr {b1} € und {m1} € pro heruntergeladenem Film.",
            "Abo Premium: monatliche Grundgebühr {b2} € und {m2} € pro heruntergeladenem Film.",
        ],
        "var": "x",
        "einheit_x": "Filme",
        "einheit_y": "€",
        "name1": "Basis",
        "name2": "Premium",
        "func_name1": "K_B",
        "func_name2": "K_P",
        "interpret_guenstiger": "günstiger",
        "breakeven_frage": "Ab wie vielen Filmen sind die monatlichen Kosten beider Abos gleich hoch?",
        "links_frage": "Bei weniger als {x} Filmen ist {interpret}:",
        "rechts_frage": "Bei mehr als {x} Filmen ist {interpret}:",
    },
    {
        "kontext": (
            "Zwei Energieversorger bieten Stromtarife mit unterschiedlicher "
            "Preisstruktur an:"
        ),
        "items": [
            "GrünStrom: monatlicher Grundpreis {b1} € und {m1} Cent pro verbrauchter kWh.",
            "StadtEnergie: monatlicher Grundpreis {b2} € und {m2} Cent pro verbrauchter kWh.",
        ],
        "var": "x",
        "einheit_x": "kWh",
        "einheit_y": "Cent",
        "name1": "GrünStrom",
        "name2": "StadtEnergie",
        "func_name1": "K_G",
        "func_name2": "K_S",
        "interpret_guenstiger": "günstiger",
        "breakeven_frage": "Ab wie vielen kWh sind die monatlichen Kosten beider Tarife gleich hoch?",
        "links_frage": "Bei einem Verbrauch unter {x} kWh ist {interpret}:",
        "rechts_frage": "Bei einem Verbrauch über {x} kWh ist {interpret}:",
    },
    {
        "kontext": (
            "Ein Betrieb vergleicht die Gesamtkosten zweier Maschinen über "
            "ihre Nutzungsdauer:"
        ),
        "items": [
            "Maschine A: Anschaffungskosten {b1} € und laufende Betriebskosten von {m1} € pro Stunde.",
            "Maschine B: Anschaffungskosten {b2} € und laufende Betriebskosten von {m2} € pro Stunde.",
        ],
        "var": "t",
        "einheit_x": "h",
        "einheit_y": "€",
        "name1": "A",
        "name2": "B",
        "func_name1": "K_A",
        "func_name2": "K_B",
        "interpret_guenstiger": "günstiger",
        "breakeven_frage": "Nach wie vielen Betriebsstunden sind die Gesamtkosten beider Maschinen gleich hoch?",
        "links_frage": "Bei weniger als {x} Betriebsstunden ist {interpret}:",
        "rechts_frage": "Bei mehr als {x} Betriebsstunden ist {interpret}:",
    },
    {
        "kontext": (
            "Zwei Fitnessstudios werben mit unterschiedlichen Mitgliedschaftsmodellen:"
        ),
        "items": [
            "FitActive: monatliche Grundgebühr {b1} € und {m1} € pro Kursbesuch.",
            "SportPlus: monatliche Grundgebühr {b2} € und {m2} € pro Kursbesuch.",
        ],
        "var": "x",
        "einheit_x": "Besuche",
        "einheit_y": "€",
        "name1": "FitActive",
        "name2": "SportPlus",
        "func_name1": "K_F",
        "func_name2": "K_S",
        "interpret_guenstiger": "günstiger",
        "breakeven_frage": "Ab wie vielen Kursbesuchen sind die monatlichen Kosten beider Studios gleich hoch?",
        "links_frage": "Bei weniger als {x} Kursbesuchen ist {interpret}:",
        "rechts_frage": "Bei mehr als {x} Kursbesuchen ist {interpret}:",
    },
    {
        "kontext": (
            "Zwei Druckereien bieten Angebote für den Druck von Flyern an:"
        ),
        "items": [
            "DruckExpress: Einrichtungspauschale {b1} € und {m1} € pro 100 Flyer.",
            "PrintProfi: Einrichtungspauschale {b2} € und {m2} € pro 100 Flyer.",
        ],
        "var": "x",
        "einheit_x": "100 Flyer",
        "einheit_y": "€",
        "name1": "DruckExpress",
        "name2": "PrintProfi",
        "func_name1": "K_D",
        "func_name2": "K_P",
        "interpret_guenstiger": "günstiger",
        "breakeven_frage": "Ab welcher Bestellmenge (in 100 Flyer) sind die Kosten beider Druckereien gleich hoch?",
        "links_frage": "Bei weniger als {x} Bestelleinheiten ist {interpret}:",
        "rechts_frage": "Bei mehr als {x} Bestelleinheiten ist {interpret}:",
    },
]


# ---------------------------------------------------------------------------
# Helfer
# ---------------------------------------------------------------------------

def _fmt_dez(value: float) -> str:
    """Zahl mit deutschem Komma für Fließtext."""
    if value == int(value):
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".").replace(".", ",")


# ===================================================================
# Check 09 – Sachsituation (eine Funktion)
# ===================================================================

class SachsituationEineFunktionGenerator(TaskGenerator):
    """Sachsituation modellieren und auswerten (inkl. Umkehrwert)."""

    generator_key = "analysis.lineare_funktionen.sachsituation_eine_funktion"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[int, float, float]] = set()

        while len(tasks) < count:
            idx = rng.randrange(len(_SZENARIEN_EINZELN))
            sz = _SZENARIEN_EINZELN[idx]

            m_abs = rng.choice(sz["m_choices"])
            b = rng.choice(sz["b_choices"])
            m = sz["m_sign"] * m_abs

            key = (idx, m, b)
            if key in used:
                continue
            used.add(key)

            text = sz["kontext"].format(
                m=_fmt_dez(m_abs),
                m_abs=_fmt_dez(m_abs),
                b=_fmt_dez(b),
            )

            var = sz["var"]
            fn = sz["func_name"]

            # Frage 1: Funktionsgleichung aufstellen (m und b in einer Frage)
            # Frage 2: Funktionswert berechnen (Anwendungskontext)
            x_fw = rng.choice([3, 5, 8, 10, 12, 15, 20])
            y_fw = m * x_fw + b

            fragen = [
                f"Bestimmen Sie die Gleichung.",
                sz["fw_frage"].format(x=x_fw),
            ]
            antworten = [
                f"$ {fn}({var}) = ${numerical_analysis_calc(m)}$ \\cdot {var} + ${numerical_analysis_calc(b)}",
                f"$ {fn}({x_fw}) = ${numerical_analysis_calc(y_fw)}",
            ]

            # Frage 3: Umkehrwert (Anwendungskontext)
            x_inv_candidates = [v for v in range(1, 25) if v != x_fw]
            rng.shuffle(x_inv_candidates)
            for x_cand in x_inv_candidates:
                y_cand = m * x_cand + b
                if y_cand > 0 and y_cand == int(y_cand):
                    y_target = int(y_cand)
                    fragen.append(
                        sz["uw_frage"].format(y=_fmt_dez(y_target))
                    )
                    antworten.append(
                        f"$ {var} = ${numerical_analysis_calc(x_cand)}"
                    )
                    break

            # Frage 4: Nullstelle (Anwendungskontext, nur bei m < 0)
            if m != 0:
                x0 = -b / m
                if x0 > 0 and x0 == int(x0):
                    x0_int = int(x0)
                    null_frage = sz.get("null_frage")
                    if null_frage:
                        fragen.append(null_frage)
                    else:
                        fragen.append(
                            f"Für welchen Wert von $ {var} $ gilt "
                            f"$ {fn}({var}) = 0 $?"
                        )
                    antworten.append(
                        f"$ {var} = ${numerical_analysis_calc(x0_int)}"
                    )

            tasks.append(Task(
                einleitung=text,
                fragen=fragen,
                antworten=antworten,
            ))

        return tasks


# ===================================================================
# Check 10 – Sachsituation Vergleich (Break-Even)
# ===================================================================

class SachsituationVergleichGenerator(TaskGenerator):
    """Zwei Modelle vergleichen, Break-Even-Punkt bestimmen."""

    generator_key = "analysis.lineare_funktionen.sachsituation_vergleich"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []
        used: set[tuple[int, float, float, float, float]] = set()

        while len(tasks) < count:
            idx = rng.randrange(len(_SZENARIEN_VERGLEICH))
            sz = _SZENARIEN_VERGLEICH[idx]

            m_pool = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
            b_pool = [0.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 80.0, 100.0]

            m1 = rng.choice(m_pool)
            m2 = rng.choice(m_pool)
            if m1 == m2:
                continue
            b1 = rng.choice(b_pool)
            b2 = rng.choice(b_pool)

            key = (idx, m1, b1, m2, b2)
            if key in used:
                continue

            x_s = (b2 - b1) / (m1 - m2)
            y_s = m1 * x_s + b1

            if x_s <= 0 or x_s > 100:
                continue
            if x_s != int(x_s) and x_s * 2 != int(x_s * 2):
                continue
            if y_s < 0:
                continue

            used.add(key)

            # HTML-Liste statt **bold**
            items_html = "\n".join(
                f"<li>{item.format(m1=_fmt_dez(m1), b1=_fmt_dez(b1), m2=_fmt_dez(m2), b2=_fmt_dez(b2))}</li>"
                for item in sz["items"]
            )
            text = f"{sz['kontext']}\n\n<ul>\n{items_html}\n</ul>"

            fn1 = sz["func_name1"]
            fn2 = sz["func_name2"]
            name1 = sz["name1"]
            name2 = sz["name2"]
            var = sz["var"]
            interpret = sz["interpret_guenstiger"]

            if m1 > m2:
                idx_links = 0
                idx_rechts = 1
            else:
                idx_links = 1
                idx_rechts = 0

            x_s_display = int(x_s) if x_s == int(x_s) else _fmt_dez(x_s)
            options_wer = [name1, name2]

            fragen = [
                f"Gleichung für {name1}",
                f"Gleichung für {name2}",
                sz["breakeven_frage"],
                sz["links_frage"].format(x=x_s_display, interpret=interpret),
                sz["rechts_frage"].format(x=x_s_display, interpret=interpret),
            ]
            antworten = [
                f"$ {fn1}({var}) = ${numerical_analysis_calc(m1)}$ \\cdot {var} + ${numerical_analysis_calc(b1)}",
                f"$ {fn2}({var}) = ${numerical_analysis_calc(m2)}$ \\cdot {var} + ${numerical_analysis_calc(b2)}",
                f"$ {var} = ${numerical_analysis_calc(x_s)}",
                mc(options_wer, idx_links),
                mc(options_wer, idx_rechts),
            ]

            tasks.append(Task(
                einleitung=text,
                fragen=fragen,
                antworten=antworten,
            ))

        return tasks
