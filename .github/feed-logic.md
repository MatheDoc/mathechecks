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
- fällige Retention-Scopes und Retention-Fallbacks für Flashcards
- Repo-Metadaten aus `checks.json` und den Lernbereichs-Daten

## Verarbeitungsreihenfolge

Die Feed-Projektion läuft in dieser Reihenfolge:

1. Aktive Core-Session laden.
2. Zentrale Systemwerte aus `public.system_settings` laden.
3. Falls eine aktive Session existiert:
   - offene Check-Schritte laden
   - offene Session-Aktivitäten laden
   - fällige Retention-Einträge für dieselbe Nutzerin oder denselben Nutzer laden
4. Check-Schritte innerhalb der Session ordnen.
5. Session-Aktivitäten und geordnete Check-Schritte zu einer Session-Liste zusammenbauen.
6. Retention-Einträge in die Session-Liste einmischen.
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

Fachliche Konsequenz:

- `recall` oder `feynman` sollen nicht erst ganz am Ende vieler neuer Checks auftauchen.
- Gleichzeitig soll eine einzelne Check-Kette nicht sofort `training → recall → feynman` am Stück durchlaufen.

## Hybrid-Logik für Session und Retention

Wenn gleichzeitig Session-Einträge und Retention-Einträge vorliegen, wird ein Hybrid-Feed gebaut.

Dabei gelten zwei getrennte Schalter:

- `feed.retention_interleave_lead_session_items`
- `feed.retention_interleave_stride`

Bedeutung:

- `feed.retention_interleave_lead_session_items` bestimmt, wie viele Session-Einträge vor dem ersten Retention-Slot kommen.
- Dieser Wert wirkt nur einmal am Anfang des gemischten Feeds.
- `feed.retention_interleave_stride` bestimmt, wie viele Session-Einträge nach einer Retention-Karte folgen, bevor die nächste Retention-Karte auftaucht.
- Dieser Wert ist kein Mindestwert und auch kein serverseitiger Freigabeabstand, sondern die Ziel-Dichte der sichtbaren Mischung.

Mit den aktuellen Defaults bedeutet das:

- zuerst 5 Session-Einträge
- danach typischerweise 1 Retention auf etwa 5 Gesamteinträge, also 1 Retention plus 4 Session-Einträge im laufenden Muster

Wichtig für Session-Neustarts:

- Bereits zeitfällige Retention-Flashcards aus früheren Sessions bleiben auch dann im Retention-Teil des Hybrid-Feeds, wenn eine neue Core-Session gestartet wird.
- Der Aktivitätszähler steuert zusätzliche Retention-Freigaben, setzt aber eine schon fällige Retention nicht erneut nach hinten.
- Praktisch heißt das: Neue Session vorne, aber alte fällige Flashcards fallen nicht mehr komplett aus dem sichtbaren Mischmodell heraus.

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
  - serverseitiger Aktivitätsabstand für user-scoped Retention-Scopes
- `feed.retention_interleave_lead_session_items`
  - Session-Einträge vor dem ersten Retention-Slot im Hybrid-Feed
- `feed.retention_interleave_stride`
  - weitere Session-Einträge zwischen zwei Retention-Slots im Hybrid-Feed
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

## Beispiel 2: Retention im Hybrid-Feed

Bei aktiver Session und gleichzeitig fälliger Retention bedeutet das aktuelle 5er-Paket:

- Session bleibt klar vorne.
- Die erste Retention taucht erst nach mehreren Session-Aktivitäten auf.
- Danach erscheint Retention sichtbar, aber nicht in jedem zweiten Slot.

Typisch ist daher eher ein Muster wie:

1. Session
2. Session
3. Session
4. Session
5. Session
6. Retention
7. Session
8. Session
9. Session
10. Session
11. Retention

Die tatsächliche Liste kann durch das Ende einer Gruppe leicht abweichen.

## Nicht in dieser Datei pflegen

Damit die Doku nicht doppelt läuft, gehört Folgendes bewusst nicht hierher:

- Tabellenfelder, Constraints, Trigger und RPC-Details
- Supabase-Deploy- oder Betriebsanweisungen
- die allgemeine Trennung von Repo-Content und Datenbank als Architekturprinzip
- größere Zielbilder jenseits des aktuell wirksamen Feed-Verhaltens

Diese Punkte bleiben in den bereits vorhandenen Dokus.