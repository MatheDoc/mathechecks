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
        intro="In einem großen Elektronikfachmarkt wurden die Verkäufe von Laptops über mehrere Monate erfasst.",
        stage1_text="Die Laptops wurden nach ihrer Preisklasse in Einsteigergeräte (E), Mittelklassegeräte (M) und Premiumgeräte (P) eingeteilt.",
        stage2_text="Als Merkmal wurde das Betriebssystem erfasst: Windows (W) oder macOS (m).",
        things="Laptops",
        cat_a="Einsteigergeräte (E)",
        cat_b="Mittelklassegeräte (M)",
        cat_c="Premiumgeräte (P)",
        out_d="Windows (W)",
        out_nd="macOS (m)",
        chance_stat_tmpl=(
            "Einsteigergeräte verzeichneten den Ausgang \u201eWindows (W)\u201c zu {p_d_a_pct}\u00a0% "
            "und Mittelklassegeräte zu {p_d_b_pct}\u00a0%."
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
            "Premiumlaptop Windows ist."
        ),
        q2_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Premiumlaptop macOS ist."
        ),
        q3_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Laptop ein Einsteigergerät mit Windows oder ein Mittelklassegerät mit Windows ist."
        ),
        q3_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter "
            "Laptop ein Einsteigergerät mit macOS oder ein Mittelklassegerät mit macOS ist."
        ),
        abs_stat_tmpl=(
            "Von den insgesamt {n_fmt} erfassten Laptops waren {p_d_pct}\u00a0% "
            "mit Windows ausgestattet, es wurden {count_a_fmt} Einsteigerger\u00e4te "
            "und {count_c_fmt} Premiumger\u00e4te verkauft."
        ),
        label_a="E", label_b="M", label_c="P", label_d="W",
    ),
    # 2) Studierende & Prüfung
    Template3Kat(
        intro="An einer Hochschule wurden die Ergebnisse einer Abschlussprüfung ausgewertet.",
        stage1_text="Die Studierenden wurden nach ihrem Studienfortschritt in drei Gruppen eingeteilt: Erstsemester (E), Mittelsemester (M) und Abschlussstudierende (A).",
        stage2_text="Das Prüfungsergebnis wurde in bestanden (B) und nicht bestanden (N) unterschieden.",
        things="Prüfungsteilnehmenden",
        cat_a="Erstsemester (E)",
        cat_b="Mittelsemester (M)",
        cat_c="Abschlussstudierende (A)",
        out_d="bestanden (B)",
        out_nd="nicht bestanden (N)",
        chance_stat_tmpl=(
            "Erstsemester haben die Prüfung zu {p_d_a_pct}\u00a0% bestanden "
            "und Mittelsemester zu {p_d_b_pct}\u00a0%."
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
            "Von den insgesamt {n_fmt} Pr\u00fcfungsteilnehmenden haben {p_d_pct}\u00a0% "
            "die Pr\u00fcfung bestanden; darunter waren {count_a_fmt} Erstsemester "
            "und {count_c_fmt} Abschlussstudierende."
        ),
        label_a="E", label_b="M", label_c="A", label_d="B",
    ),
    # 3) Patienten & Genesung
    Template3Kat(
        intro="In einer Klinik wurde der Genesungsverlauf von Patientinnen und Patienten nach einer Standardbehandlung dokumentiert.",
        stage1_text="Die Patientinnen und Patienten wurden nach dem Erkrankungsschweregrad eingeteilt: Leicht Erkrankte (L), Mittelschwer Erkrankte (M) und Schwer Erkrankte (S).",
        stage2_text="Der Genesungsverlauf wurde als genesen (G) oder nicht genesen (N) dokumentiert.",
        things="Patientinnen und Patienten",
        cat_a="Leicht Erkrankte (L)",
        cat_b="Mittelschwer Erkrankte (M)",
        cat_c="Schwer Erkrankte (S)",
        out_d="genesen (G)",
        out_nd="nicht genesen (N)",
        chance_stat_tmpl=(
            "Leicht Erkrankte sind zu {p_d_a_pct}\u00a0% genesen "
            "und Mittelschwer Erkrankte zu {p_d_b_pct}\u00a0%."
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
            "Von den insgesamt {n_fmt} behandelten Patientinnen und Patienten "
            "sind {p_d_pct}\u00a0% genesen; darunter befanden sich {count_a_fmt} "
            "Leicht Erkrankte und {count_c_fmt} Schwer Erkrankte."
        ),
        label_a="L", label_b="M", label_c="S", label_d="G",
    ),
    # 4) Lern-Apps
    Template3Kat(
        intro="Im Rahmen einer schulweiten Befragung wurden Schülerinnen und Schüler zu ihrer Nutzung von Lern-Apps befragt.",
        stage1_text="Die Befragten wurden nach ihrer App-Nutzung eingeteilt: Starter-Nutzende (S), Pro-Nutzende (P) und Nicht-Nutzende (k).",
        stage2_text="Als Nutzungszweck wurde unterschieden zwischen Prüfungsvorbereitung (V) und Unterhaltung (U).",
        things="Befragten",
        cat_a="Starter-Nutzende (S)",
        cat_b="Pro-Nutzende (P)",
        cat_c="Nicht-Nutzende (k)",
        out_d="zur Prüfungsvorbereitung (V)",
        out_nd="zur Unterhaltung (U)",
        chance_stat_tmpl=(
            "Starter-Nutzende verwenden die App zu {p_d_a_pct}\u00a0% zur Prüfungsvorbereitung "
            "und Pro-Nutzende zu {p_d_b_pct}\u00a0%."
        ),
        q1_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person keine Lern-App nutzt und diese zur Prüfungsvorbereitung einsetzen würde."
        ),
        q1_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person keine Lern-App nutzt und diese zur Unterhaltung einsetzen würde."
        ),
        q2_d=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person ohne Lern-App diese zur Prüfungsvorbereitung einsetzen würde."
        ),
        q2_nd=(
            "Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte "
            "Person ohne Lern-App diese zur Unterhaltung einsetzen würde."
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
            "Von den insgesamt {n_fmt} Befragten nutzen {p_d_pct}\u00a0% "
            "eine Lern-App zur Pr\u00fcfungsvorbereitung; darunter waren {count_a_fmt} "
            "Starter-Nutzende und {count_c_fmt} Nicht-Nutzende."
        ),
        label_a="S", label_b="P", label_c="k", label_d="V",
    ),
    # 5) Sport & Verletzungen
    Template3Kat(
        intro="Ein Sportverein hat die Verletzungsstatistik seiner Mitglieder ausgewertet.",
        stage1_text="Die Mitglieder wurden nach ihrer Hauptsportart eingeteilt: Laufende (L), Radfahrende (R) und Schwimmende (S).",
        stage2_text="Als Merkmal wurde erfasst, ob sich ein Mitglied verletzt hat: verletzt (V) oder unverletzt (U).",
        things="Sporttreibenden",
        cat_a="Laufende (L)",
        cat_b="Radfahrende (R)",
        cat_c="Schwimmende (S)",
        out_d="verletzt (V)",
        out_nd="unverletzt (U)",
        chance_stat_tmpl=(
            "Laufende verletzten sich zu {p_d_a_pct}\u00a0% und Radfahrende zu {p_d_b_pct}\u00a0%."
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
            "Von den insgesamt {n_fmt} erfassten Sporttreibenden haben sich {p_d_pct}\u00a0% "
            "verletzt; darunter waren {count_a_fmt} Laufende und {count_c_fmt} Schwimmende."
        ),
        label_a="L", label_b="R", label_c="S", label_d="V",
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
    hint = "Für die folgenden Fragen ist ein vollständig ausgefülltes Baumdiagramm hilfreich."

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
    generator_key = "stochastik.methoden.baumdiagramm_komplex_3kat"

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
