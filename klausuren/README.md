# Klausuren

Automatisierte Erstellung von Klausuren aus Themen, Lernbereichs- und Check-Material, mit Abitur-Musterprüfungen als Kontext und Qualitätsmaßstab.

## Ordnerstruktur

```
klausuren/
├── export-pdf.ps1           # PDF-Export per Pandoc (siehe Abschnitt "PDF-Export")
├── templates/                # gemeinsame Vorlage + PDF-Export-Zutaten für alle Klausuren
│   ├── template.md           # Zielformat für jede Klausur (Frontmatter, Beispielaufgaben)
│   ├── config.yml            # Muster-Config (alle Felder kommentiert) zum Kopieren
│   ├── klausurkopf-before.tpl.tex
│   ├── klausurkopf-header.tex
│   ├── punkte-summe.lua
│   ├── table-style.lua
│   ├── logo.png
│   └── img1.png               # Platzhalterbild, nur als Beispiel im Template
└── <slug>/                   # ein Ordner pro Klausur
    ├── config.yml            # Auswahl + Metadaten dieser Klausur
    └── klausur.md             # generierte Klausur (Aufgaben + Lösungen)
```

`<slug>`-Empfehlung: `<datum:YYYY-MM-DD>-<klasse>`, z. B. `2026-06-10-wg2x`.

## `config.yml` — Schema

| Feld | Bedeutung |
|---|---|
| `fach` | Überschrift/Fach, z. B. „1. Klausur Mathematik" |
| `klasse` | Klasse/Kurs |
| `datum` | Klausurdatum |
| `thema` | Kurzbeschreibung des Themas (erscheint im Klausurkopf) |
| `bearbeitungszeit` | Bearbeitungszeit in Minuten (numerisch, z. B. `135`) |
| `geplante_punkte` | grobe Zielgröße für den Umfang (keine exakt einzuhaltende Summe) |
| `themen` | optional: Liste von Thema-Slugs aus `_data/themen.yml` – Hauptsteuerung; auch Themen ohne MatheChecks-Lernbereich möglich. Passende Musterprüfungs-Teilaufgaben werden über `muster-pruefungen/abitur/pruefungen-md/_themen.json` gefunden. |
| `checks` | optional: Liste aus `lernbereich` (Slug `<gebiet>/<lernbereich>` wie in `_data/checks.json`/`_data/lernbereiche.yml`) + `checks` (Array der `Nummer`-Werte) – Feinsteuerung, was im Unterricht behandelt wurde; die Lernbereiche zählen automatisch zu den Themen |
| `hinweise` | optional: Freitext der Lehrkraft, z. B. Teilinhalte, Schwerpunkte, Ausschlüsse, Hilfsmittel oder eine bestimmte Musterprüfungs-Aufgabe als Vorbild (Aufgabe-`id` + ggf. Teilaufgaben-Label, z. B. „Aufbau wie `nw-bgym-wuv-2025-haupt-erhoeht-a3` 3.2“) – hat Vorrang vor den übrigen Angaben |

`themen`, `checks` und `hinweise` sind einzeln optional (mindestens eines angeben) und dienen als **Orientierung, nicht als Checkliste**: Nicht alles muss vorkommen, Fragestellungen dürfen in vernünftigem Rahmen abweichen. Daraus wird eine stimmige Klausur erstellt.

`logo` ist kein `config.yml`-Feld, sondern wird optional direkt in der `klausur.md`-Frontmatter gesetzt.

Vollständiges, kommentiertes Beispiel: [`templates/config.yml`](templates/config.yml).

## Musterprüfungen

`muster-pruefungen/` (gitignored, nur lokal) enthält Abitur-Musterprüfungen als PDF und teilweise als Markdown-Export (`abitur/pruefungen-md/`, Übersicht in `_inventar.json`, Konvertierung: `.github/prompts/prompt-pruefung-pdf-zu-md.prompt.md`). Die Teilaufgaben der Exporte sind nach Themen aus `_data/themen.yml` (versioniert) verschlagwortet; der daraus generierte Index `pruefungen-md/_themen.json` liefert je Thema alle passenden Teilaufgaben. Musterprüfungen dienen bei jeder Klausur als Qualitätsmaßstab für Stil, Operatoren, Granularität und Punkteverteilung; über `themen` steuern sie zusätzlich den Inhalt. Fehlt der Ordner, wird ohne Musterprüfungen gearbeitet.

## Workflow

1. `<slug>`-Ordner anlegen und `templates/config.yml` als `config.yml` hineinkopieren und anpassen.
2. Klausur erzeugen lassen mit `.github/prompts/prompt-klausur-erstellen.md` (Regeln: `.github/prompts/systemprompt-klausur.prompt.md`, Rolle: `.github/agents/agent-klausuren.md`).
3. `klausur.md` prüfen und fachlich nachschärfen.
4. PDF erzeugen: `.\klausuren\export-pdf.ps1 klausuren\<slug>\klausur.md` (ohne Parameter: Dateiauswahldialog).

## PDF-Export

Pandoc/XeLaTeX (MiKTeX); das Skript findet beide über bekannte Installationspfade.

- `templates/punkte-summe.lua` summiert alle `\punkte{n}` je `## Aufgabe N` (→ „(N Punkte)" in der Überschrift) und insgesamt (→ Klausurkopf). In `klausur.md` daher nie Summen eintragen.
- `templates/table-style.lua` vereinheitlicht Tabellen; verbundene Zellen werden nicht unterstützt.
- `templates/klausurkopf-before.tpl.tex` / `klausurkopf-header.tex` → Kopfbereich aus der Frontmatter, `\punkte{n}`-Box, Kopf-/Fußzeile.
- Logo nur, wenn die Frontmatter `logo:` setzt (Pfad relativ zum Repo-Root, z. B. `klausuren/templates/logo.png`).

## Diagramme (grafische Teilaufgaben)

`{% include graph.html %}` aus den `beispiele/*.md` funktioniert nur im Jekyll-Build, nicht im PDF-Export. Für Klausuren daher:

- Diagramm als PNG per kurzem `matplotlib`-Skript (`generate_diagramme.py` im `<slug>`-Ordner) erzeugen und als Markdown-Bild einbinden.
- Nur Kurven, Achsenbeschriftung und Ablese-Gitter – **keine markierten Lösungspunkte**.
- Beide Nullachsen ($x=0$, $y=0$) sichtbar und hervorgehoben.

Beispiel: `klausuren/matgk_wg2x_2627_1/generate_diagramme.py`.
