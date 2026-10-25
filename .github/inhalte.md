# Inhaltsstandards: Checks, Skript, Beispiele, Tipps

Verbindliche Ziele für die Inhalte eines Lernbereichs. Wo was liegt: `datenmodell.md`. Ablauf: Skill `lernbereich-erstellen`.

**Leitziel:** Ein Lernbereich bereitet auf die Abituraufgaben seines Themas vor. Checks, Skript, Beispiele, Training und Test dienen diesem Ziel.


## Abitur-Bezug

- Quelle: `muster-pruefungen/abitur/pruefungen-md/_themen.json`, Schlüssel = Lernbereich-Slug. Jede Teilaufgabe verweist per `datei` auf die Prüfungsdatei mit Aufgabe und Erwartungshorizont. Der Ordner ist gitignored, also Dateien direkt per Pfad lesen.
- Jeder im Abitur verlangte Aufgabentyp des Themas ist durch einen Check abgedeckt.
- Checks sind didaktische Einheiten, kein Abbild einzelner Abituraufgaben. Einführende und weiterführende Checks sind erlaubt.
- Sachkontexte, Einheiten, Bezeichnungen, Funktionstypen und Operatoren orientieren sich am Abitur.
- Aufgabentypen, die zu einem anderen Thema gehören (z. B. Parameterscharen, Regression), werden nicht aufgenommen, sondern im Chat gemeldet.
- Inhalte, die im Abitur nicht vorkommen, nur aufnehmen, wenn sie das Verständnis tragen, und knapp halten.


## Checks (`_data/checks.json`)

- Ein Check = eine überprüfbare Kompetenz. `Ich kann …` endet mit einem Verb.
- Reihenfolge (`Nummer`) = didaktische Progression, z. B. graphisch → rechnerisch.
- Pro Check gibt es genau eine Aufgabensammlung, ein Beispiel, einen Test und einen Abschnitt mit Check-Anker im Skript.
- `check_id` ist der Primärschlüssel für Nutzerfortschritt. Checks umnummerieren, löschen oder umdeuten nur nach Rückfrage.


## Skript (`skript.md`)

- **Einstieg:** Ein konkretes Szenario mit Zahlen wird sofort für den ersten Begriff genutzt. Keine Eingangsfrage, die erst am Ende aufgelöst wird.
  - Einführungsbeispiel (Standard): trägt den Einstieg und darf danach auslaufen, ohne Rückblick-Abschnitt.
  - Leitbeispiel: ein Zahlensatz, der in jedem Abschnitt weitergerechnet wird (z. B. Finanzmathematik).
- **Zahlen im Szenario:** plausibel. Keine zufälligen Übereinstimmungen von Größen, die im Allgemeinen verschieden sind (z. B. Startwert = Grenzwert).
- **Pro Check ein Abschnitt** (`##`/`###`): Idee, Bedeutung im Sachzusammenhang, Sonderfälle und typische Fehler werden erklärt, bevor der Check-Anker folgt. Ein Abschnitt besteht nie nur aus Anker oder Tabelle.
- **Rechnen:** Kurze Anwendungen am Szenario sind erwünscht. Vollständige Rechenwege gehören ins Beispiel.
- **Formeln** mit Worten begleiten: Was bedeutet jeder Term, was sagt das Ergebnis?
- **Aufwand verhältnismäßig:** Selten verlangte Teilfragen bekommen keinen langen Spezialabschnitt.
- **LLM-tauglich:** explizite Bezüge, keine vagen Verweise wie „siehe oben“.
- **Graphen:** `{% include graph.html … %}`. Gestrichelte Linien (z. B. Asymptoten) über `"dash":"dash"`. Optional `xdtick`/`ydtick` (z. B. `xdtick=2 ydtick=2`): festes Gitter ab 0 zum Kästchenzählen.
- **Widgets** einsetzen, wenn Interaktion einen Zusammenhang erfahrbar macht (Parameter, Fläche, Wertetabelle). Sie werden im Text vorbereitet und eingebettet. Technik: `widgets.md`, Umsetzung durch `agent-frontend-ux`.
- **Check-Anker:** `{% include check-anker.html nummer="N" %}` blendet Tipps, Beispiel und eine Aufgabe ein. Der Skripttext muss zu allen drei passen.
- Nur `##` und `###` verwenden.


## Beispiele (`beispiele/<NN>-<sammlung>.md`)

- Front Matter wie in bestehenden Beispielen: `layout: null` und `permalink` passend zum Dateinamen.
- Aufgabenstellung zuerst, dann der vollständige Rechenweg mit kurzen Zwischentexten. Rechnungen in `$$ \begin{align*} … \end{align*} $$`.
- Bei Graphenbezug ein Diagramm einbinden.
- Nur Methoden verwenden, die im Skript bis zu diesem Check eingeführt sind.
- Alle Zahlen per Skript nachrechnen.


## Tipps (`Tipps` in `_data/checks.json`)

Abrufhilfen für Skript-Anker, Recall (Antworten werden verdeckt abgefragt) und KI-Kontext in Training und Feynman.

- Format: `{"cue": …, "response": …}`, dazu `tippOrder`: `shuffle` oder `fixed`.
- Typen:
  - Formel: Name → Formel
  - Bedeutung: Symbol oder Begriff → Bedeutung
  - Bedingung: Folgerung → Bedingung
  - `Merkregel`
  - `Beachte`
  - Prozess-Tipps: `1. …`, `2. …` mit `tippOrder: fixed`
- Meist 2–6 Tipps. Stichwortartig, keine vollständigen Sätze, kein Rechenschritt, keine Frageform.
- Die `response` muss ohne weiteren Kontext abrufbar und prüfbar sein.
- Inline-LaTeX ist erlaubt.


## Training, Test, Warm-Up

- **Training:** Aufgaben werden per Generator erzeugt (`aufgaben/README.md`, `agent-python-aufgaben`). Sie sind bewusst nicht an das Skript-Szenario gebunden.
- **Test:** 10 Single-Choice-Fragen pro Check ohne Hilfsmittel, Regeln in `test/README.md`.
- **Warm-Up:** Regeln in `_data/warmup/README.md`, umgesetzt durch `agent-warmup`.


## Fertig, wenn

- alle Zahlen in Skript, Beispielen und Tests nachgerechnet sind,
- der Generator-Batch läuft und Stichproben der Aufgaben korrekt sind,
- `python test/test_coverage.py` für den Lernbereich keine Fehler meldet und die Moodle-XMLs neu erzeugt sind (nur die Dateien des Lernbereichs übernehmen),
- `bundle exec jekyll build` fehlerfrei läuft und Skript und Widgets im Browser geprüft sind.
