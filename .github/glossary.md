# Konventionen und Glossar

## LaTeX/MathJax-Konvention
- Syntax:
	- Allgemein: Inline `$...$`, Display `$$...$$`, Komma mit geschweiften Klammern `{,}`, z.B. `$0{,}5$`
	- JSON-Dateien: Escapen, zum Beispiel inline in JSON-String: `"Die Formel ist $ p=\\frac{k}{n} $"`
	- bei Replacement-Strings keine geschweiften Klammern für Kommas verwenden, keine $-Zeichen, richtig ist zB. `"{1:NUMERICAL:=0,1461:0,0001}"`
- Reiner Text:
	keine geschweiften Klammern für Kommas verwenden, z.B. `0,5` statt `0{,}5`.



## Glossar

- **Benutzer:** Authentifizierte Identität aus dem Auth-System; besitzt persönliche Sessions und Zustände.
- **Profil:** Anwendungsseitige Ergänzung zur Auth-Identität, z. B. Anzeigename oder interne Rolleninformation.
- **Session / Core-Session:** Zeitlich begrenzter Kernplan eines Benutzers mit Lernbereichen, aktiven Checks und Planungsparametern wie Zieltermin und Freigabelimits; im UI derzeit bewusst als **Session** bezeichnet.
- **Planungsziel:** Kanonischer Zieltermin einer Core-Session; Eingaben wie „bis Datum X" oder „in Y Tagen" werden intern darauf abgebildet.
- **Target Source:** Herkunft des Planungsziels: `explicit` bei bewusster Nutzervorgabe, `suggested` bei Systemvorschlag.
- **Planungsrevision:** Version der zukünftigen Session-Planung; steigt bei nachträglichen Änderungen der aktiven Session, ohne vergangene Abschlüsse umzuschreiben.
- **Freigabe:** Übergang einer Aktivität aus der Zukunftsplanung in den offenen Bereich; der Tagesgrenzwert gilt für neue Freigaben, nicht für alle offenen Aktivitäten.
- **Aktivitätsfenster:** Zeitliche Hülle einer Aktivität mit `available_from`, `due_start` und `due_end` statt nur eines einzelnen Fälligkeitszeitpunkts.
- **Lernaktivität:** Persistierbare Nutzeraktion im Kontext eines Moduls; kleinste Fortschrittseinheit vor einem echten Feed.
- **Versuch:** Einzelner Abschluss einer Lernaktivität mit Ergebnis, z. B. `can_do` oder `repeat`.
- **Check-Status:** Abgeleitete Zustandsprojektion pro Check; nicht identisch mit einzelnen Versuchen.
- **Parallel-Check-Stream:** Check mit aktuell offenem Core-Schritt; begrenzt, wie viele Checks gleichzeitig neu in den Feed gedrückt werden.
- **Freier Aufruf:** Direkte Nutzung eines Moduls ohne aktiven Feed-Kontext; didaktisch sinnvoll, aber ohne Feed-Abschluss.
- **Feed-Kontext:** Aufruf eines Moduls aus einem konkreten Feed-Eintrag; nur dann erscheinen einheitliche Plattform-Aktionen zum Abschließen oder Offenlassen.
- **Aktivitätsscope:** Fachlicher Bezug einer Feed-Aktivität: `check`, `lernbereich` oder später `session`.
- **Feed-Shell:** Gemeinsamer UI-Rahmen um ein Modul im Feed-Kontext; zeigt Kontext, Navigation und einheitliche Feed-Aktionen.
- **Feed-Start:** Einheitlicher Einstieg aus einem Feed-Eintrag in eine Aktivität; nicht modulspezifisch.
- **Feed-Abschluss:** Einheitliche Plattform-Entscheidung `abschließen` oder `offen lassen`; nicht Teil der Modulkarte.
- **Geplant:** Aktivität ist fachlich angelegt, aber noch nicht freigegeben.
- **Verfügbar:** Aktivität darf bereits bearbeitet werden, liegt aber noch vor dem eigentlichen Empfehlungsfenster.
- **Fällig:** Aktivität liegt aktuell im Empfehlungsfenster zwischen `due_start` und `due_end`.
- **Überfällig:** Aktivität ist nach `due_end` weiter offen; sie verschwindet nicht, sondern konkurriert mit neueren sinnvollen Alternativen.
- **Abgeschlossen:** Modul oder Check hat seine Abschlussbedingung erfüllt; bei `recall` und `feynman` zunächst `can_do`.
- **Feed:** Priorisierte Read-Projection offener nächster Lernaktivitäten; nicht Source of Truth der Rohdaten. Er kann sich aus mehreren Quellen speisen, z. B. aktiver Session, Wiederholung oder später weiteren kurzen Formaten.
- **Feed-Eintrag:** Konkrete UI-Aufforderung zu einer Lernaktivität; kann check-bezogen oder lernbereichsbezogen sein.
- **Aktivitätsprojektion:** Materialisierter UI-naher Zustand einer Feed-Aktivität, aktuell `session_check_state` für Check-Pipeline und `session_activity_state` für Flashcards.
- **Retention-Track:** Nutzerweite Wiederholungsschicht jenseits einer endlichen Core-Session; aktuell fachlich vor allem für Flashcards relevant.
- **Retention-Scope:** Nutzerbezogener Wiederholungsumfang eines Lernbereichs oder später eines anderen Aktivitätstyps; kann `active`, `paused` oder `opted_out` sein.
- **Flashcard-Durchgang:** Server-backed Feed-Runde aus stabil ausgewählten Karten eines Lernbereichs; Karteninhalt bleibt im Repo, Durchgang und Bewertungen liegen in Supabase.
- **Lernbereich:** Klar definierter mathematischer Themenbereich.
- **Check:** Didaktische Einheit im Lernbereich; Primärbezug in Feed/State.
- **Modultyp:** `start`, `warmup`, `kompetenzliste`, `training`, `recall`, `feynman`, `skript`, `flashcards`.
- **Kompetenz:** Textuelle Lernziel-Formulierung eines Checks in der Kompetenzliste.
- **Aufgabensammlung:** Pool von Trainingsaufgaben zu einem Check (z. B. 20 Varianten).
- **Aufgabe:** Eine konkrete Aufgabe aus der Aufgabensammlung.
- **Frage:** Kleinste bewertete Einheit innerhalb einer Aufgabe.
- **Rolle:** Autorisierungsmerkmal eines Benutzers, z. B. `user` oder `admin`; im MVP möglichst klein halten.
- **Skript-Widget:** Interaktive Slider-gesteuerte Visualisierung im Skript (Include aus `_includes/widgets/`, Logik in `skript-visuals.js`).

**Kurzglossar (1-Zeiler, für Prompts)**
`Benutzer = Auth-Identität; Profil = anwendungsseitige Ergänzung zur Identität; Session/Core-Session = endlicher Kernplan eines Benutzers; Planungsziel = kanonischer Zieltermin der Session; Target Source = explicit|suggested; Planungsrevision = Version der Zukunftsplanung; Freigabe = neue Aktivität wird offen; Aktivitätsfenster = available_from|due_start|due_end; Lernaktivität = persistierbare Modulaktion; Versuch = einzelner Aktivitätsabschluss mit Ergebnis; Check-Status = abgeleitete Projektion pro Check; Parallel-Check-Stream = aktuell offener Check-Strang; freier Aufruf = Modulnutzung ohne Feed; Feed-Kontext = Modulnutzung aus einem Feed-Eintrag; Aktivitätsscope = check|lernbereich|session; Feed-Shell = gemeinsamer UI-Rahmen im Feed-Kontext; Feed-Start = einheitlicher Einstieg aus dem Feed; Feed-Abschluss = einheitliche Plattformentscheidung; geplant = noch nicht freigegeben; verfügbar = bearbeitbar vor dem Empfehlungsfenster; fällig = im Empfehlungsfenster; überfällig = nach due_end noch offen; abgeschlossen = Abschlussbedingung erfüllt; Feed = priorisierte Read-Projection nächster Aktivitäten; Feed-Eintrag = konkrete UI-Aufforderung; Aktivitätsprojektion = UI-naher Feed-Zustand; Retention-Track = nutzerweite Wiederholungsschicht; Retention-Scope = active|paused|opted_out je Wiederholungsumfang; Flashcard-Durchgang = serverseitige Kartenrunde; Lernbereich = fachlicher Themenraum; Modultyp = start|warmup|kompetenzliste|training|recall|feynman|skript|flashcards; Check = didaktische Einheit im Lernbereich; Kompetenz = Lernzieltext in der Kompetenzliste; Aufgabensammlung = Sammlung an Aufgaben pro Check; Aufgabe = konkrete Trainingsaufgabe aus der Aufgabensammlung; Frage = kleinste bewertete Einheit; Rolle = Autorisierungsmerkmal; check_id = stabiler Primärschlüssel im Content und in Fortschrittsdaten.`
