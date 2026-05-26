# Feed-Logik

Stand: Mai 2026

Diese Datei beschreibt die aktuell wirksame Feed-Logik in MatheChecks.
Sie dokumentiert die fachliche Reihenfolge- und Mischlogik des Feeds, nicht das vollständige Datenmodell und nicht das historische Zielbild.

## Dokumentgrenzen

- Diese Datei beschreibt die aktuelle Projektion und Reihenfolge des Feeds aus Sicht von Dashboard, Sidebar und Feed-Kontext im Frontend.
- `.github/benutzerverwaltung-mvp.md` beschreibt dagegen Datenmodell, Tabellen, RPCs, Sicherheitsmodell und den Plattform-Schnitt des Feeds.
- `.github/datenmodell.md` beschreibt die Trennung zwischen Repo-Content und persistenter Plattformlogik.
- `.github/feed-design-vorschlag.md` bleibt als breiterer Design- und Zielbildtext erhalten; die dortigen Aussagen zur aktuellen Reihenfolge werden nicht mehr als operative Spezifikation gepflegt.

## Zielbild in Kurzform

- Der Feed zeigt den nächsten sinnvollen Lernschritt, nicht nur eine rohe Liste offener Datenbankzeilen.
- Offene Session-Aktivitäten bleiben während einer aktiven Core-Session leitend.
- Begonnene Check-Ketten sollen sichtbar weitergehen, aber nicht sofort komplett durchlaufen.
- Retention-Flashcards aus früheren Sessions bleiben sichtbar, sollen die aktive Session aber nicht dominieren.
- Dashboard und Sidebar lesen dieselbe Projektion und dieselbe Reihenfolge.
- Der Feed-Kontext bleibt von freiem Modulzugriff getrennt.

## Datenquellen des Feeds

Die aktuelle Feed-Projektion in `assets/js/platform/feed-projection.js` kombiniert:

- aktive Core-Session aus `learning_sessions`
- offene checkbezogene Schritte aus `session_check_state`
- offene lernbereichsweite Session-Aktivitäten aus `session_activity_state`
- aktive Retention-Scopes und user-scoped Flashcard-Fälligkeiten
- Repo-Metadaten aus `checks.json` und den Lernbereichs-Daten

## Verarbeitungsreihenfolge

Die Feed-Projektion läuft in dieser Reihenfolge:

1. Aktive Core-Session laden.
2. Zentrale Systemwerte aus `public.system_settings` laden.
3. Falls eine aktive Session existiert:
   - offene Check-Schritte laden
   - offene Session-Aktivitäten laden
  - aktive und bereits sichtbare Retention-Einträge für dieselbe Nutzerin oder denselben Nutzer laden
4. Check-Schritte innerhalb der Session ordnen.
5. Session-Aktivitäten und geordnete Check-Schritte zu einer Session-Liste zusammenbauen.
6. Retention-Einträge queuebasiert in die Session-Liste einmischen.
7. Falls keine Session-Einträge übrig sind, auf reine Retention-Projektion ohne aktive Session zurückfallen.
8. Erst ganz am Ende auf das sichtbare Feed-Limit kürzen.

## Session-Logik für Check-Ketten

Die zentrale didaktische Regel lautet:

- Eine begonnene Check-Kette soll sichtbar weitergehen.
- Sie soll aber nicht sofort komplett durchlaufen.
- Zwischen zwei Folgeaktivitäten derselben oder verschiedener Check-Ketten dürfen daher einige frische `training_1`-Einträge liegen, aber nicht zu viele.

Aktuell wird das so umgesetzt:

- Offene Check-Schritte werden zunächst in zwei Gruppen getrennt:
  - frische Starts mit `training`
  - Folgeaktivitäten mit `recall`, `feynman`, `kompetenzliste_gate`
- Die Gruppe der Folgeaktivitäten wird nicht einfach komplett nach vorne gezogen.
- Stattdessen gilt `feed.session_follow_up_max_gap` als Obergrenze für frische `training`-Einträge zwischen zwei Folgeaktivitäten.
- Dieser Abstand ist absichtlich keine starre Blockgröße.
- Wenn vorne `training`-Einträge verschwinden, schrumpft der tatsächliche Abstand dynamisch, damit wartende Folgeaktivitäten nach vorne rücken können.
- Tiefere frische `training`-Einträge füllen verbrauchte Plätze vor älteren Follow-ups nicht wieder auf.

Fachliche Konsequenz:

- `recall` oder `feynman` sollen nicht erst ganz am Ende vieler neuer Checks auftauchen.
- Gleichzeitig soll eine einzelne Check-Kette nicht sofort `training → recall → feynman` am Stück durchlaufen.

## Queue-Logik für Session und Retention

Wenn gleichzeitig Session-Einträge und Retention-Einträge vorliegen, wird ein gemeinsamer Feed-Kopf gebaut.

Dabei gilt ein zentraler Schalter:

- `feed.retention_new_item_position`

Bedeutung:

- Neue oder neu sichtbare Retention-Einträge steigen an dieser sichtbaren Position in den Feed ein.
- Mit dem aktuellen Default `5` erscheint eine neue Retention also zunächst auf Platz 5.
- Werden Feed-Aktivitäten vor ihr abgeschlossen, rutscht dieselbe Retention bei der nächsten Projektion entsprechend nach oben.
- Bereits fällige Retention-Einträge können dadurch mit wachsender Wartezeit weiter nach oben rücken; sie kleben nicht an einem festen Slot.
- Checkbezogene Folgeaktivitäten `recall`, `feynman` und `kompetenzliste` dürfen eine sichtbare Retention trotzdem überholen, wenn sie sonst aus ihrem zulässigen Follow-up-Fenster fallen würden.
- Es gibt keinen festen Lead-/Stride-Interleave mehr.

Wichtig für Session-Neustarts:

- Bereits fällige Retention-Flashcards aus früheren Sessions bleiben auch dann sichtbar, wenn eine neue Core-Session gestartet wird.
- Neu aus einer Session entstehende Retention-Scopes werden sofort im Feed-Kopf angekündigt, auch wenn ihr serverseitiger Wiederholungsabstand noch nicht vollständig abgelaufen ist.
- Für diese frühe Sichtbarkeit bleibt der eigentliche Startpfad serverseitig getrennt: Vor dem Fälligkeitszeitpunkt wird Retention nur dort früh gestartet, wo der Feed das ausdrücklich erlaubt.

## Deterministische Reihenfolge

Die Feed-Reihenfolge wird nicht mehr lokal pro Browser-Tab nachstabilisiert.

- Dashboard, Sidebar und Feed-Kontext lesen dieselbe fachlich berechnete Reihenfolge.
- Zwei Tabs mit derselben Session sollen deshalb dieselbe sichtbare Feed-Reihenfolge zeigen.
- Lokaler Browser-State darf die fachliche Reihenfolge nicht mehr umsortieren.

## Aktuelle Systemwerte

Die Feed-Logik nutzt aktuell diese relevanten Schlüssel in `public.system_settings`:

- `feed.dashboard_item_limit`
  - maximale Zahl sichtbarer Feed-Einträge im Dashboard
- `feed.retention_activity_base_gap`
  - serverseitiger Basisabstand für user-scoped Retention-Scopes; die Wiedereinblendung einer erledigten Retention wächst als `N`, `2N`, `3N`, ... abgeschlossene Feed-Aktivitäten
- `feed.retention_new_item_position`
  - sichtbare Einstiegsposition neuer oder neu sichtbarer Retention-Einträge im Feed-Kopf
- `feed.session_follow_up_max_gap`
  - Obergrenze frischer `training`-Einträge zwischen zwei Folgeaktivitäten laufender Check-Ketten

## Beispiel 1: Session-Folgeaktivitäten

Beispielhafte sichtbare Session-Liste:

1. Check 6 Training
2. Check 7 Training
3. Check 8 Training
4. Check 1 Recall
5. Check 9 Training

Wenn `Check 6 Training` abgeschlossen wird, soll `Check 1 Recall` nicht starr auf Platz 4 kleben.
Die aktuelle Logik versucht deshalb, verbleibende sichtbare Einträge nach oben rücken zu lassen und den Recall-Abstand nur als Obergrenze zu behandeln.

## Beispiel 2: Retention im Feed-Kopf

Bei aktiver Session und einer neu sichtbaren Retention mit Default-Wert `5` ist ein typischer Anfang:

1. Start oder Session-Aktivität
2. Check 1 Training
3. Check 2 Training
4. Check 3 Training
5. Retention X
6. Check 4 Training

Wird danach eine der Positionen 1 bis 4 abgeschlossen, rutscht `Retention X` in der nächsten Projektion um einen Platz nach oben.

Beispiel nach einem abgeschlossenen Eintrag davor:

1. Check 1 Training
2. Check 2 Training
3. Check 3 Training
4. Retention X
5. Check 4 Training

Falls an dieser Stelle ein älterer `recall`-, `feynman`- oder `kompetenzliste`-Schritt wegen `feed.session_follow_up_max_gap` weiter nach vorne gezogen werden muss, darf dieser Schritt vor `Retention X` landen.

## Nicht in dieser Datei pflegen

Damit die Doku nicht doppelt läuft, gehört Folgendes bewusst nicht hierher:

- Tabellenfelder, Constraints, Trigger und RPC-Details
- Supabase-Deploy- oder Betriebsanweisungen
- die allgemeine Trennung von Repo-Content und Datenbank als Architekturprinzip
- größere Zielbilder jenseits des aktuell wirksamen Feed-Verhaltens

Diese Punkte bleiben in den bereits vorhandenen Dokus.