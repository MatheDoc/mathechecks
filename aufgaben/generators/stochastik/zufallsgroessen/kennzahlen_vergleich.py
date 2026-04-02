"""Kennzahlen zweier Zufallsgrößen vergleichen – Erwartungswert und Standardabweichung.

Pro Aufgabe:
  1. Welche der beiden Zufallsgrößen hat den höheren (oder niedrigeren) Erwartungswert?
  2. Welche Zufallsgröße ist konstanter (kleinere Standardabweichung)?
  3. Ist ein gegebener Messwert für Größe A eine ungewöhnliche Abweichung?
  4. Ist ein gegebener Messwert für Größe B eine ungewöhnliche Abweichung?

Alle Fragen sind Multiple-Choice (3 Optionen).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc
from aufgaben.generators.base import TaskGenerator


# ── Formatierungshelfer ───────────────────────────────────────────────────

def _fmt(value: float, dec: int) -> str:
    """Zahl → LaTeX-String mit deutschem Dezimalkomma (für $ ... $)."""
    if dec == 0:
        return str(int(round(value)))
    return f"{value:.{dec}f}".replace(".", "{,}")


def _fmt_plain(value: float, dec: int) -> str:
    """Zahl → Text mit deutschem Dezimalkomma (für Fragetexte)."""
    if dec == 0:
        return str(int(round(value)))
    return f"{value:.{dec}f}".replace(".", ",")


def _gen_cat_value(mu: float, sigma: float, cat: int,
                   rng: random.Random, dec: int) -> float:
    """Zufälligen Wert in der angegebenen σ-Abstandskategorie erzeugen.

    Kategorien:
      0 – innerhalb 1σ         (|x – μ| ≤ σ)
      1 – ein bis zwei σ       (σ < |x – μ| ≤ 2σ)
      2 – mehr als zwei σ      (|x – μ| > 2σ)
    """
    fracs = [(0.20, 0.85), (1.15, 1.85), (2.20, 3.00)]
    lo, hi = fracs[cat]
    frac = rng.uniform(lo, hi)
    direction = rng.choice([-1, 1])
    x = round(mu + direction * frac * sigma, dec)
    # Physikalisch sinnvoll: Wert ≥ 0 (außer Temperatur, aber deren μ >> 3σ)
    return x


# ── MC-Optionen für Q3/Q4 (σ-Abstandskategorien, drei Varianten-Sets) ────

_Q34_OPTION_SETS: tuple[tuple[str, str, str], ...] = (
    (
        "Kein ungewöhnlicher Wert – er liegt innerhalb einer Standardabweichung"
        " vom Erwartungswert.",
        "Leicht erhöhte Abweichung – der Wert liegt ein bis zwei"
        " Standardabweichungen vom Erwartungswert entfernt.",
        "Deutliche Abweichung – der Wert liegt mehr als zwei"
        " Standardabweichungen vom Erwartungswert entfernt.",
    ),
    (
        "Normaler Bereich – der Abstand zum Erwartungswert beträgt weniger als"
        " eine Standardabweichung.",
        "Erhöhte, aber noch übliche Abweichung – zwischen einer und zwei"
        " Standardabweichungen vom Erwartungswert.",
        "Ungewöhnlicher Wert – der Abstand zum Erwartungswert überschreitet"
        " zwei Standardabweichungen.",
    ),
    (
        "Keine deutliche Abweichung – der Wert liegt im Bereich"
        " $ \\mu \\pm \\sigma $.",
        "Moderate Abweichung – der Wert liegt ein bis zwei Standardabweichungen"
        " außerhalb des Erwartungswerts.",
        "Starke Abweichung – der Abstand zum Erwartungswert übersteigt zwei"
        " Standardabweichungen.",
    ),
)


# ── Einleitungstemplates (drei Varianten) ────────────────────────────────
# Platzhalter: {sym}, {var_name}, {unit}, {ea}, {eb}, {ma}, {sa}, {mb}, {sb}

_INTRO_TPLS: tuple[str, ...] = (
    (
        "Zufallsgröße $ {sym} $: {var_name} in {unit}. "
        "{ea}: $ E({sym}_A) = {ma} $, $ \\sigma({sym}_A) = {sa} $; "
        "{eb}: $ E({sym}_B) = {mb} $, $ \\sigma({sym}_B) = {sb} $."
    ),
    (
        "{var_name} in {unit} wird für {ea} und {eb} als Zufallsgröße"
        " $ {sym} $ modelliert. "
        "Für {ea}: $ E({sym}_A) = {ma} $, $ \\sigma({sym}_A) = {sa} $. "
        "Für {eb}: $ E({sym}_B) = {mb} $, $ \\sigma({sym}_B) = {sb} $."
    ),
    (
        "Für den Vergleich von {ea} und {eb} liegen folgende Kennzahlen der"
        " Zufallsgröße $ {sym} $ ({var_name}, in {unit}) vor: "
        "$ E({sym}_A) = {ma} $, $ \\sigma({sym}_A) = {sa} $, "
        "$ E({sym}_B) = {mb} $, $ \\sigma({sym}_B) = {sb} $."
    ),
)


# ── Szenario-Datenklasse ─────────────────────────────────────────────────

@dataclass(frozen=True)
class VarScenario:
    var_symbol: str          # LaTeX-Buchstabe, z.B. „E"
    var_name: str            # z.B. „Stromertrag pro Tag"
    unit: str                # z.B. „kWh"
    entity_a: str            # z.B. „Anlage A"
    entity_b: str            # z.B. „Anlage B"
    mu_center: float         # typischer Mittelwert
    mu_step: float           # Schritteinheit für μ-Differenzen
    sigma_base: float        # typischer σ-Wert
    decimals: int            # Nachkommastellen
    q1_seeks_lower: bool     # True → Q1 fragt nach kleinerem E (z.B. Lieferzeit)
    q1_variants: tuple       # Fragevarianten für Q1
    q1_equal_text: str       # MC-Option „beide gleich" für Q1
    q2_variants: tuple       # Fragevarianten für Q2
    q2_equal_text: str       # MC-Option „beide gleich" für Q2
    q3_templates: tuple      # Fragetemplates für Q3 (Platzhalter: {x})
    q4_templates: tuple      # Fragetemplates für Q4 (Platzhalter: {x})


# ── Szenario-Pool ────────────────────────────────────────────────────────

SCENARIOS: list[VarScenario] = [

    # 1) Solaranlagen
    VarScenario(
        var_symbol="E",
        var_name="Stromertrag pro Tag",
        unit="kWh",
        entity_a="Anlage A",
        entity_b="Anlage B",
        mu_center=400.0, mu_step=20.0, sigma_base=30.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welche Anlage liefert im Mittel mehr Strom?",
            "Bei welcher Anlage ist der durchschnittliche Tagesertrag größer?",
        ),
        q1_equal_text="Beide Anlagen haben den gleichen mittleren Stromertrag.",
        q2_variants=(
            "Welche Anlage arbeitet gleichmäßiger?",
            "Bei welcher Anlage sind die täglichen Schwankungen im Stromertrag geringer?",
        ),
        q2_equal_text="Beide Anlagen haben die gleiche Standardabweichung.",
        q3_templates=(
            "An einem Tag produzierte Anlage A {x} kWh."
            " Handelt es sich um eine ungewöhnliche Abweichung vom Erwartungswert?",
            "Anlage A erzielte an einem Tag einen Ertrag von {x} kWh."
            " Wie ist dieser Wert einzuordnen?",
        ),
        q4_templates=(
            "An einem Tag produzierte Anlage B {x} kWh."
            " Handelt es sich um eine ungewöhnliche Abweichung vom Erwartungswert?",
            "Anlage B erzielte an einem Tag einen Ertrag von {x} kWh."
            " Wie ist dieser Wert einzuordnen?",
        ),
    ),

    # 2) Investitionsfonds
    VarScenario(
        var_symbol="G",
        var_name="tägliche Rendite",
        unit="€",
        entity_a="Fonds X",
        entity_b="Fonds Y",
        mu_center=800.0, mu_step=50.0, sigma_base=100.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welcher Fonds liefert im Durchschnitt die höhere Rendite?",
            "Bei welchem Fonds ist die mittlere Tagesrendite größer?",
        ),
        q1_equal_text="Beide Fonds haben im Mittel die gleiche Rendite.",
        q2_variants=(
            "Welcher Fonds weist geringere Schwankungen in der Rendite auf?",
            "Welcher Fonds ist die stabilere Anlage?",
        ),
        q2_equal_text="Beide Fonds haben die gleiche Streuung.",
        q3_templates=(
            "Fonds X erzielte an einem Tag eine Rendite von {x} €."
            " Handelt es sich um einen ungewöhnlichen Wert?",
            "An einem Handelstag erwirtschaftete Fonds X {x} €."
            " Wie ist dies im Kontext der Verteilung einzuordnen?",
        ),
        q4_templates=(
            "Fonds Y erzielte an einem Tag eine Rendite von {x} €."
            " Handelt es sich um einen ungewöhnlichen Wert?",
            "An einem Handelstag erwirtschaftete Fonds Y {x} €."
            " Wie ist dies im Kontext der Verteilung einzuordnen?",
        ),
    ),

    # 3) Produktionslinien
    VarScenario(
        var_symbol="P",
        var_name="Tagesproduktion",
        unit="Stück",
        entity_a="Linie A",
        entity_b="Linie B",
        mu_center=2500.0, mu_step=100.0, sigma_base=200.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welche Produktionslinie stellt im Mittel mehr Stücke her?",
            "Bei welcher Linie ist die durchschnittliche Tagesproduktion höher?",
        ),
        q1_equal_text="Beide Linien haben die gleiche mittlere Tagesproduktion.",
        q2_variants=(
            "Welche Linie produziert konstanter?",
            "Bei welcher Linie schwankt die Tagesproduktion weniger?",
        ),
        q2_equal_text="Beide Linien haben die gleiche Standardabweichung.",
        q3_templates=(
            "Linie A fertigte an einem Tag {x} Stück."
            " Ist das eine deutliche Abweichung vom Erwartungswert?",
            "An einem Arbeitstag produzierte Linie A {x} Stück."
            " Wie würden Sie diesen Wert einordnen?",
        ),
        q4_templates=(
            "Linie B fertigte an einem Tag {x} Stück."
            " Ist das eine deutliche Abweichung vom Erwartungswert?",
            "An einem Arbeitstag produzierte Linie B {x} Stück."
            " Wie würden Sie diesen Wert einordnen?",
        ),
    ),

    # 4) Paketdienstleister (q1_seeks_lower: kürzere Lieferzeit ist besser)
    VarScenario(
        var_symbol="L",
        var_name="Lieferzeit",
        unit="h",
        entity_a="Anbieter A",
        entity_b="Anbieter B",
        mu_center=48.0, mu_step=2.0, sigma_base=5.0, decimals=1,
        q1_seeks_lower=True,
        q1_variants=(
            "Bei welchem Anbieter ist die durchschnittliche Lieferzeit kürzer?",
            "Welcher Anbieter liefert im Mittel schneller?",
        ),
        q1_equal_text="Beide Anbieter haben die gleiche durchschnittliche Lieferzeit.",
        q2_variants=(
            "Welcher Anbieter liefert zuverlässiger (geringere Schwankungen)?",
            "Welcher Anbieter ist in seiner Lieferzeit konstanter?",
        ),
        q2_equal_text="Beide Anbieter haben die gleiche Standardabweichung.",
        q3_templates=(
            "Eine Lieferung von Anbieter A traf nach {x} h ein."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "Anbieter A hatte bei einer Lieferung eine Lieferzeit von {x} h."
            " Wie ist dies einzuordnen?",
        ),
        q4_templates=(
            "Eine Lieferung von Anbieter B traf nach {x} h ein."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "Anbieter B hatte bei einer Lieferung eine Lieferzeit von {x} h."
            " Wie ist dies einzuordnen?",
        ),
    ),

    # 5) Filialen – Tagesumsatz
    VarScenario(
        var_symbol="U",
        var_name="Tagesumsatz",
        unit="€",
        entity_a="Filiale Nord",
        entity_b="Filiale Süd",
        mu_center=12000.0, mu_step=500.0, sigma_base=1200.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welche Filiale erzielt im Durchschnitt den höheren Tagesumsatz?",
            "Bei welcher Filiale ist der mittlere Tagesumsatz größer?",
        ),
        q1_equal_text="Beide Filialen haben den gleichen mittleren Tagesumsatz.",
        q2_variants=(
            "Bei welcher Filiale schwankt der Tagesumsatz weniger?",
            "Welche Filiale weist gleichmäßigere Umsatzzahlen auf?",
        ),
        q2_equal_text="Beide Filialen haben die gleiche Standardabweichung.",
        q3_templates=(
            "Filiale Nord erzielte an einem Tag einen Umsatz von {x} €."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "An einem Verkaufstag erwirtschaftete Filiale Nord {x} €."
            " Wie ist dieser Wert zu bewerten?",
        ),
        q4_templates=(
            "Filiale Süd erzielte an einem Tag einen Umsatz von {x} €."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "An einem Verkaufstag erwirtschaftete Filiale Süd {x} €."
            " Wie ist dieser Wert zu bewerten?",
        ),
    ),

    # 6) Museen / Ausstellungsorte – Besucherzahl
    VarScenario(
        var_symbol="B",
        var_name="tägliche Besucherzahl",
        unit="Personen",
        entity_a="Standort A",
        entity_b="Standort B",
        mu_center=500.0, mu_step=25.0, sigma_base=60.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welcher Standort verzeichnet im Mittel mehr Besucher?",
            "Bei welchem Standort ist die durchschnittliche Besucherzahl größer?",
        ),
        q1_equal_text="Beide Standorte haben die gleiche mittlere Besucherzahl.",
        q2_variants=(
            "Bei welchem Standort sind die Besucherzahlen stabiler?",
            "Welcher Standort weist geringere Schwankungen in der Besucherzahl auf?",
        ),
        q2_equal_text="Beide Standorte haben die gleiche Standardabweichung.",
        q3_templates=(
            "An einem Tag besuchten {x} Personen Standort A."
            " Ist das ein ungewöhnlicher Wert?",
            "Standort A zählte an einem Tag {x} Besucher."
            " Wie ist dieser Wert einzuordnen?",
        ),
        q4_templates=(
            "An einem Tag besuchten {x} Personen Standort B."
            " Ist das ein ungewöhnlicher Wert?",
            "Standort B zählte an einem Tag {x} Besucher."
            " Wie ist dieser Wert einzuordnen?",
        ),
    ),

    # 7) Prüfungsgruppen – Punktzahl
    VarScenario(
        var_symbol="N",
        var_name="Prüfungspunktzahl",
        unit="Punkte",
        entity_a="Gruppe A",
        entity_b="Gruppe B",
        mu_center=65.0, mu_step=3.0, sigma_base=8.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welche Gruppe erzielt im Schnitt mehr Punkte?",
            "Bei welcher Gruppe ist die mittlere Prüfungspunktzahl höher?",
        ),
        q1_equal_text="Beide Gruppen haben die gleiche mittlere Punktzahl.",
        q2_variants=(
            "Welche Gruppe schneidet gleichmäßiger ab?",
            "Bei welcher Gruppe sind die Prüfungsergebnisse weniger gestreut?",
        ),
        q2_equal_text="Beide Gruppen haben die gleiche Standardabweichung.",
        q3_templates=(
            "Eine Schülerin aus Gruppe A erzielte {x} Punkte."
            " Ist das ein ungewöhnliches Ergebnis?",
            "Ein Schüler aus Gruppe A erreichte {x} Punkte."
            " Wie ist dieses Ergebnis einzuordnen?",
        ),
        q4_templates=(
            "Eine Schülerin aus Gruppe B erzielte {x} Punkte."
            " Ist das ein ungewöhnliches Ergebnis?",
            "Ein Schüler aus Gruppe B erreichte {x} Punkte."
            " Wie ist dieses Ergebnis einzuordnen?",
        ),
    ),

    # 8) Industriemaschinen – Vorgangsdauer (seeks_lower: kürzere Dauer besser)
    VarScenario(
        var_symbol="D",
        var_name="Vorgangsdauer",
        unit="s",
        entity_a="Maschine A",
        entity_b="Maschine B",
        mu_center=30.0, mu_step=1.0, sigma_base=2.5, decimals=1,
        q1_seeks_lower=True,
        q1_variants=(
            "Welche Maschine hat im Mittel eine kürzere Vorgangsdauer?",
            "Bei welcher Maschine liegt der durchschnittliche Vorgang zeitlich niedriger?",
        ),
        q1_equal_text="Beide Maschinen haben die gleiche mittlere Vorgangsdauer.",
        q2_variants=(
            "Welche Maschine arbeitet präziser (geringere Streuung)?",
            "Bei welcher Maschine ist die Vorgangsdauer konstanter?",
        ),
        q2_equal_text="Beide Maschinen haben die gleiche Standardabweichung.",
        q3_templates=(
            "Ein Vorgang an Maschine A dauerte {x} s."
            " Handelt es sich um eine deutliche Abweichung?",
            "Maschine A benötigte für einen Vorgang {x} s."
            " Ist das ein ungewöhnlicher Wert?",
        ),
        q4_templates=(
            "Ein Vorgang an Maschine B dauerte {x} s."
            " Handelt es sich um eine deutliche Abweichung?",
            "Maschine B benötigte für einen Vorgang {x} s."
            " Ist das ein ungewöhnlicher Wert?",
        ),
    ),

    # 9) Online-Shops – Tagesbestellungen
    VarScenario(
        var_symbol="K",
        var_name="Anzahl der Tagesbestellungen",
        unit="Bestellungen",
        entity_a="Shop A",
        entity_b="Shop B",
        mu_center=850.0, mu_step=40.0, sigma_base=100.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welcher Shop erhält im Mittel mehr Bestellungen pro Tag?",
            "Bei welchem Shop ist die mittlere Anzahl an Tagesbestellungen höher?",
        ),
        q1_equal_text="Beide Shops haben die gleiche mittlere Anzahl an Tagesbestellungen.",
        q2_variants=(
            "Welcher Shop weist konstantere Bestellzahlen auf?",
            "Bei welchem Shop schwankt die Anzahl der Tagesbestellungen weniger?",
        ),
        q2_equal_text="Beide Shops haben die gleiche Standardabweichung.",
        q3_templates=(
            "An einem Tag gingen bei Shop A {x} Bestellungen ein."
            " Ist das eine ungewöhnliche Abweichung?",
            "Shop A verzeichnete an einem Tag {x} Bestellungen."
            " Wie ist dies einzuordnen?",
        ),
        q4_templates=(
            "An einem Tag gingen bei Shop B {x} Bestellungen ein."
            " Ist das eine ungewöhnliche Abweichung?",
            "Shop B verzeichnete an einem Tag {x} Bestellungen."
            " Wie ist dies einzuordnen?",
        ),
    ),

    # 10) Landwirtschaftliche Betriebe – Tagesertrag
    VarScenario(
        var_symbol="M",
        var_name="tägliche Ernte",
        unit="kg",
        entity_a="Betrieb A",
        entity_b="Betrieb B",
        mu_center=1200.0, mu_step=50.0, sigma_base=150.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welcher Betrieb erntet im Durchschnitt mehr?",
            "Bei welchem Betrieb ist der mittlere Tagesertrag größer?",
        ),
        q1_equal_text="Beide Betriebe haben den gleichen mittleren Tagesertrag.",
        q2_variants=(
            "Bei welchem Betrieb ist der Tagesertrag konstanter?",
            "Welcher Betrieb weist geringere Schwankungen im Ernteertrag auf?",
        ),
        q2_equal_text="Beide Betriebe haben die gleiche Standardabweichung.",
        q3_templates=(
            "Betrieb A erntete an einem Tag {x} kg."
            " Ist das eine deutliche Abweichung vom Erwartungswert?",
            "An einem Erntetag brachte Betrieb A {x} kg ein."
            " Wie ist dieser Wert zu bewerten?",
        ),
        q4_templates=(
            "Betrieb B erntete an einem Tag {x} kg."
            " Ist das eine deutliche Abweichung vom Erwartungswert?",
            "An einem Erntetag brachte Betrieb B {x} kg ein."
            " Wie ist dieser Wert zu bewerten?",
        ),
    ),

    # 11) Wetterstationen – Tageshöchsttemperatur
    VarScenario(
        var_symbol="T",
        var_name="Tageshöchsttemperatur",
        unit="°C",
        entity_a="Station A",
        entity_b="Station B",
        mu_center=18.0, mu_step=0.5, sigma_base=2.5, decimals=1,
        q1_seeks_lower=False,
        q1_variants=(
            "An welcher Station ist die durchschnittliche Tageshöchsttemperatur höher?",
            "Welche Station weist im Mittel wärmere Tageshöchsttemperaturen auf?",
        ),
        q1_equal_text="Beide Stationen haben die gleiche mittlere Tageshöchsttemperatur.",
        q2_variants=(
            "Welche Station hat gleichmäßigere Temperaturen?",
            "Bei welcher Station schwankt die Tageshöchsttemperatur weniger?",
        ),
        q2_equal_text="Beide Stationen haben die gleiche Standardabweichung.",
        q3_templates=(
            "Station A maß an einem Tag eine Höchsttemperatur von {x} °C."
            " Handelt es sich um einen ungewöhnlichen Wert?",
            "An einem Tag betrug die Höchsttemperatur an Station A {x} °C."
            " Wie ist dies einzuordnen?",
        ),
        q4_templates=(
            "Station B maß an einem Tag eine Höchsttemperatur von {x} °C."
            " Handelt es sich um einen ungewöhnlichen Wert?",
            "An einem Tag betrug die Höchsttemperatur an Station B {x} °C."
            " Wie ist dies einzuordnen?",
        ),
    ),

    # 12) Kassenschalter – Wartezeit (seeks_lower: kürzere Wartezeit besser)
    VarScenario(
        var_symbol="W",
        var_name="Wartezeit",
        unit="min",
        entity_a="Schalter A",
        entity_b="Schalter B",
        mu_center=8.0, mu_step=0.5, sigma_base=1.5, decimals=1,
        q1_seeks_lower=True,
        q1_variants=(
            "An welchem Schalter ist die durchschnittliche Wartezeit kürzer?",
            "Welcher Schalter hat im Mittel einen niedrigeren Erwartungswert der Wartezeit?",
        ),
        q1_equal_text="Beide Schalter haben die gleiche mittlere Wartezeit.",
        q2_variants=(
            "An welchem Schalter sind die Wartezeiten konstanter?",
            "Welcher Schalter weist geringere Schwankungen in der Wartezeit auf?",
        ),
        q2_equal_text="Beide Schalter haben die gleiche Standardabweichung.",
        q3_templates=(
            "Ein Kunde wartete an Schalter A genau {x} min."
            " Handelt es sich um eine ungewöhnlich lange Wartezeit?",
            "An Schalter A betrug die Wartezeit einmal {x} min."
            " Wie ist dies einzuordnen?",
        ),
        q4_templates=(
            "Ein Kunde wartete an Schalter B genau {x} min."
            " Handelt es sich um eine ungewöhnlich lange Wartezeit?",
            "An Schalter B betrug die Wartezeit einmal {x} min."
            " Wie ist dies einzuordnen?",
        ),
    ),

    # 13) Stromverbrauch – Maschinen
    VarScenario(
        var_symbol="S",
        var_name="täglicher Stromverbrauch",
        unit="kWh",
        entity_a="Maschine X",
        entity_b="Maschine Y",
        mu_center=36.0, mu_step=2.0, sigma_base=4.0, decimals=1,
        q1_seeks_lower=True,
        q1_variants=(
            "Welche Maschine verbraucht im Mittel weniger Strom?",
            "Bei welcher Maschine ist der durchschnittliche Tagesverbrauch geringer?",
        ),
        q1_equal_text="Beide Maschinen haben den gleichen mittleren Stromverbrauch.",
        q2_variants=(
            "Bei welcher Maschine ist der Stromverbrauch gleichmäßiger?",
            "Welche Maschine weist geringere Schwankungen im Tagesverbrauch auf?",
        ),
        q2_equal_text="Beide Maschinen haben die gleiche Standardabweichung.",
        q3_templates=(
            "Maschine X verbrauchte an einem Tag {x} kWh."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "An einem Tag lag der Stromverbrauch von Maschine X bei {x} kWh."
            " Wie ist dieser Wert einzuordnen?",
        ),
        q4_templates=(
            "Maschine Y verbrauchte an einem Tag {x} kWh."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "An einem Tag lag der Stromverbrauch von Maschine Y bei {x} kWh."
            " Wie ist dieser Wert einzuordnen?",
        ),
    ),

    # 14) Wöchentliche Verkäufe – Produkte
    VarScenario(
        var_symbol="V",
        var_name="wöchentliche Verkaufszahl",
        unit="Einheiten",
        entity_a="Produkt A",
        entity_b="Produkt B",
        mu_center=850.0, mu_step=30.0, sigma_base=120.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welches Produkt wird im Mittel häufiger verkauft?",
            "Bei welchem Produkt ist die durchschnittliche wöchentliche Verkaufszahl höher?",
        ),
        q1_equal_text="Beide Produkte haben die gleiche mittlere Verkaufszahl.",
        q2_variants=(
            "Bei welchem Produkt ist die Nachfrage konstanter?",
            "Welches Produkt weist geringere Schwankungen in den Verkaufszahlen auf?",
        ),
        q2_equal_text="Beide Produkte haben die gleiche Standardabweichung.",
        q3_templates=(
            "In einer Woche wurden von Produkt A {x} Einheiten verkauft."
            " Ist das eine ungewöhnliche Abweichung?",
            "Produkt A erzielte in einer Woche {x} Verkäufe."
            " Wie ist dieser Wert einzuordnen?",
        ),
        q4_templates=(
            "In einer Woche wurden von Produkt B {x} Einheiten verkauft."
            " Ist das eine ungewöhnliche Abweichung?",
            "Produkt B erzielte in einer Woche {x} Verkäufe."
            " Wie ist dieser Wert einzuordnen?",
        ),
    ),

    # 15) Fahrdienst – Tageskilometer
    VarScenario(
        var_symbol="F",
        var_name="täglich zurückgelegte Strecke",
        unit="km",
        entity_a="Fahrer A",
        entity_b="Fahrer B",
        mu_center=280.0, mu_step=10.0, sigma_base=35.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welcher Fahrer legt im Mittel mehr Kilometer zurück?",
            "Bei welchem Fahrer ist die durchschnittliche Tagesstrecke länger?",
        ),
        q1_equal_text="Beide Fahrer legen im Mittel die gleiche Tagesstrecke zurück.",
        q2_variants=(
            "Bei welchem Fahrer ist die Tagesstrecke gleichmäßiger?",
            "Welcher Fahrer weist geringere Schwankungen in der täglich gefahrenen Strecke auf?",
        ),
        q2_equal_text="Beide Fahrer haben die gleiche Standardabweichung.",
        q3_templates=(
            "Fahrer A legte an einem Tag {x} km zurück."
            " Ist das eine deutliche Abweichung vom Erwartungswert?",
            "An einem Arbeitstag fuhr Fahrer A {x} km."
            " Wie ist dieser Wert zu bewerten?",
        ),
        q4_templates=(
            "Fahrer B legte an einem Tag {x} km zurück."
            " Ist das eine deutliche Abweichung vom Erwartungswert?",
            "An einem Arbeitstag fuhr Fahrer B {x} km."
            " Wie ist dieser Wert zu bewerten?",
        ),
    ),

    # 16) Klinik – Behandlungsdauer (seeks_lower: kürzere Dauer besser)
    VarScenario(
        var_symbol="H",
        var_name="Behandlungsdauer",
        unit="min",
        entity_a="Abteilung A",
        entity_b="Abteilung B",
        mu_center=45.0, mu_step=2.0, sigma_base=8.0, decimals=0,
        q1_seeks_lower=True,
        q1_variants=(
            "In welcher Abteilung ist die durchschnittliche Behandlungsdauer kürzer?",
            "Welche Abteilung behandelt Patienten im Mittel schneller?",
        ),
        q1_equal_text="Beide Abteilungen haben die gleiche mittlere Behandlungsdauer.",
        q2_variants=(
            "In welcher Abteilung sind die Behandlungszeiten gleichmäßiger?",
            "Welche Abteilung weist geringere Schwankungen in der Behandlungsdauer auf?",
        ),
        q2_equal_text="Beide Abteilungen haben die gleiche Standardabweichung.",
        q3_templates=(
            "Eine Behandlung in Abteilung A dauerte {x} min."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "In Abteilung A betrug die Behandlungsdauer einmal {x} min."
            " Wie ist dieser Wert einzuordnen?",
        ),
        q4_templates=(
            "Eine Behandlung in Abteilung B dauerte {x} min."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "In Abteilung B betrug die Behandlungsdauer einmal {x} min."
            " Wie ist dieser Wert einzuordnen?",
        ),
    ),

    # 17) Mitarbeiter – bearbeitete Aufträge pro Tag
    VarScenario(
        var_symbol="A",
        var_name="Anzahl bearbeiteter Aufträge pro Tag",
        unit="Aufträge",
        entity_a="Mitarbeiter A",
        entity_b="Mitarbeiter B",
        mu_center=22.0, mu_step=1.0, sigma_base=3.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welcher Mitarbeiter bearbeitet im Mittel mehr Aufträge pro Tag?",
            "Bei welchem Mitarbeiter ist die durchschnittliche Tagesleistung höher?",
        ),
        q1_equal_text="Beide Mitarbeiter bearbeiten im Mittel gleich viele Aufträge.",
        q2_variants=(
            "Welcher Mitarbeiter arbeitet gleichmäßiger?",
            "Bei welchem Mitarbeiter schwankt die Tagesleistung weniger?",
        ),
        q2_equal_text="Beide Mitarbeiter haben die gleiche Standardabweichung.",
        q3_templates=(
            "Mitarbeiter A bearbeitete an einem Tag {x} Aufträge."
            " Ist das eine deutliche Abweichung vom Erwartungswert?",
            "An einem Arbeitstag erledigte Mitarbeiter A {x} Aufträge."
            " Wie ist dieser Wert einzuordnen?",
        ),
        q4_templates=(
            "Mitarbeiter B bearbeitete an einem Tag {x} Aufträge."
            " Ist das eine deutliche Abweichung vom Erwartungswert?",
            "An einem Arbeitstag erledigte Mitarbeiter B {x} Aufträge."
            " Wie ist dieser Wert einzuordnen?",
        ),
    ),

    # 18) Sportzentrum – Trainingseinheiten pro Tag
    VarScenario(
        var_symbol="R",
        var_name="Anzahl der Trainingseinheiten pro Tag",
        unit="Einheiten",
        entity_a="Zentrum A",
        entity_b="Zentrum B",
        mu_center=38.0, mu_step=2.0, sigma_base=5.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welches Zentrum bietet im Mittel mehr Trainingseinheiten an?",
            "Bei welchem Zentrum ist die durchschnittliche Anzahl täglicher Trainingseinheiten höher?",
        ),
        q1_equal_text="Beide Zentren bieten im Mittel gleich viele Trainingseinheiten an.",
        q2_variants=(
            "Bei welchem Zentrum ist das Angebot an Trainingseinheiten gleichmäßiger?",
            "Welches Zentrum weist geringere Schwankungen in der täglichen Anzahl von Trainingseinheiten auf?",
        ),
        q2_equal_text="Beide Zentren haben die gleiche Standardabweichung.",
        q3_templates=(
            "An einem Tag bot Zentrum A {x} Trainingseinheiten an."
            " Ist das ein ungewöhnlicher Wert?",
            "Zentrum A verzeichnete an einem Tag {x} Trainingseinheiten."
            " Wie ist dieser Wert einzuordnen?",
        ),
        q4_templates=(
            "An einem Tag bot Zentrum B {x} Trainingseinheiten an."
            " Ist das ein ungewöhnlicher Wert?",
            "Zentrum B verzeichnete an einem Tag {x} Trainingseinheiten."
            " Wie ist dieser Wert einzuordnen?",
        ),
    ),

    # 19) Logistik – täglicher Lagerbestand
    VarScenario(
        var_symbol="Z",
        var_name="täglicher Lagerbestand",
        unit="Einheiten",
        entity_a="Lager Nord",
        entity_b="Lager Süd",
        mu_center=3500.0, mu_step=100.0, sigma_base=400.0, decimals=0,
        q1_seeks_lower=False,
        q1_variants=(
            "Welches Lager hat im Mittel einen höheren Bestand?",
            "Bei welchem Lager ist der durchschnittliche Tagesbestand größer?",
        ),
        q1_equal_text="Beide Lager haben im Mittel den gleichen Bestand.",
        q2_variants=(
            "Bei welchem Lager schwankt der Bestand weniger?",
            "Welches Lager weist einen gleichmäßigeren Tagesbestand auf?",
        ),
        q2_equal_text="Beide Lager haben die gleiche Standardabweichung.",
        q3_templates=(
            "Lager Nord verzeichnete an einem Tag einen Bestand von {x} Einheiten."
            " Ist das eine deutliche Abweichung?",
            "An einem Tag lag der Bestand in Lager Nord bei {x} Einheiten."
            " Wie ist dieser Wert einzuordnen?",
        ),
        q4_templates=(
            "Lager Süd verzeichnete an einem Tag einen Bestand von {x} Einheiten."
            " Ist das eine deutliche Abweichung?",
            "An einem Tag lag der Bestand in Lager Süd bei {x} Einheiten."
            " Wie ist dieser Wert einzuordnen?",
        ),
    ),

    # 20) Callcenter – Gesprächsdauer (seeks_lower: kürzere Dauer effizienter)
    VarScenario(
        var_symbol="C",
        var_name="durchschnittliche Gesprächsdauer",
        unit="min",
        entity_a="Team A",
        entity_b="Team B",
        mu_center=6.5, mu_step=0.2, sigma_base=1.0, decimals=1,
        q1_seeks_lower=True,
        q1_variants=(
            "Welches Team hat im Mittel kürzere Gespräche?",
            "Bei welchem Team ist die durchschnittliche Gesprächsdauer geringer?",
        ),
        q1_equal_text="Beide Teams haben die gleiche mittlere Gesprächsdauer.",
        q2_variants=(
            "Bei welchem Team sind die Gesprächsdauern gleichmäßiger?",
            "Welches Team weist geringere Schwankungen in der Gesprächsdauer auf?",
        ),
        q2_equal_text="Beide Teams haben die gleiche Standardabweichung.",
        q3_templates=(
            "Ein Gespräch in Team A dauerte {x} min."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "Team A hatte ein Gespräch mit einer Dauer von {x} min."
            " Wie ist dieser Wert einzuordnen?",
        ),
        q4_templates=(
            "Ein Gespräch in Team B dauerte {x} min."
            " Handelt es sich um eine ungewöhnliche Abweichung?",
            "Team B hatte ein Gespräch mit einer Dauer von {x} min."
            " Wie ist dieser Wert einzuordnen?",
        ),
    ),
]


# ── Generator ─────────────────────────────────────────────────────────────

class KennzahlenVergleichGenerator(TaskGenerator):
    generator_key = "stochastik.zufallsgroessen.kennzahlen_vergleich"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for i in range(count):
            sc = SCENARIOS[i % len(SCENARIOS)]
            dec = sc.decimals

            # ── Erwartungswerte ────────────────────────────────────────
            mu_a = sc.mu_center + rng.randint(-3, 3) * sc.mu_step
            mu_a = max(mu_a, sc.mu_step)

            # ew_rel: 0=A>B, 1=A<B, 2=A==B
            ew_rel = rng.choices([0, 1, 2], weights=[4, 4, 2])[0]
            diff = rng.randint(1, 4) * sc.mu_step
            if ew_rel == 0:
                mu_b = max(mu_a - diff, sc.mu_step)
            elif ew_rel == 1:
                mu_b = mu_a + diff
            else:
                mu_b = mu_a

            mu_a = round(mu_a, dec)
            mu_b = round(mu_b, dec)

            # ── Standardabweichungen ───────────────────────────────────
            sigma_a = round(
                sc.sigma_base * rng.choice([0.5, 0.75, 1.0, 1.25, 1.5]), dec
            )
            min_sigma = 1 if dec == 0 else round(10 ** (-dec), dec)
            sigma_a = max(sigma_a, min_sigma)

            # sig_rel: 0=σ_A<σ_B (A konstanter), 1=σ_A>σ_B (B konstanter), 2=gleich
            sig_rel = rng.choices([0, 1, 2], weights=[4, 4, 2])[0]
            if sig_rel == 0:
                sigma_b = round(sigma_a * rng.choice([1.5, 2.0, 2.5, 3.0]), dec)
            elif sig_rel == 1:
                sigma_b = max(
                    round(sigma_a * rng.choice([0.33, 0.5, 0.67]), dec), min_sigma
                )
            else:
                sigma_b = sigma_a

            # ── Einleitung ─────────────────────────────────────────────
            intro_tpl = rng.choice(_INTRO_TPLS)
            einleitung_raw = intro_tpl.format(
                sym=sc.var_symbol,
                var_name=sc.var_name,
                unit=sc.unit,
                ea=sc.entity_a,
                eb=sc.entity_b,
                ma=_fmt(mu_a, dec),
                sa=_fmt(sigma_a, dec),
                mb=_fmt(mu_b, dec),
                sb=_fmt(sigma_b, dec),
            )
            einleitung = einleitung_raw[0].upper() + einleitung_raw[1:]

            # ── Q1: Erwartungswert ─────────────────────────────────────
            q1_text = rng.choice(sc.q1_variants)
            q1_opts = [f"{sc.entity_a}.", f"{sc.entity_b}.", sc.q1_equal_text]
            # Bei seeks_lower: A>B → B ist kürzer → korrekt=1; A<B → A kürzer → korrekt=0
            q1_correct = [1, 0, 2][ew_rel] if sc.q1_seeks_lower else ew_rel

            # ── Q2: Standardabweichung ─────────────────────────────────
            q2_text = rng.choice(sc.q2_variants)
            q2_opts = [f"{sc.entity_a}.", f"{sc.entity_b}.", sc.q2_equal_text]
            q2_correct = sig_rel  # 0=A konstanter, 1=B konstanter, 2=gleich

            # ── Q3: Messwert für A einordnen ───────────────────────────
            cat_a = rng.choices([0, 1, 2], weights=[5, 4, 3])[0]
            x_a = _gen_cat_value(mu_a, sigma_a, cat_a, rng, dec)
            q3_text = rng.choice(sc.q3_templates).format(x=_fmt_plain(x_a, dec))
            opt_set_3 = rng.choice(_Q34_OPTION_SETS)

            # ── Q4: Messwert für B einordnen ───────────────────────────
            cat_b = rng.choices([0, 1, 2], weights=[5, 4, 3])[0]
            x_b = _gen_cat_value(mu_b, sigma_b, cat_b, rng, dec)
            q4_text = rng.choice(sc.q4_templates).format(x=_fmt_plain(x_b, dec))
            opt_set_4 = rng.choice(_Q34_OPTION_SETS)

            tasks.append(Task(
                einleitung=einleitung,
                fragen=[q1_text, q2_text, q3_text, q4_text],
                antworten=[
                    mc(q1_opts, correct_index=q1_correct),
                    mc(q2_opts, correct_index=q2_correct),
                    mc(list(opt_set_3), correct_index=cat_a),
                    mc(list(opt_set_4), correct_index=cat_b),
                ],
            ))

        return tasks
