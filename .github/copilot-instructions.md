# MatheChecks – Copilot Instructions

## Projektkontext
Jekyll-Lernplattform für Mathematik (Sekundarstufe II).

Mathematische Aussagen müssen fachlich korrekt und konsistent sein.

Sprache: Deutsch  
Priorität: fachliche Korrektheit vor Stil.

Änderungsprinzip:
- Kleine, gezielte Änderungen bevorzugen
- Bestehende Struktur respektieren
- Keine großen Umbauten ohne explizite Nachfrage
- Klare, offensichtliche Rechenfehler ohne Rückfrage korrigieren, die Korrektur im Feedback kurz nennen


## Inhaltliche Grundstruktur

- Fachlich sind Inhalte in **Lernbereiche** gegliedert.
- **Checks** unterteilen Lernbereiche weiter in einzelne Einheiten.
- Die Zuordnung von Checks zu Lernbereichen und Modulen erfolgt über `_data/checks.json`.
- Ziel jedes Lernbereichs: Vorbereitung auf die Abituraufgaben seines Themas (Musterprüfungen in `muster-pruefungen/abitur/pruefungen-md/`, Index `_themen.json`).

Gebiete der Plattform:

Analysis  
Lineare Algebra  
Stochastik  
Finanzmathematik


## Module eines Lernbereichs

Jeder Lernbereich enthält mindestens folgende Dateien:

`start.md`  
`kompetenzliste.md`  
`training.md`  
`recall.md`  
`feynman.md`  
`test.md`  
`skript.md`  
`flashcards.md`


## Check-Struktur

Jeder Check ist über `_data/checks.json` verknüpft mit:

- genau einem Kompetenzlisteneintrag
- einer Aufgabensammlung (Training, Flashcards)
- Tipps (Recall, Feynman, Skript)
- einem Beispiel (`beispiele/`)
- einem Test (`test/`)
- einem Abschnitt mit Check-Anker im Skript


## Aufgabensammlungen

Aufgabensammlungen liegen in

`aufgaben/exports/json`

Sie werden vom Python-Aufgabengenerator erzeugt.


## Weitere Dokumentation

Datenmodell (wo liegt was)  
→ `.github/datenmodell.md`

Inhaltsstandards (Checks, Skript, Beispiele, Tipps, Abiturbezug)  
→ `.github/inhalte.md`

Lernbereiche  
→ `lernbereiche/README.md`

Aufgabengenerator  
→ `aufgaben/README.md`

Skript-Widgets  
→ `.github/widgets.md`

Test-Fragen  
→ `test/README.md`

Warm-Up (geführter Einstieg pro Check, nicht verlinkt)  
→ `_data/warmup/README.md`

Klausuren  
→ `klausuren/README.md`

Glossar  
→ `.github/glossary.md`


## Datei-Rollen

`.github/agents/agent-<rolle>.md`  
Rollen, Zuständigkeiten und Pflichtlektüre

`.github/skills/<name>/SKILL.md`  
konkrete Arbeitsaufträge und verbindliche Regelwerke (Übersicht: `.github/skills/README.md`)