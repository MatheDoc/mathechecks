# Erklärvideos (Pilot)

Kurzvideos im Hochformat (YouTube Shorts, TikTok), eines pro Check, erzeugt mit [Manim](https://www.manim.community/) und `manim-voiceover`.

Stand: Pilot mit einem Video (Check 06 der Differentialrechnung). Die Regeln unten sind ein Arbeitsstand; Agent und Skill folgen erst nach weiteren Pilotvideos. Die Videos sind noch nicht in die Website eingebunden, der Ordner ist von Jekyll ausgeschlossen.

## Aufbau

```text
videos/
  render.py                 einziger Einstieg zum Rendern
  requirements.txt
  mcvideo/                  gemeinsame Bibliothek
    theme.py                Farben, Schrift, Bildaufteilung, Auflösung
    szene.py                Basisszene MCSzene: Logo, Bereiche, Ton, Schlusskarte, Randprüfung
    bausteine.py            Schritt, Stolperstein, Rezept, Dezimalzahl, …
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

1. **Szene** schreiben: Klasse `Video(MCSzene)` mit `kompetenz`, `schlusssatz` und `inhalt()`. Im Kopf der Datei stehen zwei Zeilen: die Kernidee und ob das Beispiel vom Musterbeispiel abweicht. Vorlage: `checks/analysis/differentialrechnung-ganzrationaler-funktionen/06-extremstellen-bestimmen.py`.
2. **Entwurf** rendern (540 × 960, etwa eine Minute):

   ```powershell
   videos\.venv\Scripts\python videos\render.py videos\checks\<gebiet>\<lernbereich>\<NN>-<sammlung>.py
   ```

   Ausgegeben werden Dauer, Wortzahl und alle Objekte außerhalb des sichtbaren Bereichs.
3. **Prüfbogen** durchsehen: `media/pruefung/<check_id>/pruefbogen.md` zeigt je Sprechabschnitt das Standbild mit Sprechtext und Untertitel (Überlappungen, Lesbarkeit, fachliche Richtigkeit). Er wird bei jedem Entwurf neu erzeugt.
4. **Final** rendern (1080 × 1920, 30 Bilder pro Sekunde) mit `--final`. Video und Untertiteldatei landen in `ausgabe/<check_id>.mp4` und `.srt`. Bei Randverstößen wird nichts ausgegeben.

## Regeln für ein Video

- Umfang: Ziel 60–90 Sekunden, Richtwert höchstens 200 Wörter Sprechtext, Obergrenze 180 Sekunden.
- Das Video beginnt mit einer konkreten Frage. Das erste Bild ist nicht leer, es gibt keinen Vorspann.
- Ein Video trägt eine Kernidee. Die Rechnung stammt in der Regel aus dem Musterbeispiel; ist es zu lang, wird ein kleineres Beispiel gewählt oder nur der entscheidende Schritt gezeigt.
- Fester Baustein „Stolperstein“: ein typischer Fehler.
- „Dein Rezept“ fasst die Schritte zusammen und folgt den Tipps des Checks.
- Schluss: Der Kompetenzsatz wird abgehakt, gesprochen „… ? Check!“.
- Begriffe und Schreibweisen wie im Skript des Lernbereichs.
- Das Bild muss ohne Ton verständlich sein. Der Sprechtext wird so geschrieben, wie er gesprochen wird („x Quadrat“); weicht die Lesefassung ab, steht sie als `untertitel` daneben.
- Keine Originalaufgaben aus `muster-pruefungen/`.

## Gestaltung

Alles Gestalterische steht in `mcvideo/theme.py` und gilt nach dem Neurendern für alle Videos.

- Farben und Schrift folgen der Website (`assets/css/shared.css`, Inter). Formeln setzt LaTeX.
- Farbrollen: `HERVOR` lenkt den Blick, `ROSE` und `BLAU` unterscheiden zwei Objekte (etwa Hoch- und Tiefpunkt), `GRUEN` gehört nur dem Check-Häkchen.
- Bildaufteilung von oben nach unten: Kopf (Logo, Titel), Bühne (Graph, Skizze), Tafel (Rechnung, Text). `self.tafel(...)` und `self.achsen(...)` passen Inhalte in ihren Bereich ein.
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
