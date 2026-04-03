# Diskussionsstand - Kennzahlen graphisch E2K3 (Check 4)

Zusammenfassung der Optimierungsrunde (Stand April 2026).

---

## 1 Ausgangslage und Ziel

Ziel fuer Check 4 (Angebotsmonopol) war eine analoge Ueberarbeitung wie bei E1K3:

- parameterstabile, aber variantenreiche Kurvenformen,
- y-Achse didaktisch klar gesteuert,
- x-Achse bis kurz nach der Saettigungsmenge,
- robuste numerische Kriterien fuer gueltige Aufgaben.

---

## 2 Umgesetzte Loesung (Generator)

Datei:
`aufgaben/generators/analysis/ganzrationale_oekonomische_funktionen/kennzahlen_graphisch_e2k3.py`

### 2.1 Musterfunktionen als Basis

Eingebaute Template-Basis:

- `E(x) = -0.15x^2 + 2x`
- `K(x) = 0.02x^3 - 0.25x^2 + x + 3`

Die Zufallsparameter werden potenzbewusst skaliert (x/y-Scale + Wobble), analog zur E1K3-Idee.

### 2.2 Harte Plausibilitaetsbedingungen

Im Sampler werden weiterhin harte Bedingungen geprueft, u. a.:

- `a2 < 0`, `a1 > 0` fuer die Erlösfunktion,
- `k3 > 0`, `k2 < 0`, `k1 > 0`, `k0 > 0` fuer die Kostenfunktion,
- Monotoniebedingung fuer K: `k2^2 <= 3*k3*k1`,
- positive Gewinnphase mit gueltiger Gewinnschwelle/Gewinngrenze.

### 2.3 Ausgabeformat (visual.spec)

Der Export wurde auf ein kompaktes Spezifikationsformat umgestellt:

- `type: "economic-curves"` statt großer `plotly`-Trace-Arrays,
- Parameter in `spec.params` (u. a. `a2`, `a1`, `k3`, `k2`, `k1`, `k0`, `capacity`, `xMax`),
- Achsenbereiche explizit in `layout.xaxis.range` und `layout.yaxis.range`.

---

## 3 Achsenregeln (final)

### 3.1 y-Achse

Umgesetzt gemaess Vorgabe:

- `y_max` liegt etwas ueber dem Erlösmaximum,
- `y_min` liegt etwas unterhalb von `G(0)`.

Konkret im Generator:

- `y_min = G(0) - max(2.0, 0.08 * Referenzspanne)`
- `y_max = E_max + max(3.0, 0.08 * E_max)`
- zusaetzliche Sicherheitschecks garantieren weiterhin `y_min < G(0)` und `y_max > E_max`.

### 3.2 x-Achse

Finale Regel (nach Feinschliff):

- `x_max = x_saettigung * U(1.03, 1.08)`

Interpretation: Diagramm endet gezielt kurz nach der Saettigungsmenge.

---

## 4 Verifikation (zuletzt gemessen)

Ziel-JSON:
`aufgaben/exports/json/analysis/ganzrationale-oekonomische-funktionen/kennzahlen-graphisch-e2k3.json`

### 4.1 y-Regeln (20 Aufgaben)

- `y_max > E_max`: fuer alle Aufgaben erfuellt
- `y_min < G(0)`: fuer alle Aufgaben erfuellt

Gemessene Margins:

- top margin (`y_max - E_max`): min `5.882`, median `20.353`, max `39.574`
- bottom margin (`G(0) - y_min`): min `8.027`, median `29.585`, max `53.331`

### 4.2 x-Regel zur Saettigungsmenge (20 Aufgaben)

- `x_max / x_saettigung`: min `1.033`, median `1.058`, max `1.079`
- alle Aufgaben im Zielband `[1.03, 1.08]`.

---

## 5 Reproduzierbare Kommandos

Check 4 gezielt neu erzeugen:

```bash
python aufgaben/run.py kennzahlen-graphisch-e2k3
```

x_max-Saettigungs-Check (Auswertung):

```bash
python -c "import json, statistics; from pathlib import Path
p=Path('aufgaben/exports/json/analysis/ganzrationale-oekonomische-funktionen/kennzahlen-graphisch-e2k3.json')
data=json.loads(p.read_text(encoding='utf-8'))
rat=[]
for t in data:
    pr=t['visual']['spec']['params']
    rat.append(float(pr['xMax'])/float(pr['capacity']))
print('xmax/x_sat min/med/max', round(min(rat),3), round(statistics.median(rat),3), round(max(rat),3))
print('all in 1.03..1.08', all(1.03 <= r <= 1.08 for r in rat))"
```

---

## 6 Offene optionale Feintuning-Punkte

- y-Margins enger setzen, falls der Plot noch kompakter gewuenscht ist.
- x-Band bei Bedarf enger setzen (z. B. 1.04-1.07) fuer noch einheitlichere Darstellungen.
- Falls gewuenscht, dieselbe Dokumentationsstruktur fuer weitere Checks fortfuehren.
