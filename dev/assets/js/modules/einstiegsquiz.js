/**
 * Einstieg module – interactive curiosity cards.
 */
export async function initEinstiegsquizModule({ lernbereich } = {}) {
    const wrap = document.querySelector(".ei-wrap");
    if (!wrap) return;

    const cards = [...wrap.querySelectorAll(".ei-card")];
    const dots = [...wrap.querySelectorAll(".ei-dot")];
    let current = 0;

    /* ── Reveal buttons (wusstest-du, alltag) ─────────────── */
    for (const btn of wrap.querySelectorAll(".ei-reveal-btn")) {
        btn.addEventListener("click", () => {
            const card = btn.closest(".ei-card");
            card.querySelector(".ei-detail").hidden = false;
            btn.hidden = true;
            enableNext(card);
        });
    }

    /* ── Option buttons (schaetzfrage, vorwissen) ─────────── */
    for (const group of wrap.querySelectorAll(".ei-options")) {
        const korrekt = parseInt(group.dataset.korrekt, 10);
        const opts = [...group.querySelectorAll(".ei-opt")];
        let answered = false;

        for (const opt of opts) {
            opt.addEventListener("click", () => {
                if (answered) return;
                answered = true;

                const idx = parseInt(opt.dataset.idx, 10);
                const card = group.closest(".ei-card");
                const typ = card.dataset.typ;

                opts[korrekt].classList.add("ei-opt--correct");
                if (idx !== korrekt) opt.classList.add("ei-opt--selected");
                for (const o of opts) o.disabled = true;

                if (typ === "vorwissen") {
                    const key = idx === korrekt ? ".ei-fb--richtig" : ".ei-fb--falsch";
                    card.querySelector(key).hidden = false;
                } else {
                    card.querySelector(".ei-feedback").hidden = false;
                }

                enableNext(card);
            });
        }
    }

    /* ── Navigation ───────────────────────────────────────── */
    for (const btn of wrap.querySelectorAll(".ei-btn-next")) {
        btn.addEventListener("click", () => goTo(current + 1));
    }

    function enableNext(card) {
        const btn = card.querySelector(".ei-btn-next");
        if (btn) btn.disabled = false;
    }

    function goTo(idx) {
        if (idx >= cards.length) return;
        cards[current].hidden = true;
        if (dots[current]) {
            dots[current].classList.remove("active");
            dots[current].classList.add("done");
        }
        current = idx;
        cards[current].hidden = false;
        if (dots[current]) {
            dots[current].classList.add("active");
        }
    }
}
