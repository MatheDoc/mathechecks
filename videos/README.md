# Erklärvideos (Pilot)

Kurzvideos im Hochformat (YouTube Shorts, TikTok), eines pro Check, erzeugt mit [Manim](https://www.manim.community/) und `manim-voiceover`.

Stand: Pilot mit fünf Videos; sie sind noch nicht in die Website eingebunden, der Ordner ist von Jekyll ausgeschlossen. Arbeitsauftrag für die KI: Skill `video-erstellen` (`.github/skills/video-erstellen/SKILL.md`), Rolle `agent-video`.

## Vorlagen

Neue Szenen entstehen aus der Vorlage, die dem Check am nächsten kommt (alle unter `checks/`):

| Art des Checks | Vorlage |
|---|---|
| Rechenverfahren in Schritten, tragender Graph | `analysis/differentialrechnung-ganzrationaler-funktionen/06-extremstellen-bestimmen.py` |
| Algorithmus an einer Matrix | `lineare-algebra/lineare-gleichungssysteme/02-lgs-loesen-3x3.py` |
| Textverständnis, viele Fallarten, Bild begleitet nur | `stochastik/binomialverteilung/05-bereichswahrscheinlichkeiten-berechnung.py` |
| Diagramm lesen ohne Ablauf, nach den Teilaufgaben des Trainings | `stochastik/bedingte-wahrscheinlichkeiten/03-baumdiagramm-folgern-mit-unabh.py` |
| Graph im Sachzusammenhang lesen (Kennzahl ↔ Merkmal, jede Kennzahl eine Farbe) | `analysis/produktlebenszyklus/01-kennzahlen-graphisch-umsatz.py` |

## Aufbau

```text
videos/
  render.py                 einziger Einstieg zum Rendern
  aufnahme.py, aufnahme.html  eigene Stimme einsprechen (lokale Seite im Browser)
  requirements.txt
  mcvideo/                  gemeinsame Bibliothek
    theme.py                Farben, Schrift, Bildaufteilung, Auflösung
    szene.py                Basisszene MCSzene: Logo, Bereiche, Ton, Schlussbild, Randprüfung
    bausteine.py            Frage, Schritt, Kurzfassung, Aufzählung, Legende, Zahlenstrahl, Versuche, ErweiterteMatrix, Baumdiagramm, Dezimalzahl, …
    stimme.py               Sprachdienst: eigene Aufnahmen, sonst Entwurfsstimme
    fonts/                  Inter (SIL Open Font License)
  checks/<gebiet>/<lernbereich>/<NN>-<sammlung>.py   Szene eines Checks
  aufnahmen/<gebiet>/<lernbereich>/<NN>-<sammlung>/   eigene Sprachaufnahmen je Sprechabschnitt (MP3, im Repo)
  media/                    Zwischenstände, Tonzwischenspeicher, Prüfbögen (gitignored)
  ausgabe/<gebiet>/<lernbereich>/<NN> <Schlagwort> <Lernbereichsname>.mp4  fertige Videos (gitignored)
```

Die Szene heißt `<NN>-<sammlung>.py` nach der Aufgabensammlung des Checks (Feld `Sammlung` in `_data/checks.json`). Sie ist die Quelle des Videos, zusammen mit den eigenen Sprachaufnahmen, sobald es sie gibt. Aus dem Pfad ergibt sich die `check_id`; `render.py` bricht ab, wenn es sie in `_data/checks.json` nicht gibt.

## Einrichten

```powershell
python -m venv videos\.venv
videos\.venv\Scripts\python -m pip install -r videos\requirements.txt
```

Zusätzlich nötig: LaTeX (MiKTeX) für die Formeln und eine Internetverbindung für die Entwurfsstimme. Getestet mit Python 3.14.

## Ablauf

1. **Szene** schreiben: Klasse `Video(MCSzene)` mit der Methode `inhalt()`, die mit `self.einstieg(...)` beginnt. Im Kopf der Datei stehen zwei Zeilen: die Kernidee und ob das Beispiel vom Musterbeispiel abweicht. Ausgangspunkt ist eine der Vorlagen oben.
2. **Entwurf** rendern (540 × 960, etwa eine Minute):

   ```powershell
   videos\.venv\Scripts\python videos\render.py videos\checks\<gebiet>\<lernbereich>\<NN>-<sammlung>.py
   ```

   Ausgegeben werden Dauer, Wortzahl und alle Objekte außerhalb des sichtbaren Bereichs.
3. **Prüfbogen** durchsehen: `media/pruefung/<check_id>/pruefbogen.md` zeigt je Sprechabschnitt das Standbild mit dem Sprechtext (Überlappungen, Lesbarkeit, fachliche Richtigkeit). Er wird bei jedem Entwurf neu erzeugt.
4. **Einsprechen** (wenn das Video die eigene Stimme bekommen soll): siehe „Eigene Stimme einsprechen“.
5. **Final** rendern (1080 × 1920, 30 Bilder pro Sekunde) mit `--final`. Das Video landet in `ausgabe/<gebiet>/<lernbereich>/` und heißt `<NN> <Schlagwort> <Lernbereichsname>.mp4`, etwa `02 LGS 3x3 Lineare Gleichungssysteme.mp4`. YouTube übernimmt den Dateinamen beim Hochladen als Titel und ersetzt Bindestriche durch Leerzeichen; Schlagwort und Lernbereichsname aus `_data/checks.json` müssen deshalb als Dateiname taugen (Regel in `.github/datenmodell.md`). Ein früheres Video des Checks wird ersetzt. Bei Randverstößen oder unvollständigen Aufnahmen wird nichts ausgegeben.

## Regeln für ein Video

- Umfang: Ziel 60–90 Sekunden, Richtwert höchstens 200 Wörter Sprechtext, Obergrenze 180 Sekunden.
- Einstieg (für alle Videos gleich, `self.einstieg(...)`):
  1. Ein kennzeichnendes Bild entsteht, am besten eines, mit dem das Video weiterarbeitet (hier der Graph), sonst ein Bild mit Symbolcharakter. Das erste Bild ist nicht leer.
  2. Dazu erscheint die Frage, gesprochen und geschrieben, weiß und ohne Farbcode. Sie steht in der Du-Form und benennt das Thema sofort, nach dem Muster „Wie bestimmst du Hoch- und Tiefpunkte?“ (der umgedrehte Kompetenzsatz des Checks). Die Frage bleibt kurz, höchstens zwei Zeilen; eine nötige Ergänzung steht als `zusatz` kleiner darunter und wird mitgesprochen, etwa „(mit bedingten Wahrscheinlichkeiten)“.
  3. Begrüßung: Unter der Frage erscheint das Logo mit Lichtschein, darunter `mathechecks.de` (wie im Schlussbild, nur kleiner); gesprochen wird `MCSzene.begruessung`.
  4. Das Logo wandert in die Ecke und bleibt dort; erst jetzt erscheint die Kopfzeile.
- Die Kopfzeile ist freiwillig. Sie zeigt das Gegebene, auf das sich die Rechnung durchgehend bezieht (etwa den Funktionsterm). Steht das Gegebene schon auf der Bühne, bleibt sie zunächst leer und nimmt am Ende das Ergebnis auf (Check 02 der linearen Gleichungssysteme).
- Das Video bereitet auf die Trainingsaufgabe des Checks vor. Maßgeblich sind deren Teilaufgaben (Export unter `aufgaben/exports/json/<gebiet>/<lernbereich>/<sammlung>.json`, Arten der Teilaufgaben im zugehörigen Generator): Jede Art von Teilaufgabe soll im Video vorkommen oder bewusst weggelassen sein; nicht jede muss durchgerechnet werden. Das Bild entspricht dem der Aufgabe (etwa ein vollständig ausgefülltes Baumdiagramm).
- Ein Video trägt eine Kernidee. Das Musterbeispiel ist nur Orientierung: Es rechnet nicht immer die Trainingsaufgabe vor, sondern erläutert teils allgemeiner. Sachzusammenhang und Zahlen werden möglichst übernommen, aber das Video zeigt nur so viele Fälle, wie die Kernidee braucht (Check 05 der Binomialverteilung: fünf von dreizehn Ereignissen, je eines pro Schwierigkeit, und ein Lösungsweg statt zwei).
- Ein Check bekommt genau ein Video. Gehört zum Check auch die Abgrenzung (etwa „binomialverteilt oder nicht“), kommt sie als kurzer eigener Fall ins selbe Video.
- Nummern stehen nur für einen Ablauf. Checks ohne festen Rechenweg (Textverständnis, viele Fallarten, Diagramme lesen) bekommen keine nummerierten Schritte, sondern Abschnitte mit einfacher Überschrift oder mehrere kurze Fälle nach demselben Muster: Wortlaut, Bild, Rechnung.
- Geht es um das Lesen eines Diagramms, zeigt das Video vor allem, wo welche Größe steht und welche nicht dort steht. Die entscheidende Unterscheidung des Checks bekommt einen eigenen Abschnitt, in dem beide Fälle untereinander stehen (Check 03 der bedingten Wahrscheinlichkeiten: $P_A(B)$ ablesen, $P_B(A)$ rechnen).
- Das Video erklärt, wie es geht. Fehlerwarnungen gehören nicht hinein; nur eine bekannte Fehlvorstellung darf ausnahmsweise ausdrücklich angesprochen werden.
- Vor dem Schluss steht eine Kurzfassung ohne Überschrift, die den Tipps des Checks folgt: bei einem Ablauf die nummerierten Schritte oder Leitfragen (Baustein `kurzfassung`), sonst eine Übersicht ohne Nummern mit Punkten in der Stimmungsfarbe (Baustein `aufzaehlung`, etwa Stichwort und zugehörige Größen unter „ablesen“ und „rechnen“).
- Schluss: für alle Videos gleich und nicht je Video zu schreiben. Das Logo wandert aus der Ecke in die Bildmitte, dazu „Jetzt bist du dran.“ und die Adresse; gesprochen „Jetzt bist du dran. Bis zum nächsten Check!“. Text und Ton stehen in `MCSzene` (`schlussbild`, `schlusston`).
- Sprache: direkt, verbindlich und motivierend; „du“ in Einstieg und Schluss, „wir“ beim Rechnen. Lockere Wendungen und Anglizismen sind erlaubt, Fachbegriffe bleiben exakt wie im Skript des Lernbereichs.
- Das Bild muss ohne Ton verständlich sein. Der Sprechtext wird so geschrieben, wie er gesprochen wird („x Quadrat“). Eine eigene Untertiteldatei gibt es nicht; die automatischen Untertitel von YouTube genügen.
- Einblendungen hängen am Ton, nicht an festen Sekunden: `self.warte_bis(0.6)` wartet, bis 60 % des laufenden Sprechtexts gesprochen sind. So passen die Zeiten auch nach einem Stimmwechsel.
- Keine Originalaufgaben aus `muster-pruefungen/`.

## Gestaltung

Alles Gestalterische steht in `mcvideo/theme.py` und gilt nach dem Neurendern für alle Videos.

- Schrift wie auf der Website (Inter), Formeln setzt LaTeX. Wörter stehen nicht in Formeln, sondern als Text daneben (`reihe`). Steht eine kleine Formel (etwa $a'$) mitten in einem Satz, sitzen Text und Formel mit `reihe(..., grundlinie=True)` auf einer gemeinsamen Schriftgrundlinie, sonst wirkt die Formel zu tief.
- Zwei Farbebenen:
  - Stimmungsfarbe (`MARKE`, das Violett der Website), gedämpft und nur in Flächen und Rändern: Schimmer im Hintergrund, getönte Karte, Schrittnummern, Lichtpunkt beim Zeichnen, Schlussbild. Sie ist nie Schrift- oder Linienfarbe in der Rechnung und in allen Gebieten dieselbe, damit die Objektfarben in jedem Video dasselbe bedeuten.
  - Objektfarben, kräftig: Was zusammengehört, hat dieselbe Farbe, im Bild wie in der Rechnung. `HERVOR` (Orange) ist das Objekt, um das es gerade geht (Tangente und ihre Steigung, Kandidaten); `ROSE` und `BLAU` unterscheiden ein Paar (Hoch- und Tiefpunkt); `TUERKIS` und `GRUEN` stehen für weitere Objekte bereit. `BLAU` ist ein Himmelblau, damit es sich vom Violett absetzt.
- Text, Überschriften und Rechnung sind weiß.
- Objekte werden nur über die Schriftfarbe gekennzeichnet, ohne farbige Hinterlegung.
- Bewegung mit Bedeutung: `zeichnen` baut eine Linie mit mitlaufendem Lichtpunkt auf; `welle` markiert die Stelle, an der gerade etwas passiert; `auftritt` blendet Text ein.
- Bildaufteilung von oben nach unten: Kopf (Logo, Titel), Bühne auf einer Karte (`self.buehne()`), Tafel (Rechnung, Text). `self.tafel(...)`, `self.achsen(...)` und `self.auf_buehne(...)` passen Inhalte in ihren Bereich ein. `achsen` beschriftet die Achsen mit `namen=("x", "y")`; im Sachzusammenhang etwa `namen=("t", "a(t)")`.
- Die Höhe der Bühne richtet sich nach dem Bild: volle Höhe für einen Graphen, flach (`self.buehne(hoehe=2.5)`) für ein Bild, das nur begleitet, etwa den `Zahlenstrahl`. Die Tafel rückt dann nach oben und bekommt mehr Platz; die Schrift darf dort größer sein. So bleibt auch bei textlastigen Checks ohne tragendes Bild die obere Bildhälfte nicht leer.
- Ein Bild stützt jedes Video, auch textlastige: Auf dem `Zahlenstrahl` erscheint der Bereich, von dem der Text spricht; `Versuche` zeigt einzelne Versuche, wenn es nicht um eine Anzahl geht.
- Matrizen: `ErweiterteMatrix` zeigt ein LGS in Matrixform mit Zeilennamen. Umformungen stehen wie im Heft rechts neben der Zeile; die Nebenrechnung darunter steht in denselben Spalten (`zahlenzeile`), danach wird die Zeile ersetzt (`umformen`). Zeilennamen sind aufrechte römische Zahlen.
- Baumdiagramme: `Baumdiagramm` zeigt zwei Ereignisse A und B wie auf der Website (von links nach rechts, Wahrscheinlichkeiten an den Ästen, Produkte an den Pfadenden). `markiere` färbt die Äste und Pfadenden, um die es gerade geht, in der Farbe der zugehörigen Zahlen in der Rechnung.
- Ein Wert, der weiterverwendet wird, behält seine Farbe und wandert sichtbar an die Stelle, an der er eingesetzt wird (Rückwärtseinsetzen).
- Bleibt unter der Rechnung Platz frei, rückt `self.tafel(...)` den Block ein Stück nach unten (`TAFEL_LAGE` in `theme.py`), damit das Bild gleichmäßiger gefüllt ist. Leere Flächen sind in Ordnung.
- Zeichen und ihre Bedeutung stehen zweispaltig bündig (`legende`).
- Sichtbarer Bereich: Der untere Rand und die Bedienleiste rechts unten bleiben frei, weil die Shorts-Oberfläche sie überdeckt. Die Werte in `theme.py` sind Richtwerte und noch nicht am Handy geprüft.
- Zahlen mit Dezimalkomma: `Dezimalzahl` statt `DecimalNumber`.

## Stimme

Entwürfe sprechen mit gTTS (kostenlos, braucht Internet). Der Ton wird je Sprechabschnitt in `media/voiceovers/` zwischengespeichert; ändert sich ein Text, wird nur dieser Abschnitt neu erzeugt. Die Entwurfsstimme wird an einer Stelle gewechselt, in `mcvideo/stimme.py`.

### Eigene Stimme einsprechen

Erst wenn Bild und Text stehen (Entwurf mit der Entwurfsstimme abgenommen), wird eingesprochen:

```powershell
videos\.venv\Scripts\python videos\aufnahme.py videos\checks\<gebiet>\<lernbereich>\<NN>-<sammlung>.py
```

Das öffnet eine lokale Seite im Browser (beim ersten Mal das Mikrofon freigeben). Sie zeigt je Sprechabschnitt den stummen Videoausschnitt und groß den Sprechtext.

| Taste | Wirkung |
|---|---|
| Leertaste | Aufnahme starten; während der Aufnahme: speichern und direkt den nächsten Abschnitt aufnehmen |
| Enter | Aufnahme beenden und speichern |
| Esc | Aufnahme verwerfen |
| A | Aufnahme des gewählten Abschnitts zum Videoausschnitt anhören |
| ↑ ↓ | Abschnitt wählen (oder in der Liste anklicken) |

- Ein Abschnitt lässt sich beliebig oft neu aufnehmen; die neue Aufnahme ersetzt die alte. Stille und Tastenanschlag an Anfang und Ende werden abgeschnitten, die Lautstärke wird angeglichen.
- „Entwurf neu rendern“ baut das Video mit den Aufnahmen: Die Einblendungen richten sich dann nach der eigenen Sprechdauer. Danach „Ganzes Video ansehen“.
- „Final rendern“ entspricht `render.py --final`. Ein finales Video entsteht nur mit einer Stimme: entweder sind alle Abschnitte eingesprochen oder keiner.
- Die Aufnahmen liegen als MP3 unter `videos/aufnahmen/<gebiet>/<lernbereich>/<NN>-<sammlung>/` (derselbe Teilpfad wie die Szene) und gehören ins Repo: Zusammen mit der Szene sind sie die Quelle des fertigen Videos. `render.py` verwendet sie automatisch.
- Eine Aufnahme gehört zu genau einem Sprechtext (Kennung am Ende des Dateinamens). Wird der Text geändert, spricht diesen Abschnitt wieder die Entwurfsstimme, bis er neu aufgenommen ist; `render.py` nennt die betroffenen Abschnitte in der Zeile „Stimme“.
- Begrüßung und Schluss werden für jedes Video neu gesprochen, nicht zentral gespeichert.

## Offen

- sichtbaren Bereich mit einem Testvideo am Handy prüfen
- Ablage der fertigen Videos, Upload, Einbindung in die Website
- `abspann.mp4` und `abspann.pptx` sind der frühere Abspann und werden von den neuen Videos nicht verwendet
