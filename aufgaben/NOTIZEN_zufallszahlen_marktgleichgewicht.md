# Zufallszahlen & Parameterwahl – Marktgleichgewicht

Zusammenfassung der Optimierungsrunde (Stand April 2026).

---

## 1  Ausgangsprobleme

| Problem | Betroffene Generatoren |
|---|---|
| Gleichgewichtspunkt oft am Rand oder kaum sichtbar | Grundlagen + Vertiefung |
| Sättigungsmenge fast immer ≈ 10, Achsen immer 0–10 | Grundlagen |
| Plotly skaliert y-Achse an Angebotskurve statt an Höchstpreis | Vertiefung Check 1 |
| KR-Flächen bei Abschöpfung zu klein / zu nah am Rand | Vertiefung Checks 4 & 5 |
| `uniform_sig` braucht ~218 ms / 1000 Aufrufe (Kandidaten-Grid) | Alle |

---

## 2  Kernergebnisse

### 2.1  `nice_axis_max()` (tolerances.py)

Rundet einen Wert auf die nächste `axis_tick_step`-Grenze auf.
Verhindert, dass Plotly „unrunde" Achsen-Obergrenzen wählt.

### 2.2  Grundlagen – `_sample_linear_market_parameters`

Datei: `generators/analysis/marktgleichgewicht_grundlagen/shared.py`

| Parameter | Bereich | Anmerkung |
|---|---|---|
| `supply_slope` | 0,1 – 4,0 | `uniform_sig` (≤ 2 sig. Stellen) |
| `demand_slope` | 0,1 – 4,0 | |
| `min_price` | 1 – 80 | |
| `max_price` | min + 5 … min + 300 | Cap 950 |
| `sat_quantity` | ≥ 3 (bis ~950) | `max_price / demand_slope` |
| `eq_quantity` | ≥ 1,5 ; ≤ 80 % der Sättigungsmenge | |
| `eq_price` | ≤ 85 % des Höchstpreises | |

Diese Bereiche erzeugen Achsen von klein (≈ 15) bis groß (≈ 700).

### 2.3  Vertiefung – `_sample_market_params`

Datei: `generators/analysis/marktgleichgewicht_vertiefung/shared.py`

**Angebotsfunktion** (zufällig linear / quadratisch / exponentiell):

| Typ | Schlüsselparameter |
|---|---|
| linear | slope 0,12–4,5 ; intercept 1–45 |
| quadratisch | a₂ 0,003–0,12 ; a₁ 0,05–0,8 ; a₀ 1–45 |
| exponentiell | amplitude 3–80 ; rate 0,02–0,25 ; min_price 1–40 |

**Nachfragefunktion** (zufällig linear / quadratisch / exponentiell):

| Typ | Schlüsselparameter |
|---|---|
| linear | slope 0,15–5 ; intercept min+4 … min+250 |
| quadratisch | a₂ 0,005–0,2 ; a₁ 0,01–0,5 ; a₀ min+4 … min+250 |
| exponentiell | amplitude 4–120 ; rate 0,02–0,22 ; floor −15 … −0,3 |

**Filterregeln:**

- `max_price ≤ 950`, `sat_quantity` 3–950, `eq_x ≥ 1,5`
- Gleichgewicht im Bereich: `eq_x ≤ 85 % sat_quantity`, `eq_p` zwischen min + 0,5 und max − 0,5
- Nachfrage streng fallend: Ableitung < −0,01 bei x = 0 und x = eq_x
- **KR-Abschöpfung (Checks 4 & 5):** `p2` muss ≥ 15 % von `(max_price − eq_p)` Abstand zu **beiden** Rändern halten → KR₁ und KR₂ sind immer deutlich sichtbar
- **Betrag (Check 4):** `p2` muss ≥ 20 % von `(max_price − min_price)` Abstand zu eq_p **und** zu max_price halten
- Root-Search-Obergrenze auf 2000 erhöht (für große Sättigungsmengen)

### 2.4  Vertiefung Check 1 – y-Achse

`max_y = nice_axis_max(max_price * 1.08)` statt aus `eq_p`.
Layout hat explizit `range: [0, max_x]` und `range: [0, max_y]`, damit Plotly nicht auto-skaliert.
Zusätzlich: `eq_p < max_price * 0.2` → Reject (Gleichgewicht zu tief).

---

## 3  Refactoring: Check 2 (rechnerisch LQE)

`kennzahlen_rechnerisch_linearquadratischexp.py` wurde von ~220 auf ~65 Zeilen reduziert.
Lokale Duplikate (`_build_supply`, `_build_demand`, `_find_first_positive_root`, `_fmt`, `_sign_term`) entfernt – nutzt jetzt `_sample_market_params` und `_kennzahlen_items_allgemein` aus `shared.py`.

---

## 4  Diagnose-Tool

Während der Optimierung wurde `_measure_rejections.py` (Wurzelverzeichnis) erstellt.
Gibt pro Generator Akzeptanzrate, Reject-Gründe und Laufzeit aus.
**Ergebnisse nach Optimierung:** Grundlagen ~74 %, Vertiefung ~79 % Akzeptanzrate.

---

## 5  Offene Punkte / mögliche nächste Schritte

- **`uniform_sig` Performance:** Baut bei jedem Aufruf ein vollständiges Kandidaten-Grid auf (~218 ms / 1000 Calls). Könnte durch Caching oder direkte Generierung beschleunigt werden.
- **Weitere Redundanz-Reduktion:** `shared_formatting`- und `shared_calculus`-Module wurden in der Analyse empfohlen, aber noch nicht umgesetzt.
- **Koeffizienten-Qualität:** Stichprobenartig prüfen, ob Koeffizienten immer ≤ 2–3 signifikante Stellen haben (Schülerfreundlichkeit).

---

## 6  Batch-Verifizierung

Alle 8 Marktgleichgewicht-Jobs (3 Grundlagen + 5 Vertiefung) erzeugen je 20 Aufgaben fehlerfrei.
CLI-Filter: `python aufgaben/run.py marktgleichgewicht_grundlagen` (Unterstriche, keine Bindestriche).
