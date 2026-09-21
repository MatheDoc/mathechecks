/**
 * Zeitstrahl zur Herleitung der Zinseszinsformel K_n = K_0 · q^n:
 * Kapitalstände je Jahr, Zinsen mit Rechenweg, Zinsfaktor-Bögen je Jahr
 * und ein zusammenfassender Bogen über alle n Jahre. Liefert einen SVG-String.
 */

const MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";

const euro = new Intl.NumberFormat("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export function formatQ(p) {
    const q = 1 + p / 100;
    return q.toFixed(p % 1 ? 3 : 2).replace(".", ",");
}

export function formatP(p) {
    return String(p).replace(".", ",");
}

function esc(text) {
    return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;");
}

// Bogen, der nach unten durchhängt; endet kurz vor x2, damit die Pfeilspitze auf dem Tick sitzt
function arcDown(x1, x2, y, lift) {
    const m = (x1 + x2) / 2;
    return `M ${x1} ${y} Q ${m} ${y + lift} ${x2 - 6} ${y}`;
}

function kapitalTerm(qs, i) {
    if (i === 0) return `K<tspan dy="3" font-size="7">0</tspan>`;
    let s = `K<tspan dy="3" font-size="7">0</tspan><tspan dy="-3"> · ${qs}</tspan>`;
    if (i > 1) s += `<tspan dy="-4" font-size="7">${i}</tspan>`;
    return s;
}

export function buildZinseszinsZeitstrahlSvg({ k0, p, n, zeigeZinsen = true, idPrefix = "zzh" }) {
    const q = 1 + p / 100;
    const qs = formatQ(p);
    const ps = formatP(p);

    const x0 = 100;
    const xn = 720;
    const step = (xn - x0) / n;

    const yAxis = 36;
    const yKapital = 84;
    const yKapTerm = 100;
    const yZinsArc = 128;
    const yZinsBetrag = 160;
    const yZinsRechnung = 175;
    const yFacArc = zeigeZinsen ? 204 : 128;
    const yFacLabel = yFacArc + 36;
    const yBigArc = zeigeZinsen ? 266 : 190;
    const bigLift = 70;
    const height = yBigArc + bigLift + 12;

    const ah = `${idPrefix}-ah`;
    const ahP = `${idPrefix}-ahP`;

    let s = `<svg viewBox="0 0 760 ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Zeitstrahl zur Herleitung der Zinseszinsformel">`;
    s += "<defs>";
    s += `<marker id="${ah}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--text-dim)"/></marker>`;
    s += `<marker id="${ahP}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--pink)"/></marker>`;
    s += "</defs>";

    // Achse
    s += `<text x="6" y="${yAxis + 5}" font-size="13" fill="var(--text-dim)">Jahr</text>`;
    s += `<line x1="86" y1="${yAxis}" x2="746" y2="${yAxis}" stroke="var(--text)" stroke-width="1.2" opacity=".6" marker-end="url(#${ah})"/>`;
    s += `<text x="6" y="${yKapital}" font-size="13" fill="var(--text-dim)">Kapital</text>`;

    for (let i = 0; i <= n; i += 1) {
        const x = x0 + i * step;
        const ki = k0 * Math.pow(q, i);
        s += `<line x1="${x}" y1="${yAxis - 7}" x2="${x}" y2="${yAxis + 7}" stroke="var(--text)" stroke-width="1.2" opacity=".6"/>`;
        s += `<text x="${x}" y="${yAxis - 13}" font-size="12" text-anchor="middle" fill="var(--text-dim)">${i}</text>`;
        s += `<text x="${x}" y="${yKapital}" font-size="11.5" text-anchor="middle" fill="var(--text)" font-weight="600">${esc(euro.format(ki))} €</text>`;
        s += `<text x="${x}" y="${yKapTerm}" font-size="10" text-anchor="middle" fill="var(--text-muted)" font-family="${MONO}">${kapitalTerm(qs, i)}</text>`;
    }

    // Zinsen-Zeile: Bogen je Jahr, Betrag und Rechenweg
    if (zeigeZinsen) {
        s += `<text x="6" y="${yZinsBetrag}" font-size="13" fill="var(--text-dim)">Zinsen</text>`;
        for (let i = 0; i < n; i += 1) {
            const a = x0 + i * step;
            const b = x0 + (i + 1) * step;
            const m = (a + b) / 2;
            const ki = k0 * Math.pow(q, i);
            const zi = ki * p / 100;
            s += `<path d="${arcDown(a, b, yZinsArc, 26)}" fill="none" stroke="var(--text-dim)" stroke-width="1.1" marker-end="url(#${ah})"/>`;
            s += `<text x="${m}" y="${yZinsBetrag}" font-size="11.5" text-anchor="middle" fill="var(--text)" font-weight="600">+ ${esc(euro.format(zi))} €</text>`;
            s += `<text x="${m}" y="${yZinsRechnung}" font-size="9.5" text-anchor="middle" fill="var(--text-muted)" font-family="${MONO}">${esc(euro.format(ki))} · ${ps}/100</text>`;
        }
    }

    // Zinsfaktor-Zeile: ein Bogen je Jahr mit · q
    s += `<text x="6" y="${yFacLabel}" font-size="13" fill="var(--text-dim)">Zinsfaktor</text>`;
    for (let i = 0; i < n; i += 1) {
        const a = x0 + i * step;
        const b = x0 + (i + 1) * step;
        const m = (a + b) / 2;
        s += `<path d="${arcDown(a, b, yFacArc, 22)}" fill="none" stroke="var(--pink)" stroke-width="1.3" marker-end="url(#${ahP})"/>`;
        s += `<text x="${m}" y="${yFacLabel}" font-size="12.5" text-anchor="middle" fill="var(--pink)" font-weight="600">· ${qs}</text>`;
    }

    // großer zusammenfassender Bogen
    s += `<path d="${arcDown(x0, xn, yBigArc, bigLift)}" fill="none" stroke="var(--text)" stroke-width="1.3" opacity=".8" marker-end="url(#${ah})"/>`;
    const midX = (x0 + xn) / 2;
    const badgeY = yBigArc + bigLift * 0.92;
    s += `<rect x="${midX - 60}" y="${badgeY - 16}" width="120" height="26" rx="7" fill="var(--pink-soft)" stroke="var(--pink)" stroke-width="1"/>`;
    s += `<text x="${midX}" y="${badgeY + 3}" font-size="14" text-anchor="middle" fill="var(--pink)" font-weight="600">· ${qs}<tspan dy="-6" font-size="10">${n}</tspan></text>`;

    s += "</svg>";
    return s;
}
