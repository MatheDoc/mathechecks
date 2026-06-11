import { initTrainingModule } from "./modules/training.js?v=20260611-pwa-mod-scroll";
import { initRecallModule } from "./modules/recall.js?v=20260611-pwa-mod-scroll";
import { initFeynmanModule } from "./modules/feynman.js?v=20260611-pwa-mod-scroll";
import { initFlashcardsModule } from "./modules/flashcards.js?v=20260609-complete-icon";
import { initScriptTaskDuplicatesModule } from "./modules/script-task-duplicates.js?v=20260610-script-duplicate-complete";
import { initCheckAnker } from "./modules/check-anker.js?v=20260523-checks-url-fix";
import { initSkriptHeadingNav } from "./modules/skript-heading-nav.js?v=20260523-checks-url-fix";
import { initSkriptVisuals, refreshSkriptTables } from "./modules/skript-visuals.js";
import { initStartModule } from "./modules/start.js?v=20260609-complete-icon";
import { initWarmupModule } from "./modules/warmup.js";
import { initKompetenzlisteModule } from "./modules/kompetenzliste.js?v=20260609-complete-icon";
import { getChecksByLernbereich } from "./data/checks-repo.js?v=20260523-checks-url-fix";
import { confirmFeedActivityAbort, initFeedActivityGuard } from "./modules/ui/feed-activity-guard.js?v=20260516-feed-dialog-polish";

const SCROLL_STORAGE_PREFIX = "mathechecks.scrollPositions.v2";
const TAB_SCOPE_SESSION_KEY = "mathechecks.tabScope.v1";
let suppressScrollSaveUntil = 0;
let userScrolledSinceBootstrap = false;
let userInteractedSinceBootstrap = false;
let userInteractionTrackingBound = false;
const USER_SCROLL_KEYS = new Set(["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End", " "]);

function bindUserInteractionTracking() {
  if (userInteractionTrackingBound) return;
  userInteractionTrackingBound = true;

  const markUserInteraction = (event) => {
    if (event?.type === "keydown") {
      const key = String(event.key || "");
      if (!USER_SCROLL_KEYS.has(key)) {
        return;
      }
    }
    userInteractedSinceBootstrap = true;
  };

  window.addEventListener("wheel", markUserInteraction, { passive: true, capture: true });
  window.addEventListener("touchstart", markUserInteraction, { passive: true, capture: true });
  window.addEventListener("pointerdown", markUserInteraction, { passive: true, capture: true });
  window.addEventListener("keydown", markUserInteraction, { capture: true });
}

function getTabScopeId() {
  try {
    let scope = window.sessionStorage.getItem(TAB_SCOPE_SESSION_KEY);
    if (!scope) {
      const randomPart = Math.random().toString(36).slice(2, 10);
      scope = `tab-${Date.now().toString(36)}-${randomPart}`;
      window.sessionStorage.setItem(TAB_SCOPE_SESSION_KEY, scope);
    }
    return scope;
  } catch {
    return "tab-fallback";
  }
}

const SCROLL_STORAGE_KEY = `${SCROLL_STORAGE_PREFIX}::${getTabScopeId()}`;

async function typesetMath(targetNode = document.body, retries = 8) {
  if (!targetNode) return;

  const mathJax = window.MathJax;
  if (mathJax && typeof mathJax.typesetPromise === "function") {
    try {
      await mathJax.typesetPromise([targetNode]);
      return;
    } catch {
      // Keep page usable even if one formula fails to parse.
      return;
    }
  }

  if (retries <= 0) return;
  await new Promise((resolve) => setTimeout(resolve, 150));
  await typesetMath(targetNode, retries - 1);
}

function getPageContext() {
  const body = document.body;
  const params = new URLSearchParams(window.location.search);
  const checkIdFromQuery = params.get("check_id") || "";
  const isFeedContext = params.get("feed") === "1";
  return {
    lernbereich: body?.dataset?.lernbereich || "",
    moduleKey: body?.dataset?.moduleKey || "",
    checkId: checkIdFromQuery || body?.dataset?.checkId || "",
    activityContext: isFeedContext
      ? {
        mode: "feed",
        activityKey: params.get("activity_key") || "",
        activityStep: params.get("activity_step") || "",
        activityRun: params.get("activity_run") || "",
      }
      : null,
  };
}

function setNoteCardExpanded(noteNode, expanded) {
  if (!noteNode) return;

  const toggleButton = noteNode.querySelector(".mc-note__toggle");
  const contentNode = noteNode.querySelector(".mc-note__content");
  const isExpanded = Boolean(expanded);

  noteNode.dataset.noteOpen = isExpanded ? "true" : "false";
  if (toggleButton) {
    toggleButton.setAttribute("aria-expanded", isExpanded ? "true" : "false");
  }
  if (contentNode) {
    contentNode.hidden = !isExpanded;
  }
}

async function initSkriptInfoCards(root, lernbereich = "") {
  if (!root) return;

  const titleByKey = new Map();
  if (lernbereich) {
    try {
      const checks = await getChecksByLernbereich(lernbereich);
      checks.forEach((check) => {
        const title = String(check?.Schlagwort || "").trim();
        if (!title) return;

        const checkId = String(check?.check_id || "").trim().toLowerCase();
        const nummer = Number.isFinite(Number(check?.Nummer)) ? String(Number(check.Nummer)) : "";
        const nummerPadded = nummer ? nummer.padStart(2, "0") : "";

        if (checkId) titleByKey.set(checkId, title);
        if (nummer) titleByKey.set(nummer, title);
        if (nummerPadded) titleByKey.set(nummerPadded, title);
      });
    } catch {
      // Keep existing note title if check metadata cannot be loaded.
    }
  }

  const noteNodes = Array.from(root.querySelectorAll(".mc-note"));
  noteNodes.forEach((noteNode) => {
    const toggleButton = noteNode.querySelector(".mc-note__toggle");
    const contentNode = noteNode.querySelector(".mc-note__content");
    const titleNode = noteNode.querySelector(".mc-note__title");
    if (!toggleButton || !contentNode) return;

    if (titleNode && titleNode.dataset.normalized !== "true") {
      const keyCandidates = [
        String(noteNode.dataset?.check || "").trim().toLowerCase(),
        String(noteNode.dataset?.key || "").trim().toLowerCase(),
        String(noteNode.id || "").replace(/^check-/, "").trim().toLowerCase(),
      ].filter(Boolean);

      const mappedTitle = keyCandidates
        .map((key) => titleByKey.get(key) || "")
        .find((value) => String(value).trim());

      const cleanTitle = String(mappedTitle || titleNode.textContent || "")
        .replace(/\s*:\s*$/, "")
        .replace(/\s+/g, " ")
        .trim();

      if (cleanTitle) {
        titleNode.textContent = cleanTitle;
      }
      titleNode.dataset.normalized = "true";
    }

    if (noteNode.dataset.noteBound !== "true") {
      noteNode.dataset.noteBound = "true";
      toggleButton.addEventListener("click", () => {
        const isOpen = noteNode.dataset.noteOpen === "true";
        setNoteCardExpanded(noteNode, !isOpen);
      });
    }

    setNoteCardExpanded(noteNode, noteNode.dataset.noteOpen === "true");
  });
}

function openNoteCardIfPresent(target) {
  if (!target) return;

  const noteNode =
    target.matches?.(".mc-note")
      ? target
      : target.querySelector?.(".mc-note") || target.closest?.(".mc-note");
  if (noteNode) {
    setNoteCardExpanded(noteNode, true);
    return;
  }

  const details =
    target.matches?.("details")
      ? target
      : target.querySelector?.("details.mc-note__card") || target.closest?.("details.mc-note__card");
  if (details && details.tagName === "DETAILS") {
    details.open = true;
  }
}

function resolveScrollTargetId(context) {
  const hash = window.location.hash || "";
  if (hash.startsWith("#")) {
    return decodeURIComponent(hash.slice(1));
  }
  return "";
}

function clearLocationHash() {
  try {
    const url = new URL(window.location.href);
    url.hash = "";
    window.history.replaceState(null, "", `${url.pathname}${url.search}`);
  } catch {
    // Ignore malformed URL edge cases and keep the page usable.
  }
}

function resetDeferredSkriptHashScroll() {
  const moduleScroller = document.querySelector(".mod-main");
  if (moduleScroller) {
    moduleScroller.scrollTop = 0;
  }
  window.scrollTo({ top: 0, left: 0, behavior: "auto" });
}

function getScrollPageKey() {
  try {
    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);

    // Keep scroll memory stable across transient navigation parameters.
    params.delete("check_id");
    params.delete("feed");
    params.delete("activity_key");
    params.delete("activity_step");

    const search = params.toString();
    return `${url.pathname}${search ? `?${search}` : ""}`;
  } catch {
    return window.location.pathname || "";
  }
}

function readStoredScrollPositions() {
  try {
    const raw = window.localStorage.getItem(SCROLL_STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function writeStoredScrollPositions(positions) {
  try {
    window.localStorage.setItem(SCROLL_STORAGE_KEY, JSON.stringify(positions));
  } catch {
    // Ignore quota/storage errors, app should stay usable.
  }
}

function shouldSuppressScrollSave() {
  return Date.now() < suppressScrollSaveUntil;
}

function suppressScrollSaveFor(ms = 500) {
  suppressScrollSaveUntil = Date.now() + Math.max(0, Number(ms) || 0);
}

function getPreferredScrollBehavior() {
  if (window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches) {
    return "auto";
  }
  return "smooth";
}

function getScrollHost() {
  const moduleScroller = document.querySelector(".mod-main");
  if (moduleScroller && document.body?.classList?.contains("page-module")) {
    return moduleScroller;
  }
  return window;
}

function readCurrentScrollTop() {
  const host = getScrollHost();
  if (host === window) {
    return Math.max(0, Math.round(window.scrollY || window.pageYOffset || 0));
  }
  return Math.max(0, Math.round(host.scrollTop || 0));
}

function applyScrollTop(y) {
  const safeY = Math.max(0, Math.round(Number(y) || 0));
  const host = getScrollHost();
  if (host === window) {
    window.scrollTo({ top: safeY, left: 0, behavior: "auto" });
    return;
  }
  host.scrollTop = safeY;
}

function saveScrollPosition(pageKey) {
  if (!pageKey) return;
  if (shouldSuppressScrollSave()) return;
  const positions = readStoredScrollPositions();
  positions[pageKey] = readCurrentScrollTop();
  writeStoredScrollPositions(positions);
}

function restoreScrollPosition(pageKey) {
  if (!pageKey) return false;
  const positions = readStoredScrollPositions();
  const y = Number(positions[pageKey]);
  if (!Number.isFinite(y) || y < 0) return false;
  suppressScrollSaveFor(700);
  applyScrollTop(y);
  return true;
}

function bindScrollPersistence(pageKey) {
  if (!pageKey) return;

  let scheduled = false;
  let hasUserScrolled = false;

  const onScroll = (event) => {
    if (shouldSuppressScrollSave()) return;

    // Ignore programmatic scroll updates (restore/smooth scroll) to avoid drift.
    if (event && event.isTrusted === false) return;
    userScrolledSinceBootstrap = true;
    hasUserScrolled = true;

    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(() => {
      scheduled = false;
      saveScrollPosition(pageKey);
    });
  };

  const scrollHost = getScrollHost();
  window.addEventListener("scroll", onScroll, { passive: true });
  if (scrollHost !== window) {
    scrollHost.addEventListener("scroll", onScroll, { passive: true });
  }
  window.addEventListener("pagehide", () => {
    if (hasUserScrolled && !shouldSuppressScrollSave()) saveScrollPosition(pageKey);
  });
  window.addEventListener("beforeunload", () => {
    if (hasUserScrolled && !shouldSuppressScrollSave()) saveScrollPosition(pageKey);
  });
}

function scheduleStabilizedRestore(pageKey, explicitTargetId, skipRestore = false) {
  if (explicitTargetId || skipRestore) return;
  if (!pageKey) return;

  const passesMs = [120, 320, 700, 1200];
  passesMs.forEach((delay) => {
    window.setTimeout(() => {
      // Never fight with the user once they started scrolling manually.
      if (userInteractedSinceBootstrap) return;
      restoreScrollPosition(pageKey);
    }, delay);
  });

  window.addEventListener("load", () => {
    if (userInteractedSinceBootstrap) return;
    restoreScrollPosition(pageKey);
  }, { once: true });
}

function scrollToTargetId(targetId, retries = 8) {
  if (!targetId) return;

  const target = document.getElementById(targetId);
  if (target) {
    openNoteCardIfPresent(target);
    requestAnimationFrame(() => {
      suppressScrollSaveFor(900);
      target.scrollIntoView({ behavior: getPreferredScrollBehavior(), block: "start", inline: "nearest" });
      if (window.location.hash !== `#${targetId}`) {
        window.history.replaceState(null, "", `#${targetId}`);
      }
    });
    return;
  }

  if (retries <= 0) return;
  setTimeout(() => scrollToTargetId(targetId, retries - 1), 120);
}

function scrollToSkriptTargetId(targetId, retries = 8, behavior = "auto") {
  if (!targetId) return;

  const target = document.getElementById(targetId);
  if (target) {
    openNoteCardIfPresent(target);
    requestAnimationFrame(() => {
      suppressScrollSaveFor(900);

      const scrollContainer = document.querySelector(".mod-main");
      const navWrap = document
        .querySelector("#skript-h2-jump-nav")
        ?.closest(".check-jump-nav-wrap");
      const modTabNav = document.querySelector(".mod-tab-nav");
      const navWrapH = navWrap ? navWrap.offsetHeight : 0;
      const tabNavH = modTabNav ? modTabNav.offsetHeight : 0;
      const offset = tabNavH + navWrapH + 12;

      if (scrollContainer) {
        const containerRect = scrollContainer.getBoundingClientRect();
        const targetRect = target.getBoundingClientRect();
        const y = scrollContainer.scrollTop + (targetRect.top - containerRect.top) - offset;
        scrollContainer.scrollTo({ top: y, behavior });
      } else {
        const y = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top: y, behavior });
      }

      if (window.location.hash !== `#${targetId}`) {
        window.history.replaceState(null, "", `#${targetId}`);
      }
    });
    return;
  }

  if (retries <= 0) return;
  setTimeout(() => scrollToSkriptTargetId(targetId, retries - 1, behavior), 120);
}

function scheduleSkriptTargetAlignment(targetId) {
  if (!targetId) return;

  const passesMs = [160, 420, 860, 1300];
  passesMs.forEach((delay) => {
    window.setTimeout(() => {
      if (userInteractedSinceBootstrap) return;
      scrollToSkriptTargetId(targetId, 0, "auto");
    }, delay);
  });

  window.addEventListener("load", () => {
    if (userInteractedSinceBootstrap) return;
    scrollToSkriptTargetId(targetId, 0, "auto");
  }, { once: true });
}

function setManualScrollRestoration() {
  try {
    if ("scrollRestoration" in window.history) {
      window.history.scrollRestoration = "manual";
    }
  } catch {
    // Ignore if browser does not allow changing scroll restoration.
  }
}

function bindLernbereichSwitchNavigation() {
  const switches = Array.from(document.querySelectorAll("select.lb-switch[data-lb-nav='true']"));
  if (!switches.length) return;

  switches.forEach((selectNode) => {
    if (selectNode.dataset.boundNav === "true") return;
    selectNode.dataset.boundNav = "true";

    selectNode.addEventListener("change", (event) => {
      const value = String(event?.target?.value || "").trim();
      if (!value) return;
      if (value === window.location.pathname) return;
      if (!confirmFeedActivityAbort()) {
        selectNode.value = window.location.pathname;
        return;
      }
      window.location.assign(value);
    });
  });
}

function bindLernbereichSwitchTheme() {
  const switches = Array.from(document.querySelectorAll("select.lb-switch[data-lb-nav='true']"));
  if (!switches.length) return;

  const applyGebiet = (selectNode) => {
    const selected = selectNode.selectedOptions?.[0] || null;
    const gebiet = String(selected?.dataset?.gebiet || "").trim().toLowerCase();
    selectNode.dataset.gebiet = gebiet;
  };

  switches.forEach((selectNode) => {
    applyGebiet(selectNode);
    if (selectNode.dataset.boundTheme === "true") return;
    selectNode.dataset.boundTheme = "true";
    selectNode.addEventListener("change", () => applyGebiet(selectNode));
  });
}

async function bootstrap() {
  setManualScrollRestoration();
  bindLernbereichSwitchTheme();
  bindLernbereichSwitchNavigation();
  bindUserInteractionTracking();
  userScrolledSinceBootstrap = false;
  userInteractedSinceBootstrap = false;

  const context = getPageContext();
  initFeedActivityGuard(context.activityContext);
  const pageKey = getScrollPageKey();
  const explicitTargetId = resolveScrollTargetId(context);
  const isFeedContext = context.activityContext?.mode === "feed";
  const shouldRestoreRememberedScroll = !explicitTargetId && !isFeedContext;
  const contentRoot = document.querySelector(".mod-content") || document.body;
  const shouldDeferNativeSkriptHash = context.moduleKey === "skript" && Boolean(explicitTargetId);
  let handledSkriptTargetEarly = false;
  let scriptContentRoot = null;

  if (shouldDeferNativeSkriptHash) {
    suppressScrollSaveFor(1200);
    clearLocationHash();
    resetDeferredSkriptHashScroll();
  }

  bindScrollPersistence(pageKey);

  // Pre-restore to reduce visual jump from top to remembered position.
  if (shouldRestoreRememberedScroll) {
    restoreScrollPosition(pageKey);
  }

  scheduleStabilizedRestore(pageKey, explicitTargetId, isFeedContext);

  if (context.moduleKey === "training") {
    const root = document.getElementById("training-root");
    if (!root) return;
    await initTrainingModule({
      root,
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
      activityContext: context.activityContext,
      usePersistedState: true,
    });
    await typesetMath(root);
    if (explicitTargetId) {
      scrollToTargetId(explicitTargetId);
    } else if (shouldRestoreRememberedScroll) {
      // Post-restore after rendering to counter layout shifts.
      restoreScrollPosition(pageKey);
    }
    return;
  }

  if (context.moduleKey === "start") {
    await initStartModule({
      lernbereich: context.lernbereich,
      activityContext: context.activityContext,
    });
    return;
  }

  if (context.moduleKey === "warmup") {
    await initWarmupModule({
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
    });
    return;
  }

  if (context.moduleKey === "kompetenzliste") {
    const root = document.getElementById("kompetenzliste-root");
    await initKompetenzlisteModule({
      root,
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
      activityContext: context.activityContext,
    });
    if (root) await typesetMath(root);
    return;
  }

  if (context.moduleKey === "recall") {
    const root = document.getElementById("recall-root");
    if (!root) return;
    await initRecallModule({
      root,
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
      activityContext: context.activityContext,
    });
    await typesetMath(root);
    if (explicitTargetId) {
      scrollToTargetId(explicitTargetId);
    } else if (shouldRestoreRememberedScroll) {
      restoreScrollPosition(pageKey);
    }
    return;
  }

  if (context.moduleKey === "feynman") {
    const root = document.getElementById("feynman-root");
    if (!root) return;
    await initFeynmanModule({
      root,
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
      activityContext: context.activityContext,
    });
    await typesetMath(root);
    if (explicitTargetId) {
      scrollToTargetId(explicitTargetId);
    } else if (shouldRestoreRememberedScroll) {
      restoreScrollPosition(pageKey);
    }
    return;
  }

  if (context.moduleKey === "flashcards") {
    const root = document.getElementById("flashcards-root");
    if (!root) return;
    await initFlashcardsModule({
      root,
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
      activityContext: context.activityContext,
    });
    await typesetMath(root);
    if (explicitTargetId) {
      scrollToTargetId(explicitTargetId);
    } else if (shouldRestoreRememberedScroll) {
      restoreScrollPosition(pageKey);
    }
    return;
  }

  // Static pages such as skript rely on markdown content already in the DOM.
  if (context.moduleKey === "skript") {
    await initSkriptHeadingNav({
      root: contentRoot,
      lernbereich: context.lernbereich,
    });
    scriptContentRoot = contentRoot.querySelector(":scope > .mod-script-content") || contentRoot;

    if (explicitTargetId) {
      scrollToSkriptTargetId(explicitTargetId, 2, "auto");
      scheduleSkriptTargetAlignment(explicitTargetId);
      handledSkriptTargetEarly = true;
    }

    initSkriptVisuals(scriptContentRoot);
    await Promise.all([
      initSkriptInfoCards(scriptContentRoot, context.lernbereich),
      initCheckAnker({ root: scriptContentRoot, lernbereich: context.lernbereich }),
      initScriptTaskDuplicatesModule({
        root: scriptContentRoot,
        lernbereich: context.lernbereich,
        usePersistedState: true,
        activityContext: context.activityContext,
        preferredCheckId: context.checkId,
      }),
    ]);
  }

  await typesetMath(contentRoot);

  if (context.moduleKey === "skript" && scriptContentRoot) {
    refreshSkriptTables(scriptContentRoot);
  }

  if (explicitTargetId) {
    if (context.moduleKey === "skript") {
      if (!handledSkriptTargetEarly) {
        scrollToSkriptTargetId(explicitTargetId, 10, "auto");
        scheduleSkriptTargetAlignment(explicitTargetId);
      }
    } else {
      scrollToTargetId(explicitTargetId);
    }
  } else if (shouldRestoreRememberedScroll) {
    restoreScrollPosition(pageKey);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootstrap);
} else {
  bootstrap();
}
