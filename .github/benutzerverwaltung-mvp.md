# Benutzerverwaltung & Session-MVP

Stand: Mai 2026

Diese Datei beschreibt die erste persistente Plattform-Stufe für MatheChecks, den aktuellen checkbezogenen Feed-Schnitt und die additive v2-Grundlage für Planungsziel, Freigabelimits und Retention nach Ende einer Core-Session.
Sie umfasst Benutzer, Profile, Lern-Sessions, `session_check_state` als erste Check-Pipeline-Projektion, additive Planungsparameter und schlanke Fortschrittsschreibpfade für Training, Recall, Feynman und Flashcards.

## Dokumentgrenzen

- Diese Datei beschreibt fachliches Zielbild, Datenmodell, Sicherheitsmodell und MVP-Scope.
- `.github/feed-v2-core-spec.md` ist die kanonische Feed-Zieldoku; diese Datei trägt dafür nur die additive Datenmodell- und Migrationssicht.
- `supabase/README.md` dokumentiert dagegen CLI-Workflow, lokales vs. gehostetes Setup, Dashboard-Schritte und SMTP.
- Die Trennung ist bewusst sinnvoll: Architektur und Betriebs-Runbook ändern sich oft in unterschiedlichem Tempo.

## Zielbild

- Nutzer können sich über einen E-Mail-Link oder externe Provider anmelden und registrieren.
- Jeder Nutzer hat genau eine Auth-Identität und ein minimales anwendungsseitiges Profil.
- Nutzer können eine zeitlich begrenzte Core-Session mit Zielhorizont starten und verwalten.
- Checkbezogene Feed-Schritte können in einer ersten Pipeline serverseitig weitergeschaltet werden.
- Neue Feed-Aktivitäten werden perspektivisch über explizite Freigaben statt über eine starre Menge offener Aufgaben pro Tag begrenzt.
- Explizite Recall-/Feynman-Abschlüsse werden zusätzlich als minimale Aktivitätsversuche gespeichert.
- Flashcards können nach Abschluss einer Core-Session als Retention-Track weiterlaufen, ohne dass die Core-Session künstlich offen bleiben muss.
- Lerninhalte bleiben vollständig im Repo; die Datenbank speichert nur nutzerbezogene Persistenz.
- Vollständiger generischer Feed, Trainings- und Fragehistorie auf Aufgabenniveau, Lehrer-/Klassenlogik und soziale Funktionen sind nicht Teil dieses MVP.

## Empfehlung

Für diesen MVP ist Supabase die naheliegende Wahl.

Gründe:

- Das künftige Modell ist relational: Benutzer, Profil, Lern-Session, Session-Umfang und später Zustands- oder Feed-Projektionen.
- Supabase kombiniert Auth, Postgres und Row Level Security in einer Form, die direkt zu einem statischen Jekyll-Frontend passt.
- Besitzregeln wie „ein Benutzer sieht nur seine Daten" oder „pro Benutzer höchstens eine aktive Lern-Session" lassen sich in Postgres robuster ausdrücken als in einer dokumentbasierten Struktur.
- Der spätere Ausbau zu Check-State, Feed-Projektionen, Versuchen oder Admin-Auswertungen bleibt ohne Modellbruch möglich.

## Boardmittel von Supabase, die im MVP genutzt werden sollten

- E-Mail-Link für Anmeldung und Registrierung
- OAuth-Anmeldung über konfigurierte externe Provider, aktuell Google und Apple
- Login und Logout
- Passwortänderung im angemeldeten Konto
- Session-Handling und JWTs
- Row Level Security für Datenzugriffe aus dem Browser

Hinweis:
Für Produktion sollte ein eigenes SMTP-Setup verwendet werden. Der eingebaute Mailversand reicht eher für Test und frühe Entwicklung.

## Umsetzungsprinzip im Repo

- Datenbankschema, Policies, Trigger und RPCs werden versioniert im Repo gepflegt.
- Die erste MVP-Migration liegt unter `supabase/migrations/20260514170000_benutzerverwaltung_mvp.sql`.
- Der lokale Workflow ist in `supabase/README.md` beschrieben.
- Das Supabase-Dashboard bleibt für Projekt-Setup, Auth-Einstellungen, Redirect-URLs, SMTP und Laufzeitinspektion relevant.
- Schreibende Browserzugriffe laufen im MVP bewusst über wenige RPCs statt über freie Tabellen-CRUDs.
- Die aktuelle Auth-Oberfläche läuft über `konto.html`; dieselbe Seite dient auch als Ziel für E-Mail-Link-, OAuth- und Recovery-Redirects.

## Aktueller Umsetzungsstand

- Die erste Migration für Benutzerverwaltung und Lern-Sessions ist im Remote-Projekt bereits aktiv.
- Die Folge-Migration für den schlanken Session-Schreibpfad über `save_active_learning_session(...)` ist im Remote-Projekt bereits aktiv.
- Die Migration für `learning_activity_attempts` ergänzt einen ersten Fortschrittsschreibpfad für Recall und Feynman.
- Die Migration `session_check_state_v1` führt eine materialisierte Check-Pipeline ein und erweitert `save_active_learning_session(...)` um die synchronisierten Check-Zeilen.
- `complete_current_training_step(...)` bildet den manuellen Feed-Abschluss von `training` ab.
- `record_check_module_attempt(...)` schreibt Recall-/Feynman-Versuche; im aktuellen Frontend bewegen erfolgreiche Abschlüsse die Check-Pipeline nur aus dem Feed-Kontext weiter.
- Die Flashcards-Folge-Migration führt `session_activity_state` als erste lernbereichsweite Feed-Projektion ein; inzwischen trägt sie `start` als direkte Einstiegsaktivität pro Lernbereich und `flashcards` als persistente Wiederholungsaktivität.
- `get_or_create_flashcard_round(...)`, `record_flashcard_review(...)` und `resolve_flashcard_round(...)` bilden den session-scoped Feed-Schreibpfad für Flashcards ab.
- `complete_start_activity(...)` schließt die einmalige Start-Aktivität eines Lernbereichs innerhalb der aktiven Session ab und erhöht dabei den user-scoped Feed-Aktivitätszähler.
- `get_or_create_retention_flashcard_round(...)`, `record_retention_flashcard_review(...)` und `resolve_retention_flashcard_round(...)` ergänzen den user-scoped Retention-Schreibpfad nach Session-Ende.
- `complete_kompetenzliste_gate(...)` schließt den letzten checkbezogenen Kompetenzlisten-Schritt ab und beendet die aktive Core-Session automatisch, sobald kein Check mehr offen ist.
- E-Mail-/Passwort-Anmeldung, Registrierung, OAuth-Anmeldung, Logout, Passwortänderung und Kontolöschung laufen aktuell über Supabase Auth, RPCs und `konto.html`.
- `delete_current_user_account(...)` löscht nach expliziter Bestätigung den aktuellen Auth-User; abhängige Plattformdaten werden über bestehende `on delete cascade`-Beziehungen entfernt.
- Der Recovery-Link führt derzeit zurück auf `konto.html`, wo der Nutzer ein neues Passwort setzt.
- Das Session-Modal im Dashboard kann ein explizites `target_date` speichern; die Session-Box zeigt dieses Datum anschließend zusammen mit einer groben Heuristik auf Basis der noch offenen Check-Schritte.
- Das Dashboard trennt im UI zwischen `Session` und `Feed`: Die Session verwaltet die aktive Core-Session, der Feed bündelt Empfehlungen aus der aktiven Session und aus Wiederholungen.
- Die Feed-Projektion zeigt im Dashboard aktuell genau ein aktuelles Element, priorisiert offene `start`-Aktivitäten und sonst serverseitig freigegebene Check-Schritte mit materialisierten Zeitfenstern; aktive oder fällige Retention-Flashcards aus früheren Sessions bleiben ein Fallback, wenn keine Session-Aktivität sichtbar ist.
- Ein `Nein, zum Dashboard` im Feed ändert den Aktivitätszustand nicht persistent; die Aktivität bleibt offen und erscheint in ihrer normalen fachlichen Reihenfolge weiter.
- Dashboard und Sidebar lesen inzwischen dieselbe Feed-Projektion; die Feed-Shell und eine gemeinsame Feed-Aktionsschicht sind für `start`, `training`, `recall`, `feynman`, `kompetenzliste` und `flashcards` umgesetzt.
- Das Dashboard ergänzt dazu eine eigene Box `Abgeschlossen`, die vollständig bestätigte Lernbereiche auch nach Ende der zugehörigen Session aus bestehenden Check-State-Zeilen und Retention-Bezügen ableitet.
- Die v2-Grundlage ergänzt additive Planungsparameter an `learning_sessions`, `last_completed_at` an `session_check_state` und user-scoped Retention-Tabellen für Flashcards.
- Für den ersten Core-Feed-V2-Umbau ist die kleinste additive Richtung derzeit: `start` zunächst in `session_activity_state` belassen, checkbezogene Zeitfenster an `session_check_state` ergänzen und einen separaten session-scoped Feed-Cursor einführen. Retention bleibt in diesem ersten Umbau ausdrücklich außen vor.
- Zentrale Systemwerte werden in `public.system_settings` mit Integer-Wert und Kurzbeschreibung gepflegt; dazu gehören aktuell Core-Gap für didaktische Folgeaktivitäten, Retention-Abstand, Retention-Einstiegsposition und Default-Tempo.

## Additive V2-Richtung

Für den anstehenden Core-Feed-V2-Umbau soll das Datenmodell nicht neu erfunden, sondern entlang der bestehenden Projektionen erweitert werden.

- `session_check_state` bleibt die checkbezogene Pipeline-Projektion und wird um materialisierte Zeitfenster für checkbezogene Schritte erweitert.
- `session_activity_state` bleibt im ersten V2-Schnitt Träger von `start`; eine spätere Zusammenführung in ein gemeinsames Schrittmodell bleibt offen.
- Eine neue session-scoped Projektion `session_feed_cursor` trägt `current_activity_key`, `locked_until`, `selected_at` und `selection_reason`.
- Checkbezogene Rohversuche außerhalb des Feed-Kontexts dürfen im Core-Feed-V2 keinen Feed-Schritt abschließen; die eigentliche Pipeline-Bewegung wandert in einen cursor-validierten Feed-Abschluss.
- Retention bleibt im ersten Core-Feed-V2-Umbau außerhalb des neuen Core-Read-Pfads und wird erst nach stabilem Cursor- und Zeitfenster-Modell wieder angebunden.

## Begriffstrennung

- **Auth-Session:** Technische Login-Session von Supabase Auth mit Token und Ablaufzeit.
- **Lern-Session / Core-Session:** Fachliches Objekt von MatheChecks; endlicher Kernplan eines Benutzers mit Zielhorizont und Freigabeparametern.

Weitere Trennung für den aktuellen und nächsten Ausbauschritt:

- **Lernaktivität / Versuch:** Append-only Rohdaten eines expliziten Modulabschlusses, zum Beispiel `recall` oder `feynman` mit `can_do` oder `repeat`.
- **Check-Status:** Materialisierte Zustandsprojektion pro Check in `session_check_state`; wird nicht direkt per Tabellen-CRUD vom Frontend geschrieben.
- **Feed:** UI-nahe Projektion offener nächster Aktionen; in v1 aus checkbezogenen Schritten in `session_check_state`, `start`/Flashcards in `session_activity_state`, user-scoped Retention-Scopes und Repo-Metadaten abgeleitet, später mit expliziten Freigaben und Aktivitätsfenstern.
- **Feed-Aktivität:** Konkreter Bearbeitungskontext einer Feed-Karte, im Frontend über `activity_key`, `activity_step` und `activity_run` transportiert.
- **Feed-Cursor:** Session-scoped Persistenz des aktuell ausgewählten Core-Feed-Elements mit Lock-Information und Auswahlgrund.
- **Feed-Abschluss:** Serverseitig validierte Entscheidung auf die aktuelle Feed-Aktivität; nur mit gültigem Feed-Cursor darf dadurch die Check-Pipeline weiterbewegt werden.
- **Retention-Track:** Nutzerweite Wiederholungsschicht jenseits der endlichen Core-Session; aktuell fachlich auf Flashcards begrenzt.

Diese Begriffe dürfen weder in UI noch im Datenmodell vermischt werden.

## Source of Truth

- Repo: Lernbereiche, Checks, Modultexte, Aufgabenpools, fachliche Metadaten
- Datenbank: Identität, Profil, Lern-Sessions und nutzerbezogene Session-Konfiguration

Die Datenbank speichert im MVP keine Kopien von `checks.json`, Lernbereichstexten oder Aufgaben-JSONs.

## Minimales Datenmodell

### 1. `auth.users` (Supabase)

Verantwortung:
Authentifizierung, Credentials, E-Mail-Status, technische Login-Identität.

Bemerkung:
Diese Tabelle wird nicht durch Anwendungscode direkt gepflegt, sondern durch Supabase Auth.

### 2. `public.profiles`

Zweck:
Anwendungsseitige Ergänzung zur Auth-Identität.

Vorgeschlagene Felder:

- `user_id uuid primary key references auth.users(id) on delete cascade`
- `display_name text null`
- `role text not null default 'user'`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Regeln:

- Im MVP reichen `user` und optional `admin`.
- Rollen sind kein frei editierbares Nutzerprofilfeld im Frontend.
- Die Profilzeile sollte automatisch bei neuer Auth-Identität erzeugt werden, idealerweise per Datenbank-Trigger.

### 3. `public.learning_sessions`

Zweck:
Fachliche Lern-Sessions eines Benutzers.

Vorgeschlagene Felder:

- `id uuid primary key default gen_random_uuid()`
- `user_id uuid not null references auth.users(id) on delete cascade`
- `status text not null check (status in ('active', 'completed', 'aborted'))`
- `activities_per_day numeric(6,2) not null` — materialisierte Session-Geschwindigkeit in Aktivitäten pro Tag
- `target_date date null`
- `target_source text null check (target_source in ('explicit', 'suggested'))`
- `planning_timezone text not null default 'Europe/Berlin'`
- `daily_new_release_limit integer not null default 3`
- `max_parallel_check_streams integer not null default 4`
- `planning_revision integer not null default 1`
- `started_at timestamptz not null default now()`
- `ended_at timestamptz null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Regeln:

- Pro Benutzer höchstens eine aktive Lern-Session.
- Das sollte über einen partiellen Unique Index erzwungen werden, nicht nur in der UI.
- Eine abgeschlossene oder abgebrochene Session bleibt aus Nachvollziehbarkeitsgründen erhalten.
- `target_date` ist der kanonische Zielwert, unabhängig davon, ob der Nutzer ihn direkt oder über „in X Tagen" gesetzt hat.
- Ohne separate Pace-UI setzt das System `activities_per_day` nicht frei durch den Nutzer, sondern serverseitig.
- Bei `target_source = 'explicit'` wird zusätzlich `required_activities_per_day` aus verbleibender Session-Last und `target_date` abgeleitet.
- Bei `target_source is null` oder `target_source = 'suggested'` bleibt `activities_per_day = planning.default_activities_per_day`.
- `daily_new_release_limit` begrenzt neue Freigaben pro Tag, nicht die Gesamtzahl bereits offener Aktivitäten.
- `planning_revision` steigt bei Änderungen an der aktiven Session, ohne vergangene Abschlüsse umzuschreiben.

### 4. `public.session_lernbereiche`

Zweck:
Welche Lernbereiche zu einer Lern-Session gehören.

Felder:

- `session_id uuid not null references public.learning_sessions(id) on delete cascade`
- `lernbereich_slug text not null`
- `sort_index integer not null default 0` — didaktische Reihenfolge innerhalb eines Gebiets; identische Werte starten gleichzeitig
- `gebiet text not null default ''` — Gebiet des Lernbereichs (z. B. `analysis`); `''` bedeutet keine Sequenzierung
- `created_at timestamptz not null default now()`

Schlüssel:

- `primary key (session_id, lernbereich_slug)`

Bemerkung:

- `lernbereich_slug` referenziert bewusst auf Repo-Content, nicht auf eine eigene Content-Tabelle in der Datenbank.
- `sort_index` und `gebiet` kommen aus `lernbereiche.yml` (`didactic_order`) und werden vom Frontend beim Speichern der Session übergeben.
- Lernbereiche verschiedener Gebiete laufen vollständig parallel; die Reihenfolge gilt nur innerhalb desselben Gebiets.

### 4a. `public.system_settings`

Zweck:
Zentrale Stelle für globale Systemwerte, die Frontend und serverseitige Feed-/Planungslogik gemeinsam verwenden.

Aktuelle Schlüssel:

- `planning.default_activities_per_day`
- `feed.core_gap_very_tight_hours`
- `feed.core_gap_tight_hours`
- `feed.core_gap_normal_hours`
- `feed.core_gap_relaxed_hours`
- `feed.core_gap_very_relaxed_hours`
- `feed.pressure_very_tight_threshold`
- `feed.pressure_tight_threshold`
- `feed.pressure_relaxed_threshold`
- `feed.pressure_very_relaxed_threshold`
- `feed.retention_activity_base_gap`
- `feed.retention_new_item_position`

Die `feed.core_gap_*_hours`-Werte definieren die fünf serverseitigen `G`-Profile für neue didaktische Übergänge. Welche Stufe gezogen wird, entscheidet das Druckverhältnis aus `activities_per_day` und `required_activities_per_day`. `available_from` und `overdue_from` liegen dazu bereits in `session_check_state`; `planned_from` und der eigentliche Feed-Cursor bleiben nächste V2-Schritte.

`feed.retention_activity_base_gap` steuert für Retention-Scopes sowohl den ersten serverseitigen Due-Abstand `N` als auch die weiteren linearen Wiederkehr-Abstände `2N`, `3N`, `4N`, ... nach abgeschlossenen Retention-Runden.

### 4b. `public.user_feed_activity_counters`

Zweck:
User-scoped Zähler für abgeschlossene Feed-Aktivitäten. Die Tabelle liefert serverseitige Referenzwerte für Retention-Abstände und andere feedweite Freigabelogik.

Gezählt werden aktuell abgeschlossene `start`-, `training`-, erfolgreiche `recall`-/`feynman`-, `kompetenzliste`- und abgeschlossene Retention-Aktivitäten.

Aktuelle Felder:

- `user_id uuid not null references auth.users(id) on delete cascade`
- `completed_activity_count bigint not null default 0`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Regeln:

- Primärschlüssel ist `user_id`.
- `completed_activity_count` steigt nur über serverseitige Abschlusslogik, nicht über Tabellen-CRUD aus dem Frontend.
- Der Zähler ist bewusst klein und integerbasiert gehalten und bleibt von sichtbaren Listenplätzen entkoppelt.
- Die Werte sind bewusst klein und integerbasiert gehalten.
- Jeder Schlüssel trägt zusätzlich eine Kurzbeschreibung direkt in der Tabelle.
- Änderungen an diesen Werten sollen zukünftige Feed- und Planungseffekte steuern, ohne Suchläufe durch mehrere Frontend-Dateien oder SQL-Funktionen zu erzwingen.

### 5. `public.session_check_exclusions`

Zweck:
Optionale Ausschlüsse einzelner Checks innerhalb einer Lern-Session.

Vorgeschlagene Felder:

- `session_id uuid not null references public.learning_sessions(id) on delete cascade`
- `check_id text not null`
- `created_at timestamptz not null default now()`

Schlüssel:

- `primary key (session_id, check_id)`

Bemerkung:

- Das ist für den MVP schlanker als eine vollständige Tabelle aller Session-Checks.
- Der effektive Session-Umfang ergibt sich aus ausgewählten Lernbereichen minus ausgeschlossenen Checks.
- Ausschlüsse werden dabei über stabile `check_id`-Werte aus `checks.json` gespeichert, nicht über Anzeige- oder Kompetenztexte.

### 6. `public.learning_activity_attempts`

Zweck:
Append-only Log für explizite Recall-/Feynman-Abschlussentscheidungen. Der Log bleibt Rohdatenquelle; `session_check_state` ist die dazugehörige aktuelle Projektion.

Vorgeschlagene Felder:

- `id uuid primary key default gen_random_uuid()`
- `user_id uuid not null references auth.users(id) on delete cascade`
- `session_id uuid null references public.learning_sessions(id) on delete set null`
- `lernbereich_slug text not null`
- `check_id text null`
- `module_key text not null`
- `outcome_key text not null`
- `created_at timestamptz not null default now()`

Regeln:

- Der erste Schnitt umfasst bewusst nur `recall` und `feynman`; Training wird in v1 nicht als `learning_activity_attempt` gespeichert.
- Jeder Klick auf `Kann ich` oder `Wiederholen/noch nicht` erzeugt einen eigenen Versuch.
- `session_id` wird nur gesetzt, wenn der Abschluss in den Umfang der aktuellen aktiven Lern-Session fällt.
- Das Frontend schreibt nur diesen Rohversuch; passende Check-Zustände werden serverseitig in derselben RPC weiterbewegt.

### 7. `public.session_check_state`

Zweck:
Materialisierte Projektion des aktuellen checkbezogenen Feed-Schritts pro Check in einer aktiven Lern-Session.

Felder:

- `session_id uuid not null references public.learning_sessions(id) on delete cascade`
- `check_id text not null`
- `current_step_key text not null`
- `current_step_status text not null`
- `last_outcome_key text null`
- `last_completed_at timestamptz null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Schlüssel:

- `primary key (session_id, check_id)`

Aktuelle Werte für `current_step_key`:

- `training`
- `recall`
- `feynman`
- `kompetenzliste_gate`
- `check_completed`

Aktuelle Werte für `current_step_status`:

- `blocked`
- `due`
- `completed`

Regeln:

- Beim Speichern der aktiven Session synchronisiert `save_active_learning_session(...)` die Zeilen aus den im Frontend aufgelösten enthaltenen Checks.
- Neue Zeilen starten in v1 mit `training` und `due`.
- Nicht mehr enthaltene Checks werden aus der aktiven Session-Projektion entfernt.
- Das Frontend darf `session_check_state` lesen, aber nicht direkt schreiben.
- `last_completed_at` materialisiert den tatsächlichen Abschlusszeitpunkt des zuletzt erfolgreich abgeschlossenen Vorgängerschritts; spätere Nachfolgefenster sollen darauf aufbauen, nicht auf bloß geplanten Fälligkeiten.

### 8. `public.session_activity_state`

Zweck:
Materialisierte Projektion für nicht checkbezogene Feed-Aktivitäten. Aktuell wird sie auf Lernbereichsebene für `start` und `flashcards` genutzt.

Felder:

- `session_id uuid not null references public.learning_sessions(id) on delete cascade`
- `activity_key text not null`
- `activity_type text not null`
- `scope_type text not null`
- `lernbereich_slug text null`
- `check_id text null`
- `target_module_key text not null`
- `status text not null`
- `due_at timestamptz not null default now()`
- `sort_bucket integer not null default 50`
- `sort_index integer not null default 0`
- `last_outcome_key text null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Schlüssel:

- `primary key (session_id, activity_key)`

Aktuelle Werte:

- `activity_type in ('start', 'flashcards')`
- `scope_type = 'lernbereich'`
- `target_module_key` verweist aktuell auf `start` oder `flashcards`
- `status in ('blocked', 'due', 'completed')`

Regeln:

- `start` wird pro Lernbereich unmittelbar beim Speichern oder Erweitern einer aktiven Session fällig und genau einmal pro Session abgeschlossen.
- Flashcards werden fällig, wenn alle ausgewählten Checks eines Lernbereichs mindestens `kompetenzliste_gate` erreicht haben.
- Ausgeschlossene Checks werden beim Fälligkeitscheck und beim Kartenpool ignoriert.
- Das Frontend liest die Projektion, schreibt sie aber nicht direkt.

### 9. Flashcard-Zustand

Zweck:
Serverseitige Wiederholungslogik für Flashcards innerhalb einer aktiven Lern-Session plus additive user-scoped Retention-Grundlage nach Ende der Core-Session.

Tabellen:

- `session_flashcard_card_state`: Kartenstand pro Session, Lernbereich und Karte mit Level, nächster Fälligkeit, letzter Bewertung und Zähler.
- `session_flashcard_rounds`: ein aktiver oder abgeschlossener Durchgang pro Lernbereich.
- `session_flashcard_round_cards`: stabile Kartenliste eines Durchgangs mit Aufgabenindex und Bewertung.
- `user_retention_scopes`: user-scoped Retention-Scope pro Lernbereich mit Status `active`, `paused` oder `opted_out`; `feed_queue_entry_activity_count` verankert neu sichtbare Retention-Einträge im Feed-Kopf.
- `retention_flashcard_card_state`: user-scoped Kartenfälligkeit für Flashcards jenseits der Core-Session.
- `retention_flashcard_rounds`: user-scoped Retention-Durchgänge für fällige Flashcards nach Ende der Core-Session.
- `retention_flashcard_round_cards`: stabile Kartenliste eines Retention-Durchgangs mit Bewertung.

Schreibpfade:

- `get_or_create_flashcard_round(...)` erzeugt oder liest den aktiven 20-Karten-Durchgang.
- `record_flashcard_review(...)` speichert eine Kartenbewertung.
- `resolve_flashcard_round(...)` schließt den Durchgang ab oder hält Flashcards sofort fällig.
- `finish_learning_session(..., 'completed')` überführt bestehende Flashcard-Zustände zusätzlich in die user-scoped Retention-Grundlage.
- `get_or_create_retention_flashcard_round(...)`, `record_retention_flashcard_review(...)` und `resolve_retention_flashcard_round(...)` bilden denselben Durchgangspfad user-scoped für den Retention-Track ab.
- `set_retention_scope_status(...)` erlaubt späteres Pausieren oder explizites Entfernen eines Flashcard-Retention-Scopes.

## Nicht Teil dieses MVP-Datenmodells

- `feed_events`
- Trainings- und Fragenversuche auf Aufgabenebene
- Antwort- oder Fragenhistorie
- Klassen, Kurse, Lehrkräfte, Freigaben
- öffentliche Profile

Diese Objekte können später ergänzt werden, ohne das Grundmodell zu brechen.

## Minimale Schreibflüsse

### E-Mail-/Passwort-Anmeldung und Registrierung

1. Frontend zeigt auf `konto.html` einen Login-Modus und einen separaten Registrierungsmodus.
2. Bestehende Nutzer melden sich über `supabase.auth.signInWithPassword(...)` an.
3. Neue Nutzer werden über `supabase.auth.signUp(...)` mit E-Mail, Passwort und optionalem `display_name` registriert.
4. Nach Anlage des Auth-Benutzers wird automatisch ein `profiles`-Datensatz erzeugt.
5. In der aktuellen Hosted-Konfiguration ist die E-Mail-Bestätigung deaktiviert, damit neue Nutzer nach der Registrierung sofort angemeldet sind.
6. Falls diese Bestätigung später wieder aktiviert wird, brauchen Registrierung und Recovery wieder eine funktionierende Mailzustellung.

### OAuth-Login

1. Frontend liest die aktivierten Provider aus `supabase_oauth_providers`.
2. Nutzer wählt einen externen Provider wie Google oder Apple.
3. Frontend ruft `supabase.auth.signInWithOAuth(...)` mit Redirect zurück auf `konto.html` auf.
4. Supabase verknüpft die externe Identität mit `auth.users` und erzeugt wie bei E-Mail-Registrierung das Profil über den bestehenden Trigger.
5. Provider-Secrets und Provider-Aktivierung liegen im Supabase-Dashboard, nicht im Repo.

### Passwort ändern und Recovery

1. Angemeldete Nutzer können auf `konto.html` ein neues Passwort setzen.
2. Bestehende Recovery-Redirects landen weiterhin auf `konto.html` im Recovery-Modus.
3. Dort setzt der Nutzer das neue Passwort über Supabase Auth.

### Konto löschen

1. Frontend verlangt die Bestätigung `LÖSCHEN`.
2. Frontend ruft `delete_current_user_account(...)` auf.
3. Die RPC löscht den aktuellen Eintrag in `auth.users`.
4. `profiles`, Lern-Sessions und abhängige Session-Projektionen werden über `on delete cascade` entfernt.
5. Das Frontend meldet den lokalen Auth-Client anschließend ab.

### Lern-Session speichern oder leeren

1. Nutzer wählt Lernbereiche und optional ausgeschlossene Checks; Tempo kann im ersten schlanken UI-Schritt implizit bei `1` bleiben.
2. Das Frontend löst aus `checks.json` die tatsächlich enthaltenen `check_id`-Werte auf und übergibt sie als `p_included_check_ids`.
3. `save_active_learning_session(...)` legt bei Bedarf eine aktive Lern-Session an oder ersetzt die Auswahl der bestehenden aktiven Session atomar.
4. Die RPC synchronisiert `session_lernbereiche`, `session_check_exclusions` und `session_check_state` in einem Schreibpfad.
5. Eine leere Lernbereichsauswahl räumt die aktive Lern-Session aus dem Weg, indem sie als `aborted` beendet wird.
6. `finish_learning_session(...)` bleibt für spätere explizite Abschlüsse oder Abbrüche bestehen.
7. Bei einer Änderung der aktiven Session steigt `planning_revision`; vergangene Abschlüsse bleiben unberührt, nur die Zukunftsplanung wird neu versioniert.

### Aktive Lern-Session löschen

1. Nutzer bestätigt im Dashboard das Löschen der aktiven Session.
2. `delete_active_learning_session()` markiert die aktive Session als `aborted` und entfernt zugehörige Projektionen über die bestehenden Cascades.
3. Das Dashboard lädt danach den leeren Session-Zustand neu.

### Training im Feed abschließen

1. Nutzer öffnet einen fälligen Trainingsschritt aus dem Feed.
2. Die Feed-Shell erlaubt den Abschluss erst nach Bearbeitung aller Teilfragen und nach `Abschluss vorbereiten`.
3. `complete_current_training_step(p_check_id)` bewegt `training -> recall`.
4. Dieser Abschluss ist ein manueller Feed-Abschluss, noch kein automatisierter fehlerfreier Trainingsnachweis.
5. Der tatsächliche Abschlusszeitpunkt wird in `session_check_state.last_completed_at` materialisiert.

### Recall- oder Feynman-Abschluss speichern

1. Nutzer bearbeitet einen Check in `recall` oder `feynman`.
2. Im Feed-Kontext bereitet die gemeinsame Feed-Shell den Abschluss vor; freie Modulaufrufe bleiben ohne Feed-Fortschritt.
3. Das Frontend ruft `record_check_module_attempt(...)` mit `lernbereich_slug`, `check_id`, `module_key` und `outcome_key` auf.
4. Die Datenbank verknüpft den Versuch optional mit der aktiven Lern-Session, wenn Lernbereich und Check in deren Umfang liegen.
5. Bei `can_do` bewegt die RPC passende `session_check_state`-Zeilen weiter und materialisiert den tatsächlichen Abschlusszeitpunkt; bei `repeat` bleibt derselbe Schritt fällig und nur `last_outcome_key` wird aktualisiert.

### Core-Session abschließen

1. Heute markiert primär das System die aktive Core-Session als `completed`, sobald der letzte offene Check über `complete_kompetenzliste_gate(...)` nach `check_completed` übergeht.
2. Die Session endet fachlich; `ended_at` wird gesetzt.
3. Aus den enthaltenen Lernbereichen werden additive `user_retention_scopes` für Flashcards abgeleitet und mit einem Queue-Anker für den sichtbaren Feed-Kopf versehen.
4. Bestehende session-scoped Flashcard-Kartenstände werden in `retention_flashcard_card_state` user-scoped übernommen.
5. Bereits `paused` oder `opted_out` gesetzte Retention-Scopes werden dabei nicht automatisch reaktiviert.

## MVP-RPCs

- `update_own_profile(p_display_name text)`
- `save_active_learning_session(p_lernbereiche text[], p_excluded_check_ids text[], p_activities_per_day numeric default null, p_included_check_ids text[] default array[]::text[], p_target_date date default null, p_target_source text default null, p_lernbereiche_meta jsonb default null)` — `p_lernbereiche_meta`: optionales JSON-Array `[{slug, gebiet, sort_index}, …]` für didaktische Reihenfolge; fehlt es, starten alle Checks als `due`
- `delete_active_learning_session()`
- `complete_start_activity(p_lernbereich_slug text)`
- `complete_current_training_step(p_check_id text)`
- `record_check_module_attempt(p_lernbereich_slug text, p_check_id text, p_module_key text, p_outcome_key text)`
- `complete_kompetenzliste_gate(p_check_id text)`
- `finish_learning_session(p_session_id uuid, p_status text)`
- `set_retention_scope_status(p_lernbereich_slug text, p_status text)`
- `delete_current_user_account()`

### Interne Hilfsfunktionen (kein direkter Nutzer-Grant)

- `unlock_successor_lernbereiche(p_session_id uuid, p_lernbereich_slug text)` — prüft nach einem erfolgreichen Recall, ob alle Checks der Prerequisite-Tier im selben Gebiet abgeschlossen sind, und schaltet die nächste Tier (`sort_index`-Stufe) frei; wird intern von `record_check_module_attempt` aufgerufen

## Minimale Leseflüsse

- Profil des eingeloggten Nutzers laden
- aktive Lern-Session des Nutzers laden
- zugehörige Lernbereiche und Check-Ausschlüsse laden, falls eine Session aktiv ist
- `session_check_state` und `session_activity_state` für die aktive Session lesen
- zusätzlich aktive `user_retention_scopes` und Retention-Fälligkeiten für Flashcards lesen
- bei Bedarf eigene Recall-/Feynman-Versuche lesen
- daraus im Frontend den effektiven Session-Umfang, Feed-Titel, die Queue-Reihenfolge sichtbarer Retention und Routingdaten gegen Repo-Content auflösen

## Stand heute: Feed-Schnitt

Wichtig für das Verständnis:

- Beim Start oder Speichern einer Lern-Session wird weiterhin der fachliche Umfang gespeichert: aktive Lernbereiche, ausgeschlossene Checks und daraus abgeleitete enthaltene Checks.
- Für enthaltene Checks wird inzwischen `session_check_state` synchronisiert; neue Checks starten mit `training` als `due`.
- `recall` und `feynman` schreiben weiterhin Rohversuche nach `learning_activity_attempts`; bei passendem Feed-Kontext bewegen sie zusätzlich die Check-Pipeline weiter.
- Für `start` und Flashcards gibt es inzwischen zusätzlich `session_activity_state` als erste lernbereichsweite Feed-Projektion.
- Ein `Nein, zum Dashboard` verlässt nur den aktuellen Feed-Kontext; die Aktivität bleibt ohne zusätzliche Persistenzschicht offen.
- Flashcard-Durchgänge, Kartenbewertungen und Karten-Fälligkeiten liegen serverseitig in eigenen Flashcard-Tabellen; der freie Flashcards-Aufruf bleibt ohne persistente Spaced-Repetition.
- Mit der v2-Grundlage kommen user-scoped Retention-Scope und user-scoped Flashcard-Fälligkeiten hinzu; die laufende Feed-UI nutzt diese Grundlage inzwischen als Session-first-Projektion mit queuebasiertem Retention-Kopf.
- Retention-Flashcards können dabei auch dann wieder in den Feed fallen, wenn für einen aktiven Lernbereich noch keine Retention-Card-State-Zeilen existieren.
- `warmup` ist im aktuellen Feed-Schnitt bewusst ausgeklammert; Begriffe wie `fällig` oder `abgeschlossen` sind aktuell für checkbezogene Pipeline-Schritte sowie für `start` und Flashcards materialisiert.

## Freier Modulzugriff vs. Feed-Kontext

Für den aktuellen Schnitt gilt ausdrücklich:

- Alle Module bleiben direkt zugänglich, auch ohne Session und ohne Feed.
- Die Session beschränkt also nicht den Modulzugriff, sondern nur den fachlichen Umfang des Feed.
- Ein Modul kann daher in zwei Kontexten laufen: als **freier Aufruf** oder als **Feed-Kontext**.
- Nur im Feed-Kontext bietet die Plattform eine echte Abschlussentscheidung an.

Architekturfolge:

- Die Feed-Abschlussentscheidung liegt in der gemeinsamen Feed-Shell im Kartenkopf, nicht in modulspezifischen Sonderbuttons.
- Das Modul liefert nur ein neutrales Ergebnis oder ein Signal `bereit für Feed-Entscheidung`.
- Die eigentliche Entscheidung `abschließen`, `wiederholen` oder `abbrechen` gehört in die gemeinsame Feed-Shell.

Wichtig für den aktuellen Datenmodellschnitt:

- `session_check_state` reicht nur für checkbezogene Pipeline-Schritte.
- Für einheitliches Feed-UI über `start`, `flashcards`, `recall`, `feynman` und spätere Aktivitäten braucht es zusätzlich eine generische Aktivitätsprojektion; die ersten konkreten Fälle sind jetzt `start` und `flashcards`.
- Sinnvolle Arbeitsteilung:
	- `session_check_state` als fachliche Projektion pro Check
	- `session_activity_state` als UI-nahe Projektion für nicht-checkbezogene Feed-Aktivitäten; aktuell konkret für `start` und Flashcards

Didaktisch ist die Kette trotzdem bereits klar gedacht:

- `recall` und `feynman` sind Teil einer Pipeline pro Check, nicht zwei unabhängige Module.
- Ein erfolgreiches `recall` ist nicht nur ein einzelner Versuch, sondern fachlich der Abschluss des Recall-Schritts für diesen Check.
- Ein `repeat` bei `recall` oder `feynman` bedeutet nicht `abgeschlossen`, sondern: derselbe Schritt bleibt offen.
- `feynman` kann fachlich erst sinnvoll `fällig` werden, wenn der vorherige Schritt der Kette erfolgreich abgeschlossen wurde.

Der nächste sinnvolle technische Schritt ist deshalb nicht mehr `session_check_state`, sondern die kontrollierte Verbreiterung der Flashcards-spezifischen Aktivitätsschicht zu einer generischen Feed-Schicht für spätere Feed-Historie und Start-/Abbruchereignisse. `warmup` gehört ausdrücklich nicht in den aktuellen Ausbauumfang.

### Statussemantik der ersten Projektion

Ohne Zeitlogik reicht für `recall` und `feynman` zunächst diese Unterscheidung:

- `blocked`: Modul gehört zwar zur Check-Kette, ist aber noch nicht erreichbar, weil der vorherige Schritt nicht abgeschlossen ist.
- `due`: Modul ist der aktuell nächste offene Schritt in der Check-Kette.
- `completed`: für dieses Modul liegt ein erfolgreicher Abschluss vor.

Zusätzlich sinnvoll als Rohinformation:

- `last_outcome_key`: letzter Versuch, zum Beispiel `repeat` oder `can_do`
- `ready_for_feed_decision`: optionales UI-Signal des Moduls, dass der eigentliche Lernablauf durchlaufen wurde

### Aktueller Implementierungsschnitt

Für den aktuellen technischen Schnitt ist wichtig:

- `session_check_state` ist keine reine SQL-View.
- `session_check_state` ist auch keine leere Tabelle, sondern hat echte serverseitige Übergangslogik.
- `session_activity_state` existiert aktuell als echte Tabelle für `start` und Flashcards, aber noch nicht als vollständige generische Projektion aller Feed-Aktivitäten.

Begruendung:

- Für `training` existiert in v1 bewusst nur der manuelle Feed-Abschluss, nicht die fragebasierte Erfolgswertung.
- Für `warmup` fehlen noch eigene serverseitige Rohdaten.
- Für Flashcards sind eigene serverseitige Rohdaten eingeführt: Kartenzustand, Durchgänge und Durchgangskarten; `start` braucht bewusst keinen separaten Rohdatenpfad.

Umgesetzt ist:

1. `save_active_learning_session(...)` initialisiert und synchronisiert Check-State-Zeilen.
2. `complete_current_training_step(...)` bildet den ersten serverseitigen Trainingsabschluss ab.
3. `record_check_module_attempt(...)` bindet Recall-/Feynman-Abschlüsse an dieselbe Projektion an.
4. `get_or_create_flashcard_round(...)`, `record_flashcard_review(...)` und `resolve_flashcard_round(...)` bilden den session-scoped Flashcards-Schreibpfad ab.
5. `get_or_create_retention_flashcard_round(...)`, `record_retention_flashcard_review(...)` und `resolve_retention_flashcard_round(...)` bilden den user-scoped Flashcards-Retentionpfad ab.

Für `session_activity_state` gilt aktuell:

- Eigene Tabelle für `start` und Flashcards.
- Checkbezogene Feed-Schritte bleiben in `session_check_state` und werden im Dashboard weiterhin zuerst gelesen.
- Dashboard und Sidebar lesen bereits dieselbe Feed-Liste; eine generische serverseitige `resolve_feed_activity(...)`-Schicht bleibt Zielbild.

### Einheitliche Feed-Schreibpfade in v1

Wenn Start und Abschluss designtechnisch überall gleich aussehen sollen, braucht auch der Schreibpfad eine einheitliche Form.

Empfohlene generische Übergänge:

- `open_feed_activity(activity_key)`
- `resolve_feed_activity(activity_key, decision_key)`

Empfohlene Werte für `decision_key` in v1:

- `complete`
- `keep_open`

Regeln:

- `open_feed_activity(...)` ist zunächst vor allem Routing- und Kontextlogik; eine persistente Speicherung ist optional.
- `resolve_feed_activity(...)` ist die eigentliche Plattformentscheidung aus der Feed-Shell und validiert `activity_key` gegen den aktuellen Feed-Cursor.
- Modulspezifische Details wie Recall-/Feynman-Ergebnis, Trainingsabschluss oder spätere Flashcard-Logik bleiben eigene Rohdatenquellen, werden aber nicht direkt als UI-Aktion exponiert.
- Die Feed-Shell spricht langfristig nur mit diesem generischen Aktivitätsmodell, nicht mit modulspezifischen Button-Semantiken.

### Weitere serverseitige Einführung

Der bereits erledigte Teil ist:

1. `training` serverseitig als erster relevanter Check-Übergang persistieren
2. `session_check_state` als echte Tabelle einführen
3. Recall-/Feynman-Abschlüsse an diese Projektion anbinden
4. `start` und Flashcards als erste lernbereichsweite Feed-Aktivitäten über `session_activity_state` persistieren; Flashcards zusätzlich über eigene Round-/Card-State-Tabellen

Der nächste größere Schritt ist:

1. `session_activity_state` von `start`/Flashcards auf weitere nicht-checkbezogene Feed-Elemente verbreitern
2. Feed-Historie, Abbruch-/Start-Events und automatisierte Trainingsnachweise ergänzen
3. Erst danach weitere lernbereichsweite Aktivitäten mit eigenen Rohdaten prüfen; `warmup` bleibt bis dahin bewusst außerhalb des Feed-Schnitts

### Was genau der erste serverseitige Trainingsübergang ist

Für v1 ist dieser erste Trainingsübergang bewusst **nicht** frage- oder punktbasiert.

Begründung aus dem aktuellen Ist-Stand:

- Das Training-Modul persistiert heute noch keine serverseitigen Frageergebnisse.
- Es gibt noch keinen robusten serverseitigen Begriff von `alle Fragen korrekt gelöst`.
- Es gibt auch noch keine serverseitige Trennung zwischen `mit Lösung gearbeitet` und `ohne Lösung korrekt gelöst`.

Deshalb ist der erste serverseitige Trainingsschreibpfad so klein wie möglich:

- Ein Training-Schritt gilt in v1 als abgeschlossen, wenn der Nutzer ihn **im Feed-Kontext** über die gemeinsame Feed-Shell als abgeschlossen markiert.

Das ist fachlich ein **manueller Feed-Abschluss**, nicht schon ein automatisierter Trainingsnachweis.

Empfohlene v1-Semantik:

- Ein Abschluss aus `training` setzt den nächsten Schritt `recall` auf `due`.
- Diese serverseitige Pipeline-Logik ist getrennt von späteren Kompetenz- oder Statistikdaten.

Wichtig:

- Der erste serverseitige Trainingsübergang sagt nur: `Der Trainingsschritt in der Feed-Kette wurde bewusst abgeschlossen.`
- Er sagt **noch nicht**: `Der Check wurde automatisiert fehlerfrei gelöst.`
- Automatisierte Trainingsabschlüsse für Kompetenzlisten-Freigabe und feinere Fortschrittswerte sind ein eigener, späterer Datenpfad.

### Aktuelle Training-RPC und Zielbild

Für das Zielbild bleibt fachlich eine generische Entscheidung aus der Feed-Shell wünschenswert:

- `resolve_feed_activity(activity_key, decision_key = 'complete')`

Der aktuelle v1-Schnitt ist bewusst checknah:

- `complete_current_training_step(p_check_id text)`

Präferenz für das Zielbild:

- Langfristig besser die generische Feed-Variante.
- Der schmale checknahe RPC ist für v1 akzeptabel, solange die Feed-Shell selbst bereits mit `activity_key` und generischer UI arbeitet.
- Eine spätere Migration zu `resolve_feed_activity(...)` sollte die vorhandene Semantik nur kapseln, nicht den fachlichen Ablauf ändern.

Aktueller v1-Schnitt:

- `save_active_learning_session(...)` bekommt zusätzlich die ausgewählten `p_included_check_ids` und hält damit `session_check_state` synchron.
- `complete_current_training_step(p_check_id text)` bildet den ersten serverseitigen Pipeline-Übergang für `training`.
- `record_check_module_attempt(...)` bleibt der Rohdaten-Log für `recall` und `feynman`; im Core-Feed-V2 soll die eigentliche Pipeline-Bewegung hinter `resolve_feed_activity(...)` bzw. einem cursor-validierten Feed-Abschluss liegen.

### Feed-Kontext im Frontend

Aktive Feed-Aktivitäten werden im Frontend über URL-Parameter transportiert:

- `feed=1`: Seite läuft im Feed-Kontext.
- `check_id`: fachlicher Check-Bezug für checkbezogene Aktivitäten.
- `activity_key`: stabile Feed-Aktivität, zum Beispiel `check:<check_id>:training`.
- `activity_step`: aktueller Pipeline-Schritt oder Aktivitätsschritt, zum Beispiel `training`, `recall`, `feynman` oder `flashcards`.
- `activity_run`: frischer UI-Durchlauf für Eingaben, Bewertungsmarkierungen und lokale Aufgaben-UI.

Regeln:

- `activity_key` bleibt über Abbruch und erneutes Öffnen stabil und darf daher für die Feed-Aufgabeninstanz verwendet werden.
- `activity_run` ist absichtlich flüchtig und sorgt dafür, dass ein neuer Start keine alten Eingaben oder roten/grünen Markierungen zeigt.
- Freies Training und Feed-Training verwenden getrennte lokale Aufgabenindizes und Shuffle-Nonces.
- Freie Flashcards und Feed-Flashcards sind getrennt: freier Modus hat keine Persistenz, Feed-Modus nutzt serverseitige Durchgänge.
- Ein Seitenwechsel ohne denselben Feed-Kontext fragt nach, ob die Aktivität wirklich abgebrochen werden soll.
- Links, die denselben Feed-Kontext weitertragen, zum Beispiel `Tipps` vom Training ins Skript, gelten nicht als Abbruch.

### So läuft das aktuell für einen Check

1. Session startet: Der Check liegt im Umfang der Session, aber `recall` und `feynman` sind noch nicht automatisch `due`.
2. Erst wenn der vorgelagerte Trainingsschritt im Feed abgeschlossen wird, wird `recall` zum nächsten offenen Schritt und damit `due`.
3. Öffnet der Nutzer Recall frei ohne Feed, bearbeitet er nur das Modul; an der Session-Projektion ändert sich dadurch zunächst nichts.
4. Öffnet der Nutzer Recall aus einem Feed-Eintrag, läuft derselbe Modulablauf, aber mit zusätzlichem Feed-Kontext.
5. Wird die Aktivität abgebrochen oder wiederholt, bleibt `recall` für diesen Check `due`.
6. Erst ein erfolgreicher Feed-Abschluss bewegt die Check-Pipeline auf den nächsten Kettenschritt.
7. `feynman` wird in dieser ersten Stufe direkt `due`, sobald sein Vorgängerschritt erfolgreich abgeschlossen ist.

Kurz gesagt:

- Die Session definiert zuerst den Geltungsbereich.
- Die Module bleiben frei benutzbar.
- Der Feed liefert einen zusätzlichen Bearbeitungskontext.
- Die Versuche liefern die Rohereignisse.
- `fällig` und `abgeschlossen` entstehen für Checks in `session_check_state`.
- Für das UI bleibt langfristig eine zweite, generische Projektion pro Aktivität sinnvoll.

## Sicherheitsmodell

Alle Browserzugriffe laufen über Supabase mit aktivierter Row Level Security.

Mindestregeln:

- Nutzer dürfen genau ihr eigenes Profil lesen.
- Nutzer dürfen genau ihre eigenen Lern-Sessions lesen.
- Nutzer dürfen Session-Lernbereiche und Check-Ausschlüsse nur für eigene Lern-Sessions lesen.
- Nutzer dürfen eigene Aktivitätsversuche lesen.
- Schreibzugriffe auf Profil und Lern-Sessions laufen im MVP über explizite RPCs mit internen Besitzprüfungen.
- Schreibzugriffe auf Fortschrittsdaten laufen im ersten Schritt ebenfalls über eine explizite RPC.
- Admin-Rechte sind separat zu modellieren und nicht aus frei editierbarer User-Metadaten im Client abzuleiten.

## Empfohlene technische Details

- `profiles` per Trigger aus `auth.users` erzeugen
- `updated_at` per Trigger pflegen
- partieller Unique Index auf aktive Lern-Sessions pro Nutzer
- Session-Erstellung als RPC statt als lose Folge mehrerer Client-Inserts
- direkte Tabellen-Schreibrechte aus dem Browser möglichst klein halten

## Offene Fragen nach diesem MVP

- Soll neben `display_name` noch ein Pflichtfeld wie `schule` oder `kursstufe` ins Profil?
- Braucht der Nutzer mehrere gespeicherte Entwürfe für Sessions oder nur genau eine aktive und beliebig viele historische?
- Bleibt `start` auch nach dem ersten Core-Feed-V2-Umbau in `session_activity_state`, oder zieht es später in ein gemeinsames Schrittmodell um?
- Soll `activity_key` künftig serverseitig validiert und in einer generischen Feed-RPC wie `resolve_feed_activity(...)` aufgelöst werden?
- Bleibt `learning_activity_attempts` checkbezogenen Modulversuchen vorbehalten, oder bekommt `warmup` einen eigenen Rohdatenpfad wie Flashcards?