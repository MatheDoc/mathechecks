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

Beim Übertrag nach `klausur.md` wird `bearbeitungszeit` auf das Textformat des Templates gebracht, z. B. `135` → `135 Minuten` (siehe `templates/template.md`). Ein optionales `logo`-Feld kann zusätzlich in der `klausur.md`-Frontmatter gesetzt werden (nicht Teil von `config.yml`), siehe Abschnitt „PDF-Export".

## Workflow

1. Neuen `<slug>`-Ordner anlegen und darin eine `config.yml` mit Lernbereichen/Checks füllen.
2. Klausur erzeugen lassen mit `.github/prompts/prompt-klausur-erstellen.md` (Pfad zur `config.yml` angeben).
3. Ergebnis `klausur.md` prüfen und bei Bedarf fachlich nachschärfen.
4. PDF erzeugen mit `klausuren/export-pdf.ps1 klausuren/<slug>/klausur.md` (siehe Abschnitt „PDF-Export").

`klausur.md` enthält dabei ausschließlich `\punkte{n}` je Teilaufgabe — keine Summen in Überschriften oder im Klausurkopf. Diese werden beim Export automatisch berechnet und eingefügt (siehe unten).

## PDF-Export

`export-pdf.ps1` erzeugt aus einer `klausur.md` per Pandoc/XeLaTeX ein PDF mit einheitlichem Klausurkopf:

- Aufruf: `.\klausuren\export-pdf.ps1 klausuren\<slug>\klausur.md` (ohne Parameter öffnet sich ein Dateiauswahldialog).
- **`templates/punkte-summe.lua`** liest alle `\punkte{n}` im Dokument, hängt die Summe je Aufgabe (`## Aufgabe N`) als „(N Punkte)" an die Überschrift an und berechnet die Gesamtpunktzahl, die in den Klausurkopf (`$gesamtpunkte$` in `klausurkopf-before.tpl.tex`) eingesetzt wird. Abschnitte ohne `\punkte{n}` (z. B. `# Lösungen`) bleiben unverändert. Diese Berechnung passiert **ausschließlich beim Export**, nie manuell in `klausur.md`.
- **`templates/table-style.lua`** rendert Markdown-Tabellen in der Klausur einheitlich (gleiche Spaltenbreite, zentriert, Rahmenlinien). Verschmolzene Zellen (Row-/Colspan) werden nicht unterstützt — bei Tabellen in Klausuraufgaben darauf verzichten.
- **`templates/klausurkopf-before.tpl.tex`** rendert den Kopfbereich (Logo, Fach/Klasse/Datum/Thema, Punkte-/Noten-Zeile) aus der Frontmatter von `klausur.md`.
- **`templates/klausurkopf-header.tex`** definiert u. a. den LaTeX-Befehl `\punkte{n}`, der als rechtsbündige Box „`/ n P`" neben der Teilaufgabe erscheint, sowie Kopf-/Fußzeile und Tabellen-Pakete.
- **`templates/logo.png`** ist das Standardlogo. Es wird nur eingebunden, wenn `klausur.md` ein `logo`-Feld in der Frontmatter setzt und die Datei existiert (Pfad relativ zum Repo-Root, z. B. `logo: klausuren/templates/logo.png`); ohne `logo`-Feld erscheint kein Logo.
- Voraussetzung: Pandoc und eine LaTeX-Distribution (MiKTeX) sind lokal installiert; das Skript sucht sie automatisch über bekannte Installationspfade.

## Quellen je Check

Pro ausgewähltem Check (`Nummer` in `config.yml`) werden automatisch herangezogen:

- `checks.json` → `Ich kann`, `Tipps`, `Sammlung`
- `lernbereiche/<gebiet>/<lernbereich>/beispiele/<NN>-<Sammlung>.md` → durchgerechnetes Beispiel (Rechenweg-Stil)
- `aufgaben/exports/json/<gebiet>/<lernbereich>/<Sammlung>.json` → Stichprobe realistischer Zahlenwerte/Szenarien (Stilvorbild, keine Kopiervorlage)

Siehe auch `.github/datenmodell.md` für die vollständige Feldsemantik von `checks.json`.

## Diagramme (grafische Teilaufgaben)

Checks vom Typ „Kennzahlen graphisch" (z. B. `kennzahlen-graphisch-*`) verlangen ein Diagramm zum Ablesen. Die `beispiele/*.md`-Dateien binden solche Diagramme per Jekyll-Liquid-Tag `{% include graph.html ... %}` ein — das funktioniert **nur beim Jekyll-Build der Website**, nicht im späteren PDF-Export der Klausur (Pandoc + Lua-Filter), der ohne Jekyll läuft.

Für Klausuren gilt deshalb eine andere Konvention:

- Diagramme als **statische Bilddatei** (z. B. PNG) erzeugen, am einfachsten mit einem kurzen Python-Skript (`matplotlib`), das die relevanten Funktionen plottet.
- Einbindung über normales Markdown-Bild gemäß `templates/template.md`: `![Alt-Text: ...](dateiname.png){width=NN%}`.
- Das Diagramm zeigt **nur Kurven, Achsenbeschriftung und ein Gitter** in sinnvoller Schrittweite zum Ablesen — **keine eingezeichneten oder beschrifteten Lösungspunkte** (das wäre die gesuchte Antwort).
- Das Erzeugungsskript (z. B. `generate_diagramme.py`) im selben `<slug>`-Ordner wie `config.yml`/`klausur.md` ablegen, damit Diagramme bei Bedarf reproduzierbar und anpassbar bleiben.

Beispielumsetzung: `klausuren/matgk_wg2x_2627_1/generate_diagramme.py` mit den zugehörigen `diagramm-aufgabe*.png`-Dateien.

## Verwandte Dateien

- `.github/agents/agent-klausuren.md` – Rolle und Prioritäten
- `.github/prompts/systemprompt-klausur.prompt.md` – verbindliche Ausgaberegeln
- `.github/prompts/prompt-klausur-erstellen.md` – konkreter Arbeitsauftrag
