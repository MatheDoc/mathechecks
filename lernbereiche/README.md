# Lernbereiche – Modultypen

Jeder Lernbereich besteht aus einem definierten Set an Seiten.

Verbindliche Modultypen pro Lernbereich: `start`, `training`, `recall`, `feynman`, `test`, `kompetenzliste`, `skript`, `flashcards`.

Zusätzlich, nicht verlinkt:

- `warmup` – geführter Einstieg pro Check, nur in Lernbereichen mit Warm-Up (→ `_data/warmup/README.md`).
- `vertiefung.md` – Platzhalter mit Ideen für weiterführende Fragen, ohne Navigation.

→ Ablage der Inhalte: `.github/datenmodell.md` · Inhaltliche Ziele: `.github/inhalte.md`

| Modul | Zweck | Didaktischer Kern | Zusammenhang mit anderen Modulen |
|---|---|---|---|
| **Start** | Überblick, Vorwissen, optionaler Audio-Überblick | Orientierung, Motivation | Natürlicher Feed-Einstieg pro Lernbereich vor den ersten checkbezogenen Aktivitäten |
| **Warm-Up** *(nicht verlinkt)* | Geführter Einstieg in einen Check | Lernen am vorgerechneten Beispiel, Fading | Pro Check vor dem Training; derzeit nicht verlinkt und nicht im Feed |
| **Kompetenzliste** | Übersicht aller Kompetenzen des Lernbereichs | Lernziel-Orientierung | Jede Kompetenz ist mit Training und Skript verknüpft |
| **Training** | Interaktive Aufgaben | Üben mit formativem Feedback | Zu jeder Kompetenz in der Kompetenzliste gibt es genau eine Aufgabensammlung im Training |
| **Recall** | Geführter Abruf der Kernideen eines Checks | Active Recall mit Selbstüberprüfung | Zweites Glied der Check-Kette nach dem Training |
| **Feynman** | Erklären einer Technik/eines Sachverhalts | Elaboration und tieferes Verständnis | Drittes Glied der Check-Kette nach dem Recall |
| **Test** | 10 Single-Choice-Fragen pro Check, ohne Hilfsmittel | Schneller Kompetenz-Abruf mit Erfolgsquote | Letztes Glied der Check-Kette; schließt den Check im Feed ab |
| **Skript** | Mathematische Inhalte | Einführen, Verstehen, Nachschlagen, Beispiele mit Fading | Zu jedem Check gibt es einen Check-Anker |
| **Flashcards** | Begriffe, Formeln, Zusammenhänge wiederholen | Retrieval Practice, Spaced Repetition | Karteninhalt aus Aufgaben; im Feed serverseitige Durchgänge und Fälligkeiten, frei ohne Persistenz |

`_data/checks.json` enthält die verbindliche Zuordnung der Checks zu Kompetenzliste, Training, Recall, Feynman, Test, Skript und Flashcards.

Konvention für Start-Podcasts:

- Ein Podcast zum Lernbereich liegt standardmäßig unter `lernbereiche/<gebiet>/<lernbereich>/medien/podcast.mp3`.
- Die Startseite nutzt diesen Pfad automatisch, auch ohne zusätzlichen YAML-Eintrag.
- Falls nötig, kann der Standardpfad im Start-Datensatz weiterhin über `podcast.audio_url` überschrieben werden.
- Ein `podcast`-Block in `_data/start/<lernbereich>.yml` ist nur noch optional für `title`, `description`, `transcript_url` oder `credit`.
