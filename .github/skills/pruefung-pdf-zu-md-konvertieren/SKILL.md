---
name: pruefung-pdf-zu-md-konvertieren
description: Konvertiert Abitur-Musterprüfungen (PDF) in strukturierte Markdown-Dateien mit validiertem YAML-Frontmatter (Inventar, Scaffold, Grafiken, Transkription, Validierung).
disable-model-invocation: true
argument-hint: "PDF-Datei(en) oder Ordner unter muster-pruefungen/abitur/pruefungen/"
---
# Skill: Musterprüfung PDF → Markdown

Du konvertierst eine oder mehrere Abitur-Prüfungen (PDF) in Markdown-Dateien mit YAML-Frontmatter.
Die Exporte dienen als **KI-Kontext für Klausurerstellung und Content-Entwicklung**. Priorität
haben deshalb exakte Aufgabentexte, Teilaufgaben-Labels, Punkte, Operatoren und
Erwartungshorizont. Layouttreue ist zweitrangig. Arbeite die Schritte der Reihe nach ab.

Pipeline: PDF sichten → Prüfungsinventar → Datei-/Aufgabenplan → Scaffold → Grafiken →
Transkription → Themen taggen → Validierung + Themen-Index → Coverage-Check → visuelle
Endkontrolle → Projekt-Inventar.

## Pfade

Alle Befehle werden vom Repo-Root aus ausgeführt. `MP` steht für `muster-pruefungen/abitur`.
Der Ordner `muster-pruefungen/` ist per gitignore ausgeschlossen (urheberrechtlich geschützte
Inhalte). Versioniert werden nur dieser Skill und `_data/themen.yml`.

| Inhalt | Pfad |
|---|---|
| Original-PDFs (Quelle der Wahrheit) | `MP/pruefungen/<land schulform …>/` |
| Schemas + Validator | `muster-pruefungen/abitur/pruefungen/schema/aufgabe.schema.json`, `muster-pruefungen/abitur/pruefungen/schema/pruefung-index.schema.json`, `MP/pruefungen/schema/validate_frontmatter.py` |
| MD-Exporte | `MP/pruefungen-md/{land}/{schulform-slug}/{niveau}/{pruefung-id}/` |
| Projekt-Inventar | `muster-pruefungen/abitur/pruefungen-md/_inventar.json` |
| Themen-Vokabular (versioniert) | `_data/themen.yml` |
| Themen-Index (generiert) | `MP/pruefungen-md/_themen.json` |
| Gemeinsame Tools | `MP/pruefungen-md/_tools/` (`scaffold.py`, `scaffold.example.yaml`, `figures.py`) |

Python-Abhängigkeiten (im Projekt-venv `.venv`): `.venv\Scripts\python.exe -m pip install pymupdf pyyaml jsonschema`.

**Schlank arbeiten:** Für die gesamte Konvertierung genügen diese vier Aufrufe:

```
.venv\Scripts\python.exe MP/pruefungen-md/_tools/figures.py render <pdf> [--seiten 3-5]   # Seiten lesen
.venv\Scripts\python.exe MP/pruefungen-md/_tools/scaffold.py <spec.yaml>                   # Grundgerüst
.venv\Scripts\python.exe MP/pruefungen-md/_tools/figures.py crop <pdf> <seite> <ziel.png> [--clip x0 y0 x1 y1]
.venv\Scripts\python.exe MP/pruefungen/schema/validate_frontmatter.py                     # alle Checks
```

Schreibe **keine eigenen Hilfsskripte**, weder für die Transkription noch für Datei-Updates oder
Prüfungen. Stubs, `_index.md` und `_inventar.json` bearbeitest du direkt mit dem Edit-Werkzeug.
Fehlt eine wiederkehrende Funktion, erweitere das gemeinsame Tool und dokumentiere sie hier.

## 0. Kontext laden

- Lies beide Schemas: Sie sind die verbindliche Quelle für erlaubte Felder und Enums.
- Lies `_inventar.json`, um zu sehen, welche Prüfungen bereits ganz oder teilweise konvertiert sind.
- Lies `sonderfaelle.md` (gleicher Ordner) mindestens für das Land und die Schulform der aktuellen Prüfung.
- Nutze die vorhandenen Tools, statt eigene zu schreiben.

## 1. PDFs sichten, nicht nur Dateinamen interpretieren

Öffne jede PDF tatsächlich, mindestens die Titelseite und die Kopfzeilen als gerendertes Bild
(siehe Schritt 4). Erst danach trägst du Land, Schulform, Fachrichtung, Jahr, Termin, Niveau und
Hilfsmittel ins Frontmatter ein. Kläre außerdem:

- Welche PDFs gehören zusammen und wie sind sie aufgeteilt? Mögliche Fälle: Aufgabe und Lösung
  getrennt, Teil A/B getrennt, alles in einer Datei, GK/LK als eigene Dateien. Nimm keinen
  dieser Fälle als Standard an.
- Gibt es einen Erwartungshorizont, und liegt er in derselben oder in einer separaten Datei?

## 2. Prüfungsinventar vor dem Scaffold

Erfasse das Inventar vor dem Scaffold als kurze Tabelle im Chat, nicht als eigene Datei:
PDF → Seiten → Prüfungsteile → Aufgaben → Teilaufgaben → Themenbereich → Pflicht/Wahl → Lösung
vorhanden?

- Regex-Muster in Kopfzeilen oder Seitenzahlen sind nur ein Indikator. Bei Konflikten gilt:
  gerenderte Seite (Bild) > `get_text()` > Dateiname.
- Prüfe zwei Fälle besonders:
  - Ein Aufgaben-Slot enthält interne Varianten.
  - Teilaufgaben einer Aufgabe gehören zu verschiedenen Themenbereichen (dann splitten, siehe Schritt 7).
- Lege die Anzahl der Aufgabe-Dateien erst nach diesem Inventar fest.

## 3. Anti-Halluzinations-Regel

Nichts ergänzen, glätten oder mathematisch „korrigieren“. Zahlen, Indizes, Exponenten,
Vorzeichen und Labels übernimmst du exakt wie im Original, auch wenn sie seltsam wirken.
Unleserliche Stellen markierst du mit `<!-- UNSICHER: ... -->` oder fragst nach.

## 4. Inhalt lesen: Formeln nur vom Bild

`page.get_text()` zerlegt Formeln oft in unbrauchbare Fragmente (z. B. `ൌ` statt `=`, `ଶ` statt
`²`). Ursache sind Font-Subsets und die absolute Positionierung der Glyphen.

- Für Formeln: Seiten mit `figures.py render <pdf>` als PNG rendern und das Bild lesen. Liegen
  die Seiten bereits als Bilder im Chat vor (PDF-Anhang), entfällt das Rendern.
- Für reinen Fließtext ohne Formeln reicht der extrahierte Text.
- Gleiche Zahlen, Indizes, Exponenten, Operatoren, Ungleichheitszeichen und Einheiten gezielt mit
  dem Bild ab.

## 5. Grundgerüst erzeugen

Schreibe eine YAML-Spec nach dem Muster von `MP/pruefungen-md/_tools/scaffold.example.yaml`
(temporär, z. B. im Temp-Ordner; sie wird nicht aufbewahrt) und führe aus:

```
.venv\Scripts\python.exe muster-pruefungen/abitur/pruefungen-md/_tools/scaffold.py <spec.yaml>
```

Das Skript erzeugt Ordnerstruktur, `_index.md` und je Aufgabe eine Stub-Datei mit validem
Frontmatter. Trage Teilaufgaben, Punkte und `themen` (Schritt 8) schon in der Spec ein. Dann
musst du im Frontmatter später nur noch `erwartungshorizont` und `enthaelt_grafik` anpassen.

> ⚠️ `scaffold.py` überschreibt vorhandene Dateien ohne Rückfrage. Führe es nur für neue
> Prüfungen aus, niemals über bereits transkribierte Ordner.

## 6. Grafiken extrahieren

Je Abbildung genügt ein Aufruf. Ein prüfungsspezifisches Skript ist nicht nötig, die PNGs in
`_assets/` sind das Ergebnis:

```
.venv\Scripts\python.exe muster-pruefungen/abitur/pruefungen-md/_tools/figures.py crop <pdf> <seite> <pruefung-ordner>/_assets/<name>.png
```

- `<pdf>` darf ein bloßer Dateiname sein, `<seite>` ist 1-basiert („Seite x von y“).
- Ohne `--clip` wird die Bounding-Box automatisch bestimmt. Teilt sich die Grafik die Seite mit
  Tabellen, Fließtext oder Fotos, setzt du `--clip x0 y0 x1 y1` (in pt, A4 = 595 × 842, Ursprung
  oben links). Der verwendete Ausschnitt wird ausgegeben und lässt sich so nachjustieren.
- Prüfe jeden Ausschnitt im Bild-Viewer. Grafiken werden nie nachgezeichnet.
- Bildnamen sind deterministisch, z. B. `a2-4-abb1.png`.
- Zierfotos ohne mathematischen Inhalt werden nicht übernommen.

## 7. Inhalt in die Stubs schreiben

Ersetze den Stub-Inhalt jeder Datei direkt mit dem Edit-Werkzeug, inklusive des Markers
`<!-- STUB … -->`. Ein Build-Skript für die Transkription schreibst du nicht.

- Aufgabenstellung und Erwartungshorizont kommen in die jeweiligen Abschnitte.
  - Formeln als LaTeX (`$…$`/`$$…$$`)
  - Tabellen als GFM
  - Bilder als Link auf `_assets/*.png`
- Teilaufgaben-Labels schreibst du als **Bold-Inline am Zeilenanfang** (`**2.1.1**`, `**f)**`,
  `**(1)**`), nicht als Markdown-Liste. Jedes Label entspricht einem `teilaufgaben[].bezeichnung`
  im Frontmatter. Ein `)` oder `.` am Ende lässt du in `bezeichnung` weg (`**f)**` → `"f"`).
  Übergeordnete Kontext-Labels wie `**2.1**` vor `2.1.1` sind erlaubt.
- Direkt nach der H1 folgt ein kursiver Satz `*…*` mit Strukturfakten, die nicht ins Frontmatter
  passen: Pflicht/Wahl, Auswahlregeln, Querverweis bei gesplitteten Aufgaben.
- Deckt eine Aufgabe mehrere `themenbereich`-Werte ab, teilst du sie an der Themengrenze in
  mehrere Dateien auf, mit gegenseitigem Querverweis. Gibt es keine klare Grenze, bleibt die
  Originalstruktur unverändert.
- `erwartungshorizont.status` bleibt `"keine"`, bis wirklich Lösungsinhalt in der Datei steht.
  Danach setzt du ihn auf `vollstaendig` oder `teilweise`.
- Nicht übernommen wird Boilerplate: Deckblätter, Bewertungsbögen, Notenschlüssel und
  Hinweisseiten. Die Punkteverteilung aus Bewertungsbögen übernimmst du aber.
- Im Abschnitt „Bekannte Lücken“ der `_index.md` dokumentierst du, was bewusst ausgelassen oder
  beschnitten wurde.

## 8. Themen taggen

Jede Teilaufgabe bekommt im Frontmatter `themen: [...]` mit Slugs aus `_data/themen.yml` (plattformunabhängiges Vokabular; ein Thema ist auf
MatheChecks umgesetzt, wenn es in `_data/lernbereiche.yml` einen Lernbereich mit gleichem Slug
gibt). Der Index `_themen.json` wird daraus beim Validieren automatisch erzeugt.

```yaml
teilaufgaben:
  - bezeichnung: "3.2.4"
    punkte: 4
    themen: ["mehrstufige-produktionsprozesse", "quadratische-funktionen"]
```

- **Kern taggen, nicht Hilfsmittel:** nur Themen, deren Kompetenzen die Teilaufgabe im Kern
  prüft (meist 1, selten 2–3). Reine Werkzeuge nicht zusätzlich taggen, z. B. Matrizenmultiplikation
  in Produktionsprozessen, Ableiten bei Kennzahlberechnungen, Gleichungslösen.
- Zur Abgrenzung die `Ich kann`-Texte der Checks in `_data/checks.json` heranziehen.
- Aufgaben ohne `teilaufgaben`: `themen` auf Aufgabenebene setzen. Eine Datei wird immer
  vollständig getaggt (alle Teilaufgaben) oder gar nicht.
- **Neues Thema** nur, wenn kein bestehendes sinnvoll passt: in `_data/themen.yml` ergänzen
  (Zuschnitt etwa in Lernbereichsgröße, Slug-Konvention wie bei Lernbereichen) und im Chat melden.

## 9. Validieren

Führe nach jedem Batch aus und behebe Fehler sofort:

```
.venv\Scripts\python.exe muster-pruefungen/abitur/pruefungen/schema/validate_frontmatter.py
```

Der Validator prüft:

- Schema, Themen-Slugs und den Abgleich `themen.yml` ↔ `lernbereiche.yml`.
- Je Aufgabe-Datei: Jedes Teilaufgaben-Label steht genau einmal in der Aufgabenstellung und
  (bei befülltem Erwartungshorizont) genau einmal im Erwartungshorizont. Es gibt keine
  unbekannten Labels, die Punktesumme der Teilaufgaben stimmt, alle `_assets`-Bilder existieren,
  `enthaelt_grafik` passt und es sind keine STUB-Reste übrig.
- Je Prüfung: Die Aufgabe-Dateien aus `_index.md` existieren, es gibt keine ungenutzten Bilder
  und einen Eintrag in `_inventar.json`.

Nur wenn alles fehlerfrei ist, schreibt er `_themen.json` neu. Eigene Prüfskripte sind nicht
nötig; `[WARN]`-Zeilen (z. B. noch offene Stubs) prüfst du und behebst sie, soweit sie die
aktuelle Prüfung betreffen.

## 10. Coverage-Check

Gleiche das Inventar aus Schritt 2 mit den erzeugten Dateien ab:

- Jede Teilaufgabe steht in genau einer Datei.
- Jeder relevante Seitenbereich ist abgedeckt.

So fällt auch der Fall „Schema ok, aber zwei Seiten fehlen“ auf.

## 11. Visuelle Endkontrolle

Vergleiche ein bis zwei Dateien stichprobenhaft mit den Original-Seiten. Achte besonders auf
Exponenten, Vorzeichen, Indizes und Ergebniswerte.

## 12. Projekt-Inventar aktualisieren

Ergänze `_inventar.json` direkt mit dem Edit-Werkzeug um folgende Felder: `id`, `land`,
`schulform`, `jahr`, `termin`,
`niveau`, `status` (`vollstaendig`/`teilweise`), `fortschritt` und `pfad`. Bei `teilweise`
beschreibst du in `fortschritt` kurz, was noch fehlt.

> Aufgabe-`id`s und Teilaufgaben-Labels sind stabil: Sie werden in `_themen.json` und ggf. in
> `hinweise` von `klausuren/*/config.yml` referenziert. Ändere sie nachträglich nur in Absprache.

## 13. Erkenntnisse festhalten

Neue Sonderfälle, widerlegte Annahmen und Konventionsentscheidungen trägst du knapp in `sonderfaelle.md` ein.

## Umfang und Rückfragen

Nenne bei großen PDFs kurz den Umfang laut Inventar und arbeite dann selbstständig in Batches.
Die Größe allein ist kein Grund für eine Rückfrage. Frag nur bei echter Mehrdeutigkeit nach:
Land- oder Kurszuordnung, widersprüchliche Seitenangaben, unleserliche Stellen.
