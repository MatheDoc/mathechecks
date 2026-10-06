---
description: Verbindliche Regeln für automatisiert erstellte Klausuren (Zielformat klausuren/templates/template.md)
---

# Systemprompt: Klausur-Erstellung

Ziel ist eine **runde, in sich stimmige Klausur** auf dem Qualitätsniveau zentraler Abiturprüfungen – keine aneinandergereihten Check-Abfragen und keine Abarbeitung aller Angaben aus `config.yml`.

## 0) Quellen und ihre Rollen

`themen`, `checks` und `hinweise` sind **jeweils optional** (mindestens eine Angabe muss vorhanden sein). Sie stecken gemeinsam den **inhaltlichen Rahmen** ab, sind aber **Orientierung, keine Checkliste**: Nicht alles daraus muss in der Klausur vorkommen, und Fragestellungen dürfen in einem vernünftigen Rahmen davon abweichen (z. B. naheliegende Ergänzungen im selben Themenfeld). Ziel ist eine *vernünftige* Klausur, nicht die vollständige Abarbeitung der Angaben.

**Themen der Klausur** = `themen` ∪ Lernbereiche aus `checks`. Ein Thema (`_data/themen.yml`) ist auf MatheChecks umgesetzt, wenn es einen Lernbereich mit gleichem Slug gibt (`_data/lernbereiche.yml`).

| Quelle | Rolle |
|---|---|
| `themen` | Hauptsteuerung: welche Themen die Klausur behandelt. Alle passenden Musterprüfungs-Teilaufgaben (`_themen.json`, alle Jahrgänge) dienen als Ideengeber für Fragetypen, Aufgabenideen und Punkte. |
| `checks` | Feinsteuerung bei umgesetzten Themen: was innerhalb des Lernbereichs behandelt wurde. Notation/Methoden aus `skript.md`; Beispiele (`beispiele/*.md`) nur für Notation, Rechenweg und Zahlenniveau – **nicht** als Formulierungsvorlage (zu stringent). |
| `hinweise` | Ausdrückliche Wünsche der Lehrkraft (z. B. Teilinhalte, Schwerpunkte, Ausschlüsse, gezielt eine bestimmte Musterprüfungs-Aufgabe als Vorbild) – haben Vorrang vor den übrigen Angaben. |
| Musterprüfungen allgemein (`muster-pruefungen/abitur/pruefungen-md/`) | **Immer** Qualitätsmaßstab für das **Wie**: Stil, Operatoren, Einleitungstexte, Aufgabenideen, Granularität der Teilaufgaben, Punkteverteilung. |

**Notation:** Bei umgesetzten Themen gilt das `skript.md` des Lernbereichs (auch bei Abweichung zur Musterprüfung). Bei nicht umgesetzten Themen gilt die Notation der Musterprüfungen.

Fehlt `muster-pruefungen/` lokal (gitignored), entfallen Themen-Treffer und Stilreferenzen – dann gelten nur die übrigen Regeln.

## 1) Inhalt & Didaktik

- **Kein Szenario 1:1 aus Musterprüfungen:** Unternehmen, Produkt, Kontext, Zahlen und Funktionsterme immer neu. Übernehmen dürfen nur Aufgabenideen, Aufbau der Teilaufgaben-Kette, Operatoren und Stil – auch bei in `hinweise` gezielt genannten Musteraufgaben.
- **Leitszenario:** Teilen die Lernbereiche ein Anwendungssetting (z. B. Kosten/Erlös/Gewinn), ein durchgängiges Unternehmen/Produkt für alle Anwendungsaufgaben verwenden. Rein innermathematische Aufgaben sind ausgenommen.
- **Einleitungstexte wie in Musterprüfungen:** Informationen (Daten, Funktionsterme, Tabellen, Grafiken) in der Aufgabeneinleitung vorgeben, auf die sich die Teilaufgaben beziehen; weitere Informationen dürfen im Verlauf hinzukommen („Im Folgenden gilt …").
- **Aufgaben ≠ Themen/Checks:** Eine Aufgabe darf mehrere Themen und Checks mischen, ein Thema darf sich über mehrere Aufgaben verteilen. Teilaufgaben dürfen thematisch aufeinander aufbauen.
- **Teilaufgaben unabhängig lösbar (verbindlich):** Jede Teilaufgabe muss ohne Ergebnis einer früheren Teilaufgabe lösbar sein (kein Folgefehler). Wird ein früheres Ergebnis gebraucht, die benötigte Größe in der Teilaufgabe bzw. per „Im Folgenden gilt …" vor den betroffenen Teilaufgaben nennen oder die Teilaufgabe so formulieren, dass der Weg aus den gegebenen Daten offen bleibt (z. B. „Auftrag aus c) (15 ME …)" statt nur „Auftrag aus c)"; Bereichsprüfung am konkreten Wert statt „Bereich aus f)"). Genannt wird nur, was zum Weiterarbeiten nötig ist (Zwischenergebnis/Kontrollwert), ohne die Lösung der Quellteilaufgabe wesentlich vorwegzunehmen. Nicht „mithilfe Ihrer Ergebnisse aus …" verlangen. In der Lösung den unabhängigen Weg kurz erwähnen, falls er vom Weg über die Vorgängerin abweicht.
- **Granularität:** Maßstab sind die Musterprüfungen. Eine Teilaufgabe darf mehrere Kompetenzen bündeln, solange sie nicht zu lang wird.
- **Prosa auch in Teilaufgaben:** Teilaufgaben knüpfen an die Situation an (wer will was wissen und warum), statt nur „Berechnen Sie …". Operatoren wie in den Musterprüfungen. Je Anwendungsaufgabe mindestens eine Teilaufgabe mit Deutung/Beurteilung im Sachkontext.
- **Inhaltlicher Rahmen:** Themen, Checks und `hinweise` geben die Richtung vor (siehe Abschnitt 0). Lieber eine stimmige Klausur mit einer sinnvollen Auswahl als eine überladene, die alles abdeckt. Keine Inhalte, die erkennbar außerhalb des Rahmens liegen (z. B. nicht genannte Themen).
- **Reihenfolge:** primär nach Rechenaufwand/GTR-Eignung (Ablesen und einfache Rechnungen zuerst, z. B. Nullstellen ganzrationaler Funktionen 3. Grades zuletzt), sekundär nach `config.yml`.
- **Keine Doppelabfrage** derselben Größe im selben Sachkontext; in einem anderen Kontext (z. B. Polypol vs. Monopol) ist das erlaubt.
- **Eigenständig:** neue Zahlen und Formulierungen, keine Übernahme aus `beispiele/*.md`. Zahlen so wählen, dass Ergebnisse handhabbar sind.
- Umfang grob an `geplante_punkte` und `bearbeitungszeit` orientieren.

## 2) Punkte

- Ausschließlich `\punkte{n}` direkt hinter der Teilaufgabe. Keine Summen in Überschriften oder Kopf – die berechnet `export-pdf.ps1`.
- Nach mathematischem Aufwand, nicht nach Anzahl gesuchter Größen: Ablesen/Einsetzen max. 1 P; notwendige + hinreichende Bedingung (z. B. gewinnmaximale Menge) ca. 4 P. Relative Punkteverteilung an den Musterprüfungen orientieren.

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
3. `hinweise` der Lehrkraft
4. Stimmigkeit und Qualität im Stil der Musterprüfungen (Leitszenario, Einleitung, Prosa, Granularität)
5. Nähe zu `themen` und `checks`
