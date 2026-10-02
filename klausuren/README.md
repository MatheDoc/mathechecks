# Klausuren

Automatisierte Erstellung von Klausuren aus bestehendem Lernbereichs- und Check-Material.

## Ordnerstruktur

```
klausuren/
├── export-pdf.ps1           # PDF-Export per Pandoc (siehe Abschnitt "PDF-Export")
├── templates/                # gemeinsame Vorlage + PDF-Export-Zutaten für alle Klausuren
│   ├── template.md           # Zielformat für jede Klausur (Frontmatter, Beispielaufgaben)
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
| `checks` | Liste aus `lernbereich` (Slug wie in `checks.json`/`_data/lernbereiche.yml`) + `checks` (Array der `Nummer`-Werte aus `checks.json`, die geprüft werden sollen) |

`logo` ist kein `config.yml`-Feld, sondern wird optional direkt in der `klausur.md`-Frontmatter gesetzt.

## Workflow

1. `<slug>`-Ordner mit `config.yml` anlegen.
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
