# Klausuren

Automatisierte Erstellung von Klausuren mit Abitur-Musterprüfungen als primärer Vorlage, ergänzt um Lernbereichs- und Check-Material.

## Ordnerstruktur

```
klausuren/
├── export-pdf.ps1           # PDF-Export per Pandoc (siehe Abschnitt "PDF-Export")
├── diagramme/                # gemeinsames Python-Paket für alle Klausurdiagramme (siehe Abschnitt "Diagramme")
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
    ├── klausur.md             # generierte Klausur (Aufgaben + Lösungen)
    └── generate_diagramme.py # optional: ruft nur `diagramme/` auf → diagramm-*.png
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
| `themen` | optional: Thema-Slugs aus `_data/themen.yml`, auch ohne MatheChecks-Lernbereich; wählt die Musterprüfungs-Teilaufgaben aus |
| `checks` | optional: Liste aus `lernbereich` (Slug `<gebiet>/<lernbereich>`) + `checks` (`Nummer`-Werte) – grenzt ein, was im Unterricht behandelt wurde; die Lernbereiche zählen automatisch zu den Themen |
| `hinweise` | optional: Freitext der Lehrkraft, z. B. Schwerpunkte, Ausschlüsse, Hilfsmittel oder eine Musteraufgabe als Vorbild (Aufgabe-`id` + ggf. Label, z. B. „Aufbau wie `nw-bgym-wuv-2025-haupt-erhoeht-a3` 3.2“) – höchste Priorität |

Mindestens eines von `themen`, `checks`, `hinweise` angeben; alle drei sind Orientierung, keine Checkliste. Gewichtung der Quellen: `.github/prompts/systemprompt-klausur.prompt.md`, Abschnitt 1.

`logo` ist kein `config.yml`-Feld, sondern wird optional direkt in der `klausur.md`-Frontmatter gesetzt.

Vollständiges, kommentiertes Beispiel: [`templates/config.yml`](templates/config.yml).

## Musterprüfungen

`muster-pruefungen/` (gitignored, nur lokal) enthält Abitur-Musterprüfungen als PDF und teilweise als Markdown-Export (`abitur/pruefungen-md/`, Übersicht in `_inventar.json`, Konvertierung: `.github/prompts/prompt-pruefung-pdf-zu-md.prompt.md`). Die Teilaufgaben sind nach Themen aus `_data/themen.yml` verschlagwortet; der Index `pruefungen-md/_themen.json` liefert je Thema alle passenden Teilaufgaben.

## Workflow

1. `<slug>`-Ordner anlegen und `templates/config.yml` als `config.yml` hineinkopieren und anpassen.
2. Klausur erzeugen lassen mit `.github/prompts/prompt-klausur-erstellen.md` (Regeln: `.github/prompts/systemprompt-klausur.prompt.md`, Rolle: `.github/agents/agent-klausuren.md`).
3. `klausur.md` prüfen und fachlich nachschärfen.
4. PDF erzeugen: `.\klausuren\export-pdf.ps1 klausuren\<slug>\klausur.md` (ohne Parameter: Dateiauswahldialog).

## PDF-Export

Pandoc/XeLaTeX (MiKTeX); das Skript findet beide über bekannte Installationspfade.

- `templates/punkte-summe.lua` summiert alle `\punkte{n}` je `## Aufgabe N` (→ „(N Punkte)" in der Überschrift) und insgesamt (→ Klausurkopf). In `klausur.md` daher nie Summen eintragen. Wahlaufgaben: Enthält die Überschrift „Wahlaufgabe“ (z. B. `## Aufgabe 5 – Wahlaufgabe`), zählen davon nur so viele (die punktreichsten) zur Gesamtpunktzahl, wie `wahlaufgaben: <Anzahl>` in der `klausur.md`-Frontmatter angibt (ohne Angabe zählen alle).
- `templates/table-style.lua` vereinheitlicht Tabellen; verbundene Zellen werden nicht unterstützt.
- `templates/klausurkopf-before.tpl.tex` / `klausurkopf-header.tex` → Kopfbereich aus der Frontmatter, `\punkte{n}`-Box, Kopf-/Fußzeile.
- Logo nur, wenn die Frontmatter `logo:` setzt (Pfad relativ zum Repo-Root, z. B. `klausuren/templates/logo.png`).

## Diagramme (grafische Teilaufgaben)

`{% include graph.html %}` aus den `beispiele/*.md` funktioniert nur im Jekyll-Build, nicht im PDF-Export. Klausurdiagramme entstehen daher als PNG über das gemeinsame Paket [`diagramme/`](diagramme/) (matplotlib). Es ist bewusst getrennt von den Plotly-Grafiken der Website (`assets/js/visuals/`): andere Laufzeit (Python statt Browser) und andere Anforderungen (Druck, kein Hover). Die Parameternamen orientieren sich aber an den Website-Includes (`funktionen`/`term`, `flaechen`, `punkte`, `hilfslinien`, `xmin`…); Terme dürfen als String in derselben Syntax angegeben werden (`"0.1*x^3 - 2*x"`, `exp`, `log` = ln).

### Druckstil (verbindlich, im Paket umgesetzt)

- **Keine Farben.** Linien immer schwarz; mehrere Graphen werden über Linienstile unterschieden (durchgezogen, gestrichelt, gepunktet, Strich-Punkt …) und **direkt am Graphen beschriftet** statt per Legende.
- Graustufen nur für Flächen und Histogrammbalken (hell, Hervorhebung dunkler) oder Schraffur.
- Dichtes Ablese-Gitter (Haupt- und Nebenlinien), beide Nullachsen hervorgehoben, Dezimalkomma an den Achsen.
- In Aufgaben-Diagrammen **keine markierten Lösungspunkte**; `zulaessig_markieren`, `zielgeraden`, `punkte` usw. nur für Lösungsskizzen oder wenn Teil der Aufgabenstellung.

### Verwendung

Pro Klausur ein kurzes `generate_diagramme.py` im `<slug>`-Ordner, das nur das Paket aufruft:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diagramme import *  # noqa: F403

OUT = Path(__file__).parent
funktionsgraph(OUT / "diagramm-aufgabe1.png", [Kurve("15*x", "$E$"), Kurve(K, "$K$")],
               xlim=(0, 20), ylim=(-100, 350), yhaupt=50, yneben=10,
               xachse="Menge $x$ in ME", yachse="Betrag in GE")
```

| Funktion | Zweck | wichtige Parameter |
|---|---|---|
| `funktionsgraph(pfad, kurven, xlim=, ylim=)` | Koordinatensystem mit Graphen; ohne `kurven` leeres Koordinatensystem | `Kurve(term, name, stil, von, bis, bei_x)`, `flaechen=[Flaeche(oben, unten, von, bis, schraffur)]`, `hilfslinien=[Hilfslinie(x=…/y=…)]`, `punkte=[Punkt(x, y, name)]`, `xhaupt/xneben/yhaupt/yneben`, `skizze=True` (ohne Gitter/Zahlen) |
| `histogramm_binomial(pfad, n, p)` | Histogramm $B(n;p)$ | `kumuliert=True`, `kmin/kmax`, `hervorheben=(a, b)`, `ymax`, `yhaupt/yneben` |
| `histogramm(pfad, ks, werte)` | beliebige Verteilung | wie oben |
| `baumdiagramm(pfad, aeste)` | Baumdiagramm beliebiger Tiefe | Äste `(Ereignis, p[, Unteräste])`, `LUECKE` = leeres Kästchen, `richtung="unten"/"rechts"`, `pfadwahrscheinlichkeiten=True`; Helfer `baum_zweistufig(p_a, p_b_a, p_b_na)`, `baum_bernoulli(n, p)`, `quer("A")` |
| `lineare_optimierung(pfad, restriktionen, xlim=, ylim=)` | grafisches Verfahren | `Restriktion(a, b, c, "<=", name)` für $ax+by\le c$, `zulaessig_markieren`, `zielgeraden=[Zielgerade(a, b, wert, name)]`, `punkte` |
| `uebergangsgraph(pfad, zustaende, kanten)` | Übergangsgraph (Markov) | `kanten={("A", "B"): 0.15, ("A", "A"): 0.8, …}` (von, nach), `positionen` |
| `verflechtungsdiagramm(pfad, stufen, kanten)` | Gozinto-Graph R → Z → E | `kanten_aus_matrix(zeilen, spalten, RZ)` (Zeile = von, Spalte = nach) |

Beschriftungen werden automatisch an eine freie Stelle gesetzt; liegen Graphen sehr dicht, mit `bei_x=` nachsteuern. Vierfeldertafeln als Markdown-Tabelle, nicht als Bild.

Beispiele aller Typen: `python klausuren/diagramme/galerie.py` (Ausgabe in `klausuren/diagramme/_galerie/`, nicht versioniert). Klausur-Beispiel: `klausuren/matgk_wg2x_2627_1_probe/generate_diagramme.py`.
