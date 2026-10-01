---
description: Klausur aus Lernbereichen/Checks gemäß config.yml erzeugen
---

# Prompt: Klausur erstellen

## Ziel

Erzeuge aus einer `config.yml` eine vollständige Klausur `klausur.md` im Zielformat von `klausuren/templates/template.md`.

## Eingabe

- Config-Datei: `klausuren/<slug>/config.yml`
- Wenn kein Pfad genannt ist, arbeite mit der aktuell geöffneten `config.yml`.

## Arbeitsschritte

- Lies `config.yml`: Klausurmetadaten (`fach`, `klasse`, `datum`, `thema`, `bearbeitungszeit`, `geplante_punkte`) sowie die Liste aus `lernbereich` + `checks` (Nummern).
- Löse für jede Check-Nummer je Lernbereich den passenden Eintrag in `checks.json` auf (`Ich kann`, `Tipps`, `Sammlung`, `Schlagwort`).
- Lies je Check das zugehörige Beispiel: `lernbereiche/<gebiet>/<lernbereich>/beispiele/<NN>-<Sammlung>.md` (Rechenweg-Stil, Notation).
- Lies je Check mindestens eine Aufgabe aus `aufgaben/exports/json/<gebiet>/<lernbereich>/<Sammlung>.json` stichprobenartig (Zahlen-/Szenariostil zur Kalibrierung, nicht kopieren).
- Prüfe, ob die ausgewählten Lernbereiche ein durchgängiges Anwendungssetting teilen (z. B. immer Kosten/Erlös/Gewinn/Preis); lege in diesem Fall ein einheitliches Leitszenario fest, das in den Anwendungsaufgaben der Klausur konsistent verwendet wird (einzelne rein innermathematische Aufgaben ausgenommen).
- Entwirf Klausuraufgaben, die alle ausgewählten Checks abdecken; mehrere Checks dürfen in einer Aufgabe mit mehreren Teilaufgaben kombiniert werden.
- Ordne die Aufgaben primär nach Taschenrechner-Eignung (Ablese-/einfache Rechenaufgaben zuerst, rechenintensive Aufgaben zuletzt) und prüfe, dass keine zwei Teilaufgaben im selben Sachkontext dieselbe Größe doppelt erfragen.
- Formatiere nach `.github/prompts/systemprompt-klausur.prompt.md` und schreibe das Ergebnis nach `klausuren/<slug>/klausur.md` (gleicher Ordner wie die `config.yml`).

## Ausgabe

- Datei `klausuren/<slug>/klausur.md`.
- Kurze Zusammenfassung: abgedeckte Lernbereiche/Checks, evtl. fehlende Quelldaten (z. B. kein Beispiel vorhanden).
- Hinweis an den Nutzer, dass das PDF bei Bedarf mit `klausuren/export-pdf.ps1 klausuren/<slug>/klausur.md` erzeugt werden kann.

Es gelten die Prioritäten aus `agent-klausuren` sowie die Regeln aus `systemprompt-klausur.prompt.md`.
