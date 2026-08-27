# Test-Aktivität

Kurze Single-Choice-Fragen pro Check für den schnellen Kompetenz-Abruf.
Ausgabeformate: Test-Modul der Plattform (letztes Glied der Check-Kette) und Moodle-XML.

## Ablage

```
aufgaben/test/<gebiet>/<lernbereich>/<check_id>.json
```

- Eine JSON-Datei pro Check, Dateiname = `check_id` (z. B. `stochastik__binomialverteilung__01.json`).
- Handgepflegte **Quelldateien** – keine Generator-Pipeline, kein Eintrag in `project_config.json`.
- Erzeugte Moodle-XMLs (eine pro Check, Kategorie = Check) landen unter `aufgaben/exports/moodle/`.

## JSON-Schema

```json
{
    "fragen": [
        {
            "frage": "Gegeben sind \\(P_1(0 \\mid 0)\\) und \\(P_2(6 \\mid 3)\\). Wie groß ist \\(m\\)?",
            "antworten": ["\\(0{,}5\\)", "\\(2\\)", "\\(-0{,}5\\)", "\\(6\\)"],
            "fehler": ["\\(\\frac{Δx}{Δy}\\) vertauscht", "Vorzeichenfehler", "nur \\(x_2\\) abgelesen"]
        }
    ]
}
```

- `frage`: Fragetext, LaTeX inline als `\\( … \\)`.
- `antworten`: genau 4 Einträge, **die erste ist die richtige** (Mischen übernimmt Moodle bzw. das Test-Modul). LaTeX ist auch in Antworten erlaubt.
- **Antwortlänge:** möglichst ≤ 60 Zeichen (inkl. LaTeX-Markup), hartes Maximum 90 Zeichen – längere Antworten passen nicht in die fix dimensionierten Antwort-Buttons des Test-Moduls und werden von `aufgaben/tools/test_coverage.py` als ungültig gemeldet.
- `fehler` (optional): beschreibt die Distraktoren, `fehler[i]` gehört zu `antworten[i+1]`. Dient der Dokumentation/Selbstkontrolle beim Schreiben und kann später falsch-spezifisches Feedback speisen. Allgemeine Beschreibungen sind zulässig.


## Didaktische Regeln

- Single-Choice, genau 4 Optionen, genau 1 richtig.
- Keine Hilfsmittel (kein Taschenrechner, keine Formelsammlung); ca. 10–20 Sekunden pro Frage.
- **Atomarität:** Jede Frage prüft möglichst eine kleine Teilkompetenz, kein mehrschrittiges Verfahren.
  - Zu groß: „Aus zwei Punkten die Funktionsgleichung bestimmen."
  - Geeignet: „Welche Formel brauchst du zuerst, um m zu berechnen?" – oder bei bewusst trivialen Zahlen nur die Berechnung von m.
- Keine künstliche Komplexität: keine unnötigen Informationen, komplizierten Zahlen oder Zusatzschritte. Im Mittelpunkt steht der schnelle Abruf, nicht die Rechenlast.
- **Distraktoren:** möglichst konkrete, plausible typische Fehler oder Fehlvorstellungen (z. B. Vorzeichenfehler, vertauschte Formelteile), idealerweise aus der korrekten Lösung durch genau diesen Fehler entstehend. Allgemeine Fehlerantworten sind zulässig.
- Umfang: 10 verschiedene atomare Fragen pro Check; punktuell mehrere Varianten einer Frage, wo Auswendiglernen der Antwort droht.
- **Keine Grafiken:** Test-Fragen kommen ohne Abbildungen aus. Didaktisch oft wünschenswert, aber im Moodle-XML-Export nur mit Workarounds (Base64/Dateianhänge) machbar und im 10–20-s-Format kaum sinnvoll erfassbar.

## Fragenarten

- **Wert bestimmen:** Mini-Rechnung mit bewusst einfachen Zahlen (siehe Beispiel oben).
- **Notation deuten:** z. B. „Was bedeutet \\(P(X \\geq 4)\\)?" → mindestens / höchstens / weniger als / mehr als 4 Treffer.
- **Notation bilden (Umkehrrichtung):** „‚höchstens 4 Treffer' – welche Schreibweise passt?" → \\(P(X \\leq 4)\\) usw.
- **Formel-/Ansatzwahl:** „Welche Formel brauchst du zuerst, um m zu berechnen?"
- **Satzvervollständigung:** „Die notwendige Bedingung für eine Extremstelle lautet: …"
- **Aussage beurteilen:** „Welche Aussage ist richtig?" (oder: „Welche ist falsch?") – vier kurze Aussagen als Optionen.
- **Nächster Schritt:** „Du hast m berechnet. Was ist der nächste Schritt?"
- **Voraussetzung erkennen:** „Welche Bedingung muss erfüllt sein, damit X binomialverteilt ist?"
- **Plausibilität/Schätzen ohne Rechnung:** „Ohne zu rechnen: Welcher Wert kommt für \\(\\mu\\) in Frage?" – prüft Größenordnungsgefühl.
- **Begriff ↔ Definition zuordnen:** „Wie heißt die Stelle, an der der Graph die x-Achse schneidet?"

Die Liste ist offen – zulässig ist jede Frageart, die die Regeln oben erfüllt (atomar, ohne Hilfsmittel, ohne Grafik, in 10–20 s beantwortbar).

## Moodle-Export

Konverter (geplant): `aufgaben/tools/test_to_moodle.py` – liest die JSON-Dateien und schreibt pro Check eine Moodle-XML (Fragetyp `multichoice`, `single=true`, `shuffleanswers=true`, Fragenname `<check_id>-NN`). Vorlage für die XML-Parameter: `beispiel moodle xml.xml` im Repo-Root.
