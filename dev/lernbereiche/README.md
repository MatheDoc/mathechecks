# Lernbereiche – Modultypen

Jeder Lernbereich besteht aus einem definierten Set an Seiten.

Verbindliche Modultypen pro Lernbereich: `start`, `warmup`, `training`, `blurting`, `feynman`, `kompetenzliste`, `skript`, `flashcards`.

→ Datenmodell & Architektur: `.github/datenmodell.md`

| Modul | Zweck | Didaktischer Kern | Zusammenhang mit anderen Modulen |
|---|---|---|---|
| **Start** | Überblick, Vorwissensaktivierung | Orientierung, Motivation | 
| **Warm-Up** | Kurzer motivierender Einstieg (4 Karten) | Vorwissensaktivierung, kognitive Aktivierung, Neugier wecken | Startpunkt der Feed-Kette, danach erster Trainingsschritt |
| **Kompetenzliste** | Übersicht aller Kompetenzen des Lernbereichs | Lernziel-Orientierung | Jede Kompetenz ist mit Training und Skript verknüpft |
| **Training** | Interaktive Aufgaben | Üben mit formativem Feedback | Zu jeder Kompetenz in der Kompetenzliste gibt es genau eine Aufgabensammlung im Training |
| **Blurting** | Stichwortartiger Abruf eines Begriffs | Active Recall mit Selbstüberprüfung | Zwischenmodul in der Feed-Kette vor dem zweiten Training |
| **Feynman** | Erklären einer Technik/eines Sachverhalts | Elaboration und tieferes Verständnis | Zwischenmodul in der Feed-Kette vor dem dritten Training |
| **Skript** | Mathematische Inhalte | Einführen, Verstehen, Nachschlagen, Beispiele mit Fading | Zu jedem Check gibt es einen Check-Anker |
| **Flashcards** | Begriffe, Formeln, Zusammenhänge wiederholen | Retrieval Practice, Spaced Repetition | Zu jeder Aufgabe, ggf. zu jeder Frage einer Aufgabe, gibt es eine Flashcard |

`checks.json` enthält die verbindliche Zuordnung der Checks zu Kompetenzliste, Training, Blurting, Feynman, Skript und Flashcards.
