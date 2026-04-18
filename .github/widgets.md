# Skript-Widgets

Interaktive Visualisierungen innerhalb von `skript.md`-Dateien.
Widgets werden per `{% include dev/widgets/widget-*.html %}` eingebunden und über Slider/Checkboxen gesteuert.


## Dateien

| Schicht | Pfad | Rolle |
|---|---|---|
| **HTML** | `_includes/dev/widgets/widget-*.html` | Markup (Slider, Labels, Plot-Container) |
| **CSS** | `dev/assets/css/shared.css` → Abschnitt *Skript-Widget System* | Layout, Panel-Styling, Dark-Mode |
| **JS – Logik** | `dev/assets/js/modules/skript-visuals.js` | Event-Handling, Slider → Figure-Builder → Plotly-Render |
| **JS – Visuals** | `dev/assets/js/visuals/*.js` | Figure-Builder (Daten + Layout für Plotly) |
| **JS – Plotly** | `dev/assets/js/visuals/plotly-defaults.js` | `plotlyRender()`, `themeTextColor()`, shared Defaults |


## Widgets

| Widget | Include | CSS-Selektor | Outputs |
|---|---|---|---|
| Histogramm binomial | `widget-histogramm-binomial.html` | `.hb-widget` | Einzel- und kumuliertes Histogramm |
| Baumdiagramm binomial | `widget-baumdiagramm-binomial.html` | `.bb-widget` | Baumdiagramm + Bernoulli-Formel |
| Baumdiagramme & Vierfeldertafel | `widget-baumdiagramme-vierfeldertafel.html` | `.bvt-widget` | 2 Baumdiagramme + Vierfeldertafel |
| Lineare Funktionen | `widget-lineare-funktionen.html` | `.lf-widget` | Graph + Wertetabelle |
| Quadratische Funktionen | `widget-quadratische-funktionen.html` | `.qf-widget` | Graph + Wertetabelle + Formel |
| Quadratische Funktionen Parameter | `widget-quadratische-funktionen-parameter.html` | `.qfp-widget` | Graph + Scheitel + Formel |


## HTML-Struktur

Jedes Widget folgt demselben Aufbau:

```html
<div class="skript-widget [skript-widget--aside] <prefix>-widget">
    <div class="widget-controls">
        <div class="widget-row">
            <label>… <span class="<prefix>-wert"></span></label>
            <input type="range" class="<prefix>-slider" …>
        </div>
        <!-- weitere widget-row / widget-row--center / widget-row--label / widget-info -->
    </div>

    <div class="widget-outputs">
        <div class="<prefix>-plot diagramm"></div>
        <!-- ggf. weitere Outputs (Tabelle, zweiter Plot) -->
    </div>
</div>
```

### CSS-Klassen

| Klasse | Funktion |
|---|---|
| `.skript-widget` | Flex-Container (column), Margin, Gap |
| `.skript-widget--aside` | Ab 900 px: Controls links, Outputs rechts (row) |
| `.widget-controls` | Panel mit Rand, Hintergrund `--panel-solid`, Schatten |
| `.widget-row` | Zeile: Label + Slider, space-between |
| `.widget-row--center` | Zentrierter Inhalt (z. B. Formelausgabe) |
| `.widget-row--label` | Reine Textzeile, kleiner, `--text-dim` |
| `.widget-info` | Info-Block unter den Slidern |
| `.widget-outputs` | Flex-Wrap für Diagramme/Tabellen |
| `.diagramm` | Plotly-Container (flex: 1 1 420px, max-width: 600px) |

### Modifier-Konventionen

- `--aside`: Nur für Widgets verwenden, bei denen Controls + Outputs nebeneinander sinnvoll sind (z. B. `bb-widget`, `lf-widget`).
- Widget-spezifische Overrides über den Widget-Selektor (z. B. `.bb-widget .diagramm { max-width: 800px }`).


## JS-Architektur

### Figure-Builder (`dev/assets/js/visuals/`)

Reine Funktionen: Eingabe-Parameter → `{ data, layout }` Objekt.
Kein DOM-Zugriff, kein Plotly-Aufruf.

Beispiele:
- `buildHistogrammEinzelnFigure({ n, p, a, b, titel, autoY })`
- `buildBaumdiagrammBinomialFigure({ n, p, k })`
- `buildGraphFigure({ funktionen, punkte, flaechen, … })`

### plotlyRender (`plotly-defaults.js`)

Wrapper um `Plotly.newPlot()`. Merged automatisch:
- Transparenter Hintergrund
- `dragmode: false`, Toolbar ausgeblendet
- Schriftfarbe aus `themeTextColor()` (liest CSS `--text`)
- Achsen-Defaults (tickfont, titlefont, gridcolor, zerolinecolor)
- Touch-Scroll-Fix (verhindert Scroll-Blocking auf Mobilgeräten)

### skript-visuals.js

Einstiegspunkt: `initSkriptVisuals(root)`.
- Findet alle Widget-Container via CSS-Klasse (`.hb-widget`, `.lf-widget`, …)
- Bindet Slider-Events → ruft Figure-Builder → `plotlyRender()`
- Findet auch statische Plotly-Blöcke (`.baumdiagramm-auto`, `.histogramm-einzel-auto`, …) und rendert sie


## Dark-Mode

- CSS-Variablen (`--text`, `--panel-solid`, `--border`, `--surface-hi`) werden per `.light`-Klasse auf `<html>` umgeschaltet.
- `themeTextColor()` liest `--text` zur Renderzeit.
- Theme-Toggle löst `location.reload()` aus, damit Plotly-Farben neu berechnet werden.


## Neues Widget anlegen

1. HTML-Include in `_includes/dev/widgets/widget-<name>.html` mit Standard-Markup (s. o.)
2. Figure-Builder in `dev/assets/js/visuals/<name>.js` – exportiert eine `build*Figure()`-Funktion
3. Handler-Block in `skript-visuals.js`: Container suchen, Slider-Events binden, Builder + `plotlyRender()` aufrufen
4. Falls nötig: Widget-spezifisches CSS in `shared.css` unterhalb des Widget-System-Blocks
5. In `skript.md` einbinden: `{% include dev/widgets/widget-<name>.html %}`
