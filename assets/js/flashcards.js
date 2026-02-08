"use strict";

const storageKey = `flashcards:${window.lernbereich || ""}`;
const msPerDay = 24 * 60 * 60 * 1000;

const state = {
    cards: [],
    progress: {},
    currentCard: null,
};

function loadProgress() {
    try {
        const raw = localStorage.getItem(storageKey);
        state.progress = raw ? JSON.parse(raw) : {};
    } catch (err) {
        console.warn("Flashcards: progress reset due to error", err);
        state.progress = {};
    }
}

function saveProgress() {
    localStorage.setItem(storageKey, JSON.stringify(state.progress));
}

function getCardState(cardId) {
    const entry = state.progress[cardId];
    if (!entry) {
        return { reps: 0, interval: 0, ease: 2.5, due: 0 };
    }
    return entry;
}

function setCardState(cardId, data) {
    state.progress[cardId] = data;
    saveProgress();
}

function buildCardId(entry, aufgabeIndex, frageIndex) {
    const suffix = frageIndex === null ? "all" : String(frageIndex);
    return `${entry.Sammlung}::${aufgabeIndex}::${suffix}`;
}

function buildIndexCardId(entry, frageIndex) {
    return `${entry.Sammlung}::index::${frageIndex}`;
}

function extractMultipleChoice(text) {
    const result = [];
    let index = 0;

    while (index < text.length) {
        const start = text.indexOf("{", index);
        if (start === -1) {
            result.push(text.slice(index));
            break;
        }

        result.push(text.slice(index, start));
        const rest = text.slice(start);
        const mcMatch = rest.match(/^\{(\d+):(MC|MCV|MULTICHOICE):/);
        if (!mcMatch) {
            result.push("{");
            index = start + 1;
            continue;
        }

        let braceLevel = 0;
        let end = start;
        while (end < text.length) {
            if (text[end] === "{") braceLevel++;
            if (text[end] === "}") braceLevel--;
            if (braceLevel === 0 && end > start) break;
            end++;
        }

        const fullMatch = text.slice(start, end + 1);
        const inner = fullMatch.replace(/^\{\d+:(MC|MCV|MULTICHOICE):/, "").slice(0, -1);
        const options = inner.split(/(?<!\\)~/);
        const correct = options.find((opt) => opt.trim().startsWith("=")) || options[0] || "";
        const clean = correct.replace(/^=/, "").trim().replace(/\\~/g, "~");

        result.push(clean);
        index = end + 1;
    }

    return result.join("");
}

function cleanupAnswer(text) {
    if (!text) return "";
    let cleaned = text;
    cleaned = cleaned.replace(/\{TIKTOK:id=[A-Za-z0-9_-]+}/g, "");
    cleaned = cleaned.replace(/\{YOUTUBE:id=[A-Za-z0-9_-]+}/g, "");
    cleaned = cleaned.replace(/\{\d+:NUMERICAL:=(-?[0-9.,]+):[0-9.,]+}/g, "$1");
    cleaned = extractMultipleChoice(cleaned);
    return cleaned;
}

function buildFront(card) {
    const intro = card.einleitung ? `<div class="flashcards-intro">${card.einleitung}</div>` : "";
    if (card.fragen.length === 1) {
        return `${intro}<h3>Frage</h3><p>${card.fragen[0]}</p>`;
    }
    const items = card.fragen.map((frage) => `<li>${frage}</li>`).join("");
    return `${intro}<h3>Fragen</h3><ol>${items}</ol>`;
}

function buildBack(card) {
    const cleanedAnswers = card.antworten.map((antwort) => cleanupAnswer(antwort));
    if (cleanedAnswers.length === 1) {
        return `<h3>Antwort</h3><p>${cleanedAnswers[0]}</p>`;
    }
    const items = cleanedAnswers.map((antwort) => `<li>${antwort}</li>`).join("");
    return `<h3>Antworten</h3><ol>${items}</ol>`;
}

function updateCounts(dueCount, totalCount, nextDueText) {
    const countsEl = document.getElementById("flashcards-counts");
    const messageEl = document.getElementById("flashcards-message");
    if (countsEl) {
        countsEl.textContent = `Fällig: ${dueCount} / Gesamt: ${totalCount}`;
    }
    if (messageEl) {
        messageEl.textContent = nextDueText || "";
    }
}

function formatDueMessage(nextDue) {
    if (!nextDue) return "";
    const now = Date.now();
    const diff = Math.max(nextDue - now, 0);
    const minutes = Math.ceil(diff / 60000);
    if (minutes < 60) {
        return `Naechste Karte in ca. ${minutes} Min.`;
    }
    const hours = Math.round(minutes / 60);
    return `Naechste Karte in ca. ${hours} Std.`;
}

function selectNextCard(cards) {
    const now = Date.now();
    const dueCards = [];
    let nextUpcoming = null;

    cards.forEach((card) => {
        const cardState = getCardState(card.id);
        const due = cardState.due || 0;
        if (due <= now) {
            dueCards.push({ card, due });
        } else if (!nextUpcoming || due < nextUpcoming.due) {
            nextUpcoming = { card, due };
        }
    });

    const selected =
        dueCards.length > 0
            ? dueCards[Math.floor(Math.random() * dueCards.length)].card
            : nextUpcoming?.card || null;
    const message = dueCards.length > 0 ? "" : formatDueMessage(nextUpcoming?.due);

    updateCounts(dueCards.length, cards.length, message);
    return selected;
}

function renderCard(card) {
    const cardEl = document.getElementById("flashcards-card");
    const innerEl = document.getElementById("flashcards-inner");
    const frontEl = document.getElementById("flashcards-front");
    const backEl = document.getElementById("flashcards-back");
    const ratingEl = document.getElementById("flashcards-rating");

    if (!cardEl || !innerEl || !frontEl || !backEl) return;

    state.currentCard = card;
    cardEl.classList.remove("is-flipped");
    cardEl.setAttribute("aria-pressed", "false");
    ratingEl?.classList.remove("is-active");

    const displayCard = card.isInteractive
        ? (() => {
            const tasks = card.tasks || [];
            if (!tasks.length) return card;
            const randomTask = tasks[Math.floor(Math.random() * tasks.length)];
            const frage = randomTask.fragen?.[card.index] ?? "";
            const antwort = randomTask.antworten?.[card.index] ?? "";
            return {
                einleitung: randomTask.einleitung || "",
                fragen: [frage],
                antworten: [antwort],
            };
        })()
        : card;

    frontEl.innerHTML = buildFront(displayCard);
    backEl.innerHTML = buildBack(displayCard);

    const adjustHeight = () => {
        innerEl.style.height = "auto";
        innerEl.style.minHeight = "300px";
        const frontHeight = frontEl.scrollHeight;
        const backHeight = backEl.scrollHeight;
        const maxHeight = Math.max(frontHeight, backHeight, 300);
        innerEl.style.minHeight = `${maxHeight}px`;
        innerEl.style.height = `${maxHeight}px`;
    };

    const bindImageLoad = () => {
        const images = [...frontEl.querySelectorAll("img"), ...backEl.querySelectorAll("img")];
        images.forEach((img) => {
            if (img.complete) return;
            img.addEventListener("load", adjustHeight, { once: true });
        });
    };

    if (typeof MathJax !== "undefined" && MathJax.typesetPromise) {
        MathJax.typesetPromise([frontEl, backEl])
            .then(() => {
                requestAnimationFrame(() => {
                    adjustHeight();
                    bindImageLoad();
                });
            })
            .catch((err) => {
                console.error("MathJax Error:", err);
                adjustHeight();
                bindImageLoad();
            });
    } else {
        adjustHeight();
        bindImageLoad();
    }
}

function flipCard() {
    const cardEl = document.getElementById("flashcards-card");
    const ratingEl = document.getElementById("flashcards-rating");
    if (!cardEl) return;

    cardEl.classList.toggle("is-flipped");
    const flipped = cardEl.classList.contains("is-flipped");
    cardEl.setAttribute("aria-pressed", flipped ? "true" : "false");
    if (ratingEl) {
        ratingEl.classList.toggle("is-active", flipped);
    }
}

function rateCurrentCard(grade) {
    if (!state.currentCard) return;
    const cardId = state.currentCard.id;
    const now = Date.now();
    const stateData = getCardState(cardId);

    let reps = stateData.reps || 0;
    let interval = stateData.interval || 0;
    let ease = stateData.ease || 2.5;

    if (grade < 3) {
        reps = 0;
        interval = 1;
    } else {
        reps += 1;
        if (reps === 1) {
            interval = 1;
        } else if (reps === 2) {
            interval = 6;
        } else {
            interval = Math.round(interval * ease);
        }
    }

    const delta = 0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02);
    ease = Math.max(1.3, ease + delta);

    const due = now + interval * msPerDay;
    setCardState(cardId, { reps, interval, ease, due });

    const next = selectNextCard(state.cards);
    if (next) {
        renderCard(next);
    }
}

function resetProgress() {
    if (!window.confirm("Fortschritt wirklich löschen?")) return;
    localStorage.removeItem(storageKey);
    state.progress = {};
    const next = selectNextCard(state.cards);
    if (next) {
        renderCard(next);
    }
}

function buildCards(entries) {
    const cards = [];
    entries.forEach((entry) => {
        const sammlung = entry._sammlung;
        if (!Array.isArray(sammlung)) return;

        if (entry.Ankityp === "gruppiert") {
            sammlung.forEach((aufgabe, aufgabeIndex) => {
                if (!aufgabe || !Array.isArray(aufgabe.fragen)) return;
                cards.push({
                    id: buildCardId(entry, aufgabeIndex, null),
                    einleitung: aufgabe.einleitung || "",
                    fragen: aufgabe.fragen || [],
                    antworten: aufgabe.antworten || [],
                });
            });
            return;
        }

        if (entry.Typ === "interaktiv") {
            const firstTask = sammlung[0];
            const count = Array.isArray(firstTask?.fragen) ? firstTask.fragen.length : 0;
            for (let index = 0; index < count; index += 1) {
                cards.push({
                    id: buildIndexCardId(entry, index),
                    isInteractive: true,
                    index,
                    tasks: sammlung,
                    fragen: [""],
                    antworten: [""],
                    einleitung: "",
                });
            }
            return;
        }

        sammlung.forEach((aufgabe, aufgabeIndex) => {
            if (!aufgabe || !Array.isArray(aufgabe.fragen)) return;

            if (entry.Ankityp === "einzeln") {
                aufgabe.fragen.forEach((frage, frageIndex) => {
                    const antwort = aufgabe.antworten?.[frageIndex] || "";
                    cards.push({
                        id: buildCardId(entry, aufgabeIndex, frageIndex),
                        einleitung: aufgabe.einleitung || "",
                        fragen: [frage],
                        antworten: [antwort],
                    });
                });
            }
        });
    });

    for (let i = cards.length - 1; i > 0; i -= 1) {
        const j = Math.floor(Math.random() * (i + 1));
        [cards[i], cards[j]] = [cards[j], cards[i]];
    }

    return cards;
}

async function loadData() {
    if (!window.lernbereich) {
        updateCounts(0, 0, "Kein Lernbereich gefunden.");
        return;
    }

    try {
        const response = await fetch("/kompetenzliste.json");
        const allEntries = await response.json();
        const entries = allEntries.filter(
            (eintrag) => eintrag.Lernbereich === window.lernbereich
        );

        for (const entry of entries) {
            const responseSammlung = await fetch(`/json/${entry.Sammlung}.json`);
            entry._sammlung = await responseSammlung.json();
        }

        state.cards = buildCards(entries);
        loadProgress();

        if (!state.cards.length) {
            updateCounts(0, 0, "Keine Flashcards gefunden.");
            return;
        }

        const next = selectNextCard(state.cards);
        if (next) {
            renderCard(next);
        }
    } catch (err) {
        console.error("Flashcards: Fehler beim Laden", err);
        updateCounts(0, 0, "Fehler beim Laden der Flashcards.");
    }
}

function setupEvents() {
    const flipBtn = document.getElementById("flashcards-flip");
    const cardEl = document.getElementById("flashcards-card");
    const resetBtn = document.getElementById("flashcards-reset");

    flipBtn?.addEventListener("click", flipCard);
    cardEl?.addEventListener("click", flipCard);
    resetBtn?.addEventListener("click", resetProgress);

    document.querySelectorAll(".flashcards-rate").forEach((button) => {
        button.addEventListener("click", (event) => {
            const grade = Number(event.currentTarget.dataset.grade || 0);
            if (!grade) return;
            rateCurrentCard(grade);
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setupEvents();
    loadData();
});
