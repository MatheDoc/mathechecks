---
description: "Startet die PDF-zu-Markdown-Konvertierungspipeline für Abitur-Prüfungen (Schema, Scaffold, Grafik-Extraktion, KI-Transkription, Validierung)."
name: "Prüfung PDF zu MD konvertieren"
argument-hint: "Nenne die zu konvertierende(n) PDF-Datei(en)/Ordner (ggf. mehrere Prüfungen)"
agent: "agent"
---

Du konvertierst eine oder mehrere Abitur-Prüfungen (PDF) in strukturierte Markdown-Dateien mit
YAML-Frontmatter, nach dem in diesem Repository etablierten Schema und Workflow. Arbeite die
folgenden Schritte der Reihe nach ab. Wenn etwas unklar/mehrdeutig ist, frage kurz nach statt zu
raten - insbesondere bei Bundesland/Kursart/Aufgaben-Zusammenstellung (siehe Warnung unten).

Ideale Pipeline im Überblick: PDF sichten → Prüfungsinventar → Datei-/Aufgabenplan → Scaffold →
Grafiken → Transkription → Erwartungshorizont → Schema-Validierung → Coverage-Check →
visuelle Endkontrolle → Projekt-Inventar aktualisieren.

## 0. Kontext laden

- Lies `/memories/repo/pruefungen-md-schema.md` (falls vorhanden) für bereits gesammelte
  Erkenntnisse, Sonderfälle und Konventionen aus früheren Konvertierungen.
- Lies die beiden Schema-Dateien [aufgabe.schema.json](../../abitur/pruefungen/schema/aufgabe.schema.json)
  und [pruefung-index.schema.json](../../abitur/pruefungen/schema/pruefung-index.schema.json) - sie sind
  die verbindliche, aktuelle Quelle für erlaubte Felder/Enums (nicht nur auf Gedächtnis-Notizen
  verlassen, die können veraltet sein).
- Lies [_inventar.json](../../abitur/pruefungen-md/_inventar.json) für den Überblick, welche Prüfungen
  bereits (vollständig oder teilweise) konvertiert sind.
- Prüfe, ob `pruefungen-md/_tools/figures.py`, `pruefungen-md/_tools/scaffold.py` und
  `pruefungen/schema/validate_frontmatter.py` existieren und nutze sie (nicht neu erfinden).

## 1. PDFs sichten, NICHT nur Dateinamen interpretieren

Wichtige Lektion aus früheren Läufen: identische Buchstaben-Suffixe bedeuten in verschiedenen
Bundesland-/Schulform-Ordnern nachweislich Verschiedenes (z. B. `_G_`/`_L_` mal Aufgabe/Lösung,
mal Grundkurs/Leistungskurs). Öffne daher jede genannte PDF-Datei tatsächlich (Titelseite +
Kopfzeilen rendern, siehe Schritt 4) bevor du Land/Schulform/Fachrichtung/Jahr/Termin/Niveau/
Hilfsmittel ins Frontmatter schreibst. Kläre außerdem:
- Wie viele PDFs gehören zusammen, und wie sind sie aufgeteilt (Aufgabe+Lösung getrennt, Teil A/B
  getrennt, alles in einer Datei, Grundkurs/Leistungskurs als eigene Dateien, etc.)? Das variiert
  zwischen Bundesländern/Schulformen und darf nicht als Standardfall angenommen werden.
- Gibt es überhaupt eine Lösung/einen Erwartungshorizont, und falls ja, in derselben oder einer
  separaten Datei?

## 2. Prüfungsinventar erstellen, bevor gescaffoldet wird

Bei längeren PDFs (mehr als ~15 Seiten) zuerst ein Inventar erfassen statt sofort Seite für Seite
zu lesen oder gar direkt zu scaffolden: PDF → Seiten → Prüfungsteile → Aufgaben → Teilaufgaben →
Themenbereiche → Pflicht/Wahl → Lösung vorhanden? Dieses Inventar kann eine kurze Tabelle im Chat
sein, muss keine eigene Datei sein.
- Kopfzeilen-/Seitenzahlmuster per Regex sind dabei nur ein **Indikator** für Seiten- und
  Aufgabengrenzen, keine gesicherte Wahrheit. Bei Konflikten gilt die Priorität: gerenderte
  PDF-Seite (Bild) > `get_text()` > Dateiname/Vermutung. Erkannte Grenzen immer anhand des
  gerenderten Bildes verifizieren.
- Prüfen, ob einzelne Aufgaben-Slots interne Varianten enthalten (z. B. eine zusätzliche
  alternative Aufgabe innerhalb eines Slots) oder ob Teilaufgaben innerhalb einer Aufgabe
  unterschiedliche Themenbereiche abdecken (dann später in mehrere Dateien pro Themenbereich
  aufteilen, siehe Schritt 7).
- Erst nach diesem Inventar committen, wie viele Aufgabe-Dateien es geben wird (Datei-/Aufgabenplan).

## 3. Anti-Halluzinations-Regel

Nichts inhaltlich ergänzen, glätten oder mathematisch "korrigieren", was im Original unklar,
unleserlich oder scheinbar fehlerhaft ist. Zahlen, Indizes, Exponenten, Vorzeichen und Labels
exakt so übernehmen wie im Original abgebildet - auch wenn ein Ergebnis mathematisch seltsam
wirkt. Bei echter Unleserlichkeit (Scan-Qualität, verdeckte Stelle) das im Fließtext explizit als
`<!-- UNSICHER: ... -->` markieren oder nachfragen, statt zu raten.

## 4. Inhalt lesen: PDF-Text ist für Formeln unzuverlässig

`page.get_text()` zerlegt mathematische Ausdrücke häufig in einzelne, unlesbare Fragmente
(Font-Subsets mit Sonderkodierung, absolute Glyph-Positionierung). Verlasse dich für Formeln NICHT
auf reinen Textextrakt. Stattdessen: Seiten mit PyMuPDF als PNG rendern
(`page.get_pixmap(dpi=150-200)`) und per Bildbetrachtung lesen. Fließtext ohne Formeln lässt sich
dagegen meist direkt per `get_text()` lesen (schneller). Beim Transkribieren gezielt Zahlen,
Indizes, Exponenten, Operatoren, Ungleichheitszeichen und Einheiten gegen das gerenderte Bild
gegenchecken - das sind die Stellen, an denen leicht Fehler entstehen.

## 5. Grundgerüst erzeugen (skriptbasiert, kein Rateaufwand)

Für jede identifizierte Prüfung eine YAML-Spec schreiben (Vorlage:
`pruefungen-md/_tools/scaffold.example.yaml`) und
`python pruefungen-md/_tools/scaffold.py <spec.yaml>` ausführen. Das erzeugt automatisch die
korrekte Ordnerstruktur `pruefungen-md/{land}/{schulform-fachrichtung-slug}/{niveau}/{pruefung-id}/`,
den Prüfungs-Index und eine Stub-Datei je Aufgabe mit validem Frontmatter.

## 6. Grafiken extrahieren (skriptbasiert)

Kleines `_tools/extract_figures.py` je Prüfung anlegen (Job-Liste `(pdf, seiten-index, name.png)`),
das `extract_figure()` aus `pruefungen-md/_tools/figures.py` importiert und aufruft. Ergebnisse
landen in `_assets/`. Vor Verwendung mit dem Image-Viewer stichprobenhaft prüfen, ob der
Bildausschnitt sauber ist. Falls `extract_figure()` keine brauchbare Bounding-Box findet (z. B.
rein vektorbasierte Diagramme ohne erkennbare Bilder), ersatzweise die ganze Seite oder einen
manuell festgelegten Seitenbereich zuschneiden - niemals eine Grafik selbst nachzeichnen oder
frei interpretieren. Bildnamen deterministisch aus Aufgabe+Abbildungsnummer ableiten
(z. B. `a2-4-abb1.png`), keine generischen/zufälligen Namen.

## 7. Inhalt in die Stub-Dateien schreiben

- Aufgabenstellung + Erwartungshorizont im jeweiligen Abschnitt ergänzen, Formeln als LaTeX
  (`$...$`/`$$...$$`), Tabellen als GFM-Tabellen, Bilder per Markdown-Link auf `_assets/*.png`.
- Teilaufgaben-Nummerierung im Fließtext als **Bold-Inline mit dem exakten Original-Label**
  (`**2.1.1**`, `**f)**`, `**(1)**` ...) schreiben, NICHT als Markdown-Listen (CommonMark-Listen
  erlauben keine nicht-numerischen/mehrstufigen Marker; außerdem soll das Label 1:1 zum
  `teilaufgaben[].bezeichnung`-Wert im Frontmatter passen).
- Direkt nach der H1-Überschrift ein kurzer kursiver Satz `*...*` für Strukturfakten, die nicht ins
  Frontmatter passen (Pflicht/Wahl-Status, Querverweis bei themenbereich-bedingt aufgesplitteten
  Aufgaben, sonstige Auswahlregeln).
- Wenn eine Aufgabe intern mehrere `themenbereich`-Werte abdeckt (z. B. Teilaufgaben a-d Analysis,
  e-f Lineare Algebra), in mehrere Dateien nach Themenbereich-Grenze aufteilen (nicht künstlich in
  ein Feld pressen). Das gilt unabhängig davon, ob es dabei auch eine Wahl/Pflicht-Struktur gibt.
  Nur bei klarer struktureller Grenze aufteilen, die Originalstruktur sonst nicht künstlich
  verändern, und den Querverweis zwischen den gesplitteten Dateien (siehe kursiver Hinweis oben)
  nicht vergessen.
- `erwartungshorizont.status` bleibt `"keine"`, bis wirklich Lösungsinhalt in der Datei steht -
  danach auf `vollstaendig`/`teilweise` aktualisieren (auch wenn eine Lösungsquelle referenziert
  ist, aber noch nicht übertragen wurde).
- Boilerplate (Deckblatt, Bewertungsbögen, Notenschlüssel-Tabellen, Hinweisseiten "vgl. Unterlagen
  für die Schülerinnen und Schüler") NICHT übernehmen.

## 8. Validieren

`python pruefungen/schema/validate_frontmatter.py` nach jedem Batch an Dateien laufen lassen und
Fehler sofort beheben. Zusätzlich manuell/stichprobenhaft prüfen:
- Referenzierte Bilddateien (`_assets/*.png`) existieren tatsächlich.
- Keine fehlenden oder doppelten Teilaufgaben-Labels gegenüber dem Prüfungsinventar aus Schritt 2.
- Labels im Fließtext stimmen exakt mit `teilaufgaben[].bezeichnung` im Frontmatter überein.

## 9. Coverage-Check

Am Ende das ursprüngliche Prüfungsinventar (Schritt 2) gegen die tatsächlich erzeugten Dateien
abgleichen: jede dort erfasste Aufgabe/Teilaufgabe muss in genau einer Aufgabe-Datei auftauchen,
jeder Seitenbereich muss abgedeckt sein. Ziel: auch den Fall "Frontmatter validiert einwandfrei,
aber inhaltlich fehlen 2 Seiten" erkennen, nicht nur Schema-Konformität prüfen.

## 10. Visuelle Endkontrolle

Stichprobenartig ein bis zwei erzeugte Dateien gegen die Original-PDF-Seiten gegenchecken,
insbesondere mathematisch kritische Stellen (Exponenten, Vorzeichen, Indizes, Ergebniswerte).

## 11. Projekt-Inventar aktualisieren

[_inventar.json](../../abitur/pruefungen-md/_inventar.json) um den neuen/aktualisierten Eintrag ergänzen
(id, land, schulform, jahr, termin, niveau, status vollstaendig/teilweise, fortschritt, pfad). Bei
nur teilweise transkribierten Prüfungen `fortschritt` kurz beschreiben, was fehlt.

## 12. Erkenntnisse festhalten

Neue Sonderfälle, falsche Annahmen oder Konventionsentscheidungen kurz in
`/memories/repo/pruefungen-md-schema.md` ergänzen (falls das Memory-Tool verfügbar ist), damit
künftige Durchläufe davon profitieren.

## Umfang/Rückfragen

Bei sehr umfangreichen PDFs kurz den ermittelten Umfang (Anzahl Aufgaben, Seiten) aus dem
Prüfungsinventar nennen, dann aber selbstständig in Batches weiterarbeiten - nicht wegen der
reinen Größe nachfragen. Nachfragen nur bei echter inhaltlicher Mehrdeutigkeit (z. B. unklare
Bundesland-/Kursart-Zuordnung, widersprüchliche Seitenangaben, unleserliche Stellen).
