// Konzeptseite: animierte Grafik "Check-Ketten & Erfolgsquoten".
// Phase 1: Playhead durchläuft die versetzten Ketten (quantitative Achse),
// Erfolgsquoten füllen sich beim Passieren ihres Knotens.
// Phase 2: Kette ist durch, die Quoten steigen eigenständig weiter (qualitative Achse).
(function () {
    'use strict';

    const svg = document.getElementById('konzeptSvg');
    const playBtn = document.getElementById('konzeptPlayBtn');
    const statusLabel = document.getElementById('konzeptStatus');
    if (!svg || !playBtn || !statusLabel) return;

    const svgNS = 'http://www.w3.org/2000/svg';
    function makeEl(tag, attrs) {
        const el = document.createElementNS(svgNS, tag);
        Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
        return el;
    }

    // ── Geometrie: eine Zeile pro Check, diagonal versetzt ──
    const ACTS = [
        { type: 'training', short: 'T' },
        { type: 'recall', short: 'R' },
        { type: 'feynman', short: 'F' },
        { type: 'kompetenz', short: 'K' },
    ];
    const LABEL_W = 96;
    const COL_W = 150;
    const ROW_DX = 65;
    const ROW_DY = 128;
    const R = 20;
    const TOP_PAD = 78;

    const rows = [1, 2, 3].map((checkNum, rowIndex) => {
        const offsetX = LABEL_W + rowIndex * ROW_DX;
        const y = TOP_PAD + rowIndex * ROW_DY;
        const nodes = ACTS.map((a, colIndex) => ({
            type: a.type, short: a.short, check: checkNum,
            x: offsetX + colIndex * COL_W, y,
        }));
        return { checkNum, y, nodes };
    });

    const maxX = Math.max(...rows.flatMap(r => r.nodes.map(n => n.x))) + R + 30;
    const chainMaxY = Math.max(...rows.map(r => r.y)) + R;

    const RING_R = 34;
    const RING_STROKE = 7;
    const ringY = chainMaxY + 170;
    const ringCirc = 2 * Math.PI * RING_R;
    const maxY = ringY + RING_R + 48;

    svg.setAttribute('viewBox', `0 0 ${maxX} ${maxY}`);

    function findNode(check, type) {
        return rows.find(r => r.checkNum === check).nodes.find(n => n.type === type);
    }

    const examples = [
        { check: 2, type: 'training', label: 'Training · Check 2', initial: 45 },
        { check: 2, type: 'recall', label: 'Recall · Check 2', initial: 68 },
        { check: 3, type: 'feynman', label: 'Feynman · Check 3', initial: 30 },
    ].map(ex => ({ ...ex, node: findNode(ex.check, ex.type), value: 0, filled: false }));

    // ── Achsenbeschriftungen ──
    const axisTop = makeEl('text', { x: LABEL_W - R, y: 24, class: 'kg-axis' });
    axisTop.textContent = 'zeitlicher Ablauf →';
    svg.appendChild(axisTop);

    const axisLeft = makeEl('text', {
        x: 18, y: ringY, class: 'kg-axis', 'text-anchor': 'middle',
        transform: `rotate(-90 18 ${ringY})`,
    });
    axisLeft.textContent = 'Erfolgsquote';
    svg.appendChild(axisLeft);

    // ── Verbindungslinien Knoten → Ring (unter den Zeilen) ──
    examples.forEach(ex => {
        svg.appendChild(makeEl('line', {
            x1: ex.node.x, y1: ex.node.y + R,
            x2: ex.node.x, y2: ringY - RING_R - 6,
            class: 'kg-connector',
        }));
    });

    const playhead = makeEl('line', { x1: 0, y1: 34, x2: 0, y2: maxY - 12, class: 'kg-playhead', opacity: 0 });
    svg.appendChild(playhead);

    // ── Ketten-Zeilen ──
    const rowData = rows.map(row => {
        const label = makeEl('text', { x: 4, y: row.y + 4, class: 'kg-check-tag' });
        label.textContent = 'Check ' + row.checkNum;
        svg.appendChild(label);

        const d = row.nodes.map((n, i) => (i === 0 ? 'M' : 'L') + n.x + ' ' + n.y).join(' ');
        const path = makeEl('path', { d, class: 'kg-line' });
        svg.appendChild(path);
        const len = path.getTotalLength();
        path.style.strokeDasharray = len;
        path.style.strokeDashoffset = len;

        const circleEls = row.nodes.map(n => {
            const circle = makeEl('circle', { cx: n.x, cy: n.y, r: R, class: 'kg-node type-' + n.type });
            svg.appendChild(circle);
            const txt = makeEl('text', { x: n.x, y: n.y + 4.5, 'text-anchor': 'middle', class: 'kg-node-label' });
            txt.textContent = n.short;
            svg.appendChild(txt);
            return { circle, label: txt, x: n.x };
        });

        return { path, len, startX: row.nodes[0].x, endX: row.nodes[row.nodes.length - 1].x, circleEls };
    });

    // ── Erfolgsquoten-Ringe ──
    examples.forEach(ex => {
        const cx = ex.node.x, cy = ringY;

        const bg = makeEl('circle', { cx, cy, r: RING_R, class: 'kg-ring-bg', 'stroke-width': RING_STROKE });
        svg.appendChild(bg);

        const fg = makeEl('circle', {
            cx, cy, r: RING_R, class: 'kg-ring-fg type-' + ex.type,
            'stroke-width': RING_STROKE,
            transform: `rotate(-90 ${cx} ${cy})`,
            'stroke-dasharray': ringCirc,
            'stroke-dashoffset': ringCirc,
        });
        svg.appendChild(fg);

        const pct = makeEl('text', { x: cx, y: cy + 5, 'text-anchor': 'middle', class: 'kg-ring-pct' });
        pct.textContent = '–';
        svg.appendChild(pct);

        const label = makeEl('text', { x: cx, y: cy + RING_R + 20, 'text-anchor': 'middle', class: 'kg-check-tag' });
        label.textContent = ex.label;
        svg.appendChild(label);

        const hint = makeEl('text', { x: cx, y: cy + RING_R + 38, 'text-anchor': 'middle', class: 'kg-ring-hint' });
        hint.textContent = 'Nochmal üben ↻';
        svg.appendChild(hint);

        ex.els = { fg, pct, hint };

        const clickImprove = () => improve(ex, false);
        [bg, fg, hint].forEach(el => el.addEventListener('click', clickImprove));
    });

    function updateRing(ex) {
        ex.els.fg.setAttribute('stroke-dashoffset', ringCirc - (ex.value / 100) * ringCirc);
        ex.els.pct.textContent = ex.filled ? ex.value + '%' : '–';
        if (ex.value >= 100) {
            ex.els.hint.textContent = 'Gemeistert';
            ex.els.hint.classList.add('is-done');
        } else {
            ex.els.hint.textContent = 'Nochmal üben ↻';
            ex.els.hint.classList.remove('is-done');
        }
    }

    function improve(ex, auto) {
        if (!ex.filled || ex.value >= 100) return;
        const gain = 8 + Math.floor(Math.random() * 10);
        // automatische Phase-2-Schritte lassen Luft nach oben, "Gemeistert" nur per Klick
        ex.value = Math.min(auto ? 92 : 100, ex.value + gain);
        updateRing(ex);
    }

    const DURATION_MS = 3400;
    let phase2Timers = [];
    let running = false;

    function reset() {
        phase2Timers.forEach(clearTimeout);
        phase2Timers = [];
        playhead.setAttribute('opacity', 0);
        rowData.forEach(rd => {
            rd.path.style.strokeDashoffset = rd.len;
            rd.circleEls.forEach(c => {
                c.circle.classList.remove('active');
                c.label.classList.remove('active');
            });
        });
        examples.forEach(ex => {
            ex.value = 0;
            ex.filled = false;
            updateRing(ex);
        });
    }

    function startPhase2() {
        statusLabel.textContent = 'Kette abgeschlossen – die Quoten steigen weiter …';
        const stepGap = 450;
        examples.forEach((ex, i) => {
            phase2Timers.push(setTimeout(() => improve(ex, true), 600 + i * stepGap));
            phase2Timers.push(setTimeout(() => improve(ex, true), 2100 + i * stepGap));
        });
        phase2Timers.push(setTimeout(() => {
            statusLabel.textContent = 'Ringe anklicken, um weiter zu üben';
            playBtn.disabled = false;
            playBtn.textContent = '↻ Noch einmal abspielen';
            running = false;
        }, 2100 + examples.length * stepGap + 500));
    }

    function playChain() {
        if (running) return;
        running = true;
        reset();
        playBtn.disabled = true;
        statusLabel.textContent = 'Die Kette läuft …';
        playhead.setAttribute('opacity', 1);

        const start = performance.now();

        function frame(now) {
            const t = Math.min(1, (now - start) / DURATION_MS);
            const playheadX = t * maxX;
            playhead.setAttribute('x1', playheadX);
            playhead.setAttribute('x2', playheadX);

            rowData.forEach(rd => {
                const frac = Math.min(1, Math.max(0, (playheadX - rd.startX) / (rd.endX - rd.startX)));
                rd.path.style.strokeDashoffset = (1 - frac) * rd.len;
                rd.circleEls.forEach(c => {
                    if (playheadX >= c.x) {
                        c.circle.classList.add('active');
                        c.label.classList.add('active');
                    }
                });
            });

            examples.forEach(ex => {
                if (!ex.filled && playheadX >= ex.node.x) {
                    ex.filled = true;
                    ex.value = ex.initial;
                    updateRing(ex);
                }
            });

            if (t < 1) {
                requestAnimationFrame(frame);
            } else {
                playhead.setAttribute('opacity', 0);
                startPhase2();
            }
        }
        requestAnimationFrame(frame);
    }

    playBtn.addEventListener('click', playChain);

    // Einmalig automatisch abspielen, sobald die Grafik sichtbar wird
    let autoPlayed = false;
    if ('IntersectionObserver' in window) {
        const io = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !autoPlayed) {
                    autoPlayed = true;
                    io.disconnect();
                    playChain();
                }
            });
        }, { threshold: 0.3 });
        io.observe(svg);
    }
})();
