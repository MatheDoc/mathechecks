# Erklärvideos (Pilot)

Kurzvideos im Hochformat (YouTube Shorts, TikTok), eines pro Check, erzeugt mit [Manim](https://www.manim.community/) und `manim-voiceover`.

Stand: Pilot mit achtzehn Videos. Der Ordner ist von Jekyll ausgeschlossen; die fertigen Videos liegen auf YouTube und erscheinen auf der Website im Modul „Video“ (siehe „Einbindung in die Website“). Arbeitsauftrag für die KI: Skill `video-erstellen` (`.github/skills/video-erstellen/SKILL.md`), Rolle `agent-video`.

## Vorlagen

Neue Szenen entstehen aus der Vorlage, die dem Check am nächsten kommt (alle unter `checks/`):

| Art des Checks | Vorlage |
|---|---|
| Rechenverfahren in Schritten, tragender Graph | `analysis/differentialrechnung-ganzrationaler-funktionen/06-extremstellen-bestimmen.py` |
| Algorithmus an einer Matrix | `lineare-algebra/lineare-gleichungssysteme/02-lgs-loesen-3x3.py` |
| Kennzahlen einer Matrix ablesen und vergleichen, Fälle durch Ändern einer Zeile | `lineare-algebra/lineare-gleichungssysteme/05-lgs-rangkriterium.py` |
| Textverständnis, viele Fallarten, Bild begleitet nur | `stochastik/binomialverteilung/05-bereichswahrscheinlichkeiten-berechnung.py` |
| Diagramm lesen ohne Ablauf, nach den Teilaufgaben des Trainings | `stochastik/bedingte-wahrscheinlichkeiten/03-baumdiagramm-folgern-mit-unabh.py` |
| Diagramm mit Lücken vervollständigen, Werte wandern aus der Rechnung ins Feld | `stochastik/bedingte-wahrscheinlichkeiten/02-baumdiagramm-erstellen-mit-unabh.py` |
| Symbole in Worte übersetzen, Wahrscheinlichkeit als Teil durch Ganzes (Punktefeld mit Ereigniskästen) | `stochastik/bedingte-wahrscheinlichkeiten/01-interpretationen-mit-bedingt.py` |
| Graph im Sachzusammenhang lesen (Kennzahl ↔ Merkmal, jede Kennzahl eine Farbe) | `analysis/produktlebenszyklus/01-kennzahlen-graphisch-umsatz.py` |
| Sachaufgabe: Größen im Text erkennen und in eine Formel einsetzen (Orange nur für die gesuchte Größe, Zeitstrahl) | `finanzmathematik/zinseszinsrechnung/02-zinseszins-sachaufgaben.py` |
| Bereiche einer Verteilung im Histogramm, Tabelle bleibt oben stehen (Hypothesentest) | `stochastik/hypothesentests/01-hypothesenergebnis.py` |
| Formel umformen: wo die Unbekannte steht, entscheidet über das Werkzeug (Formel bleibt groß auf der Bühne) | `finanzmathematik/zinseszinsrechnung/01-zinseszinsformel-umformen.py` |
| Zwei Abschnitte über einen Zwischenwert verbinden, vorwärts oder rückwärts rechnen (`Phasenstrahl`) | `finanzmathematik/zinseszinsrechnung/03-zinssatzwechsel.py` |
| Angebote mit Zahlungen zu verschiedenen Zeitpunkten vergleichen (`Zahlungsplan`) | `finanzmathematik/zinseszinsrechnung/04-kapitalvergleich-einmalzahlungen.py` |

## Aufbau

```text
videos/
  render.py                 einziger Einstieg zum Rendern
  aufnahme.py, aufnahme.html  eigene Stimme einsprechen (lokale Seite im Browser)
  requirements.txt
  mcvideo/                  gemeinsame Bibliothek
    theme.py                Farben, Schrift, Bildaufteilung, Auflösung
    szene.py                Basisszene MCSzene: Logo, Bereiche, Ton, Schlussbild, Randprüfung
    bausteine.py            Frage, Schritt, Kurzfassung, Aufzählung, Legende, Tabelle, Zahlenstrahl, Versuche, Histogramm, Zeitstrahl, Phasenstrahl, Zahlungsplan, ErweiterteMatrix, Baumdiagramm, Punktefeld, Betrag, Dezimalzahl, …
    stimme.py               Sprachdienst: eigene Aufnahmen, sonst Entwurfsstimme
    fonts/                  Inter (SIL Open Font License)
  checks/<gebiet>/<lernbereich>/<NN>-<sammlung>.py   Szene eines Checks
  aufnahmen/<gebiet>/<lernbereich>/<NN>-<sammlung>/   eigene Sprachaufnahmen je Sprechabschnitt (MP3, im Repo)
  media/                    Zwischenstände, Tonzwischenspeicher, Prüfbögen (gitignored)
  ausgabe/<gebiet>/<lernbereich>/<NN> <Schlagwort> <Lernbereichsname>.mp4  fertige Videos (gitignored)
```

Die Szene heißt `<NN>-<sammlung>.py` nach der Aufgabensammlung des Checks (Feld `Sammlung` in `_data/checks.json`). Sie ist die Quelle des Videos, zusammen mit den eigenen Sprachaufnahmen, sobald es sie gibt. Aus dem Pfad ergibt sich die `check_id`; `render.py` bricht ab, wenn es sie in `_data/checks.json` nicht gibt.

## Einrichten

```powershell
python -m venv videos\.venv
videos\.venv\Scripts\python -m pip install -r videos\requirements.txt
```

Zusätzlich nötig: LaTeX (MiKTeX) für die Formeln und eine Internetverbindung für die Entwurfsstimme. Getestet mit Python 3.14.

## Ablauf

1. **Szene** schreiben: Klasse `Video(MCSzene)` mit der Methode `inhalt()`, die mit `self.einstieg(...)` beginnt. Im Kopf der Datei stehen zwei Zeilen: die Kernidee und ob das Beispiel vom Musterbeispiel abweicht. Ausgangspunkt ist eine der Vorlagen oben.
2. **Entwurf** rendern (540 × 960, etwa eine Minute):

   ```powershell
   videos\.venv\Scripts\python videos\render.py videos\checks\<gebiet>\<lernbereich>\<NN>-<sammlung>.py
   ```

   Ausgegeben werden Dauer, Wortzahl und alle Objekte außerhalb des sichtbaren Bereichs.
3. **Prüfbogen** durchsehen: `media/pruefung/<check_id>/pruefbogen.md` zeigt je Sprechabschnitt das Standbild mit dem Sprechtext (Überlappungen, Lesbarkeit, fachliche Richtigkeit). Er wird bei jedem Entwurf neu erzeugt.
4. **Einsprechen** (wenn das Video die eigene Stimme bekommen soll): siehe „Eigene Stimme einsprechen“.
5. **Final** rendern (1080 × 1920, 30 Bilder pro Sekunde) mit `--final`. Das Video landet in `ausgabe/<gebiet>/<lernbereich>/` und heißt `<NN> <Schlagwort> <Lernbereichsname>.mp4`, etwa `02 LGS 3x3 Lineare Gleichungssysteme.mp4`. YouTube übernimmt den Dateinamen beim Hochladen als Titel und ersetzt Bindestriche durch Leerzeichen; Schlagwort und Lernbereichsname aus `_data/checks.json` müssen deshalb als Dateiname taugen (Regel in `.github/datenmodell.md`). Ein früheres Video des Checks wird ersetzt. Bei Randverstößen oder unvollständigen Aufnahmen wird nichts ausgegeben. Zusätzlich entsteht das Vorschaubild der Website `assets/img/videos/<check_id>.webp` (Bild und Frage am Ende des ersten Sprechabschnitts, 720 × 1280); es gehört ins Repo.
6. **Hochladen** auf YouTube (als Short) und die Video-ID im Feld `video` des Checks in `_data/checks.json` eintragen (die 11 Zeichen aus `youtube.com/shorts/<ID>`). Damit erscheint das Video im Modul „Video“.

## Regeln für ein Video

- Umfang: Ziel 60–90 Sekunden, Richtwert höchstens 200 Wörter Sprechtext, Obergrenze 180 Sekunden.
- Einstieg (für alle Videos gleich, `self.einstieg(...)`):
  1. Ein kennzeichnendes Bild entsteht, am besten eines, mit dem das Video weiterarbeitet (hier der Graph), sonst ein Bild mit Symbolcharakter. Das erste Bild ist nicht leer.
  2. Dazu erscheint die Frage, gesprochen und geschrieben, weiß und ohne Farbcode. Sie steht in der Du-Form und benennt das Thema sofort, nach dem Muster „Wie bestimmst du Hoch- und Tiefpunkte?“ (der umgedrehte Kompetenzsatz des Checks). Die Frage bleibt kurz, höchstens zwei Zeilen; eine nötige Ergänzung steht als `zusatz` kleiner darunter und wird mitgesprochen, etwa „(mit bedingten Wahrscheinlichkeiten)“.
  3. Begrüßung: Unter der Frage erscheint das Logo mit Lichtschein, darunter `mathechecks.de` (wie im Schlussbild, nur kleiner); gesprochen wird `MCSzene.begruessung`.
  4. Das Logo wandert in die Ecke und bleibt dort; erst jetzt erscheint die Kopfzeile.
- Die Kopfzeile ist freiwillig. Sie zeigt das Gegebene, auf das sich die Rechnung durchgehend bezieht (etwa den Funktionsterm). Steht das Gegebene schon auf der Bühne, bleibt sie zunächst leer und nimmt am Ende das Ergebnis auf (Check 02 der linearen Gleichungssysteme).
- Das Video bereitet auf die Trainingsaufgabe des Checks vor. Maßgeblich sind deren Teilaufgaben (Export unter `aufgaben/exports/json/<gebiet>/<lernbereich>/<sammlung>.json`, Arten der Teilaufgaben im zugehörigen Generator): Jede Art von Teilaufgabe soll im Video vorkommen oder bewusst weggelassen sein; nicht jede muss durchgerechnet werden. Das Bild entspricht dem der Aufgabe (etwa ein vollständig ausgefülltes Baumdiagramm).
- Ein Video trägt eine Kernidee. Das Musterbeispiel ist nur Orientierung: Es rechnet nicht immer die Trainingsaufgabe vor, sondern erläutert teils allgemeiner. Sachzusammenhang und Zahlen werden möglichst übernommen, aber das Video zeigt nur so viele Fälle, wie die Kernidee braucht (Check 05 der Binomialverteilung: fünf von dreizehn Ereignissen, je eines pro Schwierigkeit, und ein Lösungsweg statt zwei).
- Ein Check bekommt genau ein Video. Gehört zum Check auch die Abgrenzung (etwa „binomialverteilt oder nicht“), kommt sie als kurzer eigener Fall ins selbe Video.
- Nummern stehen nur für einen Ablauf. Checks ohne festen Rechenweg (Textverständnis, viele Fallarten, Diagramme lesen) bekommen keine nummerierten Schritte, sondern Abschnitte mit einfacher Überschrift oder mehrere kurze Fälle nach demselben Muster: Wortlaut, Bild, Rechnung.
- Geht es um das Lesen eines Diagramms, zeigt das Video vor allem, wo welche Größe steht und welche nicht dort steht. Die entscheidende Unterscheidung des Checks bekommt einen eigenen Abschnitt, in dem beide Fälle untereinander stehen (Check 03 der bedingten Wahrscheinlichkeiten: $P_A(B)$ ablesen, $P_B(A)$ rechnen).
- Das Video erklärt, wie es geht. Fehlerwarnungen gehören nicht hinein; nur eine bekannte Fehlvorstellung darf ausnahmsweise ausdrücklich angesprochen werden.
- Vor dem Schluss steht eine Kurzfassung ohne Überschrift, die den Tipps des Checks folgt: bei einem Ablauf die nummerierten Schritte oder Leitfragen (Baustein `kurzfassung`), sonst eine Übersicht ohne Nummern mit Punkten in der Stimmungsfarbe (Baustein `aufzaehlung`, etwa Stichwort und zugehörige Größen unter „ablesen“ und „rechnen“).
- Schluss: für alle Videos gleich und nicht je Video zu schreiben. Das Logo wandert aus der Ecke in die Bildmitte, dazu „Jetzt bist du dran.“ und die Adresse; gesprochen „Jetzt bist du dran. Bis zum nächsten Check!“. Text und Ton stehen in `MCSzene` (`schlussbild`, `schlusston`).
- Sprache: direkt, verbindlich und motivierend; „du“ in Einstieg und Schluss, „wir“ beim Rechnen. Lockere Wendungen und Anglizismen sind erlaubt, Fachbegriffe bleiben exakt wie im Skript des Lernbereichs.
- Das Bild muss ohne Ton verständlich sein. Der Sprechtext wird so geschrieben, wie er gesprochen wird („x Quadrat“). Eine eigene Untertiteldatei gibt es nicht; die automatischen Untertitel von YouTube genügen.
- Einblendungen hängen am Ton, nicht an festen Sekunden: `self.warte_bis(0.6)` wartet, bis 60 % des laufenden Sprechtexts gesprochen sind. So passen die Zeiten auch nach einem Stimmwechsel.
- Keine Originalaufgaben aus `muster-pruefungen/`.

## Gestaltung

Alles Gestalterische steht in `mcvideo/theme.py` und gilt nach dem Neurendern für alle Videos.

- Schrift wie auf der Website (Inter), Formeln setzt LaTeX. Wörter stehen nicht in Formeln, sondern als Text daneben (`reihe`). Steht eine Formel mitten in einem Satz, sitzen Text und Formel mit `reihe(..., grundlinie=True)` auf einer gemeinsamen Schriftgrundlinie, sonst wirkt die Formel verschoben. Unterlängen werden dabei herausgerechnet, bei Text (g, p, y …) wie bei Formeln (Indizes wie $H_0$, Dezimalkomma wie $0{,}0287$); eine Zeile wie „Fehler 1. Art: 0,0287“ braucht deshalb keine Handkorrektur.
- Zwei Farbebenen:
  - Stimmungsfarbe (`MARKE`, das Violett der Website), gedämpft und nur in Flächen und Rändern: Schimmer im Hintergrund, getönte Karte, Schrittnummern, Lichtpunkt beim Zeichnen, Schlussbild. Sie ist nie Schrift- oder Linienfarbe in der Rechnung und in allen Gebieten dieselbe, damit die Objektfarben in jedem Video dasselbe bedeuten.
  - Objektfarben, kräftig: Was zusammengehört, hat dieselbe Farbe, im Bild wie in der Rechnung. `HERVOR` (Orange) ist das Objekt, um das es gerade geht (Tangente und ihre Steigung, Kandidaten, die gesuchte Größe); `ROSE` und `BLAU` unterscheiden ein Paar (Hoch- und Tiefpunkt); `TUERKIS` und `GRUEN` stehen für weitere Objekte bereit. `BLAU` ist ein Himmelblau, damit es sich vom Violett absetzt.
- Farben sparsam einsetzen, in dieser Rangfolge:
  1. Weiß ist die Grundfarbe für Text, Überschriften und Rechnung, Grau für Nebensächliches.
  2. Orange (`HERVOR`) ist die erste Betonungsfarbe; viele Videos kommen mit Weiß und Orange aus. Orange darf auch einzelne Wörter im Wortlaut einer Aufgabe markieren (Signalwörter).
  3. Weitere Objektfarben kommen erst dazu, wenn mehrere Dinge gleichzeitig unterschieden werden müssen. Sie gehören zu einem Objekt im Bild (Punkt, Linie, Ast) und zu dem Wert, der daran abgelesen oder berechnet wird; erklärender Text bleibt weiß oder grau.
  4. Das erste Bild kommt ohne Objektfarben aus. Farben kommen nach und nach dazu, in der Regel eine oder ein Paar pro Abschnitt; erst die Kurzfassung darf alle als Legende zeigen.
  5. Größen, die in jedem Abschnitt alle zugleich vorkommen (etwa $K_0$, $K_n$, $p$ und $n$), bekommen keine eigenen Farben: Zugeordnet wird über den Ort im Bild, betont über Bewegung. Orange bleibt dann der gesuchten Größe vorbehalten (Check 02 der Zinseszinsrechnung).
- Objekte werden nur über die Schriftfarbe gekennzeichnet, ohne farbige Hinterlegung.
- Bewegung mit Bedeutung: `zeichnen` baut eine Linie mit mitlaufendem Lichtpunkt auf; `welle` markiert die Stelle, an der gerade etwas passiert; `auftritt` blendet Text ein.
- Bildaufteilung von oben nach unten: Kopf (Logo, Titel), Bühne auf einer Karte (`self.buehne()`), Tafel (Rechnung, Text). `self.tafel(...)`, `self.achsen(...)` und `self.auf_buehne(...)` passen Inhalte in ihren Bereich ein. `achsen` beschriftet die Achsen mit `namen=("x", "y")`; im Sachzusammenhang etwa `namen=("t", "a(t)")`.
- Die Höhe der Bühne richtet sich nach dem Bild: volle Höhe für einen Graphen, flach (`self.buehne(hoehe=2.5)`) für ein Bild, das nur begleitet, etwa den `Zahlenstrahl`. Die Tafel rückt dann nach oben und bekommt mehr Platz; die Schrift darf dort größer sein. So bleibt auch bei textlastigen Checks ohne tragendes Bild die obere Bildhälfte nicht leer.
- Ein Bild stützt jedes Video, auch textlastige: Auf dem `Zahlenstrahl` erscheint der Bereich, von dem der Text spricht; `Versuche` zeigt einzelne Versuche, wenn es nicht um eine Anzahl geht.
- Matrizen: `ErweiterteMatrix` zeigt ein LGS in Matrixform mit Zeilennamen und hält den aktuellen Stand der Zahlen (`werte`). `gleichungen()` setzt das LGS als Gleichungen, `aus_gleichungen()` lässt die Koeffizienten von dort in die Matrix wandern. Umformungen stehen wie im Heft rechts neben der Zeile; `self.zeilenumformung(matrix, zeile, faktor, basis, ...)` zeigt darunter die Nebenrechnung in denselben Spalten (`nebenrechnung`) und ersetzt danach die Zeile. Zeilennamen sind aufrechte römische Zahlen.
- Baumdiagramme: `Baumdiagramm` zeigt zwei Ereignisse A und B wie auf der Website (von links nach rechts, Wahrscheinlichkeiten an den Ästen, Produkte an den Pfadenden). `markiere` färbt die Äste und Pfadenden, um die es gerade geht, in der Farbe der zugehörigen Zahlen in der Rechnung; mit `knoten=False` bleiben die Kreise ungefärbt, wenn nur Werte verglichen werden (Check 02: zweite Stufe oben und unten gleich). Mit `luecken=(…)` stehen in offenen Feldern die Feldnummern ① bis ⑩ wie auf der Website (Baustein `feldnummer`, auch für die Rechnung); `fuelle(nr, quelle=…)` lässt den Wert aus der Rechnung (oder von einem anderen Ast) in das Feld wandern.
- Punktefeld: `Punktefeld` zeigt Personen (oder Ergebnisse) als Gitter, Ereignisse als durchsichtige Kästen in ihrer Farbe wie im Kontextbild, den Namen außen daneben (`zeige`). `markiere(ganzes, teil, kasten)` lässt alle außerhalb des Ganzen zurücktreten, färbt den Teil und hebt den Kasten der Bedingung hervor: Wahrscheinlichkeit als Teil durch Ganzes. Kästen, die über das ganze Feld reichen, machen die Ereignisse unabhängig; für bedingte Wahrscheinlichkeiten deshalb Kästen wählen, die das nicht tun.
- Histogramme: `Histogramm` zeigt die Binomialverteilung mit dem Wert von p rechts oben. `faerbe` färbt Bereiche samt ihren Grenzen in der Beschriftung (Hypothesentests: Ablehnungsbereich `ROSE`, Annahmebereich `BLAU`), `zu` wechselt p bei gleichem Maßstab (etwa von $p_0$ zu $p_1$). Gesprochen wird „Annahmebereich“ und „Ablehnungsbereich“, nicht „A“ und „A quer“.
- Was beim Rechnen stehen bleiben soll (etwa Hypothesen mit Annahme- und Ablehnungsbereich als `tabelle`), setzt `self.oben_auf_tafel(...)` oben auf die Tafel; `self.tafel(..., unter=...)` ordnet die Rechnung darunter an.
- Zeitstrahl (Finanzmathematik): `Zeitstrahl` zeigt links den früheren und rechts den späteren Zeitpunkt. Über dem Strahl stehen die Zeitangaben, darunter Beträge und Zins. `zeige` ersetzt einzelne Angaben; `uebernimm` lässt ein Ergebnis aus der Rechnung an die Stelle des Fragezeichens wandern.
- Phasenstrahl (Zinssatzwechsel): `Phasenstrahl` ist ein Zeitstrahl mit Teilstrich am Übergang zweier Zinsphasen, schematisch statt maßstäblich, damit die Beträge nebeneinander passen. Über den Phasen stehen Dauer und Zinssatz (`phase1`, `phase2`), darunter `anfang`, `mitte` (Zwischenwert) und `ende`. `phase(nr)` legt eine Fläche in der Stimmungsfarbe unter die Phase, in der gerade gerechnet wird; `zeige`, `uebernimm` und `betone` wie beim `Zeitstrahl`.
- Zahlungsplan (Kapitalvergleich): `Zahlungsplan` zeigt je Angebot eine Zeile mit den Zahlungen an ihren Jahren und rechts die Spalte „Barwert“. `bogen` zeichnet den Abzinsungspfeil von einer Zahlung zurück auf heute, `faerbe` färbt die Zahlung, `barwert` lässt den Barwert aus der Rechnung rechtsbündig in die Spalte wandern.
- Wortlaut einer Aufgabe: `wortlaut` setzt ihn in Anführungszeichen, eine Bildzeile je Argument; Signalwörter erscheinen orange.
- Geldbeträge: `betrag` setzt das Eurozeichen in der Hausschrift hinter die Formel, weil LaTeX hier kein Eurozeichen setzt (`\text{€}` bleibt leer).
- Ein Wert, der weiterverwendet wird, behält seine Farbe und wandert sichtbar an die Stelle, an der er eingesetzt wird (Rückwärtseinsetzen).
- Bleibt unter der Rechnung Platz frei, rückt `self.tafel(...)` den Block ein Stück nach unten (`TAFEL_LAGE` in `theme.py`), damit das Bild gleichmäßiger gefüllt ist. Leere Flächen sind in Ordnung.
- Zeichen und ihre Bedeutung stehen zweispaltig bündig (`legende`).
- Sichtbarer Bereich: Der untere Rand und die Bedienleiste rechts unten bleiben frei, weil die Shorts-Oberfläche sie überdeckt. Die Werte in `theme.py` sind Richtwerte und noch nicht am Handy geprüft.
- Zahlen mit Dezimalkomma: `Dezimalzahl` statt `DecimalNumber`.

## Stimme

Entwürfe sprechen mit gTTS (kostenlos, braucht Internet). Der Ton wird je Sprechabschnitt in `media/voiceovers/` zwischengespeichert; ändert sich ein Text, wird nur dieser Abschnitt neu erzeugt. Die Entwurfsstimme wird an einer Stelle gewechselt, in `mcvideo/stimme.py`.

### Eigene Stimme einsprechen

Erst wenn Bild und Text stehen (Entwurf mit der Entwurfsstimme abgenommen), wird eingesprochen:

```powershell
videos\.venv\Scripts\python videos\aufnahme.py videos\checks\<gebiet>\<lernbereich>\<NN>-<sammlung>.py
```

Das öffnet eine lokale Seite im Browser (beim ersten Mal das Mikrofon freigeben). Sie zeigt je Sprechabschnitt den stummen Videoausschnitt und groß den Sprechtext.

| Taste | Wirkung |
|---|---|
| Leertaste | Aufnahme starten; während der Aufnahme: speichern und direkt den nächsten Abschnitt aufnehmen |
| Enter | Aufnahme beenden und speichern |
| Esc | Aufnahme verwerfen |
| A | Aufnahme des gewählten Abschnitts zum Videoausschnitt anhören |
| ↑ ↓ | Abschnitt wählen (oder in der Liste anklicken) |

- Ein Abschnitt lässt sich beliebig oft neu aufnehmen; die neue Aufnahme ersetzt die alte. Stille und Tastenanschlag an Anfang und Ende werden abgeschnitten, die Lautstärke wird angeglichen.
- „Entwurf neu rendern“ baut das Video mit den Aufnahmen: Die Einblendungen richten sich dann nach der eigenen Sprechdauer. Danach „Ganzes Video ansehen“.
- „Final rendern“ entspricht `render.py --final`. Ein finales Video entsteht nur mit einer Stimme: entweder sind alle Abschnitte eingesprochen oder keiner.
- Die Aufnahmen liegen als MP3 unter `videos/aufnahmen/<gebiet>/<lernbereich>/<NN>-<sammlung>/` (derselbe Teilpfad wie die Szene) und gehören ins Repo: Zusammen mit der Szene sind sie die Quelle des fertigen Videos. `render.py` verwendet sie automatisch.
- Eine Aufnahme gehört zu genau einem Sprechtext (Kennung am Ende des Dateinamens). Wird der Text geändert, spricht diesen Abschnitt wieder die Entwurfsstimme, bis er neu aufgenommen ist; `render.py` nennt die betroffenen Abschnitte in der Zeile „Stimme“.
- Begrüßung und Schluss werden für jedes Video neu gesprochen, nicht zentral gespeichert.

## Einbindung in die Website

Modul „Video“ in jedem Lernbereich (`lernbereiche/<gebiet>/<lb>/video.md`, Reiter zwischen Kompetenzliste und Warm-Up). Es zeigt nur Checks mit Feld `video` in `_data/checks.json`; Auswahl per `#check-<Nummer>`. Kein Feed, keine Quote, keine XP.

| Datei | Rolle |
|---|---|
| `_includes/module/video-content.html` | Check-Navigation, Liste der Checks mit Warm-Up |
| `assets/js/modules/video.js` | Abspieler |
| `assets/css/video.css` | Styling (Präfix `vid-`) |
| `assets/img/videos/<check_id>.webp` | Vorschaubild aus `render.py --final` |

- **Datenschutz:** Beim Seitenaufruf wird nur das eigene Vorschaubild geladen, keine Verbindung zu YouTube. Erst der Klick auf das Bild lädt die YouTube-IFrame-API und den Player (`youtube-nocookie.com`, `rel=0`) und startet das Video; Abschnitt „YouTube-Videos“ in `datenschutz.md`. Im Kartenkopf steht hinter dem Schlagwort ein kleiner Link „Auf YouTube ↗“.
- **Ein Klick:** Auf dem Desktop startet das Video direkt. Auf iPhone und iPad kann Safari den automatischen Start verweigern; dann bleibt der Play-Knopf von YouTube stehen und ein zweites Tippen ist nötig.
- **Ende:** Statt der YouTube-Vorschläge erscheint eine eigene Fläche mit „Warm-Up“ (falls vorhanden), „Training“ und „Nochmal“.
- Fehlt das Vorschaubild, zeigt die Karte stattdessen den Kompetenzsatz.
- **Cache:** nach Änderungen an `video.js` den `?v=` des Imports in `assets/js/app.js` und den von `app.js` in `_layouts/module.html` erhöhen; nach Änderungen an `video.css` `page_css` in allen `video.md`.

## Offen

- `abspann.mp4` und `abspann.pptx` sind der frühere Abspann und werden von den neuen Videos nicht verwendet
