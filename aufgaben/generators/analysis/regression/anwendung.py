"""Regression im Sachzusammenhang.

20 Szenarien mit Datentabelle; der Regressionstyp (linear, quadratisch,
kubisch) wird vorgegeben. Punktanzahl variiert: linear 2-4, quadratisch 3-4,
kubisch genau 4 Punkte (Tabellenlänge dynamisch). Bei Minimalanzahl ist der
Fit eine exakte Interpolation (gewollt, kein Hinweis im Text). Annahmefilter:
R² >= 0,95 und Formtreue (siehe shared.model_plausible). Fragen:
Koeffizienten der Regressionsfunktion, Prognose (x -> y) und Umkehrfrage
(y -> x, nur linear/quadratisch; bei kubischen Modellen stattdessen eine
zweite Einsetz-Frage).
"""

import random

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical_analysis_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.analysis.regression.shared import (
    assert_fit_matches,
    fd_deviations,
    fmt_number,
    make_table,
    model_plausible,
    poly_eval,
    poly_function_answer,
)

_DEGREE = {"linear": 1, "quadratisch": 2, "kubisch": 3}

# Punktanzahl je Modellgrad (maximal 4 Datenpunkte).
_N_CHOICES = {1: [2, 3, 4], 2: [3, 4], 3: [4]}

_ANSATZ_TEMPLATE = {
    "linear": "{fn}({var}) = m \\cdot {var} + b",
    "quadratisch": "{fn}({var}) = a {var}^2 + b {var} + c",
    "kubisch": "{fn}({var}) = a {var}^3 + b {var}^2 + c {var} + d",
}

# Koeffizienten-Auswahllisten jeweils von a_0 (konstant) zu a_d (Leitkoeffizient).
_SZENARIEN: list[dict] = [
    # ------------------------------------------------------------------
    # Linear (8)
    # ------------------------------------------------------------------
    {
        "kontext": (
            "Ein Streaming-Dienst wertet die Entwicklung seiner Nutzerzahlen aus. "
            "Für die ersten Monate nach dem Start liegen folgende Daten vor "
            "($ t $: Monate seit Start, Nutzerzahl in Tausend):"
        ),
        "modell": "linear",
        "var": "t",
        "fn": "N",
        "x_label": "Monat $ t $",
        "y_label": "Nutzer (Tsd.)",
        "x_values": [0, 1, 2, 3, 4, 5],
        "coeffs": [[120, 140, 150, 160, 180], [8, 10, 12, 15, 20]],
        "dev_scales": [1.0, 2.0],
        "prognose_x": [8, 9, 10, 12],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell die Nutzerzahl (in Tausend) im Monat {x}."
        ),
        "umkehr_x": [9, 10, 12, 14],
        "umkehr_frage": (
            "In welchem Monat erreicht die Nutzerzahl nach dem Modell erstmals {y} Tausend?"
        ),
    },
    {
        "kontext": (
            "Ein Fahrradhändler erfasst die jährlichen E-Bike-Verkäufe "
            "($ t $: Jahre seit 2020, Verkäufe in Stück):"
        ),
        "modell": "linear",
        "var": "t",
        "fn": "V",
        "x_label": "Jahr $ t $",
        "y_label": "Verkäufe",
        "x_values": [0, 1, 2, 3, 4],
        "coeffs": [[400, 450, 500, 550, 600], [60, 70, 80, 90, 100]],
        "dev_scales": [5.0, 10.0],
        "prognose_x": [6, 7, 8],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell die Verkaufszahl im Jahr $ t = {x} $."
        ),
        "umkehr_x": [6, 7, 8, 9],
        "umkehr_frage": (
            "In welchem Jahr $ t $ werden nach dem Modell erstmals {y} E-Bikes verkauft?"
        ),
    },
    {
        "kontext": (
            "Ein Fitnessstudio dokumentiert seine Mitgliederzahlen "
            "($ t $: Monate seit der Neueröffnung):"
        ),
        "modell": "linear",
        "var": "t",
        "fn": "M",
        "x_label": "Monat $ t $",
        "y_label": "Mitglieder",
        "x_values": [0, 1, 2, 3, 4, 5],
        "coeffs": [[240, 260, 280, 300], [15, 20, 25, 30]],
        "dev_scales": [2.0, 4.0],
        "prognose_x": [8, 9, 10],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell die Mitgliederzahl im Monat {x}."
        ),
        "umkehr_x": [8, 10, 12],
        "umkehr_frage": (
            "In welchem Monat erreicht das Studio nach dem Modell erstmals {y} Mitglieder?"
        ),
    },
    {
        "kontext": (
            "Eine Gemeinde senkt durch Sparmaßnahmen ihren Wasserverbrauch "
            "($ t $: Jahre seit Beginn der Maßnahmen, Verbrauch in Tausend Kubikmetern):"
        ),
        "modell": "linear",
        "var": "t",
        "fn": "W",
        "x_label": "Jahr $ t $",
        "y_label": "Verbrauch (Tsd. m³)",
        "x_values": [0, 1, 2, 3, 4, 5],
        "coeffs": [[100, 110, 120, 130], [-5, -4, -3, -2]],
        "dev_scales": [0.5, 1.0],
        "prognose_x": [8, 10],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell den Verbrauch (in Tausend Kubikmetern) "
            "im Jahr $ t = {x} $."
        ),
        "umkehr_x": [8, 10, 12],
        "umkehr_frage": (
            "In welchem Jahr $ t $ sinkt der Verbrauch nach dem Modell erstmals "
            "auf {y} Tausend Kubikmeter?"
        ),
    },
    {
        "kontext": (
            "Ein Rechenzentrum misst den Jahresstromverbrauch in Abhängigkeit "
            "von der Anzahl der betriebenen Serverschränke "
            "($ x $: Anzahl Serverschränke, Verbrauch in MWh):"
        ),
        "modell": "linear",
        "var": "x",
        "fn": "E",
        "x_label": "Schränke $ x $",
        "y_label": "Verbrauch (MWh)",
        "x_values": [1, 2, 3, 4, 5],
        "coeffs": [[20, 30, 40], [30, 40, 50]],
        "dev_scales": [1.0, 2.0],
        "prognose_x": [8, 10],
        "prognose_frage": (
            "Berechnen Sie mit dem Modell den erwarteten Verbrauch (in MWh) "
            "bei {x} Serverschränken."
        ),
        "umkehr_x": [7, 9, 11],
        "umkehr_frage": (
            "Bei wie vielen Serverschränken beträgt der Verbrauch nach dem Modell {y} MWh?"
        ),
    },
    {
        "kontext": (
            "In einem Schulgarten wird die Wuchshöhe einer Sonnenblume in der "
            "Hauptwachstumsphase wöchentlich gemessen ($ t $: Woche, Höhe in cm):"
        ),
        "modell": "linear",
        "var": "t",
        "fn": "h",
        "x_label": "Woche $ t $",
        "y_label": "Höhe (cm)",
        "x_values": [1, 2, 3, 4, 5, 6],
        "coeffs": [[15, 20, 25, 30], [12, 14, 15, 16, 18]],
        "dev_scales": [1.0, 2.0],
        "prognose_x": [8, 9],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell die Höhe (in cm) in Woche {x}."
        ),
        "umkehr_x": [8, 9, 10],
        "umkehr_frage": (
            "In welcher Woche erreicht die Sonnenblume nach dem Modell erstmals "
            "eine Höhe von {y} cm?"
        ),
    },
    {
        "kontext": (
            "Ein Podcast gewinnt seit dem Start kontinuierlich Abonnenten "
            "($ t $: Monate seit Start, Abonnenten in Hundert):"
        ),
        "modell": "linear",
        "var": "t",
        "fn": "A",
        "x_label": "Monat $ t $",
        "y_label": "Abonnenten (Hd.)",
        "x_values": [0, 1, 2, 3, 4, 5],
        "coeffs": [[30, 40, 50, 60], [6, 8, 10, 12]],
        "dev_scales": [0.5, 1.0],
        "prognose_x": [8, 10],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell die Abonnentenzahl (in Hundert) "
            "im Monat {x}."
        ),
        "umkehr_x": [7, 9, 11],
        "umkehr_frage": (
            "In welchem Monat erreicht der Podcast nach dem Modell erstmals "
            "{y} Hundert Abonnenten?"
        ),
    },
    {
        "kontext": (
            "Ein Energieversorger untersucht, wie viel CO₂ durch Solaranlagen "
            "eingespart wird ($ x $: installierte Anlagen in Hundert, "
            "jährliche Einsparung in Tonnen):"
        ),
        "modell": "linear",
        "var": "x",
        "fn": "S",
        "x_label": "Anlagen (Hd.) $ x $",
        "y_label": "Einsparung (t)",
        "x_values": [1, 2, 3, 4, 5],
        "coeffs": [[5, 10, 15], [25, 30, 35, 40, 45]],
        "dev_scales": [2.0, 3.0],
        "prognose_x": [7, 8],
        "prognose_frage": (
            "Berechnen Sie mit dem Modell die jährliche Einsparung (in Tonnen) "
            "bei {x} Hundert Anlagen."
        ),
        "umkehr_x": [6, 8, 10],
        "umkehr_frage": (
            "Bei wie vielen Hundert Anlagen beträgt die jährliche Einsparung "
            "nach dem Modell {y} Tonnen?"
        ),
    },
    # ------------------------------------------------------------------
    # Quadratisch (7)
    # ------------------------------------------------------------------
    {
        "kontext": (
            "Bei Bremstests wird der Anhalteweg eines Pkw bei verschiedenen "
            "Geschwindigkeiten gemessen ($ v $: Geschwindigkeit in km/h, "
            "Anhalteweg in m):"
        ),
        "modell": "quadratisch",
        "var": "v",
        "fn": "s",
        "x_label": "Tempo $ v $ (km/h)",
        "y_label": "Anhalteweg (m)",
        "x_values": [20, 40, 60, 80, 100],
        "coeffs": [[0, 1, 2], [0.2, 0.25, 0.3], [0.01]],
        "dev_scales": [0.5],
        "prognose_x": [110, 120],
        "prognose_frage": (
            "Berechnen Sie mit dem Modell den Anhalteweg (in m) bei {x} km/h."
        ),
        "umkehr_x": [50, 70, 90, 110],
        "umkehr_frage": (
            "Bei welcher Geschwindigkeit (in km/h) beträgt der Anhalteweg "
            "nach dem Modell {y} m?"
        ),
    },
    {
        "kontext": (
            "Die kumulierten Downloads einer neuen App steigen immer schneller "
            "($ t $: Monate seit Veröffentlichung, Downloads in Tausend):"
        ),
        "modell": "quadratisch",
        "var": "t",
        "fn": "D",
        "x_label": "Monat $ t $",
        "y_label": "Downloads (Tsd.)",
        "x_values": [0, 1, 2, 3, 4, 5],
        "coeffs": [[5, 10, 15, 20], [2, 3, 4, 5], [1, 1.5, 2]],
        "dev_scales": [0.5, 1.0],
        "prognose_x": [7, 8],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell die Downloadzahl (in Tausend) "
            "im Monat {x}."
        ),
        "umkehr_x": [7, 8, 9],
        "umkehr_frage": (
            "In welchem Monat erreicht die App nach dem Modell erstmals "
            "{y} Tausend Downloads?"
        ),
    },
    {
        "kontext": (
            "In einem Physikpraktikum wird die Fallstrecke einer Stahlkugel "
            "gemessen ($ t $: Zeit in Sekunden, Fallstrecke in m):"
        ),
        "modell": "quadratisch",
        "var": "t",
        "fn": "s",
        "x_label": "Zeit $ t $ (s)",
        "y_label": "Strecke (m)",
        "x_values": [0, 0.5, 1, 1.5, 2, 2.5],
        "coeffs": [[0], [0, 1, 2], [5]],
        "dev_scales": [0.25, 0.5],
        "prognose_x": [3, 3.5],
        "prognose_frage": (
            "Berechnen Sie mit dem Modell die Fallstrecke (in m) nach {x} Sekunden."
        ),
        "umkehr_x": [1.8, 2.2, 2.8],
        "umkehr_frage": (
            "Nach welcher Zeit (in Sekunden) hat die Kugel nach dem Modell "
            "eine Strecke von {y} m zurückgelegt?"
        ),
    },
    {
        "kontext": (
            "Die kumulierte installierte Leistung eines wachsenden Solarparks "
            "entwickelt sich beschleunigt ($ t $: Jahre seit Baubeginn, "
            "Leistung in MW):"
        ),
        "modell": "quadratisch",
        "var": "t",
        "fn": "P",
        "x_label": "Jahr $ t $",
        "y_label": "Leistung (MW)",
        "x_values": [0, 1, 2, 3, 4, 5],
        "coeffs": [[2, 4, 6], [1, 2, 3], [0.5, 1, 1.5]],
        "dev_scales": [0.25, 0.5],
        "prognose_x": [7, 8],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell die installierte Leistung "
            "(in MW) im Jahr $ t = {x} $."
        ),
        "umkehr_x": [7, 8, 9],
        "umkehr_frage": (
            "In welchem Jahr $ t $ erreicht der Solarpark nach dem Modell "
            "erstmals eine Leistung von {y} MW?"
        ),
    },
    {
        "kontext": (
            "Bei einer Datenleitung nimmt die Zahl der Übertragungsfehler mit "
            "der Kabellänge überproportional zu ($ x $: Länge in 100 m, "
            "Fehler pro Stunde):"
        ),
        "modell": "quadratisch",
        "var": "x",
        "fn": "F",
        "x_label": "Länge $ x $ (100 m)",
        "y_label": "Fehler/h",
        "x_values": [1, 2, 3, 4, 5],
        "coeffs": [[1, 2, 3], [0, 1, 2], [0.5, 1]],
        "dev_scales": [0.5],
        "prognose_x": [7, 8],
        "prognose_frage": (
            "Berechnen Sie mit dem Modell die erwartete Fehlerzahl pro Stunde "
            "bei einer Länge von {x} mal 100 m."
        ),
        "umkehr_x": [6, 7, 8],
        "umkehr_frage": (
            "Bei welcher Länge (in 100 m) treten nach dem Modell {y} Fehler "
            "pro Stunde auf?"
        ),
    },
    {
        "kontext": (
            "Ein Hersteller kalkuliert die Kosten quadratischer Werbetafeln: "
            "Materialkosten wachsen mit der Fläche, Rahmenkosten mit dem Umfang "
            "($ x $: Kantenlänge in m, Kosten in €):"
        ),
        "modell": "quadratisch",
        "var": "x",
        "fn": "K",
        "x_label": "Kante $ x $ (m)",
        "y_label": "Kosten (€)",
        "x_values": [1, 2, 3, 4, 5],
        "coeffs": [[20, 30, 40, 50], [10, 15, 20, 25], [40, 50, 60, 70, 80]],
        "dev_scales": [5.0, 10.0],
        "prognose_x": [6, 7],
        "prognose_frage": (
            "Berechnen Sie mit dem Modell die Kosten (in €) einer Tafel mit "
            "Kantenlänge {x} m."
        ),
        "umkehr_x": [6, 7, 8],
        "umkehr_frage": (
            "Welche Kantenlänge (in m) hat nach dem Modell eine Tafel, "
            "die {y} € kostet?"
        ),
    },
    {
        "kontext": (
            "Ein neues Stadtviertel wächst zunehmend schneller "
            "($ t $: Jahre seit Erschließung, Einwohner in Hundert):"
        ),
        "modell": "quadratisch",
        "var": "t",
        "fn": "E",
        "x_label": "Jahr $ t $",
        "y_label": "Einwohner (Hd.)",
        "x_values": [0, 1, 2, 3, 4, 5],
        "coeffs": [[50, 60, 70, 80], [2, 3, 4], [0.5, 1]],
        "dev_scales": [0.5, 1.0],
        "prognose_x": [8, 10],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell die Einwohnerzahl (in Hundert) "
            "im Jahr $ t = {x} $."
        ),
        "umkehr_x": [8, 9, 10],
        "umkehr_frage": (
            "In welchem Jahr $ t $ erreicht das Viertel nach dem Modell "
            "erstmals {y} Hundert Einwohner?"
        ),
    },
    # ------------------------------------------------------------------
    # Kubisch (5)
    # ------------------------------------------------------------------
    {
        "kontext": (
            "Die abgegebene Leistung einer kleinen Windkraftanlage hängt stark "
            "von der Windgeschwindigkeit ab ($ v $: Windgeschwindigkeit in m/s, "
            "Leistung in kW):"
        ),
        "modell": "kubisch",
        "var": "v",
        "fn": "P",
        "x_label": "Wind $ v $ (m/s)",
        "y_label": "Leistung (kW)",
        "x_values": [2, 3, 4, 5, 6, 7],
        "coeffs": [[0, 2, 5], [0, 1], [0, 1], [0.5, 1]],
        "dev_scales": [0.25, 0.5],
        "prognose_x": [8, 9],
        "prognose_frage": (
            "Berechnen Sie mit dem Modell die Leistung (in kW) bei einer "
            "Windgeschwindigkeit von {x} m/s."
        ),
        "prognose2_x": [10, 11],
        "prognose2_frage": (
            "Berechnen Sie zum Vergleich die Leistung (in kW) bei {x} m/s."
        ),
    },
    {
        "kontext": (
            "Für die Produktion eines Guts wird ein ertragsgesetzlicher "
            "Kostenverlauf vermutet ($ x $: Menge in ME, Kosten in GE):"
        ),
        "modell": "kubisch",
        "var": "x",
        "fn": "K",
        "x_label": "Menge $ x $ (ME)",
        "y_label": "Kosten (GE)",
        "x_values": [1, 2, 3, 4, 5, 6],
        "coeffs": [[20, 30, 40, 50], [15, 20, 25], [-5, -4], [1]],
        "dev_scales": [0.5, 1.0],
        "monoton": True,
        "prognose_x": [8],
        "prognose_frage": (
            "Berechnen Sie mit dem Modell die Kosten (in GE) bei einer "
            "Produktionsmenge von {x} ME."
        ),
        "prognose2_x": [10],
        "prognose2_frage": (
            "Berechnen Sie zum Vergleich die Kosten (in GE) bei {x} ME."
        ),
    },
    {
        "kontext": (
            "Bei Karpfen wächst das Gewicht näherungsweise mit der dritten "
            "Potenz der Körperlänge ($ L $: Länge in dm, Gewicht in kg):"
        ),
        "modell": "kubisch",
        "var": "L",
        "fn": "G",
        "x_label": "Länge $ L $ (dm)",
        "y_label": "Gewicht (kg)",
        "x_values": [2, 3, 4, 5, 6, 7],
        "coeffs": [[0], [0], [0], [0.01, 0.02]],
        "dev_scales": [0.05],
        "prognose_x": [8],
        "prognose_frage": (
            "Berechnen Sie mit dem Modell das Gewicht (in kg) eines Karpfens "
            "mit einer Länge von {x} dm."
        ),
        "prognose2_x": [9, 10],
        "prognose2_frage": (
            "Berechnen Sie zum Vergleich das Gewicht (in kg) bei einer "
            "Länge von {x} dm."
        ),
    },
    {
        "kontext": (
            "Der Absatz eines Produkts folgt einem typischen Lebenszyklus: "
            "erst wachsend, später abflachend ($ t $: Quartale seit "
            "Markteinführung, Absatz in Hundert Stück):"
        ),
        "modell": "kubisch",
        "var": "t",
        "fn": "A",
        "x_label": "Quartal $ t $",
        "y_label": "Absatz (Hd.)",
        "x_values": [0, 1, 2, 3, 4, 5],
        "coeffs": [[10, 15, 20], [5, 6], [4], [-1]],
        "dev_scales": [0.5, 1.0],
        "prognose_x": [4],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell den Absatz (in Hundert Stück) "
            "im Quartal $ t = {x} $."
        ),
        "prognose2_x": [5],
        "prognose2_frage": (
            "Prognostizieren Sie zum Vergleich den Absatz (in Hundert Stück) "
            "im Quartal $ t = {x} $."
        ),
    },
    {
        "kontext": (
            "Der Umsatz eines Start-ups wächst anfangs langsam und zieht "
            "dann deutlich an ($ t $: Jahre seit Gründung, Umsatz in 100 Tsd. €):"
        ),
        "modell": "kubisch",
        "var": "t",
        "fn": "U",
        "x_label": "Jahr $ t $",
        "y_label": "Umsatz (100 Tsd. €)",
        "x_values": [0, 1, 2, 3, 4, 5],
        "coeffs": [[2, 4, 6], [1, 2, 3], [0, 1, 2], [0.5, 1]],
        "dev_scales": [0.25, 0.5],
        "monoton": True,
        "prognose_x": [6, 7],
        "prognose_frage": (
            "Prognostizieren Sie mit dem Modell den Umsatz (in 100 Tsd. €) "
            "im Jahr $ t = {x} $."
        ),
        "prognose2_x": [8],
        "prognose2_frage": (
            "Prognostizieren Sie zum Vergleich den Umsatz (in 100 Tsd. €) "
            "im Jahr $ t = {x} $."
        ),
    },
]


def _is_two_decimals(value: float) -> bool:
    return abs(round(value * 100) - value * 100) < 1e-6


def _other_quadratic_root(coeffs: list[float], y_star: float, x_star: float) -> float:
    """Zweite Lösung von f(x)=y* über das Wurzelprodukt (c-y*)/a."""
    a0, _, a2 = coeffs
    return (a0 - y_star) / (a2 * x_star)


class RegressionAnwendungGenerator(TaskGenerator):
    generator_key = "analysis.regression.anwendung"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for index in range(count):
            szenario = _SZENARIEN[index % len(_SZENARIEN)]
            tasks.append(self._build_task(rng, szenario))

        return tasks

    def _build_task(self, rng: random.Random, sz: dict) -> Task:
        degree = _DEGREE[sz["modell"]]

        while True:
            n_points = rng.choice(_N_CHOICES[degree])
            x_values = [float(x) for x in sz["x_values"][:n_points]]
            coeffs = [float(rng.choice(choices)) for choices in sz["coeffs"]]
            deviations = fd_deviations(rng, len(x_values), degree, sz["dev_scales"])
            y_values = [
                round(poly_eval(coeffs, x) + e, 2)
                for x, e in zip(x_values, deviations)
            ]
            if any(y < 0 for y in y_values):
                continue
            if not model_plausible(x_values, y_values, coeffs):
                continue

            prognose_x = float(rng.choice(sz["prognose_x"]))
            prognose_y = poly_eval(coeffs, prognose_x)
            if prognose_y < 0:
                continue

            if degree == 3:
                zweite_x = float(rng.choice(sz["prognose2_x"]))
                zweite_y = poly_eval(coeffs, zweite_x)
                if zweite_y < 0:
                    continue
                umkehr = None
            else:
                x_star = float(rng.choice(sz["umkehr_x"]))
                y_star = poly_eval(coeffs, x_star)
                if x_star == prognose_x:
                    continue
                if y_star < 0 or not _is_two_decimals(y_star):
                    continue
                if degree == 2:
                    # Zweite Lösung muss außerhalb des Sachkontexts liegen.
                    other = _other_quadratic_root(coeffs, y_star, x_star)
                    if other > min(x_values) - 0.5:
                        continue
                umkehr = (x_star, y_star)
                zweite_x = zweite_y = None

            if sz.get("monoton"):
                check_points = sorted(x_values + [prognose_x] + (
                    [zweite_x] if zweite_x is not None else []
                ))
                values = [poly_eval(coeffs, x) for x in check_points]
                if any(b <= a for a, b in zip(values, values[1:])):
                    continue

            assert_fit_matches(x_values, y_values, coeffs)
            break

        table = make_table(
            x_values, y_values, x_label=sz["x_label"], y_label=sz["y_label"]
        )
        ansatz = _ANSATZ_TEMPLATE[sz["modell"]].format(fn=sz["fn"], var=sz["var"])
        einleitung = (
            f"{sz['kontext']}{table}"
            f"Die Daten sollen durch eine {sz['modell']}e Regressionsfunktion "
            f"mit dem Ansatz $ {ansatz} $ modelliert werden."
        )

        fragen = [
            f"Bestimmen Sie die {sz['modell']}e Regressionsfunktion.",
            sz["prognose_frage"].format(x=fmt_number(prognose_x)),
        ]
        antworten = [
            poly_function_answer(coeffs, var=sz["var"], func_name=sz["fn"]),
            numerical_analysis_calc(prognose_y),
        ]

        if umkehr is not None:
            x_star, y_star = umkehr
            fragen.append(sz["umkehr_frage"].format(y=fmt_number(y_star)))
            antworten.append(numerical_analysis_calc(x_star))
        else:
            fragen.append(sz["prognose2_frage"].format(x=fmt_number(zweite_x)))
            antworten.append(numerical_analysis_calc(zweite_y))

        return Task(einleitung=einleitung, fragen=fragen, antworten=antworten)
