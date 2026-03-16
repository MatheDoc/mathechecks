# Konventionen und Glossar

## LaTeX/MathJax-Konvention
- Zielsyntax nach Dateityp:
	- Markdown-Dateien: Inline `$...$`, Display `$$...$$`
	- JSON-Dateien: Inline `\(...\)`, Display `\[...\]`
- JSON-Dateien:
	- In JSON-Strings Backslashes escapen, also `\\(` `\\)` `\\[` `\\]`.
	- Beispiel inline in JSON-String: `"Die Formel ist \\\\(p=\\frac{k}{n}\\\\)"`
- Markdown-Dateien:
	- Immer `$...$` und `$$...$$` schreiben.
	- Nicht verwenden: `\(...\)`, `\[...\]`.
- Reines HTML:
	- Ebenfalls `$...$` und `$$...$$` im Text/Markup verwenden.



## Glossar

- **Session:** Aktive Lernkonfiguration mit genau einem Aktionsfeed (Lernbereiche, aktive Checks, Tempo `x`).
- **Lernbereich:** Klar definierter mathematischer Themenbereich.
- **Check:** Didaktische Einheit im Lernbereich; Primärbezug in Feed/State.
- **Modultyp:** `start`, `einstiegsquiz`, `kompetenzliste`, `training`, `blurting`, `feynman`, `skript`, `flashcards`.
- **Kompetenz:** Textuelle Lernziel-Formulierung eines Checks in der Kompetenzliste.
- **Aufgabensammlung:** Pool von Trainingsaufgaben zu einem Check (z. B. 20 Varianten).
- **Aufgabe:** Eine konkrete Aufgabe aus der Aufgabensammlung.
- **Frage:** Kleinste bewertete Einheit innerhalb einer Aufgabe.

**Kurzglossar (1-Zeiler, für Prompts)**
`Session = aktive Lernkonfiguration mit genau einem Feed; Lernbereich = fachlicher Themenraum; Modultyp = start|einstiegsquiz|kompetenzliste|training|blurting|feynman|skript|flashcards; Check = didaktische Einheit im Lernbereich; Kompetenz = Lernzieltext in der Kompetenzliste; Aufgabensammlung = Sammlung an Aufgaben pro Check; Aufgabe = konkrete Trainingsaufgabe aus der Aufgabensammlung; Frage = kleinste bewertete Einheit; check_id = Primärschlüssel in Feed/State.`