# Aufgabengenerator

Modulares Python-Projekt zur Erzeugung und Verwaltung von JSON-Aufgabensammlungen für die MatheChecks-Lernplattform (Analysis, Stochastik u. a.).

## Ordnerstruktur

```
aufgaben/
├── cli.py                  # CLI für Einzel-, Batch- und Validierungsbefehle
├── run.py                  # Kurzskript: python aufgaben/run.py [filter]
├── project_config.json     # Zentrale Konfiguration: jobs + static
├── core/
│   ├── models.py           # Datenmodell (Task, Frage, Antwort)
│   ├── io.py               # JSON-Schreib-Funktionen
│   ├── placeholders.py     # Platzhalter-Auflösung (Plotly etc.)
│   ├── validation.py       # Batch-Plausibilitätsprüfung
│   └── moodle_xml.py       # (pausiert – wird später neu aufgesetzt)
├── generators/
│   ├── base.py             # Abstrakte Basisklasse TaskGenerator
│   ├── registry.py         # Auto-Discovery aller Generatoren
│   ├── analysis/           # Generatoren für Analysis
│   └── stochastik/         # Generatoren für Stochastik
├── exports/
│   └── json/               # Ausgabeverzeichnis (gebiet/lernbereich/sammlung.json)
├── preview/                # Lokale HTML-Vorschau der erzeugten Aufgaben
├── runtime/                # JS-Rendering für die Website
└── tools/
    └── validate_binomial_semantics.py
```

## Zentrale Konfiguration: `project_config.json`

`project_config.json` ist die **einzige Quelle** für die Zuordnung von Aufgabensammlungen zu Gebieten und Lernbereichen. Es gibt zwei Arten von Einträgen:

### Jobs (generierte Sammlungen)

Jeder Job verknüpft einen Generator mit einem oder mehreren Ausgabezielen (`targets`):

```json
{
  "defaults": {
    "count": 20,
    "outputDir": "aufgaben/exports/json",
    "questionOrder": "fixed"
  },
  "jobs": [
    {
      "generator": "analysis.regression",
      "seed": 42,
      "targets": [
        {
          "gebiet": "analysis",
          "lernbereich": "analysis-diverses",
          "sammlung": "regression",
          "questionOrder": "shuffle"
        }
      ]
    }
  ]
}
```

Beim Batch-Lauf erzeugt jeder Job eine JSON-Datei unter:  
`aufgaben/exports/json/<gebiet>/<lernbereich>/<sammlung>.json`

### Static (handgepflegte Sammlungen)

Sammlungen, die nicht durch einen Generator erzeugt werden, sondern manuell erstellt und gepflegt sind:

```json
{
  "static": [
    {
      "gebiet": "analysis",
      "lernbereich": "ertragsgesetzliche-kostenfunktionen",
      "sammlung": "nachweis"
    }
  ]
}
```

Static-Einträge liegen als JSON-Dateien im gleichen Verzeichnisschema.  
Sie werden beim Cleanup **nicht gelöscht**, solange sie in `project_config.json` registriert sind.

### Cleanup-Regel

Nach einem vollständigen Batch-Lauf (ohne `--filter`) werden alle JSON-Dateien in `exports/json/` gelöscht, die **weder** einem Job-Target **noch** einem Static-Eintrag entsprechen. Das stellt sicher, dass verwaiste Dateien automatisch entfernt werden.

## Bezug zu `dev/checks.json`

`checks.json` ist die zentrale Kompetenzliste der Website. Jeder Eintrag dort verweist über `Sammlung` auf den Dateinamen einer Aufgabensammlung (ohne `.json`).  
Die Kette ist:

```
checks.json  →  Sammlung: "regression"
                         ↓
project_config.json  →  targets[].sammlung: "regression"
                         ↓
aufgaben/exports/json/analysis/analysis-diverses/regression.json
```

`checks.json` bestimmt, welche Sammlungen die Website verwendet.  
`project_config.json` bestimmt, welche Sammlungen erzeugt bzw. vorgehalten werden.  
Beide müssen konsistent sein.

## CLI

### Batch (empfohlen)

Alle Jobs ausführen:

```bash
python -m aufgaben.cli batch --config aufgaben/project_config.json
```

Oder kürzer über das Hilfsskript:

```bash
python aufgaben/run.py
```

Mit Filter (nur passende Jobs):

```bash
python aufgaben/run.py binomial
python -m aufgaben.cli batch --config aufgaben/project_config.json --filter e2k3
```

Bei Verwendung von `--filter` wird kein Cleanup durchgeführt.

### Einzelgenerator

```bash
python -m aufgaben.cli generate analysis.regression --count 20 --seed 42
```

### Verfügbare Generatoren auflisten

```bash
python -m aufgaben.cli list
```

### Binomial-Semantik prüfen

```bash
python -m aufgaben.cli validate-binomial
```

## Aufgabenauswahl und Fragen-Reihenfolge

### Zwei unabhängige Zufallsebenen

1. **Aufgabenauswahl (Sammlung → Aufgabe):**  
   Jede Sammlung enthält in der Regel ~20 Aufgaben. Das Frontend wählt bei jeder Anzeige zufällig eine davon aus (bzw. beim Reload eine andere). Das ist **immer** der Fall und unabhängig von `questionOrder`.

2. **Fragen-Reihenfolge (innerhalb einer Aufgabe):**  
   Jede Aufgabe hat ein Array `fragen` mit zugehörigem Array `antworten`. Ob diese Paare bei der Anzeige permutiert werden, steuert `questionOrder` in `dev/checks.json`:
   - `"fixed"` – Reihenfolge wie im Generator bzw. in der JSON-Datei definiert.
   - `"shuffle"` – Frage-Antwort-Paare werden bei jedem Rendern zufällig permutiert (Fisher-Yates).

### Wo wird was entschieden?

| Aspekt | Quelle | Ort |
|---|---|---|
| Aufgabenauswahl (welche der ~20) | Frontend | `dev/assets/js/modules/training.js` |
| Fragen-Reihenfolge | `questionOrder` in `dev/checks.json` | Frontend (`training.js`, `script-task-duplicates.js`) |
| Aufgabenerzeugung | Generatoren / statische JSON | `aufgaben/` (CLI) |

### Regeln

- Generatoren erzeugen Aufgaben **immer in fester Reihenfolge** – kein Shuffling in der CLI oder in Generatoren.
- `questionOrder` wird ausschließlich in `dev/checks.json` pro Check-Eintrag gesetzt.
- Das Frontend liest `questionOrder` aus den Check-Daten und shuffelt die Fragen/Antworten nur bei `"shuffle"`.

## Neuen Generator anlegen

1. Neue Klasse in `aufgaben/generators/<bereich>/...` von `TaskGenerator` ableiten.
2. `generator_key` setzen (z. B. `analysis.nullstellen.linear`).
3. Job mit `targets` in `project_config.json` ergänzen.
4. Passenden Eintrag in `dev/checks.json` anlegen (mit übereinstimmender `Sammlung`).

## Neue statische Sammlung anlegen

1. JSON-Datei manuell unter `aufgaben/exports/json/<gebiet>/<lernbereich>/<sammlung>.json` ablegen.
2. Eintrag in `project_config.json` unter `"static"` hinzufügen.
3. Passenden Eintrag in `dev/checks.json` anlegen.

## Moodle-XML-Export

Aktuell pausiert. Der vorhandene Code in `core/moodle_xml.py` wird zu einem späteren Zeitpunkt von Grund auf neu aufgesetzt.

## Visuals (Hybrid)

Optional kann eine Aufgabe ein zusätzliches Feld `visual` enthalten. Das kanonische Aufgaben-JSON bleibt dabei bildfrei und kann stattdessen eine Spezifikation für die Web-Darstellung tragen.

Beispiel:

```json
{
	"einleitung": "...",
	"fragen": ["..."],
	"antworten": ["{1:NUMERICAL:=...}"],
	"visual": {
		"type": "plot",
		"spec": {
			"functions": ["E", "K", "G"],
			"xRange": [0, 80]
		}
	}
}
```

Wenn `visual.spec` vorhanden ist, kann die Web-Vorschau (`preview.js`) das Diagramm clientseitig rendern.

### Visuelle Spec-Typen (`visual.spec.type`)

Eigene kompakte Spec-Typen sind gegenüber rohen `"plotly"`-Trace-Arrays bevorzugt:

| Typ | Beschreibung |
|---|---|
| `cost-curves` | Grenzkosten-, Stückkosten-, variable Stückkostenfunktion (K3-Polynom) |
| `market-curves` | Einfaches lineares Marktdiagramm |
| `market-equilibrium` | Marktgleichgewicht mit variablen Funktionstypen (linear/quadratisch/exp); `p_N` endet bei `satX` |
| `market-abschoepfung` | Preisdifferenzierung mit KR1/KR2-Flächen |
| `economic-curves` | Erlös-, Kosten-, Gewinnfunktion |
| `plotly` | Fallback: explizite Trace-Arrays mit x/y-Werten |
| `vft` | Vier-Felder-Tafel als DOM-Tabelle (kein Plotly) |
| `wkt-tabelle` | Diskrete Wahrscheinlichkeitsverteilung (x-Zeile + P-Zeile, `null` = leere Zelle) |

Neue Diagrammtypen erhalten einen eigenen Branch in `preview.js` (`renderVisual` → `else if (specType === '...')`). Tabellendaten nie als HTML in `einleitung` hartcodieren, sondern als `visual` mit passendem `spec.type` übergeben.

### Parameter-Format für Funktionen in Specs

```json
{ "type": "linear",    "a": 1.5,  "b": 3.2 }
{ "type": "quadratic", "a": 0.03, "b": 0.15, "c": 2.0 }
{ "type": "exp",       "A": -18.5, "rate": 0.12, "c": 21.0 }
```

Alle Parameterwerte sind auf sinnvolle Dezimalstellen gerundet (max. 3–4 NKS).

## Namenskonventionen

### Sammlung-Namen (`sammlung` in `project_config.json`)

- Format: `kebab-case`
- Nur inhaltliche Bezeichnung, kein Gebiets- oder Lernbereichspräfix
- Beispiele: `kennzahlen-graphisch-allgemein`, `kennzahlen-rechnerisch-lqe`, `renten-bestimmung-prkr`, `abschoepfung-kr-bestimmung-preis`

Der `sammlung`-Name bestimmt direkt den Dateinamen der JSON-Ausgabe (z. B. `kennzahlen-graphisch-allgemein.json`) sowie den Ablageordner unter `aufgaben/exports/json/<gebiet>/<lernbereich>/`.

## Toleranzregeln

- **Analysis:** Möglichst (Ausnahmen bei Steckbriefaufgaben) höchstens 2 zählende Stellen bei erzeugten Zufallszahlen.
  Richtig: `0,3` · `450` · `0,056` · `40` · `8`
  Falsch: `723` · `23,4` · `0,928` · `3,54`
- **Stochastik:** Gegebene Wahrscheinlichkeit mit höchstens 4 Nachkommastellen.
- **Diagramme:**
  - Werte so wählen, dass Graphen ihr typisches Erscheinungsbild im Sachzusammenhang haben.
  - Gesuchte Werte müssen gut abgelesen werden können.
  - Standardtoleranz für Ableseaufgaben: ein Viertel der Schrittweite der jeweiligen Achse.

### Natürliche Fragesätze statt technischer Labels

Fragen sollen als **vollständige, natürliche Sätze** formuliert sein — besonders bei Sachaufgaben. Keine formalen Variablen vor dem Eingabefeld.

**Richtig**: `"Welche maximale Höhe erreicht der Speer?"`  
**Falsch**: `"Maximale Höhe (Scheitelpunkt): $ h(x_S) = $"`

**Richtig**: `"Bei welchem Preis wird der Gewinn maximal?"`  
**Falsch**: `"Bei welchem Preis wird der Gewinn maximal? $ p = $"`

## Formulierungen

### Hinweise bei Mehrdeutigkeit

Wenn die Antwort eine Sortierung oder Fallunterscheidung erfordert, den Hinweis in die Frage integrieren:

```python
_FRAGE = (
    "Geben Sie die $ x $-Werte in aufsteigender Reihenfolge an. "
    "Bei nur einer Lösung: beide Felder füllen."
)
```
