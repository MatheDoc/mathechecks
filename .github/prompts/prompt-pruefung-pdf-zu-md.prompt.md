---
description: "Konvertiert Abitur-Musterprüfungen (PDF) in strukturierte Markdown-Dateien mit validiertem YAML-Frontmatter (Inventar, Scaffold, Grafiken, Transkription, Validierung)."
name: "Prüfung PDF zu MD konvertieren"
argument-hint: "PDF-Datei(en) oder Ordner unter muster-pruefungen/abitur/pruefungen/"
agent: "agent"
---

# Prompt: Musterprüfung PDF → Markdown

Du konvertierst eine oder mehrere Abitur-Prüfungen (PDF) in Markdown-Dateien mit YAML-Frontmatter.
Die Exporte dienen als **KI-Kontext für Klausurerstellung und Content-Entwicklung**. Priorität
haben deshalb exakte Aufgabentexte, Teilaufgaben-Labels, Punkte, Operatoren und
Erwartungshorizont. Layouttreue ist zweitrangig. Arbeite die Schritte der Reihe nach ab.

Pipeline: PDF sichten → Prüfungsinventar → Datei-/Aufgabenplan → Scaffold → Grafiken →
Transkription → Validierung → Coverage-Check → visuelle Endkontrolle → Projekt-Inventar.

## Pfade

Alle Befehle werden vom Repo-Root aus ausgeführt. `MP` steht für `muster-pruefungen/abitur`.
Der Ordner `muster-pruefungen/` ist per gitignore ausgeschlossen (urheberrechtlich geschützte
Inhalte). Nur dieser Prompt wird versioniert.

| Inhalt | Pfad |
|---|---|
| Original-PDFs (Quelle der Wahrheit) | `MP/pruefungen/<land schulform …>/` |
| Schemas + Validator | [aufgabe.schema.json](../../muster-pruefungen/abitur/pruefungen/schema/aufgabe.schema.json), [pruefung-index.schema.json](../../muster-pruefungen/abitur/pruefungen/schema/pruefung-index.schema.json), `MP/pruefungen/schema/validate_frontmatter.py` |
| MD-Exporte | `MP/pruefungen-md/{land}/{schulform-slug}/{niveau}/{pruefung-id}/` |
| Projekt-Inventar | [_inventar.json](../../muster-pruefungen/abitur/pruefungen-md/_inventar.json) |
| Gemeinsame Tools | `MP/pruefungen-md/_tools/` (`scaffold.py`, `scaffold.example.yaml`, `figures.py`) |

Python-Abhängigkeiten: `pip install pymupdf pyyaml jsonschema`.

## 0. Kontext laden

- Lies beide Schemas: Sie sind die verbindliche Quelle für erlaubte Felder und Enums.
- Lies `_inventar.json`, um zu sehen, welche Prüfungen bereits ganz oder teilweise konvertiert sind.
- Lies den Abschnitt [Bekannte Sonderfälle](#bekannte-sonderfälle) am Ende dieses Prompts.
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

`page.get_text()` zerlegt Formeln oft in unbrauchbare Fragmente. Ursache sind Font-Subsets und
die absolute Positionierung der Glyphen.

- Für Formeln: Seiten mit PyMuPDF rendern (`page.get_pixmap(dpi=150-200)`) und das Bild lesen.
- Für reinen Fließtext ohne Formeln reicht `get_text()`.
- Gleiche Zahlen, Indizes, Exponenten, Operatoren, Ungleichheitszeichen und Einheiten gezielt mit
  dem Bild ab.

## 5. Grundgerüst erzeugen

Schreibe eine YAML-Spec nach dem Muster von `MP/pruefungen-md/_tools/scaffold.example.yaml` und
führe aus:

```
python muster-pruefungen/abitur/pruefungen-md/_tools/scaffold.py <spec.yaml>
```

Das Skript erzeugt Ordnerstruktur, `_index.md` und je Aufgabe eine Stub-Datei mit validem
Frontmatter.

> ⚠️ `scaffold.py` überschreibt vorhandene Dateien ohne Rückfrage. Führe es nur für neue
> Prüfungen aus, niemals über bereits transkribierte Ordner.

## 6. Grafiken extrahieren

- Lege je Prüfung ein Skript `<pruefung-id>/_tools/extract_figures.py` mit einer Job-Liste
  `(pdf, seiten-index, name.png)` an. Es importiert `extract_figure()` aus `_tools/figures.py`.
  Die Ergebnisse landen in `<pruefung-id>/_assets/`.
- Verwende **keine absoluten Pfade**, alles relativ zu `__file__` (die Arbeit läuft auf mehreren
  Rechnern). Vorlage: `MP/pruefungen-md/nw/bgym-wuv/erhoeht/nw-bgym-wuv-2025-haupt-erhoeht/_tools/extract_figures.py`.
- Prüfe die Ausschnitte stichprobenhaft im Bild-Viewer.
- Findet das Skript keine Bounding-Box, schneidest du die ganze Seite oder einen manuell
  festgelegten Bereich zu. Grafiken werden nie nachgezeichnet.
- Bildnamen sind deterministisch, z. B. `a2-4-abb1.png`.

## 7. Inhalt in die Stubs schreiben

- Aufgabenstellung und Erwartungshorizont kommen in die jeweiligen Abschnitte.
  - Formeln als LaTeX (`$…$`/`$$…$$`)
  - Tabellen als GFM
  - Bilder als Link auf `_assets/*.png`
- Teilaufgaben-Labels schreibst du als **Bold-Inline mit dem exakten Original-Label** (`**2.1.1**`,
  `**f)**`, `**(1)**`), nicht als Markdown-Liste. Jedes Label muss 1:1 einem
  `teilaufgaben[].bezeichnung` im Frontmatter entsprechen.
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

## 8. Validieren

Führe nach jedem Batch aus und behebe Fehler sofort:

```
python muster-pruefungen/abitur/pruefungen/schema/validate_frontmatter.py
```

Prüfe zusätzlich:

- Alle referenzierten `_assets/*.png` existieren.
- Kein Teilaufgaben-Label fehlt oder ist doppelt (Abgleich mit dem Inventar aus Schritt 2).
- Labels im Fließtext und `teilaufgaben[].bezeichnung` stimmen exakt überein.

## 9. Coverage-Check

Gleiche das Inventar aus Schritt 2 mit den erzeugten Dateien ab:

- Jede Teilaufgabe steht in genau einer Datei.
- Jeder relevante Seitenbereich ist abgedeckt.

So fällt auch der Fall „Schema ok, aber zwei Seiten fehlen“ auf.

## 10. Visuelle Endkontrolle

Vergleiche ein bis zwei Dateien stichprobenhaft mit den Original-Seiten. Achte besonders auf
Exponenten, Vorzeichen, Indizes und Ergebniswerte.

## 11. Projekt-Inventar aktualisieren

Ergänze `_inventar.json` um folgende Felder: `id`, `land`, `schulform`, `jahr`, `termin`,
`niveau`, `status` (`vollstaendig`/`teilweise`), `fortschritt` und `pfad`. Bei `teilweise`
beschreibst du in `fortschritt` kurz, was noch fehlt.

> Aufgabe-`id`s und Teilaufgaben-Labels sind stabil: Sie werden in `klausuren/*/config.yml`
> (`vorlagen`) referenziert. Ändere sie nachträglich nur in Absprache.

## 12. Erkenntnisse festhalten

Neue Sonderfälle, widerlegte Annahmen und Konventionsentscheidungen trägst du knapp unten im
Abschnitt [Bekannte Sonderfälle](#bekannte-sonderfälle) ein.

## Umfang und Rückfragen

Nenne bei großen PDFs kurz den Umfang laut Inventar und arbeite dann selbstständig in Batches.
Die Größe allein ist kein Grund für eine Rückfrage. Frag nur bei echter Mehrdeutigkeit nach:
Land- oder Kurszuordnung, widersprüchliche Seitenangaben, unleserliche Stellen.

## Bekannte Sonderfälle

- **Dateinamen-Suffixe sind ordnerabhängig:**
  - `nw allg gym` (`M_23_c_L_NT_GG.pdf`): `G`/`L` = Grundkurs/Leistungskurs. Eine Datei enthält
    je Aufgabe Aufgabenstellung **und** Modelllösung („Unterlagen für die Lehrkraft“).
  - `nw berufl gym wv lk|gk` (`mathe_wlk_wuv_abitur2025_ht_cas_s.pdf`): `_s`/`_l` =
    Schüler-/Lösungsdatei, `ohimi`/`cas` = Prüfungsteil A/B, `wlk`/`gk` = Kursart.
- **NW Gymnasium, Teil A:** Die Teilaufgaben einer Pflichtaufgabe mischen Themenbereiche (z. B. A1
  a–d Analysis, e–f LinAlg). Lösung: Split in `a1-analysis.md` und `a1-linalg.md`.
- **NW Berufliches Gymnasium WuV:** Teil A hat 4 Pflicht- und 4 Wahlaufgaben (2 aus 4), jede als
  eigene Datei. Die 5 Punkte Darstellungsleistung sind keiner Aufgabe zugeordnet; sie zählen nur
  in `gesamtpunkte` des Index.
- **NW Berufliches Gymnasium WuV 2023 (WLK):** Teil A hat nur 4 Pflichtaufgaben 1.1–1.4 (je 6 Punkte,
  keine Wahl), Teil B 3 Aufgaben mit je 32 Punkten (Summe 125 inkl. 5 Punkte Darstellung). Der
  Erwartungshorizont nutzt feinere Bewertungspositionen (z. B. `2.1.2.1`, `2.1.2.2`; bei Aufgabe 3.4
  das Label `3.4.1`). Diese werden je Teilaufgabe zusammengefasst, Einzelpunkte und AFB stehen in
  Klammern. Zierfotos ohne mathematischen Inhalt (Abbildungen 2–4) werden nicht übernommen.
  Grafiken im Erwartungshorizont, die in Tabellenzeilen stecken, brauchen einen manuellen Ausschnitt
  (4. Tupel-Element in `extract_figures.py`), da `figure_bbox` sonst die ganze Tabelle erfasst.
- **GK-PDFs (`nw berufl gym wv gk`)** liegen teils nur als 1-Byte-Platzhalter vor (Google-Drive-Sync)
  und können nicht gelesen werden; vor der Konvertierung die Dateigröße prüfen.
- **Einfache Baumdiagramme** im Erwartungshorizont (nur Zahlenlabels) dürfen als Text übertragen
  werden. Dieser Fall wird in „Bekannte Lücken“ vermerkt.
