"""Komplexe Baumdiagramme aus einem Sachtext aufstellen und auswerten.

Jede Aufgabe hat denselben Aufbau (questionOrder: fixed):
  1. Baumwahl A–D (MC, Visual ``tree-choice``; falsche Bäume nur strukturell falsch)
  2. Sicherheitsfrage: Wohin gehört eine Angabe (Pfadende oder Summe)? (MC)
  3. Anteil auf einer Stufe (Kante, nicht gegeben, bevorzugt rückwärts berechnet)
  4. Pfadwahrscheinlichkeit (Pfadende, nicht gegeben)
  5. Summe mehrerer Pfadwahrscheinlichkeiten (Ereignis, nicht gegeben)

Schwierigkeitsprofil, vom Löser geprüft:
  - Angaben genau so viele wie Freiheitsgrade, Baum schrittweise vollständig lösbar
  - mindestens ein Rückwärtsschritt (Division)
  - mindestens eine absolute Häufigkeit, eine Prozentangabe und eine Angabe
    als Pfadende oder Summe
  - möglichst ein Bruchanteil („Ein Fünftel …“, „Jeder Zweite …“)

Keine Notation für bedingte Wahrscheinlichkeiten: Werte auf Stufe 2 und 3 nur
in Worten („Welcher Anteil der … ?“).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from fractions import Fraction

from aufgaben.core.models import Task
from aufgaben.core.placeholders import mc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator
from aufgaben.generators.stochastik.mehrstufige_zufallsexperimente._baum_kern import (
    Angabe,
    Baum,
    Pfad,
    hat_hoechstens_dezimalen,
    loese,
    mutationen,
    wahre_werte,
)

_NBSP = " "
_VERBOTENE_LABELS = {"P", "E", "I", "O", "L"}

# (Text, Numerus des Verbs, nur bei Personen)
_BRUCH_TEXT: dict[Fraction, list[tuple[str, str, bool]]] = {
    Fraction(1, 2): [("Die Hälfte", "sg", False), ("Jeder Zweite", "sg", True)],
    Fraction(1, 4): [("Ein Viertel", "sg", False), ("Jeder Vierte", "sg", True)],
    Fraction(3, 4): [("Drei Viertel", "pl", False)],
    Fraction(1, 5): [("Ein Fünftel", "sg", False), ("Jeder Fünfte", "sg", True)],
    Fraction(2, 5): [("Zwei Fünftel", "pl", False)],
    Fraction(3, 5): [("Drei Fünftel", "pl", False)],
    Fraction(4, 5): [("Vier Fünftel", "pl", False)],
    Fraction(1, 10): [("Ein Zehntel", "sg", False), ("Jeder Zehnte", "sg", True)],
}


# ---------------------------------------------------------------------------
# Szenarien
# ---------------------------------------------------------------------------

def _p(text: str) -> Pfad:
    return tuple(text.split("/")) if text else ()


@dataclass(frozen=True)
class Ereignis:
    pl: str                 # „kommen zu spät“
    sg: str                 # „kommt zu spät“
    blaetter: tuple[str, ...]  # Pfade in Kurzform, z. B. ("B/V", "F/V")


@dataclass
class Szenario:
    key: str
    form: str
    baum: str
    intro: str
    gesamt: str             # mit {N}
    alle_gen: str           # „aller Befragten“
    der_alle: str           # „der Befragten“
    gruppe_gen: dict[str, str]   # innerer Knoten -> Genitiv der Gruppe („der Busfahrer“)
    pl: dict[str, str]      # Knoten -> Prädikat Plural („kommen zu spät“)
    sg: dict[str, str]      # Knoten -> Prädikat Singular
    ereignisse: list[Ereignis]
    n_werte: list[int]
    pfad_pl: dict[str, str] = field(default_factory=dict)
    pfad_sg: dict[str, str] = field(default_factory=dict)
    bereiche: dict[str, tuple[float, float]] = field(default_factory=dict)
    mutationen: tuple[str, ...] = ("fortsetzen", "kappen", "angleichen", "tauschen", "weglassen")
    personen: bool = False  # erlaubt „Jeder Fünfte …“


SZENARIEN: list[Szenario] = [
    # ---- T2: 3 x 2 --------------------------------------------------------
    Szenario(
        key="sportverein", personen=True, form="T2", baum="K(W F) J(W F) A(W F)",
        intro=(
            "Ein Sportverein hat seine Mitglieder ausgewertet. Sie sind Kinder (K), "
            "Jugendliche (J) oder Erwachsene (A). Außerdem wurde erfasst, ob ein Mitglied "
            "an Wettkämpfen teilnimmt (W) oder nur in der Freizeit trainiert (F)."
        ),
        gesamt="Der Verein hat {N} Mitglieder.",
        alle_gen="aller Mitglieder", der_alle="der Mitglieder",
        gruppe_gen={"": "der Mitglieder", "K": "der Kinder", "J": "der Jugendlichen", "A": "der Erwachsenen"},
        pl={"K": "sind Kinder", "J": "sind Jugendliche", "A": "sind Erwachsene",
            "K/W": "nehmen an Wettkämpfen teil", "K/F": "trainieren nur in der Freizeit",
            "J/W": "nehmen an Wettkämpfen teil", "J/F": "trainieren nur in der Freizeit",
            "A/W": "nehmen an Wettkämpfen teil", "A/F": "trainieren nur in der Freizeit"},
        sg={"K": "ist ein Kind", "J": "ist jugendlich", "A": "ist erwachsen",
            "K/W": "nimmt an Wettkämpfen teil", "K/F": "trainiert nur in der Freizeit",
            "J/W": "nimmt an Wettkämpfen teil", "J/F": "trainiert nur in der Freizeit",
            "A/W": "nimmt an Wettkämpfen teil", "A/F": "trainiert nur in der Freizeit"},
        pfad_pl={"K/W": "sind Kinder und nehmen an Wettkämpfen teil",
                 "K/F": "sind Kinder und trainieren nur in der Freizeit",
                 "J/W": "sind Jugendliche und nehmen an Wettkämpfen teil",
                 "J/F": "sind Jugendliche und trainieren nur in der Freizeit",
                 "A/W": "sind Erwachsene und nehmen an Wettkämpfen teil",
                 "A/F": "sind Erwachsene und trainieren nur in der Freizeit"},
        pfad_sg={"K/W": "ist ein Kind und nimmt an Wettkämpfen teil",
                 "K/F": "ist ein Kind und trainiert nur in der Freizeit",
                 "J/W": "ist jugendlich und nimmt an Wettkämpfen teil",
                 "J/F": "ist jugendlich und trainiert nur in der Freizeit",
                 "A/W": "ist erwachsen und nimmt an Wettkämpfen teil",
                 "A/F": "ist erwachsen und trainiert nur in der Freizeit"},
        ereignisse=[
            Ereignis("nehmen an Wettkämpfen teil", "nimmt an Wettkämpfen teil", ("K/W", "J/W", "A/W")),
            Ereignis("trainieren nur in der Freizeit", "trainiert nur in der Freizeit", ("K/F", "J/F", "A/F")),
            Ereignis("sind minderjährig und nehmen an Wettkämpfen teil",
                     "ist minderjährig und nimmt an Wettkämpfen teil", ("K/W", "J/W")),
        ],
        n_werte=[400, 500, 800, 1000, 1200, 1600, 2000],
        bereiche={"K": (0.2, 0.5), "J": (0.15, 0.4), "A": (0.2, 0.5)},
    ),
    Szenario(
        key="onlineshop", form="T2", baum="R(Z B) K(Z B) S(Z B)",
        intro=(
            "Ein Onlineshop hat seine Bestellungen ausgewertet. Bezahlt wurde per Rechnung (R), "
            "per Kreditkarte (K) oder per Sofortüberweisung (S). Außerdem wurde erfasst, ob die "
            "Ware zurückgeschickt (Z) oder behalten (B) wurde."
        ),
        gesamt="Ausgewertet wurden {N} Bestellungen.",
        alle_gen="aller Bestellungen", der_alle="der Bestellungen",
        gruppe_gen={"": "der Bestellungen", "R": "der Bestellungen auf Rechnung",
                    "K": "der Bestellungen mit Kreditkarte", "S": "der Bestellungen mit Sofortüberweisung"},
        pl={"R": "werden per Rechnung bezahlt", "K": "werden per Kreditkarte bezahlt",
            "S": "werden per Sofortüberweisung bezahlt",
            "R/Z": "werden zurückgeschickt", "R/B": "werden behalten",
            "K/Z": "werden zurückgeschickt", "K/B": "werden behalten",
            "S/Z": "werden zurückgeschickt", "S/B": "werden behalten"},
        sg={"R": "wird per Rechnung bezahlt", "K": "wird per Kreditkarte bezahlt",
            "S": "wird per Sofortüberweisung bezahlt",
            "R/Z": "wird zurückgeschickt", "R/B": "wird behalten",
            "K/Z": "wird zurückgeschickt", "K/B": "wird behalten",
            "S/Z": "wird zurückgeschickt", "S/B": "wird behalten"},
        pfad_pl={"R/Z": "werden per Rechnung bezahlt und zurückgeschickt",
                 "R/B": "werden per Rechnung bezahlt und behalten",
                 "K/Z": "werden per Kreditkarte bezahlt und zurückgeschickt",
                 "K/B": "werden per Kreditkarte bezahlt und behalten",
                 "S/Z": "werden per Sofortüberweisung bezahlt und zurückgeschickt",
                 "S/B": "werden per Sofortüberweisung bezahlt und behalten"},
        pfad_sg={"R/Z": "wird per Rechnung bezahlt und zurückgeschickt",
                 "R/B": "wird per Rechnung bezahlt und behalten",
                 "K/Z": "wird per Kreditkarte bezahlt und zurückgeschickt",
                 "K/B": "wird per Kreditkarte bezahlt und behalten",
                 "S/Z": "wird per Sofortüberweisung bezahlt und zurückgeschickt",
                 "S/B": "wird per Sofortüberweisung bezahlt und behalten"},
        ereignisse=[
            Ereignis("werden zurückgeschickt", "wird zurückgeschickt", ("R/Z", "K/Z", "S/Z")),
            Ereignis("werden behalten", "wird behalten", ("R/B", "K/B", "S/B")),
            Ereignis("werden nicht per Rechnung bezahlt und zurückgeschickt",
                     "wird nicht per Rechnung bezahlt und zurückgeschickt", ("K/Z", "S/Z")),
        ],
        n_werte=[400, 500, 800, 1000, 2000, 4000, 5000],
        bereiche={"R/Z": (0.1, 0.5), "K/Z": (0.1, 0.4), "S/Z": (0.1, 0.4)},
    ),
    # ---- T4: ein Ast endet sofort ------------------------------------------
    Szenario(
        key="lernapp", personen=True, form="T4", baum="G(U V) B(U V) K",
        intro=(
            "An einer Schule wurde gefragt, wie Lern-Apps genutzt werden. Die Befragten nutzen "
            "eine kostenlose Version (G), eine Bezahlversion (B) oder keine Lern-App (K). Wer eine "
            "App nutzt, wurde zusätzlich gefragt, ob er sie vor allem zur Unterhaltung (U) oder zur "
            "Prüfungsvorbereitung (V) nutzt."
        ),
        gesamt="Befragt wurden {N} Schülerinnen und Schüler.",
        alle_gen="aller Befragten", der_alle="der Befragten",
        gruppe_gen={"": "der Befragten", "G": "der Nutzer der kostenlosen Version",
                    "B": "der Nutzer der Bezahlversion"},
        pl={"G": "nutzen die kostenlose Version", "B": "nutzen die Bezahlversion",
            "K": "nutzen keine Lern-App",
            "G/U": "nutzen sie vor allem zur Unterhaltung", "G/V": "nutzen sie vor allem zur Prüfungsvorbereitung",
            "B/U": "nutzen sie vor allem zur Unterhaltung", "B/V": "nutzen sie vor allem zur Prüfungsvorbereitung"},
        sg={"G": "nutzt die kostenlose Version", "B": "nutzt die Bezahlversion",
            "K": "nutzt keine Lern-App",
            "G/U": "nutzt sie vor allem zur Unterhaltung", "G/V": "nutzt sie vor allem zur Prüfungsvorbereitung",
            "B/U": "nutzt sie vor allem zur Unterhaltung", "B/V": "nutzt sie vor allem zur Prüfungsvorbereitung"},
        pfad_pl={"G/U": "nutzen die kostenlose Version vor allem zur Unterhaltung",
                 "G/V": "nutzen die kostenlose Version vor allem zur Prüfungsvorbereitung",
                 "B/U": "nutzen die Bezahlversion vor allem zur Unterhaltung",
                 "B/V": "nutzen die Bezahlversion vor allem zur Prüfungsvorbereitung"},
        pfad_sg={"G/U": "nutzt die kostenlose Version vor allem zur Unterhaltung",
                 "G/V": "nutzt die kostenlose Version vor allem zur Prüfungsvorbereitung",
                 "B/U": "nutzt die Bezahlversion vor allem zur Unterhaltung",
                 "B/V": "nutzt die Bezahlversion vor allem zur Prüfungsvorbereitung"},
        ereignisse=[
            Ereignis("nutzen eine Lern-App vor allem zur Unterhaltung",
                     "nutzt eine Lern-App vor allem zur Unterhaltung", ("G/U", "B/U")),
            Ereignis("nutzen eine Lern-App vor allem zur Prüfungsvorbereitung",
                     "nutzt eine Lern-App vor allem zur Prüfungsvorbereitung", ("G/V", "B/V")),
        ],
        n_werte=[400, 500, 800, 1000, 1200, 2000],
        bereiche={"G": (0.3, 0.6), "B": (0.15, 0.35), "K": (0.1, 0.35)},
    ),
    Szenario(
        key="bibliothek", form="T4", baum="B(R V) M(R V) N",
        intro=(
            "Eine Stadtbibliothek hat ihre Besuche ausgewertet. Bei einem Besuch werden Bücher (B) "
            "oder andere Medien wie Filme und Spiele (M) ausgeliehen, oder es wird nichts (N) "
            "ausgeliehen. Wer etwas ausleiht, gibt es rechtzeitig (R) oder verspätet (V) zurück."
        ),
        gesamt="Ausgewertet wurden {N} Besuche.",
        alle_gen="aller Besuche", der_alle="der Besuche",
        gruppe_gen={"": "der Besuche", "B": "der Buchausleihen", "M": "der Ausleihen anderer Medien"},
        pl={"B": "sind Buchausleihen", "M": "sind Ausleihen anderer Medien",
            "N": "sind Besuche ohne Ausleihe",
            "B/R": "werden rechtzeitig zurückgegeben", "B/V": "werden verspätet zurückgegeben",
            "M/R": "werden rechtzeitig zurückgegeben", "M/V": "werden verspätet zurückgegeben"},
        sg={"B": "ist eine Buchausleihe", "M": "ist eine Ausleihe anderer Medien",
            "N": "ist ein Besuch ohne Ausleihe",
            "B/R": "wird rechtzeitig zurückgegeben", "B/V": "wird verspätet zurückgegeben",
            "M/R": "wird rechtzeitig zurückgegeben", "M/V": "wird verspätet zurückgegeben"},
        pfad_pl={"B/R": "sind rechtzeitig zurückgegebene Buchausleihen",
                 "B/V": "sind verspätet zurückgegebene Buchausleihen",
                 "M/R": "sind rechtzeitig zurückgegebene Ausleihen anderer Medien",
                 "M/V": "sind verspätet zurückgegebene Ausleihen anderer Medien"},
        pfad_sg={"B/R": "ist eine rechtzeitig zurückgegebene Buchausleihe",
                 "B/V": "ist eine verspätet zurückgegebene Buchausleihe",
                 "M/R": "ist eine rechtzeitig zurückgegebene Ausleihe anderer Medien",
                 "M/V": "ist eine verspätet zurückgegebene Ausleihe anderer Medien"},
        ereignisse=[
            Ereignis("sind verspätet zurückgegebene Ausleihen",
                     "ist eine verspätet zurückgegebene Ausleihe", ("B/V", "M/V")),
            Ereignis("sind rechtzeitig zurückgegebene Ausleihen",
                     "ist eine rechtzeitig zurückgegebene Ausleihe", ("B/R", "M/R")),
        ],
        n_werte=[400, 500, 800, 1000, 2000, 4000],
        bereiche={"B": (0.3, 0.6), "M": (0.15, 0.4), "N": (0.1, 0.35), "B/V": (0.1, 0.4), "M/V": (0.1, 0.5)},
    ),
    # ---- T6: unterschiedliche zweite Stufe ----------------------------------
    Szenario(
        key="reise", form="T6", baum="F(R V A) B(R V)",
        intro=(
            "Ein Reisebüro hat die Rückmeldungen seiner Kunden ausgewertet. Gereist wurde mit dem "
            "Flugzeug (F) oder mit der Bahn (B). Bei Bahnreisen wurde erfasst, ob die Fahrt "
            "pünktlich (R) oder verspätet (V) war. Bei Flugreisen war der Flug pünktlich (R), "
            "verspätet (V) oder er ist ausgefallen (A)."
        ),
        gesamt="Ausgewertet wurden {N} Reisen.",
        alle_gen="aller Reisen", der_alle="der Reisen",
        gruppe_gen={"": "der Reisen", "F": "der Flugreisen", "B": "der Bahnreisen"},
        pl={"F": "sind Flugreisen", "B": "sind Bahnreisen",
            "F/R": "sind pünktlich", "F/V": "sind verspätet", "F/A": "fallen aus",
            "B/R": "sind pünktlich", "B/V": "sind verspätet"},
        sg={"F": "ist eine Flugreise", "B": "ist eine Bahnreise",
            "F/R": "ist pünktlich", "F/V": "ist verspätet", "F/A": "fällt aus",
            "B/R": "ist pünktlich", "B/V": "ist verspätet"},
        pfad_pl={"F/R": "sind pünktliche Flugreisen", "F/V": "sind verspätete Flugreisen",
                 "F/A": "sind ausgefallene Flugreisen",
                 "B/R": "sind pünktliche Bahnreisen", "B/V": "sind verspätete Bahnreisen"},
        pfad_sg={"F/R": "ist eine pünktliche Flugreise", "F/V": "ist eine verspätete Flugreise",
                 "F/A": "ist eine ausgefallene Flugreise",
                 "B/R": "ist eine pünktliche Bahnreise", "B/V": "ist eine verspätete Bahnreise"},
        ereignisse=[
            Ereignis("sind verspätet", "ist verspätet", ("F/V", "B/V")),
            Ereignis("sind pünktlich", "ist pünktlich", ("F/R", "B/R")),
            Ereignis("sind nicht pünktlich", "ist nicht pünktlich", ("F/V", "F/A", "B/V")),
        ],
        n_werte=[400, 500, 800, 1000, 2000, 4000],
        bereiche={"F": (0.3, 0.7), "F/A": (0.05, 0.15), "F/R": (0.5, 0.8), "B/R": (0.4, 0.8)},
        mutationen=("angleichen", "tauschen", "weglassen", "kappen"),
    ),
    Szenario(
        key="hotel", form="T6", baum="Z(F N) D(F H N)",
        intro=(
            "Ein Hotel hat seine Buchungen ausgewertet. Gebucht wurde ein Einzelzimmer (Z) oder ein "
            "Doppelzimmer (D). Einzelzimmer gibt es mit Frühstück (F) oder ohne Verpflegung (N). "
            "Doppelzimmer gibt es mit Frühstück (F), mit Halbpension (H) oder ohne Verpflegung (N)."
        ),
        gesamt="Ausgewertet wurden {N} Buchungen.",
        alle_gen="aller Buchungen", der_alle="der Buchungen",
        gruppe_gen={"": "der Buchungen", "Z": "der Einzelzimmerbuchungen", "D": "der Doppelzimmerbuchungen"},
        pl={"Z": "sind Einzelzimmerbuchungen", "D": "sind Doppelzimmerbuchungen",
            "Z/F": "sind mit Frühstück gebucht", "Z/N": "sind ohne Verpflegung gebucht",
            "D/F": "sind mit Frühstück gebucht", "D/H": "sind mit Halbpension gebucht", "D/N": "sind ohne Verpflegung gebucht"},
        sg={"Z": "ist eine Einzelzimmerbuchung", "D": "ist eine Doppelzimmerbuchung",
            "Z/F": "ist mit Frühstück gebucht", "Z/N": "ist ohne Verpflegung gebucht",
            "D/F": "ist mit Frühstück gebucht", "D/H": "ist mit Halbpension gebucht", "D/N": "ist ohne Verpflegung gebucht"},
        pfad_pl={"Z/F": "sind Einzelzimmer mit Frühstück", "Z/N": "sind Einzelzimmer ohne Verpflegung",
                 "D/F": "sind Doppelzimmer mit Frühstück", "D/H": "sind Doppelzimmer mit Halbpension",
                 "D/N": "sind Doppelzimmer ohne Verpflegung"},
        pfad_sg={"Z/F": "ist ein Einzelzimmer mit Frühstück", "Z/N": "ist ein Einzelzimmer ohne Verpflegung",
                 "D/F": "ist ein Doppelzimmer mit Frühstück", "D/H": "ist ein Doppelzimmer mit Halbpension",
                 "D/N": "ist ein Doppelzimmer ohne Verpflegung"},
        ereignisse=[
            Ereignis("sind mit Frühstück gebucht", "ist mit Frühstück gebucht", ("Z/F", "D/F")),
            Ereignis("sind ohne Verpflegung gebucht", "ist ohne Verpflegung gebucht", ("Z/N", "D/N")),
            Ereignis("sind mit Verpflegung gebucht", "ist mit Verpflegung gebucht", ("Z/F", "D/F", "D/H")),
        ],
        n_werte=[400, 500, 800, 1000, 2000, 4000],
        bereiche={"Z": (0.2, 0.5), "D/H": (0.1, 0.3)},
        mutationen=("angleichen", "tauschen", "weglassen", "kappen"),
    ),
    # ---- T7: Prozess mit Abbruch beim ersten Erfolg ------------------------
    Szenario(
        key="fahrpruefung", personen=True, form="T7", baum="B N(B N(B N))",
        intro=(
            "Eine Fahrschule hat die praktischen Prüfungen ihrer Fahrschüler ausgewertet. Jeder "
            "Fahrschüler hat höchstens drei Versuche. Eine Prüfung wird bestanden (B) oder nicht "
            "bestanden (N). Wer bestanden hat, tritt nicht mehr an."
        ),
        gesamt="Ausgewertet wurden {N} Fahrschüler.",
        alle_gen="aller Fahrschüler", der_alle="der Fahrschüler",
        gruppe_gen={"": "der Fahrschüler",
                    "N": "der im ersten Versuch durchgefallenen Fahrschüler",
                    "N/N": "der auch im zweiten Versuch durchgefallenen Fahrschüler"},
        pl={"B": "bestehen im ersten Versuch", "N": "fallen im ersten Versuch durch",
            "N/B": "bestehen im zweiten Versuch", "N/N": "fallen auch im zweiten Versuch durch",
            "N/N/B": "bestehen im dritten Versuch", "N/N/N": "fallen auch im dritten Versuch durch"},
        sg={"B": "besteht im ersten Versuch", "N": "fällt im ersten Versuch durch",
            "N/B": "besteht im zweiten Versuch", "N/N": "fällt auch im zweiten Versuch durch",
            "N/N/B": "besteht im dritten Versuch", "N/N/N": "fällt auch im dritten Versuch durch"},
        pfad_pl={"N/B": "bestehen erst im zweiten Versuch", "N/N": "fallen zweimal durch",
                 "N/N/B": "bestehen erst im dritten Versuch", "N/N/N": "fallen dreimal durch"},
        pfad_sg={"N/B": "besteht erst im zweiten Versuch", "N/N": "fällt zweimal durch",
                 "N/N/B": "besteht erst im dritten Versuch", "N/N/N": "fällt dreimal durch"},
        ereignisse=[
            Ereignis("bestehen die Prüfung", "besteht die Prüfung", ("B", "N/B", "N/N/B")),
            Ereignis("bestehen spätestens im zweiten Versuch",
                     "besteht spätestens im zweiten Versuch", ("B", "N/B")),
            Ereignis("fallen mindestens einmal durch", "fällt mindestens einmal durch",
                     ("N/B", "N/N/B", "N/N/N")),
        ],
        n_werte=[1000, 2000, 4000, 5000, 8000, 10000],
        bereiche={"B": (0.5, 0.8), "N/B": (0.4, 0.8), "N/N/B": (0.3, 0.7)},
        mutationen=("fortsetzen", "kappen"),
    ),
    Szenario(
        key="qualitaet", form="T7", baum="F M(F M(F M))",
        intro=(
            "In einer Fabrik wird jedes Bauteil geprüft. Es ist fehlerfrei (F) oder mangelhaft (M). "
            "Ein fehlerfreies Teil wird ausgeliefert. Ein mangelhaftes Teil wird nachgebessert und "
            "erneut geprüft. Ein Teil wird höchstens zweimal nachgebessert, danach wird es aussortiert."
        ),
        gesamt="Ausgewertet wurden {N} Bauteile.",
        alle_gen="aller Bauteile", der_alle="der Bauteile",
        gruppe_gen={"": "der Bauteile",
                    "M": "der bei der ersten Prüfung mangelhaften Teile",
                    "M/M": "der auch nach der ersten Nachbesserung mangelhaften Teile"},
        pl={"F": "sind bei der ersten Prüfung fehlerfrei", "M": "sind bei der ersten Prüfung mangelhaft",
            "M/F": "sind nach der ersten Nachbesserung fehlerfrei",
            "M/M": "sind auch nach der ersten Nachbesserung mangelhaft",
            "M/M/F": "sind nach der zweiten Nachbesserung fehlerfrei",
            "M/M/M": "sind auch nach der zweiten Nachbesserung mangelhaft"},
        sg={"F": "ist bei der ersten Prüfung fehlerfrei", "M": "ist bei der ersten Prüfung mangelhaft",
            "M/F": "ist nach der ersten Nachbesserung fehlerfrei",
            "M/M": "ist auch nach der ersten Nachbesserung mangelhaft",
            "M/M/F": "ist nach der zweiten Nachbesserung fehlerfrei",
            "M/M/M": "ist auch nach der zweiten Nachbesserung mangelhaft"},
        pfad_pl={"M/F": "sind erst nach der ersten Nachbesserung fehlerfrei",
                 "M/M": "sind auch nach der ersten Nachbesserung noch mangelhaft",
                 "M/M/F": "sind erst nach der zweiten Nachbesserung fehlerfrei",
                 "M/M/M": "werden aussortiert"},
        pfad_sg={"M/F": "ist erst nach der ersten Nachbesserung fehlerfrei",
                 "M/M": "ist auch nach der ersten Nachbesserung noch mangelhaft",
                 "M/M/F": "ist erst nach der zweiten Nachbesserung fehlerfrei",
                 "M/M/M": "wird aussortiert"},
        ereignisse=[
            Ereignis("werden ausgeliefert", "wird ausgeliefert", ("F", "M/F", "M/M/F")),
            Ereignis("müssen nachgebessert werden", "muss nachgebessert werden", ("M/F", "M/M/F", "M/M/M")),
            Ereignis("werden höchstens einmal nachgebessert und dann ausgeliefert",
                     "wird höchstens einmal nachgebessert und dann ausgeliefert", ("F", "M/F")),
        ],
        n_werte=[1000, 2000, 4000, 5000, 8000, 10000],
        bereiche={"F": (0.6, 0.9), "M/F": (0.5, 0.9), "M/M/F": (0.3, 0.8)},
        mutationen=("fortsetzen", "kappen"),
    ),
    # ---- T10: nur ein Ast geht in eine dritte Stufe -------------------------
    Szenario(
        key="werkstatt", form="T10", baum="W(S T) R(S T(V B))",
        intro=(
            "Eine Fahrradwerkstatt hat ihre Aufträge ausgewertet. Ein Fahrrad kommt zur Wartung (W) "
            "oder zur Reparatur (R). Der Auftrag ist sofort erledigt (S), oder es wird ein Ersatzteil "
            "gebraucht (T). Bei Reparaturen mit Ersatzteil wurde außerdem erfasst, ob das Teil "
            "vorrätig (V) war oder bestellt (B) werden musste."
        ),
        gesamt="Ausgewertet wurden {N} Aufträge.",
        alle_gen="aller Aufträge", der_alle="der Aufträge",
        gruppe_gen={"": "der Aufträge", "W": "der Wartungen", "R": "der Reparaturen",
                    "R/T": "der Reparaturen mit Ersatzteil"},
        pl={"W": "sind Wartungen", "R": "sind Reparaturen",
            "W/S": "sind sofort erledigt", "W/T": "brauchen ein Ersatzteil",
            "R/S": "sind sofort erledigt", "R/T": "brauchen ein Ersatzteil",
            "R/T/V": "haben ein vorrätiges Teil", "R/T/B": "müssen auf ein bestelltes Teil warten"},
        sg={"W": "ist eine Wartung", "R": "ist eine Reparatur",
            "W/S": "ist sofort erledigt", "W/T": "braucht ein Ersatzteil",
            "R/S": "ist sofort erledigt", "R/T": "braucht ein Ersatzteil",
            "R/T/V": "hat ein vorrätiges Teil", "R/T/B": "muss auf ein bestelltes Teil warten"},
        pfad_pl={"W/S": "sind sofort erledigte Wartungen", "W/T": "sind Wartungen mit Ersatzteil",
                 "R/S": "sind sofort erledigte Reparaturen", "R/T": "sind Reparaturen mit Ersatzteil",
                 "R/T/V": "sind Reparaturen mit vorrätigem Ersatzteil",
                 "R/T/B": "sind Reparaturen mit bestelltem Ersatzteil"},
        pfad_sg={"W/S": "ist eine sofort erledigte Wartung", "W/T": "ist eine Wartung mit Ersatzteil",
                 "R/S": "ist eine sofort erledigte Reparatur", "R/T": "ist eine Reparatur mit Ersatzteil",
                 "R/T/V": "ist eine Reparatur mit vorrätigem Ersatzteil",
                 "R/T/B": "ist eine Reparatur mit bestelltem Ersatzteil"},
        ereignisse=[
            Ereignis("sind sofort erledigt", "ist sofort erledigt", ("W/S", "R/S")),
            Ereignis("brauchen ein Ersatzteil", "braucht ein Ersatzteil", ("W/T", "R/T/V", "R/T/B")),
            Ereignis("sind ohne Warten auf ein bestelltes Teil erledigt",
                     "ist ohne Warten auf ein bestelltes Teil erledigt", ("W/S", "W/T", "R/S", "R/T/V")),
        ],
        n_werte=[1000, 2000, 4000, 5000, 8000, 10000],
        bereiche={"W": (0.3, 0.7), "W/S": (0.5, 0.9), "R/S": (0.2, 0.6)},
        mutationen=("fortsetzen", "angleichen", "kappen"),
    ),
    Szenario(
        key="pakete", form="T10", baum="D(Z N(F R)) A(Z N)",
        intro=(
            "Ein Paketdienst hat seine Zustellungen ausgewertet. Ein Paket bleibt in Deutschland (D) oder geht "
            "ins Ausland (A). Es wird beim ersten Versuch zugestellt (Z) oder der Empfänger wird nicht "
            "angetroffen (N). Ein Inlandspaket, das nicht zugestellt werden konnte, wird in einer "
            "Filiale abgeholt (F) oder an den Absender zurückgeschickt (R)."
        ),
        gesamt="Ausgewertet wurden {N} Pakete.",
        alle_gen="aller Pakete", der_alle="der Pakete",
        gruppe_gen={"": "der Pakete", "D": "der Inlandspakete", "A": "der Auslandspakete",
                    "D/N": "der nicht zugestellten Inlandspakete"},
        pl={"D": "bleiben in Deutschland", "A": "gehen ins Ausland",
            "D/Z": "werden beim ersten Versuch zugestellt", "D/N": "können nicht zugestellt werden",
            "A/Z": "werden beim ersten Versuch zugestellt", "A/N": "können nicht zugestellt werden",
            "D/N/F": "werden in einer Filiale abgeholt", "D/N/R": "werden zurückgeschickt"},
        sg={"D": "bleibt in Deutschland", "A": "geht ins Ausland",
            "D/Z": "wird beim ersten Versuch zugestellt", "D/N": "kann nicht zugestellt werden",
            "A/Z": "wird beim ersten Versuch zugestellt", "A/N": "kann nicht zugestellt werden",
            "D/N/F": "wird in einer Filiale abgeholt", "D/N/R": "wird zurückgeschickt"},
        pfad_pl={"D/Z": "sind beim ersten Versuch zugestellte Inlandspakete",
                 "D/N": "sind nicht zugestellte Inlandspakete",
                 "A/Z": "sind beim ersten Versuch zugestellte Auslandspakete",
                 "A/N": "sind nicht zugestellte Auslandspakete",
                 "D/N/F": "sind in einer Filiale abgeholte Inlandspakete",
                 "D/N/R": "sind zurückgeschickte Inlandspakete"},
        pfad_sg={"D/Z": "ist ein beim ersten Versuch zugestelltes Inlandspaket",
                 "D/N": "ist ein nicht zugestelltes Inlandspaket",
                 "A/Z": "ist ein beim ersten Versuch zugestelltes Auslandspaket",
                 "A/N": "ist ein nicht zugestelltes Auslandspaket",
                 "D/N/F": "ist ein in einer Filiale abgeholtes Inlandspaket",
                 "D/N/R": "ist ein zurückgeschicktes Inlandspaket"},
        ereignisse=[
            Ereignis("werden beim ersten Versuch zugestellt", "wird beim ersten Versuch zugestellt", ("D/Z", "A/Z")),
            Ereignis("werden nicht beim ersten Versuch zugestellt",
                     "wird nicht beim ersten Versuch zugestellt", ("D/N/F", "D/N/R", "A/N")),
            Ereignis("erreichen ihren Empfänger", "erreicht seinen Empfänger", ("D/Z", "D/N/F", "A/Z")),
        ],
        n_werte=[1000, 2000, 4000, 5000, 8000, 10000],
        bereiche={"D": (0.6, 0.9), "D/Z": (0.6, 0.9), "A/Z": (0.5, 0.8), "D/N/F": (0.6, 0.9)},
        mutationen=("fortsetzen", "angleichen", "kappen"),
    ),
]


# ---------------------------------------------------------------------------
# Formatierung
# ---------------------------------------------------------------------------

def _dez(wert: Fraction) -> str:
    text = f"{float(wert):.4f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def _prozent(wert: Fraction) -> str:
    text = f"{float(wert * 100):.2f}".rstrip("0").rstrip(".")
    return text.replace(".", ",") + _NBSP + "%"


def _ganz(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _pfeil(pfad: Pfad) -> str:
    return " → ".join(pfad)


_PARTIKEL = {"teil", "durch", "aus", "an", "ab", "zurück", "mit"}
_FINIT = {
    "sind", "ist", "werden", "nehmen", "trainieren", "nutzen", "fallen", "bestehen",
    "gehen", "bleiben", "können", "müssen", "brauchen", "haben", "erreichen",
}


def _verb_ans_ende(teil: str) -> str:
    """„nehmen an Wettkämpfen teil“ -> „an Wettkämpfen teilnehmen“."""
    woerter = teil.split()
    finit, rest = woerter[0], woerter[1:]
    if rest and rest[-1] in _PARTIKEL:
        return " ".join(rest[:-1] + [rest[-1] + finit])
    return " ".join(rest + [finit])


def _nebensatz(praedikat_pl: str) -> str:
    """Prädikat (Plural, Hauptsatzstellung) in Nebensatzstellung für „…, die …“.

    Koordinationen mit eigenem Verb werden einzeln umgestellt
    („sind Kinder und nehmen … teil“ -> „Kinder sind und … teilnehmen“),
    elliptische als Ganzes („werden bezahlt und zurückgeschickt“ ->
    „bezahlt und zurückgeschickt werden“).
    """
    if "," in praedikat_pl:
        raise ValueError(f"Prädikat mit Komma nicht umstellbar: {praedikat_pl!r}")
    if praedikat_pl.split()[0] not in _FINIT:
        raise ValueError(f"Unbekanntes finites Verb: {praedikat_pl!r}")
    teile = praedikat_pl.split(" und ")
    if len(teile) > 1 and all(t.split()[0] in _FINIT for t in teile):
        return " und ".join(_verb_ans_ende(t) for t in teile)
    return _verb_ans_ende(praedikat_pl)


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

@dataclass
class _Fall:
    szenario: Szenario
    baum: Baum
    kanten: dict[Pfad, Fraction]
    werte: dict
    angaben: list[Angabe]
    n: int
    bruch_texte: dict[Pfad, str]


class _Szenariohelfer:
    def __init__(self, sz: Szenario):
        self.sz = sz
        self.baum = Baum.parse(sz.baum)
        self.ereignisse = [
            (e, tuple(_p(b) for b in e.blaetter)) for e in sz.ereignisse
        ]
        self._pruefe()

    def _pruefe(self) -> None:
        sz, baum = self.sz, self.baum
        verboten = baum.labels() & _VERBOTENE_LABELS
        if verboten:
            raise ValueError(f"{sz.key}: verbotene Labels {verboten}")
        for p in baum.knoten():
            key = "/".join(p)
            if key not in sz.pl or key not in sz.sg:
                raise ValueError(f"{sz.key}: Prädikat für {key} fehlt")
        for p in baum.innere():
            if "/".join(p) not in sz.gruppe_gen:
                raise ValueError(f"{sz.key}: Gruppe für {'/'.join(p) or 'Wurzel'} fehlt")
        for p in baum.knoten():
            _nebensatz(sz.pl["/".join(p)])
            if len(p) >= 2 and baum.ist_blatt(p):
                _nebensatz(self.pfad_pl(p))
        blaetter = set(baum.blaetter())
        for e, bl in self.ereignisse:
            if not set(bl) <= blaetter or len(bl) < 2:
                raise ValueError(f"{sz.key}: Ereignis {e.pl} passt nicht zum Baum")
            _nebensatz(e.pl)

    # -- Texte ----------------------------------------------------------------

    def pfad_pl(self, p: Pfad) -> str:
        key = "/".join(p)
        if len(p) == 1:
            return self.sz.pl[key]
        return self.sz.pfad_pl[key]

    def pfad_sg(self, p: Pfad) -> str:
        key = "/".join(p)
        if len(p) == 1:
            return self.sz.sg[key]
        return self.sz.pfad_sg[key]

    def gruppe(self, p: Pfad) -> str:
        return self.sz.gruppe_gen["/".join(p)]

    def satz(self, a: Angabe, n: int, bruch_texte: dict[Pfad, tuple[str, str]]) -> str:
        sz = self.sz
        if a.art == "kante":
            p = a.ziel[0]
            key = "/".join(p)
            gruppe = self.gruppe(p[:-1])
            if a.darstellung == "prozent":
                return f"{_prozent(a.wert)} {gruppe} {sz.pl[key]}."
            if a.darstellung == "bruch":
                text, numerus = bruch_texte[p]
                verb = sz.sg[key] if numerus == "sg" else sz.pl[key]
                return f"{text} {gruppe} {verb}."
            return f"{_ganz(int(a.wert * n))} {sz.der_alle} {sz.pl[key]}."
        if a.art == "knoten":
            p = a.ziel[0]
            if a.darstellung == "prozent":
                return f"{_prozent(a.wert)} {sz.alle_gen} {self.pfad_pl(p)}."
            return f"{_ganz(int(a.wert * n))} {sz.der_alle} {self.pfad_pl(p)}."
        ereignis = self._ereignis_zu(a.ziel)
        if a.darstellung == "prozent":
            return f"Insgesamt {_prozent(a.wert)} {sz.alle_gen} {ereignis.pl}."
        return f"Insgesamt {_ganz(int(a.wert * n))} {sz.der_alle} {ereignis.pl}."

    def _ereignis_zu(self, blaetter: tuple[Pfad, ...]) -> Ereignis:
        for e, bl in self.ereignisse:
            if bl == blaetter:
                return e
        raise KeyError(blaetter)

    # -- Zahlen ---------------------------------------------------------------

    def ziehe_kanten(self, rng: random.Random) -> dict[Pfad, Fraction] | None:
        baum, sz = self.baum, self.sz
        tief = baum.tiefe()
        kanten: dict[Pfad, Fraction] = {}
        for p in baum.innere():
            ks = baum.kinder(p)
            raster = Fraction(1, 20) if (len(p) == 0 or tief <= 2) else Fraction(1, 10)
            werte = self._ziehe_verteilung(rng, ks, raster)
            if werte is None:
                return None
            kanten.update(werte)
        for q in wahre_werte(baum, kanten).values():
            if not hat_hoechstens_dezimalen(q, 4):
                return None
        return kanten

    def _ziehe_verteilung(self, rng, ks: list[Pfad], raster: Fraction) -> dict[Pfad, Fraction] | None:
        sz = self.sz
        schritte = int(1 / raster)
        for _ in range(200):
            werte: dict[Pfad, Fraction] = {}
            rest = Fraction(1)
            ok = True
            for k in ks[:-1]:
                lo, hi = sz.bereiche.get("/".join(k), (0.1, 0.9))
                kandidaten = [
                    Fraction(i, schritte) for i in range(1, schritte)
                    if lo - 1e-9 <= i / schritte <= hi + 1e-9 and Fraction(i, schritte) < rest
                ]
                if not kandidaten:
                    ok = False
                    break
                w = rng.choice(kandidaten)
                werte[k] = w
                rest -= w
            if not ok:
                continue
            letzter = ks[-1]
            lo, hi = sz.bereiche.get("/".join(letzter), (0.05, 0.95))
            if not (lo - 1e-9 <= float(rest) <= hi + 1e-9) or rest <= 0:
                continue
            werte[letzter] = rest
            if len(set(werte.values())) < len(werte):
                continue  # gleiche Werte an Geschwisterästen wirken zufällig
            return werte
        return None


def _kandidaten(h: _Szenariohelfer, kanten: dict[Pfad, Fraction], werte: dict) -> list[Angabe]:
    baum = h.baum
    out: list[Angabe] = []
    for p in baum.knoten():
        e = kanten[p]
        darst = ["prozent"]
        if e in _BRUCH_TEXT:
            darst.append("bruch")
        if len(p) == 1:
            darst.append("absolut")
        for d in darst:
            out.append(Angabe("kante", (p,), e, d))
        if len(p) >= 2 and baum.ist_blatt(p):
            for d in ("prozent", "absolut"):
                out.append(Angabe("knoten", (p,), werte[("q", p)], d))
    for _, bl in h.ereignisse:
        w = sum((werte[("q", b)] for b in bl), Fraction(0))
        for d in ("prozent", "absolut"):
            out.append(Angabe("summe", bl, w, d))
    return out


def _ziel_key(a: Angabe) -> tuple:
    return (a.art == "summe", a.ziel)


def _waehle_angaben(rng, h: _Szenariohelfer, kandidaten: list[Angabe], streng: bool):
    baum = h.baum
    k = baum.freiheitsgrade()
    for _ in range(400):
        rng.shuffle(kandidaten)
        gewaehlt: list[Angabe] = []
        belegt: set = set()
        for a in kandidaten:
            # pro Knoten höchstens eine Angabe (Kante oder Pfadende)
            key = _ziel_key(a)
            if key in belegt:
                continue
            gewaehlt.append(a)
            belegt.add(key)
            if len(gewaehlt) == k:
                break
        if len(gewaehlt) < k:
            continue
        darst = [a.darstellung for a in gewaehlt]
        if "absolut" not in darst or "prozent" not in darst:
            continue
        if darst.count("absolut") > 2:
            continue
        if streng and "bruch" not in darst:
            continue
        if not any(a.art in ("knoten", "summe") for a in gewaehlt):
            continue
        if sum(1 for a in gewaehlt if a.art == "summe") > 1:
            continue
        loesung = loese(baum, gewaehlt)
        if not loesung.vollstaendig or loesung.rueckwaerts < 1:
            continue
        return gewaehlt, loesung
    return None


def _waehle_n(rng, sz: Szenario, angaben: list[Angabe]) -> int | None:
    kandidaten = list(sz.n_werte)
    rng.shuffle(kandidaten)
    for n in kandidaten:
        ok = True
        for a in angaben:
            if a.darstellung == "absolut":
                anzahl = a.wert * n
                if anzahl.denominator != 1 or anzahl < 10:
                    ok = False
                    break
        if ok:
            return n
    return None


class BaumdiagrammKomplexGenerator(TaskGenerator):
    generator_key = "stochastik.mehrstufige_zufallsexperimente.baumdiagramm_komplex"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        helfer = [_Szenariohelfer(sz) for sz in SZENARIEN]
        reihenfolge: list[_Szenariohelfer] = []
        while len(reihenfolge) < count:
            runde = list(helfer)
            rng.shuffle(runde)
            reihenfolge.extend(runde)
        return [self._aufgabe(rng, h) for h in reihenfolge[:count]]

    # -- eine Aufgabe ---------------------------------------------------------

    def _aufgabe(self, rng: random.Random, h: _Szenariohelfer) -> Task:
        for versuch in range(300):
            streng = versuch < 200
            kanten = h.ziehe_kanten(rng)
            if kanten is None:
                continue
            werte = wahre_werte(h.baum, kanten)
            auswahl = _waehle_angaben(rng, h, _kandidaten(h, kanten, werte), streng)
            if auswahl is None:
                continue
            angaben, loesung = auswahl
            n = _waehle_n(rng, h.sz, angaben)
            if n is None:
                continue
            fragen = self._fragen(rng, h, kanten, werte, angaben, loesung)
            if fragen is None:
                continue
            bruch_texte = {
                a.ziel[0]: rng.choice([
                    (t, num) for t, num, nur_personen in _BRUCH_TEXT[a.wert]
                    if h.sz.personen or not nur_personen
                ])
                for a in angaben if a.darstellung == "bruch"
            }
            return self._baue(rng, h, angaben, n, bruch_texte, fragen)
        raise RuntimeError(f"Keine gültige Aufgabe für Szenario {h.sz.key}")

    def _fragen(self, rng, h, kanten, werte, angaben, loesung):
        baum = h.baum
        gegebene_kanten = {a.ziel[0] for a in angaben if a.art == "kante"}
        gegebene_knoten = {a.ziel[0] for a in angaben if a.art == "knoten"}
        gegebene_summen = {a.ziel for a in angaben if a.art == "summe"}

        # Frage 3: Kante auf Stufe >= 2, nicht gegeben; bevorzugt rückwärts berechnet
        kanten_kand = [p for p in baum.knoten() if len(p) >= 2 and p not in gegebene_kanten]
        if not kanten_kand:
            return None
        rueck = {s.groesse[1] for s in loesung.schritte if s.regel == "division" and s.groesse[0] == "e"}
        bevorzugt = [p for p in kanten_kand if p in rueck]
        f3 = rng.choice(bevorzugt or kanten_kand)

        # Frage 4: Pfadende (Tiefe >= 2), nicht gegeben, möglichst nicht der Pfad aus Frage 3
        blatt_kand = [b for b in baum.blaetter() if len(b) >= 2 and b not in gegebene_knoten]
        if not blatt_kand:
            return None
        anders = [b for b in blatt_kand if b != f3]
        f4 = rng.choice(anders or blatt_kand)

        # Frage 5: Ereignis über mehrere Pfade, nicht gegeben
        ereignis_kand = [(e, bl) for e, bl in h.ereignisse if bl not in gegebene_summen]
        if not ereignis_kand:
            return None
        f5 = rng.choice(ereignis_kand)

        # Frage 2: Angabe als Pfadende oder Summe
        zuordnung_kand = [a for a in angaben if a.art in ("knoten", "summe")]
        f2 = rng.choice(zuordnung_kand)

        return f2, f3, f4, f5

    def _zuordnung(self, rng, h: _Szenariohelfer, a: Angabe) -> tuple[list[str], int]:
        if a.art == "knoten":
            p = a.ziel[0]
            richtig = f"am Ende des Pfades {_pfeil(p)}"
            falsch = [
                f"am letzten Ast des Pfades {_pfeil(p)}",
                f"am ersten Ast des Pfades {_pfeil(p)}",
                f"an jedem Ast, der zu {p[-1]} führt",
            ]
        else:
            bl = a.ziel
            liste = [_pfeil(b) for b in bl]
            richtig = (
                "nicht an einer Stelle: Er ist die Summe der Pfade "
                + ", ".join(liste[:-1]) + " und " + liste[-1]
            )
            b0 = bl[0]
            falsch = [f"am Ende des Pfades {_pfeil(b0)}"]
            if len(b0) >= 2:
                falsch.append(f"am letzten Ast des Pfades {_pfeil(b0)}")
            falsch.append(f"an jedem Ast, der zu {b0[-1]} führt")
        optionen = [richtig] + falsch[:3]
        rng.shuffle(optionen)
        return optionen, optionen.index(richtig)

    def _baue(self, rng, h: _Szenariohelfer, angaben, n, bruch_texte, fragen) -> Task:
        sz, baum = h.sz, h.baum
        f2, f3, f4, f5 = fragen

        # Sachtext: Stufe-1-Angaben zuerst, dann tiefere Kanten/Pfade, dann Summen
        def ordnung(a: Angabe):
            if a.art == "summe":
                return (9, ())
            return (len(a.ziel[0]), baum.knoten().index(a.ziel[0]))

        saetze = [h.satz(a, n, bruch_texte) for a in sorted(angaben, key=ordnung)]
        einleitung = " ".join(
            [sz.intro, sz.gesamt.format(N=_ganz(n))]
            + saetze
            + ["Zeichnen Sie zuerst das Baumdiagramm und tragen Sie die gegebenen Werte ein. "
               "Geben Sie Anteile als Dezimalzahl an."]
        )

        # Frage 1: Baumwahl
        falsche = self._falsche_baeume(rng, h)
        optionen = [baum] + falsche
        rng.shuffle(optionen)
        richtig_idx = optionen.index(baum)
        buchstaben = ["A", "B", "C", "D"]

        alle = loese(baum, angaben).werte

        wert3 = alle[("e", f3)]
        wert4 = alle[("q", f4)]
        e5, bl5 = f5
        wert5 = sum((alle[("q", b)] for b in bl5), Fraction(0))

        z_opts, z_idx = self._zuordnung(rng, h, f2)
        z_satz = h.satz(f2, n, bruch_texte)

        fragen_text = [
            "Geben Sie an, welches Baumdiagramm (A, B, C oder D) zum Sachverhalt passt.",
            f"Geben Sie an, wo der Anteil aus der Angabe „{z_satz}“ im Baumdiagramm steht.",
            f"Bestimmen Sie den Anteil {h.gruppe(f3[:-1])}, die {_nebensatz(sz.pl['/'.join(f3)])}.",
            f"Bestimmen Sie den Anteil {sz.alle_gen}, die {_nebensatz(h.pfad_pl(f4))}.",
            f"Bestimmen Sie den Anteil {sz.alle_gen}, die {_nebensatz(e5.pl)}.",
        ]
        antworten = [
            mc(buchstaben, richtig_idx),
            mc(z_opts, z_idx),
            numerical_stochastik_calc(float(wert3)),
            numerical_stochastik_calc(float(wert4)),
            numerical_stochastik_calc(float(wert5)),
        ]
        visual = {
            "type": "plot",
            "spec": {
                "type": "tree-choice",
                "labels": buchstaben,
                "options": [b.to_spec() for b in optionen],
            },
        }
        return Task(einleitung=einleitung, fragen=fragen_text, antworten=antworten, visual=visual)

    def _falsche_baeume(self, rng, h: _Szenariohelfer) -> list[Baum]:
        muts = mutationen(h.baum)
        nach_art: dict[str, list[Baum]] = {}
        for art, b in muts:
            if b.tiefe() > 3 or len(b.blaetter()) > 9:
                continue
            nach_art.setdefault(art, []).append(b)
        arten = [a for a in h.sz.mutationen if a in nach_art]
        anzahl = 3
        gewaehlt: list[Baum] = []
        # möglichst verschiedene Arten, bevorzugt in der Reihenfolge des Szenarios
        for art in rng.sample(arten[:anzahl], min(anzahl, len(arten[:anzahl]))):
            gewaehlt.append(rng.choice(nach_art[art]))
        rest = [b for a in arten for b in nach_art[a] if b not in gewaehlt]
        rng.shuffle(rest)
        while len(gewaehlt) < anzahl and rest:
            gewaehlt.append(rest.pop())
        if len(gewaehlt) < anzahl:
            raise RuntimeError(f"{h.sz.key}: zu wenige falsche Bäume")
        return gewaehlt
