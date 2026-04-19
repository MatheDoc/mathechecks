# Blurting-Modul – Design & Architektur

Dokumentation des 5-Phasen-Blurting-Moduls (Spaced Retrieval).


## Dateien

| Schicht | Pfad | Rolle |
|---|---|---|
| **JS** | `dev/assets/js/modules/blurting.js` | Karten-Rendering, Phasensteuerung, Timer-Logik |
| **CSS** | `dev/assets/css/shared.css` → Abschnitt `bl-*` | Blurting-spezifische Styles |
| **Layout** | `_layouts/dev-module.html` | Gemeinsames Modul-Layout |
| **Daten** | `dev/checks.json` | Felder `Tipps`, `Ich kann`, `Schlagwort` pro Check |


## Lernfluss (5 Phasen)

```
┌──────────────────────────────────────────────────────┐
│ Phase 1 – Recall (Abruf)                             │
│  idle: Prompt + [Start]-Button                       │
│  active: Kompetenz (Ich kann) + Timer (30 s)         │
│  → Button „Weiter" wird nach Timer-Ablauf freigegeben│
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│ Phase 2 – Memorize (Einprägen)                       │
│  Timer + Kernpunkte (aus check.Tipps) als Liste      │
│  Dauer: refCount × 5 s, min 10 s, max 45 s          │
│  → Button „Weiter" gesperrt bis Timer abgelaufen     │
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│ Phase 3 – Retrieve (Abrufen)                         │
│  N Eingabefelder (eines pro Tipp)                    │
│  → Button „Jetzt vergleichen"                        │
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│ Phase 4 – Compare (Vergleichen)                      │
│  Deine Notizen (User-Eingaben als Pills)             │
│  Kernpunkte (Referenz-Pills aus check.Tipps)         │
│  Selbsteinschätzung: [✓ Kann ich] [↺ Noch nicht]    │
└─────────┬──────────────────────────────┬─────────────┘
          │ ✓ Kann ich                   │ ↺ Noch nicht
          ▼                              ▼
┌──────────────────┐    Zurück zu Phase 2 (Memorize)
│ Phase 5 – Result │    mit neuem Timer
│  Erfolgs-Screen  │
└──────────────────┘
```


## Datenfelder pro Check

| Feld in `checks.json` | Verwendung im Blurting |
|---|---|
| `Tipps` (Array) | Kernpunkte in Phase 2 (Liste), Phase 3 (Anzahl Inputs), Phase 4 (Referenz-Pills) |
| `Ich kann` | Kompetenzanzeige in Phase 1 (nach Start-Klick) |
| `Schlagwort` | Fallback-Titel der Karte |
| `blurting.begriff` | Optionaler Titel-Override |


## Timer-Logik

```js
const BL_RECALL_DELAY_MS = 30000; // Phase 1: 30 Sekunden

// Phase 2: dynamisch nach Anzahl Tipps
const memDuration = Math.min(Math.max(refCount * 5000, 10000), 45000);
```

Die Funktion `startTimerBar(scope, durationMs, btn)` wird für beide Phasen einheitlich verwendet:
- Animiert `bl-timer-bar__fill` per CSS-Transition von 100 % → 0 %
- Sperrt den zugehörigen Button (`bl-reveal-btn--locked`, `disabled`) bis zum Ablauf


## CSS-Klassen (Übersicht)

### Layout & Phasensteuerung

| Klasse | Zweck |
|---|---|
| `bl-prompt` | Anweisungstext pro Phase |
| `bl-action-row` | Flex-Container für Buttons |
| `bl-reveal-btn` | Phasen-Button (Modul-Farbe Amber) |
| `bl-reveal-btn--locked` | Gesperrt-Zustand (Opacity + pointer-events) |
| `bl-kompetenz` | Kompetenz-Anzeige (kursiv, kein Rahmen) |

### Timer

| Klasse | Zweck |
|---|---|
| `bl-timer-bar` | Äußerer Container (6 px Höhe, abgerundet) |
| `bl-timer-bar__fill` | Animierter Füllbalken (Amber, 55 % Opacity) |

### Kernpunkte (Phase 2)

| Klasse | Zweck |
|---|---|
| `bl-list-items` | Grid-Container für Kernpunkt-Einträge |
| `bl-list-item` | Einzelner Kernpunkt (Rahmen, abgerundet) |
| `bl-list-dot` | Amber-Punkt vor jedem Eintrag |
| `bl-list-text` | Textinhalt des Eintrags |
| `bl-no-refs` | Hinweis „Keine Kernpunkte hinterlegt." |

### Eingabe (Phase 3)

| Klasse | Zweck |
|---|---|
| `bl-input-slots` | Grid-Container für Eingabefelder |
| `bl-input-slot` | Einzelnes Eingabefeld (Modul-Farbe Border + Focus-Glow) |

### Vergleich (Phase 4)

| Klasse | Zweck |
|---|---|
| `bl-divider` | Trennlinie mit Label (z. B. „Deine Notizen", „Kernpunkte") |
| `bl-user-notes` | Container für User-Eingaben |
| `bl-user-entries` | Flex-Wrap-Container für User-Pills |
| `bl-kw` | Einzelner Keyword-Pill (Referenz) |
| `bl-kwdot` | Punkt im Keyword-Pill |
| `bl-kw--user` | Modifier: User-Eingabe-Pill (Amber-Hintergrund) |
| `bl-kws` | Flex-Wrap-Container für Referenz-Pills |

### Selbsteinschätzung (Phase 4)

| Klasse | Zweck |
|---|---|
| `bl-selbst-lbl` | Label „Wie vollständig war dein Abruf?" |
| `bl-selbst-btns` | Flex-Container für die zwei Buttons |
| `bl-sb` | Einzelner Selbsteinschätzungs-Button |
| `bl-sb.yes` | Grüner Button „Kann ich" |
| `bl-sb.no` | Amber-Button „Noch nicht" |
| `bl-sb-icon` | Icon (✓ / ↺) |
| `bl-sb-title` | Titel im Button |
| `bl-sb-sub` | Erklärungstext im Button |

### Ergebnis (Phase 5)

Nutzt die gemeinsamen `outcome`-Klassen (`oc-icon`, `oc-title`, `oc-sub`), die auch von Feynman verwendet werden.


## HTML-Datenattribute

| Attribut | Element | Zweck |
|---|---|---|
| `data-bl-card` | `article` | Identifiziert eine Blurting-Karte |
| `data-bl-check-viewport` | `section` | Viewport-Container mit `data-check-id` und `data-bl-ref-count` |
| `data-bl-stage="…"` | `div` | Phasen-Container (`recall`, `memorize`, `retrieve`, `compare`, `result-yes`) |
| `data-bl-recall-idle` | `div` | Sub-State: Start-Button-Ansicht |
| `data-bl-recall-active` | `div` | Sub-State: Kompetenz + Timer |
| `data-bl-start` | `button` | Start-Button (Phase 1 idle → active) |
| `data-bl-to-memorize` | `button` | Weiter-Button (Phase 1 → 2) |
| `data-bl-to-retrieve` | `button` | Weiter-Button (Phase 2 → 3) |
| `data-bl-to-compare` | `button` | Vergleichs-Button (Phase 3 → 4) |
| `data-bl-answer="yes/no"` | `button` | Selbsteinschätzung (Phase 4 → 5 oder → 2) |
| `data-bl-timer-bar="…"` | `div` | Timer-Bar-Container (`recall` / `memorize`) |
| `data-bl-timer-fill="…"` | `div` | Timer-Füllbalken |
| `data-bl-input-slots` | `div` | Container der Eingabefelder |
| `data-bl-slot="N"` | `input` | Einzelnes Eingabefeld (Index) |
| `data-bl-user-notes` | `div` | Platzhalter für User-Eingaben in Phase 4 |


## Modul-Farbe

Das Blurting-Modul nutzt Amber als Systemfarbe:

```css
--mt-blurting-rgb: 245, 166, 35
--mt-blurting: var(--amber)
--mt-blurting-soft: var(--amber-soft)
```

Abgeleitete Transparenzen werden inline per `rgba(var(--mt-blurting-rgb), .22)` etc. gebildet.
