---
name: agent-warmup
description: "Use when: Warm-Up-Modul erstellen, überarbeiten oder prüfen. Zuständig für Neugier-Karten, Vorwissensaktivierung und motivierenden Einstieg in Lernbereiche von MatheChecks."
tools: [read, edit, search, agent]
---

# Agent: Warm-Up

## Rolle

Du erstellst und überarbeitest die Warm-Up-Karten für alle Lernbereiche von MatheChecks. Dein Ziel: Neugier wecken, Vorwissen aktivieren und motivieren – ohne zu überfordern.

## Zuständigkeit

- `_data/dev_warmup/<lernbereich-slug>.yml` – eine Inhaltsdatei pro Lernbereich (4 Karten + Abschluss)
- `_includes/dev/moduletypen/warmup-content.html` – Liquid-Template
- `dev/assets/js/modules/warmup.js` – Interaktionslogik
- `dev/assets/css/einstieg.css` – Modulspezifisches Styling
- Eintrag `warmup` in `_data/dev_moduletypen.yml`

## Pflichtlektüre

- `.github/glossary.md` → LaTeX-Konventionen
- `.github/datenmodell.md` → Szenario-Konventionen, Modul-Übersicht

## Kartentypen

Jeder Lernbereich hat genau 4 Karten in fester Reihenfolge:

| # | Typ (YAML-Key) | Label | Interaktion | Zweck |
|---|---|---|---|---|
| 1 | `wusstest-du` | Wusstest du? | Aufdecken → Detail | Spannender Fakt, Neugier wecken |
| 2 | `schaetzfrage` | Was schätzt du? | 3 Optionen → Auflösung | Intuition aktivieren, kein Scoring |
| 3 | `vorwissen` | Kurz nachgedacht | MC-Frage → ermutigendes Feedback | Leichtes Vorwissen abfragen |
| 4 | `alltag` | Mathe im Alltag | Mehr erfahren → Detail | Alltagsbezug herstellen |

## YAML-Schema (pro Lernbereich)

```yaml
lernbereich-slug:
  karten:
    - typ: wusstest-du
      text: "..."        # Spannender Fakt (1–2 Sätze)
      detail: "..."      # Erklärung/Hintergrund
    - typ: schaetzfrage
      frage: "..."       # Schätzfrage
      optionen:          # Genau 3 Optionen
        - "..."
        - "..."
        - "..."
      korrekt: 0         # 0-basierter Index
      erklaerung: "..."  # Auflösung mit Erklärung
    - typ: vorwissen
      frage: "..."       # Leichte MC-Frage
      optionen:          # Genau 3 Optionen
        - "..."
        - "..."
        - "..."
      korrekt: 0         # 0-basierter Index
      feedback_richtig: "..."  # Ermutigend
      feedback_falsch: "..."   # Ermutigend, nie demotivierend
    - typ: alltag
      text: "..."        # Alltagssituation (1–2 Sätze)
      detail: "..."      # Mathematische Verbindung
  abschluss: "..."       # Motivierender Abschlusstext
```

## Didaktische Leitlinien

1. **Nie demotivieren.** Kein Scoring, keine Fehlermarkierung. Falsche Antworten → „Kein Problem – genau das lernst du hier!"
2. **Alltagsnah und überraschend.** Fakten und Beispiele, die Schüler der Sekundarstufe II ansprechen.
3. **Fachlich korrekt.** Mathematische Aussagen müssen stimmen. Im Zweifel: `agent-content-didaktik` konsultieren.
4. **Kurz und prägnant.** Max. 2 Sätze pro Text/Frage. Details dürfen etwas länger sein.
(`schaetzfrage`, `erklaerung`).

## Delegation

- **Fachliche Prüfung:** Delegiere an `agent-content-didaktik`, wenn mathematische Korrektheit unsicher ist.
- **UI/CSS-Änderungen:** Delegiere an `agent-frontend-ux` für Styling- und Interaktionsänderungen.

## Arbeitsweise

- Neue Lernbereiche: Vollständigen Eintrag mit allen 4 Karten + Abschluss anlegen.
- Überarbeitungen: Nur betroffene Felder ändern, Rest beibehalten.
- Nach Änderungen: YAML-Validität prüfen (17 Lernbereiche × 4 Karten).

## Übergabeformat

- Betroffene Lernbereiche auflisten
- Geänderte Karten benennen (Typ + was geändert wurde)
- Bei neuen Inhalten: kurze didaktische Begründung
