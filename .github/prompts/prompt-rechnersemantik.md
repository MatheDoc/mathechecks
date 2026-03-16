---
description: Verbindliche Semantik- und Ausgabe-Regeln für den MatheChecks-Rechner
---

# Systemprompt: Rechnersemantik

## 1) Ziel

- Rechnerverhalten wie wissenschaftlicher Taschenrechner mit toleranter Eingabe.
- Eindeutige, konsistente Ausgabe mit deutscher Zahlformatierung.

## 2) Muss-Kriterien

- Eingabe akzeptiert Dezimalkomma und Dezimalpunkt.
- Ausgabe nutzt Dezimalkomma und Tausenderpunkte.
- Wissenschaftliche Schreibweise unterstützen (`1E+3`, `2,5E-4`).
- Konstanten: `pi`/`π`, `e`.
- Kontextsensitive Klammerlogik und implizite Multiplikation.
- Standard-Priorität: Potenz vor Punkt vor Strich.
- Unterstützte Funktionen: `sin`, `cos`, `tan`, `ln`, `log`, `wurzel`, `exp`.
- Erweiterte Funktionen: `lgs(...)`, `binom(...)`, `graph(...)`.
- Gleichungslogik mit genau einem `=` als Gleichung interpretieren.
- Symbolisches Ausmultiplizieren: Ausdruck mit `x` ohne `=` wird expandiert (z. B. `(x-1)(x+2)` → `x^2+x-2`).
- Unklare Eingaben führen zu verständlicher Fehlermeldung.

## 3) Soll-Kriterien

- Eingaben möglichst sinnvoll interpretieren.
- Fehlermeldungen präzise und handlungsleitend formulieren.

## 4) Ausgabeformat

- Ergebnis als eindeutig formatierte numerische oder symbolische Ausgabe.
- Mehrfachlösungen als klare Sammelausgabe.

## 5) Negativliste

- Keine Berechnung bei nicht eindeutiger Interpretation.
- Keine stille Umdeutung nicht interpretierbarer Bezeichner.
- Kein `=` in Popup-Feldern.

## 6) Prioritäten bei Konflikten

1. Eindeutige und fachlich korrekte Interpretation
2. Konsistente Eingabelogik über alle Felder
3. Verständliche, korrekt formatierte Ausgabe
4. Benutzerfreundliche Fehlerrückmeldung
