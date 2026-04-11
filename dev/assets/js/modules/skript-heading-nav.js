import { getChecksByLernbereich } from "../data/checks-repo.js";

const skriptHeadingNavCleanup = new WeakMap();

function ensureSkriptContentContainer(root) {
    const existingContainer = root.querySelector(":scope > .mod-script-content");
    if (existingContainer) return existingContainer;

    const container = document.createElement("div");
    container.className = "mod-script-content";

    const movableNodes = Array.from(root.children).filter((node) => {
        return !node.classList.contains("check-jump-nav-wrap");
    });

    movableNodes.forEach((node) => {
        container.appendChild(node);
    });

    root.appendChild(container);
    return container;
}

function setActiveTab(navNode, targetId) {
    const tabs = Array.from(navNode.querySelectorAll(".check-jump-tab"));
    let matched = false;

    tabs.forEach((tab) => {
        const isActive = tab.dataset.targetId === targetId;
        tab.classList.toggle("active", isActive);
        if (isActive) matched = true;
    });

    if (!matched && tabs[0]) {
        tabs[0].classList.add("active");
    }
}

function renderCheckTabs(navNode, checkAnkers, checkMap) {
    navNode.innerHTML = checkAnkers
        .map((anker) => {
            const nummer = anker.dataset.nummer;
            const check = checkMap.get(nummer);
            const label = check
                ? `${check.Nummer}. ${check.Schlagwort || "Check"}`
                : `${nummer}. Check`;
            const id = anker.id;
            return `<a class="check-jump-tab" href="#${id}" data-target-id="${id}">${label}</a>`;
        })
        .join("");

    if (navNode.dataset.boundClick === "1") return;
    navNode.dataset.boundClick = "1";

    navNode.addEventListener("click", (event) => {
        const tab = event.target.closest(".check-jump-tab");
        if (!tab) return;
        event.preventDefault();
        const targetId = tab.dataset.targetId || "";
        setActiveTab(navNode, targetId);
        const target = document.getElementById(targetId);
        if (target) {
            const scrollContainer = document.querySelector(".mod-main");
            const navWrap = navNode.closest(".check-jump-nav-wrap");
            const modTabNav = document.querySelector(".mod-tab-nav");
            const navWrapH = navWrap ? navWrap.offsetHeight : 0;
            const tabNavH = modTabNav ? modTabNav.offsetHeight : 0;
            const offset = tabNavH + navWrapH + 12;
            if (scrollContainer) {
                const containerRect = scrollContainer.getBoundingClientRect();
                const targetRect = target.getBoundingClientRect();
                const y = scrollContainer.scrollTop + (targetRect.top - containerRect.top) - offset;
                scrollContainer.scrollTo({ top: y, behavior: "smooth" });
            } else {
                const y = target.getBoundingClientRect().top + window.pageYOffset - offset;
                window.scrollTo({ top: y, behavior: "smooth" });
            }
        }
    });
}

function bindScrollSync(navNode, anchorNodes) {
    const existingCleanup = skriptHeadingNavCleanup.get(navNode);
    if (typeof existingCleanup === "function") {
        existingCleanup();
        skriptHeadingNavCleanup.delete(navNode);
    }

    const nodes = Array.from(anchorNodes || []).filter((node) => node?.id);
    if (nodes.length === 0) return;

    const updateActiveFromScroll = () => {
        const offsetTop = 230;
        let passedNode = null;
        let upcomingNode = null;
        let upcomingDistance = Number.POSITIVE_INFINITY;

        nodes.forEach((node) => {
            const top = node.getBoundingClientRect().top;
            const distance = top - offsetTop;

            if (distance <= 0) {
                passedNode = node;
                return;
            }

            if (distance < upcomingDistance) {
                upcomingDistance = distance;
                upcomingNode = node;
            }
        });

        const activeNode = passedNode || upcomingNode || nodes[0];
        setActiveTab(navNode, activeNode?.id || "");
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

export async function initSkriptHeadingNav({ root, lernbereich }) {
    if (!root) return;

    const existingWrap = root.querySelector("#dev-skript-h2-jump-nav")?.closest(".check-jump-nav-wrap");
    if (existingWrap) existingWrap.remove();

    const contentContainer = ensureSkriptContentContainer(root);
    const checkAnkers = Array.from(contentContainer.querySelectorAll(".check-anker[data-nummer]"));

    if (checkAnkers.length < 2) return;

    const checkMap = new Map();
    if (lernbereich) {
        const checks = await getChecksByLernbereich(lernbereich);
        for (const check of checks) {
            checkMap.set(String(Number(check.Nummer)), check);
        }
    }

    const wrap = document.createElement("div");
    wrap.className = "check-jump-nav-wrap check-jump-nav-wrap--skript-h2";

    const nav = document.createElement("nav");
    nav.id = "dev-skript-h2-jump-nav";
    nav.className = "check-jump-nav check-jump-nav--skript-h2";
    nav.setAttribute("aria-label", "Check-Navigation");

    wrap.appendChild(nav);
    root.insertAdjacentElement("afterbegin", wrap);

    renderCheckTabs(nav, checkAnkers, checkMap);
    bindScrollSync(nav, checkAnkers);

    const hash = window.location.hash;
    if (hash.startsWith("#")) {
        const targetId = decodeURIComponent(hash.slice(1));
        const hashTarget = checkAnkers.find((a) => a.id === targetId);
        if (hashTarget) {
            setActiveTab(nav, hashTarget.id);
            return;
        }
    }

    setActiveTab(nav, checkAnkers[0].id);
}
