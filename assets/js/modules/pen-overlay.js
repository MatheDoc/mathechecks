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
const MARKER_ALPHA = 0.38;
const PEN_BASE_W   = 3;
const ERASER_WIDTH = 28;

// ─── Cursor-SVGs (dynamisch, farbabhängig) ────────────────────────────────────
function _cur(svg, hx, hy) {
  return `url("data:image/svg+xml,${encodeURIComponent(svg)}") ${hx} ${hy}, auto`;
}

function _enc(hex) {
  // "#3b82f6" → "%233b82f6" für SVG-Attribute im data-URL
  return encodeURIComponent(hex);
}

function _cursorPen(color) {
  // Stift: Spitze unten-links, Körper in gewählter Farbe
  const c  = _enc(color);
  const c2 = _enc(color + 'cc'); // leicht transparent für Schaftfläche
  return _cur(
    `<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'>`
    + `<path d='M4 16L13 7L17 11L8 20Z' fill='${c2}' stroke='%23fff' stroke-width='0.8' stroke-linejoin='round'/>`
    + `<path d='M2 20L4 16L8 20Z' fill='%23888' stroke='%23fff' stroke-width='0.6'/>`
    + `<path d='M13 7L16 4L20 4L20 8L17 11Z' fill='%23e0e0e0' stroke='%23fff' stroke-width='0.6'/>`
    + `</svg>`,
    2, 20
  );
}

function _cursorMarker(color) {
  const c = _enc(color);
  return _cur(
    `<svg xmlns='http://www.w3.org/2000/svg' width='12' height='24'>`
    + `<rect x='0' y='0' width='12' height='24' rx='2' fill='${c}' fill-opacity='0.55' stroke='%23333' stroke-width='1'/>`
    + `</svg>`,
    6, 12
  );
}

function _cursorEraser() {
  return _cur(
    `<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><rect x='1' y='5' width='18' height='11' rx='2' fill='%23f8d7c4' stroke='%23cc4455' stroke-width='1.5'/><line x1='1' y1='11' x2='19' y2='11' stroke='%23cc4455' stroke-width='1'/></svg>`,
    10, 10
  );
}

function _cursorLasso() {
  return _cur(
    `<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'><ellipse cx='10' cy='8' rx='7' ry='5' fill='none' stroke='%23fff' stroke-width='3'/><ellipse cx='10' cy='8' rx='7' ry='5' fill='none' stroke='%23222' stroke-width='1.5' stroke-dasharray='3 2'/><line x1='10' y1='13' x2='10' y2='20' stroke='%23fff' stroke-width='3' stroke-linecap='round'/><line x1='10' y1='13' x2='10' y2='20' stroke='%23222' stroke-width='1.5' stroke-linecap='round'/></svg>`,
    10, 8
  );
}

function applyToolCursor() {
  if (!penMode) { canvas.style.cursor = 'default'; return; }
  const cursors = {
    pen:    _cursorPen(penColor),
    marker: _cursorMarker(markerColor),
    eraser: _cursorEraser(),
    lasso:  _cursorLasso(),
  };
  canvas.style.cursor = cursors[activeTool] ?? 'crosshair';
}

// Scratch-to-Erase-Schwellen
const SCRATCH_MIN_REVERSALS  = 4;    // Mindestanzahl Richtungsumkehrungen
const SCRATCH_MIN_SPEED_SQ   = 8*8;  // Mindestgeschwindigkeit² je Segment (px)
const SCRATCH_MIN_TOTAL_DIST = 60;   // Mindest-Gesamtweg des Strichs (px)

// ─── State ────────────────────────────────────────────────────────────────────
let penMode     = false;
let activeTool  = 'pen';   // 'pen' | 'marker' | 'lasso' | 'eraser'
let penColor    = '#3b82f6';
let markerColor = '#fde047';
let drawing     = false;

/**
 * @typedef {{ x: number, y: number, w: number }} Point
 * @typedef {{ tool: string, color: string, points: Point[] }} Stroke
 */

/** @type {Stroke[]} */
let strokes = [];

/** @type {Stroke|null} */
let liveStroke = null;

// Scratch-to-Erase
/** Richtungs-Vorzeichen des letzten Segments (+1 / -1 / 0) */
let scratchLastDirX = 0;
let scratchReversals = 0;
let scratchTotalDist = 0;

// Lasso
/** @type {{ x: number, y: number }[]} */
let lassoPoints  = [];
let lassoClosed  = false;
/** @type {Set<number>} */
let selectedIds  = new Set();
/** @type {{ docX: number, docY: number, origStrokes: Map<number, Point[]>, origLasso: { x: number, y: number }[] }|null} */
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

scrollEl.addEventListener('scroll', redraw, { passive: true });

// ─── Koordinaten-Helper ───────────────────────────────────────────────────────
/** PointerEvent → Dokument-Koordinaten (y einschließlich scrollTop) */
function toDoc(e) {
  return { x: e.clientX, y: e.clientY + scrollEl.scrollTop };
}

// ─── Rendering ────────────────────────────────────────────────────────────────
function redraw() {
  const sy = scrollEl.scrollTop;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < strokes.length; i++) {
    renderStroke(ctx, strokes[i], sy, selectedIds.has(i));
  }
  if (liveStroke) renderStroke(ctx, liveStroke, sy, false);
  if (lassoPoints.length > 1) renderLasso(sy);
}

/** Rendert einen Strich; y-Koordinaten werden um scrollTop verschoben. */
function renderStroke(c, s, sy, selected) {
  if (!s.points || s.points.length < 2) return;
  if (s.tool === 'marker') { renderMarker(c, s, sy, selected); return; }
  if (s.tool === 'eraser') { renderEraser(c, s, sy);           return; }

  // ── Stift ──────────────────────────────────────────────────────────────────
  c.save();
  c.lineCap     = 'round';
  c.lineJoin    = 'round';
  c.strokeStyle = selected ? 'rgba(124,106,255,1)' : s.color;
  c.globalAlpha = 1;
  c.beginPath();
  c.moveTo(s.points[0].x, s.points[0].y - sy);
  for (let i = 1; i < s.points.length; i++) {
    c.lineWidth = s.points[i].w;
    if (i < s.points.length - 1) {
      const mx = (s.points[i].x   + s.points[i + 1].x) / 2;
      const my = (s.points[i].y   + s.points[i + 1].y) / 2;
      c.quadraticCurveTo(s.points[i].x, s.points[i].y - sy, mx, my - sy);
    } else {
      c.lineTo(s.points[i].x, s.points[i].y - sy);
    }
  }
  c.stroke();
  c.restore();
}

/**
 * Textmarker: Off-screen-Canvas verhindert Alpha-Akkumulation innerhalb
 * eines Strichs → gleichmäßige, flache Deckung wie ein echter Textmarker.
 */
function renderMarker(c, s, sy, selected) {
  if (!markerBuf || !markerBufCtx) return;
  const mc = markerBufCtx;
  mc.clearRect(0, 0, markerBuf.width, markerBuf.height);
  mc.save();
  mc.lineCap     = 'square';
  mc.lineJoin    = 'bevel';
  mc.lineWidth   = MARKER_WIDTH;
  mc.strokeStyle = selected ? 'rgb(124,106,255)' : s.color;
  mc.globalAlpha = 1;
  mc.beginPath();
  mc.moveTo(s.points[0].x, s.points[0].y - sy);
  for (const pt of s.points.slice(1)) mc.lineTo(pt.x, pt.y - sy);
  mc.stroke();
  mc.restore();

  c.save();
  c.globalAlpha = selected ? 0.58 : MARKER_ALPHA;
  c.drawImage(markerBuf, 0, 0);
  c.restore();
}

function renderEraser(c, s, sy) {
  c.save();
  c.globalCompositeOperation = 'destination-out';
  c.lineCap     = 'round';
  c.lineJoin    = 'round';
  c.strokeStyle = 'rgba(0,0,0,1)';
  c.beginPath();
  c.moveTo(s.points[0].x, s.points[0].y - sy);
  for (const pt of s.points.slice(1)) {
    c.lineWidth = pt.w;
    c.lineTo(pt.x, pt.y - sy);
  }
  c.stroke();
  c.restore();
}

function renderLasso(sy) {
  ctx.save();
  ctx.strokeStyle = 'rgba(124,106,255,0.88)';
  ctx.fillStyle   = 'rgba(124,106,255,0.07)';
  ctx.lineWidth   = 1.5;
  ctx.setLineDash([5, 4]);
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(lassoPoints[0].x, lassoPoints[0].y - sy);
  for (let i = 1; i < lassoPoints.length; i++) {
    ctx.lineTo(lassoPoints[i].x, lassoPoints[i].y - sy);
  }
  if (lassoClosed) ctx.closePath();
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

// ─── Pointer-Events ───────────────────────────────────────────────────────────
canvas.addEventListener('pointerdown',   onDown);
canvas.addEventListener('pointermove',   onMove);
canvas.addEventListener('pointerup',     onUp);
canvas.addEventListener('pointercancel', onUp);

function onDown(e) {
  if (!penMode || drawing) return;
  canvas.setPointerCapture(e.pointerId);
  const doc = toDoc(e);

  if (activeTool === 'lasso') {
    // Klick innerhalb bestehender Selektion → Drag starten
    if (selectedIds.size > 0 && isInsideLasso(doc)) {
      startDrag(doc);
      return;
    }
    // Neue Lasso-Selektion
    clearSelection();
    lassoPoints = [doc];
    lassoClosed = false;
    drawing = true;
    return;
  }

  drawing = true;
  const color = activeTool === 'marker' ? markerColor : penColor;
  liveStroke = { tool: activeTool, color, points: [] };
  // Scratch-Zähler zurücksetzen
  scratchLastDirX  = 0;
  scratchReversals = 0;
  scratchTotalDist = 0;
  appendPoint(e, doc);
  redraw();
}

function onMove(e) {
  if (!penMode) return;
  const doc = toDoc(e);

  if (dragState) {
    applyDrag(doc);
    return;
  }
  if (!drawing) return;

  if (activeTool === 'lasso') {
    lassoPoints.push(doc);
    redraw();
    return;
  }

  appendPoint(e, doc);
  // Scratch-to-Erase nur beim Stift prüfen
  if (activeTool === 'pen' && liveStroke && liveStroke.points.length >= 2) {
    updateScratch(liveStroke);
  }
  redraw();
}

function onUp(e) {
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

function appendPoint(e, doc) {
  const pressure = e.pressure > 0 ? e.pressure : 0.5;
  const w = activeTool === 'pen'
    ? PEN_BASE_W * (0.5 + pressure)
    : activeTool === 'eraser'
      ? ERASER_WIDTH
      : MARKER_WIDTH;
  liveStroke.points.push({ x: doc.x, y: doc.y, w });
}

// ─── Scratch-to-Erase ────────────────────────────────────────────────────────
/**
 * Analysiert den laufenden Strich auf Zickzack-Muster.
 * Kriterien: mind. SCRATCH_MIN_REVERSALS X-Richtungsumkehrungen,
 * jedes Segment schnell genug, Gesamtweg ≥ Mindestdistanz.
 */
function updateScratch(stroke) {
  const pts = stroke.points;
  const n   = pts.length;
  if (n < 2) return;

  const p1 = pts[n - 2];
  const p2 = pts[n - 1];
  const dx  = p2.x - p1.x;
  const dy  = p2.y - p1.y;
  const d2  = dx * dx + dy * dy;

  scratchTotalDist += Math.sqrt(d2);
  if (d2 < SCRATCH_MIN_SPEED_SQ) return;   // zu langsam / zu kurz

  const dir = dx > 0 ? 1 : dx < 0 ? -1 : 0;
  if (dir !== 0 && scratchLastDirX !== 0 && dir !== scratchLastDirX) {
    scratchReversals++;
  }
  if (dir !== 0) scratchLastDirX = dir;

  if (
    scratchReversals >= SCRATCH_MIN_REVERSALS &&
    scratchTotalDist >= SCRATCH_MIN_TOTAL_DIST
  ) {
    triggerScratchErase(stroke);
  }
}

/**
 * Löscht alle Striche, die der Scratch-Strich kreuzt,
 * und verwirft den Scratch-Strich selbst.
 */
function triggerScratchErase(scratchStroke) {
  const bbox = strokeBBox(scratchStroke.points);
  const toDelete = new Set();

  strokes.forEach((s, i) => {
    if (s.tool === 'eraser') return;
    if (!bboxOverlaps(bbox, strokeBBox(s.points))) return;
    if (strokesCross(scratchStroke.points, s.points)) toDelete.add(i);
  });

  if (toDelete.size > 0) {
    strokes = strokes.filter((_, i) => !toDelete.has(i));
  }

  // Scratch-Strich nicht in strokes aufnehmen, Aktion als abgeschlossen markieren
  drawing    = false;
  liveStroke = null;
  scratchReversals = 0;
  scratchTotalDist = 0;
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
    if (s.points.some(pt => pointInPolygon(pt.x, pt.y, lasso))) ids.add(i);
  });
  return ids;
}

function isInsideLasso(doc) {
  return lassoPoints.length >= 3 && pointInPolygon(doc.x, doc.y, lassoPoints);
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
function startDrag(doc) {
  const origStrokes = new Map();
  for (const i of selectedIds) {
    origStrokes.set(i, strokes[i].points.map(p => ({ ...p })));
  }
  dragState = {
    docX: doc.x,
    docY: doc.y,
    origStrokes,
    origLasso: lassoPoints.map(p => ({ ...p })),
  };
}

function applyDrag(doc) {
  const dx = doc.x - dragState.docX;
  const dy = doc.y - dragState.docY;
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
  canvas.style.pointerEvents = on ? 'auto' : 'none';

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
    clearSelection();
    redraw();
  }
  updateBodyClass();
}

function updateBodyClass() {
  document.body.classList.toggle('pen-drawing',  penMode && activeTool !== 'eraser' && activeTool !== 'lasso');
  document.body.classList.toggle('pen-erasing',  penMode && activeTool === 'eraser');
  document.body.classList.toggle('pen-lassoing', penMode && activeTool === 'lasso');
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
