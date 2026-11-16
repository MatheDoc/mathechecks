---
name: video-erstellen
description: Erklärvideo (Kurzvideo im Hochformat) für einen Check erstellen oder überarbeiten – Inhalt im Chat vorstellen, Szene schreiben, rendern, prüfen.
disable-model-invocation: true
---
# Erklärvideo erstellen oder überarbeiten

Eingabe: Check (Lernbereich und Nummer) und Auftrag. Verbindlich: `videos/README.md` (Regeln für ein Video, Gestaltung, Bausteine, Befehle).

## 1. Quellen lesen

- `_data/checks.json`: `Ich kann`, `Tipps`, `Sammlung`.
- **Trainingsaufgabe** (darauf bereitet das Video vor): eine Aufgabe aus `aufgaben/exports/json/<gebiet>/<lb>/<sammlung>.json` und die Arten der Teilaufgaben im zugehörigen Generator.
- Musterbeispiel in `lernbereiche/<gebiet>/<lb>/beispiele/` (Sachzusammenhang, Zahlen), Skript-Abschnitt zum Check (Begriffe, Schreibweisen), Warm-Up, falls vorhanden.
- Die passende Vorlage aus `videos/README.md`, Abschnitt „Vorlagen“.

## 2. Inhalt im Chat vorstellen (vor der Szene)

Knapp und nur inhaltlich, ohne Gestaltung und Animationen:

- Frage (ggf. Zusatz), Kernidee, Beispiel und Abweichungen vom Musterbeispiel
- Tabelle: Abschnitt | Text und Formeln im Bild | Sprechtext
- Kurzfassung am Schluss
- Teilaufgaben des Trainings: abgedeckt oder bewusst weggelassen

Erst nach Zustimmung weiter mit Schritt 3.

## 3. Szene schreiben

- `videos/checks/<gebiet>/<lb>/<NN>-<sammlung>.py`, Klasse `Video(MCSzene)`; im Kopf der Datei Kernidee und Bezug zum Musterbeispiel.
- Alle Zahlen per Skript nachrechnen.
- Wiederverwendbares gehört als Baustein nach `videos/mcvideo/` und in `videos/README.md`, nicht in die Szene.

## 4. Rendern und prüfen

1. Entwurf rendern, gemeldete Randverstöße beheben.
2. Standbilder des Prüfbogens ansehen:
   - keine Überlappungen, alles lesbar; eine zu breite oder zu hohe Zeile verkleinert unbemerkt den ganzen Block
   - Bild und Sprechtext passen in jedem Abschnitt zusammen
   - Farben nach den Regeln: gleiche Farbe für Zusammengehöriges im Bild und in der Rechnung
3. Dauer und Wortzahl mit den Zielwerten vergleichen.
4. Nach Änderungen an `videos/mcvideo/` eine andere Szene als Entwurf rendern.
5. Final rendern.

## Überarbeiten

- Die Szene vor jeder Änderung neu lesen; Änderungen des Nutzers bleiben erhalten.
- Gibt es Aufnahmen unter `videos/aufnahmen/<gebiet>/<lb>/<NN>-<sammlung>/`, Sprechtexte nur nach Rückfrage ändern: Jede Änderung macht die Aufnahme des Abschnitts ungültig.
- Schritt 2 nur für die geänderten Abschnitte.

## Ausgabe

- Pfad des fertigen Videos, Dauer, Wortzahl, Stimme
- geprüft und nicht geprüft (Ton und Bewegung nur nennen, wenn sie wirklich geprüft wurden)
- weggelassene Teilaufgaben, offene Entscheidungen, in den Quellen korrigierte Fehler
