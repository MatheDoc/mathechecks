# Rechner-Architektur

Stand: Mai 2026

Diese Datei beschreibt die vereinbarte Zielarchitektur des MatheChecks-Rechners. Sie ist bewusst keine Prompt-Datei, sondern eine fachlich-technische Referenz für Verhalten, Rollen und UX-Leitplanken.

## Ziel

- Der Rechner soll für Schüler direkt, tolerant und vorhersehbar nutzbar sein.
- Schnelle freie Eingabe hat Vorrang vor Moduszwang.
- Unterschiedliche Ausgabetypen werden nicht in dieselbe UI-Logik gepresst.

## Aktuelle Bedienform

- Die obere Leiste steuert genau eine aktive Eingabehilfe über ein gemeinsames Modus-Dropdown.
- Sichtbare Modusnamen sind aktuell `Verlauf` (Standard beim ersten Öffnen), `Operationen`, `Gleichungssystem`, `Binomialverteilung`, `Graph` und `Matrizen`.
- Die obere Leiste enthält keine globalen Aktions-Buttons. Ein- und Ausblenden des Rechners erfolgt über das Drei-Punkte-Menü der Topbar.
- Ab 800 px Viewport-Breite ist der Rechner rechts unter der Topbar angedockt (Breite per Griff verstellbar), darunter Vollbild-Overlay unter der Topbar.
- Tastenfeld (4 Spalten): `x = C ⌫` / `π e ^ ÷` / Ziffernblock mit Operatoren rechts / `( ) 0 , EXE`. `=` ist das Gleichungszeichen und steht bewusst weit weg von `EXE`. Alle Tasten haben dieselbe Fläche; hervorgehoben sind nur die Operatoren (Textfarbe Akzent), die Löschtasten `C`/`⌫` (Textfarbe rot) und EXE (gedämpfte Akzentfläche).
- `^` fügt `^(` ein, damit der Exponent eindeutig ist (`2^(2*π)` statt mehrdeutig `2^2π`). Bei `EXE` werden offene Klammern automatisch und sichtbar geschlossen.
- `⌫` gedrückt halten löscht nach kurzer Verzögerung fortlaufend weiter.
- Angedockt wachsen Tasten und Schrift mit der Rechnerhöhe (Container-Query); mobil bleiben die Größen fest.
- Unterwerkzeuge innerhalb eines Modus sind nicht dasselbe wie ein Rechner-Modus. Im Menü `Operationen` (intern `basic`) betrifft das z. B. `sin`, `cos`, `tan`, `ln`, `log`, `Bruch` und `Potenz`.
- Der Wechsel eines solchen Unterwerkzeugs ändert nur die lokale Eingabehilfe im aktiven Panel, nicht die globale Rechner-Semantik.

## Drei Kernbereiche

### 1. Main-Input

- Universeller Einstieg für normale Rechnungen, Gleichungen und Kommandos.
- Bleibt der primäre Kanal für schnelle Eingabe.
- Darf auch komplexere Ausdrücke enthalten, nicht nur reine Taschenrechner-Terme.
- Schlanke Code-Schreibweise (`x^2`, `sqrt(…)`, `int(…)`), keine hochgestellten Zeichen oder Integralsymbole. Grafische Hilfen gibt es nur in den Builder-Menüs hinter den Funktionstasten.
- `pi` wird beim Tippen sofort als `π` angezeigt.
- Implizite Multiplikation wird beim Tippen sichtbar als `*` eingefügt, genau an den Stellen, an denen der Parser ohnehin multipliziert: `2e` → `2*e`, `2x` → `2*x`, `3(4)` → `3*(4)`, `(1+2)(3)` → `(1+2)*(3)`. Großes `E` bleibt für die wissenschaftliche Schreibweise (`2E+5`) frei.
- ↑/↓ blättern durch frühere Eingaben (Verlauf).
- Hat eine Spracheingabe (Mikrofon im Feld), siehe Abschnitt „Spracheingabe“.

### 2. Ergebnisbereich

- Zeigt kompakte Kurzresultate.
- Darf Zahlenwerte, kurze Lösungen und kurze Statusmeldungen enthalten.
- Ist keine allgemeine Ausgabefläche für große visuelle oder mehrschrittige Ergebnisse.
- Die erste sichtbare Zeile bleibt eine kompakte Einzelzeile. Statt einer Kopieraktion gibt es Verlauf und Übernahme in Antwortfelder.
- Längere Hinweise dürfen darunter erscheinen, ersetzen aber nicht die eigentliche Panel-Ausgabe.
- Über dem Ergebnis steht klein die ausgeführte Rechnung (ohne angehängtes `=`, da Gleichungen selbst ein `=` enthalten).

### Verlauf und Übernahme in Antwortfelder

- Jede erfolgreiche Ausführung landet im Verlauf (`assets/js/calculator/history.js`, pro Gerät, max. 20). Der Verlauf ist ein eigener Menüpunkt und beim ersten Öffnen aktiv. Die neueste Rechnung steht unten, direkt über Ergebnis und Eingabe. Klick auf die Rechnung setzt sie wieder in den Main-Input.
- Übernahme (`assets/js/calculator/answer-transfer.js`): Ziel ist das zuletzt angeklickte Antwortfeld. Bei offenem Rechner trägt es oben links ein kleines 🧮-Abzeichen, der Rahmen bleibt unverändert. Jeder Wert-Chip im Verlauf (`x₁=3, x₂=5` → zwei Chips) schreibt den angezeigten Wert ins Zielfeld; ohne Zielfeld geht er in den Main-Input. Kurze Antwortfelder werden ersetzt, Freitextfelder (Recall, Feynman) bekommen den Wert an der Cursorposition.
- Kopplung nur über Ereignisse: `calculator:result` (Eingabe, Text, Werte) und `calculator:cleared`.

Typische Inhalte:

- `2,75`
- `x1=-2, x2=2`
- `Keine Lösung`
- `a=1, b=3`

### 3. Menü-Panel

- Strukturierte Eingabehilfe oder eigentliche Arbeitsfläche, je nach Menüart.
- Darf Live-Vorschauen, Hilfswerte und reichhaltige modusspezifische Ausgaben enthalten.

## Menü-Arten

### Builder-Menüs

Builder-Menüs helfen beim Erzeugen oder Verstehen einer Eingabe, sind aber nicht der einzige gültige Weg zur Funktion.

Aktuell:

- Operationen
- Binom
- LGS
- Matrizen

Regeln:

- Dürfen panelinterne Live-Werte anzeigen.
- Dürfen Inhalte per `Übernehmen` in den Main-Input schreiben.
- Wenn das Menü einen komponierbaren Ausdruck erzeugt, fügt `Übernehmen` diesen Ausdruck an der aktuellen Cursorposition im Main-Input ein und löscht den bestehenden Inhalt nicht.
- Wenn das Menü stattdessen ein vollständiges Top-Level-Kommando erzeugt, darf `Übernehmen` den Main-Input vollständig setzen.
- Erzwingen keinen automatischen Menü-Sprung, nur weil eine passende Syntax im Main-Input ausgeführt wurde.
- Werden standardmäßig nicht rückwärts aus dem Main-Input befüllt.

### Workspace-Menüs

Workspace-Menüs sind der primäre Ort für eine bestimmte Art von Ausgabe.

Aktuell:

- Graph

Regeln:

- Die eigentliche Ausgabe liegt im Panel.
- Sie schreiben normalerweise nichts per `Übernehmen` in den Main-Input, wenn dieser Transfer keinen echten Mehrwert hat.
- Ein passendes Top-Level-Kommando im Main-Input darf bei `EXE` in dieses Panel springen.
- Die Ergebniszeile zeigt dort höchstens eine knappe Status- oder Hinweisinfo, aber nicht die Hauptausgabe.

## Verhaltensregeln

### Main-Input bleibt universell

- Freie Eingabe ist immer erlaubt.
- Nutzer müssen nicht zuerst ein Menü öffnen, um rechnen zu können.
- Er muss aber nicht in jedem aktiven Workspace-Menü sichtbar sein, wenn die Arbeit bewusst im Panel stattfindet.
- Top-Level-Kommandos werden nur dann als solche behandelt, wenn sie den gesamten Main-Input bilden.
- Komponierbare Funktionen bleiben auch in größeren Ausdrücken normale Ausdrucksteile und dürfen nicht durch eine zu frühe Sonderbehandlung abgeschnitten werden.

### Ergebnisbereich bleibt kompakt

- Keine großen Objekte wie Graphen in der Ergebniszeile.
- Kurze Gleichungslösungen bleiben erlaubt, weil sie für den direkten Einsatz sehr nutzerfreundlich sind.

### Synchronisation ist asymmetrisch

- Menü-Panel -> Main-Input: ja, bewusst und explizit.
- Main-Input -> Menü-Panel: standardmäßig nein.
- `Übernehmen` ist semantisch ein Transfer in die kanonische Main-Input-Syntax, nicht einfach ein beliebiges Ersetzen des Eingabefelds.

Ausnahmen sind nur sinnvoll, wenn die Rückübertragung verlustfrei, eindeutig und nicht überraschend ist.

### Typisierte Ausdrücke bleiben explizit

- Der Main-Input darf nicht nur Skalare, sondern auch andere Ergebnistypen verarbeiten, wenn das Feature es fachlich verlangt.
- Typgrenzen sollen für Nutzer klar bleiben; implizite Umdeutungen sind zu vermeiden.
- Eine `1x1`-Matrix bleibt deshalb Matrix und wird nicht automatisch als Skalar behandelt.
- Gemischte Ausdrücke sind nur dort erlaubt, wo die Typregel eindeutig ist.
- Bei Matrizen betrifft das insbesondere skalare Faktoren vor oder nach einer Matrix sowie skalare Einträge innerhalb von `mat(...)`.
- Lokale Panel-Abkürzungen sind keine kanonische Hauptsyntax.

## Ableitungen für aktuelle Menüs

### Binom

- `binom(...)` im Main-Input verhält sich wie eine normale skalare Funktion, vergleichbar mit `sin(...)`.
- Das gilt auch in größeren Ausdrücken wie `2*binom(...)`.
- Das Binom-Panel ist Eingabehilfe, nicht kanonischer Ausführungsort.
- `Übernehmen` fügt deshalb den erzeugten `binom(...)`-Ausdruck an der Cursorposition in den Main-Input ein.
- In der Ergebniszeile reicht der nackte Zahlenwert.

### LGS

- Das LGS-Panel ist Builder und Solver-Hilfe.
- Freie LGS-Eingaben im Main-Input bleiben möglich.
- `Übernehmen` setzt hier bewusst einen vollständigen `lgs(...)`-Block in den Main-Input, statt nur ein Fragment einzufügen.
- Keine generelle Rückbefüllung des Panels aus Main-Input-Eingaben, weil dabei Struktur und Variablennamen verloren gehen können.

### Graph

- Graph-Ausgaben gehören primär ins Graph-Panel.
- Im aktiven Graph-Menü kann der Main-Input ausgeblendet sein.
- Das Graph-Menü braucht kein `Übernehmen`, solange die Arbeit vollständig im Panel stattfindet.
- `graph(...)` darf bei `EXE` das Graph-Panel aktivieren.
- `graph(...)` bleibt trotzdem als freier Eingabe- und Expertenpfad erhalten.
- Das Aktivieren passiert bewusst erst bei Ausführung, nicht schon bei bloß erfolgreichem Parse.

### Matrizen

- Das Matrizen-Menü ist ein Builder-Menü mit lokaler Arbeitsfläche, nicht ein eigener Pflichtpfad.
- Die kanonische Hauptsyntax für Matrizen ist `mat(...)`.
- Panel-Variablen wie `A` bis `H` sind nur lokale Hilfssymbole; `Übernehmen` schreibt deshalb expandierte `mat(...)`-Ausdrücke an der Cursorposition in den Main-Input.
- Normale Skalarsyntax bleibt in skalaren Positionen erlaubt, z. B. in Matrixeinträgen oder als Faktor in `2 * mat(...)`.
- Für Matrixausdrücke gelten klare Typregeln: `+` und `-` nur zwischen passenden Matrizen, `*` für Matrix-Matrix und Skalar-Matrix, keine implizite Matrix-Skalar-Umwandlung.
- Ganzzahlige Matrixexponenten sind erlaubt, aber nur für quadratische Matrizen.
- Dabei gilt insbesondere `A^0 = E`; negative ganzzahlige Exponenten laufen fachlich über die Inverse.
- Matrixgleichungen mit freier Variable wie `x` sind ein separates späteres Thema und nicht Teil der aktuellen V1-Regel.

## Spracheingabe

- Nur im Main-Input (V1). Technik gemeinsam mit den Antwortfeldern (`assets/js/modules/ui/speech-input.js`), Übersetzung in `assets/js/calculator/speech.js`.
- Gesprochene Mathematik wird wörtlich übersetzt und an der Cursorposition eingefügt, z. B. „drei mal x hoch zwei“ → `3*x^(2)`, „Klammer auf … Klammer zu“ → `( … )`.
- Während des Sprechens zeigt eine graue Live-Vorschau im Feld den bereits übersetzten Term (z. B. `3*4 ✓`). Sie ist reine Anzeige; der Feldwert ändert sich erst mit dem Endergebnis.
- Keine automatischen Klammern: „eins durch x plus eins“ → `1/x+1`. Einzige Ausnahme: Funktionen und „hoch“ (wie die `^`-Taste) klammern ihr Argument. Bei genau einem Argument wird geschlossen, „Sinus von dreißig“ → `sin(30)`, „x hoch zwei plus eins“ → `x^(2)+1`, „zum Quadrat“ → `^(2)`. Sonst bleibt die Klammer offen („zwei hoch Wurzel aus zwei“ → `2^(sqrt(2)`) und wird bei `EXE` geschlossen. Für längere Argumente „Klammer auf/zu“ sprechen.
- Ohne Signalwort wird nie ausgeführt. Abschließendes „check“, „ausrechnen“ oder „exe“ führt aus wie `EXE` und beendet die Aufnahme.
- Einzelkommandos: „löschen“ leert den Main-Input, „zurück“ löscht ein Zeichen.
- „gleich“ und „ist gleich“ sind das Zeichen `=`, keine Kommandos.
- Andere Module steuern den Rechner nur über `window.CalculatorApi` (`insert`, `setInput`, `getInput`, `execute`, `clear`, `backspace`).

## Regel für neue Rechner-Features

Ein neues Feature sollte zuerst in eine dieser Klassen eingeordnet werden:

1. Komponierbare Funktion

- Kann Teil normaler Ausdrücke sein.
- Kein automatischer Menü-Sprung.
- Ergebnis im kompakten Ergebnisbereich.

2. Kompakter Solver

- Liefert kurze Text- oder Zahlenresultate.
- Darf ein Builder-Panel haben.
- Panel ist Hilfe, nicht Pflichtweg.

3. Räumliche oder visuelle Arbeitsfläche

- Hauptausgabe gehört ins Panel.
- Menü-Sprung bei `EXE` ist sinnvoll.

## Bewertungsgrundsatz

- Etwas mehr interne Komplexität ist akzeptabel, wenn der Rechner für Schüler klarer, direkter und weniger überraschend wird.
- UX und fachlich nachvollziehbares Verhalten haben Vorrang vor technischer Vereinheitlichung um jeden Preis.