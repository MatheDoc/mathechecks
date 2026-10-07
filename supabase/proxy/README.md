# Supabase-Proxy (`api.mathechecks.de`)

## Zweck

Einige Schulnetze blockieren per DNS-Filter alle Adressen unter `*.supabase.co`. Dann schlagen Login, Dashboard, Recall- und Feynman-Bewertung fehl („Supabase ist konfiguriert, aber aktuell nicht erreichbar.“), obwohl das Projekt läuft.

`main.ts` ist ein kleiner Reverse Proxy auf Deno Deploy. Er leitet Anfragen von `https://api.mathechecks.de` unverändert an `https://ysqpmtreljfdwtlvjzis.supabase.co` weiter. `mathechecks.de` wird von den Filtern nicht blockiert.

- Weitergeleitet werden nur `/auth/v1/`, `/rest/v1/`, `/functions/v1/` und `/storage/v1/`.
- `/` und `/health` antworten mit `ok` (Erreichbarkeitstest).
- Das Ziel kann per Umgebungsvariable `SUPABASE_UPSTREAM_URL` überschrieben werden.

## Grenzen

Supabase erzeugt einige Links weiterhin mit der Projekt-URL (`*.supabase.co`). Diese funktionieren in gefilterten Netzen auch mit Proxy nicht:

- Google-Login (OAuth-Callback läuft über `https://ysqpmtreljfdwtlvjzis.supabase.co/auth/v1/callback`)

E-Mail/Passwort-Login, Datenbankzugriffe und Edge Functions laufen vollständig über den Proxy. Bestätigungs- und Passwort-Reset-Mails ebenfalls, sofern die Mail-Vorlagen auf `token_hash` umgestellt sind (siehe `supabase/README.md`, Abschnitt „E-Mail-Vorlagen ohne supabase.co-Links“).

## Einrichtung

### 1. Deno installieren und Proxy deployen

```powershell
irm https://deno.land/install.ps1 | iex
cd supabase\proxy
deno deploy create --source local --app mathechecks-api --runtime-mode dynamic --entrypoint main.ts --region eu
```

Beim ersten Aufruf öffnet sich der Browser zur Anmeldung bei Deno Deploy (Konto z. B. über GitHub). Nach dem Build ist der Proxy unter `https://mathechecks-api.<org>.deno.net` erreichbar.

Test:

```powershell
curl.exe https://mathechecks-api.<org>.deno.net/health
```

Spätere Änderungen an `main.ts` deployen mit:

```powershell
cd supabase\proxy
deno deploy --prod
```

### 2. Eigene Domain in Deno Deploy anlegen

In [console.deno.com](https://console.deno.com): Organisation → Tab **Domains** → **Add Domain** → `api.mathechecks.de` (ohne Wildcard). Der Dialog zeigt die nötigen DNS-Einträge an (Methode **CNAME**: zwei CNAME-Einträge, einer für den Traffic, einer `_acme-challenge` für das Zertifikat).

### 3. DNS bei STRATO eintragen

STRATO-Kundenlogin → Domains → `mathechecks.de` → **Subdomain anlegen**: `api`. Danach bei der Subdomain `api` unter **DNS** die beiden CNAME-Einträge aus Schritt 2 eintragen.

Anschließend in Deno Deploy **Provision Certificate** klicken und die Domain der App `mathechecks-api` zuweisen.

Test (aus einem beliebigen Netz):

```powershell
curl.exe https://api.mathechecks.de/health
```

### 4. Frontend umstellen

Erst wenn Schritt 3 erfolgreich ist, in `_config.yml` setzen:

```yaml
supabase_url: "https://api.mathechecks.de"
```

`supabase_auth_storage_key` bleibt unverändert. Dadurch nutzt der Browser weiter denselben Speicherplatz für die Anmeldung, und bestehende Logins bleiben beim Umstellen erhalten.

Zurück auf direkte Verbindung: `supabase_url` wieder auf `https://ysqpmtreljfdwtlvjzis.supabase.co` setzen.

## Lokal testen

```powershell
$env:SUPABASE_UPSTREAM_URL = "https://httpbin.org/anything"
deno run --allow-net --allow-env supabase\proxy\main.ts
curl.exe -X POST "http://localhost:8000/auth/v1/token?grant_type=password" -H "apikey: test" -d "{}"
```

`httpbin.org/anything` spiegelt die weitergeleitete Anfrage (Methode, Header, Body) zurück.
