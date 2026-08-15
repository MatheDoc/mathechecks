"""Generator 12 – Optimierung (quadratisch).

Sachaufgabe: Die Zielfunktion wird aus drei kontextbezogenen
Beobachtungswerten aufgestellt. Scheitel (Optimum) und Nullstellen
werden bewusst nicht in der Einleitung verraten.
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
# extremum "max": a < 0, Scheitelwert e > 0, Nullstellen = z. B. Gewinnschwellen.
# extremum "min": a > 0, Scheitelwert e < 0, Nullstellen = z. B. Nulldurchgänge.
# Nullstellen liegen bei d − w und d + w (beide >= 0); d = w erlaubt Nullstelle bei 0.
# ---------------------------------------------------------------------------

_SZENARIEN: list[dict] = [
    {
        "extremum": "max",
        "intro": (
            "Ein Streetfood-Stand testet verschiedene Verkaufspreise für sein "
            "beliebtestes Gericht. Über mehrere Wochen wurde der Tagesgewinn "
            "bei drei Preisen ermittelt:"
        ),
        "punkte_satz": "Bei einem Preis von {x1} € ergibt sich ein Tagesgewinn von {y1} €, bei {x2} € sind es {y2} € und bei {x3} € noch {y3} €.",
        "fn": "G",
        "var": "p",
        "y_beschreibung": "den Tagesgewinn in Euro",
        "x_beschreibung": "dem Verkaufspreis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Verkaufspreis, bei dem der Tagesgewinn am größten ist.",
        "frage_ys": "Bestimmen Sie den maximalen Tagesgewinn.",
        "frage_ns": "Bestimmen Sie die beiden Preise, bei denen der Tagesgewinn genau 0 € beträgt.",
        "frage_eval": "Bestimmen Sie den Tagesgewinn bei einem Verkaufspreis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Verkaufspreis, bei dem der Tagesgewinn ebenfalls {y_text} € beträgt.",
        "a_choices": [-20, -30],
        "w_choices": [3, 4],
        "d_choices": [6, 7, 8, 9],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein Kino kalkuliert den Ticketpreis für den Samstagabend neu. "
            "Aus früheren Preisaktionen ist der Tagesgewinn bei drei "
            "verschiedenen Preisen bekannt:"
        ),
        "punkte_satz": "Bei einem Ticketpreis von {x1} € beträgt der Tagesgewinn {y1} €, bei {x2} € sind es {y2} € und bei {x3} € ergeben sich {y3} €.",
        "fn": "G",
        "var": "p",
        "y_beschreibung": "den Tagesgewinn in Euro",
        "x_beschreibung": "dem Ticketpreis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Ticketpreis, bei dem der Tagesgewinn maximal wird.",
        "frage_ys": "Bestimmen Sie den maximalen Tagesgewinn.",
        "frage_ns": "Bestimmen Sie die beiden Ticketpreise, bei denen der Tagesgewinn genau 0 € beträgt.",
        "frage_eval": "Bestimmen Sie den Tagesgewinn bei einem Ticketpreis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Ticketpreis, bei dem der Tagesgewinn ebenfalls {y_text} € beträgt.",
        "a_choices": [-30, -40],
        "w_choices": [3, 4],
        "d_choices": [7, 8, 9, 10],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein Freibad untersucht, wie die tägliche Besucherzahl vom "
            "Eintrittspreis abhängt. Drei Beobachtungen aus den letzten "
            "Sommern liegen vor:"
        ),
        "punkte_satz": "Bei einem Eintrittspreis von {x1} € kommen {y1} Gäste, bei {x2} € sind es {y2} Gäste und bei {x3} € nur noch {y3} Gäste.",
        "fn": "B",
        "var": "p",
        "y_beschreibung": "die tägliche Besucherzahl",
        "x_beschreibung": "dem Eintrittspreis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Eintrittspreis, bei dem die Besucherzahl am größten ist.",
        "frage_ys": "Bestimmen Sie die maximale Besucherzahl.",
        "frage_ns": "Bestimmen Sie die beiden Eintrittspreise, bei denen die Besucherzahl auf 0 sinken würde.",
        "frage_eval": "Bestimmen Sie die erwartete Besucherzahl bei einem Eintrittspreis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Eintrittspreis, bei dem ebenfalls {y_text} Gäste erwartet werden.",
        "eval_step": 1,
        "a_choices": [-20, -25],
        "w_choices": [3, 4, 5],
        "d_choices": [5, 6, 7, 8],
    },
    {
        "extremum": "max",
        "intro": (
            "Eine Konzertveranstalterin plant die Ticketpreise für eine "
            "Hallentour. Die Kalkulation ergibt für drei Preise folgende "
            "Gewinne pro Abend:"
        ),
        "punkte_satz": "Bei einem Ticketpreis von {x1} € liegt der Gewinn bei {y1} €, bei {x2} € bei {y2} € und bei {x3} € bei {y3} €.",
        "fn": "G",
        "var": "p",
        "y_beschreibung": "den Gewinn pro Abend in Euro",
        "x_beschreibung": "dem Ticketpreis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Ticketpreis, bei dem der Gewinn pro Abend maximal wird.",
        "frage_ys": "Bestimmen Sie den maximalen Gewinn pro Abend.",
        "frage_ns": "Bestimmen Sie die beiden Ticketpreise, bei denen der Gewinn genau 0 € beträgt.",
        "frage_eval": "Bestimmen Sie den Gewinn pro Abend bei einem Ticketpreis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Ticketpreis, bei dem der Gewinn pro Abend ebenfalls {y_text} € beträgt.",
        "a_choices": [-10, -20],
        "w_choices": [4, 5],
        "d_choices": [8, 9, 10, 11, 12],
    },
    {
        "extremum": "max",
        "intro": (
            "Eine Bäckerei überlegt, welchen Preis sie für ihr Sauerteigbrot "
            "verlangen soll. Testwochen mit drei verschiedenen Preisen ergaben "
            "folgende Tagesgewinne:"
        ),
        "punkte_satz": "Bei einem Brotpreis von {x1} € beträgt der Tagesgewinn {y1} €, bei {x2} € sind es {y2} € und bei {x3} € ergeben sich {y3} €.",
        "fn": "G",
        "var": "p",
        "y_beschreibung": "den Tagesgewinn in Euro",
        "x_beschreibung": "dem Brotpreis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Brotpreis, bei dem der Tagesgewinn am größten ist.",
        "frage_ys": "Bestimmen Sie den maximalen Tagesgewinn.",
        "frage_ns": "Bestimmen Sie die beiden Brotpreise, bei denen der Tagesgewinn genau 0 € beträgt.",
        "frage_eval": "Bestimmen Sie den Tagesgewinn bei einem Brotpreis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Brotpreis, bei dem der Tagesgewinn ebenfalls {y_text} € beträgt.",
        "a_choices": [-15, -25],
        "w_choices": [3],
        "d_choices": [4, 5],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein Obsthof untersucht, wie viele Apfelbäume pro Reihe den "
            "größten Ernteertrag liefern: Stehen die Bäume zu dicht, nehmen "
            "sie sich gegenseitig Licht und Wasser. Drei Versuchsreihen ergaben:"
        ),
        "punkte_satz": "Mit {x1} Bäumen pro Reihe liegt der Ertrag bei {y1} Kisten, mit {x2} Bäumen bei {y2} Kisten und mit {x3} Bäumen bei {y3} Kisten.",
        "fn": "E",
        "var": "x",
        "y_beschreibung": "den Ernteertrag in Kisten",
        "x_beschreibung": "der Anzahl $x$ der Bäume pro Reihe",
        "frage_xs": "Bestimmen Sie die Baumanzahl pro Reihe, bei der der Ertrag maximal wird.",
        "frage_ys": "Bestimmen Sie den maximalen Ertrag.",
        "frage_ns": "Bestimmen Sie die beiden Baumanzahlen, bei denen der Ertrag rechnerisch auf 0 Kisten fällt.",
        "frage_eval": "Bestimmen Sie den rechnerischen Ertrag bei {x_text} Bäumen pro Reihe.",
        "frage_inverse": "Bestimmen Sie die weitere Baumanzahl pro Reihe, bei der der Ertrag ebenfalls {y_text} Kisten beträgt.",
        "eval_step": 1,
        "a_choices": [-5, -10],
        "w_choices": [3, 4],
        "d_choices": [6, 7, 8, 9],
    },
    {
        "extremum": "max",
        "intro": (
            "Eine Hausverwaltung analysiert, wie die monatlichen Mieteinnahmen "
            "eines Wohnblocks vom Mietpreis pro Quadratmeter abhängen: Bei zu "
            "hohen Mieten stehen Wohnungen leer. Drei Auswertungen liegen vor:"
        ),
        "punkte_satz": "Bei {x1} € pro Quadratmeter betragen die Einnahmen {y1} €, bei {x2} € sind es {y2} € und bei {x3} € noch {y3} €.",
        "fn": "M",
        "var": "p",
        "y_beschreibung": "die monatlichen Mieteinnahmen in Euro",
        "x_beschreibung": "dem Mietpreis $p$ in Euro pro Quadratmeter",
        "frage_xs": "Bestimmen Sie den Mietpreis, bei dem die Einnahmen maximal werden.",
        "frage_ys": "Bestimmen Sie die maximalen monatlichen Einnahmen.",
        "frage_ns": "Bestimmen Sie die beiden Mietpreise, bei denen die Einnahmen rechnerisch 0 € betragen.",
        "frage_eval": "Bestimmen Sie die monatlichen Einnahmen bei einem Mietpreis von {x_text} € pro Quadratmeter.",
        "frage_inverse": "Bestimmen Sie den weiteren Mietpreis pro Quadratmeter, bei dem die monatlichen Einnahmen ebenfalls {y_text} € betragen.",
        "a_choices": [-50],
        "w_choices": [3, 4],
        "d_choices": [8, 9, 10, 11, 12],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein Gartenbesitzer möchte mit einer festen Zaunlänge eine "
            "rechteckige Gemüsefläche an einer Mauer abstecken. Für drei "
            "verschiedene Seitenlängen wurde die eingezäunte Fläche berechnet:"
        ),
        "punkte_satz": "Bei einer Seitenlänge von {x1} m ergibt sich eine Fläche von {y1} m², bei {x2} m sind es {y2} m² und bei {x3} m ergeben sich {y3} m².",
        "fn": "A",
        "var": "x",
        "y_beschreibung": "die eingezäunte Fläche in Quadratmetern",
        "x_beschreibung": "der Seitenlänge $x$ in Metern",
        "frage_xs": "Bestimmen Sie die Seitenlänge, bei der die Fläche maximal wird.",
        "frage_ys": "Bestimmen Sie die maximale Fläche.",
        "frage_ns": "Bestimmen Sie die beiden Seitenlängen, bei denen die Fläche 0 m² beträgt.",
        "frage_eval": "Bestimmen Sie die eingezäunte Fläche bei einer Seitenlänge von {x_text} m.",
        "frage_inverse": "Bestimmen Sie die weitere Seitenlänge, bei der die eingezäunte Fläche ebenfalls {y_text} m² beträgt.",
        "a_choices": [-1],
        "w_choices": [5, 6, 7, 8, 9],
        "d_choices": [],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein Foodtruck verkauft mittags ein Wochengericht. Der Betreiber "
            "hat notiert, wie viele Portionen bei verschiedenen Preisen "
            "verkauft wurden, und daraus den Tagesgewinn berechnet:"
        ),
        "punkte_satz": "Bei einem Preis von {x1} € beträgt der Tagesgewinn {y1} €, bei {x2} € sind es {y2} € und bei {x3} € ergeben sich {y3} €.",
        "fn": "G",
        "var": "p",
        "y_beschreibung": "den Tagesgewinn in Euro",
        "x_beschreibung": "dem Portionspreis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Portionspreis, bei dem der Tagesgewinn am größten ist.",
        "frage_ys": "Bestimmen Sie den maximalen Tagesgewinn.",
        "frage_ns": "Bestimmen Sie die beiden Portionspreise, bei denen der Tagesgewinn genau 0 € beträgt.",
        "frage_eval": "Bestimmen Sie den Tagesgewinn bei einem Portionspreis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Portionspreis, bei dem der Tagesgewinn ebenfalls {y_text} € beträgt.",
        "a_choices": [-15, -20],
        "w_choices": [3, 4],
        "d_choices": [6, 7, 8, 9],
    },
    {
        "extremum": "max",
        "intro": (
            "Eine Theatergruppe plant die Ticketpreise für ihre neue "
            "Produktion. Aus den letzten Spielzeiten sind die Einnahmen "
            "pro Vorstellung bei drei Preisen bekannt:"
        ),
        "punkte_satz": "Bei einem Ticketpreis von {x1} € lagen die Einnahmen bei {y1} €, bei {x2} € bei {y2} € und bei {x3} € bei {y3} €.",
        "fn": "E",
        "var": "p",
        "y_beschreibung": "die Einnahmen pro Vorstellung in Euro",
        "x_beschreibung": "dem Ticketpreis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Ticketpreis, bei dem die Einnahmen maximal werden.",
        "frage_ys": "Bestimmen Sie die maximalen Einnahmen pro Vorstellung.",
        "frage_ns": "Bestimmen Sie die beiden Ticketpreise, bei denen die Einnahmen rechnerisch 0 € betragen.",
        "frage_eval": "Bestimmen Sie die Einnahmen pro Vorstellung bei einem Ticketpreis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Ticketpreis, bei dem die Einnahmen pro Vorstellung ebenfalls {y_text} € betragen.",
        "a_choices": [-25],
        "w_choices": [3, 4],
        "d_choices": [6, 7, 8, 9],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein Hofladen verkauft im Juni Erdbeerkörbe. Die Betreiberin hat "
            "in drei Wochen unterschiedliche Preise getestet und jeweils den "
            "Wochengewinn bestimmt:"
        ),
        "punkte_satz": "Bei einem Korbpreis von {x1} € ergab sich ein Wochengewinn von {y1} €, bei {x2} € waren es {y2} € und bei {x3} € noch {y3} €.",
        "fn": "G",
        "var": "p",
        "y_beschreibung": "den Wochengewinn in Euro",
        "x_beschreibung": "dem Korbpreis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Korbpreis, bei dem der Wochengewinn maximal wird.",
        "frage_ys": "Bestimmen Sie den maximalen Wochengewinn.",
        "frage_ns": "Bestimmen Sie die beiden Korbpreise, bei denen der Wochengewinn genau 0 € beträgt.",
        "frage_eval": "Bestimmen Sie den Wochengewinn bei einem Korbpreis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Korbpreis, bei dem der Wochengewinn ebenfalls {y_text} € beträgt.",
        "a_choices": [-20, -30],
        "w_choices": [3],
        "d_choices": [5, 6, 7],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein Fitnessstudio untersucht, wie die Zahl der Neuanmeldungen "
            "pro Monat vom Monatsbeitrag abhängt. Drei Auswertungen aus "
            "Aktionsmonaten liegen vor:"
        ),
        "punkte_satz": "Bei einem Monatsbeitrag von {x1} € gab es {y1} Neuanmeldungen, bei {x2} € waren es {y2} und bei {x3} € nur {y3}.",
        "fn": "N",
        "var": "p",
        "y_beschreibung": "die Zahl der Neuanmeldungen pro Monat",
        "x_beschreibung": "dem Monatsbeitrag $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Monatsbeitrag, bei dem die Zahl der Neuanmeldungen maximal wird.",
        "frage_ys": "Bestimmen Sie die maximale Zahl der Neuanmeldungen.",
        "frage_ns": "Bestimmen Sie die beiden Monatsbeiträge, bei denen die Zahl der Neuanmeldungen rechnerisch auf 0 fällt.",
        "frage_eval": "Bestimmen Sie die erwartete Zahl der Neuanmeldungen bei einem Monatsbeitrag von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Monatsbeitrag, bei dem ebenfalls {y_text} Neuanmeldungen erwartet werden.",
        "eval_step": 1,
        "a_choices": [-10],
        "w_choices": [3, 4],
        "d_choices": [6, 7, 8],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein Kleingärtner testet, wie viel Dünger sein Gemüsebeet "
            "vertragen kann: Zu wenig bringt kaum Wirkung, zu viel schadet "
            "den Pflanzen. Drei Versuche ergaben folgende Erträge:"
        ),
        "punkte_satz": "Mit {x1} kg Dünger liegt der Ertrag bei {y1} kg Gemüse, mit {x2} kg bei {y2} kg und mit {x3} kg bei {y3} kg.",
        "fn": "E",
        "var": "x",
        "y_beschreibung": "den Ernteertrag in Kilogramm",
        "x_beschreibung": "der Düngermenge $x$ in Kilogramm",
        "frage_xs": "Bestimmen Sie die Düngermenge, bei der der Ertrag maximal wird.",
        "frage_ys": "Bestimmen Sie den maximalen Ertrag.",
        "frage_ns": "Bestimmen Sie die beiden Düngermengen, bei denen der Ertrag rechnerisch auf 0 kg fällt.",
        "frage_eval": "Bestimmen Sie den rechnerischen Ertrag bei einer Düngermenge von {x_text} kg.",
        "frage_inverse": "Bestimmen Sie die weitere Düngermenge, bei der der Ertrag ebenfalls {y_text} kg beträgt.",
        "a_choices": [-2],
        "w_choices": [4, 5],
        "d_choices": [6, 7, 8, 9],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein Webshop testet Rabattaktionen: Kleine Rabatte locken kaum "
            "Kundschaft, sehr große Rabatte drücken den Erlös. Für drei "
            "Rabattsätze wurde der zusätzliche Tagesumsatz gemessen:"
        ),
        "punkte_satz": "Bei {x1} % Rabatt beträgt der zusätzliche Umsatz {y1} €, bei {x2} % sind es {y2} € und bei {x3} % noch {y3} €.",
        "fn": "U",
        "var": "r",
        "y_beschreibung": "den zusätzlichen Tagesumsatz in Euro",
        "x_beschreibung": "dem Rabattsatz $r$ in Prozent",
        "frage_xs": "Bestimmen Sie den Rabattsatz, bei dem der zusätzliche Umsatz maximal wird.",
        "frage_ys": "Bestimmen Sie den maximalen zusätzlichen Umsatz.",
        "frage_ns": "Bestimmen Sie die beiden Rabattsätze, bei denen der zusätzliche Umsatz 0 € beträgt.",
        "frage_eval": "Bestimmen Sie den zusätzlichen Tagesumsatz bei einem Rabattsatz von {x_text} %.",
        "frage_inverse": "Bestimmen Sie den weiteren Rabattsatz, bei dem der zusätzliche Tagesumsatz ebenfalls {y_text} € beträgt.",
        "a_choices": [-50],
        "w_choices": [3, 4],
        "d_choices": [5, 6, 7, 8],
    },
    {
        "extremum": "max",
        "intro": (
            "Auf einem Stadtfest verkauft ein Stand Crêpes. Der Betreiber hat "
            "an drei Tagen unterschiedliche Preise verlangt und jeweils den "
            "Tagesgewinn notiert:"
        ),
        "punkte_satz": "Bei einem Preis von {x1} € ergab sich ein Tagesgewinn von {y1} €, bei {x2} € waren es {y2} € und bei {x3} € noch {y3} €.",
        "fn": "G",
        "var": "p",
        "y_beschreibung": "den Tagesgewinn in Euro",
        "x_beschreibung": "dem Crêpes-Preis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Preis, bei dem der Tagesgewinn maximal wird.",
        "frage_ys": "Bestimmen Sie den maximalen Tagesgewinn.",
        "frage_ns": "Bestimmen Sie die beiden Preise, bei denen der Tagesgewinn genau 0 € beträgt.",
        "frage_eval": "Bestimmen Sie den Tagesgewinn bei einem Crêpes-Preis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Crêpes-Preis, bei dem der Tagesgewinn ebenfalls {y_text} € beträgt.",
        "a_choices": [-20],
        "w_choices": [3],
        "d_choices": [5, 6, 7],
    },
    {
        "extremum": "max",
        "intro": (
            "Ein kleiner Verlag kalkuliert den Verkaufspreis eines neuen "
            "Romans. Die Marktanalyse liefert den erwarteten Monatsgewinn "
            "für drei Preise:"
        ),
        "punkte_satz": "Bei einem Verkaufspreis von {x1} € wird ein Monatsgewinn von {y1} € erwartet, bei {x2} € sind es {y2} € und bei {x3} € noch {y3} €.",
        "fn": "G",
        "var": "p",
        "y_beschreibung": "den erwarteten Monatsgewinn in Euro",
        "x_beschreibung": "dem Verkaufspreis $p$ in Euro",
        "frage_xs": "Bestimmen Sie den Verkaufspreis, bei dem der Monatsgewinn maximal wird.",
        "frage_ys": "Bestimmen Sie den maximalen Monatsgewinn.",
        "frage_ns": "Bestimmen Sie die beiden Verkaufspreise, bei denen der Monatsgewinn genau 0 € beträgt.",
        "frage_eval": "Bestimmen Sie den erwarteten Monatsgewinn bei einem Verkaufspreis von {x_text} €.",
        "frage_inverse": "Bestimmen Sie den weiteren Verkaufspreis, bei dem der Monatsgewinn ebenfalls {y_text} € beträgt.",
        "a_choices": [-10, -15],
        "w_choices": [4, 5],
        "d_choices": [10, 11, 12, 13, 14],
    },
    {
        "extremum": "min",
        "intro": (
            "In einer klaren Winternacht wird die Lufttemperatur an einer "
            "Wetterstation aufgezeichnet. Zwischen dem Abend und dem nächsten "
            "Vormittag lässt sich der Verlauf gut quadratisch beschreiben; "
            "$t$ ist die Zeit in Stunden seit 18 Uhr:"
        ),
        "punkte_satz": "Zum Zeitpunkt $t = {x1}$ werden {y1} °C gemessen, zum Zeitpunkt $t = {x2}$ sind es {y2} °C und zum Zeitpunkt $t = {x3}$ wieder {y3} °C.",
        "fn": "T",
        "var": "t",
        "y_beschreibung": "die Temperatur in Grad Celsius",
        "x_beschreibung": "der Zeit $t$ in Stunden seit 18 Uhr",
        "frage_xs": "Bestimmen Sie den Zeitpunkt, zu dem die Temperatur am niedrigsten ist.",
        "frage_ys": "Bestimmen Sie die tiefste Temperatur.",
        "frage_ns": "Bestimmen Sie die beiden Zeitpunkte, zu denen die Temperatur genau 0 °C beträgt.",
        "frage_eval": "Bestimmen Sie die Temperatur zum Zeitpunkt $t = {x_text}$.",
        "frage_inverse": "Bestimmen Sie den weiteren Zeitpunkt, zu dem die Temperatur ebenfalls {y_text} °C beträgt.",
        "a_choices": [0.5],
        "w_choices": [3, 4],
        "d_choices": [6, 7, 8, 9],
    },
    {
        "extremum": "min",
        "intro": (
            "An einem Messpfahl im Wattenmeer wird der Wasserstand relativ "
            "zum Normalwert erfasst. Rund um die Ebbe lässt sich der Verlauf "
            "quadratisch modellieren; $t$ ist die Zeit in Stunden seit Messbeginn:"
        ),
        "punkte_satz": "Zum Zeitpunkt $t = {x1}$ liegt der Wasserstand bei {y1} cm, zum Zeitpunkt $t = {x2}$ bei {y2} cm und zum Zeitpunkt $t = {x3}$ bei {y3} cm.",
        "fn": "P",
        "var": "t",
        "y_beschreibung": "den Wasserstand relativ zum Normalwert in Zentimetern",
        "x_beschreibung": "der Zeit $t$ in Stunden seit Messbeginn",
        "frage_xs": "Bestimmen Sie den Zeitpunkt des niedrigsten Wasserstands.",
        "frage_ys": "Bestimmen Sie den niedrigsten Wasserstand.",
        "frage_ns": "Bestimmen Sie die beiden Zeitpunkte, zu denen der Wasserstand genau dem Normalwert entspricht.",
        "frage_eval": "Bestimmen Sie den Wasserstand zum Zeitpunkt $t = {x_text}$.",
        "frage_inverse": "Bestimmen Sie den weiteren Zeitpunkt, zu dem der Wasserstand ebenfalls {y_text} cm beträgt.",
        "a_choices": [5, 10],
        "w_choices": [3, 4],
        "d_choices": [5, 6, 7],
    },
    {
        "extremum": "min",
        "intro": (
            "Ein Sportverein wertet seinen Kontostand im Jahresverlauf aus: "
            "Zu Jahresbeginn und am Jahresende ist das Konto gut gefüllt, in "
            "der Saisonmitte wird es durch große Ausgaben knapp. Drei "
            "Kontostände relativ zum Jahresanfangswert liegen vor; $m$ ist der Monat:"
        ),
        "punkte_satz": "Im Monat $m = {x1}$ liegt der Kontostand relativ zum Anfangswert bei {y1} €, im Monat $m = {x2}$ bei {y2} € und im Monat $m = {x3}$ wieder bei {y3} €.",
        "fn": "K",
        "var": "m",
        "y_beschreibung": "den Kontostand relativ zum Jahresanfangswert in Euro",
        "x_beschreibung": "dem Monat $m$",
        "frage_xs": "Bestimmen Sie den Monat, in dem der Kontostand am niedrigsten ist.",
        "frage_ys": "Bestimmen Sie den niedrigsten Kontostand relativ zum Anfangswert.",
        "frage_ns": "Bestimmen Sie die beiden Monate, in denen der Kontostand genau dem Anfangswert entspricht.",
        "frage_eval": "Bestimmen Sie den Kontostand relativ zum Anfangswert im Monat $m = {x_text}$.",
        "frage_inverse": "Bestimmen Sie den weiteren Monat, in dem der Kontostand ebenfalls {y_text} € relativ zum Anfangswert beträgt.",
        "eval_step": 1,
        "a_choices": [50],
        "w_choices": [3, 4],
        "d_choices": [5, 6, 7, 8],
    },
    {
        "extremum": "min",
        "intro": (
            "Eine Straße führt durch eine Unterführung unter einer Bahnlinie "
            "hindurch. Die Fahrbahnhöhe relativ zum normalen Straßenniveau "
            "lässt sich quadratisch beschreiben; $x$ ist der Abstand vom "
            "Beginn der Absenkung:"
        ),
        "punkte_satz": "In {x1} m Abstand liegt die Fahrbahnhöhe relativ zum Normalniveau bei {y1} m, in {x2} m Abstand bei {y2} m und in {x3} m Abstand bei {y3} m.",
        "fn": "h",
        "var": "x",
        "y_beschreibung": "die Fahrbahnhöhe relativ zum Normalniveau in Metern",
        "x_beschreibung": "dem Abstand $x$ vom Beginn der Absenkung in Metern",
        "frage_xs": "Bestimmen Sie den Abstand, in dem die Fahrbahn am tiefsten liegt.",
        "frage_ys": "Bestimmen Sie die niedrigste Fahrbahnhöhe relativ zum Normalniveau.",
        "frage_ns": "Bestimmen Sie die beiden Stellen, an denen die Fahrbahn genau auf Normalniveau liegt.",
        "frage_eval": "Bestimmen Sie die Fahrbahnhöhe relativ zum Normalniveau in {x_text} m Abstand vom Beginn der Absenkung.",
        "frage_inverse": "Bestimmen Sie den weiteren Abstand vom Beginn der Absenkung, in dem die Fahrbahnhöhe ebenfalls {y_text} m relativ zum Normalniveau beträgt.",
        "a_choices": [0.05],
        "w_choices": [8, 10],
        "d_choices": [],
    },
]


class OptimierungQuadGenerator(TaskGenerator):
    generator_key = "analysis.quadratische_funktionen.optimierung_quad"

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
        is_max = sz["extremum"] == "max"
        a = rng.choice(sz["a_choices"])
        w = rng.choice(sz["w_choices"])

        if sz["d_choices"]:
            d_options = [d for d in sz["d_choices"] if d >= w]
            if not d_options:
                return None
            d = rng.choice(d_options)
        else:
            # Nullstelle bei 0 (z. B. Fläche, Unterführung).
            d = w

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

        # Drei Beobachtungspunkte zwischen den Nullstellen, nie Scheitel/Nullstellen.
        pool = [x for x in range(x1_ns + 1, x2_ns) if x != d]
        if len(pool) < 3:
            return None
        px = sorted(rng.sample(pool, 3))
        py = [f(x) for x in px]
        if not all(clean(v) for v in py):
            return None
        if is_max and not all(v > 0 for v in py):
            return None
        if not is_max and not all(v < 0 for v in py):
            return None

        eval_step = sz.get("eval_step", 0.5)
        eval_pool = [
            x1_ns + step * eval_step
            for step in range(1, round(2 * w / eval_step))
            if x1_ns + step * eval_step != d
            and x1_ns + step * eval_step not in px
            and 2 * d - (x1_ns + step * eval_step) not in px
        ]
        if not eval_pool:
            return None
        x_eval = rng.choice(eval_pool)
        y_eval = f(x_eval)
        x_inverse = 2 * d - x_eval

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
        var = sz["var"]

        fragen = [
            (
                f"Bestimmen Sie die Gleichung der Funktion "
                f"$ {fn}({var}) = a{var}^2 + b{var} + c $, die "
                f"{sz['y_beschreibung']} in Abhängigkeit von "
                f"{sz['x_beschreibung']} angibt."
            ),
            sz["frage_xs"],
            sz["frage_ys"],
            sz["frage_ns"],
            sz["frage_eval"].format(x_text=_fmt_dez(x_eval)),
            sz["frage_inverse"].format(y_text=_fmt_dez(y_eval)),
        ]
        antworten = [
            (
                f"$ {fn}({var})= ${numerical_analysis_calc(float(a))}"
                f"$ {var}^2+ ${numerical_analysis_calc(float(b))}"
                f"$ {var}+ ${numerical_analysis_calc(float(c))}"
            ),
            f"$ {var} = ${numerical_analysis_calc(float(d))}",
            numerical_analysis_calc(float(y_s)),
            (
                f"$ {var}_1 = ${numerical_analysis_calc(float(x1_ns))}"
                f"$ \\quad {var}_2 = ${numerical_analysis_calc(float(x2_ns))}"
            ),
            numerical_analysis_calc(float(y_eval)),
            numerical_analysis_calc(float(x_inverse)),
        ]

        return Task(
            einleitung=einleitung,
            fragen=fragen,
            antworten=antworten,
        )
