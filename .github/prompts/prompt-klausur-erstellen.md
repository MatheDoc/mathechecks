---
description: Klausur aus Themen, Lernbereichen/Checks und Musterprüfungen gemäß config.yml erzeugen
---

# Prompt: Klausur erstellen

Eingabe: `klausuren/<slug>/config.yml` (ohne Pfadangabe die aktuell geöffnete; nicht `klausuren/templates/config.yml`). Regeln: `.github/prompts/systemprompt-klausur.prompt.md`.

`themen`, `checks` und `hinweise` sind jeweils optional und dienen als Orientierung (siehe Systemprompt, Abschnitt 0). Nur wenn keines davon angegeben ist, nachfragen.

Musterprüfungen liegen in `muster-pruefungen/abitur/pruefungen-md/` (gitignored → Dateien direkt per Pfad lesen, Such-Tools überspringen den Ordner oft). Fehlt der Ordner, entfallen die Schritte mit Musterprüfungen.

## Schritte

1. **Themen bestimmen:** `themen` ∪ Lernbereiche aus `checks`. Je Thema in `_data/themen.yml` nachsehen und feststellen, ob es ein Lernbereich ist (gleicher Slug in `_data/lernbereiche.yml`).
2. **Plattform-Material** je umgesetztem Thema:
   - `lernbereiche/<gebiet>/<lernbereich>/skript.md` → Notation, Methoden
   - bei angegebenen `checks`: `checks.json` → `Ich kann`, `Tipps`, `Sammlung`; `beispiele/<NN>-<Sammlung>.md` → Rechenweg, Zahlenniveau
   - nur falls kein Beispiel existiert: Stichprobe aus `aufgaben/exports/json/<gebiet>/<lernbereich>/<Sammlung>.json`
3. **Musterprüfungen laden:**
   - **Themen-Treffer:** in `pruefungen-md/_themen.json` je Thema die `teilaufgaben` nachschlagen; bevorzugt gleiche `schulform`/`fachrichtung`/`niveau` wie der Kurs, bei vielen Treffern über Jahrgänge streuen. Aus der jeweiligen `datei` die Teilaufgabe inkl. Aufgabeneinleitung und Erwartungshorizont lesen.
   - **In `hinweise` gezielt genannte Musteraufgaben** (Aufgabe-`id`, ggf. Teilaufgaben-Label): Datei über `_themen.json` (Feld `datei`) oder `_inventar.json` (`pfad` → `_index.md` → `aufgaben[].datei`) finden; übergeordnetes Label wie `2.1` umfasst `2.1.1`, `2.1.2`, …
   - **Stilreferenz (immer):** Reichen die Treffer oben nicht, zusätzlich 1–2 Aufgaben aus `_inventar.json` mit `status: vollstaendig`, bevorzugt gleiche Schulform/Fachrichtung.
4. **Planen:** Leitszenario festlegen (neu, kein Szenario aus Musterprüfungen); aus Themen, Checks und Hinweisen eine sinnvolle Auswahl treffen und zu Aufgaben mit Einleitungstext und aufeinander aufbauenden Teilaufgaben verweben; Granularität und Punkteverteilung an den Musterprüfungen orientieren; Reihenfolge festlegen.
5. **Schreiben:** `klausuren/<slug>/klausur.md` (ggf. Diagramm-Skript + PNGs im selben Ordner).
6. **Prüfen:** alle Lösungen nachrechnen (bei Bedarf per Python), Ergebnisse handhabbar? Jede Teilaufgabe unabhängig von den vorherigen lösbar (Querverweise „aus a)" auf Angaben prüfen, nötige Zwischenergebnisse nennen)? Kontextbezug in Teilaufgaben? Keine Doppelabfragen? Kein Szenario aus einer Musterprüfung übernommen?
7. **Exportieren:** PDF-Export der fertigen Klausur über `klausuren/export-pdf.ps1 klausuren/<slug>/klausur.md`.

## Ausgabe an den Nutzer

- Zuordnung Thema / Check / Hinweis → Aufgabe/Teilaufgabe; nicht aufgegriffene Angaben und bewusste Abweichungen kurz begründen; fehlende Quelldaten
- Themen ohne Lernbereich (Notation aus Musterprüfungen → bitte prüfen)
- genutzte Musterprüfungs-Teilaufgaben (Aufgabe-`id` + Label)
- Hinweis auf PDF-Export: `klausuren/export-pdf.ps1 klausuren/<slug>/klausur.md`
