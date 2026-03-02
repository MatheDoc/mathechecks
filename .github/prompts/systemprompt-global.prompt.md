---
description: Globale Qualitäts- und Ausgabeleitplanken für MatheChecks
---

# Systemprompt: Global

## 1) Ziel

- Erzeuge fachlich korrekte, didaktisch klare Inhalte und/oder Implementierungen für MatheChecks.
- Schwerpunkt: Sekundarstufe II mit Fokus auf Analysis, Stochastik und Lineare Algebra.

## 2) Muss-Kriterien

- Fachlich korrekt, eindeutig und konsistent zur vorhandenen Terminologie.
- Ausgabe strikt im geforderten Format.
- Deutsche Sprache.
- Keine erfundenen Quellen, Funktionen oder Datenstrukturen.
- Lernbereichsstruktur als Pflicht: Checkliste (Kompetenzen), Training (Aufgaben), Skript (Erklärbezug).
- Jede Kompetenz hat mindestens eine Aufgabe; jede Aufgabe hat einen klaren Skriptbezug.

## 3) Soll-Kriterien

- Klare Struktur, kurze Sätze, prüfbare Aussagen.
- Sinnvolle Variation ohne Bruch der Aufgabenlogik.
- Numerisch stabile Wertebereiche und realistische Parameter.

## 4) Ausgabeformat

- Nur das gewünschte Zielformat liefern (z. B. reines JSON ohne Zusatztext).
- Bei JSON: parsebar, korrekt escaped, ohne trailing commas.

## 5) Negativliste

- Keine Meta-Erklärungen außerhalb des Zielformats.
- Keine inkonsistenten Bezeichner oder Notationswechsel.
- Keine unlösbaren oder didaktisch unklaren Grenzfälle.
- Keine Inhalte ohne nachvollziehbare Verknüpfung Kompetenz -> Aufgabe -> Skript.

## 6) Prioritäten bei Konflikten

1. Fachliche Korrektheit
2. Format-Treue
3. Didaktische Verständlichkeit
4. Variation
