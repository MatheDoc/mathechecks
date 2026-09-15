# Kontextprüfung der Testfragen

Erstsichtung: 15.09.2026. Gesichtet wurden die Fragetexte aller 140 Test-JSONs mit insgesamt 1.400 Fragen. Auffällige Stellen wurden zusätzlich anhand ihrer Antwortoptionen geprüft.

## Umsetzung

Die klaren Kontextlücken sind inzwischen mit kurzen Ergänzungen behoben. Die beiden komplexen Baumdiagrammtests enthalten jeweils zehn neue, unabhängige Mini-Fragen. Suchraster, konkrete Ereigniszuordnungen, benötigte Ansätze und Testrichtungen wurden ergänzt; die Faustregel-Fragen prüfen jetzt direkt die Lage zur Ein-Sigma-Umgebung.

Nach Rücksprache bleiben typische Notation und naheliegende Standardannahmen vorausgesetzt. Rein formale Präzisierungen wurden nicht flächendeckend umgesetzt. Das Format bleibt bei zehn kurzen, zügig beantwortbaren Fragen je Test. Die folgenden Abschnitte dokumentieren die Befunde des ursprünglichen Stands, nicht eine aktuelle Liste offener Mängel.

## Maßstab

- Jede Frage muss ohne andere Fragen, Skript, Trainingsaufgaben oder Kenntnis ihrer Ablage verständlich sein.
- Typische mathematische Notation und Fachbegriffe dürfen vorausgesetzt werden. Insbesondere sind RZ, ZE und m kein Beanstandungsgrund.
- Bekanntes Fachwissen ist von fehlenden Aufgabendaten zu unterscheiden: Ein Symbol muss nicht erklärt werden; Funktionsgrad, konkrete Ereigniszuordnung, Verteilung, Einheiten und benötigte Fallannahmen müssen aber feststehen.
- Ein vollständig beschriebener kleiner Sachkontext ist zulässig. Die Wiedererkennung einer konkreten Trainingsaufgabe darf nicht nötig sein.
- Fragenummern beziehen sich auf die Reihenfolge im JSON, nicht auf einen gemischten Testdurchlauf.

Dies ist eine redaktionelle Kontextprüfung, keine vollständige rechnerische Validierung sämtlicher Antworten und Fehlererklärungen. Die Befunde sind nach Fehlermustern gebündelt; eine nicht aufgeführte Frage ist damit nicht formal als fehlerfrei zertifiziert.

## 1. Die beiden Kontexttests neu ausrichten

### Komplexes Baumdiagramm I

[stochastik/mehrstufige-zufallsexperimente/stochastik__mehrstufige-zufallsexperimente__05.json](stochastik/mehrstufige-zufallsexperimente/stochastik__mehrstufige-zufallsexperimente__05.json)

- Frage 3: Die Antwort 0,7 setzt voraus, dass Einsteiger-, Mittelklasse- und Premiumgeräte die gesamte Grundgesamtheit überschneidungsfrei aufteilen. Das steht nicht in der Frage.
- Frage 6: EW, MW und PW sind konkrete Kategorien des Laptopmodells, keine allgemein festgelegte Notation. Es fehlt auch die Angabe, dass diese drei Pfade das Windows-Ereignis vollständig zerlegen.
- Fragen 8 und 9: „das andere Betriebssystem“ setzt eine nicht angegebene Aufteilung in genau zwei Betriebssystemkategorien voraus. „nicht mit Windows“ wäre dagegen eindeutig.
- Insgesamt: Die Zahlen und Kategorien bilden eine zusammenhängende Laptopaufgabe nach. Ein Teil der Fragen ist isoliert lösbar, aber die Sammlung trifft damit nicht die gewünschte kontextübergreifende Ausrichtung.

### Komplexes Baumdiagramm II

[stochastik/mehrstufige-zufallsexperimente/stochastik__mehrstufige-zufallsexperimente__06.json](stochastik/mehrstufige-zufallsexperimente/stochastik__mehrstufige-zufallsexperimente__06.json)

- Frage 3: Für den gesamten Starter-Anteil muss feststehen, dass die beiden genannten Pfade alle Starter-Fälle erfassen.
- Frage 4: „ohne App“, „Starter“ und „Pro“ müssen eine vollständige, überschneidungsfreie Einteilung bilden. Diese Modellannahme fehlt.
- Frage 5: Aus vier bekannten Pfaden folgt die fehlende Wahrscheinlichkeit nur, wenn genau ein weiterer Endpfad existiert und damit alle Endpfade erfasst sind.
- Fragen 8 und 9: „Anteil der Nutzung“ lässt die Bezugsgruppe offen: alle Befragten oder nur App-Nutzende? Die vorgesehenen Antworten beziehen sich auf alle Befragten.
- Insgesamt: Auch hier sollte nicht der bekannte App-Kontext abgefragt werden, sondern das Ergänzen und Auswerten komplexerer Baumstrukturen.

**Empfohlene Neuausrichtung beider Sammlungen:** unabhängige Mini-Fragen zu mehr als zwei Ästen, vollständig benannten Pfadgruppen, unterschiedlich tiefen Teilbäumen, indirekter Bestimmung von Astwahrscheinlichkeiten, korrekten Bezugsgruppen und dem Erkennen unzureichender Angaben. Jede Frage enthält ihre eigene relevante Baumstruktur in Worten. Einfache Zahlen erhalten den schnellen, atomaren Charakter. Nicht bloß Laptop- und App-Bezeichnungen durch A, B und C ersetzen.

## 2. Gesicherte Informationslücken

### Funktionsansatz fehlt

[analysis/ertragsgesetzliche-kostenfunktionen/analysis__ertragsgesetzliche-kostenfunktionen__06.json](analysis/ertragsgesetzliche-kostenfunktionen/analysis__ertragsgesetzliche-kostenfunktionen__06.json), Fragen **3, 4, 9, 10**.

Die Lösungen verwenden die Koeffizienten des Ansatzes K(x) = ax³ + bx² + cx + d, der jeweils nicht genannt wird. Beispielsweise ergibt K(2) = 20 erst mit diesem Ansatz die erwartete Gleichung 8a + 4b + 2c + d = 20. Den Ansatz in jede betroffene Frage aufnehmen; bekannte Koeffizientennotation allein legt den Funktionsgrad nicht fest.

### Größe des LGS fehlt

[lineare-algebra/lineare-gleichungssysteme/lineare-algebra__lineare-gleichungssysteme__03.json](lineare-algebra/lineare-gleichungssysteme/lineare-algebra__lineare-gleichungssysteme__03.json), Fragen **2, 3, 4**.

Die Antworten setzen ein 4×4-LGS voraus. Ohne diese Angabe sind weder die Anzahl der zu eliminierenden Einträge noch die Dimension des verbleibenden Teilsystems bestimmt. Jeweils „Bei einem 4×4-LGS …“ ergänzen.

### Ausgangsschema oder Ziel der Reduktion fehlt

- [lineare-algebra/matrizenrechnung/lineare-algebra__matrizenrechnung__03.json](lineare-algebra/matrizenrechnung/lineare-algebra__matrizenrechnung__03.json), Frage **6**: Aus dem Endschema (E₂ | B) allein folgt nicht B = A⁻¹. Das Ausgangsschema (A | E₂) muss genannt werden; bei (A | C) ergibt sich stattdessen B = A⁻¹C.
- [lineare-algebra/matrizenrechnung/lineare-algebra__matrizenrechnung__04.json](lineare-algebra/matrizenrechnung/lineare-algebra__matrizenrechnung__04.json), Frage **2**: „Welche Matrix steht zu Beginn rechts neben A?“ nennt weder die Inversenberechnung noch die Größe von A. Beides ergänzen.

### Binomialverteilung wird nur durch die Ablage vorausgesetzt

- [stochastik/binomialverteilung/stochastik__binomialverteilung__12.json](stochastik/binomialverteilung/stochastik__binomialverteilung__12.json), Fragen **1–10**.
- [stochastik/binomialverteilung/stochastik__binomialverteilung__13.json](stochastik/binomialverteilung/stochastik__binomialverteilung__13.json), Fragen **1–8 und 10**.
- [stochastik/binomialverteilung/stochastik__binomialverteilung__14.json](stochastik/binomialverteilung/stochastik__binomialverteilung__14.json), Fragen **1–10**.
- [stochastik/binomialverteilung/stochastik__binomialverteilung__15.json](stochastik/binomialverteilung/stochastik__binomialverteilung__15.json), Fragen **2–10**.

Typische Symbole wie n, p, μ und σ dürfen bekannt sein, legen aber keine Verteilungsfamilie fest. Beispielsweise folgt aus n = 4 und μ = 2 nicht allgemein σ = 1. „Für eine Binomialverteilung …“ beziehungsweise X ~ B(n; p) genügt. Die ausgenommenen Fragen nennen bereits die umzustellende Gleichung und benötigen dafür keine zusätzliche Modellannahme.

### Ganzzahligkeit von X fehlt

[stochastik/binomialverteilung/stochastik__binomialverteilung__03.json](stochastik/binomialverteilung/stochastik__binomialverteilung__03.json), Fragen **1, 2, 3, 4, 7, 8, 9**.

Umformungen wie P(X < 6) = P(X ≤ 5) gelten nicht für beliebige Zufallsgrößen. „Für eine ganzzahlige Zufallsgröße X …“ reicht aus; eine Binomialverteilung ist hierfür nicht erforderlich. Frage 10 macht diese Voraussetzung bereits ausdrücklich.

### Suchraster oder Bedingung fehlt

[stochastik/binomialverteilung/stochastik__binomialverteilung__09.json](stochastik/binomialverteilung/stochastik__binomialverteilung__09.json), Fragen **2, 5, 7**.

Zwei geprüfte p-Werte bestimmen nicht das tatsächliche Minimum oder Maximum auf einem kontinuierlichen Parameterbereich. In Frage 2 kann die Grenze zwischen 0,40 und 0,41 liegen; in Frage 5 zwischen 0,30 und 0,31. Bei Frage 7 besitzt die strikte Ungleichung im üblichen kontinuierlichen Binomialmodell überhaupt kein kleinstes erfüllendes p. Das Suchraster ausdrücklich vorgeben oder nur nach dem passenden der vorgegebenen Prüfwerte fragen. Frage 9 nennt Hundertstelschritte bereits.

- [stochastik/binomialverteilung/stochastik__binomialverteilung__08.json](stochastik/binomialverteilung/stochastik__binomialverteilung__08.json), Frage **9**: Dass n = 30 scheitert und n = 31 passt, beweist ohne genannte Bedingung beziehungsweise Monotonie nicht, dass 31 das kleinste passende n ist.
- [stochastik/binomialverteilung/stochastik__binomialverteilung__10.json](stochastik/binomialverteilung/stochastik__binomialverteilung__10.json), Frage **10**: Analog beweisen die zwei Prüfwerte ohne Bedingung nicht, dass 9 das größte passende k ist. Die tatsächlich untersuchte Ungleichung nennen.

### Konkrete Ereignisse wurden nur in anderen Fragen definiert

[stochastik/zufallsexperimente-und-wahrscheinlichkeiten/stochastik__zufallsexperimente-und-wahrscheinlichkeiten__02.json](stochastik/zufallsexperimente-und-wahrscheinlichkeiten/stochastik__zufallsexperimente-und-wahrscheinlichkeiten__02.json), Fragen **5 und 6**.

Die Zuordnung A = regelmäßiges Zähneputzen und B = gesunde Zähne fehlt. Allgemeine Ereignisnotation ist bekannt, aber diese konkrete Zuordnung nicht. Beide Ereignisse jeweils erneut nennen.

### Koeffizienten der Erwartungswertgleichung fehlen

[stochastik/zufallsgroessen/stochastik__zufallsgroessen__05.json](stochastik/zufallsgroessen/stochastik__zufallsgroessen__05.json), Frage **5**.

Aus E(X) = 0,29 und bekannten Beiträgen von −1,06 folgt lediglich, dass die unbekannten Beiträge zusammen 1,35 ergeben. Für die erwartete Gleichung −x + 4y = 1,35 fehlt die Angabe, dass x und y zu den Werten −1 und 4 gehören. Diese steht nur in Frage 3 und muss wiederholt werden.

### Testrichtung und Bedeutung der Grenze fehlen

- [stochastik/hypothesentests/stochastik__hypothesentests__05.json](stochastik/hypothesentests/stochastik__hypothesentests__05.json), Frage **8**.
- [stochastik/hypothesentests/stochastik__hypothesentests__06.json](stochastik/hypothesentests/stochastik__hypothesentests__06.json), Frage **8**.

„Es wurde k = 27/35 bestimmt“ legt keine Entscheidungsregel fest. Links-/Rechtsseitigkeit und die Bedeutung von k als größter/kleinster noch zur Ablehnung führender Trefferzahl nennen. Das ist keine Frage der Symbolkenntnis.

### Maßeinheiten fehlen

- [analysis/differentialrechnung-ganzrationaler-funktionen/analysis__differentialrechnung-ganzrationaler-funktionen__01.json](analysis/differentialrechnung-ganzrationaler-funktionen/analysis__differentialrechnung-ganzrationaler-funktionen__01.json), Frage **8**: Die Lösung ist in m/s, aber t wird nicht als Zeit in Sekunden festgelegt.
- [analysis/lineare-funktionen/analysis__lineare-funktionen__09.json](analysis/lineare-funktionen/analysis__lineare-funktionen__09.json), besonders Frage **3**, außerdem **2 und 4**: Die Antworten ergänzen Stunden/Liter beziehungsweise Euro, die im Fragetext fehlen. Die Steigung eines Wasservorratsmodells allein liefert keine Einheit „Liter pro Stunde“. Einheiten kurz angeben. Bei Frage 8 sind Liter und Stunden bereits aus dem Auftrag ersichtlich.

### Zeitmodell statt Mengenmodell nicht festgelegt

- [analysis/produktlebenszyklus/analysis__produktlebenszyklus__04.json](analysis/produktlebenszyklus/analysis__produktlebenszyklus__04.json), besonders Frage **9**: Aus u(6) = 14 folgt ohne Definition nicht „jährlicher Umsatz nach 6 Jahren“.
- [analysis/produktlebenszyklus/analysis__produktlebenszyklus__05.json](analysis/produktlebenszyklus/analysis__produktlebenszyklus__05.json), Fragen **2–7**: Die Antworten setzen jährliche Erlös-, Kosten- und Gewinnraten in Abhängigkeit der Zeit voraus. E, K und G sind bekannte Symbole, aber im üblichen Mengenmodell haben sie eine andere Bedeutung; auch kumulierte Zeitfunktionen sind möglich. Das Zeit-/Ratenmodell in jeder betroffenen Frage kurz nennen.

## 3. Aufträge und Bezugnahmen präzisieren

Diese Stellen sind teilweise aus den Antwortoptionen erschließbar. Sie sollten trotzdem überarbeitet werden, damit bereits der Auftrag selbst klar ist.

- **„In diesem Check“:** [stochastik/binomialverteilung/stochastik__binomialverteilung__08.json](stochastik/binomialverteilung/stochastik__binomialverteilung__08.json), [stochastik/binomialverteilung/stochastik__binomialverteilung__09.json](stochastik/binomialverteilung/stochastik__binomialverteilung__09.json) und [stochastik/binomialverteilung/stochastik__binomialverteilung__10.json](stochastik/binomialverteilung/stochastik__binomialverteilung__10.json), jeweils Frage **1**. Statt der Check-Zugehörigkeit die konkrete Parametersuche im Binomialmodell beschreiben. Jeweils Frage **8** außerdem um die festgehaltenen Parameter ergänzen.
- **Nicht bezeichnetes Ziel im Baum:** [stochastik/bedingte-wahrscheinlichkeiten/stochastik__bedingte-wahrscheinlichkeiten__02.json](stochastik/bedingte-wahrscheinlichkeiten/stochastik__bedingte-wahrscheinlichkeiten__02.json), Fragen **6 und 7**. Den gesuchten Ast beziehungsweise Endpfad ausdrücklich nennen. Die Optionen verraten aktuell erst, welcher gemeint ist.
- **Nicht benannte Operation:** [lineare-algebra/matrizenrechnung/lineare-algebra__matrizenrechnung__07.json](lineare-algebra/matrizenrechnung/lineare-algebra__matrizenrechnung__07.json), Fragen **6 und 10**. „Welche Regel gilt für ein Produkt/eine Summe?“ um „beim Transponieren von Matrizen“ ergänzen.
- **Nicht beschriebenes Eliminationsschema:** [lineare-algebra/matrizenrechnung/lineare-algebra__matrizenrechnung__04.json](lineare-algebra/matrizenrechnung/lineare-algebra__matrizenrechnung__04.json), Frage **5**. Dimension und Ziel der Vorwärtselimination nennen; „linke untere Ecke“ ist für die angebotenen vollständigen 3×3-Schemata unpräzise.
- **Nicht benanntes Abschöpfungsmodell:** [analysis/marktgleichgewicht-vertiefung/analysis__marktgleichgewicht-vertiefung__04.json](analysis/marktgleichgewicht-vertiefung/analysis__marktgleichgewicht-vertiefung__04.json), besonders Fragen **3–6**, und [analysis/marktgleichgewicht-vertiefung/analysis__marktgleichgewicht-vertiefung__05.json](analysis/marktgleichgewicht-vertiefung/analysis__marktgleichgewicht-vertiefung__05.json), Fragen **1, 2 und 10**. Das Modell kurz beschreiben: Für x₂ Einheiten wird statt p_G der höhere Preis p₂ verlangt; gesucht ist der zusätzliche Erlös. In Frage 6 des ersten Tests fehlt sogar die ausdrückliche Zielgröße, im zweiten Test Frage 10 die Ausgangszielfunktion zum „Einsetzen“.
- **„Nach der Faustregel“:** [stochastik/zufallsgroessen/stochastik__zufallsgroessen__03.json](stochastik/zufallsgroessen/stochastik__zufallsgroessen__03.json), Fragen **8 und 9**. Das gemeinte Vergleichsintervall E(X) ± σ(X) nennen oder direkt nach „innerhalb/außerhalb“ fragen. „Gewöhnlich“ ist ohne definierte Regel kein eindeutiges mathematisches Prädikat.
- **Trefferzahl nicht genannt:** [stochastik/binomialverteilung/stochastik__binomialverteilung__02.json](stochastik/binomialverteilung/stochastik__binomialverteilung__02.json), Frage **5**. X als Trefferzahl nennen oder allgemein nach der Wahrscheinlichkeit für den Wert 3 fragen; „im Sachzusammenhang“ verweist derzeit auf keinen beschriebenen Sachverhalt.
- **Testgrenze ohne vollständigen Prüfauftrag:** [stochastik/hypothesentests/stochastik__hypothesentests__03.json](stochastik/hypothesentests/stochastik__hypothesentests__03.json) und [stochastik/hypothesentests/stochastik__hypothesentests__04.json](stochastik/hypothesentests/stochastik__hypothesentests__04.json), jeweils Fragen **7 und 9**, sowie [stochastik/hypothesentests/stochastik__hypothesentests__05.json](stochastik/hypothesentests/stochastik__hypothesentests__05.json) und [stochastik/hypothesentests/stochastik__hypothesentests__06.json](stochastik/hypothesentests/stochastik__hypothesentests__06.json), jeweils Frage **7**. Testseite, Wahrscheinlichkeiten unter H₀ und gesuchte größte/kleinste zulässige Grenze ausdrücklich nennen.

## 4. Nebenbefunde in den Kontexttests

Bei der Neufassung die Distraktoren samt Fehlererklärungen erneut prüfen:

- Baumdiagramm-Test 05, Frage 5: Der Distraktor 0,14 passt nicht zur Erklärung „durch 0,5 dividiert“. 0,7 : 0,5 ergibt 1,4.
- Baumdiagramm-Test 06, Frage 4: „Nur Starter-Anteil von 1 abgezogen“ ergibt 0,4, nicht den zugeordneten Distraktor 0,84.
- Baumdiagramm-Test 06, Frage 10: „Pro-Anteil statt Pfadwahrscheinlichkeit verwendet“ ergäbe beim Pro-Anteil 0,16 die Anzahl 320, nicht 416. Zudem sollte eine Fehlererklärung keine nur aus anderen Fragen bekannte Zahl voraussetzen.

## Konsequenz

Keine flächendeckende Erklärung üblicher Notation und kein pauschales Entfernen von Sachkontexten. Zuerst die beiden komplexen Baumdiagrammtests inhaltlich neu ausrichten, anschließend die gesicherten Lücken mit kleinen Ergänzungen schließen. Die Präzisierungen separat bearbeiten. Für zukünftige Fragen gilt: Aufgabe und Antwortoptionen gedanklich aus der Datei herauslösen und prüfen, ob weiterhin dieselbe eindeutige Aufgabe vorliegt.