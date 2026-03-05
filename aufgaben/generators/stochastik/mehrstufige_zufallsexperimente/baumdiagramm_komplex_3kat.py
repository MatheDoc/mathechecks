"""Komplexes Baumdiagramm – 3 Kategorien × 2 Ausgänge (Rückwärts-Modus).

Struktur: Zweistufiger Baum
  Stufe 1: drei Kategorien A, B, C  (P(A) + P(B) + P(C) = 1)
  Stufe 2: je zwei Ausgänge D, D̄    (P(D|X) + P(D̄|X) = 1)

Im Szenario-Text werden gegeben:
  - P(A), P(C)  → P(B) = 1 − P(A) − P(C) ist ableitbar
  - P(D|A), P(D|B)  als Prozentzahlen
  - P(D) gesamt  als Prozentzahl

Der/die Lernende muss das Baumdiagramm aufstellen und daraus drei Größen
bestimmen. Jede Frage wählt zufällig zwischen Ausgang D und D̄:
  1. P(C ∩ D)  bzw. P(C ∩ D̄)   – Verbundwahrscheinlichkeit für Kategorie C
  2. P(D|C)   bzw. P(D̄|C)      – bedingte Wahrscheinlichkeit für Kategorie C
                                   (Rückwärts-Rechnung: P(D|C) nicht direkt gegeben)
  3. P(A∩D) + P(B∩D)  bzw. entsprechend D̄
                                 – Verbund über die beiden direkt gegebenen Kategorien

Kein Visual in der Ausgabe – alle Fragen sind rein textuelle numerical-Slots.
"""

import random
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical
from aufgaben.generators.base import TaskGenerator


_Q4 = Decimal("0.0001")
_Q2 = Decimal("0.01")


def _r4(v: Decimal) -> Decimal:
    return v.quantize(_Q4, rounding=ROUND_HALF_UP)


def _r2(v: Decimal) -> Decimal:
    return v.quantize(_Q2, rounding=ROUND_HALF_UP)


def _f(v: Decimal) -> float:
    return float(v)


def _fmt_int(n: int) -> str:
    """Ganzzahl mit deutschem Tausenderpunkt, z. B. 80.000."""
    return f"{n:,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Scenario-Vorlage
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Template3Kat:
    """Thematische Vorlage für einen 3-Kategorien-Baum."""
    intro: str           # Satz 1: Beschreibung, um was es geht
    stage1_text: str     # Satz 2: Ausprägungen der 1. Stufe mit Abkürzungen
    stage2_text: str     # Satz 3: Ausprägungen der 2. Stufe mit Abkürzungen
    things: str          # Pluralform des Untersuchungsobjekts, z. B. "Laptops"
    cat_a: str           # Name Kategorie A   (z. B. "Einsteigergeräte (E)")
    cat_b: str           # Name Kategorie B
    cat_c: str           # Name Kategorie C
    out_d: str           # Positiver Ausgang  (z. B. "Windows (W)")
    out_nd: str          # Negativer Ausgang  (z. B. "macOS (m)")
    # Satz 4: bedingte Wahrscheinlichkeiten für A und B
    chance_stat_tmpl: str  # Platzhalter: {p_d_a_pct}, {p_d_b_pct}
    # Satz 5: absolute Häufigkeiten + P(D) gesamt
    abs_stat_tmpl: str     # Platzhalter: {n_fmt}, {p_d_pct}, {count_a_fmt}, {count_c_fmt}
    # Fragetexte: je Ausgang d (positiv) und nd (negativ)
    q1_d: str            # Q1: P(C ∩ D)   – joint für cat_c, Ausgang D
    q1_nd: str           # Q1: P(C ∩ D̄)  – joint für cat_c, Ausgang D̄
    q2_d: str            # Q2: P(D|C)     – konditional, Ausgang D (Rückwärts-Berechnung)
    q2_nd: str           # Q2: P(D̄|C)    – konditional, Ausgang D̄
    q3_d: str            # Q3: P(A∩D)+P(B∩D)   – joint A und B, Ausgang D
    q3_nd: str           # Q3: P(A∩D̄)+P(B∩D̄)  – joint A und B, Ausgang D̄
    # Formatierungshilfen für Angaben im Szenariotext
    label_a: str         # kurzes Label, z. B. "E" für Einsteigergeräte
    label_b: str
    label_c: str
    label_d: str


TEMPLATES: list[Template3Kat] = [
    # 1) Laptops
    Template3Kat(
        intro="In einem großen Elektronikfachmarkt wurden über mehrere Monate die Laptopverkäufe ausgewertet.",
        stage1_text="Die Laptops wurden nach der Preisklasse in Einsteigergeräte (E), Mittelklassegeräte (M) und Premiumgeräte (P) eingeteilt.",
        stage2_text="Zusätzlich wurde erfasst, ob ein Gerät Windows (W) oder macOS (m) nutzt.",
        things="Laptops",
        cat_a="Einsteigergeräte (E)",
        cat_b="Mittelklassegeräte (M)",
        cat_c="Premiumgeräte (P)",
        out_d="Windows (W)",
        out_nd="macOS (m)",
        chance_stat_tmpl=(
            "Bei den Einsteigergeräten liegt der Windows-Anteil bei {p_d_a_pct}\u00a0%, "
            "bei den Mittelklassegeräten bei {p_d_b_pct}\u00a0%."
        ),
        q1_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Laptop ein Premiumgerät mit Windows ist."
        ),
        q1_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Laptop ein Premiumgerät mit macOS ist."
        ),
        q2_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Premiumlaptop Windows nutzt."
        ),
        q2_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Premiumlaptop macOS nutzt."
        ),
        q3_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Laptop entweder ein Einsteigergerät mit Windows oder ein Mittelklassegerät mit Windows ist."
        ),
        q3_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Laptop entweder ein Einsteigergerät mit macOS oder ein Mittelklassegerät mit macOS ist."
        ),
        abs_stat_tmpl=(
            "Von insgesamt {n_fmt} erfassten Laptops nutzen {p_d_pct}\u00a0% Windows; "
            "darunter wurden {count_a_fmt} Einsteigergeräte und {count_c_fmt} Premiumgeräte verkauft."
        ),
        label_a="E", label_b="M", label_c="P", label_d="W",
    ),
    # 2) Studierende & Prüfung
    Template3Kat(
        intro="An einer Hochschule wurden die Ergebnisse einer Abschlussprüfung ausgewertet.",
        stage1_text="Die Studierenden wurden nach ihrem Studienfortschritt in drei Gruppen eingeteilt: Erstsemester (E), Mittelsemester (M) und Abschlussstudierende (A).",
        stage2_text="Beim Ergebnis wird unterschieden zwischen bestanden (B) und nicht bestanden (N).",
        things="Prüfungsteilnehmenden",
        cat_a="Erstsemester (E)",
        cat_b="Mittelsemester (M)",
        cat_c="Abschlussstudierende (A)",
        out_d="bestanden (B)",
        out_nd="nicht bestanden (N)",
        chance_stat_tmpl=(
            "Erstsemester bestehen die Prüfung mit {p_d_a_pct}\u00a0%, "
            "Mittelsemester mit {p_d_b_pct}\u00a0%."
        ),
        q1_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person in der Abschlussphase die Prüfung bestanden hat."
        ),
        q1_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person in der Abschlussphase die Prüfung nicht bestanden hat."
        ),
        q2_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Abschlussstudierende die Prüfung bestanden hat."
        ),
        q2_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Abschlussstudierende die Prüfung nicht bestanden hat."
        ),
        q3_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person ein Erstsemester oder ein Mittelsemester ist und die Prüfung bestanden hat."
        ),
        q3_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person ein Erstsemester oder ein Mittelsemester ist und die Prüfung nicht bestanden hat."
        ),
        abs_stat_tmpl=(
            "Von insgesamt {n_fmt} Prüfungsteilnehmenden haben {p_d_pct}\u00a0% die Prüfung bestanden; "
            "darunter waren {count_a_fmt} Erstsemester und {count_c_fmt} Abschlussstudierende."
        ),
        label_a="E", label_b="M", label_c="A", label_d="B",
    ),
    # 3) Patienten & Genesung
    Template3Kat(
        intro="In einer Klinik wurde der Genesungsverlauf nach einer Standardbehandlung dokumentiert.",
        stage1_text="Die Patientinnen und Patienten wurden nach dem Schweregrad eingeteilt: leicht (L), mittelschwer (M) und schwer (S) erkrankt.",
        stage2_text="Beim Verlauf wird unterschieden zwischen genesen (G) und nicht genesen (N).",
        things="Patientinnen und Patienten",
        cat_a="Leicht Erkrankte (L)",
        cat_b="Mittelschwer Erkrankte (M)",
        cat_c="Schwer Erkrankte (S)",
        out_d="genesen (G)",
        out_nd="nicht genesen (N)",
        chance_stat_tmpl=(
            "Leicht Erkrankte genesen mit {p_d_a_pct}\u00a0%, "
            "mittelschwer Erkrankte mit {p_d_b_pct}\u00a0%."
        ),
        q1_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person schwer erkrankt war und genesen ist."
        ),
        q1_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person schwer erkrankt war und nicht genesen ist."
        ),
        q2_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "schwer erkrankte Person genesen ist."
        ),
        q2_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "schwer erkrankte Person nicht genesen ist."
        ),
        q3_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person leicht erkrankt und genesen oder mittelschwer erkrankt und genesen ist."
        ),
        q3_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person leicht erkrankt und nicht genesen oder mittelschwer erkrankt und nicht genesen ist."
        ),
        abs_stat_tmpl=(
            "Von insgesamt {n_fmt} behandelten Patientinnen und Patienten sind {p_d_pct}\u00a0% genesen; "
            "darunter waren {count_a_fmt} leicht Erkrankte und {count_c_fmt} schwer Erkrankte."
        ),
        label_a="L", label_b="M", label_c="S", label_d="G",
    ),
    # 4) Lern-Apps
    Template3Kat(
        intro="Im Rahmen einer schulweiten Befragung ging es um die Nutzung von Lern-Apps.",
        stage1_text="Die Befragten wurden in drei Gruppen eingeteilt: Starter-Nutzende (S), Pro-Nutzende (P) und Gelegenheits-Nutzende (G).",
        stage2_text="Als Nutzungszweck wird unterschieden zwischen Prüfungsvorbereitung (V) und Unterhaltung (U).",
        things="Befragten",
        cat_a="Starter-Nutzende (S)",
        cat_b="Pro-Nutzende (P)",
        cat_c="Gelegenheits-Nutzende (G)",
        out_d="zur Prüfungsvorbereitung (V)",
        out_nd="zur Unterhaltung (U)",
        chance_stat_tmpl=(
            "Starter-Nutzende verwenden die App in {p_d_a_pct}\u00a0% der Fälle zur Prüfungsvorbereitung, "
            "Pro-Nutzende in {p_d_b_pct}\u00a0% der Fälle."
        ),
        q1_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person zu den Gelegenheits-Nutzenden gehört und die App zur Prüfungsvorbereitung nutzt."
        ),
        q1_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person zu den Gelegenheits-Nutzenden gehört und die App zur Unterhaltung nutzt."
        ),
        q2_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person aus der Gruppe der Gelegenheits-Nutzenden die App zur Prüfungsvorbereitung nutzt."
        ),
        q2_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person aus der Gruppe der Gelegenheits-Nutzenden die App zur Unterhaltung nutzt."
        ),
        q3_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person eine Starter-Version oder eine Pro-Version zur Prüfungsvorbereitung nutzt."
        ),
        q3_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person eine Starter-Version oder eine Pro-Version zur Unterhaltung nutzt."
        ),
        abs_stat_tmpl=(
            "Von insgesamt {n_fmt} Befragten nutzen {p_d_pct}\u00a0% eine Lern-App zur Prüfungsvorbereitung; "
            "darunter waren {count_a_fmt} Starter-Nutzende und {count_c_fmt} Gelegenheits-Nutzende."
        ),
        label_a="S", label_b="P", label_c="G", label_d="V",
    ),
    # 5) Sport & Verletzungen
    Template3Kat(
        intro="Ein Sportverein hat die Verletzungsstatistik seiner Mitglieder ausgewertet.",
        stage1_text="Die Mitglieder wurden nach ihrer Hauptsportart eingeteilt: Laufende (L), Radfahrende (R) und Schwimmende (S).",
        stage2_text="Außerdem wurde erfasst, ob sich jemand verletzt hat: verletzt (V) oder unverletzt (U).",
        things="Sporttreibenden",
        cat_a="Laufende (L)",
        cat_b="Radfahrende (R)",
        cat_c="Schwimmende (S)",
        out_d="verletzt (V)",
        out_nd="unverletzt (U)",
        chance_stat_tmpl=(
            "Laufende verletzen sich in {p_d_a_pct}\u00a0% der Fälle und Radfahrende in {p_d_b_pct}\u00a0% der Fälle."
        ),
        q1_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Sportler schwimmt und sich verletzt hat."
        ),
        q1_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Sportler schwimmt und sich nicht verletzt hat."
        ),
        q2_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Schwimmender sich verletzt hat."
        ),
        q2_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Schwimmender sich nicht verletzt hat."
        ),
        q3_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Sportler läuft und sich verletzt hat oder Rad fährt und sich verletzt hat."
        ),
        q3_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Sportler läuft und sich nicht verletzt hat oder Rad fährt und sich nicht verletzt hat."
        ),
        abs_stat_tmpl=(
            "Von insgesamt {n_fmt} erfassten Sporttreibenden haben sich {p_d_pct}\u00a0% verletzt; "
            "darunter waren {count_a_fmt} Laufende und {count_c_fmt} Schwimmende."
        ),
        label_a="L", label_b="R", label_c="S", label_d="V",
    ),
    # 6) Streaming-Abos
    Template3Kat(
        intro="Ein Medienunternehmen hat das Nutzungsverhalten seiner Streamingkundschaft untersucht.",
        stage1_text="Die Konten wurden in Basis-Abo (B), Standard-Abo (S) und Premium-Abo (P) eingeteilt.",
        stage2_text="Erfasst wurde, ob Inhalte überwiegend mobil (M) oder am TV-Gerät (T) konsumiert werden.",
        things="Konten",
        cat_a="Basis-Abo (B)",
        cat_b="Standard-Abo (S)",
        cat_c="Premium-Abo (P)",
        out_d="mobil (M)",
        out_nd="am TV-Gerät (T)",
        chance_stat_tmpl=(
            "Beim Basis-Abo liegt der mobile Anteil bei {p_d_a_pct}\u00a0%, beim Standard-Abo bei {p_d_b_pct}\u00a0%."
        ),
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Konto ein Premium-Abo mit mobiler Nutzung ist.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Konto ein Premium-Abo mit TV-Nutzung ist.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Premium-Konto überwiegend mobil genutzt wird.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Premium-Konto überwiegend am TV genutzt wird.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Konto entweder Basis mit mobiler Nutzung oder Standard mit mobiler Nutzung ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Konto entweder Basis mit TV-Nutzung oder Standard mit TV-Nutzung ist.",
        abs_stat_tmpl=(
            "Von insgesamt {n_fmt} erfassten Konten nutzen {p_d_pct}\u00a0% den Dienst überwiegend mobil; darunter waren {count_a_fmt} Basis-Abos und {count_c_fmt} Premium-Abos."
        ),
        label_a="B", label_b="S", label_c="P", label_d="M",
    ),
    # 7) Bibliothek
    Template3Kat(
        intro="Eine Stadtbibliothek hat die Ausleihdaten des vergangenen Jahres ausgewertet.",
        stage1_text="Die Ausleihen wurden in Jugendmedien (J), Sachmedien (S) und Belletristik (B) eingeteilt.",
        stage2_text="Zusätzlich wurde erfasst, ob die Medien digital (D) oder physisch (P) ausgeliehen wurden.",
        things="Ausleihen",
        cat_a="Jugendmedien (J)",
        cat_b="Sachmedien (S)",
        cat_c="Belletristik (B)",
        out_d="digital (D)",
        out_nd="physisch (P)",
        chance_stat_tmpl="Bei Jugendmedien beträgt der Digitalanteil {p_d_a_pct}\u00a0%, bei Sachmedien {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Ausleihe Belletristik in digitaler Form betrifft.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Ausleihe Belletristik in physischer Form betrifft.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Belletristik-Ausleihe digital ist.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Belletristik-Ausleihe physisch ist.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Ausleihe entweder Jugendmedien digital oder Sachmedien digital ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Ausleihe entweder Jugendmedien physisch oder Sachmedien physisch ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} Ausleihen erfolgten {p_d_pct}\u00a0% digital; darunter waren {count_a_fmt} Jugendmedien und {count_c_fmt} Belletristik-Ausleihen.",
        label_a="J", label_b="S", label_c="B", label_d="D",
    ),
    # 8) Mobilität
    Template3Kat(
        intro="In einer Pendlerstudie wurde das Verkehrsverhalten in einer Region untersucht.",
        stage1_text="Die Wege wurden nach Distanz in kurz (K), mittel (M) und lang (L) eingeteilt.",
        stage2_text="Außerdem wurde erfasst, ob der Weg mit dem ÖPNV (O) oder mit dem Auto (A) zurückgelegt wurde.",
        things="Wege",
        cat_a="kurz (K)",
        cat_b="mittel (M)",
        cat_c="lang (L)",
        out_d="mit dem ÖPNV (O)",
        out_nd="mit dem Auto (A)",
        chance_stat_tmpl="Bei kurzen Wegen liegt der ÖPNV-Anteil bei {p_d_a_pct}\u00a0%, bei mittleren Wegen bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Weg lang ist und mit dem ÖPNV zurückgelegt wurde.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Weg lang ist und mit dem Auto zurückgelegt wurde.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter langer Weg mit dem ÖPNV erfolgt.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter langer Weg mit dem Auto erfolgt.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Weg entweder kurz mit ÖPNV oder mittel mit ÖPNV ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Weg entweder kurz mit Auto oder mittel mit Auto ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} ausgewerteten Wegen wurden {p_d_pct}\u00a0% mit dem ÖPNV zurückgelegt; darunter waren {count_a_fmt} kurze und {count_c_fmt} lange Wege.",
        label_a="K", label_b="M", label_c="L", label_d="O",
    ),
    # 9) Konzertpublikum
    Template3Kat(
        intro="Ein Festivalteam hat Daten zum Konzertpublikum erhoben.",
        stage1_text="Die Tickets wurden in Frühbuchung (F), Normalpreis (N) und Abendkasse (A) eingeteilt.",
        stage2_text="Zusätzlich wurde erfasst, ob Besucherinnen und Besucher früh (E) oder spät (S) auf das Gelände kamen.",
        things="Tickets",
        cat_a="Frühbuchung (F)",
        cat_b="Normalpreis (N)",
        cat_c="Abendkasse (A)",
        out_d="früh gekommen (E)",
        out_nd="spät gekommen (S)",
        chance_stat_tmpl="Bei Frühbuchungen liegt der Früh-Anteil bei {p_d_a_pct}\u00a0%, bei Normalpreis-Tickets bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Ticket zur Abendkasse gehört und die Person früh kommt.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Ticket zur Abendkasse gehört und die Person spät kommt.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Abendkassen-Ticket früh kommt.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Abendkassen-Ticket spät kommt.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Ticket entweder Frühbuchung mit frühem Kommen oder Normalpreis mit frühem Kommen ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Ticket entweder Frühbuchung mit spätem Kommen oder Normalpreis mit spätem Kommen ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} Tickets entfielen {p_d_pct}\u00a0% auf frühes Kommen; darunter waren {count_a_fmt} Frühbuchungen und {count_c_fmt} Abendkassen-Tickets.",
        label_a="F", label_b="N", label_c="A", label_d="E",
    ),
    # 10) Unternehmensschulungen
    Template3Kat(
        intro="Ein Unternehmen hat die Teilnahme an internen Schulungen analysiert.",
        stage1_text="Die Mitarbeitenden wurden nach Abteilung in Vertrieb (V), Technik (T) und Verwaltung (W) gruppiert.",
        stage2_text="Beim Ergebnis wurde unterschieden zwischen bestanden (B) und nicht bestanden (N).",
        things="Teilnahmen",
        cat_a="Vertrieb (V)",
        cat_b="Technik (T)",
        cat_c="Verwaltung (W)",
        out_d="bestanden (B)",
        out_nd="nicht bestanden (N)",
        chance_stat_tmpl="Im Vertrieb liegt die Bestehensquote bei {p_d_a_pct}\u00a0%, in der Technik bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme aus der Verwaltung stammt und bestanden wurde.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme aus der Verwaltung stammt und nicht bestanden wurde.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme aus der Verwaltung bestanden wurde.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme aus der Verwaltung nicht bestanden wurde.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme entweder im Vertrieb bestanden oder in der Technik bestanden wurde.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme entweder im Vertrieb nicht bestanden oder in der Technik nicht bestanden wurde.",
        abs_stat_tmpl="Von insgesamt {n_fmt} Schulungsteilnahmen wurden {p_d_pct}\u00a0% bestanden; darunter waren {count_a_fmt} Teilnahmen aus dem Vertrieb und {count_c_fmt} aus der Verwaltung.",
        label_a="V", label_b="T", label_c="W", label_d="B",
    ),
    # 11) Museum
    Template3Kat(
        intro="Ein Museum hat Besucherströme über mehrere Monate dokumentiert.",
        stage1_text="Die Besuche wurden nach Ticketart in regulär (R), ermäßigt (E) und Gruppe (G) eingeteilt.",
        stage2_text="Zusätzlich wurde erfasst, ob der Besuch mit Führung (F) oder ohne Führung (O) stattfand.",
        things="Besuche",
        cat_a="regulär (R)",
        cat_b="ermäßigt (E)",
        cat_c="Gruppe (G)",
        out_d="mit Führung (F)",
        out_nd="ohne Führung (O)",
        chance_stat_tmpl="Bei regulären Tickets liegt der Anteil mit Führung bei {p_d_a_pct}\u00a0%, bei ermäßigten Tickets bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Besuch ein Gruppenbesuch mit Führung ist.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Besuch ein Gruppenbesuch ohne Führung ist.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Gruppenbesuch mit Führung stattfindet.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Gruppenbesuch ohne Führung stattfindet.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Besuch entweder regulär mit Führung oder ermäßigt mit Führung ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Besuch entweder regulär ohne Führung oder ermäßigt ohne Führung ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} Besuchen fanden {p_d_pct}\u00a0% mit Führung statt; darunter waren {count_a_fmt} reguläre und {count_c_fmt} Gruppen-Besuche.",
        label_a="R", label_b="E", label_c="G", label_d="F",
    ),
    # 12) Wohnungsmarkt
    Template3Kat(
        intro="Für einen kommunalen Bericht wurden Mietanzeigen ausgewertet.",
        stage1_text="Die Wohnungen wurden nach Größe in klein (K), mittel (M) und groß (G) eingeteilt.",
        stage2_text="Als Merkmal wurde erfasst, ob ein Balkon (B) vorhanden ist oder nicht (N).",
        things="Wohnungen",
        cat_a="klein (K)",
        cat_b="mittel (M)",
        cat_c="groß (G)",
        out_d="Balkon (B)",
        out_nd="kein Balkon (N)",
        chance_stat_tmpl="Bei kleinen Wohnungen liegt der Balkonanteil bei {p_d_a_pct}\u00a0%, bei mittleren Wohnungen bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Wohnung groß ist und einen Balkon hat.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Wohnung groß ist und keinen Balkon hat.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte große Wohnung einen Balkon hat.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte große Wohnung keinen Balkon hat.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Wohnung entweder klein mit Balkon oder mittel mit Balkon ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Wohnung entweder klein ohne Balkon oder mittel ohne Balkon ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} ausgewerteten Wohnungen haben {p_d_pct}\u00a0% einen Balkon; darunter waren {count_a_fmt} kleine und {count_c_fmt} große Wohnungen.",
        label_a="K", label_b="M", label_c="G", label_d="B",
    ),
    # 13) Ehrenamt
    Template3Kat(
        intro="Ein Trägerverein hat das Engagement in seinen Projekten ausgewertet.",
        stage1_text="Die Einsätze wurden den Bereichen Nachhilfe (N), Umwelt (U) und Seniorenhilfe (S) zugeordnet.",
        stage2_text="Zusätzlich wurde erfasst, ob der Einsatz regelmäßig (R) oder unregelmäßig (Ue) erfolgt.",
        things="Einsätze",
        cat_a="Nachhilfe (N)",
        cat_b="Umwelt (U)",
        cat_c="Seniorenhilfe (S)",
        out_d="regelmäßig (R)",
        out_nd="unregelmäßig (Ue)",
        chance_stat_tmpl="Im Bereich Nachhilfe liegt der Anteil regelmäßiger Einsätze bei {p_d_a_pct}\u00a0%, im Umweltbereich bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einsatz in der Seniorenhilfe regelmäßig erfolgt.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einsatz in der Seniorenhilfe unregelmäßig erfolgt.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einsatz in der Seniorenhilfe regelmäßig ist.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einsatz in der Seniorenhilfe unregelmäßig ist.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einsatz entweder in der Nachhilfe regelmäßig oder im Umweltbereich regelmäßig erfolgt.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einsatz entweder in der Nachhilfe unregelmäßig oder im Umweltbereich unregelmäßig erfolgt.",
        abs_stat_tmpl="Von insgesamt {n_fmt} dokumentierten Einsätzen erfolgten {p_d_pct}\u00a0% regelmäßig; darunter waren {count_a_fmt} Einsätze in der Nachhilfe und {count_c_fmt} in der Seniorenhilfe.",
        label_a="N", label_b="U", label_c="S", label_d="R",
    ),
    # 14) Einzelhandel
    Template3Kat(
        intro="Eine Handelskette hat Retouren aus dem Online-Shop analysiert.",
        stage1_text="Die Bestellungen wurden in Kleidung (K), Elektronik (E) und Haushalt (H) eingeteilt.",
        stage2_text="Erfasst wurde, ob eine Bestellung retourniert (R) oder behalten (B) wurde.",
        things="Bestellungen",
        cat_a="Kleidung (K)",
        cat_b="Elektronik (E)",
        cat_c="Haushalt (H)",
        out_d="retourniert (R)",
        out_nd="behalten (B)",
        chance_stat_tmpl="Bei Kleidung liegt die Retourenquote bei {p_d_a_pct}\u00a0%, bei Elektronik bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Bestellung aus dem Haushalt stammt und retourniert wird.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Bestellung aus dem Haushalt stammt und behalten wird.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Haushaltsbestellung retourniert wird.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Haushaltsbestellung behalten wird.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Bestellung entweder Kleidung retourniert oder Elektronik retourniert ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Bestellung entweder Kleidung behalten oder Elektronik behalten wurde.",
        abs_stat_tmpl="Von insgesamt {n_fmt} Bestellungen wurden {p_d_pct}\u00a0% retourniert; darunter waren {count_a_fmt} Bestellungen aus Kleidung und {count_c_fmt} aus Haushalt.",
        label_a="K", label_b="E", label_c="H", label_d="R",
    ),
    # 15) Kulturkurse
    Template3Kat(
        intro="Eine Volkshochschule hat die Teilnahme an Kulturkursen ausgewertet.",
        stage1_text="Die Teilnahmen wurden in Musik (M), Theater (T) und Fotografie (F) eingeteilt.",
        stage2_text="Zusätzlich wurde erfasst, ob der Kurs online (O) oder in Präsenz (P) besucht wurde.",
        things="Teilnahmen",
        cat_a="Musik (M)",
        cat_b="Theater (T)",
        cat_c="Fotografie (F)",
        out_d="online (O)",
        out_nd="in Präsenz (P)",
        chance_stat_tmpl="Bei Musikkursen liegt der Online-Anteil bei {p_d_a_pct}\u00a0%, bei Theaterkursen bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme ein Fotokurs online ist.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme ein Fotokurs in Präsenz ist.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme im Fotokurs online stattfindet.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme im Fotokurs in Präsenz stattfindet.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme entweder Musik online oder Theater online ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme entweder Musik in Präsenz oder Theater in Präsenz ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} Kurs-Teilnahmen fanden {p_d_pct}\u00a0% online statt; darunter waren {count_a_fmt} Musik- und {count_c_fmt} Fotografie-Teilnahmen.",
        label_a="M", label_b="T", label_c="F", label_d="O",
    ),
    # 16) Tourismus
    Template3Kat(
        intro="Ein Tourismusverband hat Buchungsdaten aus der Ferienzeit analysiert.",
        stage1_text="Die Reisen wurden in Städtereise (S), Natururlaub (N) und Küstenurlaub (K) eingeteilt.",
        stage2_text="Erfasst wurde, ob die Buchung früh (F) oder kurzfristig (Kf) erfolgte.",
        things="Buchungen",
        cat_a="Städtereise (S)",
        cat_b="Natururlaub (N)",
        cat_c="Küstenurlaub (K)",
        out_d="früh gebucht (F)",
        out_nd="kurzfristig gebucht (Kf)",
        chance_stat_tmpl="Bei Städtereisen liegt der Anteil früher Buchungen bei {p_d_a_pct}\u00a0%, bei Natururlauben bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Buchung Küstenurlaub und frühe Buchung ist.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Buchung Küstenurlaub und kurzfristige Buchung ist.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Küstenreise früh gebucht wurde.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Küstenreise kurzfristig gebucht wurde.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Buchung entweder Städtereise früh oder Natururlaub früh ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Buchung entweder Städtereise kurzfristig oder Natururlaub kurzfristig ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} Buchungen waren {p_d_pct}\u00a0% frühe Buchungen; darunter waren {count_a_fmt} Städtereisen und {count_c_fmt} Küstenreisen.",
        label_a="S", label_b="N", label_c="K", label_d="F",
    ),
    # 17) Schule
    Template3Kat(
        intro="An einer Schule wurde die Bearbeitung von Hausaufgaben ausgewertet.",
        stage1_text="Die Klassen wurden in Unterstufe (U), Mittelstufe (M) und Oberstufe (O) eingeteilt.",
        stage2_text="Als Merkmal wurde erfasst, ob Aufgaben pünktlich (P) oder verspätet (V) abgegeben wurden.",
        things="Abgaben",
        cat_a="Unterstufe (U)",
        cat_b="Mittelstufe (M)",
        cat_c="Oberstufe (O)",
        out_d="pünktlich (P)",
        out_nd="verspätet (V)",
        chance_stat_tmpl="In der Unterstufe liegt die Pünktlichkeitsquote bei {p_d_a_pct}\u00a0%, in der Mittelstufe bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Abgabe aus der Oberstufe pünktlich ist.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Abgabe aus der Oberstufe verspätet ist.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Oberstufen-Abgabe pünktlich erfolgt.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Oberstufen-Abgabe verspätet erfolgt.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Abgabe entweder aus der Unterstufe pünktlich oder aus der Mittelstufe pünktlich ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Abgabe entweder aus der Unterstufe verspätet oder aus der Mittelstufe verspätet ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} Abgaben wurden {p_d_pct}\u00a0% pünktlich abgegeben; darunter waren {count_a_fmt} Abgaben aus der Unterstufe und {count_c_fmt} aus der Oberstufe.",
        label_a="U", label_b="M", label_c="O", label_d="P",
    ),
    # 18) Gesundheit
    Template3Kat(
        intro="Ein Gesundheitszentrum hat die Teilnahme an Präventionskursen ausgewertet.",
        stage1_text="Die Teilnehmenden wurden in die Altersgruppen jung (J), mittel (M) und älter (A) eingeteilt.",
        stage2_text="Zusätzlich wurde erfasst, ob der Kurs vollständig (V) oder nur teilweise (T) besucht wurde.",
        things="Teilnahmen",
        cat_a="jung (J)",
        cat_b="mittel (M)",
        cat_c="älter (A)",
        out_d="vollständig besucht (V)",
        out_nd="teilweise besucht (T)",
        chance_stat_tmpl="In der jungen Gruppe liegt die vollständige Teilnahme bei {p_d_a_pct}\u00a0%, in der mittleren Gruppe bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme aus der älteren Gruppe vollständig ist.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme aus der älteren Gruppe teilweise ist.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme aus der älteren Gruppe vollständig erfolgt.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme aus der älteren Gruppe teilweise erfolgt.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme entweder aus der jungen Gruppe vollständig oder aus der mittleren Gruppe vollständig ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Teilnahme entweder aus der jungen Gruppe teilweise oder aus der mittleren Gruppe teilweise ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} erfassten Teilnahmen wurden {p_d_pct}\u00a0% vollständig besucht; darunter waren {count_a_fmt} aus der jungen und {count_c_fmt} aus der älteren Gruppe.",
        label_a="J", label_b="M", label_c="A", label_d="V",
    ),
    # 19) Arbeitsmarkt
    Template3Kat(
        intro="Eine Arbeitsagentur hat Ergebnisse eines Weiterbildungsprogramms ausgewertet.",
        stage1_text="Die Teilnehmenden wurden nach Vorerfahrung in gering (G), mittel (M) und hoch (H) eingeteilt.",
        stage2_text="Beim Programmausgang wurde unterschieden zwischen direkter Vermittlung (D) und keiner direkten Vermittlung (K).",
        things="Teilnehmenden",
        cat_a="gering (G)",
        cat_b="mittel (M)",
        cat_c="hoch (H)",
        out_d="direkte Vermittlung (D)",
        out_nd="keine direkte Vermittlung (K)",
        chance_stat_tmpl="Bei geringer Vorerfahrung liegt die direkte Vermittlungsquote bei {p_d_a_pct}\u00a0%, bei mittlerer Vorerfahrung bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person mit hoher Vorerfahrung direkt vermittelt wird.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person mit hoher Vorerfahrung nicht direkt vermittelt wird.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person mit hoher Vorerfahrung direkt vermittelt wird.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person mit hoher Vorerfahrung nicht direkt vermittelt wird.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person entweder mit geringer Vorerfahrung direkt oder mit mittlerer Vorerfahrung direkt vermittelt wird.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person entweder mit geringer Vorerfahrung nicht direkt oder mit mittlerer Vorerfahrung nicht direkt vermittelt wird.",
        abs_stat_tmpl="Von insgesamt {n_fmt} Teilnehmenden wurden {p_d_pct}\u00a0% direkt vermittelt; darunter waren {count_a_fmt} mit geringer und {count_c_fmt} mit hoher Vorerfahrung.",
        label_a="G", label_b="M", label_c="H", label_d="D",
    ),
    # 20) Ernährung
    Template3Kat(
        intro="Eine Ernährungsstudie hat das Kaufverhalten in Supermärkten untersucht.",
        stage1_text="Die Einkäufe wurden in frisch (F), gemischt (G) und überwiegend fertig (V) eingeteilt.",
        stage2_text="Zusätzlich wurde erfasst, ob der Einkauf geplant (P) oder spontan (S) war.",
        things="Einkäufe",
        cat_a="frisch (F)",
        cat_b="gemischt (G)",
        cat_c="überwiegend fertig (V)",
        out_d="geplant (P)",
        out_nd="spontan (S)",
        chance_stat_tmpl="Bei frischen Einkäufen liegt der Anteil geplanter Einkäufe bei {p_d_a_pct}\u00a0%, bei gemischten Einkäufen bei {p_d_b_pct}\u00a0%.",
        q1_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einkauf überwiegend fertig und geplant ist.",
        q1_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einkauf überwiegend fertig und spontan ist.",
        q2_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter überwiegend fertiger Einkauf geplant ist.",
        q2_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter überwiegend fertiger Einkauf spontan ist.",
        q3_d="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einkauf entweder frisch geplant oder gemischt geplant ist.",
        q3_nd="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Einkauf entweder frisch spontan oder gemischt spontan ist.",
        abs_stat_tmpl="Von insgesamt {n_fmt} erfassten Einkäufen waren {p_d_pct}\u00a0% geplant; darunter waren {count_a_fmt} frische und {count_c_fmt} überwiegend fertige Einkäufe.",
        label_a="F", label_b="G", label_c="V", label_d="P",
    ),
]


# ---------------------------------------------------------------------------
# Parameter-Sampling
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Case3Kat:
    p_a: float
    p_b: float
    p_c: float
    p_d_a: float   # P(D|A)
    p_d_b: float   # P(D|B)
    p_d_c: float   # P(D|C) – berechnet aus den übrigen
    p_d: float     # P(D) gesamt


def _sample_case(rng: random.Random) -> Case3Kat | None:
    """
    Erzeugt einen Case3Kat mit hübschen Dezimalstellen.
    P(A) und P(C) werden als Vielfache von 0,05 gewählt,
    P(D|A), P(D|B) als Vielfache von 0,05,
    P(D) als Vielfaches von 0,05.
    Gibt None zurück, wenn P(D|C) nicht in (0,02 ; 0,98) liegt.
    """
    steps = list(range(1, 20))  # 0.05 … 0.95

    pa = Decimal(rng.choice(steps)) * Decimal("0.05")
    pc_max = int((Decimal("0.90") - pa) / Decimal("0.05"))
    if pc_max < 1:
        return None
    pc = Decimal(rng.randint(1, pc_max)) * Decimal("0.05")
    pb = Decimal("1") - pa - pc

    if pb <= Decimal("0.04"):
        return None

    p_d_a = Decimal(rng.choice(steps)) * Decimal("0.05")
    p_d_b = Decimal(rng.choice(steps)) * Decimal("0.05")

    # P(D) so wählen, dass P(D|C) = (P(D) − pa·p_d_a − pb·p_d_b) / pc ∈ (0.02, 0.98)
    # d.h. P(D) ∈ ( pa·p_d_a + pb·p_d_b + 0.02·pc , pa·p_d_a + pb·p_d_b + 0.98·pc )
    base = _r4(pa * p_d_a + pb * p_d_b)
    pd_low = _r2(base + Decimal("0.02") * pc) + Decimal("0.01")
    pd_high = _r2(base + Decimal("0.98") * pc) - Decimal("0.01")

    # Kandidaten für P(D) als Vielfache von 0,05 im zulässigen Bereich
    cands = [
        Decimal(i) * Decimal("0.05")
        for i in range(1, 20)
        if pd_low <= Decimal(i) * Decimal("0.05") <= pd_high
    ]
    if not cands:
        return None

    pd = Decimal(rng.choice(cands))
    p_d_c = _r4((pd - base) / pc)

    # Plausibilitätscheck
    if not (Decimal("0.01") < p_d_c < Decimal("0.99")):
        return None

    return Case3Kat(
        p_a=_f(pa),
        p_b=_f(pb),
        p_c=_f(pc),
        p_d_a=_f(p_d_a),
        p_d_b=_f(p_d_b),
        p_d_c=_f(p_d_c),
        p_d=_f(pd),
    )


def _sample_case_retry(rng: random.Random, max_tries: int = 100) -> Case3Kat:
    for _ in range(max_tries):
        c = _sample_case(rng)
        if c is not None:
            return c
    raise RuntimeError("Konnte keinen gültigen Case3Kat erzeugen.")


# ---------------------------------------------------------------------------
# Formatierungs-Helpers
# ---------------------------------------------------------------------------

def _fmt(v: float, decimals: int = 2) -> str:
    """Zahl mit Dezimalkomma."""
    return f"{v:.{decimals}f}".replace(".", ",")


def _pct(v: float) -> str:
    """Prozentzahl ohne Nachkommastellen, z. B. '45'."""
    return str(round(v * 100))


def _frac_text(v: float) -> str:
    """
    Versucht einen hübschen Bruchtext zu erzeugen (z. B. 'ein Fünftel',
    'die Hälfte', 'drei Viertel'). Fällt auf Prozentzahl zurück.
    """
    frac_map = {
        Fraction(1, 10): "einem Zehntel",
        Fraction(1, 5): "einem Fünftel",
        Fraction(3, 10): "drei Zehnteln",
        Fraction(2, 5): "zwei Fünfteln",
        Fraction(1, 2): "der Hälfte",
        Fraction(3, 5): "drei Fünfteln",
        Fraction(7, 10): "sieben Zehnteln",
        Fraction(4, 5): "vier Fünfteln",
        Fraction(9, 10): "neun Zehnteln",
        Fraction(1, 4): "einem Viertel",
        Fraction(3, 4): "drei Vierteln",
        Fraction(1, 3): "einem Drittel",
        Fraction(2, 3): "zwei Dritteln",
        Fraction(1, 20): "einem Zwanzigstel",
        Fraction(3, 20): "drei Zwanzigsteln",
        Fraction(7, 20): "sieben Zwanzigsteln",
        Fraction(9, 20): "neun Zwanzigsteln",
        Fraction(11, 20): "elf Zwanzigsteln",
        Fraction(13, 20): "dreizehn Zwanzigsteln",
        Fraction(1, 8): "einem Achtel",
        Fraction(3, 8): "drei Achteln",
        Fraction(5, 8): "fünf Achteln",
        Fraction(7, 8): "sieben Achteln",
    }
    frac = Fraction(v).limit_denominator(20)
    return frac_map.get(frac, f"{_pct(v)}\u00a0%")


def _intro_text(tmpl: Template3Kat, case: Case3Kat, total_n: int) -> str:
    """
    Baut den vollständigen Einleitungstext nach dem 6-Satz-Schema:
      1. Beschreibung  2. Stufe-1-Ausprägungen  3. Stufe-2-Ausprägungen
      4. Bedingte W'keiten für A und B  5. Absolut-Statistik  6. Hinweis
    Ganzzahlen werden über Integer-Arithmetik berechnet, um Rundungsdifferenzen
    zu vermeiden (total_n Vielfaches von 100, p_a/p_c Vielfache von 5 %).
    """
    hint = "Für die folgenden Fragen ist es sinnvoll, das Baumdiagramm zuerst vollständig auszufüllen."

    p_d_a_pct = _pct(case.p_d_a)
    p_d_b_pct = _pct(case.p_d_b)
    p_d_pct = _pct(case.p_d)

    pa_int = round(case.p_a * 100)
    pc_int = round(case.p_c * 100)
    count_a = (total_n * pa_int) // 100
    count_c = (total_n * pc_int) // 100

    chance_stat = tmpl.chance_stat_tmpl.format(
        p_d_a_pct=p_d_a_pct,
        p_d_b_pct=p_d_b_pct,
    )
    abs_stat = tmpl.abs_stat_tmpl.format(
        n_fmt=_fmt_int(total_n),
        p_d_pct=p_d_pct,
        count_a_fmt=_fmt_int(count_a),
        count_c_fmt=_fmt_int(count_c),
    )

    return (
        f"{tmpl.intro} "
        f"{tmpl.stage1_text} "
        f"{tmpl.stage2_text} "
        f"{chance_stat} "
        f"{abs_stat} "
        f"{hint}"
    )


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class MethodenBaumdiagrammKomplex3KatGenerator(TaskGenerator):
    generator_key = "stochastik.mehrstufige_zufallsexperimente.baumdiagramm_komplex_3kat"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        _nice_totals = [2000, 4000, 5000, 8000, 10000, 20000, 40000, 50000, 80000, 100000]

        for index in range(count):
            tmpl = TEMPLATES[index % len(TEMPLATES)]
            case = _sample_case_retry(rng)
            total_n = rng.choice(_nice_totals)

            da = Decimal(str(case.p_d_a))
            db = Decimal(str(case.p_d_b))
            dc = Decimal(str(case.p_d_c))
            pa = Decimal(str(case.p_a))
            pb = Decimal(str(case.p_b))
            pc = Decimal(str(case.p_c))

            # Q1: P(C ∩ D) und P(C ∩ D̄)
            p_c_and_d  = _f(_r4(pc * dc))
            p_c_and_nd = _f(_r4(pc * (Decimal("1") - dc)))

            # Q2: P(D|C) und P(D̄|C)
            p_d_given_c  = case.p_d_c
            p_nd_given_c = _f(_r4(Decimal("1") - dc))

            # Q3: P(A∩D)+P(B∩D) und P(A∩D̄)+P(B∩D̄)
            p_ab_and_d  = _f(_r4(pa * da + pb * db))
            p_ab_and_nd = _f(_r4(pa * (Decimal("1") - da) + pb * (Decimal("1") - db)))

            # Zufällige Ausgang-Wahl pro Frage (D oder D̄)
            q1_use_d = rng.choice([True, False])
            q2_use_d = rng.choice([True, False])
            q3_use_d = rng.choice([True, False])

            intro = _intro_text(tmpl, case, total_n)

            fragen = [
                tmpl.q1_d if q1_use_d else tmpl.q1_nd,
                tmpl.q2_d if q2_use_d else tmpl.q2_nd,
                tmpl.q3_d if q3_use_d else tmpl.q3_nd,
            ]

            antworten = [
                numerical(p_c_and_d  if q1_use_d else p_c_and_nd,  tolerance=0.001, decimals=4),
                numerical(p_d_given_c if q2_use_d else p_nd_given_c, tolerance=0.001, decimals=4),
                numerical(p_ab_and_d  if q3_use_d else p_ab_and_nd,  tolerance=0.001, decimals=4),
            ]

            tasks.append(Task(
                einleitung=intro,
                fragen=fragen,
                antworten=antworten,
            ))

        return tasks
