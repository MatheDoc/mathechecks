---
description: Klausur aus Themen, Lernbereichen/Checks und Musterprüfungen gemäß config.yml erzeugen
---

# Prompt: Klausur erstellen

Eingabe: `klausuren/<slug>/config.yml` (ohne Pfadangabe die aktuell geöffnete; nicht `klausuren/templates/config.yml`). Regeln und Gewichtung der Quellen: `.github/prompts/systemprompt-klausur.prompt.md`. Nur nachfragen, wenn weder `themen` noch `checks` noch `hinweise` angegeben sind oder Angaben sich widersprechen.

Musterprüfungen liegen in `muster-pruefungen/abitur/pruefungen-md/` (gitignored → Dateien direkt per Pfad lesen, Such-Tools überspringen den Ordner oft).

## Schritte

1. **Themen bestimmen:** `themen` ∪ Lernbereiche aus `checks`; je Thema prüfen, ob es einen Lernbereich gibt (`_data/lernbereiche.yml`).
2. **Musterprüfungen laden (primär):**
   - In `_themen.json` je Thema die `teilaufgaben` nachschlagen; bevorzugt gleiche `schulform`/`fachrichtung`/`niveau` wie der Kurs, bei vielen Treffern über Jahrgänge streuen. Aus der `datei` die Teilaufgabe inkl. Aufgabeneinleitung und Erwartungshorizont lesen.
   - In `hinweise` genannte Musteraufgaben (Aufgabe-`id`, ggf. Label): Datei über `_themen.json` (`datei`) oder `_inventar.json` (`pfad` → `_index.md` → `aufgaben[].datei`); ein Label wie `2.1` umfasst `2.1.1`, `2.1.2`, …
   - Reichen die Treffer nicht als Stilreferenz, 1–2 Aufgaben mit `status: vollstaendig` aus `_inventar.json` ergänzen.
3. **Plattform-Material (sekundär)** je umgesetztem Thema: `skript.md` (Notation); bei angegebenen `checks` zusätzlich `checks.json` (`Ich kann`, `Tipps`, `Sammlung`) und `beispiele/<NN>-<Sammlung>.md`, nur falls kein Beispiel existiert eine Stichprobe aus `aufgaben/exports/json/<gebiet>/<lernbereich>/<Sammlung>.json`.
4. **Planen:** Von den Musterprüfungs-Teilaufgaben ausgehen und mit `hinweise` und `checks` abgleichen; je übernommener Idee entscheiden: Standardaufgabe oder ungewöhnliche Idee (→ abwandeln/ersetzen, Systemprompt Abschnitt 2). Leitszenario festlegen, Aufgaben mit Einleitungstext und Teilaufgaben-Kette sowie Reihenfolge planen.
5. **Schreiben:** `klausuren/<slug>/klausur.md` (ggf. Diagramm-Skript + PNGs im selben Ordner).
6. **Prüfen:** Lösungen nachrechnen (bei Bedarf per Python) und Systemprompt Abschnitte 2–5 abhaken, insbesondere: Teilaufgaben unabhängig lösbar, kein Szenario/Wert aus Musterprüfungen, ungewöhnliche Ideen nicht 1:1 wiederholt.
7. **Exportieren:** `klausuren/export-pdf.ps1 klausuren/<slug>/klausur.md`.

## Ausgabe an den Nutzer

- Zuordnung Hinweis / Musterprüfungs-Teilaufgabe (Aufgabe-`id` + Label) / Thema / Check → Aufgabe/Teilaufgabe; bei ungewöhnlichen Vorlagen kurz die Abwandlung nennen
- nicht aufgegriffene Angaben und bewusste Abweichungen kurz begründen; fehlende Quelldaten
- Themen ohne Lernbereich (Notation aus Musterprüfungen → bitte prüfen)
- Pfad der erzeugten PDF
