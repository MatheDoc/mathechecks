---
description: Klausur aus Lernbereichen/Checks gemäß config.yml erzeugen
---

# Prompt: Klausur erstellen

Eingabe: `klausuren/<slug>/config.yml` (ohne Pfadangabe die aktuell geöffnete). Regeln: `.github/prompts/systemprompt-klausur.prompt.md`.

## Schritte

1. **Material sammeln** je Check aus `config.yml`:
   - `checks.json` → `Ich kann`, `Tipps`, `Sammlung`
   - `lernbereiche/<gebiet>/<lernbereich>/beispiele/<NN>-<Sammlung>.md` → Notation, Rechenweg
   - Stichprobe aus `aufgaben/exports/json/<gebiet>/<lernbereich>/<Sammlung>.json` → Zahlenniveau
2. **Planen:** Leitszenario festlegen und die Checks zu Aufgaben mit aufeinander aufbauenden Teilaufgaben verweben; Reihenfolge und grobe Punkteverteilung festlegen.
3. **Schreiben:** `klausuren/<slug>/klausur.md` (ggf. Diagramm-Skript + PNGs im selben Ordner).
4. **Prüfen:** alle Lösungen nachrechnen (bei Bedarf per Python), Ergebnisse handhabbar? Kontextbezug in Teilaufgaben? Keine Doppelabfragen?

## Ausgabe an den Nutzer

- Zuordnung Check → Aufgabe/Teilaufgabe, fehlende Quelldaten
- Hinweis auf PDF-Export: `klausuren/export-pdf.ps1 klausuren/<slug>/klausur.md`
