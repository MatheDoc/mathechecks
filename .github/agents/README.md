# Agenten-Struktur für MatheChecks

Rollendefinitionen für wiederkehrende Arbeitsmodi.
Agenten definieren **wer mit welchem Fokus** arbeitet.
Technische Specs und Konventionen liegen in den Referenzdokumenten, auf die Agenten per Pflichtlektüre verweisen.

## Agenten

1. `agent-content-didaktik.md`
   - Mathematische Inhalte, Erklärtexte, Aufgabenstellungen, Feedbacksprache
2. `agent-python-aufgaben.md`
   - Aufgabengeneratoren, Exportlogik, Python-Refactoring in `aufgaben/`
3. `agent-frontend-ux.md`
   - Lernoberfläche, Includes, Layouts, Barrierearmut und Bedienbarkeit
4. `agent-infra-architektur.md`
   - Systemgrenzen, Backend-Services, Deploy-/Risikoaspekte
5. `agent-plattform-architektur.md`
   - Datenbank, Benutzerverwaltung, Session-State, Aktionsfeed, Rollen und Migration
6. `agent-warmup.md`
   - Warm-Up pro Check: geführter Einstieg mit vorgerechnetem Beispiel und Fading, Übergabe ans Training (derzeit nicht verlinkt)
7. `agent-klausuren.md`
   - Klausuren: automatisierte Erstellung aus Lernbereichen/Checks gemäß `klausuren/config.yml`

## 3-Schichten-Modell

| Schicht | Dateien | Antwort auf |
|---|---|---|
| **Projektkontext** (immer geladen) | `copilot-instructions.md` | Was ist das Projekt? |
| **Agenten** (bei Auswahl geladen) | `agent-*.md` | Wer arbeitet mit welchem Fokus? |
| **Referenzdokumente** (per Pflichtlektüre) | `glossary.md`, `datenmodell.md`, `aufgaben/README.md` u. a. | Welche Konventionen und Specs gelten? |

## Konvention

- Dateinamen: `agent-<rolle>.md`
- Format: Markdown mit YAML-Frontmatter (`name`, `description`)
- Inhalt: Rolle, Zuständigkeiten, Pflichtlektüre, Prioritäten, Arbeitsmodus, Übergabeformat
- Keine technischen Specs im Agent duplizieren – stattdessen auf Referenzdokumente verweisen
