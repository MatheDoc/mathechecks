# Konventionen und Glossar

## LaTeX/MathJax-Konvention
- Syntax:
	- Allgemein: Inline `$...$`, Display `$$...$$`, Komma mit geschweiften Klammern `{,}`, z.B. `$0{,}5$`
	- JSON-Dateien: Escapen, zum Beispiel inline in JSON-String: `"Die Formel ist $ p=\\frac{k}{n} $"`
	- bei Replacement-Strings keine geschweiften Klammern für Kommas verwenden, keine $-Zeichen, richtig ist zB. `"{1:NUMERICAL:=0,1461:0,0001}"`
- Reiner Text:
	keine geschweiften Klammern für Kommas verwenden, z.B. `0,5` statt `0{,}5`.
- Terme: Koeffizient 1 weglassen (`t` statt `1t`), Klammern nur um mehrgliedrige Faktoren (`1{,}5te^{-0{,}1t}`, aber `(t+2)e^{-t}`).



## Glossar

- **Benutzer:** Authentifizierte Identität aus dem Auth-System; besitzt persönliche Sessions und Zustände.
- **Profil:** Anwendungsseitige Ergänzung zur Auth-Identität, z. B. Anzeigename oder interne Rolleninformation.
- **Session / Core-Session:** Zeitlich begrenzter Kernplan eines Benutzers mit Lernbereichen, aktiven Checks und Planungsparametern wie Zieltermin und Freigabelimits; im UI derzeit bewusst als **Session** bezeichnet.
- **Planungsziel:** Kanonischer Zieltermin einer Core-Session; Eingaben wie „bis Datum X" oder „in Y Tagen" werden intern darauf abgebildet.
- **Target Source:** Herkunft des Planungsziels: `explicit` bei bewusster Nutzervorgabe, `suggested` bei Systemvorschlag.
- **Planungsrevision:** Version der zukünftigen Session-Planung; steigt bei nachträglichen Änderungen der aktiven Session, ohne vergangene Abschlüsse umzuschreiben.
- **Lernaktivität:** Persistierbare Nutzeraktion im Kontext eines Moduls; kleinste Fortschrittseinheit vor einem echten Feed.
- **Versuch:** Einzelner Abschluss einer Lernaktivität mit Ergebnis, z. B. `can_do` oder `repeat`.
- **Session-Aktivität:** `start`, `training`, `test`, `recall`, `feynman` oder `flashcards` innerhalb einer Session; identifiziert über `activity_key`.
- **Abschluss / Gutschrift:** Einmalige Zählung einer Session-Aktivität („einmal durchgemacht“), egal ob frei oder aus dem Feed gestartet und in welcher Reihenfolge; rein quantitativ, Qualität zeigt die Quote.
- **Kettenreihenfolge:** Didaktisch empfohlene Reihenfolge je Check: `training` → `test` → `recall` → `feynman`; keine Sperre.
- **Empfohlener Abstand (G):** Zeit zwischen zwei Schritten derselben Kette, ab der ein Folgeschritt als reif empfohlen wird.
- **Feed:** Zustandslose Empfehlung der nächsten offenen Session-Aktivität plus fällige Wiederholungen; kein Cursor, keine Sperre, nicht Source of Truth.
- **Tagesziel:** Empfohlene Anzahl Session-Aktivitäten pro Tag; der Header-Badge zeigt „heute noch X“.
- **Retention-Track:** Nutzerweite Wiederholungsschicht jenseits einer endlichen Core-Session; aktuell fachlich vor allem für Flashcards relevant.
- **Retention-Scope:** Nutzerbezogener Wiederholungsumfang eines Lernbereichs oder später eines anderen Aktivitätstyps; kann `active`, `paused` oder `opted_out` sein.
- **Flashcard-Durchgang:** Server-backed Feed-Runde aus stabil ausgewählten Karten eines Lernbereichs; Karteninhalt bleibt im Repo, Durchgang und Bewertungen liegen in Supabase.
- **Thema:** Plattformunabhängige fachliche Einheit aus `_data/themen.yml` (etwa in Lernbereichsgröße), v. a. zur Verschlagwortung von Musterprüfungen und zur Klausursteuerung.
- **Lernbereich:** Auf MatheChecks umgesetztes Thema (gleicher Slug in `_data/lernbereiche.yml`) mit Checks, Skript und Modulen.
- **Check:** Didaktische Einheit im Lernbereich; Primärbezug in Feed/State.
- **Modultyp:** `start`, `warmup`, `kompetenzliste`, `training`, `recall`, `feynman`, `test`, `skript`, `flashcards`.
- **Kompetenz:** Textuelle Lernziel-Formulierung eines Checks in der Kompetenzliste.
- **Aufgabensammlung:** Pool von Trainingsaufgaben zu einem Check (z. B. 20 Varianten).
- **Aufgabe:** Eine konkrete Aufgabe aus der Aufgabensammlung.
- **Frage:** Kleinste bewertete Einheit innerhalb einer Aufgabe.
- **Frage-Score:** Bewertung einer einzelnen prüfbaren Frage; `s = max(0, 1 − (n−1)·p)` über die Versuchszahl `n` mit Straffaktor `p`, oder `0` bei eingeblendeter Lösung.
- **Aufgaben-Score:** Mittelwert der Frage-Scores über alle prüfbaren Fragen einer abgeschlossenen Trainingsaufgabe.
- **Quote:** Nutzerbezogene, recency-gewichtete Kennzahl je Check aus den jüngsten Aufgaben-Scores (`Quote = Σ(d^age·s)/Σ(d^age)`); Lernbereich-, Session- und Gesamt-Quote sind nur Sichtfilter über dieselbe Check-Quote. Read-Model, kein eigener Speicher.
- **XP:** Nutzerweite, nur wachsende Erfahrungspunkte (nicht Flashcards). Training, Test und Warm-Up vergeben sie sofort je richtiger Teilantwort, Recall und Feynman sofort nach jeder KI-Auswertung (`award_xp`); `XP = Gewicht · Score · Faktor` mit Faktor für erstmals / mit Abstand wiederholt / gehäuft wiederholt. Nicht zu verwechseln mit dem Wiederholungslevel (`review_level`) der Quoten.
- **Stufe:** Aus den XP abgeleitete, rein symbolische Rangstufe. Schritt von Stufe `L` zu `L+1` = `xp.level_step · min(L, xp.level_ramp_levels)` XP (Standard: 40, 80, … bis Stufe 10, danach konstant 400).
- **Rolle:** Autorisierungsmerkmal eines Benutzers, z. B. `user` oder `admin`; im MVP möglichst klein halten.
- **Skript-Widget:** Interaktive Slider-gesteuerte Visualisierung im Skript (Include aus `_includes/widgets/`, Logik in `skript-visuals.js`).

**Kurzglossar (1-Zeiler, für Prompts)**
`Benutzer = Auth-Identität; Profil = anwendungsseitige Ergänzung zur Identität; Session/Core-Session = endlicher Kernplan eines Benutzers; Planungsziel = kanonischer Zieltermin der Session; Target Source = explicit|suggested; Planungsrevision = Version der Zukunftsplanung; Lernaktivität = persistierbare Modulaktion; Versuch = einzelner Aktivitätsabschluss mit Ergebnis; Session-Aktivität = start|training|test|recall|feynman|flashcards einer Session; Abschluss = einmalige Gutschrift unabhängig von Reihenfolge und Einstieg; Kettenreihenfolge = training→test→recall→feynman als Empfehlung; G = empfohlener Abstand innerhalb einer Kette; Feed = zustandslose Empfehlung ohne Cursor; Tagesziel = empfohlene Aktivitäten pro Tag; Retention-Track = nutzerweite Wiederholungsschicht; Retention-Scope = active|paused|opted_out je Wiederholungsumfang; Flashcard-Durchgang = serverseitige Kartenrunde; Lernbereich = auf MatheChecks umgesetztes Thema; Thema = plattformunabhängige fachliche Einheit (themen.yml); Modultyp = start|warmup|kompetenzliste|training|recall|feynman|test|skript|flashcards; Check = didaktische Einheit im Lernbereich; Kompetenz = Lernzieltext in der Kompetenzliste; Aufgabensammlung = Sammlung an Aufgaben pro Check; Aufgabe = konkrete Trainingsaufgabe aus der Aufgabensammlung; Frage = kleinste bewertete Einheit; Frage-Score = max(0,1−(n−1)·p) bzw. 0 bei eingeblendeter Lösung; Aufgaben-Score = Mittel der Frage-Scores; Quote = recency-gewichtete Check-Kennzahl als Read-Model, Lernbereich/Session/Gesamt nur Sichtfilter; Rolle = Autorisierungsmerkmal; check_id = stabiler Primärschlüssel im Content und in Fortschrittsdaten.`
