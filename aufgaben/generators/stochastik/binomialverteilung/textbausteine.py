from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioTemplate:
    intro_prefix: str
    sample_object_plural: str
    group_dative_plural: str
    success_plural: str
    failure_plural: str
    success_event_accusative: str


def sample_probability_intro_variants(
    scenario: ScenarioTemplate,
    n: int,
    p_text: str,
) -> list[str]:
    return [
        (
            f"{scenario.intro_prefix} Es werden {n} {scenario.sample_object_plural} betrachtet. "
            f"Die Wahrscheinlichkeit für {scenario.success_event_accusative} beträgt {p_text}."
        ),
        (
            f"{scenario.intro_prefix} Die Stichprobe umfasst {n} {scenario.sample_object_plural}. "
            f"Dabei liegt die Wahrscheinlichkeit, {scenario.success_event_accusative} anzutreffen, bei {p_text}."
        ),
        (
            f"{scenario.intro_prefix} {n} {scenario.sample_object_plural} werden zufällig ausgewählt. "
            f"Für jedes Element der Stichprobe beträgt die Wahrscheinlichkeit für {scenario.success_event_accusative} {p_text}."
        ),
    ]


def probability_intro_variants(
    scenario: ScenarioTemplate,
    p_text: str,
) -> list[str]:
    return [
        f"{scenario.intro_prefix} Die Wahrscheinlichkeit für {scenario.success_event_accusative} beträgt {p_text}.",
        f"{scenario.intro_prefix} Die Wahrscheinlichkeit, {scenario.success_event_accusative} anzutreffen, liegt bei {p_text}.",
        f"{scenario.intro_prefix} Im betrachteten Modell beträgt die Wahrscheinlichkeit für {scenario.success_event_accusative} {p_text}.",
    ]


def join_sentences(*parts: str) -> str:
    return " ".join(part.strip() for part in parts if part and part.strip())


SCENARIOS: list[ScenarioTemplate] = [
    ScenarioTemplate(
        intro_prefix="Ein Kontrolleur überprüft die Funktionsfähigkeit von Halbleitern.",
        sample_object_plural="Halbleiter",
        group_dative_plural="kontrollierten Halbleitern",
        success_plural="defekte Halbleiter",
        failure_plural="heile Halbleiter",
        success_event_accusative="einen defekten Halbleiter",
    ),
    ScenarioTemplate(
        intro_prefix="Eine Schaffnerin kontrolliert Fahrscheine in einer Regionalbahn.",
        sample_object_plural="Passagiere",
        group_dative_plural="kontrollierten Passagieren",
        success_plural="Passagiere ohne gültigen Fahrschein",
        failure_plural="Passagiere mit gültigem Fahrschein",
        success_event_accusative="einen Passagier ohne gültigen Fahrschein",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Eisstand untersucht Bestellungen mit und ohne Streusel.",
        sample_object_plural="Bestellungen",
        group_dative_plural="betrachteten Bestellungen",
        success_plural="Bestellungen mit Streuseln",
        failure_plural="Bestellungen ohne Streuseln",
        success_event_accusative="eine Bestellung mit Streuseln",
    ),
    ScenarioTemplate(
        intro_prefix="Eine Trainerin protokolliert Treffer bei Freiwürfen.",
        sample_object_plural="Freiwürfe",
        group_dative_plural="beobachteten Freiwürfen",
        success_plural="Treffer",
        failure_plural="Fehlwürfe",
        success_event_accusative="einen Treffer",
    ),
    ScenarioTemplate(
        intro_prefix="Eine Ärztin bewertet Eignungstests von Bewerbern.",
        sample_object_plural="Bewerber",
        group_dative_plural="Bewerbern",
        success_plural="erfolgreiche Bewerber",
        failure_plural="nicht erfolgreiche Bewerber",
        success_event_accusative="einen erfolgreichen Bewerber",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Fahrlehrer wertet theoretische Führerscheinprüfungen aus.",
        sample_object_plural="Prüfungen",
        group_dative_plural="ausgewerteten Prüfungen",
        success_plural="nicht bestandene Prüfungen",
        failure_plural="bestandene Prüfungen",
        success_event_accusative="eine nicht bestandene Prüfung",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Zollbeamter überprüft Turnschuhe auf Fälschungen.",
        sample_object_plural="Turnschuhe",
        group_dative_plural="untersuchten Turnschuhen",
        success_plural="gefälschte Turnschuhe",
        failure_plural="nicht gefälschte Turnschuhe",
        success_event_accusative="einen gefälschten Turnschuh",
    ),
    ScenarioTemplate(
        intro_prefix="Eine Fußballspielerin dokumentiert Torschüsse im Training.",
        sample_object_plural="Torschüsse",
        group_dative_plural="beobachteten Torschüssen",
        success_plural="Fehlschüsse",
        failure_plural="Treffer",
        success_event_accusative="einen Fehlschuss",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Unternehmen erhebt die Zufriedenheit der Mitarbeitenden.",
        sample_object_plural="befragte Mitarbeitende",
        group_dative_plural="befragten Mitarbeitenden",
        success_plural="zufriedene Mitarbeitende",
        failure_plural="unzufriedene Mitarbeitende",
        success_event_accusative="eine zufriedene Person",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Restaurant betrachtet Bestellungen vegetarischer Gerichte.",
        sample_object_plural="Bestellungen",
        group_dative_plural="kontrollierten Bestellungen",
        success_plural="vegetarische Gerichte",
        failure_plural="Gerichte mit Fleisch",
        success_event_accusative="ein vegetarisches Gericht",
    ),
    ScenarioTemplate(
        intro_prefix="Eine Gärtnerei überprüft Pflanzen auf Trockenstress.",
        sample_object_plural="Pflanzen",
        group_dative_plural="geprüften Pflanzen",
        success_plural="zu trockene Pflanzen",
        failure_plural="ausreichend bewässerte Pflanzen",
        success_event_accusative="eine zu trockene Pflanze",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Onlineshop prüft, ob Werkzeuge mit Akku ausgeliefert werden.",
        sample_object_plural="Werkzeuge",
        group_dative_plural="registrierten Werkzeugen",
        success_plural="Werkzeuge mit Akku",
        failure_plural="Werkzeuge mit Kabel",
        success_event_accusative="ein Werkzeug mit Akku",
    ),
    ScenarioTemplate(
        intro_prefix="Eine IT-Abteilung kontrolliert Geräte auf ausreichenden Virenschutz.",
        sample_object_plural="Computer",
        group_dative_plural="untersuchten Computern",
        success_plural="Computer ohne ausreichenden Virenschutz",
        failure_plural="Computer mit ausreichendem Virenschutz",
        success_event_accusative="einen Computer ohne ausreichenden Virenschutz",
    ),
    ScenarioTemplate(
        intro_prefix="Eine Glaserei untersucht Krüge auf Kratzer.",
        sample_object_plural="Krüge",
        group_dative_plural="überprüften Krügen",
        success_plural="Krüge mit Kratzer",
        failure_plural="Krüge ohne Kratzer",
        success_event_accusative="einen Krug mit Kratzer",
    ),
    ScenarioTemplate(
        intro_prefix="Eine Plattform wertet Reaktionen auf Produktempfehlungen aus.",
        sample_object_plural="angezeigte Empfehlungen",
        group_dative_plural="angezeigten Empfehlungen",
        success_plural="angeklickte Empfehlungen",
        failure_plural="nicht angeklickte Empfehlungen",
        success_event_accusative="eine angeklickte Empfehlung",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Versandhändler legt stichprobenartig Gutscheine in Pakete.",
        sample_object_plural="Pakete",
        group_dative_plural="kontrollierten Paketen",
        success_plural="Pakete mit Gutschein",
        failure_plural="Pakete ohne Gutschein",
        success_event_accusative="ein Paket mit Gutschein",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Verlag prüft Drucke auf Rechtschreibfehler.",
        sample_object_plural="gedruckte Seiten",
        group_dative_plural="geprüften Seiten",
        success_plural="Seiten mit Rechtschreibfehler",
        failure_plural="fehlerfreie Seiten",
        success_event_accusative="eine Seite mit Rechtschreibfehler",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Labor testet Wasserproben auf einen Grenzwert.",
        sample_object_plural="Wasserproben",
        group_dative_plural="analysierten Wasserproben",
        success_plural="auffällige Wasserproben",
        failure_plural="unauffällige Wasserproben",
        success_event_accusative="eine auffällige Wasserprobe",
    ),
    ScenarioTemplate(
        intro_prefix="Ein Kundendienst erfasst Anfragen, die im Erstkontakt gelöst werden.",
        sample_object_plural="Serviceanfragen",
        group_dative_plural="erfassten Serviceanfragen",
        success_plural="im Erstkontakt gelöste Anfragen",
        failure_plural="nicht im Erstkontakt gelöste Anfragen",
        success_event_accusative="eine im Erstkontakt gelöste Anfrage",
    ),
    ScenarioTemplate(
        intro_prefix="Eine Schule dokumentiert Anwesenheiten im Mathekurs.",
        sample_object_plural="Teilnahmen",
        group_dative_plural="dokumentierten Teilnahmen",
        success_plural="Anwesenheiten",
        failure_plural="Fehlzeiten",
        success_event_accusative="eine Anwesenheit",
    ),
]
