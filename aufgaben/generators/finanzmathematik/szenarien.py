"""Gemeinsamer Szenario-Pool der Finanzmathematik (privat und Unternehmen).

Alle Texte sind ohne Zahlenwerte; die Zahlen kommen in den Teilfragen.
Sätze in den Generatoren beginnen stets mit ``subjekt`` (Nominativ, Singular),
danach wird nur das Pronomen ``pron`` benötigt.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from aufgaben.generators.finanzmathematik.shared import STUFEN, Stufe


@dataclass(frozen=True)
class Szenario:
    subjekt: str
    pron: str
    stufe_name: str
    zweck_anlage: str
    zweck_darlehen: str
    verkauf_akk: str
    kauf_akk: str
    intro_anlage: str
    intro_darlehen: str

    @property
    def stufe(self) -> Stufe:
        return STUFEN[self.stufe_name]


SZENARIEN: tuple[Szenario, ...] = (
    # ── privat, kleine Beträge ───────────────────────────────────────────
    Szenario(
        subjekt="Familie Berger",
        pron="sie",
        stufe_name="privat_klein",
        zweck_anlage="für ein Auslandsjahr der Tochter",
        zweck_darlehen="für die Anschaffung eines Kleinwagens",
        verkauf_akk="ihren gebrauchten Wohnwagen",
        kauf_akk="ein E-Bike mit Zubehör",
        intro_anlage="Familie Berger möchte für ein Auslandsjahr der Tochter Geld zurücklegen und lässt sich bei der Bank verschiedene Sparmöglichkeiten erklären.",
        intro_darlehen="Familie Berger benötigt für die Anschaffung eines Kleinwagens ein Darlehen und vergleicht die Konditionen ihrer Hausbank.",
    ),
    Szenario(
        subjekt="Herr Nowak",
        pron="er",
        stufe_name="privat_klein",
        zweck_anlage="für seine Weiterbildung zum Meister",
        zweck_darlehen="für eine neue Einbauküche",
        verkauf_akk="seinen Gebrauchtwagen",
        kauf_akk="einen gebrauchten Kleinwagen",
        intro_anlage="Herr Nowak möchte seine Weiterbildung zum Meister aus eigenen Ersparnissen finanzieren und überlegt, wie er sein Geld am besten anlegt.",
        intro_darlehen="Herr Nowak plant den Kauf einer neuen Einbauküche und möchte dafür ein Darlehen aufnehmen.",
    ),
    Szenario(
        subjekt="Frau Lindqvist",
        pron="sie",
        stufe_name="privat_klein",
        zweck_anlage="für eine Weltreise nach dem Studium",
        zweck_darlehen="für die Einrichtung ihrer ersten eigenen Wohnung",
        verkauf_akk="ihre professionelle Fotoausrüstung",
        kauf_akk="ein gebrauchtes Motorrad",
        intro_anlage="Frau Lindqvist spart für eine Weltreise nach dem Studium und rechnet verschiedene Anlagevarianten durch.",
        intro_darlehen="Frau Lindqvist richtet ihre erste eigene Wohnung ein und prüft, welches Darlehen dafür infrage kommt.",
    ),
    Szenario(
        subjekt="Der Sportverein Blau-Weiß Hartmannsdorf",
        pron="er",
        stufe_name="privat_klein",
        zweck_anlage="für die Sanierung des Vereinsheims",
        zweck_darlehen="für einen neuen Rasentraktor",
        verkauf_akk="den alten Vereinsbus",
        kauf_akk="eine Flutlichtanlage",
        intro_anlage="Der Sportverein Blau-Weiß Hartmannsdorf legt Geld für die Sanierung des Vereinsheims zurück und berät in der Vorstandssitzung über die Geldanlage.",
        intro_darlehen="Der Sportverein Blau-Weiß Hartmannsdorf benötigt einen neuen Rasentraktor und holt Angebote für ein Darlehen ein.",
    ),
    Szenario(
        subjekt="Die Schülerfirma „Grüne Kiste“",
        pron="sie",
        stufe_name="privat_klein",
        zweck_anlage="für die Anschaffung eines Lastenrads",
        zweck_darlehen="für einen Kühlschrank am Verkaufsstand",
        verkauf_akk="ihren gebrauchten Verkaufsanhänger",
        kauf_akk="einen Lastenanhänger",
        intro_anlage="Die Schülerfirma „Grüne Kiste“ verkauft Gemüsekisten und möchte ihre Überschüsse für die Anschaffung eines Lastenrads anlegen.",
        intro_darlehen="Die Schülerfirma „Grüne Kiste“ braucht einen Kühlschrank für den Verkaufsstand und überlegt, ihn über ein kleines Darlehen zu finanzieren.",
    ),
    Szenario(
        subjekt="Familie Yilmaz",
        pron="sie",
        stufe_name="privat_klein",
        zweck_anlage="für die Hochzeitsfeier der Tochter",
        zweck_darlehen="für eine Photovoltaikanlage",
        verkauf_akk="ihren Zweitwagen",
        kauf_akk="ein gebrauchtes Wohnmobil",
        intro_anlage="Familie Yilmaz möchte rechtzeitig für die Hochzeitsfeier der Tochter vorsorgen und vergleicht Sparangebote.",
        intro_darlehen="Familie Yilmaz möchte eine Photovoltaikanlage auf dem Dach installieren und sie teilweise über ein Darlehen finanzieren.",
    ),
    Szenario(
        subjekt="Der Musiker Jonas Reuter",
        pron="er",
        stufe_name="privat_klein",
        zweck_anlage="für die Aufnahme eines eigenen Albums",
        zweck_darlehen="für ein neues Klavier",
        verkauf_akk="seine bisherige Bühnentechnik",
        kauf_akk="einen gebrauchten Konzertflügel",
        intro_anlage="Der Musiker Jonas Reuter spart auf die Aufnahme eines eigenen Albums und überlegt, wie er seine Einnahmen anlegt.",
        intro_darlehen="Der Musiker Jonas Reuter möchte ein neues Klavier kaufen und dafür ein Darlehen aufnehmen.",
    ),
    # ── privat, große Beträge ────────────────────────────────────────────
    Szenario(
        subjekt="Familie Osterloh",
        pron="sie",
        stufe_name="privat_gross",
        zweck_anlage="für das Eigenkapital eines Eigenheims",
        zweck_darlehen="für den Kauf einer Eigentumswohnung",
        verkauf_akk="ihr Ferienhaus an der Küste",
        kauf_akk="ein Baugrundstück",
        intro_anlage="Familie Osterloh spart Eigenkapital für ein Eigenheim an und lässt sich verschiedene Anlageformen vorrechnen.",
        intro_darlehen="Familie Osterloh möchte eine Eigentumswohnung kaufen und vergleicht Darlehensangebote.",
    ),
    Szenario(
        subjekt="Frau Dr. Ahrens",
        pron="sie",
        stufe_name="privat_gross",
        zweck_anlage="für ihre private Altersvorsorge",
        zweck_darlehen="für die Modernisierung ihres Hauses",
        verkauf_akk="eine geerbte Wohnung",
        kauf_akk="ein Ferienhaus in den Bergen",
        intro_anlage="Frau Dr. Ahrens kümmert sich um ihre private Altersvorsorge und prüft, wie sich verschiedene Anlagen entwickeln.",
        intro_darlehen="Frau Dr. Ahrens plant die Modernisierung ihres Hauses und möchte dafür ein Darlehen aufnehmen.",
    ),
    Szenario(
        subjekt="Herr Brandt",
        pron="er",
        stufe_name="privat_gross",
        zweck_anlage="für das Studium seiner Kinder",
        zweck_darlehen="für den Ausbau des Dachgeschosses",
        verkauf_akk="sein Segelboot",
        kauf_akk="ein Grundstück am See",
        intro_anlage="Herr Brandt möchte das Studium seiner Kinder finanziell absichern und vergleicht dafür Sparpläne und Einmalanlagen.",
        intro_darlehen="Herr Brandt möchte das Dachgeschoss seines Hauses ausbauen und benötigt dafür ein Darlehen.",
    ),
    Szenario(
        subjekt="Frau Kowalski",
        pron="sie",
        stufe_name="privat_gross",
        zweck_anlage="für eine Weltumsegelung im Ruhestand",
        zweck_darlehen="für den Anbau eines Wintergartens",
        verkauf_akk="ihren Oldtimer",
        kauf_akk="eine Ferienwohnung",
        intro_anlage="Frau Kowalski träumt von einer Weltumsegelung im Ruhestand und legt dafür planmäßig Geld an.",
        intro_darlehen="Frau Kowalski möchte einen Wintergarten anbauen lassen und holt dafür Darlehensangebote ein.",
    ),
    Szenario(
        subjekt="Herr Petersen",
        pron="er",
        stufe_name="privat_gross",
        zweck_anlage="für einen vorzeitigen Ruhestand",
        zweck_darlehen="für den Kauf einer Ferienwohnung",
        verkauf_akk="sein kleines Mietshaus",
        kauf_akk="einen Bauplatz am Stadtrand",
        intro_anlage="Herr Petersen möchte vorzeitig in den Ruhestand gehen und rechnet aus, wie sich seine Ersparnisse entwickeln.",
        intro_darlehen="Herr Petersen möchte eine Ferienwohnung kaufen und dafür ein Darlehen aufnehmen.",
    ),
    # ── Unternehmen ──────────────────────────────────────────────────────
    Szenario(
        subjekt="Die Bäckerei Konrad",
        pron="sie",
        stufe_name="unternehmen",
        zweck_anlage="für einen neuen Backofen",
        zweck_darlehen="für den Umbau der Backstube",
        verkauf_akk="einen älteren Lieferwagen",
        kauf_akk="eine Teigknetmaschine",
        intro_anlage="Die Bäckerei Konrad bildet Rücklagen für einen neuen Backofen und lässt sich von ihrer Bank Anlagemöglichkeiten vorrechnen.",
        intro_darlehen="Die Bäckerei Konrad plant den Umbau der Backstube und prüft verschiedene Finanzierungsangebote.",
    ),
    Szenario(
        subjekt="Die Möbelmanufaktur Lindner",
        pron="sie",
        stufe_name="unternehmen",
        zweck_anlage="für die Erweiterung der Ausstellungsfläche",
        zweck_darlehen="für eine CNC-Fräse",
        verkauf_akk="eine gebrauchte Furnierpresse",
        kauf_akk="eine Lackieranlage",
        intro_anlage="Die Möbelmanufaktur Lindner möchte ihre Ausstellungsfläche erweitern und legt dafür Gewinne zurück.",
        intro_darlehen="Die Möbelmanufaktur Lindner will eine CNC-Fräse anschaffen und diese über ein Darlehen finanzieren.",
    ),
    Szenario(
        subjekt="Das Start-up „Solvia Energy“",
        pron="es",
        stufe_name="unternehmen",
        zweck_anlage="für die Entwicklung eines neuen Speichersystems",
        zweck_darlehen="für die Einrichtung eines Prüflabors",
        verkauf_akk="ein Patent für eine Ladeelektronik",
        kauf_akk="eine Testanlage",
        intro_anlage="Das Start-up „Solvia Energy“ hat eine Finanzierungsrunde abgeschlossen und möchte einen Teil des Geldes bis zur Entwicklung eines neuen Speichersystems anlegen.",
        intro_darlehen="Das Start-up „Solvia Energy“ richtet ein Prüflabor ein und verhandelt mit der Bank über ein Darlehen.",
    ),
    Szenario(
        subjekt="Die Spedition Rademacher",
        pron="sie",
        stufe_name="unternehmen",
        zweck_anlage="für die Erneuerung der Fahrzeugflotte",
        zweck_darlehen="für den Bau einer Lagerhalle",
        verkauf_akk="eine ausgemusterte Sattelzugmaschine",
        kauf_akk="einen Gabelstapler",
        intro_anlage="Die Spedition Rademacher spart auf die Erneuerung ihrer Fahrzeugflotte und vergleicht Anlageangebote.",
        intro_darlehen="Die Spedition Rademacher plant den Bau einer Lagerhalle und benötigt dafür ein Darlehen.",
    ),
    Szenario(
        subjekt="Das Hotel Seeblick",
        pron="es",
        stufe_name="unternehmen",
        zweck_anlage="für die Renovierung der Zimmer",
        zweck_darlehen="für den Bau eines Wellnessbereichs",
        verkauf_akk="ein nicht mehr genutztes Nebengebäude",
        kauf_akk="eine neue Küchenausstattung",
        intro_anlage="Das Hotel Seeblick legt Rücklagen für die Renovierung der Zimmer an und lässt verschiedene Anlagevarianten durchrechnen.",
        intro_darlehen="Das Hotel Seeblick möchte einen Wellnessbereich bauen und prüft die Konditionen eines Darlehens.",
    ),
    Szenario(
        subjekt="Die Gärtnerei Wendland",
        pron="sie",
        stufe_name="unternehmen",
        zweck_anlage="für den Neubau eines Gewächshauses",
        zweck_darlehen="für eine Bewässerungsanlage",
        verkauf_akk="eine gebrauchte Pflanzmaschine",
        kauf_akk="einen Kühlraum",
        intro_anlage="Die Gärtnerei Wendland plant den Neubau eines Gewächshauses und legt dafür regelmäßig Geld an.",
        intro_darlehen="Die Gärtnerei Wendland möchte eine Bewässerungsanlage anschaffen und dafür ein Darlehen aufnehmen.",
    ),
    Szenario(
        subjekt="Das Architekturbüro Feld & Vogt",
        pron="es",
        stufe_name="unternehmen",
        zweck_anlage="für den Umzug in größere Räume",
        zweck_darlehen="für neue Büroausstattung und Software",
        verkauf_akk="die bisher genutzten Büroräume",
        kauf_akk="eine größere Bürofläche",
        intro_anlage="Das Architekturbüro Feld & Vogt spart auf den Umzug in größere Räume und rechnet verschiedene Sparvarianten durch.",
        intro_darlehen="Das Architekturbüro Feld & Vogt benötigt neue Büroausstattung und Software und will die Investition über ein Darlehen finanzieren.",
    ),
    Szenario(
        subjekt="Die Zahnarztpraxis Dr. Steinbach",
        pron="sie",
        stufe_name="unternehmen",
        zweck_anlage="für die Erweiterung der Praxis",
        zweck_darlehen="für eine neue Behandlungseinheit",
        verkauf_akk="ein älteres Röntgengerät",
        kauf_akk="einen 3D-Scanner",
        intro_anlage="Die Zahnarztpraxis Dr. Steinbach bildet Rücklagen für die Erweiterung der Praxis und vergleicht Anlageformen.",
        intro_darlehen="Die Zahnarztpraxis Dr. Steinbach möchte eine neue Behandlungseinheit anschaffen und dafür ein Darlehen aufnehmen.",
    ),
)


def szenario_folge(rng: random.Random, count: int) -> list[Szenario]:
    """Liefert ``count`` Szenarien; jedes Szenario kommt erst wieder vor, wenn alle genutzt wurden."""
    folge: list[Szenario] = []
    while len(folge) < count:
        block = list(SZENARIEN)
        rng.shuffle(block)
        folge.extend(block)
    return folge[:count]
