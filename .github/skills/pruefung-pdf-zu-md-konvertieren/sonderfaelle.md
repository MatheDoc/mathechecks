# Sonderfälle der Musterprüfungen

Ergänzung zum Skill `pruefung-pdf-zu-md-konvertieren`: bekannte Besonderheiten einzelner Ordner und Jahrgänge. Neue Erkenntnisse hier knapp ergänzen.

- **Dateinamen-Suffixe sind ordnerabhängig:**
  - `nw allg gym` (`M_23_c_L_NT_GG.pdf`): `G`/`L` = Grundkurs/Leistungskurs. Eine Datei enthält
    je Aufgabe Aufgabenstellung **und** Modelllösung („Unterlagen für die Lehrkraft“).
  - `nw berufl gym wv lk|gk` (`mathe_wlk_wuv_abitur2025_ht_cas_s.pdf`): `_s`/`_l` =
    Schüler-/Lösungsdatei, `ohimi`/`cas` = Prüfungsteil A/B, `wlk`/`gk` = Kursart.
- **NW Gymnasium, Teil A:** Die Teilaufgaben einer Pflichtaufgabe mischen Themenbereiche (z. B. A1
  a–d Analysis, e–f LinAlg). Lösung: Split in `a1-analysis.md` und `a1-linalg.md`.
- **NW Berufliches Gymnasium WuV:** Teil A hat 4 Pflicht- und 4 Wahlaufgaben (2 aus 4), jede als
  eigene Datei. Die 5 Punkte Darstellungsleistung sind keiner Aufgabe zugeordnet; sie zählen nur
  in `gesamtpunkte` des Index.
- **NW Berufliches Gymnasium WuV 2023 (WLK):** Teil A hat nur 4 Pflichtaufgaben 1.1–1.4 (je 6 Punkte,
  keine Wahl), Teil B 3 Aufgaben mit je 32 Punkten (Summe 125 inkl. 5 Punkte Darstellung). Der
  Erwartungshorizont nutzt feinere Bewertungspositionen (z. B. `2.1.2.1`, `2.1.2.2`; bei Aufgabe 3.4
  das Label `3.4.1`). Diese werden je Teilaufgabe zusammengefasst, Einzelpunkte und AFB stehen in
  Klammern. Zierfotos ohne mathematischen Inhalt (Abbildungen 2–4) werden nicht übernommen.
- **NW Berufliches Gymnasium WuV 2023 (GK):** Dateiname `HT_cas_gtr`/`HT_ohimi` mit `_S`/`_L`. Teil A hat nur eine Pflichtaufgabe 1 (1.1
  Analysis 9, 1.2 Stochastik 6, 1.3 Lineare Algebra 6 Punkte = 21, keine Wahl), Teil B 3 Aufgaben je 28 Punkte (2 Analysis,
  3 Lineare Algebra, 4 Stochastik). `gesamtpunkte` = 110 (105 + 5 Darstellung), Arbeitszeit 225 Min. Aufgabe 1 ist in
  `a1-1`/`a1-2`/`a1-3` gesplittet. Die Lösungsgrafiken zu 1.1.3 und 2.2.2 liegen in Tabellenzeilen und brauchen `--clip`.
  Im Erwartungshorizont fehlt in 1.1.2 ein „= 0“ und in 4.3.1 steht „höchsten“ (unverändert mit Kommentar übernommen).
  Im Projekt-venv fehlte `.venv`; die Tools liefen mit dem System-`python` (pymupdf, pyyaml, jsonschema installiert).
- **NW Berufliches Gymnasium WuV 2022 (GK):** Dateiname `HT_cas_gtr`/`HT_ohimi` mit `_S`/`_L`. Aufbau wie 2023 (Teil A nur Aufgabe 1 mit 1.1–1.3 = 9/6/6 Punkte, Teil B 3 Aufgaben je 28 Punkte, `gesamtpunkte` 110), aber
  Reihenfolge anders: Teil A 1.1 Analysis, 1.2 Lineare Algebra, 1.3 Stochastik; Teil B Aufgabe 2 Analysis, 3 Stochastik, 4 Lineare Algebra.
  Die Vierfeldertafel (Anlage 1) ist als GFM-Tabelle übertragen, das Baumdiagramm in 3.1.1 als verschachtelte Liste (Dezimalpunkte der
  Abbildung als Komma). Nur Anlage 2 (2.1.3) und die Lösungsgrafik dazu sind Bilder (Lösung braucht `--clip`). Die Lösungstabelle zu 1.1.3 enthält
  „Gewinn Gewinn“ (Aufgabenstellung nach Schülerfassung), 2.2.2 schreibt „K‴(2)“ ohne Index $c$.
- **NW Berufliches Gymnasium WuV 2021 (GK):** Dateiname `HT_cas_gtr`/`HT_ohimi` mit `_S`/`_L`. Aufbau wie 2022 (Teil A nur Aufgabe 1 mit 1.1–1.3 = 9/6/6 Punkte, Teil B 3 Aufgaben je 28 Punkte, `gesamtpunkte` 110),
  Teil B aber Aufgabe 2 Analysis, 3 Lineare Algebra, 4 Stochastik. Bilder: Abbildung 1 (1.1), Anlage 1 (1.2.1), Anlage 2 (1.3) und das Lösungsverflechtungsdiagramm
  zu 1.2.1 (braucht `--clip`, Tabellenzeile); das Baumdiagramm im EH zu 1.3.1 ist als verschachtelte Liste übertragen. Schülerfassung 2.1.4 „konstanten Preis“, EH nur „Preis“.
- **Grafiken in Tabellenzeilen** (Erwartungshorizont) oder neben Tabellen/Fließtext/Fotos brauchen
  `figures.py crop … --clip`, da die automatische Bounding-Box sonst die ganze Tabelle bzw. das
  Foto mit erfasst.
- **NW Berufliches Gymnasium WuV 2024 (WLK):** Aufbau wie 2025 (Teil A 1.1–1.8, 4 Pflicht + 2 aus 4 Wahl;
  Teil B 3 Aufgaben je 30 Punkte), aber Reihenfolge Teil B: Aufgabe 2 Analysis, 3 Stochastik, 4 Lineare
  Algebra. Die Aufgabenstellung zu 4.2.4 steht im Schüler-PDF erst auf der letzten Seite. Teil-A-Aufgaben mit nur
  einer Teilaufgabe (1.3.1, 1.6.1, 1.7.1) bekommen trotzdem einen `teilaufgaben`-Eintrag. Das Label
  `3.3.1.` (mit Punkt) in der Aufgabenstellung wird als `3.3.1` geführt. Der Erwartungshorizont zu 4.2.4
  enthält vermutlich einen Tippfehler (0,3629 statt 0,3269 in $M^{24}$), der unverändert mit Kommentar
  übernommen wird. Leontief-Aufgaben (4.1.x) sind mit dem neuen Thema `leontief-modell` getaggt.
  Zierfotos (Schiff, Flasche, Rucksack, Brille) werden nicht übernommen.
- **NW Berufliches Gymnasium WuV 2022 (WLK):** Dateiname mit `oHiMi` statt `ohimi`. Aufbau wie 2023, aber
  Teil A mit gemischten Themenbereichen (1.1/1.2 Analysis, 1.3 Stochastik, 1.4 Lineare Algebra), Teil B
  Aufgabe 3 komplett Lineare Algebra (3.1 mehrstufige Produktion, 3.2 stochastische Matrizen, keine
  Aufteilung nötig). Der Erwartungshorizont fasst in 1.3.1 je zwei Behauptungen zu einer Bewertungsposition
  zusammen. Das Baumdiagramm (4.1.1) und das Übergangsdiagramm (3.2.1) sind Rasterbilder in Tabellenzeilen
  und brauchen manuelle Ausschnitte.
- **NW Berufliches Gymnasium WuV 2021 (WLK):** Aufbau wie 2022 (Teil A 1.1–1.4 je 6 Punkte, Teil B Aufgaben 2–4
  je 32 Punkte), aber Teil A in der Reihenfolge Analysis, Analysis, Lineare Algebra, Stochastik. Die Aussagen
  in 1.4 sind in der Schülerfassung nur als „Aussage 1–3“ nummeriert, die Labels 1.4.1–1.4.3 stammen aus dem
  Erwartungshorizont. Offensichtliche Fehler im Erwartungshorizont (1.1.1 „K(2) = 30“ statt 38, 1.2.1 „notw.
  Bed.: G_a(x) = 0“ statt G_a'(x) = 0) werden unverändert mit Kommentar übernommen. Anlage 1 (3.3.2), Übergangs-
  graph (3.1.1), Lösungsgrafik (3.3.2) und Baumdiagramm (4.3.1) sind Bilder in Tabellenzellen und brauchen
  manuelle `--clip`-Ausschnitte. Die PDFs sind zusätzlich als Seitenbilder im Chat verfügbar, ein Rendern entfällt.
- **NW Berufliches Gymnasium WuV 2024 (GK):** Aufbau wie 2025 (Teil A 1.1–1.7, 3 Pflicht + 2 aus 4 Wahl, je 5 Punkte;
  Teil B 3 Aufgaben je 25 Punkte), aber Reihenfolge Teil B: Aufgabe 2 Analysis, 3 Stochastik, 4 Lineare Algebra.
  Gewertet werden 105 Punkte (`gesamtpunkte`), die Summe der 10 Dateien ist 110. Im Erwartungshorizont zu 4.1.2
  steht „R₁–R₃“ statt „G₁–G₃“ (unverändert mit Kommentar übernommen). Das einfache Baumdiagramm in 1.2.1 ist
  als verschachtelte Liste übertragen. Die Aufgabenstellung 2.1 enthält das Wort „Grenzkostenkostenfunktion“
  (Originalwortlaut). Die Bewertungspositionen (z. B. `2.1.2.1`) sind je Teilaufgabe zusammengefasst.
- **GK-PDFs (`nw berufl gym wv gk`)** liegen teils nur als 1-Byte-Platzhalter vor (Google-Drive-Sync)
  und können nicht gelesen werden; vor der Konvertierung die Dateigröße prüfen.
- **Einfache Baumdiagramme** im Erwartungshorizont (nur Zahlenlabels) dürfen als Text übertragen
  werden. Dieser Fall wird in „Bekannte Lücken“ vermerkt.
