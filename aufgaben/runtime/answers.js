export function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function escapeHtmlAttribute(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

export function parseMcOptions(raw) {
    return String(raw)
        .split(/(?<!\\)~/)
        .map((option) => option.trim())
        .filter((option) => option.length > 0)
        .map((option) => {
            const correct = option.startsWith("=");
            return {
                correct,
                label: correct ? option.slice(1).trim() : option,
            };
        });
}

function unescapeMoodleText(value) {
    return String(value)
        .replaceAll("\\~", "~")
        .replaceAll("\\=", "=")
        .replaceAll("\\#", "#")
        .replaceAll("\\:", ":")
        .trim();
}

function parseNumber(raw) {
    const normalized = String(raw ?? "")
        .trim()
        .replaceAll(" ", "")
        .replaceAll(",", ".");

    if (normalized.length === 0) {
        return Number.NaN;
    }

    return Number.parseFloat(normalized);
}

function getPlaceholderSpecs(answerText) {
    const specs = [];
    replaceAnswerPlaceholders(answerText, (kind, raw) => {
        specs.push({ kind, raw });
        return "";
    });
    return specs;
}

function evaluateNumerical(raw, userValue) {
    const numericalMatch = String(raw).match(/=([^:}#]+):([^:}#]+)/);
    if (!numericalMatch) {
        return { isCorrect: false, isComplete: false, expected: null };
    }

    const expected = parseNumber(numericalMatch[1]);
    const tolerance = Math.abs(parseNumber(numericalMatch[2]));
    const entered = parseNumber(userValue);

    if (Number.isNaN(entered)) {
        return {
            isCorrect: false,
            isComplete: String(userValue ?? "").trim().length > 0,
            expected,
        };
    }

    if (Number.isNaN(expected) || Number.isNaN(tolerance)) {
        return { isCorrect: false, isComplete: false, expected: null };
    }

    return {
        isCorrect: Math.abs(entered - expected) <= tolerance,
        isComplete: true,
        expected,
    };
}

function evaluateNumericalOpt(raw, userValue, noneChecked) {
    const rawTrimmed = String(raw).trim();
    const isNoneExpected = rawTrimmed.toUpperCase() === "=NONE" || rawTrimmed.toUpperCase() === "NONE";

    if (isNoneExpected) {
        return {
            isCorrect: Boolean(noneChecked),
            isComplete: Boolean(noneChecked) || String(userValue ?? "").trim().length > 0,
            expected: null,
            expectedNone: true,
        };
    }

    if (noneChecked) {
        return { isCorrect: false, isComplete: true, expected: null, expectedNone: false };
    }

    return evaluateNumerical(raw, userValue);
}

function evaluateMc(raw, userValue) {
    const selected = String(userValue ?? "").trim();
    if (!selected) {
        return { isCorrect: false, isComplete: false };
    }

    const correct = parseMcOptions(raw).find((option) => option.correct);
    if (!correct) {
        return { isCorrect: false, isComplete: false };
    }

    return {
        isCorrect: selected === unescapeMoodleText(correct.label),
        isComplete: true,
    };
}

export function replaceAnswerPlaceholders(answerText, renderPlaceholder) {
    const source = String(answerText ?? "");
    const result = [];
    let index = 0;
    let placeholderIndex = 0;

    while (index < source.length) {
        const start = source.indexOf("{", index);
        if (start === -1) {
            result.push(source.slice(index));
            break;
        }

        result.push(source.slice(index, start));

        const maybePlaceholder = source.slice(start);
        const match = maybePlaceholder.match(/^\{(\d+):(NUMERICAL_OPT|NUMERICAL|MC):/);
        if (!match) {
            result.push("{");
            index = start + 1;
            continue;
        }

        let braceLevel = 1;
        let end = start + 1;
        while (end < source.length && braceLevel > 0) {
            if (source[end] === "{") braceLevel += 1;
            if (source[end] === "}") braceLevel -= 1;
            end += 1;
        }

        if (braceLevel !== 0) {
            result.push(source.slice(start));
            break;
        }

        const kind = match[2];
        const prefix = `{${match[1]}:${kind}:`;
        const fullMatch = source.slice(start, end);
        const raw = fullMatch.slice(prefix.length, -1);

        result.push(renderPlaceholder(kind, raw, { placeholderIndex }));
        placeholderIndex += 1;
        index = end;
    }

    return result.join("");
}

export function answerToPreview(answerText) {
    return replaceAnswerPlaceholders(answerText, (kind, raw, meta) => {
        if (kind === "NUMERICAL_OPT") {
            return `<span class="answer-numopt-group" data-answer-part="${meta.placeholderIndex}" data-kind="NUMERICAL_OPT" data-raw="${escapeHtmlAttribute(raw)}"><input class="answer-numopt-input" type="text" placeholder="Antwort" /><label class="answer-numopt-label" title="keine Lösung"><input type="checkbox" class="answer-numopt-none" /> 🚫</label></span>`;
        }

        if (kind === "NUMERICAL") {
            return `<input class="answer-input" data-answer-part="${meta.placeholderIndex}" type="text" placeholder="Antwort" />`;
        }

        const options = parseMcOptions(raw)
            .map((option) => {
                const latexLabel = unescapeMoodleText(option.label);
                const encodedLatex = encodeURIComponent(latexLabel);
                return `<option value="${escapeHtmlAttribute(latexLabel)}" data-latex="${escapeHtmlAttribute(encodedLatex)}">${escapeHtml(latexLabel)}</option>`;
            })
            .join("");

        return `<select class="answer-select" data-answer-part="${meta.placeholderIndex}"><option selected value="">Antwort</option>${options}</select>`;
    });
}

export function answerToSolution(answerText) {
    return replaceAnswerPlaceholders(answerText, (kind, raw) => {
        if (kind === "NUMERICAL_OPT") {
            const rawUpper = String(raw).trim().toUpperCase();
            if (rawUpper === "=NONE" || rawUpper === "NONE") {
                return '<span class="solution-badge">existiert nicht</span>';
            }
            const numericalMatch = String(raw).match(/=([^:}]+):([^:}]+)/);
            if (!numericalMatch) {
                return '<span class="solution-badge">NUMERICAL_OPT</span>';
            }
            const value = escapeHtml(numericalMatch[1]);
            const tolerance = escapeHtml(numericalMatch[2]);
            return `<span class="solution-badge">${value} (±${tolerance})</span>`;
        }

        if (kind === "NUMERICAL") {
            const numericalMatch = String(raw).match(/=([^:}]+):([^:}]+)/);
            if (!numericalMatch) {
                return '<span class="solution-badge">NUMERICAL</span>';
            }
            const value = escapeHtml(numericalMatch[1]);
            const tolerance = escapeHtml(numericalMatch[2]);
            return `<span class="solution-badge">${value} (±${tolerance})</span>`;
        }

        const correct = parseMcOptions(raw).find((option) => option.correct);
        if (!correct) {
            return '<span class="solution-badge">MC</span>';
        }
        return `<span class="solution-badge">${escapeHtml(unescapeMoodleText(correct.label))}</span>`;
    });
}

export function evaluateAnswerFields(answerText, answerPreviewNode) {
    const specs = getPlaceholderSpecs(answerText);
    const controls = Array.from(
        answerPreviewNode?.querySelectorAll("[data-answer-part]") || []
    );

    const parts = specs.map((spec, index) => {
        const control = controls[index] || null;

        if (spec.kind === "NUMERICAL_OPT") {
            const inputField = control?.querySelector?.(".answer-numopt-input");
            const noneCheckbox = control?.querySelector?.(".answer-numopt-none");
            const value = inputField ? inputField.value : "";
            const noneChecked = noneCheckbox ? noneCheckbox.checked : false;
            const result = evaluateNumericalOpt(spec.raw, value, noneChecked);
            return {
                kind: spec.kind,
                control,
                isCorrect: result.isCorrect,
                isComplete: result.isComplete,
            };
        }

        const value = control ? control.value : "";

        if (spec.kind === "NUMERICAL") {
            const result = evaluateNumerical(spec.raw, value);
            return {
                kind: spec.kind,
                control,
                isCorrect: result.isCorrect,
                isComplete: result.isComplete,
            };
        }

        const result = evaluateMc(spec.raw, value);
        return {
            kind: spec.kind,
            control,
            isCorrect: result.isCorrect,
            isComplete: result.isComplete,
        };
    });

    const expectedCount = specs.length;
    const answeredCount = parts.filter((part) => part.isComplete).length;
    const isComplete = expectedCount > 0 ? answeredCount === expectedCount : true;
    const isCorrect = expectedCount > 0 ? isComplete && parts.every((part) => part.isCorrect) : false;

    return {
        isCorrect,
        isComplete,
        expectedCount,
        answeredCount,
        parts,
    };
}
