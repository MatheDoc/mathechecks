---
description: Verbindliche Ausgaberegeln für automatisiert erstellte Klausuren (Zielformat klausuren/templates/template.md)
---

# Systemprompt: Klausur-Erstellung

## 1) Ziel

- Aus einer Check-Auswahl (`config.yml`) eine vollständige Klausur im Format von `klausuren/templates/template.md` erzeugen: Aufgabenteil, danach Lösungsteil.

## 2) Muss-Kriterien

- YAML-Frontmatter exakt mit den Feldern aus `templates/template.md`: `fach`, `klasse`, `datum`, `thema`, `bearbeitungszeit`, optional `logo` — Werte aus `config.yml` übernehmen, nicht erfinden. `bearbeitungszeit` dabei vom numerischen `config.yml`-Wert ins Textformat des Templates bringen (z. B. `135` → `135 Minuten`).
- Dezimalkomma in Fließtext (`0,2`), in LaTeX-Formeln `{,}` (`$0{,}2$`) gemäß `.github/glossary.md`.
- Jede Aufgabe beginnt mit `## Aufgabe N` und einem kurzen einleitenden Kontext (Sachsituation), danach Teilaufgaben `a)`, `b)`, `c)` …
- Punkte ausschließlich per `\punkte{n}` direkt hinter der Teilaufgabe. Keine Punktsumme je Aufgabe und keine Gesamtpunktzahl selbst in eine Überschrift oder den Klausurkopf schreiben — das übernimmt automatisch `klausuren/export-pdf.ps1` über `templates/punkte-summe.lua` beim PDF-Export.
- Zwischen den Aufgaben `\newpage` einfügen.
- Bilder/Grafiken, falls fachlich nötig, im Format `![Alt-Text: ...](dateiname){width=NN%}`. Für grafische Ablese-Aufgaben (Checks „Kennzahlen graphisch") **kein** `{% include graph.html %}` verwenden (funktioniert nicht im Pandoc-PDF-Export) — stattdessen als statisches Bild erzeugen, siehe `klausuren/README.md` → „Diagramme (grafische Teilaufgaben)".
- Falls eine Teilaufgabe eine Tabelle braucht: keine verschmolzenen Zellen (Row-/Colspan) verwenden, da `templates/table-style.lua` diese beim PDF-Export nicht unterstützt.
- Jede Aufgabe deckt ausschließlich Checks ab, die in der `config.yml` für den jeweiligen Lernbereich gelistet sind.
- Lösungsteil (`# Lösungen`) spiegelt exakt dieselbe Gliederung (`## Aufgabe N`, `a)`, `b)`, …) und enthält je Teilaufgabe das Ergebnis plus einen sehr kurzen Lösungsweg.

## 3) Soll-Kriterien

- Aufgaben neu formulieren und mit neuen Zahlen/Kontexten versehen statt Beispiele oder Trainingsaufgaben wortgleich zu übernehmen.
- Schwierigkeit und Teilaufgaben-Anzahl an `geplante_punkte` und `bearbeitungszeit` orientieren (grobe Richtgröße, keine exakte Rechnung).
- Reihenfolge der Aufgaben folgt der Reihenfolge der Checks/Lernbereiche in `config.yml`.
- Konsistente Fachsprache und Notation mit dem zugehörigen `skript.md` des Lernbereichs.
- Wenn die ausgewählten Lernbereiche ein durchgängiges Anwendungssetting teilen (z. B. immer Kosten, Erlös, Gewinn, Preis eines Betriebs), ein einheitliches Leitszenario (ein Unternehmen/eine Branche) für alle Anwendungsaufgaben der Klausur verwenden statt je Aufgabe einen neuen Kontext zu erfinden — analog zum Leitbeispiel-Prinzip aus `.github/datenmodell.md`. Einzelne rein innermathematische Teilaufgaben ohne Sachkontext bleiben davon unberührt.

## 4) Ausgabeformat

- Eine einzelne Markdown-Datei nach dem Muster von `klausuren/templates/template.md`, gespeichert unter `klausuren/<slug>/klausur.md`.
- Reihenfolge: Frontmatter → `# Aufgaben` → Aufgabe 1..n → `# Lösungen` → Aufgabe 1..n.
- Kein zusätzlicher Kommentar, keine Meta-Erklärung außerhalb der Markdown-Datei.

## 5) Negativliste

- Keine Punkt- oder Gesamtsummen in Überschriften oder im Klausurkopf.
- Keine Dezimalpunkte (`0.2`) im Fließtext.
- Keine Methoden/Begriffe, die im Skript des Lernbereichs noch nicht eingeführt wurden.
- Keine Aufgaben zu Checks außerhalb der `config.yml`-Auswahl.
- Keine wortgleiche Übernahme aus `beispiele/*.md` oder der Aufgaben-JSON.

## 6) Prioritäten bei Konflikten

1. Fachliche Korrektheit
2. Format-Treue zu `templates/template.md` (insb. `\punkte{n}`-Regel)
3. Abdeckung der ausgewählten Checks
4. Didaktische Qualität und Variation
