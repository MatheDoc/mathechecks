# Benutzerverwaltung & Session-MVP

Stand: Juni 2026

Diese Datei beschreibt die erste persistente Plattform-Stufe für MatheChecks, den aktuellen checkbezogenen Feed-Schnitt und die additive v2-Grundlage für Planungsziel, Freigabelimits und Retention nach Ende einer Core-Session.
Sie umfasst Benutzer, Profile, Lern-Sessions, `session_check_state` als erste Check-Pipeline-Projektion, additive Planungsparameter und schlanke Fortschrittsschreibpfade für Training, Recall, Feynman und Flashcards.

## Dokumentgrenzen

- Diese Datei beschreibt fachliches Zielbild, Datenmodell, Sicherheitsmodell und MVP-Scope.
- `.github/feed.md` ist die kanonische Feed-Zieldoku; diese Datei trägt dafür nur die additive Datenmodell- und Migrationssicht.
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
- Seit der Feed-Vereinfachung (`20261121120000_feed_simplification.sql`) ist `session_check_state` nur noch Mitgliedschaft; der Session-Fortschritt liegt in `session_activity_completions` (siehe `.github/feed.md`).
- Die Flashcards-Folge-Migration führte `session_activity_state` und session-scoped Flashcard-Runden ein; beides ist seit `20261121130000_feed_legacy_cleanup.sql` entfernt bzw. stillgelegt (die Kartenstände bleiben als Historie für die Retention).
- `complete_session_start(...)` schließt die Start-Aktivität eines Lernbereichs für die aktive Session ab (idempotent); alle übrigen Aktivitäten werden über `record_user_activity(...)` gutgeschrieben.
- `get_or_create_retention_flashcard_round(...)`, `record_retention_flashcard_review(...)` und `resolve_retention_flashcard_round(...)` ergänzen den user-scoped Retention-Schreibpfad außerhalb des Core-Cursors; die Durchgänge können auch während einer aktiven Core-Session sichtbar werden.
- `user_activity_events` ergänzt einen separaten user-scoped Append-only Log für accountgebundene Aktivitätsstatistik außerhalb der Feed-Projektion.
- `record_user_activity(...)` schreibt kumulative Ereignisse für `training`, `recall`, `feynman`, `test` und `flashcards`; `get_user_activity_overview()` liefert daraus das Dashboard-Read-Model für Gesamtzahlen und 7-Tage-Überblick.
- `get_user_check_proficiency()` leitet die user-scoped Quote je Check als recency-gewichtetes Read-Model aus den `training`-Ereignissen ab (Parameter `proficiency.*` in `system_settings`); `get_user_activity_overview().trainingSuccess` und `.proficiency` beziehen ihre Erfolgsquote daraus, das Dashboard rendert die nach Quote sortierte Trainingsfokus-Liste.
- E-Mail-/Passwort-Anmeldung, Registrierung, OAuth-Anmeldung, Logout, Passwortänderung und Kontolöschung laufen aktuell über Supabase Auth, RPCs und `konto.html`.
- `delete_current_user_account(...)` löscht nach expliziter Bestätigung den aktuellen Auth-User; abhängige Plattformdaten werden über bestehende `on delete cascade`-Beziehungen entfernt.
- Der Recovery-Link führt derzeit zurück auf `konto.html`, wo der Nutzer ein neues Passwort setzt.
- Das Session-Modal im Dashboard kann ein explizites `target_date` speichern; die Session-Box zeigt dieses Datum anschließend zusammen mit einer groben Heuristik auf Basis der noch offenen Check-Schritte.
- Das Dashboard trennt im UI zwischen `Session` und `Feed`: Die Session verwaltet die aktive Core-Session, der Feed bündelt Empfehlungen aus der aktiven Session und aus Wiederholungen.
- Der Feed zeigt im Dashboard und im Header genau eine Empfehlung aus `get_feed_recommendation(...)`; fällige Retention-Flashcards dürfen den sichtbaren Feed-Kopf übernehmen, wenn die Session nur einen vorgezogenen Folgeschritt hätte.
- Alle Module laufen frei; jede abgeschlossene Aktivität zählt für die Session. Nur Retention-Flashcards nutzen noch einen Feed-Kontext mit Serverrunden.
- Das Dashboard ergänzt dazu eine eigene Box `Abgeschlossen`, die vollständig erledigte Lernbereiche aus `session_activity_completions` und Retention-Bezügen ableitet.
- Zentrale Systemwerte werden in `public.system_settings` mit Integer- oder Numeric-Wert und Kurzbeschreibung gepflegt; dazu gehören aktuell Lock-Dauer, Default-Tempo, Core-Gap-Profile, Druckschwellen, Lastgewichte, Retention-Abstand und die Quoten-Parameter.

## Feed-Vereinfachung (2026-11)

Der frühere Core-Feed mit Cursor, Sticky-Lock, materialisierten Zeitfenstern und `activity_key`-Pflicht für Abschlüsse ist abgelöst. Normativ ist `.github/feed.md`:

- Fortschritt = `session_activity_completions` (eine Zeile je abgeschlossener Aktivität und Session), geschrieben über `credit_session_activity(...)`.
- Empfehlung = zustandslose Lesefunktion `get_feed_recommendation(...)`.
- Badge = Tagesziel minus heute erledigt (`feed_attention_summary(...)`).
- `20261121130000_feed_legacy_cleanup.sql` entfernt die Altlasten: `session_feed_cursor`, `session_activity_state`, Pipeline- und Zeitfenster-Spalten in `session_check_state`, Tagesbudget-Spalten in `learning_sessions`, Replan-/Druck-/Cursor-Funktionen, session-scoped Flashcard-RPCs und die zugehörigen Systemwerte.

## Begriffstrennung

- **Auth-Session:** Technische Login-Session von Supabase Auth mit Token und Ablaufzeit.
- **Lern-Session / Core-Session:** Fachliches Objekt von MatheChecks; endlicher Kernplan eines Benutzers mit Zielhorizont und Freigabeparametern.

Weitere Trennung für den aktuellen und nächsten Ausbauschritt:

- **Lernaktivität / Versuch:** Append-only Rohdaten eines expliziten Modulabschlusses, zum Beispiel `recall` oder `feynman` mit `can_do` oder `repeat`.
- **Session-Aktivität:** `start`, `training`, `test`, `recall`, `feynman` oder `flashcards` innerhalb einer Lern-Session, identifiziert über `activity_key`.
- **Abschluss:** Einmalige Gutschrift einer Session-Aktivität in `session_activity_completions`; entsteht bei jedem Modulabschluss, frei oder aus dem Feed.
- **Feed:** Zustandslose Empfehlung der nächsten offenen Session-Aktivität plus fällige Retention; kein Cursor, keine Sperre.
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
- `gebiet_order integer not null default 0` — Reihenfolge zwischen Gebieten bei gleichzeitigen Freigaben, aktuell aus `gebiete.yml`
- `created_at timestamptz not null default now()`

Schlüssel:

- `primary key (session_id, lernbereich_slug)`

Bemerkung:

- `lernbereich_slug` referenziert bewusst auf Repo-Content, nicht auf eine eigene Content-Tabelle in der Datenbank.
- `sort_index` und `gebiet` kommen aus `lernbereiche.yml` (`didactic_order`), `gebiet_order` aus `gebiete.yml`; alle drei Werte werden beim Speichern der Session als Repo-Snapshot mitgegeben.
- `gebiet_order` und `sort_index` bestimmen die Reihenfolge, in der der Feed neuen Stoff empfiehlt; gesperrt wird nichts.

### 4a. `public.system_settings`

Zweck:
Zentrale Stelle für globale Systemwerte, die Frontend und serverseitige Feed-/Planungslogik gemeinsam verwenden.

Aktuelle Schlüssel:

- `planning.default_activities_per_day`
- `feed.recommendation_gap_hours`
- `feed.retention_activity_base_gap`
- `proficiency.window_size`
- `proficiency.recency_decay`
- `proficiency.retry_penalty`

`feed.recommendation_gap_hours` ist der empfohlene Abstand `G` zwischen zwei Schritten derselben Check-Kette (Feed-Empfehlung, Zieldatum-Vorschlag).

`feed.retention_activity_base_gap` steuert für Retention-Scopes sowohl den ersten serverseitigen Due-Abstand `N` als auch die weiteren linearen Wiederkehr-Abstände `2N`, `3N`, `4N`, ... nach abgeschlossenen Retention-Runden. Die `proficiency.*`-Werte steuern das Quoten-Read-Model (Spezifikation in `.github/quoten.md`).

### 4b. `public.user_feed_activity_counters`

Zweck:
User-scoped Zähler für abgeschlossene Feed-Aktivitäten. Die Tabelle liefert serverseitige Referenzwerte für Retention-Abstände und andere feedweite Freigabelogik.

Gezählt wird jede neue Session-Gutschrift (`credit_session_activity`) sowie abgeschlossene Retention-Runden.

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

### 4c. `public.user_activity_events`

Zweck:
User-scoped Append-only Log für accountgebundene Aktivitätsstatistik außerhalb der Feed-Pipeline. Die Tabelle ist bewusst getrennt von `user_feed_activity_counters`: Dort liegt die kleine serverseitige Referenz für Freigabelogik, hier die breitere Rohdatenbasis für Dashboard-Auswertung und spätere Activity-Map.

Aktuelle Felder:

- `id uuid primary key default gen_random_uuid()`
- `user_id uuid not null references auth.users(id) on delete cascade`
- `activity_type text not null check (activity_type in ('training', 'recall', 'feynman', 'flashcards', 'test'))`
- `lernbereich_slug text null`
- `check_id text null`
- `context_key text null` — aktuell fachlich `feed` oder `free`
- `details jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`

Regeln:

- Jeder erfolgreiche Schreibfall erzeugt genau ein neues Ereignis; es gibt keinen Reset- oder Überschreibpfad.
- Die Tabelle dient nicht als Source of Truth des Session-Fortschritts.
- `training` wird im Frontend aktuell beim ersten vollständigen Beantworten einer Aufgabenkarte geschrieben.
- `recall` und `feynman` werden aktuell beim Start des Selbstchecks geschrieben.
- `flashcards` wird pro abgeschlossenem Durchgang geschrieben, sowohl im Feed-Kontext als auch bei freiem Aufruf.
- `details` trägt nur leichte UI-/Auswertungsmetadaten und bleibt fachlich optional.

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
Mitgliedschaft: welche Checks gehören zur Lern-Session. Der Fortschritt liegt in `session_activity_completions` (Abschnitt 7a).

Felder:

- `session_id uuid not null references public.learning_sessions(id) on delete cascade`
- `check_id text not null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Schlüssel:

- `primary key (session_id, check_id)`

Regeln:

- `save_active_learning_session(...)` synchronisiert die Zeilen aus den im Frontend aufgelösten enthaltenen Checks; nicht mehr enthaltene Checks werden entfernt.
- Das Frontend darf `session_check_state` lesen, aber nicht direkt schreiben.

### 7a. `public.session_activity_completions`

Zweck:
Genau ein Abschluss je Session-Aktivität. Einzige Quelle des Session-Fortschritts.

Felder:

- `session_id uuid not null references public.learning_sessions(id) on delete cascade`
- `activity_key text not null` (`lernbereich:{slug}:start|flashcards`, `check:{check_id}:{step}`)
- `activity_type text not null` (`start`, `training`, `test`, `recall`, `feynman`, `flashcards`)
- `lernbereich_slug text not null`
- `check_id text null`
- `completed_at timestamptz not null default now()`

Schlüssel:

- `primary key (session_id, activity_key)`

Regeln:

- Geschrieben ausschließlich serverseitig über `credit_session_activity(...)` (aus `record_user_activity(...)` und `complete_session_start(...)`); idempotent.
- Das Frontend liest die eigenen Zeilen (RLS über `learning_sessions.user_id`).
- Offene Aktivitäten werden über `session_activity_items(session_id)` abgeleitet, nicht gespeichert.

### 8. (entfernt) `public.session_activity_state`

Frühere Projektion für `start`/`flashcards`; mit `20261121130000_feed_legacy_cleanup.sql` entfernt.

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

### Aktivität abschließen (frei oder aus dem Feed)

1. Nutzer bearbeitet ein Modul; sobald die Aktivität durchgemacht ist, wird das Haken-Icon abschließbar.
2. Das Modul ruft `record_user_activity(...)` auf (Start: `complete_session_start(...)`).
3. `credit_session_activity(...)` schreibt den Abschluss idempotent in `session_activity_completions`, falls die Aktivität zur aktiven Session gehört.
4. Sind danach alle Check-Schritte eines Lernbereichs erledigt, wird die Flashcards-Wiederholung des Lernbereichs aktiviert (`user_retention_scopes`).
5. Das Abschluss-Popup bietet `Nächste Aktion`, `Zum Dashboard`, `Wiederholen` und `Auf Seite bleiben`.

## MVP-RPCs

- `update_own_profile(p_display_name text)`
- `save_active_learning_session(p_lernbereiche text[], p_excluded_check_ids text[], p_activities_per_day numeric default null, p_included_check_ids text[] default array[]::text[], p_target_date date default null, p_target_source text default null, p_lernbereiche_meta jsonb default null)` — `p_lernbereiche_meta`: optionales JSON-Array `[{slug, gebiet, gebiet_order, sort_index}, …]`; `start` wird daraus gebietsweise freigeschaltet, eigentliche Check-Aktivitäten bleiben bis zum abgeschlossenen `start` des Lernbereichs `blocked`
- `delete_active_learning_session()`
- `complete_session_start(p_lernbereich_slug text)`
- `get_feed_recommendation(p_session_id uuid default null)`
- `feed_attention_summary(p_session_id uuid default null)`
- `record_user_activity(p_activity_type text, p_lernbereich_slug text default null, p_check_id text default null, p_context_key text default null, p_details jsonb default '{}'::jsonb)`
- `get_user_activity_overview()`
- `get_user_check_proficiency()`
- `finish_learning_session(p_session_id uuid, p_status text)`
- `set_retention_scope_status(p_lernbereich_slug text, p_status text)`
- `delete_current_user_account()`

### Interne Hilfsfunktionen (kein direkter Nutzer-Grant)

- `credit_session_activity(p_user_id uuid, p_activity_type text, p_lernbereich_slug text, p_check_id text)` — schreibt eine Session-Gutschrift (siehe `.github/feed.md`)
- `session_activity_items(p_session_id uuid)` — alle Aktivitäten einer Session mit Abschlusszeitpunkt
- `session_feed_recommendations(p_session_id uuid)` — sortierte Kandidaten der Empfehlung
- `handle_session_lernbereich_completion(p_session_id uuid, p_user_id uuid, p_lernbereich_slug text)` — aktiviert die Flashcards-Wiederholung nach vollständigem Lernbereich
- `_compute_training_task_score(p_details jsonb, p_retry_penalty numeric)` — berechnet den Aufgaben-Score eines `training`-Ereignisses (Mittel der Frage-Scores `max(0, 1−(n−1)·p)`, eingeblendete Lösung = 0); Legacy-Ereignisse fallen auf das alte `correctCount/totalCount`-Schema zurück

## Minimale Leseflüsse

- Profil des eingeloggten Nutzers laden
- aktive Lern-Session des Nutzers laden
- zugehörige Lernbereiche und Check-Ausschlüsse laden, falls eine Session aktiv ist
- `session_activity_completions` für die aktive Session lesen (Fortschritt) und `get_feed_recommendation(...)` für die Empfehlung
- zusätzlich aktive `user_retention_scopes` und Retention-Fälligkeiten für Flashcards lesen
- bei Bedarf eigene Recall-/Feynman-Versuche lesen
- daraus im Frontend den effektiven Session-Umfang, Feed-Titel, die Queue-Reihenfolge sichtbarer Retention und Routingdaten gegen Repo-Content auflösen

## Stand heute: Feed-Schnitt

- Alle Module bleiben direkt zugänglich, auch ohne Session und ohne Feed. Die Session legt nur den Umfang fest, für den Abschlüsse zählen.
- Es gibt keinen Feed-Kontext mehr für Session-Aktivitäten: Feed-Links öffnen das Modul normal (`?check_id=…`).
- Jede abgeschlossene Aktivität einer Session-Aktivität zählt einmal, unabhängig von Reihenfolge und Einstieg.
- Retention-Flashcards laufen weiterhin mit Feed-Kontext (`?feed=1&activity_key=retention:…`) und serverseitigen Runden.
- `warmup` ist bewusst noch keine Session-Aktivität.
- Details: `.github/feed.md`.

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
- Wird `warmup` als erste Kettenstufe Teil der Session-Aktivitäten?
- Bleibt `learning_activity_attempts` checkbezogenen Modulversuchen vorbehalten, oder bekommt `warmup` einen eigenen Rohdatenpfad wie Flashcards?