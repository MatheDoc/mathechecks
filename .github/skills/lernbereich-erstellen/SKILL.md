---
name: lernbereich-erstellen
description: Lernbereich neu anlegen, vollständig überarbeiten oder gezielt ändern (Checks, Skript, Beispiele, Aufgaben, Test) mit Abgleich gegen die Abitur-Musterprüfungen.
disable-model-invocation: true
---
# Lernbereich erstellen oder überarbeiten

Eingabe: Lernbereich-Slug und Auftrag.

- **Vollständig** (Neuanlage, wenn der Slug noch nicht in `_data/lernbereiche.yml` steht, sonst Überarbeitung): Abschnitte 1–4.
- **Gezielt** (eine konkrete Stelle): Abschnitt „Gezielte Änderung“.

Verbindlich: `.github/inhalte.md` (Ziele), `.github/datenmodell.md` (Ablage), `.github/glossary.md` (LaTeX).

## 1. Bestand und Abitur sichten

- Überarbeitung: Checks, `skript.md`, Beispiele, je eine Stichprobe aus jeder Aufgabensammlung und die Tests lesen.
- Abitur: alle Teilaufgaben zum Slug aus `_themen.json` samt Erwartungshorizont lesen.
- Prüfen, ob passende Teilaufgaben ungetaggt sind. Dann `themen` im Frontmatter der Prüfungsdatei ergänzen und `_themen.json` über `muster-pruefungen/abitur/pruefungen/schema/validate_frontmatter.py` neu erzeugen.

## 2. Abgleich vorlegen (im Chat, vor dem Umsetzen)

- Tabelle: Aufgabentyp im Abitur | Fundstellen | abdeckender Check (vorhanden / fehlt / anderes Thema).
- Vorschlag zur Check-Einteilung und zu Widgets, dazu gefundene fachliche Fehler.
- Änderungen am Zuschnitt der Checks oder an `check_id`s erst nach Zustimmung umsetzen. Klare Rechenfehler sofort korrigieren.

## 3. Umsetzen

| Was | Datei |
|---|---|
| Thema und Lernbereich (nur bei Neuanlage) | `_data/themen.yml`, `_data/lernbereiche.yml`; Modulseiten aus einem bestehenden Lernbereich kopieren und das Front Matter anpassen |
| Checks und Tipps | `_data/checks.json` |
| Skript | `lernbereiche/<gebiet>/<lb>/skript.md` |
| Beispiele | `lernbereiche/<gebiet>/<lb>/beispiele/<NN>-<sammlung>.md` |
| Aufgaben | Generator und Job in `aufgaben/project_config.json` (→ `agent-python-aufgaben`), dann `python aufgaben/run.py <lb>` |
| Test | `test/<gebiet>/<lb>/<check_id>.json`, dann `python moodle/test_to_moodle.py` |
| Startseite | `_data/start/<lb>.yml` |
| Widget | → `agent-frontend-ux`, Technik in `.github/widgets.md` |

Bei gelöschten oder umbenannten Sammlungen und Checks die verwaisten Exporte, Beispiele, Tests und Moodle-Dateien entfernen bzw. umbenennen.

## 4. Prüfen

Abschnitt „Fertig, wenn“ in `.github/inhalte.md`.

## Gezielte Änderung

1. Die Stelle und die betroffenen Checks lesen.
2. Ändern. Rückfragen und Sofortkorrekturen wie in Abschnitt 2.
3. Konsistenz der betroffenen Checks prüfen: `Ich kann` und Tipps, Skript-Abschnitt, Beispiel, Aufgabensammlung, Test, ggf. Warm-Up. Abweichungen mitändern oder als offenen Punkt melden.
4. Nur die Punkte aus „Fertig, wenn“ prüfen, die die geänderten Dateien betreffen.

## Ausgabe

- Abgleichtabelle (final) und Check-Liste (nur vollständig)
- geänderte Dateien, korrigierte Fehler
- Folgen für Nutzerfortschritt bei geänderten `check_id`s, offene Punkte (z. B. Podcast)
