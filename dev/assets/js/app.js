import { initTrainingModule } from "./modules/training.js";
import { initBlurtingModule } from "./modules/blurting.js";
import { initFeynmanModule } from "./modules/feynman.js";
import { initFlashcardsModule } from "./modules/flashcards.js";
import { initScriptTaskDuplicatesModule } from "./modules/script-task-duplicates.js";
import { initCheckAnker } from "./modules/check-anker.js";
import { initSkriptHeadingNav } from "./modules/skript-heading-nav.js";
import { initStartModule } from "./modules/start.js";
import { initEinstiegsquizModule } from "./modules/einstiegsquiz.js";
import { initKompetenzlisteModule } from "./modules/kompetenzliste.js";
import { getChecksByLernbereich } from "./data/checks-repo.js";

const SCROLL_STORAGE_PREFIX = "mathechecks.dev.scrollPositions.v2";
const TAB_SCOPE_SESSION_KEY = "mathechecks.dev.tabScope.v1";
const SESSION_NAV_STATE_KEY = "mathechecks.dev.lastModuleContext.v1";
let suppressScrollSaveUntil = 0;
let userScrolledSinceBootstrap = false;

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
  return {
    lernbereich: body?.dataset?.lernbereich || "",
    moduleKey: body?.dataset?.moduleKey || "",
    checkId: checkIdFromQuery || body?.dataset?.checkId || "",
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

function getScrollPageKey() {
  try {
    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);

    // Keep scroll memory stable across transient navigation parameters.
    params.delete("check_id");

    const search = params.toString();
    return `${url.pathname}${search ? `?${search}` : ""}`;
  } catch {
    return window.location.pathname || "";
  }
}

function isDevLernbereichPath(pathname) {
  return /^\/dev\/lernbereiche\/[^/]+\/[^/]+\//.test(String(pathname || ""));
}

function readSessionModuleContext() {
  try {
    const raw = window.sessionStorage.getItem(SESSION_NAV_STATE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeSessionModuleContext(context) {
  try {
    const payload = {
      lernbereich: context?.lernbereich || "",
      pathname: window.location?.pathname || "",
      isDevLernbereichPage: isDevLernbereichPath(window.location?.pathname || ""),
      ts: Date.now(),
    };
    window.sessionStorage.setItem(SESSION_NAV_STATE_KEY, JSON.stringify(payload));
  } catch {
    // Session storage can fail in strict privacy modes.
  }
}

function parseReferrerContext() {
  try {
    if (!document.referrer) return null;
    const refUrl = new URL(document.referrer);
    if (refUrl.origin !== window.location.origin) return null;

    const parts = refUrl.pathname.split("/").filter(Boolean);
    const isDevLernbereichPage =
      parts[0] === "dev" && parts[1] === "lernbereiche" && typeof parts[3] === "string";

    return {
      isDevLernbereichPage,
      lernbereich: isDevLernbereichPage ? parts[3] : "",
      pathname: refUrl.pathname,
    };
  } catch {
    return null;
  }
}

function shouldHydrateLocalState(context) {
  const currentPath = window.location?.pathname || "";
  const isCurrentDevLernbereichPage = isDevLernbereichPath(currentPath);
  if (!isCurrentDevLernbereichPage) {
    return true;
  }

  const currentLernbereich = String(context?.lernbereich || "").trim();
  if (!currentLernbereich) {
    return false;
  }

  const ref = parseReferrerContext();
  if (ref?.isDevLernbereichPage && ref.lernbereich === currentLernbereich) {
    return true;
  }

  const previous = readSessionModuleContext();
  if (
    previous?.isDevLernbereichPage &&
    String(previous.lernbereich || "") === currentLernbereich
  ) {
    return true;
  }

  return false;
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
  if (moduleScroller && document.body?.classList?.contains("page-module-designs")) {
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

function scheduleStabilizedRestore(pageKey, explicitTargetId) {
  if (explicitTargetId) return;
  if (!pageKey) return;

  const passesMs = [120, 320, 700, 1200];
  passesMs.forEach((delay) => {
    window.setTimeout(() => {
      // Never fight with the user once they started scrolling manually.
      if (userScrolledSinceBootstrap) return;
      restoreScrollPosition(pageKey);
    }, delay);
  });

  window.addEventListener("load", () => {
    if (userScrolledSinceBootstrap) return;
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
  userScrolledSinceBootstrap = false;

  const context = getPageContext();
  const pageKey = getScrollPageKey();
  const explicitTargetId = resolveScrollTargetId(context);
  const contentRoot = document.querySelector(".mod-content") || document.body;
  const allowStoredHydration = shouldHydrateLocalState(context);

  bindScrollPersistence(pageKey);

  // Pre-restore to reduce visual jump from top to remembered position.
  if (!explicitTargetId && allowStoredHydration) {
    restoreScrollPosition(pageKey);
  }

  if (allowStoredHydration) {
    scheduleStabilizedRestore(pageKey, explicitTargetId);
  }

  if (context.moduleKey === "training") {
    const root = document.getElementById("dev-training-root");
    if (!root) return;
    await initTrainingModule({
      root,
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
      usePersistedState: allowStoredHydration,
    });
    await typesetMath(root);
    if (explicitTargetId) {
      scrollToTargetId(explicitTargetId);
    } else if (allowStoredHydration) {
      // Post-restore after rendering to counter layout shifts.
      restoreScrollPosition(pageKey);
    }
    writeSessionModuleContext(context);
    return;
  }

  if (context.moduleKey === "start") {
    await initStartModule({
      lernbereich: context.lernbereich,
    });
    writeSessionModuleContext(context);
    return;
  }

  if (context.moduleKey === "einstiegsquiz") {
    await initEinstiegsquizModule({
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
    });
    writeSessionModuleContext(context);
    return;
  }

  if (context.moduleKey === "kompetenzliste") {
    const root = document.getElementById("dev-kompetenzliste-root");
    await initKompetenzlisteModule({
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
    });
    if (root) await typesetMath(root);
    writeSessionModuleContext(context);
    return;
  }

  if (context.moduleKey === "blurting") {
    const root = document.getElementById("dev-blurting-root");
    if (!root) return;
    await initBlurtingModule({
      root,
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
    });
    await typesetMath(root);
    if (explicitTargetId) {
      scrollToTargetId(explicitTargetId);
    } else if (allowStoredHydration) {
      restoreScrollPosition(pageKey);
    }
    writeSessionModuleContext(context);
    return;
  }

  if (context.moduleKey === "feynman") {
    const root = document.getElementById("dev-feynman-root");
    if (!root) return;
    await initFeynmanModule({
      root,
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
    });
    await typesetMath(root);
    if (explicitTargetId) {
      scrollToTargetId(explicitTargetId);
    } else if (allowStoredHydration) {
      restoreScrollPosition(pageKey);
    }
    writeSessionModuleContext(context);
    return;
  }

  if (context.moduleKey === "flashcards") {
    const root = document.getElementById("dev-flashcards-root");
    if (!root) return;
    await initFlashcardsModule({
      root,
      lernbereich: context.lernbereich,
      preferredCheckId: context.checkId,
    });
    await typesetMath(root);
    if (explicitTargetId) {
      scrollToTargetId(explicitTargetId);
    } else if (allowStoredHydration) {
      restoreScrollPosition(pageKey);
    }
    writeSessionModuleContext(context);
    return;
  }

  // Static pages such as skript rely on markdown content already in the DOM.
  if (context.moduleKey === "skript") {
    initSkriptHeadingNav({
      root: contentRoot,
    });
    const scriptContentRoot = contentRoot.querySelector(":scope > .mod-script-content") || contentRoot;
    await initSkriptInfoCards(scriptContentRoot, context.lernbereich);
    await initCheckAnker({ root: scriptContentRoot, lernbereich: context.lernbereich });
    await initScriptTaskDuplicatesModule({
      root: scriptContentRoot,
      lernbereich: context.lernbereich,
      usePersistedState: true,
    });
  }

  await typesetMath(contentRoot);

  if (explicitTargetId) {
    if (context.moduleKey === "skript") {
      openNoteCardIfPresent(document.getElementById(explicitTargetId));
    } else {
      scrollToTargetId(explicitTargetId);
    }
  } else if (allowStoredHydration) {
    restoreScrollPosition(pageKey);
  }

  writeSessionModuleContext(context);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootstrap);
} else {
  bootstrap();
}
