# Recall-Modul – Design & Architektur

Hinweis: Dieses Dokument beschreibt den aktuellen Implementierungsstand des sichtbaren Moduls `Recall`.
Die geplante, feed-unabhängige Zielarchitektur für das überarbeitete Check-Modul und das neue lernbereichsweite Modul steht in `.github/konzept-recall-und-blurting.md`.

Dokumentation des aktuellen 3-Phasen-Recall-Moduls.


## Dateien

| Schicht | Pfad | Rolle |
|---|---|---|
| **JS** | `dev/assets/js/modules/recall.js` | Karten-Rendering, Phasensteuerung, Timer-Logik |
| **CSS** | `dev/assets/css/shared.css` → Abschnitte `recall-*`, `module-action-button`, `self-check-*` | Recall-spezifische Styles und geteilte UI-Bausteine |
| **Layout** | `_layouts/dev-module.html` | Gemeinsames Modul-Layout |
| **Daten** | `dev/checks.json` | Felder `Tipps`, `Ich kann`, `Schlagwort` pro Check |


## Lernfluss (3 Phasen + Ergebnis)

```
┌──────────────────────────────────────────────────────┐
│ Phase 1 – Recall (Abruf)                             │
│  Kompetenz dauerhaft sichtbar                        │
│  idle: nur Kompetenz + [Start]                       │
│  active: reine Denkphase + Timer (30 s)              │
│  → kein Notizfeld in Phase 1                         │
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│ Phase 2 – Memorize (Einprägen)                       │
│  Timer + Kernpunkte (aus check.Tipps) als Liste      │
│  Dauer: refCount × 5 s, min 10 s, max 45 s          │
│  → Button „Jetzt abrufen" nach Timer                 │
└───────────────────────┬──────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│ Phase 3 – Abrufen und Abgleichen                     │
│  N Eingabefelder (eines pro Tipp)                    │
│  danach Compare-Panel innerhalb derselben Phase      │
│  Dein Abruf (User-Eingaben als Pills)                │
│  Kernpunkte (Referenz-Pills aus check.Tipps)         │
│  Selbsteinschätzung: [✓ Kann ich] [↺ Noch nicht]    │
└─────────┬──────────────────────────────┬─────────────┘
          │ ✓ Kann ich                   │ ↺ Noch nicht
          ▼                              ▼
┌──────────────────┐    Zurück zu Phase 2 (Memorize)
│ Ergebnis         │    mit neuem Timer
│  Erfolgs-Screen  │
└──────────────────┘
```


## Datenfelder pro Check

| Feld in `checks.json` | Verwendung im Recall |
|---|---|
| `Tipps` (Array) | Kernpunkte in Phase 2 (Liste), Phase 3 (Anzahl Inputs), Compare-Panel (Referenz-Pills) |
| `Ich kann` | dauerhaft sichtbare Kompetenz im Fokus-Block |
| `Schlagwort` | Fallback-Titel der Karte |
| `recall.begriff` | Optionaler Titel-Override |


## Timer-Logik

```js
const RECALL_DELAY_MS = 30000; // Phase 1: 30 Sekunden

// Phase 2: dynamisch nach Anzahl Tipps
const memDuration = Math.min(Math.max(refCount * 5000, 10000), 45000);
```

Die Funktion `startTimerBar(scope, durationMs, btn)` wird für beide Phasen einheitlich verwendet:
- Animiert `recall-timer-bar__fill` per CSS-Transition von 100 % → 0 %
- Sperrt den zugehörigen Button (`module-action-button--locked`, `disabled`) bis zum Ablauf


## CSS-Klassen (Übersicht)

### Layout & Phasensteuerung

| Klasse | Zweck |
|---|---|
| `recall-focus` | dauerhaft sichtbarer Fokus-Block für die Kompetenz |
| `recall-prompt` | Anweisungstext pro Phase |
| `recall-action-row` | Flex-Container für Buttons |
| `module-action-button` | Aktionsbutton; in Recall amber, in Feynman modulär überschrieben |
| `module-action-button--locked` | Gesperrt-Zustand (Opacity + pointer-events) |
| `recall-competence` | Kompetenz-Anzeige (kursiv im Fokus-Block) |

### Timer

| Klasse | Zweck |
|---|---|
| `recall-timer-bar` | äußerer Container mit Glow-/Gradient-Rahmen |
| `recall-timer-bar__fill` | animierter Füllbalken mit Gradient |

### Kernpunkte (Phase 2)

| Klasse | Zweck |
|---|---|
| `recall-list-items` | Grid-Container für Kernpunkt-Einträge |
| `recall-list-item` | Einzelner Kernpunkt (Rahmen, abgerundet) |
| `recall-list-dot` | Amber-Punkt vor jedem Eintrag |
| `recall-list-text` | Textinhalt des Eintrags |
| `recall-no-refs` | Hinweis „Keine Kernpunkte hinterlegt." |

### Eingabe (Phase 3)

| Klasse | Zweck |
|---|---|
| `recall-input-slots` | Grid-Container für Eingabefelder |
| `recall-input-slot` | Einzelnes Eingabefeld (Modul-Farbe Border + Focus-Glow) |

### Vergleich innerhalb von Phase 3

| Klasse | Zweck |
|---|---|
| `recall-compare-panel` | eingeblendeter Compare-Bereich innerhalb von Phase 3 |
| `recall-divider` | Trennlinie mit Label (z. B. „Dein Abruf", „Kernpunkte") |
| `recall-user-notes` | Container für User-Eingaben |
| `recall-user-entries` | Flex-Wrap-Container für User-Pills |
| `recall-keyword` | Einzelner Keyword-Pill (Referenz) |
| `recall-keyword-dot` | Punkt im Keyword-Pill |
| `recall-keyword--user` | Modifier: User-Eingabe-Pill (Amber-Hintergrund) |
| `recall-keywords` | Flex-Wrap-Container für Referenz-Pills |

### Selbsteinschätzung in Phase 3

| Klasse | Zweck |
|---|---|
| `self-check-label` | Label zur Selbsteinschätzung der Kompetenz |
| `self-check-actions` | Flex-Container für die zwei Buttons |
| `self-check-button` | Einzelner Selbsteinschätzungs-Button |
| `self-check-button.yes` | Grüner Button „Kann ich" |
| `self-check-button.no` | Amber-Button „Noch nicht" |
| `self-check-button__icon` | Icon (✓ / ↺) |
| `self-check-button__title` | Titel im Button |
| `self-check-button__sub` | Erklärungstext im Button |

### Ergebnis

Nutzt die gemeinsamen `outcome`-Klassen (`oc-icon`, `oc-title`, `oc-sub`), die auch von Feynman verwendet werden.


## HTML-Datenattribute

| Attribut | Element | Zweck |
|---|---|---|
| `data-recall-card` | `article` | Identifiziert eine Recall-Karte |
| `data-recall-check-viewport` | `section` | Viewport-Container mit `data-check-id` und `data-recall-ref-count` |
| `data-recall-stage="…"` | `div` | Phasen-Container (`recall`, `memorize`, `retrieve`, `result-yes`) |
| `data-recall-idle` | `div` | Sub-State: Start-Button-Ansicht |
| `data-recall-active` | `div` | Sub-State: Denkphase + Timer |
| `data-recall-start` | `button` | Start-Button (Phase 1 idle → active) |
| `data-recall-to-memorize` | `button` | Weiter-Button (Phase 1 → 2) |
| `data-recall-to-retrieve` | `button` | Weiter-Button (Phase 2 → 3) |
| `data-recall-to-compare` | `button` | Compare-Button innerhalb von Phase 3 |
| `data-recall-compare-panel` | `div` | eingeblendeter Compare-Bereich innerhalb von Phase 3 |
| `data-recall-answer="yes/no"` | `button` | Selbsteinschätzung (Phase 3 → Ergebnis oder → 2) |
| `data-recall-timer-bar="…"` | `div` | Timer-Bar-Container (`recall` / `memorize`) |
| `data-recall-timer-fill="…"` | `div` | Timer-Füllbalken |
| `data-recall-input-slots` | `div` | Container der Eingabefelder |
| `data-recall-slot="N"` | `input` | Einzelnes Eingabefeld (Index) |
| `data-recall-user-notes` | `div` | Platzhalter für User-Eingaben im Compare-Bereich |


## Modul-Farbe

Das Recall-Modul nutzt Amber als Systemfarbe:

```css
--mt-recall-rgb: 245, 166, 35
--mt-recall: var(--amber)
--mt-recall-soft: var(--amber-soft)
```

Abgeleitete Transparenzen werden inline per `rgba(var(--mt-recall-rgb), .22)` etc. gebildet.
