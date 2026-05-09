# Rechner-Architektur

Stand: Mai 2026

Diese Datei beschreibt die vereinbarte Zielarchitektur des MatheChecks-Rechners. Sie ist bewusst keine Prompt-Datei, sondern eine fachlich-technische Referenz für Verhalten, Rollen und UX-Leitplanken.

## Ziel

- Der Rechner soll für Schüler direkt, tolerant und vorhersehbar nutzbar sein.
- Schnelle freie Eingabe hat Vorrang vor Moduszwang.
- Unterschiedliche Ausgabetypen werden nicht in dieselbe UI-Logik gepresst.

## Aktuelle Bedienform

- Die obere Leiste steuert genau eine aktive Eingabehilfe über ein gemeinsames Modus-Dropdown.
- Sichtbare Modusnamen sind aktuell `Standard`, `Gleichungssystem`, `Binomialverteilung`, `Graph` und `Matrizen`.
- Rechts in der oberen Leiste liegen nur globale Aktionen wie Standardansicht wiederherstellen und Schließen.
- Unterwerkzeuge innerhalb eines Modus sind nicht dasselbe wie ein Rechner-Modus. Im Standard-Menü betrifft das z. B. `sin`, `cos`, `tan`, `ln`, `log`, `Bruch` und `Potenz`.
- Der Wechsel eines solchen Unterwerkzeugs ändert nur die lokale Eingabehilfe im aktiven Panel, nicht die globale Rechner-Semantik.

## Drei Kernbereiche

### 1. Main-Input

- Universeller Einstieg für normale Rechnungen, Gleichungen und Kommandos.
- Bleibt der primäre Kanal für schnelle Eingabe.
- Darf auch komplexere Ausdrücke enthalten, nicht nur reine Taschenrechner-Terme.

### 2. Ergebnisbereich

- Zeigt kompakte Kurzresultate.
- Darf Zahlenwerte, kurze Lösungen und kurze Statusmeldungen enthalten.
- Ist keine allgemeine Ausgabefläche für große visuelle oder mehrschrittige Ergebnisse.
- Die erste sichtbare Zeile bleibt eine kompakte Einzelzeile; eine Kopieraktion für das Kurzresultat ist dort sinnvoll.
- Längere Hinweise dürfen darunter erscheinen, ersetzen aber nicht die eigentliche Panel-Ausgabe.

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

- Standard
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