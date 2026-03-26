"""Komplexes Baumdiagramm mit Nutzungsgruppen (S, P, k) und Zwecken (U, V).

Struktur: Zweistufiges Modell mit einer terminalen Gruppe
  Stufe 1: drei Gruppen S, P, k
  Stufe 2: nur S und P verzweigen nach U/V; k bleibt terminal

Gegeben werden im Text:
  - P(S∩U) und P(S∩V) als Prozentwerte
  - |P∩V| als absolute Häufigkeit
  - |k| als absolute Häufigkeit

Gefragt werden drei kontextbezogene Wahrscheinlichkeiten:
  1. P(U) oder P(V)
  2. eine bedingte Wahrscheinlichkeit aus {P(U|S), P(V|S), P(U|P), P(V|P)}
  3. P(P) oder P(S)
"""

import random
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from aufgaben.core.models import Task
from aufgaben.core.placeholders import numerical, numerical_analysis_calc, numerical_stochastik_calc
from aufgaben.generators.base import TaskGenerator


_Q4 = Decimal("0.0001")


def _r4(v: Decimal) -> Decimal:
    return v.quantize(_Q4, rounding=ROUND_HALF_UP)


def _f(v: Decimal) -> float:
    return float(v)


def _fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _pct1(v: float) -> str:
    """Prozent mit einer Nachkommastelle und Dezimalkomma, z. B. 35,7."""
    return f"{v * 100:.1f}".replace(".", ",")


@dataclass(frozen=True)
class TemplateNutzung:
    intro: str
    stage1_text: str
    stage2_text: str
    chance_stat_tmpl: str  # {p_su_pct}, {p_sv_pct}
    abs_stat_tmpl: str     # {n_fmt}, {count_pv_fmt}, {count_k_fmt}
    q_total_u: str
    q_total_v: str
    q_cond_u_s: str
    q_cond_v_s: str
    q_cond_u_p: str
    q_cond_v_p: str
    q_group_s: str
    q_group_p: str


TEMPLATES: list[TemplateNutzung] = [
    TemplateNutzung(
        intro="Was halten Jugendliche von Lern-Apps? Dazu wurde eine Befragung unter Schülerinnen und Schülern durchgeführt.",
        stage1_text="Die Befragten wurden in drei Gruppen eingeteilt: Starter-Version (S), Pro-Version (P) und keine Nutzung (k).",
        stage2_text="Bei S und P wurde als Zweck unterschieden zwischen Unterhaltung (U) und Prüfungsvorbereitung (V).",
        chance_stat_tmpl=(
            "{p_su_pct} % der Befragten nutzen Starter-Versionen zur Unterhaltung, "
            "{p_sv_pct} % nutzen Starter-Versionen zur Prüfungsvorbereitung."
        ),
        abs_stat_tmpl=(
            "Insgesamt wurden {n_fmt} Personen befragt. "
            "{count_pv_fmt} nutzen Pro-Versionen zur Prüfungsvorbereitung, "
            "{count_k_fmt} haben bislang keine Lern-App genutzt."
        ),
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die App zur Unterhaltung nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die App zur Prüfungsvorbereitung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person aus der Starter-Gruppe die App zur Unterhaltung nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person aus der Starter-Gruppe die App zur Prüfungsvorbereitung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person aus der Pro-Gruppe die App zur Unterhaltung nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person aus der Pro-Gruppe die App zur Prüfungsvorbereitung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Wie werden digitale Lernplattformen genutzt? An einer Hochschule wurde dazu eine Umfrage durchgeführt.",
        stage1_text="Die Teilnehmenden wurden in drei Gruppen erfasst: Basis-Zugang (S), Premium-Zugang (P) und keine Nutzung (k).",
        stage2_text="Bei S und P wurde der Nutzungszweck unterschieden in Orientierung (U) und Klausurvorbereitung (V).",
        chance_stat_tmpl=(
            "{p_su_pct} % aller Teilnehmenden nutzen den Basis-Zugang zur Orientierung, "
            "{p_sv_pct} % nutzen ihn zur Klausurvorbereitung."
        ),
        abs_stat_tmpl=(
            "Insgesamt nahmen {n_fmt} Personen teil. "
            "{count_pv_fmt} nutzen den Premium-Zugang zur Klausurvorbereitung, "
            "{count_k_fmt} nutzen die Plattform bislang nicht."
        ),
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform zur Orientierung nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform zur Klausurvorbereitung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Basis-Zugang die Plattform zur Orientierung nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Basis-Zugang die Plattform zur Klausurvorbereitung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Premium-Zugang die Plattform zur Orientierung nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Premium-Zugang die Plattform zur Klausurvorbereitung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Basis-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Premium-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="In einem Sportverein wurde die Nutzung einer Trainings-App ausgewertet.",
        stage1_text="Die Mitglieder wurden in drei Gruppen eingeteilt: Starter-Abo (S), Pro-Abo (P) und keine Nutzung (k).",
        stage2_text="Für S und P wurde unterschieden, ob die App eher für Motivation (U) oder für gezielte Trainingsplanung (V) genutzt wird.",
        chance_stat_tmpl=(
            "{p_su_pct} % der Mitglieder nutzen das Starter-Abo für Motivation, "
            "{p_sv_pct} % nutzen es für gezielte Trainingsplanung."
        ),
        abs_stat_tmpl=(
            "Insgesamt wurden {n_fmt} Mitglieder berücksichtigt. "
            "{count_pv_fmt} nutzen das Pro-Abo für gezielte Trainingsplanung, "
            "{count_k_fmt} nutzen keine Trainings-App."
        ),
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Mitglied die App zur Motivation nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Mitglied die App zur gezielten Trainingsplanung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Mitglied mit Starter-Abo die App zur Motivation nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Mitglied mit Starter-Abo die App zur gezielten Trainingsplanung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Mitglied mit Pro-Abo die App zur Motivation nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Mitglied mit Pro-Abo die App zur gezielten Trainingsplanung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Mitglied zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Mitglied zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Eine Schule hat die Nutzung einer Sprachlern-App in den Fremdsprachenkursen erhoben.",
        stage1_text="Die Lernenden wurden in drei Gruppen eingeteilt: Starter-Account (S), Pro-Account (P) und keine Nutzung (k).",
        stage2_text="Bei den Accounts S und P wurde zwischen Wortschatztraining (U) und Prüfungsvorbereitung (V) unterschieden.",
        chance_stat_tmpl=(
            "{p_su_pct} % aller Lernenden nutzen den Starter-Account für Wortschatztraining, "
            "{p_sv_pct} % für Prüfungsvorbereitung."
        ),
        abs_stat_tmpl=(
            "Insgesamt wurden {n_fmt} Lernende erfasst. "
            "{count_pv_fmt} nutzen den Pro-Account für Prüfungsvorbereitung, "
            "{count_k_fmt} nutzen die App gar nicht."
        ),
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die App für Wortschatztraining nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die App zur Prüfungsvorbereitung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Account die App für Wortschatztraining nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Account die App zur Prüfungsvorbereitung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Account die App für Wortschatztraining nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Account die App zur Prüfungsvorbereitung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Für ein Mathe-Förderprogramm wurde die Nutzung einer Übungs-App untersucht.",
        stage1_text="Die Teilnehmenden wurden in drei Gruppen eingeteilt: Starter-Modus (S), Pro-Modus (P) und keine Nutzung (k).",
        stage2_text="Bei S und P wurde unterschieden zwischen Wiederholung (U) und gezielter Prüfungsvorbereitung (V).",
        chance_stat_tmpl=(
            "{p_su_pct} % der Teilnehmenden nutzen den Starter-Modus zur Wiederholung, "
            "{p_sv_pct} % zur gezielten Prüfungsvorbereitung."
        ),
        abs_stat_tmpl=(
            "Insgesamt umfasst die Erhebung {n_fmt} Teilnehmende. "
            "{count_pv_fmt} nutzen den Pro-Modus zur gezielten Prüfungsvorbereitung, "
            "{count_k_fmt} nutzen keine Übungs-App."
        ),
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die App zur Wiederholung nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die App zur gezielten Prüfungsvorbereitung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person im Starter-Modus die App zur Wiederholung nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person im Starter-Modus die App zur gezielten Prüfungsvorbereitung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person im Pro-Modus die App zur Wiederholung nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person im Pro-Modus die App zur gezielten Prüfungsvorbereitung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Streamingdienst hat das Nutzungsverhalten seiner Kundschaft ausgewertet.",
        stage1_text="Die Konten wurden in Starter-Abo (S), Premium-Abo (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Unterhaltung (U) und gezielter Informationsnutzung (V).",
        chance_stat_tmpl="{p_su_pct} % der Kundschaft nutzen das Starter-Abo zur Unterhaltung, {p_sv_pct} % zur Informationsnutzung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Konten betrachtet. {count_pv_fmt} nutzen Premium für Informationsnutzung, {count_k_fmt} nutzen den Dienst nicht aktiv.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Konto den Dienst zur Unterhaltung nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Konto den Dienst zur Informationsnutzung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Konto mit Starter-Abo den Dienst zur Unterhaltung nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Konto mit Starter-Abo den Dienst zur Informationsnutzung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Konto mit Premium-Abo den Dienst zur Unterhaltung nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Konto mit Premium-Abo den Dienst zur Informationsnutzung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Konto zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Konto zur Premium-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Verlag hat die Nutzung einer Nachrichtenplattform untersucht.",
        stage1_text="Die Lesenden wurden in Basis-Zugang (S), Plus-Zugang (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Überblick (U) und vertiefter Recherche (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen den Basis-Zugang für Überblick, {p_sv_pct} % für vertiefte Recherche.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Lesende erfasst. {count_pv_fmt} nutzen Plus für vertiefte Recherche, {count_k_fmt} nutzen die Plattform nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform für Überblick nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform für vertiefte Recherche nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Basis-Zugang die Plattform für Überblick nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Basis-Zugang die Plattform für vertiefte Recherche nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Plus-Zugang die Plattform für Überblick nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Plus-Zugang die Plattform für vertiefte Recherche nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Basis-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Plus-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Kulturhaus hat die Nutzung seines Ticketportals analysiert.",
        stage1_text="Die Nutzenden wurden in Starter-Status (S), Pro-Status (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Freizeitplanung (U) und gezielter Veranstaltungsplanung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen den Starter-Status zur Freizeitplanung, {p_sv_pct} % zur Veranstaltungsplanung.",
        abs_stat_tmpl="Insgesamt umfasste die Auswertung {n_fmt} Nutzende. {count_pv_fmt} nutzen Pro für Veranstaltungsplanung, {count_k_fmt} nutzen das Portal nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person das Portal zur Freizeitplanung nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person das Portal zur Veranstaltungsplanung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Status das Portal zur Freizeitplanung nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Status das Portal zur Veranstaltungsplanung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Status das Portal zur Freizeitplanung nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Status das Portal zur Veranstaltungsplanung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Eine Stadtverwaltung hat die Nutzung einer Bürger-App ausgewertet.",
        stage1_text="Die Accounts wurden in Starter-Konto (S), Pro-Konto (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Information (U) und konkreter Antragstellung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen Starter-Konten für Information, {p_sv_pct} % für Antragstellung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Accounts betrachtet. {count_pv_fmt} nutzen Pro-Konten zur Antragstellung, {count_k_fmt} nutzen die App nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die App für Information nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die App für Antragstellung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Konto die App für Information nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Konto die App für Antragstellung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Konto die App für Information nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Konto die App für Antragstellung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Reiseportal hat das Verhalten seiner registrierten Kundschaft analysiert.",
        stage1_text="Die Accounts wurden in Starter-Zugang (S), Premium-Zugang (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Inspiration (U) und konkreter Buchungsvorbereitung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen Starter-Zugänge zur Inspiration, {p_sv_pct} % zur Buchungsvorbereitung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Accounts ausgewertet. {count_pv_fmt} nutzen Premium zur Buchungsvorbereitung, {count_k_fmt} nutzen das Portal nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account das Portal zur Inspiration nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account das Portal zur Buchungsvorbereitung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Starter-Account das Portal zur Inspiration nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Starter-Account das Portal zur Buchungsvorbereitung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Premium-Account das Portal zur Inspiration nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Premium-Account das Portal zur Buchungsvorbereitung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account zur Premium-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Fitnessanbieter hat die Nutzung seiner Trainingsplattform erhoben.",
        stage1_text="Die Nutzenden wurden in Starter-Mitgliedschaft (S), Pro-Mitgliedschaft (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Motivationstraining (U) und Leistungsaufbau (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen Starter für Motivationstraining, {p_sv_pct} % für Leistungsaufbau.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Mitgliedschaften betrachtet. {count_pv_fmt} nutzen Pro für Leistungsaufbau, {count_k_fmt} nutzen die Plattform nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform für Motivationstraining nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform für Leistungsaufbau nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Mitgliedschaft die Plattform für Motivationstraining nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Mitgliedschaft die Plattform für Leistungsaufbau nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Mitgliedschaft die Plattform für Motivationstraining nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Mitgliedschaft die Plattform für Leistungsaufbau nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Musikdienst hat das Verhalten seiner Hörerschaft ausgewertet.",
        stage1_text="Die Zugänge wurden in Starter-Tarif (S), Pro-Tarif (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen gelegentlichem Hören (U) und gezieltem Entdecken neuer Inhalte (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen den Starter-Tarif für gelegentliches Hören, {p_sv_pct} % für gezieltes Entdecken.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Zugänge ausgewertet. {count_pv_fmt} nutzen den Pro-Tarif für gezieltes Entdecken, {count_k_fmt} nutzen den Dienst nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person den Dienst für gelegentliches Hören nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person den Dienst für gezieltes Entdecken nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Tarif den Dienst für gelegentliches Hören nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Tarif den Dienst für gezieltes Entdecken nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Tarif den Dienst für gelegentliches Hören nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Tarif den Dienst für gezieltes Entdecken nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Weiterbildungsinstitut hat die Nutzung seiner Lernplattform untersucht.",
        stage1_text="Die Lernenden wurden in Starter-Zugang (S), Pro-Zugang (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Orientierung (U) und gezielter Zertifikatsvorbereitung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen Starter zur Orientierung, {p_sv_pct} % zur Zertifikatsvorbereitung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Lernende erfasst. {count_pv_fmt} nutzen Pro zur Zertifikatsvorbereitung, {count_k_fmt} nutzen die Plattform nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform zur Orientierung nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform zur Zertifikatsvorbereitung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Zugang die Plattform zur Orientierung nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Zugang die Plattform zur Zertifikatsvorbereitung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Zugang die Plattform zur Orientierung nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Zugang die Plattform zur Zertifikatsvorbereitung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Finanzportal hat die Nutzung seiner Wissensangebote ausgewertet.",
        stage1_text="Die Profile wurden in Starter-Paket (S), Pro-Paket (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Marktüberblick (U) und strategischer Planung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen das Starter-Paket für Marktüberblick, {p_sv_pct} % für strategische Planung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Profile ausgewertet. {count_pv_fmt} nutzen Pro für strategische Planung, {count_k_fmt} nutzen das Portal nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person das Portal für Marktüberblick nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person das Portal für strategische Planung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Paket das Portal für Marktüberblick nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Paket das Portal für strategische Planung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Paket das Portal für Marktüberblick nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Paket das Portal für strategische Planung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Museumsverbund hat die Nutzung seines digitalen Guides analysiert.",
        stage1_text="Die Zugänge wurden in Starter-Lizenz (S), Pro-Lizenz (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen allgemeiner Orientierung (U) und vertiefter Themenrecherche (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen die Starter-Lizenz zur Orientierung, {p_sv_pct} % zur Themenrecherche.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Zugänge erfasst. {count_pv_fmt} nutzen die Pro-Lizenz zur Themenrecherche, {count_k_fmt} nutzen den Guide nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person den Guide zur Orientierung nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person den Guide zur Themenrecherche nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Lizenz den Guide zur Orientierung nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Lizenz den Guide zur Themenrecherche nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Lizenz den Guide zur Orientierung nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Lizenz den Guide zur Themenrecherche nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Eine Wohlfahrtsorganisation hat die Nutzung ihres Helferportals erhoben.",
        stage1_text="Die Profile wurden in Starter-Zugang (S), Pro-Zugang (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Informationssuche (U) und konkreter Einsatzplanung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen Starter zur Informationssuche, {p_sv_pct} % zur Einsatzplanung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Profile erfasst. {count_pv_fmt} nutzen Pro zur Einsatzplanung, {count_k_fmt} nutzen das Portal nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person das Portal zur Informationssuche nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person das Portal zur Einsatzplanung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Zugang das Portal zur Informationssuche nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Zugang das Portal zur Einsatzplanung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Zugang das Portal zur Informationssuche nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Zugang das Portal zur Einsatzplanung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Verkehrsverbund hat die Nutzung seiner Mobilitäts-App ausgewertet.",
        stage1_text="Die Accounts wurden in Starter-Tarif (S), Pro-Tarif (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen spontaner Fahrtauskunft (U) und geplanter Pendeloptimierung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen Starter für spontane Fahrtauskunft, {p_sv_pct} % für Pendeloptimierung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Accounts ausgewertet. {count_pv_fmt} nutzen Pro für Pendeloptimierung, {count_k_fmt} nutzen die App nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account die App für spontane Fahrtauskunft nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account die App für Pendeloptimierung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Starter-Account die App für spontane Fahrtauskunft nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Starter-Account die App für Pendeloptimierung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Pro-Account die App für spontane Fahrtauskunft nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Pro-Account die App für Pendeloptimierung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Gesundheitsdienst hat die Nutzung seines Präventionsportals untersucht.",
        stage1_text="Die Nutzenden wurden in Starter-Zugang (S), Pro-Zugang (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen allgemeiner Information (U) und individueller Vorsorgeplanung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen Starter für allgemeine Information, {p_sv_pct} % für Vorsorgeplanung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Nutzende erfasst. {count_pv_fmt} nutzen Pro für Vorsorgeplanung, {count_k_fmt} nutzen das Portal nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person das Portal für allgemeine Information nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person das Portal für Vorsorgeplanung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Zugang das Portal für allgemeine Information nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Zugang das Portal für Vorsorgeplanung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Zugang das Portal für allgemeine Information nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Zugang das Portal für Vorsorgeplanung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Hochschulsportzentrum hat die Nutzung seiner Kursplattform analysiert.",
        stage1_text="Die Accounts wurden in Starter-Status (S), Pro-Status (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen freier Kurssuche (U) und strukturierter Trainingsplanung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen Starter für freie Kurssuche, {p_sv_pct} % für Trainingsplanung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Accounts betrachtet. {count_pv_fmt} nutzen Pro für Trainingsplanung, {count_k_fmt} nutzen die Plattform nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform für freie Kurssuche nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform für Trainingsplanung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Status die Plattform für freie Kurssuche nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Status die Plattform für Trainingsplanung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Status die Plattform für freie Kurssuche nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Status die Plattform für Trainingsplanung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Berufsnetzwerk hat die Nutzung seiner Karrierefunktionen ausgewertet.",
        stage1_text="Die Profile wurden in Starter-Paket (S), Pro-Paket (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen allgemeiner Orientierung (U) und gezielter Bewerbungsvorbereitung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen das Starter-Paket zur Orientierung, {p_sv_pct} % zur Bewerbungsvorbereitung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Profile analysiert. {count_pv_fmt} nutzen Pro zur Bewerbungsvorbereitung, {count_k_fmt} nutzen die Funktionen nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform zur Orientierung nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person die Plattform zur Bewerbungsvorbereitung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Paket die Plattform zur Orientierung nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Starter-Paket die Plattform zur Bewerbungsvorbereitung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Paket die Plattform zur Orientierung nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine Person mit Pro-Paket die Plattform zur Bewerbungsvorbereitung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass eine zufällig ausgewählte Person zur Pro-Gruppe gehört.",
    ),
    TemplateNutzung(
        intro="Ein Online-Shop hat die Nutzung seines Beratungsbereichs ausgewertet.",
        stage1_text="Die Accounts wurden in Starter-Zugang (S), Pro-Zugang (P) und keine Nutzung (k) eingeteilt.",
        stage2_text="Bei S und P wurde unterschieden zwischen Orientierung beim Sortiment (U) und gezielter Kaufvorbereitung (V).",
        chance_stat_tmpl="{p_su_pct} % nutzen Starter zur Sortimentsorientierung, {p_sv_pct} % zur Kaufvorbereitung.",
        abs_stat_tmpl="Insgesamt wurden {n_fmt} Accounts betrachtet. {count_pv_fmt} nutzen Pro zur Kaufvorbereitung, {count_k_fmt} nutzen den Beratungsbereich nicht.",
        q_total_u="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account den Bereich zur Sortimentsorientierung nutzt.",
        q_total_v="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account den Bereich zur Kaufvorbereitung nutzt.",
        q_cond_u_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Starter-Account den Bereich zur Sortimentsorientierung nutzt.",
        q_cond_v_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein Starter-Account den Bereich zur Kaufvorbereitung nutzt.",
        q_cond_u_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Pro-Account den Bereich zur Sortimentsorientierung nutzt.",
        q_cond_v_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein Pro-Account den Bereich zur Kaufvorbereitung nutzt.",
        q_group_s="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account zur Starter-Gruppe gehört.",
        q_group_p="Bestimmen Sie die Wahrscheinlichkeit, dass ein zufällig ausgewählter Account zur Pro-Gruppe gehört.",
    ),
]


@dataclass(frozen=True)
class CaseNutzung:
    total_n: int
    count_su: int
    count_sv: int
    count_pu: int
    count_pv: int
    count_k: int



def _sample_case(rng: random.Random) -> CaseNutzung | None:
    total_n = rng.choice([2000, 4000, 5000, 8000, 10000, 20000])

    # Start mit sinnvollen Bereichen fuer den Beispieltyp.
    p_su = Decimal(rng.randint(18, 45)) / Decimal(100)   # 0.18 .. 0.45
    p_sv = Decimal(rng.randint(8, 28)) / Decimal(100)    # 0.08 .. 0.28
    p_k = Decimal(rng.randint(8, 30)) / Decimal(100)     # 0.08 .. 0.30
    p_pv = Decimal(rng.randint(4, 22)) / Decimal(100)    # 0.04 .. 0.22

    p_sum = p_su + p_sv + p_k + p_pv
    if p_sum >= Decimal("0.95"):
        return None

    p_pu = Decimal("1") - p_sum

    # Pro-Gruppe nicht zu klein und Konditionalwerte nicht extrem.
    p_p = p_pu + p_pv
    if not (Decimal("0.08") <= p_p <= Decimal("0.50")):
        return None

    p_u_given_p = p_pu / p_p
    p_v_given_p = p_pv / p_p
    if not (Decimal("0.10") <= p_u_given_p <= Decimal("0.90")):
        return None
    if not (Decimal("0.10") <= p_v_given_p <= Decimal("0.90")):
        return None

    # Integer-Konsistenz ueber Restverteilung sicherstellen.
    count_su = int((Decimal(total_n) * p_su).to_integral_value(rounding=ROUND_HALF_UP))
    count_sv = int((Decimal(total_n) * p_sv).to_integral_value(rounding=ROUND_HALF_UP))
    count_k = int((Decimal(total_n) * p_k).to_integral_value(rounding=ROUND_HALF_UP))
    count_pv = int((Decimal(total_n) * p_pv).to_integral_value(rounding=ROUND_HALF_UP))

    count_used = count_su + count_sv + count_k + count_pv
    if count_used >= total_n:
        return None

    count_pu = total_n - count_used

    # Endgueltige Sicherheitschecks.
    if min(count_su, count_sv, count_pu, count_pv, count_k) <= 0:
        return None

    return CaseNutzung(
        total_n=total_n,
        count_su=count_su,
        count_sv=count_sv,
        count_pu=count_pu,
        count_pv=count_pv,
        count_k=count_k,
    )



def _sample_case_retry(rng: random.Random, max_tries: int = 200) -> CaseNutzung:
    for _ in range(max_tries):
        case = _sample_case(rng)
        if case is not None:
            return case
    raise RuntimeError("Konnte keinen gültigen Fall für baumdiagramm_komplex_nutzung_3kat erzeugen.")



def _intro_text(tmpl: TemplateNutzung, case: CaseNutzung) -> str:
    n = Decimal(case.total_n)
    p_su = _f(_r4(Decimal(case.count_su) / n))
    p_sv = _f(_r4(Decimal(case.count_sv) / n))

    chance_stat = tmpl.chance_stat_tmpl.format(
        p_su_pct=_pct1(p_su),
        p_sv_pct=_pct1(p_sv),
    )
    abs_stat = tmpl.abs_stat_tmpl.format(
        n_fmt=_fmt_int(case.total_n),
        count_pv_fmt=_fmt_int(case.count_pv),
        count_k_fmt=_fmt_int(case.count_k),
    )

    hint = "Für die folgenden Fragen ist es sinnvoll, das Baumdiagramm zuerst vollständig auszufüllen."

    return (
        f"{tmpl.intro} "
        f"{tmpl.stage1_text} "
        f"{tmpl.stage2_text} "
        f"{chance_stat} "
        f"{abs_stat} "
        f"{hint}"
    )


class MethodenBaumdiagrammKomplexNutzung3KatGenerator(TaskGenerator):
    generator_key = "stochastik.mehrstufige_zufallsexperimente.baumdiagramm_komplex_nutzung_3kat"

    def generate(self, count: int, seed: int | None = None) -> list[Task]:
        rng = random.Random(seed)
        tasks: list[Task] = []

        for i in range(count):
            tmpl = TEMPLATES[i % len(TEMPLATES)]
            case = _sample_case_retry(rng)

            n = Decimal(case.total_n)
            p_su = _r4(Decimal(case.count_su) / n)
            p_sv = _r4(Decimal(case.count_sv) / n)
            p_pu = _r4(Decimal(case.count_pu) / n)
            p_pv = _r4(Decimal(case.count_pv) / n)
            p_k = _r4(Decimal(case.count_k) / n)

            p_s = _r4(p_su + p_sv)
            p_p = _r4(p_pu + p_pv)
            p_u = _r4(p_su + p_pu)
            p_v = _r4(p_sv + p_pv)

            p_u_given_s = _r4(p_su / p_s)
            p_v_given_s = _r4(p_sv / p_s)
            p_u_given_p = _r4(p_pu / p_p)
            p_v_given_p = _r4(p_pv / p_p)

            q1_use_u = rng.choice([True, False])
            q2_kind = rng.choice(["u_s", "v_s", "u_p", "v_p"])
            q3_use_p = rng.choice([True, False])

            q1 = tmpl.q_total_u if q1_use_u else tmpl.q_total_v
            if q2_kind == "u_s":
                q2 = tmpl.q_cond_u_s
                a2 = p_u_given_s
            elif q2_kind == "v_s":
                q2 = tmpl.q_cond_v_s
                a2 = p_v_given_s
            elif q2_kind == "u_p":
                q2 = tmpl.q_cond_u_p
                a2 = p_u_given_p
            else:
                q2 = tmpl.q_cond_v_p
                a2 = p_v_given_p

            q3 = tmpl.q_group_p if q3_use_p else tmpl.q_group_s
            a3 = p_p if q3_use_p else p_s

            tasks.append(
                Task(
                    einleitung=_intro_text(tmpl, case),
                    fragen=[q1, q2, q3],
                    antworten=[
                        numerical(_f(p_u if q1_use_u else p_v), tolerance=0.001, decimals=4),
                        numerical(_f(a2), tolerance=0.001, decimals=4),
                        numerical(_f(a3), tolerance=0.001, decimals=4),
                    ],
                )
            )

        return tasks

