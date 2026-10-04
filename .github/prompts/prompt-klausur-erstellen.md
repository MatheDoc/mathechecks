---
description: Klausur aus Lernbereichen/Checks und Musterprüfungen gemäß config.yml erzeugen
---

# Prompt: Klausur erstellen

Eingabe: `klausuren/<slug>/config.yml` (ohne Pfadangabe die aktuell geöffnete; nicht `klausuren/templates/config.yml`). Regeln: `.github/prompts/systemprompt-klausur.prompt.md`.

`checks`, `vorlagen` und `hinweise` sind jeweils optional und dienen als Orientierung (siehe Systemprompt, Abschnitt 0). Nur wenn keines davon angegeben ist, nachfragen.

## Schritte

1. **Material sammeln** je Check aus `config.yml` (falls angegeben):
   - `checks.json` → `Ich kann`, `Tipps`, `Sammlung`
   - `lernbereiche/<gebiet>/<lernbereich>/beispiele/<NN>-<Sammlung>.md` → Notation, Rechenweg, Zahlenniveau
   - nur falls kein Beispiel existiert: Stichprobe aus `aufgaben/exports/json/<gebiet>/<lernbereich>/<Sammlung>.json`
2. **Musterprüfungen laden** (entfällt, wenn `muster-pruefungen/` fehlt; Ordner ist gitignored → Dateien direkt per Pfad lesen, Such-Tools überspringen ihn oft):
   - **`vorlagen`:** Aufgabe-`id` auflösen: in `muster-pruefungen/abitur/pruefungen-md/_inventar.json` den Eintrag suchen, dessen `id` Präfix der Aufgabe-`id` ist → `pfad` → `_index.md` → `aufgaben[].datei`. Aus der Aufgabe-Datei nur die genannten `teilaufgaben` (Labels = `teilaufgaben[].bezeichnung`; übergeordnetes Label wie `2.1` umfasst `2.1.1`, `2.1.2`, …) inkl. zugehöriger Einleitung und Erwartungshorizont verwenden.
   - **Stilreferenz (immer):** zusätzlich 1–2 Aufgaben aus `_inventar.json` mit `status: vollstaendig`, bevorzugt gleiche Schulform/Fachrichtung wie der Kurs und passender Themenbereich (siehe Tabelle in `_index.md`).
3. **Planen:** Leitszenario festlegen (neu, kein Szenario aus Musterprüfungen); aus Checks, Vorlagen und Hinweisen eine sinnvolle Auswahl treffen und zu Aufgaben mit Einleitungstext und aufeinander aufbauenden Teilaufgaben verweben; Granularität und Punkteverteilung an den Musterprüfungen orientieren; Reihenfolge festlegen.
4. **Schreiben:** `klausuren/<slug>/klausur.md` (ggf. Diagramm-Skript + PNGs im selben Ordner).
5. **Prüfen:** alle Lösungen nachrechnen (bei Bedarf per Python), Ergebnisse handhabbar? Kontextbezug in Teilaufgaben? Keine Doppelabfragen? Kein Szenario aus einer Musterprüfung übernommen?

## Ausgabe an den Nutzer

- Zuordnung Check / Vorlage / Hinweis → Aufgabe/Teilaufgabe; nicht aufgegriffene Angaben und bewusste Abweichungen kurz begründen; fehlende Quelldaten
- verwendete Stilreferenzen (Aufgabe-`id`s)
- Hinweis auf PDF-Export: `klausuren/export-pdf.ps1 klausuren/<slug>/klausur.md`
