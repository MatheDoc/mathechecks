# Konzept: Lernarchitektur MatheChecks

Dieses Dokument beschreibt die Struktur, Typen und Zusammenhänge aller Lernelemente im Projekt.
Es ist Grundlage für Systemprompts, Agent-Rollen und didaktische Qualitätsentscheidungen.

---

## 1) Ebenen der Lernarchitektur

```
Lernmethoden  (didaktische Prinzipien – anwendbar auf alle Ebenen)
      │
      ├── Lernbereich  (Inhaltsbereich, z. B. „Marktgleichgewicht")
      │       ├── Seiten/Module (Skript, Checkliste, Training, Flashcards, ...)
      │       └── Kompetenz-Aufgabe-Skript-Kette
      │
      └── Aktionsfeed  (dynamische Lernsteuerung, kontextabhängig)
              └── Feed-Einträge (Aktionstypen, zeitlich und progressionsabhängig)
```

---

## 2) Lernbereiche – Modultypen

Jeder Lernbereich besteht aus einem definierten Set an Seiten.

| Modul | Zweck | Didaktischer Kern |
|Zusammenhang mit anderen Modulen|---|---|
| **Start** | Überblick, Vorwissensaktivierung, Exportmöglichkeiten (Moodle, Anki) | Orientierung, Motivation, Einstiegsquiz mit vorausschauenden Erklärungen| ... |
| **Checkliste** | Übersicht aller Kompetenzen des Lernbereichs | Lernziel-Orientierung |
| **Training** | interaktive Aufgaben | Üben mit formativem Feedback | zu jeder Kompetenz in der Checkliste gibt es genau eine Aufgabe im Training|
| **Skript** | mathematische Inhalte | Einführen, Verstehen, Nachschlagen, Beispiele mit Fading | zu jeder Aufgabe aus Training gibt es im Skript eine Hilfestellung (aktuell im include info) |
| **Flashcards** | Begriffe, Formeln, Zusammenhänge wiederholen | Retrieval Practice, Spaced Repetition | zu jeder Aufgabe, ggfs. zu jeder Frage einer Aufgabe, gibt eine Flashcard |

`kompetenzliste.json` enthält die verbindliche Zuordnung von Kompetenzen zu Checkliste, Aufgaben im Training und Skript. Flashcards werden automatisch aus den Trainingsaufgaben generiert. 

## 3) Kompetenz-Aufgabe-Skript-Kette

Das Verknüpfungsprinzip ist für alle Module verbindlich:

```
Kompetenz (Checkliste)
    └── Aufgabe(n) (Training)
            └── Skriptabschnitt (Skript)
```

- Dieselben Kernbegriffe und Symbole in allen drei Stufen.
- Zu jeder Kompetenz: mindestens eine Trainingsaufgabe und ein Skriptbezug.
- Neue Inhalte immer entlang dieser Kette denken.

---

## 4) Aktionsfeed – Eintragstypen

Der Feed steuert, was Schüler:innen als Nächstes tun sollen.

### Übersicht

| Typ | Digital? | Status | Auslöser |
|---|:---:|---|---|
| `einstiegsquiz` | ✓ | 🔲 geplant | Lernbereich erstmals aktiviert |
| `training` | ✓ | ✅ Basis implementiert | Nächster offener Check; spaced repetition für abgeschlossene Checks |
| `flashcards` | ✓ | ✅ Basis implementiert | Alle Checks einmal bearbeitet |
| `checkliste` | ✓ | 🔲 geplant (Selbsteinschätzung fehlt) | Festes Intervall (z. B. alle x Tage) |
| `blurting` | ✗ | 🔲 geplant | Nach Checks, die den jeweiligen Begriff abdecken |
| `feynman` | ✗ | 🔲 geplant | Nach Checks zu einer abgeschlossenen Technik |
| `skript` | ✗ | ❓ offen | Vor/nach Trainingsblock — Struktur unklar |
| `klausur` | ✓ | 🔲 langfristig | Mehrere LBs ausreichend trainiert |
| `review` | ✓ | ❓ offen | Siehe unten |

---

### Typen im Detail

#### `einstiegsquiz`
- **Zweck:** Vorwissen aktivieren, Einstieg in den Lernbereich motivieren, vorausschauend zeigen „wo die Reise hingeht"
- **Aufbau:** Einfache, motivierende Fragen (keine Zufallsgeneratoren nötig); vorausschauende Erklärungen eingebettet; interaktiv oder nicht — offen
- **Auslöser:** Lernbereich erstmals aktiviert
- **Nächste Aktion:** Erster Training-Check
- **Implementierung:** Muss pro Lernbereich manuell erstellt werden

#### `training`
- **Zweck:** Kernschleife — Kompetenz aufbauen durch schrittweisen Check-Fortschritt
- **Aufbau:**
  - Checks sequenziell: nächster Check erscheint erst, wenn vorheriger bearbeitet wurde
  - Option: zum nächsten Check übergehen, auch wenn vorheriger nicht 100 % richtig — fehlerhafter Check wird nach Intervall wiederholt
  - Spaced Repetition für abgeschlossene Checks: Wiederholung nach ansteigenden Zeitabständen
- **Auslöser:** Nächster offener / fälliger Check im aktiven Lernbereich
- **Implementierung:** Aufgaben kommen aus generierten JSONs; Progressionslogik und SR-Intervalle noch auszubauen

#### `flashcards`
- **Zweck:** Retrieval Practice für Begriffe, Formeln, Zusammenhänge
- **Auslöser:** Alle Checks eines Lernbereichs mindestens einmal bearbeitet
- **Implementierung:** Basis vorhanden; Intervalllogik prüfen

#### `checkliste`
- **Zweck:** Strukturierte Selbsteinschätzung der Kompetenzen eines Lernbereichs
- **Auslöser:** Festes Intervall (z. B. alle x Tage), sobald Training begonnen wurde
- **Implementierung:** Selbsteinschätzungsfunktion auf `kompetenzliste.md` fehlt noch; muss mit automatisch erfasstem Trainingsfortschritt abgeglichen werden (offen: wie genau?)

#### `blurting`
- **Zweck:** Active Recall — Schlüsselbegriffe ohne Vorlage erklären
- **Aufbau:** Dem/der Schüler:in wird ein Schlüsselbegriff präsentiert (z. B. „Vierfeldertafel") → freies Erklären/Aufschreiben; kein automatisches Feedback
- **Auslöser:** Nach den Checks, die diesen Begriff abdecken
- **Implementierung:** Schlüsselbegriffe pro Lernbereich müssen identifiziert und annotiert werden; Anzeige-UI einfach (Begriff anzeigen, Timer optional)

#### `feynman`
- **Zweck:** Tieferes Verständnis durch Erklären einer Methode/Technik
- **Aufbau:** Prompt der Art „Erkläre, wie man die Extrempunkte einer Funktion berechnet" → freies Erklären; kein automatisches Feedback
- **Unterschied zu Blurting:** Nicht ein Begriff, sondern eine Prozedur/Technik als Prompt
- **Auslöser:** Nach Checks, die die jeweilige Technik vollständig abdecken
- **Implementierung:** Ähnlich wie Blurting; Prompts müssen pro Technik definiert werden

#### `skript`
- **Zweck:** Geführte Leseeinheit zu einem Skriptabschnitt
- **Auslöser/Format:** Unklar — damit ein Feed-Eintrag Sinn ergibt (z. B. „Lies diesen Abschnitt 15 min"), müssten Skript-Abschnitte eindeutig adressierbar und passend strukturiert sein
- **Offene Frage:** Muss die Skriptstruktur dafür angepasst werden? Oder entfällt dieser Feed-Typ, da das Skript primär zum Nachschlagen genutzt wird?

#### `klausur`
- **Zweck:** Prüfungssimulation über mehrere Lernbereiche
- **Aufbau:** Kombination aus Trainingsaufgaben + erweitertem Kontext (kein reines Recycling)
- **Auslöser:** Mehrere Lernbereiche ausreichend trainiert
- **Implementierung:** Langfristig; Konzept für erweiterten Kontext noch offen

#### `review` ❓
- **Status:** Offen — zwei Optionen:
  - **Entfällt:** Spaced Repetition ist bereits in `training` integriert → kein separater Typ nötig
  - **Bleibt als lernbereichsübergreifender Typ:** Mischt fällige Checks aus mehreren abgeschlossenen Lernbereichen in einer Session → sinnvoll, wenn Schüler:innen mehrere LBs parallel bearbeiten
- **Entscheidung steht aus**

---

## 5) Lernmethoden

Didaktische Prinzipien, die quer zu Modulen und Feed-Einträgen angewendet werden.

| Methode | Beschreibung | Primäre Anwendung |
|---|---|---|
| **Retrieval Practice** | Aktives Abrufen statt passives Wiederlesen | Flashcards, Training, Blurting |
| **Spaced Repetition** | Wiederholungsabstände anhand Behaltenskurve | Review-Einträge, Flashcard-Intervalle |
| **Worked Examples** | Musterlösungen mit schrittweisem Fading | Skript, Training (Beispiel→Aufgabe) |
| **Kognitive Aktivierung** | Aufgaben, die echtes Denken erzwingen | Training, Einstiegs-Quiz |
| **Diagnose & Feedback** | Fehler typisieren + nächsten Schritt angeben | Training, Review, Einstieg |
| **Active Recall** | Inhalte ohne Vorlage reproduzieren | Blurting, Feynman, Flashcards |
| **Elaboration** | Neue Info mit Vorwissen vernetzen | Skript, Zusammenfassung |
| **Vorwissensaktivierung** | Anknüpfen an bekannte Konzepte | Einstieg, Skript-Einleitung |
| **Metakognition** | Sicherheits- und Plausibilitätschecks | Checkliste, Trainings-Feedback |

---

## 6) Welche Lernmethoden gelten wo?

| Methode | Skript | Training | Flashcards | Einstieg | Review | Blurting/Feynman |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Retrieval Practice | – | ✓ | ✓ | – | ✓ | ✓ |
| Spaced Repetition | – | – | ✓ | – | ✓ | – |
| Worked Examples | ✓ | ✓ | – | – | – | – |
| Kognitive Aktivierung | – | ✓ | ✓ | ✓ | ✓ | – |
| Diagnose & Feedback | – | ✓ | – | ✓ | ✓ | – |
| Active Recall | – | – | ✓ | – | – | ✓ |
| Elaboration | ✓ | – | – | – | – | ✓ |
| Vorwissensaktivierung | ✓ | – | – | ✓ | – | – |
| Metakognition | – | ✓ | – | – | ✓ | ✓ |

---

## 7) Offene Fragen / Zu klärende Punkte

### Aktionsfeed
- **`review`:** Entfällt (SR in `training` integriert) oder bleibt als lernbereichsübergreifender Typ?
- **`skript`:** Muss die Skriptstruktur für adressierbare 15-min-Abschnitte angepasst werden, oder entfällt dieser Feed-Typ?
- **Anzeigereihenfolge:** Wie wird priorisiert, wenn mehrere Typen gleichzeitig fällig sind? (eigene Diskussion nötig)
- **Technische Trigger:** Wie werden Auslöser in Firestore abgebildet?

### Checkliste / Selbsteinschätzung
- Die Trainings-Progression im Aktionsfeed (wann welche Aufgabe erscheint) wird **nicht** durch die Selbsteinschätzung beeinflusst.
- Im Dashboard gibt es eine Übersicht des Trainings- und Kompetenzfortschritts; dort können Konflikte zwischen Selbsteinschätzung und tatsächlichem Trainingsstand sichtbar gemacht werden.


### Blurting / Feynman
- Schlüsselbegriffe und Technik-Prompts müssen pro Lernbereich definiert und annotiert werden — in `kompetenzliste.json` oder separater Datei?

### Klausur
- Wie wird „erweiterter Kontext" über reine Trainingsaufgaben hinaus technisch implementiert?

### Modulstruktur
- Gibt es weitere optionale Modultypen neben Start und Zusatzmaterial?
