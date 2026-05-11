---
description: Skript fachlich-didaktisch und LLM-freundlich überarbeiten
---

# Prompt: Skript überarbeiten

## Ziel

Überarbeite das angegebene `skript.md` direkt in der Datei. Nutze die Vorgaben des Agents `agent-content-didaktik` als verbindliche Grundlage und konzentriere dich hier auf die konkrete Revision des Skripttexts.

## Eingabe

- Skriptdatei: `<Pfad zu skript.md>`
- Optionaler Fokus: `<z. B. Begriffsaufbau | Stringenz | Kürzen | Übergänge | Check-Anker | LLM-Kontexttauglichkeit>`
- Optionaler Rahmen: `<bestimmte Checks, Abschnitte oder bekannte Probleme>`
- Wenn kein Pfad genannt ist, arbeite mit der aktuell geöffneten `skript.md`.

## Arbeitsauftrag

- Prüfe das Skript im Kontext des zugehörigen Lernbereichs und ziehe bei Bedarf `dev/checks.json` sowie benachbarte Moduldateien heran.
- Überarbeite den Text direkt in der Datei, mit kleinen gezielten Änderungen statt eines Totalumbaus.
- Halte die im Agenten definierten fachlichen und didaktischen Standards für Skripttexte ein.
- Berücksichtige bei jedem Check-Anker die tatsächlichen Quellen mit: Tipps aus `dev/checks.json` sowie das zugehörige Beispiel und die passende Aufgabensammlung, die über `Nummer` und `Sammlung` des Checks identifiziert werden.
- Prüfe dafür das Beispiel im `beispiele`-Ordner des Lernbereichs und nach Möglichkeit mindestens eine konkrete Aufgabe aus der passenden Datei in `aufgaben/exports/json` stichprobenartig mit.
- Integriere das Trio aus Tipps, Beispiel und Aufgabe sauber in den Skriptfluss; die Anker sollen fachlich vorbereitet, sinnvoll eingebettet und für Lernende anschlussfähig sein.
- Wenn im Skript Widgets eingebunden sind, müssen auch sie fachlich vorbereitet und sinnvoll in den Textfluss eingebettet sein.
- Formuliere zusätzlich so, dass LLM-basierte Systeme den Text als stabilen Kontext gut nutzen können: klare Übergänge, explizite Bezüge und möglichst wenig vage Verweise.
- Prüfe das Skript auf **didaktische Dünne**: Abschnitte oder Übergänge, die nur aus Check-Ankern ohne erklärenden Text bestehen, sollen durch einen kurzen, lernwirksamen Text ergänzt werden — der die zugehörige Idee, Strukturlogik oder wichtige Sonderfälle erklärt, bevor der Anker greift. Auch reine Nachschlage-Tabellen ohne einleitenden Kontext sind ein Hinweis auf didaktische Dünne.
- Wenn beim Lesen der Tipps in `dev/checks.json` eindeutige Tippfehler oder fachliche Fehler auffallen (z. B. falsche Formel, falsches Schlagwort, Tippfehler in einem Tipp-String), korrigiere sie direkt in `dev/checks.json` — ohne Rückfrage.

## Ausgabe

- Nimm die Änderungen direkt in den betroffenen Dateien vor (`skript.md` und ggf. `dev/checks.json`).
- Gib anschließend kurz an, welche Schwächen überarbeitet wurden, welche Dateien geändert wurden und ob Folgearbeiten in anderen Modulen oder in `checks.json` sinnvoll wären.

Es gelten die Prioritäten aus `agent-content-didaktik`.