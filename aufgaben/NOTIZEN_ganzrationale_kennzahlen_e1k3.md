# Diskussionsstand - Kennzahlen graphisch E1K3

Zusammenfassung der Optimierungsrunde (Stand April 2026).

---

## 1 Ausgangslage und Probleme

| Problem | Beobachtung |
|---|---|
| Zu geringe x-Variation | Gewinnmaximum lag haeufig in aehnlichen Bereichen (z. B. um ~8). |
| Zu hohe y-Skalierung | Obere y-Achse lief teils deutlich zu hoch; Ziel war harte Obergrenze. |
| Negative y-Bereiche unguenstig | Bei manchen Varianten wirkte der negative Bereich abgeschnitten/angehoben. |
| Wirtschaftliche Form nicht hart genug erzwungen | Fuer K(x) sollten Bedingungen explizit im E1K3-Sampler geprueft werden. |

---

## 2 Umgesetzte Loesung (Generator)

Datei:
`aufgaben/generators/analysis/ganzrationale_oekonomische_funktionen/kennzahlen_graphisch_e1k3.py`

### 2.1 Sampling/Skalierung

- Umstellung auf potenzbewusste Skalierung nach dem Prinzip:
  - Koeffizient ~ basis * Zufall * y_scale / x_scale^i
- Separate Skalierungsfaktoren fuer x und y.
- Zusaetzliche Koeffizienten-Wobble-Faktoren fuer mehr Formvielfalt.

Ergebnis: Deutlich breitere x-Streuung bei weiterhin plausiblen Kurvenformen.

### 2.2 Harte oekonomische Bedingungen fuer K(x)

Fuer `K(x) = k3*x^3 + k2*x^2 + k1*x + k0` gilt jetzt explizit:

- `k0 > 0`
- `k3 > 0`
- `k2 < 0`
- `k2^2 <= 3*k3*k1`

Damit ist die gewuenschte monotone Kostenstruktur im relevanten Bereich hart gefiltert.

### 2.3 y-Achse und sichtbarer Bereich

- y-Layout wird so gesetzt, dass:
  - negative Bereiche sichtbar bleiben,
  - aber die Obergrenze strikt begrenzt ist.
- Harte Regel: `y_max <= 1000`.

---

## 3 Zusaetzliche "nice chart"-Regeln (eingebaut)

### 3.1 Abstand Gewinn-Grenze zu Kapazitaet

- Zweite Gewinn-Nullstelle (`x_break_even_high`) soll nicht zu nah an der Kapazitaet liegen.
- Kapazitaet wird aus der zweiten Nullstelle abgeleitet:
  - `capacity = round(x_break_even_high * U(1.20, 1.30))`
- Zusaetzliche Band-Regel:
  - `x_break_even_high / capacity in [0.75, 0.90]`

Interpretation: Gewinnende typischerweise bei ca. 75-90 % der Kapazitaet.

### 3.2 Mindesthoehe des Gewinnmaximums

- Es gilt jetzt:
  - `G_max >= 0.10 * E(capacity)`

Interpretation: Gewinnmaximum ist visuell nicht "zu flach" im Verhaeltnis zum Umsatz bei Kapazitaet.

---

## 4 Verifikation (zuletzt gemessen)

Ziel-JSON:
`aufgaben/exports/json/analysis/ganzrationale-oekonomische-funktionen/kennzahlen-graphisch-e1k3.json`

Letzte gemeldete Kennzahlen (20 Aufgaben):

- `x2/capacity` (zweite Gewinn-Nullstelle / Kapazitaet):
  - min `0.771`, median `0.813`, max `0.832`
- `G_max / E(capacity)`:
  - min `0.134`, median `0.179`, max `0.270`
- y-Obergrenze:
  - alle Aufgaben `<= 1000`

Alle drei Regelbloecke wurden im letzten Check als erfuellt gemeldet.

---

## 5 Reproduzierbare Kommandos

E1K3 gezielt neu erzeugen:

```bash
python aufgaben/run.py e1k3
```

Voll-Batch (alle JSONs):

```bash
python -m aufgaben.cli batch --config aufgaben/project_config.json
```

---

## 6 Offene optionale Feintuning-Punkte

- Ratio-Band enger stellen (z. B. 0.78-0.88), falls noch einheitlicheres Bild gewuenscht ist.
- Kapazitaetsfaktor enger stellen (z. B. 1.22-1.28).
- Ggf. analoge Regeln spaeter auf E2K3/K3 uebertragen.
