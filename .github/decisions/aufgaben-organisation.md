# Aufgaben-Organisation – Vereinbarte Änderungen

## kompetenzliste.json

- `"Typ"` entfernen (alle Aufgaben werden künftig interaktiv)
- `"Ankityp"` → `"Kartentyp"` umbenennen
- `"QuestionOrder"` als neues Feld ergänzen (`"shuffle"` oder `"fixed"`)
- `kompetenzliste.json` wird die **zentrale Steuerdatei** für alle Verbraucher:
  - Website-JS (Flashcards, Training)
  - Moodle-XML-Export
  - Anki-Export

Zielschema pro Eintrag:
```json
{
  "Gebiet": "...",
  "Lernbereich": "...",
  "LernbereichAnzeigename": "...",
  "Nummer": 1,
  "Ich kann": "...",
  "Sammlung": "...",
  "Kartentyp": "einzeln | gruppiert",
  "QuestionOrder": "fixed | shuffle"
}
```

Hinweis: Jede Sammlung tritt nur einmal auf (eindeutig pro Lernbereich) → keine Redundanz bei `QuestionOrder`.

---

## aufgaben/project_config.json

- `"questionOrder"` überall entfernen (aus `defaults`, allen `targets`)
- Felder pro Job: nur noch `generator`, `seed`, `targets`
- Felder pro Target: nur noch `gebiet`, `lernbereich`, `sammlung` (ggf. `count`, `seed`, `output`)

Zielschema:
```json
{
  "defaults": {
    "count": 20,
    "outputDir": "aufgaben/exports/json"
  },
  "jobs": [
    {
      "generator": "...",
      "seed": 123,
      "targets": [
        {
          "gebiet": "...",
          "lernbereich": "...",
          "sammlung": "..."
        }
      ]
    }
  ]
}
```

---

## Ablage der Aufgaben-JSONs

- Generierte JSONs liegen unter `aufgaben/exports/json/<gebiet>/<lernbereich>/<sammlung>.json`
- Statische (hart kodierte) JSONs folgen demselben Schema und derselben Ordnerstruktur
- Der alte Sammelordner `/json/` wird langfristig abgelöst

---

## Rollenverteilung der Dateien

| Datei | Zuständigkeit |
|---|---|
| `kompetenzliste.json` | Didaktische Zuordnung + Präsentationsregeln (Kartentyp, QuestionOrder) |
| `aufgaben/project_config.json` | Technische Erzeugung (Generator, Seed, Targets) |
| `aufgaben/exports/json/` | Kanonische Aufgaben-JSONs, immer deterministisch (fixed) erzeugt |
