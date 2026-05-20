# Supabase lokal für MatheChecks

Diese Struktur ist der versionierte Supabase-Bestand für MatheChecks.

## Zweck

- `config.toml` enthält die lokale CLI-Konfiguration.
- `migrations/` enthält versionierte Schemaänderungen.
- `seed.sql` kann später für Testdaten genutzt werden.

## Lokaler Workflow

1. Supabase CLI installieren.
2. Docker Desktop oder eine Docker-kompatible Laufzeit installieren.
3. Im Repo `supabase start` ausführen.
4. Bei Bedarf mit `supabase db reset` die lokale Datenbank aus Migrationen neu aufbauen.
5. Änderungen am Datenmodell immer als neue Migration versionieren.

## Wichtige Befehle erklärt

### `supabase init`

Bedeutung in MatheChecks:

- Legt nur die lokale Supabase-Projektstruktur im Repo an.
- Erzeugt zum Beispiel `supabase/config.toml`.
- Verbindet nichts mit deinem echten Supabase-Projekt.
- Ändert noch nichts an einer Datenbank.

Für MatheChecks ist dieser Schritt bereits erledigt.

### `supabase link`

Bedeutung in MatheChecks:

- Verknüpft dieses lokale Repo mit deinem bereits angelegten Remote-Supabase-Projekt.
- Danach weiß die CLI, gegen welches gehostete Projekt Befehle wie `db push` oder `db pull` laufen sollen.
- Erst dieser Schritt stellt eine echte CLI-Verbindung zum Remote-Projekt her.

Wichtig:

- `link` deployt noch nichts.
- `link` allein erzeugt noch keine Tabellen im Remote-Projekt.

### `supabase start`

Bedeutung in MatheChecks:

- Startet den kompletten lokalen Supabase-Stack per Docker.
- Baut damit eine lokale Entwicklungsumgebung mit Datenbank, Auth, API und Studio auf.
- Auf diese lokale Umgebung werden dann die Migrationen aus `supabase/migrations/` angewendet.

Nutzen für MatheChecks:

- Wir testen Benutzerverwaltung, RPCs und RLS zuerst lokal.
- Fehler landen damit nicht direkt im echten Projekt.

### `supabase db reset`

Bedeutung in MatheChecks:

- Setzt die lokale Datenbank zurück und spielt alle Migrationen aus `supabase/migrations/` von vorne ein.
- Optional würden danach auch Seeds ausgeführt.

Nutzen für MatheChecks:

- Sehr gut, um zu prüfen, ob das MVP-Schema wirklich reproduzierbar ist.
- Wenn `db reset` sauber durchläuft, ist das ein gutes Zeichen, dass die Migrationen konsistent sind.

Wichtig:

- Das betrifft lokal die Datenbank im Docker-Stack.
- Das ist kein Befehl für das Remote-Projekt im normalen MVP-Workflow.

### `supabase db push`

Bedeutung in MatheChecks:

- Spielt die lokalen Migrationen in das verlinkte Remote-Supabase-Projekt ein.
- Das ist der Schritt, der echte Tabellen, Funktionen und Policies im gehosteten Projekt anlegt oder ändert.

Windows-Hinweis für dieses Repo:

- Auf diesem Rechner liegt die CLI aktuell unter `C:\Users\fue\bin\supabase.exe` und nicht im globalen `PATH`.
- Für verlässliche Remote-Deploys gibt es deshalb zusätzlich das Repo-Skript `supabase/deploy-remote.ps1`.
- Typischer Aufruf: `& .\supabase\deploy-remote.ps1`

Wichtig:

- `db push` sollte erst nach lokalem Test mit `supabase start` und `supabase db reset` verwendet werden.
- Vor `db push` sollte das Repo per `supabase link` mit dem richtigen Remote-Projekt verbunden sein.

## Empfohlene Reihenfolge für einen lokalen-first Workflow

1. `supabase init`
2. `supabase start`
3. `supabase db reset`
4. lokale Prüfung von Auth, RPCs und Schema
5. `supabase link`
6. `supabase db push`

Hinweis:

Im aktuellen Projekt lief der MVP bewusst remote-first, weil Docker lokal noch fehlt.

## Aktueller Stand in diesem Repo

- `supabase init` ist bereits erledigt.
- `supabase link` gegen das Remote-Projekt ist bereits ausgeführt.
- Die erste MVP-Migration ist bereits in das gehostete Projekt gepusht.
- Die Folge-Migration `migrations/20260515103000_save_active_learning_session.sql` ist bereits im Remote-Projekt aktiv und ergänzt den Session-Schreibpfad um `create-or-replace` für die aktive Session.
- Die nächste Migration `migrations/20260515140000_learning_activity_attempts.sql` ergänzt einen ersten Fortschritts-Log für explizite Recall-/Feynman-Abschlüsse.
- Die Folge-Migration `migrations/20260516093000_session_check_state_v1.sql` führt `session_check_state`, `complete_current_training_step(...)` und die erste echte Check-Pipeline-Projektion ein.
- Dieselbe Migration erweitert `save_active_learning_session(...)` um `p_included_check_ids`, damit Session-Umfang und Check-State-Zeilen gemeinsam synchronisiert werden.
- Die Folge-Migration `migrations/20260516101500_delete_active_learning_session.sql` ergänzt `delete_active_learning_session()` für das vollständige Löschen der aktiven Session samt zugehöriger Session-Projektionen.
- Die Folge-Migration `migrations/20260516130000_flashcards_feed_rounds.sql` ergänzt `session_activity_state`, serverseitige Flashcard-Durchgänge und die RPCs `get_or_create_flashcard_round(...)`, `record_flashcard_review(...)` und `resolve_flashcard_round(...)`.
- Die Folge-Migration `migrations/20260516143000_fix_flashcard_round_rpc_ambiguity.sql` ersetzt `get_or_create_flashcard_round(...)` mit eindeutig qualifizierten Spaltennamen, damit Flashcard-Durchgänge im Feed zuverlässig geladen werden.
- Die Folge-Migration `migrations/20260517110000_delete_current_user_account.sql` ergänzt `delete_current_user_account(...)` für die bestätigte Selbstlöschung des aktuell angemeldeten Auth-Users samt kaskadierender Plattformdaten.
- Die Folge-Migration `migrations/20260518170000_fix_save_active_learning_session_lernbereich_slug_ambiguity.sql` behebt die Laufzeitmehrdeutigkeit in `save_active_learning_session(...)`, damit das Speichern aktiver Sessions trotz Feed-/Flashcard-Sync wieder zuverlässig funktioniert.
- `_config.yml` enthält `supabase_url` und `supabase_anon_key`; Topbar und `konto.html` lesen diese Werte zur Laufzeit.
- `konto.html` deckt aktuell E-Mail-Link-Anmeldung und -Registrierung, OAuth-Anmeldung über konfigurierte externe Provider, lokalen Logout, Passwortänderung und bestätigte Kontolöschung ab.
- `dashboard.html` liest, speichert und löscht die aktive Lern-Session inzwischen über Supabase; die primäre Feed-Karte liest zuerst checkbezogene fällige Schritte aus `session_check_state` und danach lernbereichsweite Flashcards aus `session_activity_state`.
- `training` schließt Feed-Schritte über `complete_current_training_step(...)` ab.
- `recall` und `feynman` schreiben explizite Abschlussentscheidungen über `record_check_module_attempt(...)` in Supabase und bewegen passende Check-State-Zeilen weiter.
- `supabase start` ist noch nicht möglich, weil Docker lokal fehlt.

## Aktueller MVP-Stand

- Die erste Migration für Benutzerverwaltung und Lern-Sessions liegt in `migrations/20260514170000_benutzerverwaltung_mvp.sql`.
- Die aktive Folge-Migration liegt in `migrations/20260515103000_save_active_learning_session.sql` und führt `save_active_learning_session(...)` für das Anlegen, Ersetzen oder Leeren der aktiven Session ein.
- Die nächste Folge-Migration liegt in `migrations/20260515140000_learning_activity_attempts.sql` und führt `learning_activity_attempts` plus `record_check_module_attempt(...)` für Recall-/Feynman-Abschlüsse ein.
- Die Folge-Migration `migrations/20260516093000_session_check_state_v1.sql` führt `session_check_state` plus `complete_current_training_step(...)` für den ersten serverseitigen Trainingsübergang ein.
- Die Folge-Migration `migrations/20260516101500_delete_active_learning_session.sql` führt `delete_active_learning_session()` für das vollständige Löschen der aktiven Session ein.
- Die Folge-Migration `migrations/20260516130000_flashcards_feed_rounds.sql` führt die erste lernbereichsweite Feed-Projektion und serverseitige Flashcard-Runden ein.
- Die Folge-Migration `migrations/20260516143000_fix_flashcard_round_rpc_ambiguity.sql` behebt die RPC-Laufzeitmehrdeutigkeit beim Erzeugen/Laden eines Flashcard-Durchgangs.
- Die Folge-Migration `migrations/20260517110000_delete_current_user_account.sql` führt `delete_current_user_account(...)` für die bestätigte Kontolöschung ein.
- Die Folge-Migration `migrations/20260518170000_fix_save_active_learning_session_lernbereich_slug_ambiguity.sql` behebt die RPC-Laufzeitmehrdeutigkeit beim Speichern der aktiven Session.
- Schreibzugriffe laufen im MVP über RPCs statt über freie Tabellen-CRUDs.
- Lokale Auth-Redirects sind auf den Jekyll-Dev-Server unter `http://127.0.0.1:4001` bzw. `http://localhost:4001` ausgerichtet.
- Die Frontend-Brücke liest optionale Jekyll-Werte `supabase_url` und `supabase_anon_key` und aktiviert damit Topbar und `konto.html`.
- Die Frontend-Brücke liest `supabase_oauth_providers` aus `_config.yml`; aktuell werden `google` und `apple` als OAuth-Buttons in `konto.html` gerendert.
- E-Mail-Link-, OAuth- und Recovery-Redirects führen auf `konto.html` zurück; ein separater Auth-Callback ist nicht nötig.
- `dashboard.html` lädt, speichert und löscht die aktive Lern-Session inzwischen über Supabase; die Session-Auswahl arbeitet dort mit stabilen `check_id`-Werten.
- Die erste checkbezogene Feed-Projektion ist aktiv: Dashboard öffnet `training`, `recall` und `feynman` im Feed-Kontext mit `activity_key`, `activity_step` und `activity_run`.
- Flashcards sind als lernbereichsweite Feed-Aktivität angebunden und öffnen im Feed-Kontext ohne `check_id`.
- Die gemeinsame Feed-Shell fragt beim Abbruch oder Seitenwechsel nach und schützt freie Modulaktionen vor Eingriffen in Feed-Aktivitäten.

## Aktuelle Frontend-Feed-Semantik

- `activity_key` ist die stabile Identität einer Feed-Aktivität, zum Beispiel `check:<check_id>:training_1`.
- `activity_step` beschreibt den fachlichen Pipeline-Schritt.
- `activity_run` ist nur ein flüchtiger UI-Durchlauf, damit neue Starts keine alten Eingaben oder Bewertungsmarkierungen zeigen.
- Die Aufgabeninstanz im Feed-Training wird lokal nach `activity_key` stabil gehalten.
- Freies Training und Feed-Training verwenden getrennte lokale Aufgabenindizes und Shuffle-Nonces.
- Ein persistentes Start-/Abbruch-Log gibt es noch nicht.

## Noch offen

- Docker ist lokal noch nicht installiert; `supabase start` funktioniert erst danach.
- Die primäre checkbezogene Dashboard-Feed-Karte ist angebunden; vollständige Feed-Liste, Sidebar-Projektion und Fortschrittskarten lesen noch nicht vollständig aus persistenten Plattformdaten.
- Automatisierte Trainingsversuche auf Fragenebene und lernbereichsbezogene Aktivitäten wie `warmup` werden noch nicht persistiert.
- `session_activity_state` ist in v1 nur für `flashcards` eingeführt; weitere Aktivitätstypen und eine vollständige Feed-Liste fehlen noch.
- Gehostete Auth-Einstellungen wie SMTP, Redirect-URLs und Rate Limits liegen aktuell im Supabase-Dashboard und nicht versioniert im Repo.

## Remote-first: Aktueller Stand

- Die Supabase Project URL ist in `_config.yml` verdrahtet.
- Der publishable anon key ist in `_config.yml` verdrahtet.
- Der Project Ref ist lokal per `supabase link` hinterlegt.
- Die bisherigen Datenbankmigrationen bis einschließlich `20260518170000_fix_save_active_learning_session_lernbereich_slug_ambiguity.sql` sind bereits im Remote-Projekt aktiv.
- Für weitere Remote-Deploys kann auf diesem Rechner direkt `& .\supabase\deploy-remote.ps1` verwendet werden; das Skript ruft die vorhandene CLI unter `C:\Users\fue\bin\supabase.exe` auf.
- Das SMTP-Setup für das gehostete Projekt wird im Supabase-Dashboard gepflegt.

Hinweis:

- `supabase_url` und `supabase_anon_key` werden im Jekyll-Configfile `_config.yml` hinterlegt und treiben die Frontend-Brücke.
- Der `service_role`-Key wird weder im Repo noch im Frontend benötigt.
- Das eigentliche CLI-Login zu Supabase sollte direkt im Terminal erfolgen, nicht über Chat.

## OAuth-Login mit Google und Apple

Die Konto-Seite rendert OAuth-Buttons für die Provider aus `_config.yml` unter `supabase_oauth_providers`.

Aktuell vorbereitet:

- `google`
- `apple`

Damit diese Buttons funktionieren, müssen die Provider zusätzlich im gehosteten Supabase-Projekt aktiviert werden. Das geschieht im Supabase-Dashboard unter `Authentication > Providers`.

Für jeden Provider werden benötigt:

- Provider aktivieren
- Client-ID eintragen
- Client-Secret im Dashboard hinterlegen
- Redirect-/Callback-URL beim Provider hinterlegen, typischerweise `https://<project-ref>.supabase.co/auth/v1/callback`
- Site URL und erlaubte Redirect URLs in Supabase weiter auf `konto.html` bzw. die produktive Domain abstimmen

Wichtig:

- OAuth-Secrets werden nicht ins Repo geschrieben.
- `_config.yml` steuert nur, welche Buttons im Frontend angezeigt werden.
- Die eigentliche Provider-Aktivierung bleibt eine gehostete Auth-Einstellung im Supabase-Dashboard.

## Wichtig: `config.toml` vs. gehostetes Projekt

- `supabase/config.toml` steuert nur einen lokalen Supabase-Stack per Docker.
- Das gehostete Supabase-Projekt übernimmt SMTP, Redirect-URLs, Rate Limits und andere Auth-Details nicht automatisch aus dieser Datei.
- Änderungen an Hosted-Auth-Einstellungen erfolgen derzeit im Supabase-Dashboard.
- Geheimnisse wie SMTP-Passwörter oder ein `service_role`-Key werden nicht ins Repo geschrieben.

## Minimales SMTP-Setup für das MVP

Für die aktuelle Benutzerverwaltung ist ein eigenes SMTP-Setup praktisch Pflicht, sobald du Magic Links, Bestätigungsmails oder Recovery-Mails mehr als kurz antesten willst.

Wichtig für MatheChecks:

- Die eingebaute Supabase-Mailzustellung ist nur für frühe Tests gedacht.
- Ohne eigenes SMTP werden Mails nur an autorisierte Team-Adressen gesendet.
- Die eingebaute Mailzustellung ist stark limitiert, aktuell ungefähr 2 Mails pro Stunde projektweit.
- Mit eigenem SMTP setzt Supabase zunächst trotzdem ein vorsichtiges Limit von 30 Mails pro Stunde, bis du es unter `Authentication > Rate Limits` anpasst.

### Kleinster sinnvoller Weg

1. Einen einfachen SMTP-Anbieter anlegen.
2. Eine Absenderadresse oder Domain verifizieren.
3. In Supabase unter `Authentication > SMTP Settings` eigenes SMTP aktivieren.
4. Host, Port, Benutzername, Passwort und Absenderadresse eintragen.
5. Unter `Authentication > Rate Limits` das Mail-Limit prüfen.
6. Danach E-Mail-Link-Anmeldung und Registrierung erneut über `konto.html` testen.

### Welche Daten du im Supabase-Dashboard brauchst

- `smtp_host`
- `smtp_port`
- `smtp_user`
- `smtp_pass`
- Absenderadresse, zum Beispiel `no-reply@...`
- optional ein sichtbarer Absendername wie `MatheChecks`

### Minimaler Dashboard-Pfad

1. Supabase-Projekt öffnen.
2. `Authentication` aufrufen.
3. `SMTP Settings` öffnen.
4. `Enable Custom SMTP` aktivieren.
5. SMTP-Zugangsdaten des Anbieters eintragen.
6. Änderungen speichern.
7. Unter `Authentication > URL Configuration` prüfen, dass die Redirect-URLs für `http://127.0.0.1:4001` und `http://localhost:4001` weiter stimmen.
8. Unter `Authentication > Rate Limits` prüfen, ob das aktuelle Mail-Limit zum Testen reicht.

### STRATO als minimaler SMTP-Provider

Wenn bereits ein STRATO-Postfach vorhanden ist, ist das für frühe MVP-Tests oft der schnellste Weg.

Typische Felder für Supabase:

- `smtp_host`: `smtp.strato.de`
- `smtp_port`: `465`
- `smtp_user`: vollständige STRATO-E-Mail-Adresse
- `smtp_pass`: Passwort des STRATO-Postfachs
- `Sender email`: dieselbe STRATO-Adresse oder ein dazugehöriger Alias
- `Sender name`: zum Beispiel `MatheChecks`

Hinweise:

- STRATO nutzt für den SMTP-Versand typischerweise SSL auf Port `465`.
- Als Benutzername wird üblicherweise die vollständige E-Mail-Adresse verwendet, nicht nur der lokale Teil vor dem `@`.
- Für kleine, kontrollierte Tests ist das ausreichend.
- Für höhere Versandmengen, bessere Logs und robustere Zustellbarkeit ist später ein dedizierter Transaktionsanbieter oft die bessere Wahl.

### Pragmatischer MVP-Rahmen

- Für das MVP reicht ein einzelner Absender wie `no-reply@...`.
- DKIM, SPF und DMARC sollten beim Anbieter sauber gesetzt sein, sobald eine echte Domain verwendet wird.
- Der `service_role`-Key ist dafür weiterhin nicht im Frontend nötig.
- Solange noch keine produktive Domain dahintersteht, ist dieses Setup nur für kontrollierte Tests gedacht.

### Was wir dafür nicht brauchen

- keinen lokalen Docker-Supabase-Stack
- keine zusätzliche Datenbankmigration
- keine Änderung am Frontend-Auth-Code
- keinen `service_role`-Key im Browser