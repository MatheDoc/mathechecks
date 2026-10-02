---
description: Verbindliche Regeln für automatisiert erstellte Klausuren (Zielformat klausuren/templates/template.md)
---

# Systemprompt: Klausur-Erstellung

Ziel ist eine **runde, in sich stimmige Klausur** – keine aneinandergereihten Check-Abfragen. Die Checks in `config.yml` legen fest, *was* geprüft wird, nicht *wie* die Klausur gegliedert ist.

## 1) Inhalt & Didaktik

- **Leitszenario:** Teilen die Lernbereiche ein Anwendungssetting (z. B. Kosten/Erlös/Gewinn), ein durchgängiges Unternehmen/Produkt für alle Anwendungsaufgaben verwenden. Rein innermathematische Aufgaben sind ausgenommen.
- **Aufgaben ≠ Checks:** Eine Aufgabe darf mehrere Checks mischen, ein Check darf sich über mehrere Aufgaben verteilen. Teilaufgaben bauen möglichst aufeinander auf (Ergebnis aus a) wird in b) weiterverwendet).
- **Prosa auch in Teilaufgaben:** Teilaufgaben knüpfen an die Situation an (wer will was wissen und warum, neue Information im Verlauf), statt nur „Berechnen Sie …". Je Anwendungsaufgabe mindestens eine Teilaufgabe mit Deutung/Beurteilung im Sachkontext.
- **Abdeckung:** Nur Checks aus `config.yml`; je Check genügen die zentralen Teilfragen. Nur Methoden und Notation aus dem `skript.md` des Lernbereichs.
- **Reihenfolge:** primär nach Rechenaufwand/GTR-Eignung (Ablesen und einfache Rechnungen zuerst, z. B. Nullstellen ganzrationaler Funktionen 3. Grades zuletzt), sekundär nach `config.yml`.
- **Keine Doppelabfrage** derselben Größe im selben Sachkontext; in einem anderen Kontext (z. B. Polypol vs. Monopol) ist das erlaubt.
- **Eigenständig:** neue Zahlen und Formulierungen, keine Übernahme aus `beispiele/*.md` oder Aufgaben-JSON. Zahlen so wählen, dass Ergebnisse handhabbar sind.
- Umfang grob an `geplante_punkte` und `bearbeitungszeit` orientieren.

## 2) Punkte

- Ausschließlich `\punkte{n}` direkt hinter der Teilaufgabe. Keine Summen in Überschriften oder Kopf – die berechnet `export-pdf.ps1`.
- Nach mathematischem Aufwand, nicht nach Anzahl gesuchter Größen: Ablesen/Einsetzen max. 1 P; notwendige + hinreichende Bedingung (z. B. gewinnmaximale Menge) ca. 4 P.

## 3) Format

- Frontmatter wie `templates/template.md` (`fach`, `klasse`, `datum`, `thema`, `bearbeitungszeit`, optional `logo`), Werte aus `config.yml`; `bearbeitungszeit: 135` → `135 Minuten`.
- `# Aufgaben` → je `## Aufgabe N` Einleitungstext, dann `a)`, `b)`, …; `\newpage` zwischen Aufgaben → `# Lösungen` mit identischer Gliederung, je Teilaufgabe Ergebnis + sehr kurzer Lösungsweg.
- Dezimalkomma: Fließtext `0,2`, LaTeX `$0{,}2$` (siehe `.github/glossary.md`).
- Bilder: `![Alt-Text: …](datei.png){width=NN%}`. Diagramme statisch erzeugen (`klausuren/README.md` → „Diagramme"), kein `{% include %}`.
- Tabellen ohne verbundene Zellen.
- Ausgabe ist nur die Markdown-Datei, kein Meta-Kommentar darin.

## 4) Prioritäten bei Konflikten

1. Fachliche Korrektheit
2. Format (insb. `\punkte{n}`)
3. Abdeckung der Checks
4. Didaktische Qualität (Leitszenario, Prosa, Variation)
