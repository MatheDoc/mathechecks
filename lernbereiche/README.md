# Lernbereiche – Modultypen

Jeder Lernbereich besteht aus einem definierten Set an Seiten.

Verbindliche Modultypen pro Lernbereich: `start`, `warmup`, `training`, `recall`, `feynman`, `kompetenzliste`, `skript`, `flashcards`.

→ Datenmodell & Architektur: `.github/datenmodell.md`

| Modul | Zweck | Didaktischer Kern | Zusammenhang mit anderen Modulen |
|---|---|---|---|
| **Start** | Überblick, Vorwissen, optionaler Audio-Überblick | Orientierung, Motivation | Natürlicher Feed-Einstieg pro Lernbereich vor den ersten checkbezogenen Aktivitäten |
| **Warm-Up** | Kurzer motivierender Einstieg (4 Karten) | Vorwissensaktivierung, kognitive Aktivierung, Neugier wecken | Derzeit bewusst nicht Teil der aktuellen Feed-Kette |
| **Kompetenzliste** | Übersicht aller Kompetenzen des Lernbereichs | Lernziel-Orientierung | Jede Kompetenz ist mit Training und Skript verknüpft |
| **Training** | Interaktive Aufgaben | Üben mit formativem Feedback | Zu jeder Kompetenz in der Kompetenzliste gibt es genau eine Aufgabensammlung im Training |
| **Recall** | Geführter Abruf der Kernideen eines Checks | Active Recall mit Selbstüberprüfung | Zwischenmodul in der Feed-Kette vor dem zweiten Training |
| **Feynman** | Erklären einer Technik/eines Sachverhalts | Elaboration und tieferes Verständnis | Zwischenmodul in der Feed-Kette vor dem dritten Training |
| **Skript** | Mathematische Inhalte | Einführen, Verstehen, Nachschlagen, Beispiele mit Fading | Zu jedem Check gibt es einen Check-Anker |
| **Flashcards** | Begriffe, Formeln, Zusammenhänge wiederholen | Retrieval Practice, Spaced Repetition | Karteninhalt aus Aufgaben; im Feed serverseitige Durchgänge und Fälligkeiten, frei ohne Persistenz |

`checks.json` enthält die verbindliche Zuordnung der Checks zu Kompetenzliste, Training, Recall, Feynman, Skript und Flashcards.

Konvention für Start-Podcasts:

- Ein Podcast zum Lernbereich liegt standardmäßig unter `lernbereiche/<gebiet>/<lernbereich>/medien/podcast.m4a`.
- Die Startseite nutzt diesen Pfad automatisch, auch ohne zusätzlichen YAML-Eintrag.
- Falls nötig, kann der Standardpfad im Start-Datensatz weiterhin über `podcast.audio_url` überschrieben werden.
- Ein `podcast`-Block in `_data/start/<lernbereich>.yml` ist nur noch optional für `title`, `description`, `transcript_url` oder `credit`.
