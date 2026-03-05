# Aufgabengenerator

Kleines, modulares Python-Projekt zur Erzeugung von JSON-Aufgaben für verschiedene Teilbereiche (z. B. Analysis, Lineare Algebra, Stochastik).

## Struktur

- `aufgaben/core`: Datenmodell, Placeholder, Validierung, JSON-Export
- `aufgaben/generators`: Fachliche Generatoren je Teilbereich
- `aufgaben/cli.py`: CLI für Einzel- und Batch-Erzeugung
- `aufgaben/project_config.json`: Batch-Jobs

## CLI

Generatoren anzeigen:

```bash
python -m aufgaben.cli list
```

Einen Generator starten:

```bash
python -m aufgaben.cli generate analysis.regression --count 20 --seed 42
```

Batch aus Konfiguration ausführen:

```bash
python -m aufgaben.cli batch --config aufgaben/project_config.json
```

Interne Plausibilitätsprüfung für Binomial-Semantik ausführen:

```bash
python -m aufgaben.tools.validate_binomial_semantics
```

Alternativ direkt über die CLI:

```bash
python -m aufgaben.cli validate-binomial
```

## Zuordnung zu Lernbereichen

Die Zuordnung erfolgt über `aufgaben/project_config.json` (nicht hart im Code).
Ein Generator kann mehrere Lernbereiche/Sammlungen bedienen.

Beispiel:

```json
{
	"defaults": {
		"count": 20,
		"outputDir": "aufgaben/exports/json"
	},
	"jobs": [
		{
			"generator": "analysis.regression",
			"seed": 42,
			"targets": [
				{
					"gebiet": "analysis",
					"lernbereich": "analysis-diverses",
					"sammlung": "regression-linear"
				},
				{
					"gebiet": "analysis",
					"lernbereich": "marktgleichgewicht-vertiefung",
					"sammlung": "regression-linear-variante",
					"seed": 99
				}
			]
		}
	]
}
```

Konvention:
- `sammlung` nur als fachlicher Kurzname (z. B. `nullstellen-linear`, `regression-linear`).
- `gebiet` und `lernbereich` bleiben eigene Felder in `targets`.

Resultierende Pfade:
- `aufgaben/exports/json/<gebiet>/<lernbereich>/<sammlung>.json`

## Reihenfolge von Fragen

Über `questionOrder` steuerst du, ob Fragen pro Aufgabe permutiert werden:

- `fixed`: Reihenfolge bleibt wie im Generator definiert.
- `shuffle`: Frage-Antwort-Paare werden gemeinsam zufällig permutiert.

Unterstützt auf drei Ebenen (Priorität):
- `targets[].questionOrder` > `jobs[].questionOrder` > `defaults.questionOrder`

## Erweiterung

1. Neue Klasse in `aufgaben/generators/<bereich>/...` von `TaskGenerator` ableiten.
2. In der Klasse `generator_key` setzen (z. B. `analysis.nullstellen.linear`).
3. Job und `targets` in `aufgaben/project_config.json` ergänzen.

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
