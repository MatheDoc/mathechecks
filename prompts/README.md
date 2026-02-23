# Prompt-Strategie (Systemprompts)

Diese Konvention macht KI-unterstützte Entwicklung in MatheChecks konsistent und reproduzierbar.

## Ablageorte

- Global (projektweit): `prompts/systemprompt-global.txt`
- Global (pädagogisch-didaktisch): `prompts/systemprompt-global-paedagogik-didaktik.txt`
- Lokal (nah am Code): `<kontext>_systemprompt.txt` im jeweiligen Fach-/Modulordner
  - Beispiel: `aufgaben/generators/.../ganzrationale_oekonomische_funktionen_systemprompt.txt`

## Namensschema

- Global: `systemprompt-global.txt`
- Lokal: `<slug>_systemprompt.txt`
- Slug in `snake_case`, fachlich eindeutig, ohne Leerzeichen.

## Mindeststruktur je Prompt

1. Ziel
2. Muss-Kriterien (harte Regeln)
3. Soll-Kriterien (weiche Regeln)
4. Ausgabeformat (streng)
5. Negativliste (was explizit nicht erlaubt ist)
6. Prioritäten bei Konflikten

## Praxisregeln

- Zahlenbereiche, Toleranzen und Sonderfälle explizit benennen.
- Ausgabevorgaben immer testbar formulieren (z. B. „parsebares JSON-Array“).
- Keine vermischten Anforderungen (fachliche Logik getrennt von Darstellung/Format).
- Bei Generatoren zuerst fachliche Korrektheit, dann Lesbarkeit, dann Variation priorisieren.

## Startpunkt

- Für neue Kontexte die Vorlage `prompts/systemprompt-template.txt` kopieren und anpassen.
- Für didaktische Qualitätskriterien bei Erklärungen, Aufgaben und Feedback den globalen Prompt `prompts/systemprompt-global-paedagogik-didaktik.txt` zusätzlich nutzen.