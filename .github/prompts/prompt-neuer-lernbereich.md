---
description: Schrittfolge zum Anlegen eines neuen Lernbereichs in MatheChecks.
---

# Neuen Lernbereich anlegen

Lese vor Beginn `.github/datenmodell.md` und `.github/glossary.md`.

## Schrittfolge

### 1. Checks definieren (`dev/checks.json`)

- Lernbereich in überprüfbare Einheiten gliedern
- Pro Check: `Ich kann`, `Schlagwort`, `Tipps`, `skript_anchor`, `check_id`, `Nummer`
- Reihenfolge = didaktische Progression (einfach → komplex)
- Prüfungsrelevanz: Decken die Checks die typischen Abituraufgabentypen ab?

### 2. Skript schreiben (`skript.md`)

- Fachinhalt mit Check-Ankern; nur `##` und `###` verwenden
- Begriffe erklären, Formeln mit Worten begleiten, keine Zahlenbeispiele durchrechnen
- Widgets empfehlen, wo Interaktivität den Parametereinflusss erfahrbar macht

### 3. Beispiele schreiben (`beispiele/<NN>-<sammlung>.md`)

- Pro Check ein vollständig durchgerechnetes Zahlenbeispiel
- Aufgabenstellung zuerst, dann Lösungsweg mit `$$…$$`; kein Front Matter
- Nur Methoden verwenden, die bis zu diesem Check im Skript eingeführt wurden

### 4. Aufgabensammlungen (→ Python-Aufgaben-Agent)

- `Sammlung`-Slug an den Python-Agent übergeben
- Sicherstellen, dass Aufgaben zur `Ich kann`-Formulierung passen

### 5. Übrige Module prüfen

- `kompetenzliste.md`, `training.md`, `recall.md`, `feynman.md`, `flashcards.md` konsumieren `checks.json` und Aufgaben-JSON automatisch
- `start.md` — Überblick und Lernpfad schreiben

## Abhängigkeiten

```
checks.json ──→ Skript + Beispiele ──→ Aufgabensammlungen
     │                                       │
     └──→ Kompetenzliste, Recall,            └──→ Training, Flashcards
           Feynman (automatisch)
```
