# Erklärvideos (Pilot)

Kurzvideos im Hochformat (YouTube Shorts, TikTok), eines pro Check, erzeugt mit [Manim](https://www.manim.community/) und `manim-voiceover`.

Stand: Pilot mit zwei Videos (Check 06 der Differentialrechnung: Rechenverfahren mit tragendem Graphen; Check 05 der Binomialverteilung: Textverständnis ohne tragendes Bild). Die Regeln unten sind ein Arbeitsstand; Agent und Skill folgen erst nach weiteren Pilotvideos. Die Videos sind noch nicht in die Website eingebunden, der Ordner ist von Jekyll ausgeschlossen.

## Aufbau

```text
videos/
  render.py                 einziger Einstieg zum Rendern
  requirements.txt
  mcvideo/                  gemeinsame Bibliothek
    theme.py                Farben, Schrift, Bildaufteilung, Auflösung
    szene.py                Basisszene MCSzene: Logo, Bereiche, Ton, Schlussbild, Randprüfung
    bausteine.py            Frage, Schritt, Kurzfassung, Legende, Zahlenstrahl, Versuche, Dezimalzahl, …
    stimme.py               Sprachdienst (zentral umschaltbar)
    fonts/                  Inter (SIL Open Font License)
  checks/<gebiet>/<lernbereich>/<NN>-<sammlung>.py   Szene eines Checks
  media/                    Zwischenstände, Tonzwischenspeicher, Prüfbögen (gitignored)
  ausgabe/                  fertige Videos und Untertitel (gitignored)
```

Die Szene heißt wie das Musterbeispiel des Checks und ist die einzige Quelle des Videos. Aus dem Pfad ergibt sich die `check_id`; `render.py` bricht ab, wenn es sie in `_data/checks.json` nicht gibt.

## Einrichten

```powershell
python -m venv videos\.venv
videos\.venv\Scripts\python -m pip install -r videos\requirements.txt
```

Zusätzlich nötig: LaTeX (MiKTeX) für die Formeln und eine Internetverbindung für die Entwurfsstimme. Getestet mit Python 3.14.

## Ablauf

1. **Szene** schreiben: Klasse `Video(MCSzene)` mit der Methode `inhalt()`, die mit `self.einstieg(...)` beginnt. Im Kopf der Datei stehen zwei Zeilen: die Kernidee und ob das Beispiel vom Musterbeispiel abweicht. Vorlage: `checks/analysis/differentialrechnung-ganzrationaler-funktionen/06-extremstellen-bestimmen.py`.
2. **Entwurf** rendern (540 × 960, etwa eine Minute):

   ```powershell
   videos\.venv\Scripts\python videos\render.py videos\checks\<gebiet>\<lernbereich>\<NN>-<sammlung>.py
   ```

   Ausgegeben werden Dauer, Wortzahl und alle Objekte außerhalb des sichtbaren Bereichs.
3. **Prüfbogen** durchsehen: `media/pruefung/<check_id>/pruefbogen.md` zeigt je Sprechabschnitt das Standbild mit Sprechtext und Untertitel (Überlappungen, Lesbarkeit, fachliche Richtigkeit). Er wird bei jedem Entwurf neu erzeugt.
4. **Final** rendern (1080 × 1920, 30 Bilder pro Sekunde) mit `--final`. Video und Untertiteldatei landen in `ausgabe/<check_id>.mp4` und `.srt`. Bei Randverstößen wird nichts ausgegeben.

## Regeln für ein Video

- Umfang: Ziel 60–90 Sekunden, Richtwert höchstens 200 Wörter Sprechtext, Obergrenze 180 Sekunden.
- Einstieg (für alle Videos gleich, `self.einstieg(...)`):
  1. Ein kennzeichnendes Bild entsteht, am besten eines, mit dem das Video weiterarbeitet (hier der Graph), sonst ein Bild mit Symbolcharakter. Das erste Bild ist nicht leer.
  2. Dazu erscheint die Frage, gesprochen und geschrieben, weiß und ohne Farbcode. Sie steht in der Du-Form und benennt das Thema sofort, nach dem Muster „Wie bestimmst du Hoch- und Tiefpunkte?“ (der umgedrehte Kompetenzsatz des Checks).
  3. Begrüßung: Logo und Name erscheinen unter der Frage, gesprochen wird `MCSzene.begruessung`.
  4. Das Logo wandert in die Ecke und bleibt dort; erst jetzt erscheint die Kopfzeile.
- Die Kopfzeile ist freiwillig. Sie zeigt das Gegebene, auf das sich die Rechnung durchgehend bezieht (etwa den Funktionsterm), sonst bleibt sie leer.
- Ein Video trägt eine Kernidee. Das Musterbeispiel ist nur Orientierung: Sachzusammenhang und Zahlen werden möglichst übernommen, aber das Video zeigt nur so viele Fälle, wie die Kernidee braucht (Check 05 der Binomialverteilung: fünf von dreizehn Ereignissen, je eines pro Schwierigkeit, und ein Lösungsweg statt zwei).
- Ein Check bekommt genau ein Video. Gehört zum Check auch die Abgrenzung (etwa „binomialverteilt oder nicht“), kommt sie als kurzer eigener Fall ins selbe Video.
- Checks ohne festen Rechenweg (Textverständnis, viele Fallarten) bekommen keine nummerierten Schritte, sondern mehrere kurze Fälle nach demselben Muster: Wortlaut, Bild, Rechnung. Die nummerierte Kurzfassung am Ende nennt dann die Leitfragen.
- Das Video erklärt, wie es geht. Fehlerwarnungen gehören nicht hinein; nur eine bekannte Fehlvorstellung darf ausnahmsweise ausdrücklich angesprochen werden.
- Vor dem Schluss fasst eine nummerierte Kurzfassung die Schritte zusammen (Baustein `kurzfassung`, ohne Überschrift). Sie folgt den Tipps des Checks.
- Schluss: für alle Videos gleich und nicht je Video zu schreiben. Das Logo wandert aus der Ecke in die Bildmitte, dazu „Jetzt bist du dran.“ und die Adresse; gesprochen „Jetzt bist du dran. Bis zum nächsten Check!“. Text und Ton stehen in `MCSzene` (`schlussbild`, `schlusston`).
- Sprache: direkt, verbindlich und motivierend; „du“ in Einstieg und Schluss, „wir“ beim Rechnen. Lockere Wendungen und Anglizismen sind erlaubt, Fachbegriffe bleiben exakt wie im Skript des Lernbereichs.
- Das Bild muss ohne Ton verständlich sein. Der Sprechtext wird so geschrieben, wie er gesprochen wird („x Quadrat“); weicht die Lesefassung ab, steht sie als `untertitel` daneben.
- Einblendungen hängen am Ton, nicht an festen Sekunden: `self.warte_bis(0.6)` wartet, bis 60 % des laufenden Sprechtexts gesprochen sind. So passen die Zeiten auch nach einem Stimmwechsel.
- Keine Originalaufgaben aus `muster-pruefungen/`.

## Gestaltung

Alles Gestalterische steht in `mcvideo/theme.py` und gilt nach dem Neurendern für alle Videos.

- Schrift wie auf der Website (Inter), Formeln setzt LaTeX. Wörter stehen nicht in Formeln, sondern als Text daneben (`reihe`).
- Zwei Farbebenen:
  - Stimmungsfarbe (`MARKE`, das Violett der Website), gedämpft und nur in Flächen und Rändern: Schimmer im Hintergrund, getönte Karte, Schrittnummern, Lichtpunkt beim Zeichnen, Schlussbild. Sie ist nie Schrift- oder Linienfarbe in der Rechnung und in allen Gebieten dieselbe, damit die Objektfarben in jedem Video dasselbe bedeuten.
  - Objektfarben, kräftig: Was zusammengehört, hat dieselbe Farbe, im Bild wie in der Rechnung. `HERVOR` (Orange) ist das Objekt, um das es gerade geht (Tangente und ihre Steigung, Kandidaten); `ROSE` und `BLAU` unterscheiden ein Paar (Hoch- und Tiefpunkt); `TUERKIS` und `GRUEN` stehen für weitere Objekte bereit. `BLAU` ist ein Himmelblau, damit es sich vom Violett absetzt.
- Text, Überschriften und Rechnung sind weiß.
- Objekte werden nur über die Schriftfarbe gekennzeichnet, ohne farbige Hinterlegung.
- Bewegung mit Bedeutung: `zeichnen` baut eine Linie mit mitlaufendem Lichtpunkt auf; `welle` markiert die Stelle, an der gerade etwas passiert; `auftritt` blendet Text ein.
- Bildaufteilung von oben nach unten: Kopf (Logo, Titel), Bühne auf einer Karte (`self.buehne()`), Tafel (Rechnung, Text). `self.tafel(...)`, `self.achsen(...)` und `self.auf_buehne(...)` passen Inhalte in ihren Bereich ein.
- Die Höhe der Bühne richtet sich nach dem Bild: volle Höhe für einen Graphen, flach (`self.buehne(hoehe=2.5)`) für ein Bild, das nur begleitet, etwa den `Zahlenstrahl`. Die Tafel rückt dann nach oben und bekommt mehr Platz; die Schrift darf dort größer sein. So bleibt auch bei textlastigen Checks ohne tragendes Bild die obere Bildhälfte nicht leer.
- Ein Bild stützt jedes Video, auch textlastige: Auf dem `Zahlenstrahl` erscheint der Bereich, von dem der Text spricht; `Versuche` zeigt einzelne Versuche, wenn es nicht um eine Anzahl geht.
- Bleibt unter der Rechnung Platz frei, rückt `self.tafel(...)` den Block ein Stück nach unten (`TAFEL_LAGE` in `theme.py`), damit das Bild gleichmäßiger gefüllt ist. Leere Flächen sind in Ordnung.
- Zeichen und ihre Bedeutung stehen zweispaltig bündig (`legende`).
- Sichtbarer Bereich: Der untere Rand und die Bedienleiste rechts unten bleiben frei, weil die Shorts-Oberfläche sie überdeckt. Die Werte in `theme.py` sind Richtwerte und noch nicht am Handy geprüft.
- Zahlen mit Dezimalkomma: `Dezimalzahl` statt `DecimalNumber`.

## Stimme

Entwürfe sprechen mit gTTS (kostenlos, braucht Internet). Der Ton wird je Sprechabschnitt in `media/voiceovers/` zwischengespeichert; ändert sich ein Text, wird nur dieser Abschnitt neu erzeugt. Gewechselt wird die Stimme an einer Stelle, in `mcvideo/stimme.py`.

Selbst einsprechen geht mit dem `RecorderService` von `manim-voiceover`: Beim Rendern zeigt das Terminal je Abschnitt den Sprechtext, aufgenommen wird, solange die Taste `r` gedrückt ist, danach anhören, wiederholen oder annehmen. Auch diese Aufnahmen werden zwischengespeichert. Voraussetzungen: `pip install "manim-voiceover[recorder]"` (PyAudio gibt es derzeit nur bis Python 3.13) und `ffmpeg` im Pfad. Hier noch nicht eingerichtet und nicht getestet.

## Offen

- sichtbaren Bereich mit einem Testvideo am Handy prüfen
- endgültige Stimme
- Ablage der fertigen Videos, Upload, Einbindung in die Website
- `abspann.mp4` und `abspann.pptx` sind der frühere Abspann und werden von den neuen Videos nicht verwendet
