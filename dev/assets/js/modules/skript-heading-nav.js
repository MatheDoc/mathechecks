const skriptHeadingNavCleanup = new WeakMap();

function slugifyHeading(text) {
    return String(text || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, "")
        .trim()
        .replace(/\s+/g, "-")
        .replace(/-+/g, "-");
}

function ensureHeadingIds(headings) {
    const usedIds = new Set(
        Array.from(document.querySelectorAll("[id]"))
            .map((node) => String(node.id || "").trim())
            .filter(Boolean)
    );

    headings.forEach((heading, index) => {
        const existing = String(heading.id || "").trim();
        if (existing) {
            usedIds.add(existing);
            return;
        }

        const base = slugifyHeading(heading.textContent) || `skript-h2-${index + 1}`;
        let candidate = base;
        let suffix = 2;
        while (usedIds.has(candidate)) {
            candidate = `${base}-${suffix}`;
            suffix += 1;
        }

        heading.id = candidate;
        usedIds.add(candidate);
    });
}

function setActiveTab(navNode, headingId) {
    const tabs = Array.from(navNode.querySelectorAll(".check-jump-tab"));
    let matched = false;

    tabs.forEach((tab) => {
        const isActive = tab.dataset.targetId === headingId;
        tab.classList.toggle("active", isActive);
        if (isActive) matched = true;
    });

    if (!matched && tabs[0]) {
        tabs[0].classList.add("active");
    }
}

function renderHeadingTabs(navNode, headings) {
    navNode.innerHTML = headings
        .map((heading, index) => {
            const id = heading.id;
            const label = String(heading.textContent || "").trim() || `Abschnitt ${index + 1}`;
            return `<a class="check-jump-tab" href="#${id}" data-target-id="${id}">${label}</a>`;
        })
        .join("");

    if (navNode.dataset.boundClick === "1") return;
    navNode.dataset.boundClick = "1";

    navNode.addEventListener("click", (event) => {
        const tab = event.target.closest(".check-jump-tab");
        if (!tab) return;
        setActiveTab(navNode, tab.dataset.targetId || "");
    });
}

function bindHeadingScrollSync(navNode, headings) {
    const existingCleanup = skriptHeadingNavCleanup.get(navNode);
    if (typeof existingCleanup === "function") {
        existingCleanup();
        skriptHeadingNavCleanup.delete(navNode);
    }

    const headingNodes = Array.from(headings || []).filter((node) => node?.id);
    if (headingNodes.length === 0) return;

    const updateActiveFromScroll = () => {
        const offsetTop = 230;
        let passedHeading = null;
        let upcomingHeading = null;
        let upcomingDistance = Number.POSITIVE_INFINITY;

        headingNodes.forEach((heading) => {
            const top = heading.getBoundingClientRect().top;
            const distance = top - offsetTop;

            if (distance <= 0) {
                passedHeading = heading;
                return;
            }

            if (distance < upcomingDistance) {
                upcomingDistance = distance;
                upcomingHeading = heading;
            }
        });

        const activeHeading = passedHeading || upcomingHeading || headingNodes[0];
        setActiveTab(navNode, activeHeading?.id || "");
    };

    let ticking = false;
    const scrollContainer = document.querySelector(".mod-main");
    const scrollSource = scrollContainer || window;
    const onViewportChange = () => {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(() => {
            ticking = false;
            updateActiveFromScroll();
        });
    };

    scrollSource.addEventListener("scroll", onViewportChange, { passive: true });
    window.addEventListener("resize", onViewportChange);
    updateActiveFromScroll();

    skriptHeadingNavCleanup.set(navNode, () => {
        scrollSource.removeEventListener("scroll", onViewportChange);
        window.removeEventListener("resize", onViewportChange);
    });
}

export function initSkriptHeadingNav({ root }) {
    if (!root) return;

    const headings = Array.from(root.querySelectorAll("h2"));
    const existingWrap = root.querySelector("#dev-skript-h2-jump-nav")?.closest(".check-jump-nav-wrap");
    if (existingWrap) existingWrap.remove();

    if (headings.length < 2) return;

    ensureHeadingIds(headings);

    const wrap = document.createElement("div");
    wrap.className = "check-jump-nav-wrap check-jump-nav-wrap--skript-h2";

    const nav = document.createElement("nav");
    nav.id = "dev-skript-h2-jump-nav";
    nav.className = "check-jump-nav check-jump-nav--skript-h2";
    nav.setAttribute("aria-label", "Kapitel-Navigation");

    wrap.appendChild(nav);
    root.insertAdjacentElement("afterbegin", wrap);

    renderHeadingTabs(nav, headings);
    bindHeadingScrollSync(nav, headings);

    const hash = window.location.hash;
    if (hash.startsWith("#")) {
        const targetId = decodeURIComponent(hash.slice(1));
        const hashTarget = headings.find((heading) => heading.id === targetId);
        if (hashTarget) {
            setActiveTab(nav, hashTarget.id);
            return;
        }
    }

    setActiveTab(nav, headings[0].id);
}
