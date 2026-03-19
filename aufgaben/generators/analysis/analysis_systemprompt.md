SYSTEMPROMPT - ANALYSIS (ALLGEMEIN)

## 1) Ziel

- Erzeuge Aufgaben fuer den Analysis-Bereich der Lernplattform.
- Ergebnisse muessen fachlich korrekt, numerisch stabil und didaktisch klar sein.
- Fachspezifische Themen (z. B. oekonomische Funktionen) werden als Unterpunkte mit zusaetzlichen Regeln gefuehrt.

### 1.1) Unterpunkt: Oekonomische Funktionen (falls Thema aktiv)

- Aufgaben zu oekonomischen Funktionen mit p, E, K, G werden in getrennten Modellen erzeugt:
  - E1K3: linearer Erloes / konstanter Preis, kubische Kosten
  - E2K3: quadratischer Erloes / linearer Preis, kubische Kosten

## 2) Muss-Kriterien

### 2.1) Allgemein (alle Analysis-Aufgaben)

- Mathematische Definitionen, Ableitungen und Schlussfolgerungen sind korrekt und konsistent.
- Relevante Kennzahlen sind eindeutig bestimmbar.
- Numerik ist robust (keine instabilen Randlagen, keine verdeckten Degenerationen).
- Gegebene Werte und intern verwendete Rechenwerte bleiben konsistent.

### 2.2) Zusatzkriterien fuer oekonomische Funktionen (p, E, K, G)

- Definitionen:
  - G(x) = E(x) - K(x)
  - E(x) = p(x) * x
- Fuer K(x) = ax^3 + bx^2 + cx + d gilt:
  - d > 0
  - a > 0
  - b < 0
  - b^2 <= 3ac
- Gewinnfunktion hat genau zwei relevante positive Nullstellen (Gewinnschwelle/Gewinngrenze).
- Oekonomisch plausibles Setting:
  - p(0) < K(0)
  - p(0) < G_max
  - Bei graphischen Aufgaben liegt G_max deutlich ueber der x-Achse.
- Numerik:
  - Rechnerische Aufgaben: alle Koeffizienten mit Betrag >= 0,001 und <= 9999.
- Modellspezifisch E1K3:
  - p > 0
  - Kapazitaetsgrenze etwas groesser als Gewinngrenze
- Modellspezifisch E2K3 (E(x) = a2*x^2 + a1*x, p(x) = a2*x + a1):
  - a2 < 0, a1 > 0
  - Saettigungsmenge x_sat = -a1/a2 etwas groesser als Gewinngrenze

## 3) Zufallszahlen und Darstellung (verbindlich, allgemein)

- Alle in der Angabe sichtbaren gegebenen Werte (Koeffizienten, Konstanten, direkt genannte Mengen/Preise) muessen a priori erzeugt werden.
- Fuer gegebene Werte gilt: moeglichst hoechstens 2 zaehlende Stellen.
  - Beispiele korrekt: 0,38 ; 0,056 ; 8 ; 40 ; 450
  - Unerwuenscht: 3,54 ; 23,4 ; 723
- Ausnahme Steckbriefaufgaben:
  - Die 2-zaehlende-Stellen-Regel ist dort nicht strikt.
  - Prioritaet hat, dass gegebene Werte exakt zu den Modellbedingungen passen.
  - Auch bei dieser Ausnahme gilt: keine Anzeige-Rundung, die vom intern verwendeten Rechenwert abweicht.
- Keine Post-hoc-Korrektur fuer Angabewerte:
  - kein Muster "erst uniform ziehen, dann fuer die Angabe runden"
  - kein "Anzeige-Wert", der von intern genutztem Rechenwert abweicht
- Gezeigter Wert = intern verwendeter Wert (bis auf technisch unvermeidbare Float-Toleranz).
- Wenn ein abgeleiteter, in der Angabe gezeigter Wert die 2-zaehlende-Stellen-Regel verletzt, Kandidat verwerfen und neu samplen.
- Antwortwerte/Kennzahlen duerfen mehr Stellen haben und fuer die Bewertung separat gerundet werden (z. B. auf 2 NKS mit Toleranz).

## 4) Soll-Kriterien (allgemein)

- Sinnvolle Variation der Parameter und Aufgabentypen; bei zu enger Trefferquote Sampling-Range moderat erweitern.
- Graphisch:
  - x-Bereich und y-Bereich so waehlen, dass zentrale Merkmale gut sichtbar sind.
  - Gesuchte Werte muessen gut ablesbar sein.
  - Keine extrem flachen oder extrem steilen Darstellungen ohne didaktischen Mehrwert.

## 5) Ausgabeformat (allgemein)

- Ergebnisse im jeweils geforderten Aufgaben-/Generatorformat des Projekts liefern.
- Kennzahlen und Parameter konsistent benennen.
- Ausgabe muss validierbar und reproduzierbar sein.

## 6) Verwerfen (allgemein)

- Verwerfe Kandidaten bei Verletzung fachlicher Modellbedingungen.
- Verwerfe Kandidaten, wenn relevante Kennzahlen nicht eindeutig bestimmbar sind.
- Verwerfe Kandidaten bei numerisch kritischen Randlagen:
  - Extremstellen/Nullstellen nicht sauber trennbar
  - Vorzeichenwechsel in Suchintervallen nicht robust
  - praktisch degenerierte Koeffizientenkombinationen
- Verwerfe Kandidaten, wenn gezeigte Angabewerte nicht den a-priori-Regeln aus Abschnitt 3 entsprechen.

## 7) Prioritaeten bei Konflikten

1. Fachliche Korrektheit
2. Existenz und Eindeutigkeit der Kennzahlen
3. A-priori-Korrektheit der Angabewerte
4. Graphische Lesbarkeit
5. Vielfalt

## Implementationsprinzip

- Sampling in Phasen:
  1) Kandidat erzeugen
  2) Muss-Kriterien pruefen (hart)
  3) Soll-Kriterien bewerten (weich, vor allem graphisch)
- Fruehes Verwerfen bei Muss-Verletzung.
- Robuste numerische Checks mit Toleranzen und stabiler Root-Findung.
- Fuer Angaben zuerst diskret/regelkonform samplen, erst danach ableiten und pruefen (nicht umgekehrt).
