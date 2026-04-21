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


## Inhaltliche Grundstruktur

- Fachlich sind Inhalte in **Lernbereiche** gegliedert.
- **Checks** unterteilen Lernbereiche weiter in einzelne Einheiten.
- Die Zuordnung von Checks zu Lernbereichen und Modulen erfolgt über `dev/checks.json`.

Gebiete der Plattform:

Analysis  
Lineare Algebra  
Stochastik


## Module eines Lernbereichs

Jeder Lernbereich enthält mindestens folgende Dateien:

`start.md`  
`warmup.md`  
`kompetenzliste.md`  
`training.md`  
`recall.md`  
`feynman.md`  
`skript.md`  
`flashcards.md`


## Check-Struktur

Jeder Check ist über `checks.json` verknüpft mit:

- genau einem Kompetenzlisteneintrag
- einer Aufgabensammlung im Training
- einem Recall-Bezug
- einem Feynman-Eintrag
- einem Bezug im Skript


## Aufgabensammlungen

Aufgabensammlungen liegen in

`aufgaben/exports/json`

Sie werden vom Python-Aufgabengenerator erzeugt.


## Weitere Dokumentation

Datenmodell & Inhalts-Architektur  
→ `.github/datenmodell.md`

Lernbereiche  
→ `dev/lernbereiche/README.md`

Aufgabengenerator  
→ `aufgaben/README.md`

Feed-System  
→ `dev/feed/README.md`

Skript-Widgets  
→ `.github/widgets.md`

Glossar  
→ `.github/glossary.md`


## Datei-Rollen

`.github/agents/agent-<rolle>.md`  
Rollen, Zuständigkeiten und Pflichtlektüre

`.github/prompts/prompt-<zweck>.md`  
konkrete Arbeitsaufträge