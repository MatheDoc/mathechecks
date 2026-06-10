/**
 * pen-overlay.js
 * Stift-Overlay für MatheChecks-Modulseiten.
 *
 * Werkzeuge: Stift · Textmarker · Lasso · Radierer
 * Stift-Farben:  Blau, Grün, Rot, Orange
 * Marker-Farben: Gelb, Grün, Türkis, Hellrot
 *
 * Shortcuts: P Stift · M Marker · L Lasso · E Radierer
 *            Ctrl+Z Rückgängig · Entf/Backspace Selektion löschen · Esc Abbrechen
 *
 * Scratch-to-Erase: Zickzack-Kratzen mit dem Stift löscht gekreuzte Striche.
 */

// ─── DOM ──────────────────────────────────────────────────────────────────────
const canvas = /** @type {HTMLCanvasElement} */ (document.getElementById('pen-canvas'));
if (!canvas) throw new Error('pen-canvas fehlt');
const ctx = canvas.getContext('2d');

// Scroll-Container: .mod-main hat overflow-y: auto auf Modulseiten
const scrollEl = document.querySelector('.mod-main')
               || document.scrollingElement
               || document.documentElement;

// ─── Off-screen-Buffer für Marker-Rendering ───────────────────────────────────
let markerBuf    = /** @type {OffscreenCanvas|null} */ (null);
let markerBufCtx = /** @type {OffscreenCanvasRenderingContext2D|null} */ (null);

// ─── Konstanten ───────────────────────────────────────────────────────────────
const MARKER_WIDTH = 20;
const MARKER_ALPHA = 0.46;
const PEN_BASE_W   = 3;
const ERASER_WIDTH = 28;

// ─── Cursor-SVGs (dynamisch, farbabhängig) ────────────────────────────────────
// _cur() kodiert das SVG genau einmal. Daher in den SVG-Strings literale Zeichen
// (#, <, >, ') und rohe Hex-Farben verwenden – kein Vor-Encoding.
function _cur(svg, hx, hy) {
  return `url("data:image/svg+xml,${encodeURIComponent(svg)}") ${hx} ${hy}, auto`;
}

function _cursorPen(color) {
  // Stift: Korpus in gewählter Farbe, Spitze (Hotspot) unten-links.
  return _cur(
    `<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24'>`
    + `<path d='M5 19L7.4 13.4L15.4 5.4a2.1 2.1 0 0 1 3 3L10.6 16.4L5 19Z' fill='${color}' stroke='#ffffff' stroke-width='1.4' stroke-linejoin='round'/>`
    + `<path d='M5 19L6.2 16.3L7.7 17.8L5 19Z' fill='#222222' stroke='#ffffff' stroke-width='0.6' stroke-linejoin='round'/>`
    + `</svg>`,
    4, 19
  );
}

function _cursorMarker(color) {
  // Marker: stilisierter Highlighter mit breiter Keilspitze in gewählter Farbe.
  // Hotspot an der unteren Mitte der breiten Spitze.
  return _cur(
    `<svg xmlns='http://www.w3.org/2000/svg' width='26' height='26'>`
    // Schaft (neutral, grau)
    + `<path d='M16.5 4.2L21.8 9.5L13.7 17.6L8.4 12.3Z' fill='#d7d7df' stroke='#ffffff' stroke-width='1.2' stroke-linejoin='round'/>`
    // breite Spitze in Farbe
    + `<path d='M8.4 12.3L13.7 17.6L9.6 21.7L3.2 21.7L2.6 18.1Z' fill='${color}' stroke='#ffffff' stroke-width='1.2' stroke-linejoin='round'/>`
    // Abrisskante der Spitze (dunkel)
    + `<path d='M2.6 18.1L9.6 21.7L3.2 21.7Z' fill='#222222' fill-opacity='0.55'/>`
    + `</svg>`,
    3, 21
  );
}

function _cursorEraser() {
  return _cur(
    `<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><rect x='1' y='5' width='18' height='11' rx='2' fill='#f8d7c4' stroke='#cc4455' stroke-width='1.5'/><line x1='1' y1='11' x2='19' y2='11' stroke='#cc4455' stroke-width='1'/></svg>`,
    10, 10
  );
}

function _cursorLasso() {
  return _cur(
    `<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><ellipse cx='10' cy='8' rx='7' ry='5' fill='none' stroke='#ffffff' stroke-width='3'/><ellipse cx='10' cy='8' rx='7' ry='5' fill='none' stroke='#222222' stroke-width='1.5' stroke-dasharray='3 2'/><line x1='10' y1='13' x2='10' y2='20' stroke='#ffffff' stroke-width='3' stroke-linecap='round'/><line x1='10' y1='13' x2='10' y2='20' stroke='#222222' stroke-width='1.5' stroke-linecap='round'/></svg>`,
    10, 8
  );
}

function applyToolCursor() {
  const body = document.body;
  if (!penMode) { body.style.removeProperty('--pen-cursor'); return; }
  const cursors = {
    pen:    _cursorPen(penColor),
    marker: _cursorMarker(markerColor),
    eraser: _cursorEraser(),
    lasso:  _cursorLasso(),
  };
  body.style.setProperty('--pen-cursor', cursors[activeTool] ?? 'crosshair');
}

// Scratch-to-Erase-Schwellen. Die Analyse tastet den jüngsten Pfadabschnitt
// nach Bogenlänge neu ab (abtastraten-unabhängig). Unterscheidungsmerkmal
// Kratzen ↔ Schreiben: Kratzen faltet sich stark (Weglänge ≫ Bounding-Box)
// und hat viele Richtungsumkehrungen; Schreiben schreitet voran.
const SCRATCH_SCAN_LEN      = 320;  // betrachtete Pfadlänge am Strichende (px)
const SCRATCH_STEP          = 10;   // Neu-Abtast-Schritt nach Bogenlänge (px)
const SCRATCH_MIN_REVERSALS = 4;    // Richtungsumkehrungen (dominante Achse)
const SCRATCH_MIN_PATH      = 80;   // Mindest-Weglänge im Abschnitt (px)
const SCRATCH_MIN_FOLD      = 1.7;  // Weglänge / Bounding-Box-Diagonale (Faltung)
const ERASE_HIT_RADIUS      = 14;   // Trefferradius um den Kratzpfad (px)

// ─── State ────────────────────────────────────────────────────────────────────
let penMode     = false;
let activeTool  = 'pen';   // 'pen' | 'marker' | 'lasso' | 'eraser'
let penColor    = '#3b82f6';
let markerColor = '#ffe600';
let drawing     = false;
let _clipTop    = 0;       // Oberkante des Clip-Bereichs, pro redraw() berechnet
let _capturedPid = /** @type {number|null} */ (null); // gefangener Pointer (Pen/Maus)

/**
 * @typedef {{ x: number, y: number, w: number }} Point
 * @typedef {{ tool: string, color: string, points: Point[], anchorEl: Element|null, clipEls: Element[] }} Stroke
 */

/** @type {Stroke[]} */
let strokes = [];

/** @type {Stroke|null} */
let liveStroke = null;

// Lasso
/** @type {{ x: number, y: number }[]} */
let lassoPoints  = [];
let lassoClosed  = false;
/** @type {Set<number>} */
let selectedIds  = new Set();
/** @type {{ startX: number, startY: number, origStrokes: Map<number, Point[]>, origLasso: { x: number, y: number }[] }|null} */
let dragState    = null;

// ─── Canvas-Größe ─────────────────────────────────────────────────────────────
function syncSize() {
  const W = window.innerWidth;
  const H = window.innerHeight;
  if (canvas.width === W && canvas.height === H) return;
  canvas.width  = W;
  canvas.height = H;
  markerBuf     = new OffscreenCanvas(W, H);
  markerBufCtx  = markerBuf.getContext('2d');
  redraw();
}

window.addEventListener('resize', syncSize, { passive: true });
new ResizeObserver(syncSize).observe(document.documentElement);
syncSize();

// Beliebige Scroll-Quelle (auch verschachtelte Container) abfangen.
window.addEventListener('scroll', onAnyScroll, { passive: true, capture: true });

function onAnyScroll() {
  // Selektion löst sich beim Scrollen vom Inhalt → aufheben.
  if (selectedIds.size || lassoPoints.length) clearSelection();
  redraw();
}

// ─── Anker-System ─────────────────────────────────────────────────────────────
// Jeder Strich wird an das tiefste Inhaltselement unter dem Zeiger gebunden.
// Dieses Element liegt innerhalb evtl. scrollender Karten-Bodys und wandert
// daher per getBoundingClientRect() korrekt mit Scroll (auch verschachtelt),
// Zoom und Fenstergrößen-Änderung mit.
const ANCHOR_ROOT_SEL = '.mod-content';

/**
 * Findet das tiefste hit-testbare Inhaltselement an einer Viewport-Position.
 * Der Canvas ist pointer-events:none, daher liefert elementsFromPoint direkt
 * die Inhaltsknoten (Canvas und reine Deko werden nicht zurückgegeben).
 */
function findAnchorEl(clientX, clientY) {
  const content = document.querySelector(ANCHOR_ROOT_SEL);
  const stack = document.elementsFromPoint(clientX, clientY);

  for (let el of stack) {
    if (!el || el === canvas) continue;
    if (el.closest && (el.closest('#pen-toolbar') || el.closest('#pen-lasso-hint'))) continue;
    if (!el.closest || !el.closest(ANCHOR_ROOT_SEL)) continue;
    // MathJax-Interna werden bei Re-Typeset ersetzt → auf stabilen Eltern-Block.
    const mjx = el.closest('mjx-container');
    if (mjx && mjx.parentElement && mjx.parentElement.closest(ANCHOR_ROOT_SEL)) {
      el = mjx.parentElement;
    }
    return el;
  }
  return content || null;
}

/** Aktueller Viewport-Versatz eines Ankers (Fallback: Scroll-Container). */
function anchorOffset(anchorEl) {
  if (anchorEl && anchorEl.isConnected) {
    const r = anchorEl.getBoundingClientRect();
    return { ox: r.left, oy: r.top };
  }
  return { ox: 0, oy: -scrollEl.scrollTop };
}

/** Gespeicherte (anker-relative) Punkte → aktuelle Viewport-Koordinaten. */
function strokeViewportPoints(s) {
  const { ox, oy } = anchorOffset(s.anchorEl);
  return s.points.map(p => ({ x: p.x + ox, y: p.y + oy, w: p.w }));
}

// ─── Clipping ─────────────────────────────────────────────────────────────────
// Ein einzelner globaler Canvas kann per z-index nicht zwischen Kartenkörper
// und Karten-Header geschoben werden (Karten/Inhalt bilden eigene Stacking-
// Contexts). Stattdessen begrenzen wir jeden Strich beim Zeichnen auf seinen
// Scroll-/Inhaltsbereich: Anmerkungen erscheinen so nie über Karten-Header,
// Check-Nav oder außerhalb des scrollenden Karten-Bodys.
const CLIP_OVERFLOW_RE = /(auto|scroll|hidden|clip)/;

/** Sammelt alle clippenden Vorfahren (overflow ≠ visible) eines Elements. */
function collectClipAncestors(el) {
  const list = [];
  let node = el;
  while (node && node !== document.body && node !== document.documentElement) {
    const st = getComputedStyle(node);
    if (CLIP_OVERFLOW_RE.test(st.overflowY) || CLIP_OVERFLOW_RE.test(st.overflowX)) {
      list.push(node);
    }
    node = node.parentElement;
  }
  return list;
}

/** Oberkante des erlaubten Zeichenbereichs: unter den oberen Sticky-Leisten. */
function contentClipTop() {
  let top = 0;
  for (const sel of ['.topbar', '.mod-tab-nav', '.check-jump-nav-wrap']) {
    const el = document.querySelector(sel);
    if (!el) continue;
    const r = el.getBoundingClientRect();
    if (r.height > 0 && r.bottom > top) top = r.bottom;
  }
  return top;
}

/** Sichtbares Clip-Rechteck eines Strichs (Schnitt aller Clip-Vorfahren). */
function computeStrokeClip(s) {
  let left = 0, top = 0, right = canvas.width, bottom = canvas.height;
  const els = s.clipEls || [];
  for (const el of els) {
    if (!el.isConnected) continue;
    const r = el.getBoundingClientRect();
    if (r.left   > left)   left   = r.left;
    if (r.top    > top)    top    = r.top;
    if (r.right  < right)  right  = r.right;
    if (r.bottom < bottom) bottom = r.bottom;
  }
  if (_clipTop > top) top = _clipTop;
  if (right <= left || bottom <= top) return null; // nichts sichtbar
  return { left, top, right, bottom };
}

// Inhaltswechsel (z. B. neue Trainingsaufgabe) → verwaiste Striche entfernen.
const _contentRoot = document.querySelector('.mod-content') || document.body;
let _pruneScheduled = false;
const _contentObserver = new MutationObserver(() => {
  if (_pruneScheduled) return;
  _pruneScheduled = true;
  requestAnimationFrame(() => {
    _pruneScheduled = false;
    pruneOrphanStrokes();
  });
});
_contentObserver.observe(_contentRoot, { childList: true, subtree: true });

function pruneOrphanStrokes() {
  const before = strokes.length;
  strokes = strokes.filter(s => !s.anchorEl || s.anchorEl.isConnected);
  if (strokes.length !== before) clearSelection();
  redraw();
}

// ─── Rendering ────────────────────────────────────────────────────────────────
function redraw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  _clipTop = contentClipTop();

  for (let i = 0; i < strokes.length; i++) {
    const s = strokes[i];
    if (s.anchorEl && !s.anchorEl.isConnected) continue; // verwaist → nicht zeichnen
    renderStroke(ctx, s, selectedIds.has(i));
  }
  if (liveStroke) renderStroke(ctx, liveStroke, false);
  if (lassoPoints.length > 1) renderLasso();
}

/** Rendert einen Strich in aktuellen Viewport-Koordinaten (anker-bezogen). */
function renderStroke(c, s, selected) {
  const pts = strokeViewportPoints(s);
  if (pts.length < 2) return;

  const clip = computeStrokeClip(s);
  if (clip === null) return;          // vollständig hinter Header/Nav/Rand
  c.save();
  c.beginPath();
  c.rect(clip.left, clip.top, clip.right - clip.left, clip.bottom - clip.top);
  c.clip();

  if (s.tool === 'marker')      renderMarker(c, pts, s.color, selected);
  else if (s.tool === 'eraser') renderEraser(c, pts);
  else                          renderPen(c, pts, s.color, selected);

  c.restore();
}

/** Stift-Strich. */
function renderPen(c, pts, color, selected) {
  c.save();
  c.lineCap     = 'round';
  c.lineJoin    = 'round';
  c.strokeStyle = selected ? 'rgba(124,106,255,1)' : color;
  c.globalAlpha = 1;
  c.beginPath();
  c.moveTo(pts[0].x, pts[0].y);
  for (let i = 1; i < pts.length; i++) {
    c.lineWidth = pts[i].w;
    if (i < pts.length - 1) {
      const mx = (pts[i].x + pts[i + 1].x) / 2;
      const my = (pts[i].y + pts[i + 1].y) / 2;
      c.quadraticCurveTo(pts[i].x, pts[i].y, mx, my);
    } else {
      c.lineTo(pts[i].x, pts[i].y);
    }
  }
  c.stroke();
  c.restore();
}

/**
 * Textmarker: Off-screen-Canvas verhindert Alpha-Akkumulation innerhalb
 * eines Strichs → gleichmäßige, flache Deckung wie ein echter Textmarker.
 */
function renderMarker(c, pts, color, selected) {
  if (!markerBuf || !markerBufCtx) return;
  const mc = markerBufCtx;
  mc.clearRect(0, 0, markerBuf.width, markerBuf.height);
  mc.save();
  mc.lineCap     = 'square';
  mc.lineJoin    = 'bevel';
  mc.lineWidth   = MARKER_WIDTH;
  mc.strokeStyle = selected ? 'rgb(124,106,255)' : color;
  mc.globalAlpha = 1;
  mc.beginPath();
  mc.moveTo(pts[0].x, pts[0].y);
  for (const pt of pts.slice(1)) mc.lineTo(pt.x, pt.y);
  mc.stroke();
  mc.restore();

  c.save();
  c.globalAlpha = selected ? 0.64 : MARKER_ALPHA;
  c.drawImage(markerBuf, 0, 0);
  c.restore();
}

function renderEraser(c, pts) {
  c.save();
  c.globalCompositeOperation = 'destination-out';
  c.lineCap     = 'round';
  c.lineJoin    = 'round';
  c.strokeStyle = 'rgba(0,0,0,1)';
  c.beginPath();
  c.moveTo(pts[0].x, pts[0].y);
  for (const pt of pts.slice(1)) {
    c.lineWidth = pt.w;
    c.lineTo(pt.x, pt.y);
  }
  c.stroke();
  c.restore();
}

function renderLasso() {
  ctx.save();
  ctx.strokeStyle = 'rgba(124,106,255,0.88)';
  ctx.fillStyle   = 'rgba(124,106,255,0.07)';
  ctx.lineWidth   = 1.5;
  ctx.setLineDash([5, 4]);
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(lassoPoints[0].x, lassoPoints[0].y);
  for (let i = 1; i < lassoPoints.length; i++) {
    ctx.lineTo(lassoPoints[i].x, lassoPoints[i].y);
  }
  if (lassoClosed) ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

// ─── Pointer-Events ───────────────────────────────────────────────────────────
// OneNote-Systematik: Finger (touch) scrollt immer, Maus/Stylus zeichnet.
// Der Canvas selbst ist pointer-events:none → Touch erreicht den Inhalt und
// scrollt verschachtelte Container nativ. Gezeichnet wird nur bei mouse/pen.
window.addEventListener('pointerdown',   onDown, true);
window.addEventListener('pointermove',   onMove, true);
window.addEventListener('pointerup',     onUp,   true);
window.addEventListener('pointercancel', onUp,   true);
window.addEventListener('click',         onClickGuard, true);

// Eingabeart-Sonde: Sobald ein Stift (oder die Maus) den Inhalt überfährt –
// auch nur im Hover, bevor er aufsetzt – sperren wir das Scrollen des Inhalts
// (touch-action:none), damit der Stift zeichnet statt zu scrollen. Ein
// Finger setzt sofort zurück, sodass Touch weiterhin nativ scrollt.
// Die Hover-Events des Stylus liefern den nötigen Vorlauf, bevor er aufsetzt –
// nur dann greift touch-action zuverlässig für die folgende Geste.
window.addEventListener('pointerover', onPointerProbe, true);
window.addEventListener('pointermove', onPointerProbe, true);
window.addEventListener('pointerdown', onPointerProbe, true);

/** Nur Maus und Stylus zeichnen – Finger-Touch bleibt fürs Scrollen frei. */
function isDrawingPointer(e) {
  return e.pointerType === 'mouse' || e.pointerType === 'pen';
}

/** Schaltet die Inhalts-Scrollsperre (CSS-Klasse → touch-action:none). */
function setPenInputActive(active) {
  document.body.classList.toggle('pen-input-active', penMode && active);
}

/** Aktualisiert die Scrollsperre anhand der zuletzt gesehenen Eingabeart. */
function onPointerProbe(e) {
  if (!penMode) return;
  if (e.pointerType === 'touch') setPenInputActive(false);
  else if (isDrawingPointer(e))  setPenInputActive(true);
}

/** Liegt das Ziel in der Stift-UI (Toolbar/Hinweis)? Dann nicht zeichnen. */
function isPenUiTarget(e) {
  const t = e.target;
  return !!(t && t.closest && t.closest('#pen-toolbar, #pen-lasso-hint'));
}

/**
 * Fängt den Pointer (nur Maus/Stylus) für die Dauer eines Strichs.
 * Das unterdrückt die Browser-eigene Scroll-/Pan-Geste, die sonst einen
 * Stift-Strich nach kurzer Strecke per pointercancel abbricht. Finger-Touch
 * wird nicht gefangen und scrollt weiterhin nativ.
 */
function capturePointer(e) {
  try {
    document.body.setPointerCapture(e.pointerId);
    _capturedPid = e.pointerId;
  } catch { /* manche Pointer lassen sich nicht fangen – unkritisch */ }
}

function releaseCapturedPointer() {
  if (_capturedPid === null) return;
  try { document.body.releasePointerCapture(_capturedPid); } catch { /* egal */ }
  _capturedPid = null;
}

// Unterdrückt den synthetischen Klick nach einem Maus-/Stylus-Strich,
// damit darunterliegende Links/Buttons nicht ausgelöst werden.
let suppressNextClick = false;
function onClickGuard(e) {
  if (penMode && suppressNextClick && !isPenUiTarget(e)) {
    e.preventDefault();
    e.stopPropagation();
  }
  suppressNextClick = false;
}

function onDown(e) {
  if (!penMode || drawing || dragState) return;
  if (!isDrawingPointer(e)) return;      // Finger → Seite scrollen lassen
  if (isPenUiTarget(e)) return;          // Toolbar bedienen, nicht zeichnen
  e.preventDefault();
  suppressNextClick = true;
  capturePointer(e);                     // Scroll-Geste für Pen/Maus unterdrücken

  if (activeTool === 'lasso') {
    // Klick innerhalb bestehender Selektion → Drag starten
    if (selectedIds.size > 0 && isInsideLasso(e.clientX, e.clientY)) {
      startDrag(e.clientX, e.clientY);
      return;
    }
    // Neue Lasso-Selektion (Viewport-Koordinaten)
    clearSelection();
    lassoPoints = [{ x: e.clientX, y: e.clientY }];
    lassoClosed = false;
    drawing = true;
    return;
  }

  drawing = true;
  const color = activeTool === 'marker' ? markerColor : penColor;
  const anchorEl = findAnchorEl(e.clientX, e.clientY);
  const clipEls = collectClipAncestors(anchorEl);
  liveStroke = { tool: activeTool, color, points: [], anchorEl, clipEls };
  appendPoint(e);
  redraw();
}

function onMove(e) {
  if (!penMode) return;

  if (dragState) {
    e.preventDefault();
    applyDrag(e.clientX, e.clientY);
    return;
  }
  if (!drawing) return;
  if (!isDrawingPointer(e)) return;
  e.preventDefault();

  if (activeTool === 'lasso') {
    lassoPoints.push({ x: e.clientX, y: e.clientY });
    redraw();
    return;
  }

  // Bei schnellen Bewegungen bündelt der Browser mehrere Positionen in einem
  // Event. Die zusammengefassten Zwischenpunkte einlesen, sonst gehen genau
  // die Richtungswechsel eines hektischen Kratzers verloren.
  const evs = (typeof e.getCoalescedEvents === 'function')
    ? e.getCoalescedEvents()
    : null;
  if (evs && evs.length) {
    for (const ce of evs) appendPoint(ce);
  } else {
    appendPoint(e);
  }

  // Scratch-to-Erase nur beim Stift prüfen
  if (activeTool === 'pen' && liveStroke && liveStroke.points.length >= 3) {
    updateScratch(liveStroke);
  }
  redraw();
}

function onUp(e) {
  releaseCapturedPointer();
  if (dragState) {
    dragState = null;
    return;
  }
  if (!drawing) return;
  drawing = false;

  if (activeTool === 'lasso') {
    lassoClosed = true;
    selectedIds = findStrokesInLasso(lassoPoints);
    if (selectedIds.size === 0) lassoPoints = [];
    updateLassoHint();
    redraw();
    return;
  }

  if (liveStroke && liveStroke.points.length >= 2) {
    strokes.push(liveStroke);
  }
  liveStroke = null;
  redraw();
}

function appendPoint(e) {
  const pressure = e.pressure > 0 ? e.pressure : 0.5;
  const w = activeTool === 'pen'
    ? PEN_BASE_W * (0.5 + pressure)
    : activeTool === 'eraser'
      ? ERASER_WIDTH
      : MARKER_WIDTH;
  const { ox, oy } = anchorOffset(liveStroke.anchorEl);
  liveStroke.points.push({ x: e.clientX - ox, y: e.clientY - oy, w });
}

// ─── Scratch-to-Erase ────────────────────────────────────────────────────────
/**
 * Erkennt absichtliches Zickzack-Kratzen. Wichtig: Die Analyse läuft NICHT
 * auf den rohen Pointer-Punkten, da deren Dichte von der Abtastrate abhängt
 * (ein Stift liefert sehr viele Punkte je Sekunde → ein Punkt-Fenster deckt
 * nur Sekundenbruchteile und damit kaum Umkehrungen ab). Stattdessen wird der
 * jüngste Pfadabschnitt nach Bogenlänge gleichmäßig neu abgetastet
 * (fester Pixel-Schritt). So sind Richtungsumkehrungen geräteunabhängig
 * zählbar. Maßgeblich ist die Faltung: Beim Kratzen ist die Weglänge ein
 * Vielfaches der Bounding-Box-Diagonale; beim Schreiben schreitet der Strich
 * voran (geringe Faltung).
 */
function updateScratch(stroke) {
  const pts = stroke.points;
  if (pts.length < 3) return;

  // Jüngsten Pfadabschnitt bis SCRATCH_SCAN_LEN (Bogenlänge) rückwärts sammeln.
  let acc = 0;
  let startIdx = pts.length - 1;
  for (let i = pts.length - 1; i > 0; i--) {
    acc += Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
    startIdx = i - 1;
    if (acc >= SCRATCH_SCAN_LEN) break;
  }
  const tail = pts.slice(startIdx);

  // Nach Bogenlänge gleichmäßig neu abtasten (Schritt SCRATCH_STEP).
  const res = resampleByLength(tail, SCRATCH_STEP);
  if (res.length < SCRATCH_MIN_REVERSALS + 2) return;

  let pathLen = 0;
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (let i = 0; i < res.length; i++) {
    const p = res[i];
    if (p.x < minX) minX = p.x;
    if (p.x > maxX) maxX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.y > maxY) maxY = p.y;
    if (i > 0) pathLen += Math.hypot(p.x - res[i - 1].x, p.y - res[i - 1].y);
  }

  const bw   = maxX - minX;
  const bh   = maxY - minY;
  const diag = Math.hypot(bw, bh) || 1;

  // Umkehrungen entlang der dominanten Achse zählen.
  const horizontal = bw >= bh;
  let reversals = 0;
  let lastDir   = 0;
  for (let i = 1; i < res.length; i++) {
    const d = horizontal ? res[i].x - res[i - 1].x : res[i].y - res[i - 1].y;
    const dir = d > 0 ? 1 : d < 0 ? -1 : 0;
    if (dir !== 0 && lastDir !== 0 && dir !== lastDir) reversals++;
    if (dir !== 0) lastDir = dir;
  }

  if (
    reversals >= SCRATCH_MIN_REVERSALS &&
    pathLen   >= SCRATCH_MIN_PATH &&
    pathLen   >= diag * SCRATCH_MIN_FOLD
  ) {
    triggerScratchErase(stroke);
  }
}

/** Tastet eine Punktliste gleichmäßig nach Bogenlänge mit Schritt step neu ab. */
function resampleByLength(pts, step) {
  if (pts.length < 2) return pts.slice();
  const out = [{ x: pts[0].x, y: pts[0].y }];
  let prev = pts[0];
  let dist = 0;
  for (let i = 1; i < pts.length; i++) {
    let segDx = pts[i].x - prev.x;
    let segDy = pts[i].y - prev.y;
    let segLen = Math.hypot(segDx, segDy);
    while (dist + segLen >= step) {
      const t = (step - dist) / segLen;
      const nx = prev.x + segDx * t;
      const ny = prev.y + segDy * t;
      out.push({ x: nx, y: ny });
      prev = { x: nx, y: ny };
      segDx = pts[i].x - prev.x;
      segDy = pts[i].y - prev.y;
      segLen = Math.hypot(segDx, segDy);
      dist = 0;
    }
    dist += segLen;
    prev = pts[i];
  }
  return out;
}

/**
 * Löscht alle Striche, die der Scratch-Strich kreuzt,
 * und verwirft den Scratch-Strich selbst.
 */
function triggerScratchErase(scratchStroke) {
  const scratchVp = strokeViewportPoints(scratchStroke);
  const bbox = strokeBBox(scratchVp);
  const toDelete = new Set();

  strokes.forEach((s, i) => {
    if (s.tool === 'eraser') return;
    if (s.anchorEl && !s.anchorEl.isConnected) return;
    const vp = strokeViewportPoints(s);
    if (!bboxOverlaps(bbox, strokeBBox(vp))) return;
    if (strokesCross(scratchVp, vp) || strokesNear(scratchVp, vp, ERASE_HIT_RADIUS)) {
      toDelete.add(i);
    }
  });

  if (toDelete.size > 0) {
    strokes = strokes.filter((_, i) => !toDelete.has(i));
  }

  // Scratch-Strich nicht in strokes aufnehmen, Aktion als abgeschlossen markieren
  drawing    = false;
  liveStroke = null;
  releaseCapturedPointer();
  redraw();
  // Kurzes visuelles Feedback: Flackern auf dem Canvas
  flashErase();
}

function flashErase() {
  ctx.save();
  ctx.fillStyle = 'rgba(239,68,68,0.08)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.restore();
  setTimeout(() => redraw(), 120);
}

/** Bounding-Box eines Strichs (Dokument-Koordinaten) */
function strokeBBox(pts) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const p of pts) {
    if (p.x < minX) minX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.x > maxX) maxX = p.x;
    if (p.y > maxY) maxY = p.y;
  }
  return { minX, minY, maxX, maxY };
}

function bboxOverlaps(a, b) {
  return a.maxX >= b.minX && a.minX <= b.maxX &&
         a.maxY >= b.minY && a.minY <= b.maxY;
}

/** Prüft ob zwei Strich-Punktlisten sich mindestens einmal kreuzen (Segment-Schnitt). */
function strokesCross(ptsA, ptsB) {
  for (let i = 0; i < ptsA.length - 1; i++) {
    for (let j = 0; j < ptsB.length - 1; j++) {
      if (segmentsIntersect(ptsA[i], ptsA[i+1], ptsB[j], ptsB[j+1])) return true;
    }
  }
  return false;
}

/** Segment-Schnitt-Test (2D, keine Endpunkt-Randbehandlung nötig) */
function segmentsIntersect(p1, p2, p3, p4) {
  const d1x = p2.x - p1.x, d1y = p2.y - p1.y;
  const d2x = p4.x - p3.x, d2y = p4.y - p3.y;
  const cross = d1x * d2y - d1y * d2x;
  if (Math.abs(cross) < 1e-10) return false;   // parallel
  const dx = p3.x - p1.x, dy = p3.y - p1.y;
  const t = (dx * d2y - dy * d2x) / cross;
  const u = (dx * d1y - dy * d1x) / cross;
  return t >= 0 && t <= 1 && u >= 0 && u <= 1;
}

/** Prüft, ob sich zwei Strich-Punktlisten auf ≤ r Pixel annähern. */
function strokesNear(ptsA, ptsB, r) {
  const r2 = r * r;
  for (let i = 0; i < ptsA.length - 1; i++) {
    for (let j = 0; j < ptsB.length; j++) {
      if (pointSegDist2(ptsB[j], ptsA[i], ptsA[i + 1]) <= r2) return true;
    }
  }
  return false;
}

/** Quadrierte Distanz von Punkt p zum Segment a–b. */
function pointSegDist2(p, a, b) {
  const vx = b.x - a.x, vy = b.y - a.y;
  const wx = p.x - a.x, wy = p.y - a.y;
  const len2 = vx * vx + vy * vy;
  let t = len2 > 0 ? (wx * vx + wy * vy) / len2 : 0;
  t = t < 0 ? 0 : t > 1 ? 1 : t;
  const dx = a.x + t * vx - p.x;
  const dy = a.y + t * vy - p.y;
  return dx * dx + dy * dy;
}

// ─── Lasso-Hilfsfunktionen ───────────────────────────────────────────────────
function pointInPolygon(x, y, poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const xi = poly[i].x, yi = poly[i].y;
    const xj = poly[j].x, yj = poly[j].y;
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }
  return inside;
}

function findStrokesInLasso(lasso) {
  const ids = new Set();
  strokes.forEach((s, i) => {
    if (s.anchorEl && !s.anchorEl.isConnected) return;
    const vp = strokeViewportPoints(s);
    if (vp.some(pt => pointInPolygon(pt.x, pt.y, lasso))) ids.add(i);
  });
  return ids;
}

function isInsideLasso(clientX, clientY) {
  return lassoPoints.length >= 3 && pointInPolygon(clientX, clientY, lassoPoints);
}

function clearSelection() {
  selectedIds.clear();
  lassoPoints = [];
  lassoClosed = false;
  updateLassoHint();
}

function deleteSelected() {
  if (!selectedIds.size) return;
  strokes = strokes.filter((_, i) => !selectedIds.has(i));
  clearSelection();
  redraw();
}

// ─── Drag ─────────────────────────────────────────────────────────────────────
function startDrag(clientX, clientY) {
  const origStrokes = new Map();
  for (const i of selectedIds) {
    origStrokes.set(i, strokes[i].points.map(p => ({ ...p })));
  }
  dragState = {
    startX: clientX,
    startY: clientY,
    origStrokes,
    origLasso: lassoPoints.map(p => ({ ...p })),
  };
}

function applyDrag(clientX, clientY) {
  const dx = clientX - dragState.startX;
  const dy = clientY - dragState.startY;
  for (const [i, origPts] of dragState.origStrokes) {
    strokes[i].points = origPts.map(p => ({ x: p.x + dx, y: p.y + dy, w: p.w }));
  }
  lassoPoints = dragState.origLasso.map(p => ({ x: p.x + dx, y: p.y + dy }));
  redraw();
}

// ─── Hinweis-Bar ──────────────────────────────────────────────────────────────
function updateLassoHint() {
  const hint = document.getElementById('pen-lasso-hint');
  const delBtn = document.getElementById('pen-btn-delete-sel');
  if (!hint) return;
  if (selectedIds.size > 0) {
    const n = selectedIds.size;
    hint.textContent = `${n} Strich${n > 1 ? 'e' : ''} ausgewählt · Ziehen: verschieben · Entf: löschen`;
    hint.classList.add('visible');
    delBtn?.classList.toggle('visible', true);
  } else {
    hint.classList.remove('visible');
    delBtn?.classList.remove('visible');
  }
}

// ─── Tastaturkürzel ───────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (!penMode) return;
  if ((e.key === 'Delete' || e.key === 'Backspace') && selectedIds.size) {
    e.preventDefault();
    deleteSelected();
    return;
  }
  if (e.key === 'Escape') { clearSelection(); redraw(); return; }
  if ((e.ctrlKey || e.metaKey) && e.key === 'z') { e.preventDefault(); undo(); return; }
  if (!e.ctrlKey && !e.metaKey && !e.altKey) {
    if (e.key === 'p') setTool('pen');
    if (e.key === 'm') setTool('marker');
    if (e.key === 'e') setTool('eraser');
    if (e.key === 'l') setTool('lasso');
  }
});

// ─── Undo ─────────────────────────────────────────────────────────────────────
function undo() {
  if (strokes.length === 0) return;
  strokes.pop();
  clearSelection();
  redraw();
}

// ─── Stiftmodus ───────────────────────────────────────────────────────────────
function setPenMode(on) {
  penMode = on;
  // Canvas bleibt immer pointer-events:none, damit Finger-Touch zum Inhalt
  // durchreicht und scrollt; gezeichnet wird über window-Listener (mouse/pen).
  document.body.classList.toggle('pen-active', on);

  const toggle = document.getElementById('pen-btn-toggle');
  if (toggle) {
    toggle.classList.toggle('active', on);
    toggle.title = on ? 'Stiftmodus beenden' : 'Stiftmodus aktivieren';
  }
  document.querySelectorAll('.pen-tool').forEach(el => el.classList.toggle('visible', on));

  if (!on) {
    drawing = false;
    liveStroke = null;
    dragState  = null;
    releaseCapturedPointer();
    setPenInputActive(false);   // Scrollsperre aufheben
    clearSelection();
    redraw();
  }
  updateBodyClass();
}

function updateBodyClass() {
  applyToolCursor();
}

// ─── Werkzeug wählen ─────────────────────────────────────────────────────────
function setTool(name) {
  activeTool = name;

  // Button-Zustände
  const toolIds = ['pen-btn-pen', 'pen-btn-marker', 'pen-btn-lasso', 'pen-btn-erase'];
  toolIds.forEach(id => document.getElementById(id)?.classList.remove('pen-tool-active'));
  const map = { pen: 'pen-btn-pen', marker: 'pen-btn-marker', lasso: 'pen-btn-lasso', eraser: 'pen-btn-erase' };
  document.getElementById(map[name])?.classList.add('pen-tool-active');

  // Farb-Paletten: Stift-Farben nur bei pen, Marker-Farben nur bei marker
  document.querySelectorAll('.pen-color-dot[data-mode="pen"]').forEach(el => {
    /** @type {HTMLElement} */ (el).style.display = name === 'pen' ? '' : 'none';
  });
  document.querySelectorAll('.pen-color-dot[data-mode="marker"]').forEach(el => {
    /** @type {HTMLElement} */ (el).style.display = name === 'marker' ? '' : 'none';
  });

  // Lasso-Selektion beim Wechsel aufheben
  if (name !== 'lasso') {
    clearSelection();
  }

  updateBodyClass();
  redraw();
}

// ─── Toolbar-Verdrahtung ──────────────────────────────────────────────────────
document.getElementById('pen-btn-toggle')?.addEventListener('click', () => setPenMode(!penMode));
document.getElementById('pen-btn-pen')?.addEventListener('click',    () => setTool('pen'));
document.getElementById('pen-btn-marker')?.addEventListener('click', () => setTool('marker'));
document.getElementById('pen-btn-lasso')?.addEventListener('click',  () => setTool('lasso'));
document.getElementById('pen-btn-erase')?.addEventListener('click',  () => setTool('eraser'));

document.getElementById('pen-btn-undo')?.addEventListener('click', undo);

document.getElementById('pen-btn-delete-sel')?.addEventListener('click', deleteSelected);

document.getElementById('pen-btn-clear')?.addEventListener('click', () => {
  strokes = [];
  liveStroke = null;
  clearSelection();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
});

// Farb-Dots
document.querySelectorAll('.pen-color-dot').forEach(btn => {
  btn.addEventListener('click', () => {
    const b    = /** @type {HTMLElement} */ (btn);
    const mode  = b.dataset.mode;
    const color = b.dataset.color;
    if (!mode || !color) return;

    if (mode === 'pen')    { penColor    = color; if (activeTool !== 'pen')    setTool('pen');    else applyToolCursor(); }
    if (mode === 'marker') { markerColor = color; if (activeTool !== 'marker') setTool('marker'); else applyToolCursor(); }

    document.querySelectorAll(`.pen-color-dot[data-mode="${mode}"]`)
      .forEach(b2 => b2.classList.remove('selected'));
    btn.classList.add('selected');
  });
});

// Initialzustand: Marker-Farben verbergen (Stift ist Standard)
setTool('pen');
