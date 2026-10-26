# Skills für MatheChecks

Konkrete, wiederverwendbare Arbeitsaufträge und verbindliche Regelwerke. Jeder Skill liegt in `.github/skills/<name>/SKILL.md`; der Ordnername entspricht dem `name` im Frontmatter. Alle Skills sind nur manuell aufrufbar (`disable-model-invocation: true`).

## Namensschema

| Typ | Namensschema | Zweck |
|---|---|---|
| **Task-Skill** | `<zweck>` oder `prompt-<zweck>` | Konkreter Arbeitsauftrag für einen klaren Use Case |
| **Systemprompt-Skill** | `systemprompt-<kontext>` | Domänenspezifische, verbindliche Ausgaberegeln |

## Aktuelle Skills

- `lernbereich-erstellen` – Lernbereich neu anlegen, vollständig überarbeiten oder gezielt ändern, mit Abgleich gegen die Abitur-Musterprüfungen (Einstieg: `agent-lernbereich`)
- `prompt-klausur-erstellen` – Klausur aus Themen, Lernbereichen/Checks und Musterprüfungen gemäß `klausuren/<slug>/config.yml` erzeugen (verweist auf `systemprompt-klausur`)
- `systemprompt-klausur` – verbindliche Ausgaberegeln für Klausuren (Zielformat `klausuren/templates/template.md`)
- `systemprompt-template` – Vorlage für neue Systemprompts
- `pruefung-pdf-zu-md-konvertieren` – Abitur-Musterprüfungen (PDF) aus `muster-pruefungen/` in Markdown mit validiertem Frontmatter konvertieren und Teilaufgaben nach Themen (`_data/themen.yml`) taggen (Ordner ist gitignored)

## Verwandte Referenzdokumente

- `../inhalte.md` – Inhaltsstandards für Lernbereiche
- `../rechner-architektur.md` – Rechnerrollen, UX-Leitplanken und Verhaltensregeln

## Empfehlungen

- Skills kurz und zielorientiert formulieren: Ziel, Schritte, Prüfkriterien, Ausgabe.
- YAML-Frontmatter mit `name` und `description` verwenden.
- Fachlogik und Formatregeln nicht vermischen.
- Technische Specs nicht im Skill duplizieren – auf Referenzdokumente verweisen.
