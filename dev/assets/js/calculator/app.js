(() => {
    const state = {
        lgsVariables: 2,
        lgsEquations: 2,
        ans: '',
        activeMode: 'basic',
        activeStandardTool: 'sin',
        activeInputId: 'mainInput',
        lastExecutedMainInput: '',
    };

    function byId(id) {
        return document.getElementById(id);
    }

    function getCalculator() {
        return document.querySelector('.calculator--integrated');
    }

    function getMainInput() {
        return byId('mainInput');
    }

    function getMainInputText() {
        return String(getMainInput()?.value || '').trim();
    }

    function setResultStaleState(isStale) {
        const output = document.querySelector('.calculator-output');
        if (!output) return;
        output.classList.toggle('is-stale', Boolean(isStale));
        output.style.opacity = isStale ? '0.68' : '1';
    }

    function syncResultStaleState() {
        setResultStaleState(getMainInputText() !== state.lastExecutedMainInput);
    }

    function markResultFresh(mainInputValue = getMainInputText()) {
        state.lastExecutedMainInput = String(mainInputValue || '').trim();
        setResultStaleState(false);
    }

    function isDesktopDragEnabled() {
        return window.innerWidth >= 520;
    }

    function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    function getCalculatorDragBounds({ width, handleHeight }) {
        const visibleHandleHeight = Math.min(handleHeight || 0, 18);
        const visibleWidth = Math.min(width || 0, 56);
        return {
            minLeft: visibleWidth - width,
            maxLeft: window.innerWidth - visibleWidth,
            minTop: visibleHandleHeight - handleHeight,
            maxTop: window.innerHeight - visibleHandleHeight,
        };
    }

    function clearDraggedCalculatorPosition() {
        const calculator = getCalculator();
        if (!calculator) return;
        calculator.style.removeProperty('position');
        calculator.style.removeProperty('left');
        calculator.style.removeProperty('top');
        calculator.style.removeProperty('right');
        calculator.style.removeProperty('bottom');
        calculator.style.removeProperty('transform');
        calculator.style.removeProperty('margin');
    }

    function normalizeDraggedCalculatorPosition() {
        const calculator = getCalculator();
        const dragHandle = byId('calculatorDragHandle');
        if (!calculator || calculator.style.position !== 'fixed') return;
        if (!isDesktopDragEnabled()) {
            clearDraggedCalculatorPosition();
            return;
        }
        if (!dragHandle) return;
        const rect = calculator.getBoundingClientRect();
        const handleRect = dragHandle.getBoundingClientRect();
        const bounds = getCalculatorDragBounds({
            width: rect.width,
            handleHeight: handleRect.height,
        });
        calculator.style.left = `${clamp(rect.left, bounds.minLeft, bounds.maxLeft)}px`;
        calculator.style.top = `${clamp(rect.top, bounds.minTop, bounds.maxTop)}px`;
    }

    function setActiveInput(input) {
        if (input?.id) {
            state.activeInputId = input.id;
        }
    }

    function getActiveInput() {
        const focused = document.activeElement;
        if (focused?.tagName === 'INPUT' && focused.closest('#calculator-overlay')) {
            return focused;
        }
        return byId(state.activeInputId) || getMainInput();
    }

    function getModeDefinitions() {
        return {
            basic: { icon: '∑', label: 'Standard' },
            lgs: { icon: '▦', label: 'Gleichungssystem' },
            binom: { icon: '◎', label: 'Binomialverteilung' },
            graph: { icon: '↗', label: 'Graph' },
        };
    }

    function getModeDefinition(mode = state.activeMode) {
        return getModeDefinitions()[mode] || getModeDefinitions().basic;
    }

    function updateModePicker(mode = state.activeMode) {
        const { icon, label } = getModeDefinition(mode);
        const picker = byId('calculatorModePicker');
        const iconNode = byId('calculatorModeIcon');
        const modeSelect = byId('calculatorModeSelect');
        const currentLabel = `Eingabehilfe: ${label}`;
        if (picker) {
            picker.dataset.mode = mode;
            picker.title = currentLabel;
            picker.setAttribute('aria-label', currentLabel);
        }
        if (iconNode) {
            iconNode.textContent = icon;
        }
        if (modeSelect) {
            modeSelect.title = `${currentLabel} wechseln`;
            modeSelect.setAttribute('aria-label', `Eingabehilfe wählen, aktuell ${label}`);
        }
    }

    function focusInput(input, placeCursorAtEnd = true) {
        if (!input) return;
        setActiveInput(input);
        input.focus({ preventScroll: true });
        if (placeCursorAtEnd && input.setSelectionRange) {
            const pos = input.value?.length || 0;
            input.setSelectionRange(pos, pos);
        }
    }

    function emitInputEvent(input) {
        if (!input) return;
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function insertAtCursor(input, value) {
        const currentValue = input.value || '';
        const start = input.selectionStart ?? currentValue.length;
        const end = input.selectionEnd ?? start;
        input.value = currentValue.slice(0, start) + value + currentValue.slice(end);
        const nextPos = start + value.length;
        if (input.setSelectionRange) {
            input.setSelectionRange(nextPos, nextPos);
        }
    }

    function insertIntoActiveInput(value) {
        const target = getActiveInput() || getMainInput();
        if (!target) return;
        insertAtCursor(target, value === '()' ? '()' : value);
        if (value === '()' && target.setSelectionRange) {
            const pos = (target.selectionStart ?? target.value.length) - 1;
            target.setSelectionRange(pos, pos);
        }
        focusInput(target, false);
        emitInputEvent(target);
    }

    function insertIntoMainInput(value) {
        const mainInput = getMainInput();
        if (!mainInput) return;
        insertAtCursor(mainInput, value);
        focusInput(mainInput, false);
        emitInputEvent(mainInput);
    }

    function setMainInputValue(value, { focusMainInput = false } = {}) {
        const mainInput = getMainInput();
        if (!mainInput) return;
        mainInput.value = value;
        syncResultStaleState();
        if (focusMainInput) {
            focusInput(mainInput);
        }
    }

    function clearActiveInput() {
        const target = getActiveInput() || getMainInput();
        if (!target) return;
        target.value = '';
        focusInput(target, false);
        emitInputEvent(target);
        if (target === getMainInput()) {
            outputApi.setText('0', { headline: 'Bereit' });
            markResultFresh('');
        }
    }

    function backspaceActiveInput() {
        const target = getActiveInput() || getMainInput();
        if (!target) return;
        const start = target.selectionStart ?? target.value.length;
        const end = target.selectionEnd ?? start;
        if (start !== end) {
            target.value = target.value.slice(0, start) + target.value.slice(end);
            target.setSelectionRange?.(start, start);
        } else if (start > 0) {
            target.value = target.value.slice(0, start - 1) + target.value.slice(end);
            target.setSelectionRange?.(start - 1, start - 1);
        }
        focusInput(target, false);
        emitInputEvent(target);
    }

    function setMode(mode) {
        state.activeMode = getModeDefinitions()[mode] ? mode : 'basic';
        const calculator = getCalculator();
        if (calculator) {
            calculator.dataset.activeMode = state.activeMode;
        }
        const modeSelect = byId('calculatorModeSelect');
        if (modeSelect && modeSelect.value !== state.activeMode) {
            modeSelect.value = state.activeMode;
        }
        updateModePicker(state.activeMode);
        document.querySelectorAll('.calculator-panel').forEach((panel) => {
            panel.classList.toggle('is-active', panel.dataset.panel === state.activeMode);
        });
        queueMicrotask(() => {
            if (state.activeMode === 'basic') {
                focusInput(getMainInput());
                return;
            }
            const firstInput = document.querySelector(`.calculator-panel[data-panel="${state.activeMode}"] input`);
            if (firstInput) {
                focusInput(firstInput, false);
            }
        });
    }

    function renderLGSMatrix() {
        const container = byId('lgsMatrix');
        if (!container) return;
        const existingValues = {};
        container.querySelectorAll('input').forEach((input) => {
            existingValues[input.id] = input.value;
        });
        container.innerHTML = '';
        for (let equationIndex = 0; equationIndex < state.lgsEquations; equationIndex++) {
            const row = document.createElement('div');
            row.className = 'input-row';
            for (let variableIndex = 0; variableIndex < state.lgsVariables; variableIndex++) {
                if (variableIndex > 0) {
                    const plus = document.createElement('span');
                    plus.className = 'lgs-operator';
                    plus.textContent = '+';
                    row.appendChild(plus);
                }
                const input = document.createElement('input');
                input.type = 'text';
                input.id = `a${equationIndex}${variableIndex}`;
                input.value = existingValues[input.id] ?? '';
                row.appendChild(input);
                const variableLabel = document.createElement('span');
                variableLabel.className = 'lgs-var-label';
                variableLabel.textContent = DevCalculatorCommands.getLGSVariableName(variableIndex);
                row.appendChild(variableLabel);
            }
            const equals = document.createElement('span');
            equals.className = 'lgs-equals';
            equals.textContent = '=';
            row.appendChild(equals);
            const resultInput = document.createElement('input');
            resultInput.type = 'text';
            resultInput.id = `b${equationIndex}`;
            resultInput.value = existingValues[resultInput.id] ?? '';
            row.appendChild(resultInput);
            container.appendChild(row);
        }
    }

    function getLGSValues() {
        const values = {};
        document.querySelectorAll('#lgsMatrix input').forEach((input) => {
            values[input.id] = input.value;
        });
        return values;
    }

    function getBinomFields() {
        return {
            a: byId('binomA')?.value || '',
            b: byId('binomB')?.value || '',
            n: byId('binomN')?.value || '',
            p: byId('binomP')?.value || '',
        };
    }

    function getGraphFields() {
        return {
            function: byId('graphFunction')?.value || '',
            xmin: byId('graphXMin')?.value || '',
            xmax: byId('graphXMax')?.value || '',
            ymin: byId('graphYMin')?.value || '',
            ymax: byId('graphYMax')?.value || '',
        };
    }

    function setGraphFields(fields = {}) {
        const nextFields = {
            graphFunction: fields.function ?? '',
            graphXMin: fields.xmin ?? '',
            graphXMax: fields.xmax ?? '',
            graphYMin: fields.ymin ?? '',
            graphYMax: fields.ymax ?? '',
        };
        Object.entries(nextFields).forEach(([id, value]) => {
            const input = byId(id);
            if (input) {
                input.value = value;
            }
        });
    }

    function clearGraphPanelPreview() {
        const graphPanelPreview = byId('graphPanelPreview');
        const graphPanelInfo = byId('graphPanelInfo');
        if (graphPanelPreview) {
            graphPanelPreview.innerHTML = '';
            graphPanelPreview.hidden = true;
        }
        if (graphPanelInfo) {
            graphPanelInfo.innerHTML = '';
            graphPanelInfo.hidden = true;
        }
    }

    function showGraphPanelMessage(message) {
        const graphPanelInfo = byId('graphPanelInfo');
        if (!graphPanelInfo) return;
        graphPanelInfo.innerHTML = '';
        const item = document.createElement('div');
        item.className = 'point-item';
        item.textContent = message;
        graphPanelInfo.appendChild(item);
        graphPanelInfo.hidden = false;
    }

    function renderGraphPanelPreview({ funktionen, optionen, pointsHtml }) {
        const graphPanelPreview = byId('graphPanelPreview');
        const graphPanelInfo = byId('graphPanelInfo');
        if (!graphPanelPreview) return false;

        graphPanelPreview.innerHTML = '';
        graphPanelPreview.hidden = false;

        if (graphPanelInfo) {
            graphPanelInfo.innerHTML = pointsHtml || '';
            graphPanelInfo.hidden = !Boolean(pointsHtml);
        }

        try {
            if (typeof window.renderDevCalculatorGraph !== 'function' || typeof window.Plotly === 'undefined') {
                throw new Error('graph-renderer-unavailable');
            }
            window.renderDevCalculatorGraph('graphPanelPreview', funktionen, optionen);
            return true;
        } catch {
            graphPanelPreview.innerHTML = '';
            graphPanelPreview.hidden = true;
            showGraphPanelMessage('Graph konnte nicht dargestellt werden.');
            return false;
        }
    }

    const liveGraphOutputApi = {
        setText(text) {
            clearGraphPanelPreview();
            showGraphPanelMessage(String(text || 'Ungültiger Graph-Term').trim());
        },
        setGraph({ funktionen, optionen, pointsHtml }) {
            renderGraphPanelPreview({ funktionen, optionen, pointsHtml });
        },
    };

    function syncGraphLivePreview() {
        const fields = getGraphFields();
        if (!String(fields.function || '').trim()) {
            clearGraphPanelPreview();
            return;
        }
        DevCalculatorCommands.execute(DevCalculatorCommands.buildGraphCommand(fields), liveGraphOutputApi);
    }

    function getGraphCommandFromPanel() {
        const fields = getGraphFields();
        if (!String(fields.function || '').trim()) return '';
        return DevCalculatorCommands.buildGraphCommand(fields);
    }

    const outputApi = {
        setText(text, options = {}) {
            const outputRoot = document.querySelector('.calculator-output');
            const textOutput = byId('calculatorTextOutput');
            const resultDisplay = byId('resultDisplay');
            const detailText = String(options.detail || '').trim();
            if (textOutput) {
                textOutput.textContent = detailText;
                textOutput.classList.toggle('is-active', Boolean(detailText));
            }
            clearGraphPanelPreview();
            outputRoot?.classList.remove('has-graph-output');
            outputRoot?.classList.toggle('has-secondary-content', Boolean(detailText));
            if (resultDisplay) resultDisplay.textContent = text;
            state.ans = text;
        },

        setGraph({ targetId, funktionen, optionen, pointsHtml, panelFields, resultText = 'Graph' }) {
            const outputRoot = document.querySelector('.calculator-output');
            const textOutput = byId('calculatorTextOutput');
            const resultDisplay = byId('resultDisplay');
            if (textOutput) {
                textOutput.textContent = '';
                textOutput.classList.remove('is-active');
            }
            outputRoot?.classList.remove('has-secondary-content');
            outputRoot?.classList.remove('has-graph-output');
            if (resultDisplay) resultDisplay.textContent = resultText;
            setMode('graph');
            setGraphFields(panelFields);
            if (targetId === 'graphPanelPreview' && !renderGraphPanelPreview({ funktionen, optionen, pointsHtml })) {
                if (resultDisplay) resultDisplay.textContent = 'Graphfehler';
            }
            state.ans = '';
        },
    };

    function syncBinomPreview() {
        const fields = getBinomFields();
        const commandTarget = byId('binomCommandPreview');
        const resultTarget = byId('binomLiveResult');
        const previewParts = [fields.a, fields.b, fields.n, fields.p].map((value) => String(value || '').trim() || '...');
        if (commandTarget) {
            commandTarget.textContent = `binom(${previewParts.join(';')})`;
        }
        if (!resultTarget) return;
        resultTarget.textContent = DevCalculatorCommands.getLiveBinomResult(fields);
    }

    function syncLGSCommandPreview(options = {}) {
        if (!options.commitToMainInput) return;
        setMainInputValue(
            DevCalculatorCommands.buildLGSCommand({
                variables: state.lgsVariables,
                equations: state.lgsEquations,
                values: getLGSValues(),
            }),
            options
        );
    }

    function syncBinomCommandPreview(options = {}) {
        syncBinomPreview();
        if (!options.commitToMainInput) return;
        setMainInputValue(DevCalculatorCommands.buildBinomCommand(getBinomFields()), options);
    }

    function requireFilledFields(ids) {
        for (const id of ids) {
            const input = byId(id);
            if (!input) continue;
            if (!String(input.value || '').trim()) {
                focusInput(input, false);
                return false;
            }
        }
        return true;
    }

    function getStandardToolDefinitions() {
        return {
            sin: {
                focusId: 'funcSinValue',
                requiredIds: ['funcSinValue'],
                action: 'apply-func-sin',
                preview: () => `sin(${String(byId('funcSinValue')?.value || '').trim() || '...'})`,
                build: () => DevCalculatorCommands.buildUnaryFunctionExpression('sin', byId('funcSinValue')?.value || ''),
            },
            cos: {
                focusId: 'funcCosValue',
                requiredIds: ['funcCosValue'],
                action: 'apply-func-cos',
                preview: () => `cos(${String(byId('funcCosValue')?.value || '').trim() || '...'})`,
                build: () => DevCalculatorCommands.buildUnaryFunctionExpression('cos', byId('funcCosValue')?.value || ''),
            },
            tan: {
                focusId: 'funcTanValue',
                requiredIds: ['funcTanValue'],
                action: 'apply-func-tan',
                preview: () => `tan(${String(byId('funcTanValue')?.value || '').trim() || '...'})`,
                build: () => DevCalculatorCommands.buildUnaryFunctionExpression('tan', byId('funcTanValue')?.value || ''),
            },
            ln: {
                focusId: 'funcLnValue',
                requiredIds: ['funcLnValue'],
                action: 'apply-func-ln',
                preview: () => `ln(${String(byId('funcLnValue')?.value || '').trim() || '...'})`,
                build: () => DevCalculatorCommands.buildUnaryFunctionExpression('ln', byId('funcLnValue')?.value || ''),
            },
            log: {
                focusId: 'funcLogBase',
                requiredIds: ['funcLogBase', 'funcLogValue'],
                action: 'apply-func-log',
                preview: () => {
                    const base = String(byId('funcLogBase')?.value || '').trim() || '...';
                    const value = String(byId('funcLogValue')?.value || '').trim() || '...';
                    return `log(${base};${value})`;
                },
                build: () => DevCalculatorCommands.buildLogExpression({
                    base: byId('funcLogBase')?.value || '',
                    value: byId('funcLogValue')?.value || '',
                }),
            },
            fraction: {
                focusId: 'funcFractionTop',
                requiredIds: ['funcFractionTop', 'funcFractionBottom'],
                action: 'apply-func-fraction',
                preview: () => {
                    const numerator = String(byId('funcFractionTop')?.value || '').trim() || '...';
                    const denominator = String(byId('funcFractionBottom')?.value || '').trim() || '...';
                    return `(${numerator})/(${denominator})`;
                },
                build: () => DevCalculatorCommands.buildFractionExpression({
                    numerator: byId('funcFractionTop')?.value || '',
                    denominator: byId('funcFractionBottom')?.value || '',
                }),
            },
            power: {
                focusId: 'funcPowerBase',
                requiredIds: ['funcPowerBase', 'funcPowerExponent'],
                action: 'apply-func-power',
                preview: () => {
                    const base = String(byId('funcPowerBase')?.value || '').trim() || '...';
                    const exponent = String(byId('funcPowerExponent')?.value || '').trim() || '...';
                    return `(${base})^(${exponent})`;
                },
                build: () => DevCalculatorCommands.buildPowerExpression({
                    base: byId('funcPowerBase')?.value || '',
                    exponent: byId('funcPowerExponent')?.value || '',
                }),
            },
        };
    }

    function getStandardToolDefinition(tool = state.activeStandardTool) {
        return getStandardToolDefinitions()[tool] || getStandardToolDefinitions().sin;
    }

    function updateStandardToolPreview() {
        const definition = getStandardToolDefinition();
        const previewTarget = byId('standardToolPreview');
        const liveTarget = byId('standardToolLiveResult');
        const previewText = definition.preview();
        if (previewTarget) {
            previewTarget.textContent = previewText;
        }
        if (!liveTarget) return;
        const hasAllInputs = definition.requiredIds.every((id) => String(byId(id)?.value || '').trim());
        if (!hasAllInputs) {
            liveTarget.textContent = 'Wert: -';
            return;
        }
        try {
            const value = DevCalculatorUtils.evaluateExpression(definition.build());
            liveTarget.textContent = `Wert: ${DevCalculatorUtils.formatGeneralResult(value)}`;
        } catch {
            liveTarget.textContent = /(^|[^a-zA-Z])x([^a-zA-Z]|$)/i.test(previewText)
                ? 'Wert: von x abhängig'
                : 'Wert: -';
        }
    }

    function setStandardTool(tool, { focus = true } = {}) {
        state.activeStandardTool = getStandardToolDefinitions()[tool] ? tool : 'sin';
        const toolSelect = byId('standardToolSelect');
        if (toolSelect && toolSelect.value !== state.activeStandardTool) {
            toolSelect.value = state.activeStandardTool;
        }
        document.querySelectorAll('.standard-tool-editor').forEach((panel) => {
            const isActive = panel.dataset.standardToolPanel === state.activeStandardTool;
            panel.classList.toggle('is-active', isActive);
            panel.hidden = !isActive;
        });
        updateStandardToolPreview();
        if (!focus) return;
        const focusTarget = byId(getStandardToolDefinition().focusId);
        if (focusTarget) {
            focusInput(focusTarget, false);
        }
    }

    function applySelectedStandardTool() {
        applyFunctionBuilder(getStandardToolDefinition().action);
    }

    function applyFunctionBuilder(action) {
        const unaryBuilders = {
            'apply-func-sin': { fieldId: 'funcSinValue', name: 'sin' },
            'apply-func-cos': { fieldId: 'funcCosValue', name: 'cos' },
            'apply-func-tan': { fieldId: 'funcTanValue', name: 'tan' },
            'apply-func-ln': { fieldId: 'funcLnValue', name: 'ln' },
        };

        if (unaryBuilders[action]) {
            const { fieldId, name } = unaryBuilders[action];
            if (!requireFilledFields([fieldId])) return;
            insertIntoMainInput(
                DevCalculatorCommands.buildUnaryFunctionExpression(name, byId(fieldId).value)
            );
            return;
        }

        if (action === 'apply-func-log') {
            if (!requireFilledFields(['funcLogBase', 'funcLogValue'])) return;
            insertIntoMainInput(
                DevCalculatorCommands.buildLogExpression({
                    base: byId('funcLogBase').value,
                    value: byId('funcLogValue').value,
                })
            );
            return;
        }
        if (action === 'apply-func-fraction') {
            if (!requireFilledFields(['funcFractionTop', 'funcFractionBottom'])) return;
            insertIntoMainInput(
                DevCalculatorCommands.buildFractionExpression({
                    numerator: byId('funcFractionTop').value,
                    denominator: byId('funcFractionBottom').value,
                })
            );
            return;
        }
        if (action === 'apply-func-power') {
            if (!requireFilledFields(['funcPowerBase', 'funcPowerExponent'])) return;
            insertIntoMainInput(
                DevCalculatorCommands.buildPowerExpression({
                    base: byId('funcPowerBase').value,
                    exponent: byId('funcPowerExponent').value,
                })
            );
        }
    }

    function formatStepValue(value, step) {
        if (Math.abs(step) >= 1) {
            return String(Math.round(value));
        }
        const decimals = step.toString().split('.')[1]?.length || 0;
        const rounded = Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
        return String(rounded).replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1').replace('.', ',');
    }

    function adjustBinomValue(targetId, step) {
        const input = byId(targetId);
        if (!input) return;
        const raw = DevCalculatorUtils.normalizeNumberString(input.value || '0');
        const current = parseFloat(raw);
        const next = (Number.isNaN(current) ? 0 : current) + step;
        input.value = formatStepValue(next, step);
        focusInput(input, false);
        emitInputEvent(input);
    }

    function executeMainInput() {
        const mainInput = getMainInput();
        if (!mainInput) return;
        DevCalculatorCommands.execute(mainInput.value || '0', outputApi);
        markResultFresh(mainInput.value || '');
    }

    function resetCalculatorView() {
        clearDraggedCalculatorPosition();
        setMode('basic');
        setStandardTool('sin', { focus: false });
        document.querySelector('.calculator-panels')?.scrollTo({ top: 0 });
        document.querySelector('.calculator-output-body')?.scrollTo({ top: 0 });
        focusInput(getMainInput());
    }

    function bindCalculatorDrag() {
        const calculator = getCalculator();
        const dragHandle = byId('calculatorDragHandle');
        if (!calculator || !dragHandle) return;

        let dragState = null;

        const finishDrag = (event) => {
            if (!dragState) return;
            if (dragHandle.releasePointerCapture) {
                try {
                    dragHandle.releasePointerCapture(event.pointerId);
                } catch {
                    // Ignore release errors if the pointer is already gone.
                }
            }
            calculator.classList.remove('dragging');
            dragState = null;
        };

        dragHandle.addEventListener('pointerdown', (event) => {
            if (!isDesktopDragEnabled()) return;
            if (event.button !== 0) return;
            if (event.target.closest('button, input, select, textarea, a')) return;

            const rect = calculator.getBoundingClientRect();
            dragState = {
                pointerId: event.pointerId,
                offsetX: event.clientX - rect.left,
                offsetY: event.clientY - rect.top,
                width: rect.width,
                height: rect.height,
                handleHeight: dragHandle.getBoundingClientRect().height,
            };

            calculator.classList.add('dragging');
            dragHandle.setPointerCapture?.(event.pointerId);
            event.preventDefault();
        });

        dragHandle.addEventListener('pointermove', (event) => {
            if (!dragState || event.pointerId !== dragState.pointerId) return;

            const bounds = getCalculatorDragBounds(dragState);
            const left = clamp(event.clientX - dragState.offsetX, bounds.minLeft, bounds.maxLeft);
            const top = clamp(event.clientY - dragState.offsetY, bounds.minTop, bounds.maxTop);

            calculator.style.position = 'fixed';
            calculator.style.left = `${left}px`;
            calculator.style.top = `${top}px`;
            calculator.style.right = 'auto';
            calculator.style.bottom = 'auto';
            calculator.style.transform = 'none';
            calculator.style.margin = '0';
        });

        dragHandle.addEventListener('pointerup', finishDrag);
        dragHandle.addEventListener('pointercancel', finishDrag);
        window.addEventListener('resize', normalizeDraggedCalculatorPosition);
    }

    function closeOverlay() {
        if (typeof window.toggleCalculatorOverlay === 'function') {
            window.toggleCalculatorOverlay(false);
        }
    }

    function copyResult() {
        const calculator = getCalculator();
        const resultDisplay = byId('resultDisplay');
        const textOutput = byId('calculatorTextOutput');
        const mainInput = getMainInput();
        const visibleResult = resultDisplay && getComputedStyle(resultDisplay).display !== 'none'
            ? resultDisplay.textContent?.trim()
            : '';
        const visibleDetail = textOutput?.classList.contains('is-active') ? textOutput.textContent?.trim() : '';
        const fallback = mainInput?.value?.trim() || '';
        const graphCommand = getGraphCommandFromPanel();
        const resultText = calculator?.dataset.activeMode === 'graph'
            ? graphCommand
            : visibleResult || visibleDetail || fallback;
        if (!resultText) return;
        navigator.clipboard?.writeText(resultText);
        const button = byId('copyResultButton');
        if (!button) return;
        button.classList.remove('copied');
        void button.offsetWidth;
        button.classList.add('copied');
        window.setTimeout(() => button.classList.remove('copied'), 1200);
    }

    function bindEvents() {
        document.addEventListener('focusin', (event) => {
            if (event.target?.tagName === 'INPUT' && event.target.closest('#calculator-overlay')) {
                setActiveInput(event.target);
            }
        });

        byId('calculatorModeSelect')?.addEventListener('change', (event) => {
            setMode(event.target.value);
        });

        byId('standardToolSelect')?.addEventListener('change', (event) => {
            setStandardTool(event.target.value);
        });

        document.querySelectorAll('[data-standard-input]').forEach((input) => {
            input.addEventListener('input', updateStandardToolPreview);
        });

        document.querySelector('.standard-tool-editors')?.addEventListener('keydown', (event) => {
            if (event.key !== 'Enter') return;
            event.preventDefault();
            applySelectedStandardTool();
        });

        document.querySelectorAll('[data-open-mode]').forEach((button) => {
            button.addEventListener('click', () => setMode(button.dataset.openMode));
        });

        document.querySelector('.buttons--shared')?.addEventListener('click', (event) => {
            const button = event.target.closest('button');
            if (!button) return;
            const insertValue = button.dataset.insert;
            const action = button.dataset.action;

            if (insertValue) {
                insertIntoActiveInput(insertValue);
                return;
            }
            if (action === 'clear') {
                clearActiveInput();
                return;
            }
            if (action === 'backspace') {
                backspaceActiveInput();
                return;
            }
            if (action === 'insert-ans') {
                insertIntoActiveInput(state.ans || '');
                return;
            }
            if (action === 'execute') {
                if (state.activeMode === 'graph') {
                    syncGraphLivePreview();
                    return;
                }
                executeMainInput();
            }
        });

        byId('closeCalculatorButton')?.addEventListener('click', closeOverlay);
        byId('resetCalculatorViewButton')?.addEventListener('click', resetCalculatorView);
        byId('copyResultButton')?.addEventListener('click', copyResult);

        getMainInput()?.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                executeMainInput();
            }
        });

        getMainInput()?.addEventListener('input', () => {
            syncResultStaleState();
        });

        byId('lgsMatrix')?.addEventListener('input', () => {
            syncLGSCommandPreview();
        });

        ['binomA', 'binomB', 'binomN', 'binomP'].forEach((id) => {
            byId(id)?.addEventListener('input', () => {
                syncBinomCommandPreview();
            });
        });

        document.querySelectorAll('.binom-step').forEach((button) => {
            button.addEventListener('click', () => {
                adjustBinomValue(button.dataset.target, Number(button.dataset.step));
            });
        });

        ['graphFunction', 'graphXMin', 'graphXMax', 'graphYMin', 'graphYMax'].forEach((id) => {
            byId(id)?.addEventListener('input', () => {
                syncGraphLivePreview();
            });
        });

        document.querySelector('[data-action="apply-lgs"]')?.addEventListener('click', () => {
            syncLGSCommandPreview({ commitToMainInput: true, focusMainInput: true });
        });

        document.querySelector('[data-action="apply-binom"]')?.addEventListener('click', () => {
            syncBinomCommandPreview({ commitToMainInput: true, focusMainInput: true });
        });

        document.querySelector('[data-action="apply-standard-tool"]')?.addEventListener('click', () => {
            applySelectedStandardTool();
        });

        ['apply-func-sin', 'apply-func-cos', 'apply-func-tan', 'apply-func-ln', 'apply-func-log', 'apply-func-fraction', 'apply-func-power'].forEach((action) => {
            document.querySelector(`[data-action="${action}"]`)?.addEventListener('click', () => {
                applyFunctionBuilder(action);
            });
        });

        document.querySelector('[data-action="lgs-add-var"]')?.addEventListener('click', () => {
            if (state.lgsVariables < 6) {
                state.lgsVariables += 1;
                renderLGSMatrix();
                syncLGSCommandPreview();
            }
        });
        document.querySelector('[data-action="lgs-remove-var"]')?.addEventListener('click', () => {
            if (state.lgsVariables > 1) {
                state.lgsVariables -= 1;
                renderLGSMatrix();
                syncLGSCommandPreview();
            }
        });
        document.querySelector('[data-action="lgs-add-eq"]')?.addEventListener('click', () => {
            if (state.lgsEquations < 6) {
                state.lgsEquations += 1;
                renderLGSMatrix();
                syncLGSCommandPreview();
            }
        });
        document.querySelector('[data-action="lgs-remove-eq"]')?.addEventListener('click', () => {
            if (state.lgsEquations > 1) {
                state.lgsEquations -= 1;
                renderLGSMatrix();
                syncLGSCommandPreview();
            }
        });
    }

    function init() {
        if (!byId('calculator-overlay')) return;
        renderLGSMatrix();
        syncBinomPreview();
        outputApi.setText('0', { headline: 'Bereit' });
        markResultFresh('');
        bindEvents();
        bindCalculatorDrag();
        updateModePicker(state.activeMode);
        setStandardTool(state.activeStandardTool, { focus: false });
        focusInput(getMainInput());
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
