/**
 * Shared Plotly defaults for all chart types across MatheChecks.
 *
 * Import {@link plotlyRender} (or the individual constants) wherever
 * Plotly.newPlot() is called so that transparent backgrounds, hidden
 * mode-bar, scroll pass-through and 2-decimal hover formatting are
 * applied consistently in one place.
 */

/** Layout properties merged into every Plotly figure. */
export const PLOTLY_LAYOUT_DEFAULTS = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    dragmode: false,
};

/** Returns the current CSS --text color (adapts to dark/light theme). */
export function themeTextColor() {
    return getComputedStyle(document.documentElement)
        .getPropertyValue("--text").trim() || "#1a1a2e";
}

/** Config object passed as the fourth argument to Plotly.newPlot(). */
export const PLOTLY_CONFIG = {
    responsive: true,
    displaylogo: false,
    scrollZoom: false,
    staticPlot: false,
    doubleClick: false,
    displayModeBar: false,
};

/**
 * Wrapper around Plotly.newPlot that merges shared defaults
 * and ensures touch scroll pass-through.
 *
 * @param {HTMLElement|string} container – DOM element or element id
 * @param {object[]} data – Plotly trace array
 * @param {object}   [layout={}] – caller layout (takes precedence over defaults)
 * @param {object}   [config={}] – caller config overrides
 * @returns {Promise} – the Plotly.newPlot promise
 */
/**
 * Prevent Plotly from blocking page scroll on touch devices.
 *
 * Plotly registers touchstart handlers on its internal drag-overlay
 * rects and calls preventDefault(), which kills browser scrolling.
 * CSS touch-action alone cannot fix this because the JS handler fires
 * first.  We intercept touchstart in the *capture* phase on the
 * container – before it reaches Plotly's deeper handlers – and call
 * stopPropagation() so Plotly never sees it.  Because the listener is
 * passive, the browser's default scroll action proceeds normally.
 *
 * Mouse/pointer events are unaffected → desktop hover keeps working.
 */
function enableTouchScroll(plotEl) {
    if (!plotEl) return;
    plotEl.addEventListener("touchstart", (e) => {
        e.stopPropagation();
    }, { capture: true, passive: true });

    plotEl.addEventListener("touchmove", (e) => {
        e.stopPropagation();
    }, { capture: true, passive: true });
}

export function plotlyRender(container, data, layout = {}, config = {}) {
    const textColor = themeTextColor();
    const dimColor = textColor + "33";   // ~20 % for gridlines

    const axisDefaults = {
        tickfont: { color: textColor },
        titlefont: { color: textColor },
        gridcolor: dimColor,
        zerolinecolor: textColor + "55",
    };

    const mergedLayout = {
        ...PLOTLY_LAYOUT_DEFAULTS,
        ...layout,
        font: { color: textColor, ...(layout.font || {}) },
        xaxis: { ...axisDefaults, hoverformat: ".2f", ...layout.xaxis },
        yaxis: { ...axisDefaults, hoverformat: ".2f", ...layout.yaxis },
    };

    // Ensure title font inherits theme color
    if (mergedLayout.title && typeof mergedLayout.title === "object") {
        mergedLayout.title.font = { color: textColor, ...(mergedLayout.title.font || {}) };
    }

    // Ensure annotation fonts inherit theme color
    if (Array.isArray(mergedLayout.annotations)) {
        mergedLayout.annotations = mergedLayout.annotations.map((a) => ({
            ...a,
            font: { color: textColor, ...(a.font || {}) },
        }));
    }

    const mergedConfig = { ...PLOTLY_CONFIG, ...config };

    const el = typeof container === "string"
        ? document.getElementById(container)
        : container;

    return window.Plotly.newPlot(el || container, data, mergedLayout, mergedConfig)
        .then((plotEl) => {
            enableTouchScroll(plotEl);
            return plotEl;
        });
}
