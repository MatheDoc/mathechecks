# Konventionen und Glossar

## LaTeX/MathJax-Konvention
- Syntax:
	- Allgemein: Inline `$...$`, Display `$$...$$`, Komma mit geschweiften Klammern `{,}`, z.B. `$0{,}5$`
	- JSON-Dateien: Escapen, zum Beispiel inline in JSON-String: `"Die Formel ist $ p=\\frac{k}{n} $"`
	- bei Replacement-Strings keine geschweiften Klammern für Kommas verwenden, keine $-Zeichen, richtig ist zB. `"{1:NUMERICAL:=0,1461:0,0001}"`
- Reiner Text:
	keine geschweiften Klammern für Kommas verwenden, z.B. `0,5` statt `0{,}5`.



## Glossar

- **Session:** Aktive Lernkonfiguration mit genau einem Aktionsfeed (Lernbereiche, aktive Checks, Tempo `x`).
- **Lernbereich:** Klar definierter mathematischer Themenbereich.
- **Check:** Didaktische Einheit im Lernbereich; Primärbezug in Feed/State.
- **Modultyp:** `start`, `warmup`, `kompetenzliste`, `training`, `recall`, `feynman`, `skript`, `flashcards`.
- **Kompetenz:** Textuelle Lernziel-Formulierung eines Checks in der Kompetenzliste.
- **Aufgabensammlung:** Pool von Trainingsaufgaben zu einem Check (z. B. 20 Varianten).
- **Aufgabe:** Eine konkrete Aufgabe aus der Aufgabensammlung.
- **Frage:** Kleinste bewertete Einheit innerhalb einer Aufgabe.
- **Skript-Widget:** Interaktive Slider-gesteuerte Visualisierung im Skript (Include aus `_includes/dev/widgets/`, Logik in `skript-visuals.js`).

**Kurzglossar (1-Zeiler, für Prompts)**
`Session = aktive Lernkonfiguration mit genau einem Feed; Lernbereich = fachlicher Themenraum; Modultyp = start|warmup|kompetenzliste|training|recall|feynman|skript|flashcards; Check = didaktische Einheit im Lernbereich; Kompetenz = Lernzieltext in der Kompetenzliste; Aufgabensammlung = Sammlung an Aufgaben pro Check; Aufgabe = konkrete Trainingsaufgabe aus der Aufgabensammlung; Frage = kleinste bewertete Einheit; check_id = Primärschlüssel in Feed/State.`