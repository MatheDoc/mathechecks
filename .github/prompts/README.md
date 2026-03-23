# Prompt-Dateien für MatheChecks

Konkrete, wiederverwendbare Arbeitsaufträge.

## Dateitypen

| Typ | Namensschema | Zweck |
|---|---|---|
| **Task-Prompt** | `prompt-<zweck>.md` | Konkreter Arbeitsauftrag für einen klaren Use Case |
| **Systemprompt** | `systemprompt-<kontext>.md` | Domänenspezifische, verbindliche Ausgaberegeln |

## Aktuelle Prompts

- `prompt-aufgaben.md` – 20 JSON-Aufgaben erzeugen (verweist auf `aufgaben/README.md`)
- `prompt-rechnersemantik.md` – Rechnerverhalten und Eingabelogik
- `systemprompt-template.prompt.md` – Vorlage für neue Systemprompts

## Empfehlungen

- Prompts kurz, präzise, testbar formulieren.
- YAML-Frontmatter mit `description` verwenden.
- Fachlogik und Formatregeln nicht vermischen.
- Technische Specs nicht im Prompt duplizieren – auf Referenzdokumente verweisen.