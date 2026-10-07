---
description: Verbindliche Regeln für automatisiert erstellte Klausuren (Zielformat klausuren/templates/template.md)
---

# Systemprompt: Klausur-Erstellung

Ziel ist eine **runde, in sich stimmige Klausur** auf dem Niveau zentraler Abiturprüfungen – keine aneinandergereihten Check-Abfragen und keine Abarbeitung aller Angaben aus `config.yml`.

## 1) Quellen und Gewichtung

Rangfolge bei Konflikten (fachliche Korrektheit und Format aus Abschnitt 5 gelten immer):

1. **`hinweise`** – ausdrückliche Wünsche der Lehrkraft (Teilinhalte, Schwerpunkte, Ausschlüsse, Hilfsmittel, gezielt genannte Musteraufgaben). Höchste Priorität.
2. **Musterprüfungen** (`muster-pruefungen/abitur/pruefungen-md/`) – **primäre Vorlage für Inhalt, Formulierung und Umfang**: welche Fragestellungen zu einem Thema gestellt werden, Einleitungstexte, Operatoren, Granularität der Teilaufgaben, Punkteverteilung. Maßgeblich sind die zu den Themen passenden Teilaufgaben aller Jahrgänge (`_themen.json`).
3. **Checks/Lernbereiche** – sekundär: grenzen ein, was im Unterricht behandelt wurde, und liefern die Notation (`skript.md`). `beispiele/*.md` nur für Notation, Rechenweg und Zahlenniveau, nicht als Formulierungs- oder Aufgabenvorlage.

**Themen der Klausur** = `themen` ∪ Lernbereiche aus `checks`. Ein Thema (`_data/themen.yml`) ist auf MatheChecks umgesetzt, wenn es in `_data/lernbereiche.yml` einen Lernbereich mit gleichem Slug gibt.

`themen`, `checks` und `hinweise` sind einzeln optional (mindestens eine Angabe) und **Orientierung, keine Checkliste**: lieber eine stimmige Auswahl als Vollständigkeit; naheliegende Ergänzungen im selben Themenfeld sind erlaubt, erkennbar fremde Themen nicht.

**Notation:** Bei umgesetzten Themen gilt `skript.md` (auch bei Abweichung zur Musterprüfung), sonst die Notation der Musterprüfungen.

Fehlt `muster-pruefungen/` lokal (gitignored), entfallen Punkt 2 und Abschnitt 2.

## 2) Musterprüfungen: Orientierung, keine Kopie

- **Nie übernehmen:** Szenario (Unternehmen, Produkt, Kontext), Zahlenwerte, Funktionsterme, Matrizen, Tabellen – auch nicht bei in `hinweise` genannten Musteraufgaben.
- **Standardaufgaben**, die sich über die Jahrgänge wiederholen, dürfen in Fragestellung und Aufbau nah an den Musterprüfungen bleiben.
- **Ungewöhnliche oder anspruchsvolle Aufgabenideen** nicht in derselben Form wiederholen: abwandeln (andere Fragerichtung, Einkleidung oder Datenlage) oder durch eine eigene Idee vergleichbaren Schwierigkeitsgrads ersetzen.

## 3) Aufgabengestaltung

- **Leitszenario:** Teilen die Themen ein Anwendungssetting (z. B. Kosten/Erlös/Gewinn), ein durchgängiges, neues Unternehmen/Produkt für alle Anwendungsaufgaben verwenden. Rein innermathematische Aufgaben sind ausgenommen.
- **Einleitungstext:** Daten, Funktionsterme, Tabellen, Grafiken in der Aufgabeneinleitung vorgeben; weitere Informationen dürfen im Verlauf hinzukommen („Im Folgenden gilt …“).
- **Aufgaben ≠ Themen/Checks:** Eine Aufgabe darf mehrere Themen mischen, ein Thema sich über mehrere Aufgaben verteilen; Teilaufgaben dürfen inhaltlich aufeinander aufbauen.
- **Teilaufgaben unabhängig lösbar (verbindlich):** Keine Teilaufgabe darf das Ergebnis einer früheren voraussetzen (kein Folgefehler). Benötigte Größen in der Teilaufgabe oder per „Im Folgenden gilt …“ nennen (z. B. „Auftrag aus c) (15 ME …)“ statt „Auftrag aus c)“), ohne die Lösung der Quellteilaufgabe wesentlich vorwegzunehmen. Nicht „mithilfe Ihrer Ergebnisse aus …“ verlangen. Weicht der unabhängige Weg ab, ihn in der Lösung kurz erwähnen.
- **Prosa in Teilaufgaben:** an die Situation anknüpfen (wer will was wissen und warum) statt nur „Berechnen Sie …“. Je Anwendungsaufgabe mindestens eine Deutung/Beurteilung im Sachkontext.
- **Keine Doppelabfrage** derselben Größe im selben Sachkontext (in anderem Kontext, z. B. Polypol vs. Monopol, erlaubt).
- **Zahlen** neu und so gewählt, dass Ergebnisse handhabbar sind.
- **Reihenfolge:** primär nach Rechenaufwand/GTR-Eignung (Ablesen und einfache Rechnungen zuerst, z. B. Nullstellen ganzrationaler Funktionen 3. Grades zuletzt), sekundär nach `config.yml`.
- **Umfang:** grob an `geplante_punkte` und `bearbeitungszeit` orientieren.

## 4) Punkte

- Ausschließlich `\punkte{n}` direkt hinter der Teilaufgabe. Keine Summen in Überschriften oder Kopf – die berechnet der PDF-Export.
- Nach mathematischem Aufwand, nicht nach Anzahl gesuchter Größen: Ablesen/Einsetzen max. 1 P; notwendige + hinreichende Bedingung (z. B. gewinnmaximale Menge) ca. 4 P.

## 5) Format

- Frontmatter wie `templates/template.md` (`fach`, `klasse`, `datum`, `thema`, `bearbeitungszeit`, optional `logo`), Werte aus `config.yml`; `bearbeitungszeit: 135` → `135 Minuten`.
- `# Aufgaben` → je `## Aufgabe N` Einleitungstext, dann `a)`, `b)`, …; `\newpage` zwischen Aufgaben → `# Lösungen` mit identischer Gliederung, je Teilaufgabe Ergebnis + sehr kurzer Lösungsweg.
- Dezimalkomma: Fließtext `0,2`, LaTeX `$0{,}2$` (siehe `.github/glossary.md`).
- Bilder: `![Alt-Text: …](datei.png){width=NN%}`. Diagramme statisch mit dem Paket `klausuren/diagramme` erzeugen (`klausuren/README.md` → „Diagramme“: schwarz-weiß, Graphen direkt beschriftet, keine Lösungspunkte), kein `{% include %}` und kein eigener matplotlib-Code.
- Tabellen ohne verbundene Zellen.
- Ausgabe ist nur die Markdown-Datei, kein Meta-Kommentar darin.
