# Agenten-Struktur für MatheChecks

Rollendefinitionen für wiederkehrende Arbeitsmodi.
Agenten definieren **wer mit welchem Fokus** arbeitet.
Technische Specs und Konventionen liegen in den Referenzdokumenten, auf die Agenten per Pflichtlektüre verweisen.

## Agenten

1. `agent-content-didaktik.md`
   - Checks, Skripte, Beispiele, Tipps, Tests, Abiturbezug
2. `agent-python-aufgaben.md`
   - Aufgabengeneratoren, Exportlogik, Python-Refactoring in `aufgaben/`
3. `agent-frontend-ux.md`
   - Lernoberfläche, Includes, Layouts, Barrierearmut und Bedienbarkeit
4. `agent-plattform-architektur.md`
   - Datenbank, Benutzerverwaltung, Session-State, Aktionsfeed, Rollen und Migration
5. `agent-warmup.md`
   - Warm-Up pro Check: geführter Einstieg (Erklärung wie im Erklärvideo, vorgerechnetes Beispiel, Fading), Übergabe ans Training (derzeit nicht verlinkt)
6. `agent-klausuren.md`
   - Klausuren: automatisierte Erstellung aus Themen, Lernbereichen/Checks und Musterprüfungen gemäß `klausuren/<slug>/config.yml`

## 4-Schichten-Modell

| Schicht | Dateien | Antwort auf |
|---|---|---|
| **Projektkontext** (immer geladen) | `copilot-instructions.md` | Was ist das Projekt? |
| **Agenten** (bei Auswahl geladen) | `agent-*.md` | Wer arbeitet mit welchem Fokus? |
| **Skills** (bei Aufruf geladen, `../skills/<name>/SKILL.md`) | siehe `../skills/README.md` | Welcher konkrete Arbeitsauftrag bzw. welches Regelwerk gilt? |
| **Referenzdokumente** (per Pflichtlektüre) | `glossary.md`, `datenmodell.md`, `inhalte.md`, `aufgaben/README.md` u. a. | Welche Konventionen und Specs gelten? |

## Konvention

- Dateinamen: `agent-<rolle>.md`
- Format: Markdown mit YAML-Frontmatter (`name`, `description`)
- Inhalt: Rolle, Pflichtlektüre, Prioritäten, Arbeitsmodus, Übergabe – knapp, ohne Wiederholung der Referenzdokumente
- Keine technischen Specs im Agent duplizieren – stattdessen auf Referenzdokumente verweisen
