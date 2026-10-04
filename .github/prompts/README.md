# Prompt-Dateien für MatheChecks

Konkrete, wiederverwendbare Arbeitsaufträge.

## Dateitypen

| Typ | Namensschema | Zweck |
|---|---|---|
| **Task-Prompt** | `prompt-<zweck>.md` | Konkreter Arbeitsauftrag für einen klaren Use Case |
| **Systemprompt** | `systemprompt-<kontext>.md` | Domänenspezifische, verbindliche Ausgaberegeln |

## Aktuelle Prompts

- `prompt-aufgaben.md` – 20 JSON-Aufgaben erzeugen (verweist auf `aufgaben/README.md`)
- `prompt-skript-ueberarbeiten.md` – Skripte fachlich, didaktisch und LLM-freundlich überarbeiten
- `systemprompt-klausur.prompt.md` – verbindliche Ausgaberegeln für Klausuren (Zielformat `klausuren/templates/template.md`)
- `systemprompt-template.prompt.md` – Vorlage für neue Systemprompts
- `prompt-pruefung-pdf-zu-md.prompt.md` – Abitur-Musterprüfungen (PDF) aus `muster-pruefungen/` in Markdown mit validiertem Frontmatter konvertieren und Teilaufgaben nach Themen (`_data/themen.yml`) taggen (Ordner ist gitignored)
- `prompt-klausur-erstellen.md` – Klausur aus Themen, Lernbereichen/Checks und Musterprüfungen gemäß `klausuren/<slug>/config.yml` erzeugen (verweist auf `systemprompt-klausur.prompt.md`)

## Verwandte Referenzdokumente

- `../rechner-architektur.md` – Rechnerrollen, UX-Leitplanken und Verhaltensregeln

## Empfehlungen

- Prompts kurz, präzise, testbar formulieren.
- YAML-Frontmatter mit `description` verwenden.
- Fachlogik und Formatregeln nicht vermischen.
- Technische Specs nicht im Prompt duplizieren – auf Referenzdokumente verweisen.