# MatheChecks – Claude Code

Die maßgeblichen Projektanweisungen liegen in `.github/` und werden parallel von GitHub Copilot genutzt.
Diese Datei bindet sie nur ein und ergänzt Claude-spezifische Hinweise. Inhaltliche Regeln **nicht hier**, sondern in `.github/` pflegen.

@.github/copilot-instructions.md

## Hinweise für Claude Code

### Skills
Die Skills liegen in `.github/skills/<name>/SKILL.md`. Unter `.claude/skills/<name>/SKILL.md` liegen nur Verweise darauf, damit sie als `/<name>` aufrufbar sind.
Neue oder geänderte Skills: Inhalt in `.github/skills/` pflegen, in `.claude/skills/` nur den Verweis anlegen bzw. `name`/`description` abgleichen.

### Rollen (Copilot-Agenten)
`.github/agents/agent-<rolle>.md` sind Rollenbeschreibungen mit Pflichtlektüre. Wenn eine Aufgabe in den Zuständigkeitsbereich einer Rolle fällt, die Rollendatei und ihre Pflichtlektüre lesen, bevor gearbeitet wird:

| Aufgabe | Rolle |
|---|---|
| Checks, Skripte, Beispiele, Tipps, Tests, Abiturbezug, Fachsprache | `agent-content-didaktik.md` |
| Lernbereich anlegen/überarbeiten (steuert den Ablauf) | `agent-lernbereich.md` |
| Python-Aufgabengeneratoren, JSON-Export in `aufgaben/` | `agent-python-aufgaben.md` |
| Frontend, Layouts, Includes, CSS, UX | `agent-frontend-ux.md` |
| Datenbank, Benutzerverwaltung, Session-State, Feed, Migration | `agent-plattform-architektur.md` |
| Warm-Ups pro Check | `agent-warmup.md` |
| Klausuren | `agent-klausuren.md` |
| Erklärvideos (Manim) | `agent-video.md` |

Wenn eine Rolle „an Fachagenten delegiert“, heißt das hier: die Rollendatei des Fachagenten lesen und ihre Regeln anwenden.

### Sonstiges
- `muster-pruefungen/` und `klausuren/` sind gitignored (eigene private Repos), aber lokal vorhanden und lesbar.
- `_site/` ist Build-Ausgabe von Jekyll – nicht bearbeiten.
