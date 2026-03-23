---
description: Aufgaben-Generierung für MatheChecks 
---

# Prompt: Aufgaben-JSON erzeugen

## Ziel

Erzeuge mit Python ein JSON-Array mit genau 20 interaktiven Matheaufgaben desselben Aufgabentyps.

## Referenzen

- Schema, Namenskonventionen, Toleranzregeln: `aufgaben/README.md`
- LaTeX-Konventionen: `.github/glossary.md`

## Pflichtschema pro Objekt

```json
{
  "einleitung": "...",
  "fragen": ["..."],
  "antworten": ["..."]
}
```

- Genau 20 Objekte im Array.
- Keine weiteren Felder (außer optional `visual`).
- Anzahl von `fragen` und `antworten` ist pro Objekt gleich.
- Die 20 Aufgaben unterscheiden sich nur durch Zufallswerte, nicht durch die Aufgabenlogik.

## Antwort-Platzhalter

- Numerisch: `{1:NUMERICAL:=4,2:0,01}`
- Multiple Choice: `{1:MC:~falsch~=richtig}`

## Mathe-Syntax in JSON

- Inline: `\\( ... \\)` (doppelter Backslash im JSON-String)
- Display: `\\[ ... \\]`

## Ausgabe

- Nur das finale JSON, keine Markdown-Codeblöcke, keine Erklärungen.
- Gültiges, parsebares JSON ohne trailing commas.

## Prioritäten bei Konflikten

1. Format-Treue (gültiges JSON, exaktes Schema)
2. Fachliche Korrektheit
3. Konsistente Variation über Zufallswerte