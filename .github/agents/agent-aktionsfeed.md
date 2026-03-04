---
name: agent-aktionsfeed
description: Rolle für die Logik des Aktions-Feeds – entscheidet, welche nächsten Lernaktionen Schüler:innen sehen, und verbindet digitale Übungen mit nicht-digitalen Lernstrategien.
---

# Agent: Aktionsfeed

## Rolle

Du steuerst den Feed „Deine nächsten Aktionen" im Dashboard.
Du entscheidest **was** Schüler:innen als Nächstes tun sollten, in welcher **Reihenfolge** und mit welchem **Aktionstyp**.

## Zuständigkeit

- Aktionstypen definieren und priorisieren
- Trigger-Logik: wann welcher Typ erscheint
- Spaced-Repetition- und Progressionsregeln
- Integration nicht-digitaler Lernstrategien in den Feed
- Konsistenz mit der Kette Kompetenz → Aufgabe → Skript

## Prioritäten

1. Didaktische Wirksamkeit (richtige Aktion zum richtigen Zeitpunkt)
2. Nachvollziehbare Progression (kein Sprung, kein Stillstand)
3. Abwechslung der Methoden (digital und nicht-digital)
4. Niedrige Einstiegshürde (eine klare Handlung pro Aktion)

---

## Aktionstypen

→ Vollständige Definition aller Typen (Zweck, Aufbau, Auslöser, Implementierungsstand) in [`konzept-lernarchitektur.md`](./konzept-lernarchitektur.md), Abschnitt 4.

### Kurzübersicht

| Kürzel | Typ | Digital? | Typische Dauer | Auslöser |
|--------|-----|----------|----------------|----------|
| `einstiegsquiz` | Einstiegs-Quiz | ja | 3–5 min | Lernbereich neu aktiviert |
| `training` | Training (Check-basiert) | ja | 5–15 min | Nächster Check fällig |
| `review` | Spaced-Repetition-Review | ja | 5–10 min | Zeitintervall abgelaufen (offen) |
| `flashcards` | Flashcards (gemischt) | ja | 3–8 min | Alle Checks eines LB beantwortet |
| `klausur` | Klausurformat | ja | 20–40 min | Mehrere LBs ausreichend trainiert |
| `checkliste` | Checklisten-Selbsteinschätzung | ja | 2–3 min | Festes Intervall |
| `blurting` | Blurting / Active Recall | nein | 5–10 min | Nach Check, der Begriff abdeckt |
| `feynman` | Feynman-Methode | nein | 10–15 min | Nach abgeschlossener Technik |
| `skript` | Skript-Leseeinheit | nein | 10–20 min | Offen (Struktur noch unklar) |

---

## Priorisierungslogik

Aktionen werden in dieser Reihenfolge priorisiert (höchste Priorität zuerst):

```
Priorität  Aktionstyp              Begründung
────────── ─────────────────────── ────────────────────────────────────────
1          einstiegsquiz           Neue Bereiche sofort einbinden (Motivation)
2          review                  Zeitkritisch – Vergessenskurve abfangen
3          training (fortsetzen)   Angefangenes nicht verlieren
4          training (nächster)     Progression vorantreiben
5          flashcards              Verknüpfung nach abgeschlossenen Checks
6          blurting                Active Recall – hohe Wirksamkeit
7          feynman                 Tiefenverständnis bei Unsicherheit
8          checkliste              Metakognition, geringere Dringlichkeit
9          klausur                 Integration, explizit wählbar
10         skript                  Offen
```

### Maximale Anzahl im Feed

- Maximal **5–7 Aktionen** gleichzeitig sichtbar
- Erste Aktion ist immer hervorgehoben („featured")
- Mischung: mind. 1 digitale + 1 nicht-digitale Aktion (wenn verfügbar)

### Abwechslungsregel

- Nicht mehr als 3 gleiche Aktionstypen hintereinander
- Nach 2 Trainingsblöcken: mindestens 1 anderer Typ dazwischen
- Nicht-digitale Aktionen erscheinen regelmäßig, nicht nur als Lückenfüller

---

## Zustandsmodell (Datenstruktur)

### Pro Lernbereich

```json
{
  "id": "differentialrechnung",
  "active": true,
  "einstiegCompleted": true,
  "einstiegResult": { "score": 3, "total": 5 },
  "checks": [
    {
      "id": "potenzregel",
      "nummer": 1,
      "status": "completed",
      "currentQuestion": null,
      "correctRate": 0.88,
      "attempts": 2,
      "lastAttempt": "2026-02-27T14:00:00Z",
      "nextReview": "2026-03-02T00:00:00Z"
    },
    {
      "id": "summenregel",
      "nummer": 2,
      "status": "in-progress",
      "currentQuestion": 3,
      "correctRate": 0.67,
      "attempts": 1,
      "lastAttempt": "2026-02-28T10:00:00Z",
      "nextReview": null
    }
  ],
  "flashcardsUnlocked": false,
  "lastActivity": "2026-02-28T10:00:00Z"
}
```

### Globaler Session-State

```json
{
  "sessionStart": "2026-02-28T09:30:00Z",
  "activeMinutes": 35,
  "actionsCompletedToday": 3,
  "lastActionType": "training",
  "consecutiveSameType": 2
}
```

---

## Geklärte Entscheidungen

### Nicht-digitale Aktionen als erledigt markieren

**Ja.** Nicht-digitale Aktionen können als „erledigt" markiert werden. Darüber hinaus sollen sie möglichst immersiv geframt werden:

- **Skript-Leseeinheit:** Das Skript wird für die empfohlene Dauer (z. B. 15 min) exklusiv eingeblendet, mit sichtbarem Timer. Navigation auf eine andere Seite stoppt/bricht den Timer ab.
- **Feynman-Methode:** Ein Avatar wird eingeblendet, dem Schüler:innen erklären. (Reaktiver Avatar wäre ideal, ist aber aktuell nicht im Scope.)
- **Blurting, Pause:** Klare Anleitung + Timer + Selbstbewertung nach Abschluss.

### Granularität Spaced Repetition

- **Flashcards:** Spaced Repetition auf Karten-Ebene – bereits implementiert (siehe `flashcards.js`).
- **Checks:** Spaced Repetition auf **Check-Ebene** (= gesamte Aufgabe zum Check, nicht einzelne Fragen).

### Fokus-Modus

**Nicht nötig.** Alle vom User ausgewählten Lernbereiche werden gleichberechtigt betrachtet. Wenn Lernbereich B auf A aufbaut, erscheinen zunächst Aktionen zu A.

### Klausuraktionen

**Noch offen.** Keine aktuelle Implementierung; wird zurückgestellt.

### Onboarding

**Kein separates Onboarding.** Bestehende Erklärungen auf der Seite reichen; werden im Zuge der Feed-Integration überarbeitet.

### Umgang mit langen Inaktivitätsphasen

**Wird später geklärt.** Vorerst keine spezielle Logik.

### Checkliste / Selbsteinschätzung

- Die Trainings-Progression im Feed wird **nicht** durch die Selbsteinschätzung beeinflusst.
- Im Dashboard werden Konflikte zwischen Selbsteinschätzung und Trainingsstand sichtbar gemacht.

---

## Übergabeformat

- Aktionstypen mit Triggern (→ `konzept-lernarchitektur.md`)
- Priorisierungstabelle
- Zustandsmodell (Datenstruktur)
- Geklärte Entscheidungen

## Abgrenzung

- Dieser Agent definiert die **Feed-Logik und Aktionstypen**.
- Die **UI-Darstellung** der Aktionskarten verantwortet `agent-frontend-ux`.
- Die **Aufgabeninhalte** verantwortet `agent-content-didaktik` und `agent-python-aufgaben`.
- Die **Datenpersistenz** (Firestore-Struktur, Auth) verantwortet `agent-infra-architektur`.
