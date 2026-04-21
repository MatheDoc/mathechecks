# Konzept – Recall und Blurting

Dieses Dokument beschreibt die geplante **feed-unabhängige** Zielarchitektur für

- das überarbeitete, check-basierte Recall-Modul und
- ein neues, lernbereichsweites Modul für echtes Blurting.

Es beschreibt **nicht** den aktuellen technischen Ist-Stand. Dieser ist in `.github/recall-design.md` dokumentiert.


## Leitentscheidung

Die bisherige Grundidee ist richtig, aber es werden zwei unterschiedliche Lernaktivitäten vermischt:

1. **Check-naher Abruf mit klarer Stütze**
2. **Freies, größeres Brainstorming zu einem ganzen Lernbereich**

Didaktisch und architektonisch sollte das getrennt werden.


## Grundsatz: sinnvoll ohne Feed

Die Module müssen auch dann sinnvoll funktionieren, wenn es keinen echten Feed, keine Fälligkeit und keine modulübergreifende Steuerung gibt.

Daraus folgen drei Regeln:

1. Ein Modul muss seinen Zweck **aus sich heraus** erklären.
2. Ein Modul darf **keine Vorbedingung aus dem Feed** voraussetzen.
3. Ein Modul darf Ergebnisse liefern, ohne dass ein Feed sie sofort konsumieren muss.


## Architekturprinzip

Der Feed ist später nur ein **Auslöser und Konsument**, nicht Teil der Modul-Logik.

### Modul-Verantwortung

- UI und Interaktion
- lokaler Lernfluss innerhalb des Moduls
- lokaler Zustand der Seite
- Ergebniszusammenfassung wie z. B. `abgeschlossen`, `Selbsteinschätzung`, `offene Lücken`

### Nicht Aufgabe des Moduls

- Wann das Modul „dran" ist
- Welche Aktivität davor oder danach kommt
- Ob ein Ergebnis sofort gespeichert, bewertet oder in einen Feed eingehängt wird

### Technische Konsequenz

Jedes Modul sollte später mit einer einfachen Signatur auskommen:

```text
input data -> module interaction -> result summary
```

Zum Beispiel:

```text
check -> Recall-Modul -> { confidence, missingPoints, repeated }
lernbereich -> Blurting-Modul -> { coverageByCheck, unassignedNotes, openChecks }
```


## Modul A: Check-basiertes Recall-Modul

Dieses Modul ist die Weiterentwicklung des aktuellen check-basierten Recall-Moduls.

### Didaktische Rolle

Es ist **kein echtes Blurting** im engeren Sinn, sondern ein niedrigschwelliger, geführter Abruf zu **einem** Check.

Das Modul ist sinnvoll,

- direkt nach einem ersten Blick ins Skript,
- nach Training,
- zur schnellen Wiederholung zwischendurch,
- auch ohne jede Feed-Logik.

### Warum nicht mehr „Blurting"?

Bei einem einzelnen Check ist die freie Menge an abrufbarem Wissen oft klein.
Der Charakter ist daher nicht „schreibe alles auf, was du zu einem Thema weißt", sondern eher:

- Kompetenz ansehen
- kurz aktiv erinnern
- Kernpunkte konsolidieren
- gezielt wieder abrufen

Das spricht für einen anderen Namen.

### Namensempfehlung

Empfohlen als Nutzerbezeichnung:

- **Recall**

Alternativen:

- **Kernpunkte abrufen**
- **Aktiv erinnern**
- **Kurzabruf**

Empfehlung: fachlich knapp und international anschlussfähig ist **Recall** am stärksten.

### Wichtiger Architekturhinweis

Der aktuelle Modul-Key lautet inzwischen ebenfalls `recall`.
Der Begriff `Blurting` bleibt für das spätere lernbereichsweite Modul reserviert.


## Zielbild für Modul A

### Datenbasis pro Check

Das Modul braucht nur:

- `Ich kann`
- `Tipps`
- `Schlagwort`
- optional `skript_anchor`

Mehr darf es nicht voraussetzen.

### Dauerhaft sichtbarer Fokus

Die Kompetenz bleibt während des gesamten Moduls sichtbar.

Begründung:

- Der Abruf bleibt sauber auf die eigentliche Kompetenz bezogen.
- Die Lernenden verlieren die Frage nicht aus dem Blick.
- Das Modul wirkt auch ohne Feed als abgeschlossene, verständliche Aktivität.


## Lernfluss für Modul A

### Phase 1 – Freier Abruf

Startansicht:

- nur die Kompetenz
- ein Start-Button

Interaktion:

- in der ersten Umsetzung kein verpflichtendes Notizfeld
- Spracheingabe optional
- Kompetenz sichtbar
- einheitlicher Timer

Begründung:

- Die Phase bleibt dadurch deutlich niedrigschwelliger.
- Bei einem einzelnen Check ist die freie Menge an erinnerbaren Punkten oft klein.
- Die Notizen aus Phase 1 werden für Phase 2 und 3 nicht zwingend gebraucht.

Spätere Option:

- ein optionales Kurz-Notizfeld oder ein optionaler Spracheingabe-Impuls

Didaktischer Zweck:

- echtes Active Recall
- niedrige Einstiegshürde
- mentale Aktivierung ohne zusätzliche Schreibhürde

### Phase 2 – Kernpunkte konsolidieren

Prompt:

`Merke dir jetzt die wichtigsten Kernpunkte.`

Interaktion:

- Tipps als klare Liste
- gleiche Timer-Logik wie in Phase 1
- keine zusätzliche Komplexität

Didaktischer Zweck:

- Lücken schließen
- Relevantes verdichten
- Fokus auf das Wesentliche

### Phase 3 – Kernpunkte abrufen und abgleichen

Prompt:

`Rufe die Kernpunkte jetzt noch einmal ab.`

Interaktion:

- strukturierte Eingabefelder, idealerweise eines pro Tipp
- danach Referenz-Kernpunkte einblenden

Didaktischer Zweck:

- Retrieval nach Konsolidierung
- gezielter Abgleich mit den hinterlegten Kernpunkten
- Sichtbarmachen, was nach der Konsolidierung wirklich hängen geblieben ist


## Ergebnislogik von Modul A

Das Modul darf **kein Feed-Verhalten voraussetzen**.

Darum sollte die bestehende, einfache Selbsteinschätzung erhalten bleiben:

- `Kann ich`
- `Noch nicht`

Wichtig:

- `Kann ich` bedeutet hier nur: *Ich fühle mich mit diesem Check gerade ausreichend sicher.*
- `Noch nicht` bedeutet: *Ich brauche noch einen weiteren Durchlauf mit den Kernpunkten.*
- Beide Buttons dürfen später vom Feed konsumiert werden, müssen aber aktuell auch ohne Feed vollständig sinnvoll sein.

Lokales Verhalten ohne Feed:

- `Kann ich` führt zu einem einfachen Erfolgszustand.
- `Noch nicht` führt zurück zur Kernpunkt-Phase.
- Ein Skript-Link oder Trainings-Link kann ergänzend angeboten werden, ist aber nicht Teil der Kernlogik.


## Designprinzipien für Modul A

### 1. Eine Karte, drei Zustände

Keine vielen Unteransichten nebeneinander.
Eine zentrale Karte wandelt sich sichtbar durch die drei Phasen.

### 2. Kompetenz als Anker

Die Kompetenz steht oben fest und wird nicht nur am Anfang kurz eingeblendet.

### 3. Einheitliche Timer-Logik

Phase 1 und Phase 2 nutzen denselben Interaktionsrahmen.
Nur Inhalt und Dauer ändern sich.

### 4. Timer etwas prägnanter, aber nicht verspielt

Empfohlen:

- ruhiger Verlauf mit Farbgradient
- leichte Lichtkante oder Glow
- optional Ring-Timer oder Progress-Bar mit feiner Bewegung

Nicht empfohlen:

- hektische Animationen
- starke Game-Optik
- überladene Effekte

### 5. Zwei Arten von Eingabe klar unterscheiden

- Phase 1: freies Brainstorming
- Phase 3: gezielter Abruf von Kernpunkten

Gerade diese Trennung macht das Modul didaktisch sauber.


## Modul B: lernbereichsweites Blurting

Dieses neue Modul ist der Ort für **echtes Blurting**.

### Didaktische Rolle

Lernende schreiben zu einem ganzen Lernbereich alles auf, was sie schon wissen, erinnern, vermuten oder miteinander verknüpfen können.

Das Modul dient nicht primär dem Einüben eines Einzelchecks, sondern:

- der Vernetzung,
- der Selbstdiagnose,
- der Prüfungsvorbereitung,
- dem Sichtbarmachen von Wissenslücken auf Lernbereichsebene.

### Wichtig: ebenfalls feed-unabhängig

Das Modul sollte **nicht** erst sinnvoll werden, wenn „alle Checks erledigt" sind.

Bessere Formulierung:

- besonders sinnvoll **nach einem ersten Durchlauf** durch mehrere Checks
- aber jederzeit direkt startbar

So bleibt die Architektur unabhängig vom Feed.


## Namensfrage für Modul B

Didaktisch passt der Begriff **Blurting** hier deutlich besser als beim check-basierten Modul.

Empfohlene sichtbare Namen:

- **Wissenslandkarte**
- **Großes Blurting**
- **Lernbereichs-Blurting**

Empfehlung:

- nutzerseitig am klarsten: **Wissenslandkarte**
- methodisch präzise Unterzeile: `freies Blurting für den ganzen Lernbereich`


## Zielbild für Modul B

### Datenbasis pro Lernbereich

Das Modul braucht:

- Lernbereichstitel
- geordnete Check-Liste
- pro Check: `Schlagwort`, `Ich kann`, `Tipps`
- optional später: kleines Check-Bild oder Icon

### Lernfluss für Modul B

#### Phase 1 – Großer Brain Dump

Prompt-Beispiele:

- `Was weißt du schon über quadratische Funktionen?`
- `Schreibe alles auf, was dir zu diesem Lernbereich einfällt.`

Interaktion:

- großes Notizfeld
- Spracheingabe sinnvoll
- freie Stichpunkte, Fragmente, Formeln, Begriffe

#### Phase 2 – Strukturieren und zuordnen

Das System segmentiert die Notizen in einzelne Gedankenbausteine oder der User trennt sie selbst.

Danach werden die Checks sichtbar, z. B. mit:

- Schlagwort
- Kompetenz
- optional Mini-Illustration

Aufgabe:

- eigene Gedanken den passenden Checks zuordnen

#### Phase 3 – Abgleich mit Kernpunkten

Nach der Zuordnung zeigt das Modul die Tipps pro Check.

Dann wird sichtbar:

- was bereits abgedeckt ist,
- was unscharf war,
- welche Checks noch wenig oder gar nicht vorkamen.


## MVP für Modul B

Die große Idee mit frei verschiebbaren Notizzetteln ist interessant, aber als erste Version nicht nötig.

### Empfohlenes MVP

1. Freies Schreiben in einem großen Eingabefeld
2. Jede Zeile oder jeder getrennte Gedanke wird zu einem Chip
3. Jeder Chip wird per Klick oder Dropdown einem Check zugeordnet
4. Danach werden die Tipps pro Check eingeblendet
5. Abschließend zeigt das Modul eine einfache Übersicht über gut, teilweise und gar nicht abgedeckte Checks

### Warum dieses MVP besser ist als sofortiges Drag-and-Drop

- deutlich weniger Implementierungsaufwand
- besser auf Mobilgeräten
- weniger Bedienfriktion
- klarere Lernhandlung
- Barrierefreiheit leichter umsetzbar


## MVP-Spezifikation für Modul B

### Ziel von V1

V1 soll **keine automatische fachliche Bewertung** liefern, sondern eine gut strukturierte Selbstdiagnose auf Lernbereichsebene.

Am Ende der Aktivität sollen Lernende klar sehen:

- welche Checks sie bereits mit eigenen Gedanken gefüllt haben,
- welche Checks sie erst angerissen haben,
- welche Checks noch leer geblieben sind,
- welche Gedanken noch keiner Check-Struktur sauber zugeordnet sind.

Damit bleibt Modul B didaktisch nützlich, ohne künstlich „Intelligenz" vorzutäuschen.


### Datenvertrag V1

Für V1 werden **keine neuen Inhaltsfelder** eingeführt.

Das Modul liest nur bereits vorhandene Daten:

- aus `_data/dev_lernbereiche.yml`: `slug`, `name`, `gebiet`
- aus `dev/checks.json` pro Check: `check_id`, `Nummer`, `Schlagwort`, `Ich kann`, `Tipps`

Sortierung:

- Checks werden innerhalb eines Lernbereichs aufsteigend nach `Nummer` angezeigt.

Bewusst **nicht** Teil von V1:

- `beispiele/*.md`
- Aufgaben-JSON
- Feed-Daten
- neue Blurting-spezifische Autorenfelder in `checks.json`


### UI-Zustände V1

#### 1. Einstieg

Ziel:

- Zweck des Moduls kurz erklären
- Lernbereich sichtbar machen
- Aktivität mit einem klaren Start beginnen

Inhalt:

- Titel des Lernbereichs
- Unterzeile `Wissenslandkarte – freies Blurting für den ganzen Lernbereich`
- kurzer Erklärungstext in 1 bis 2 Sätzen
- Start-Button

#### 2. Brain Dump

Ziel:

- alles Vorwissen zunächst ungefiltert externalisieren

Inhalt:

- großes Textfeld
- Prompt wie z. B. `Schreibe alles auf, was dir zu diesem Lernbereich einfällt.`
- optional Spracheingabe
- Button `In Gedankenkarten aufteilen`

Regel:

- Jede nichtleere Zeile wird zunächst zu einer eigenen Gedankenkarte.

#### 3. Gedankenkarten prüfen

Ziel:

- Rohnotizen vor der Zuordnung bereinigen

Inhalt:

- jede Zeile als einzelne Karte oder Chip
- Karten können bearbeitet, gelöscht oder ergänzt werden
- zusätzlicher Button `Gedanke hinzufügen`

Regel:

- V1 nutzt nur vom User sichtbare und bearbeitbare Karten.
- Keine automatische semantische Zerlegung innerhalb einer Zeile.

#### 4. Checks zuordnen

Ziel:

- eigene Gedanken bewusst an die Check-Struktur des Lernbereichs anschließen

Inhalt:

- pro Gedankenkarte ein Dropdown oder Check-Picker
- Auswahl `noch nicht zugeordnet`
- pro Check sichtbar: `Nummer`, `Schlagwort`, `Ich kann`

Regel:

- jede Gedankenkarte hat in V1 genau **eine** Zuordnung
- wenn ein Gedanke zu mehreren Checks passt, wird er dupliziert statt mehrfach verlinkt

#### 5. Abgleich mit Kernpunkten

Ziel:

- sichtbar machen, wo das eigene Vorwissen mit der Check-Struktur zusammenpasst und wo Lücken bleiben

Inhalt pro Check:

- `Schlagwort`
- `Ich kann`
- eigene zugeordnete Gedankenkarten
- `Tipps` als Referenz-Kernpunkte

Zusätzlich:

- eigener Bereich für unzugeordnete Gedankenkarten

#### 6. Ergebnisübersicht

Ziel:

- eine einfache, ehrliche Abschlussdiagnose geben

V1 verwendet **transparente Mengenregeln** statt inhaltlicher Qualitätsurteile:

- `abgedeckt`: mindestens 2 Gedankenkarten zugeordnet
- `angerissen`: genau 1 Gedankenkarte zugeordnet
- `offen`: 0 Gedankenkarten zugeordnet
- `unzugeordnet`: Karten ohne Check-Zuordnung

Wichtig:

- Diese Übersicht ist nur eine **Strukturdiagnose**, keine fachliche Bewertung der Gedankenqualität.


### Interaktionsregeln V1

- Das Modul ist vollständig ohne Feed nutzbar.
- Der User kann jederzeit zur vorherigen Phase zurückgehen.
- Ein Lernbereich gilt nicht automatisch als „abgeschlossen".
- Ergebnisse bleiben zunächst lokal im Seitenzustand; Persistenz über Sitzungen hinweg ist optional und nicht Teil des Kern-MVP.
- Die Tipps werden erst nach der Zuordnung eingeblendet, damit der freie Abruf nicht vorzeitig gestützt wird.


### Bewusst nicht in V1

- kein Drag-and-Drop-Board
- keine freie räumliche Arbeitsfläche
- keine automatische NLP-Zuordnung von Gedanken zu Checks
- keine inhaltliche Korrektur oder automatische mathematische Bewertung
- keine Feed-Integration
- keine neuen Felder in `checks.json`


### Geeigneter Pilotumfang

Für den ersten Test ist ein Lernbereich mit **5 bis 6 Checks** am sinnvollsten.

Zu klein wäre z. B. ein Lernbereich mit nur 1 bis 3 Checks, weil dort der Mehrwert eines lernbereichsweiten Blurtings kaum sichtbar wird.
Zu groß wäre für V1 z. B. ein Lernbereich wie `binomialverteilung`, weil die erste Iteration dann sofort zu viele Zuordnungen erzeugt.

Geeignete Pilotkandidaten sind aktuell zum Beispiel:

- `produktlebenszyklus` mit 5 Checks
- `lineare-gleichungssysteme` mit 5 Checks
- `zufallsgroessen` mit 5 Checks


### Technischer Umsetzungspfad für V1

1. Zuerst eine **isolierte Prototypseite** bauen, noch **ohne** Eintrag in `dev_moduletypen.yml`.
2. Diese Prototypseite bekommt einen einzigen Lernbereich fest verdrahtet oder per `data-lernbereich` übergeben.
3. Das JS-Modul liest nur `dev/checks.json` und `_data/dev_lernbereiche.yml`.
4. Erst wenn der Ablauf didaktisch trägt, wird Modul B als echter Modultyp global in Navigation, Farben und Bootstrap aufgenommen.

Der Grund für diese Reihenfolge:

- Ein neuer Modultyp in `dev_moduletypen.yml` würde sofort global in der Tab-Navigation erscheinen.
- Für einen ersten Test ist das zu früh.
- V1 sollte zunächst als in sich geschlossener Prototyp überprüft werden.


## Spätere Ausbaustufe für Modul B

Wenn das MVP didaktisch überzeugt, kann eine stärkere Raum-Metapher folgen.

Mögliche Erweiterungen:

- frei verschiebbare Wissens-Chips
- Check-Karten als Zielbereiche
- kleine SVG-Motive pro Check
- Clusterbildung auf einer Arbeitsfläche
- Hintergrundmotiv als ruhige Wissenslandschaft statt abstraktes Whiteboard

Wichtig:

Die Raum-Metapher darf das Lernen nicht überlagern. Der Kern bleibt die inhaltliche Zuordnung.


## Empfohlene Trennung der Module

### Modul A

- klein
- schnell
- check-bezogen
- geführter Abruf
- jederzeit sinnvoll

### Modul B

- groß
- vernetzungsorientiert
- lernbereichsbezogen
- offenes Brainstorming und Strukturieren
- eher Synthese als Einzelwiederholung


## Architektur-Fazit

Die sauberste Lösung ist:

1. Das aktuelle check-basierte Modul inhaltlich zu **Recall** umdeuten und gestalterisch darauf zuschneiden.
2. Den Begriff bzw. die Methode **Blurting** für ein neues, lernbereichsweites Modul reservieren oder dort in verständlicher Form als `Wissenslandkarte` sichtbar zu machen.
3. Beide Module so entwerfen, dass sie **ohne Feed vollständig sinnvoll** sind.

Erst danach lohnt es sich, einen Feed später optional als äußere Lernsteuerung daran anzukoppeln.


## Empfohlene nächste Umsetzungsschritte

1. Einen Pilot-Lernbereich mit 5 bis 6 Checks auswählen.
2. Für diesen Lernbereich eine isolierte Modul-B-Prototypseite ohne globalen Modultyp anlegen.
3. Den oben beschriebenen klickbasierten MVP vollständig umsetzen.
4. Danach mit echtem Inhalt prüfen, ob die Ergebnisübersicht als Selbstdiagnose verständlich ist.
5. Erst nach diesem Test entscheiden, ob Drag-and-Drop oder räumliche Board-Interaktion überhaupt nötig sind.