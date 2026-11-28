// Erklärvideo pro Check (Modul „Video“). Quelle: Feld `video` (YouTube-ID) in checks.json.
// Alle Videos des Lernbereichs stehen untereinander (eine Karte pro Check, wie in Training/Recall/Feynman).
// Zunächst nur das eigene Vorschaubild; erst der Klick lädt den YouTube-Player (youtube-nocookie) und startet ihn.
// Es läuft höchstens ein Video: Startet ein anderes oder scrollt es aus dem Bild, pausiert es.
// Kein Fortschritt, kein Feed, keine XP. Einbindung und Datenschutz: videos/README.md
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { enhanceCheckJumpNav } from "./ui/check-jump-nav.js";
import { getChecksByLernbereich } from "../data/checks-repo.js?v=20260523-checks-url-fix";

const JUMP_NAV_ID = "video-jump-nav";
const WARMUP_IDS_ID = "video-warmup-ids";
const YOUTUBE_ID = /^[A-Za-z0-9_-]{11}$/;

const VISIBLE_RATIO = 0.4;

let apiPromise = null;
const players = new Set();

function el(tag, className = "", html = null) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (html !== null) node.innerHTML = html;
  return node;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function loadYouTubeApi() {
  if (window.YT?.Player) return Promise.resolve(window.YT);
  if (apiPromise) return apiPromise;
  apiPromise = new Promise((resolve, reject) => {
    const previous = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      if (typeof previous === "function") previous();
      resolve(window.YT);
    };
    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    script.async = true;
    script.onerror = () => {
      apiPromise = null;
      script.remove();
      reject(new Error("YouTube konnte nicht geladen werden."));
    };
    document.head.appendChild(script);
  });
  return apiPromise;
}

function pausePlayer(player) {
  try {
    if (player?.getPlayerState?.() === window.YT?.PlayerState?.PLAYING) player.pauseVideo();
  } catch {
    /* Player war noch nicht bereit */
  }
}

function pauseOthers(current) {
  players.forEach((player) => {
    if (player !== current) pausePlayer(player);
  });
}

const PLAY_ICON = '<svg viewBox="1.8 0 24 24" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.6-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5Z"/></svg>';
const REPLAY_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5V2L7 6l5 4V7a5 5 0 1 1-5 5H5a7 7 0 1 0 7-7Z"/></svg>';

function buildPoster(entry, vorschauBase) {
  const poster = el("button", "vid-poster");
  poster.type = "button";
  poster.setAttribute("aria-label", `Video abspielen: ${entry.titel}`);

  const img = el("img", "vid-poster__img");
  img.alt = "";
  img.decoding = "async";
  img.src = `${vorschauBase}${entry.check_id}.webp`;
  img.addEventListener("error", () => {
    img.remove();
    poster.classList.add("vid-poster--text");
  });

  const fallback = el("span", "vid-poster__text");
  fallback.append(el("span", "vid-poster__kicker", "Ich kann …"), el("span", "vid-poster__kompetenz", escapeHtml(entry.kompetenz)));

  poster.append(img, fallback, el("span", "vid-poster__play", PLAY_ICON));
  return poster;
}

function linkButton(label, href, primary = false) {
  const link = el("a", `vid-btn${primary ? " vid-btn--primary" : ""}`, `${label} <span aria-hidden="true">→</span>`);
  link.href = href;
  return link;
}

function buildNextLinks(entry) {
  const links = [];
  if (entry.warmup_url) links.push(linkButton("Warm-Up", entry.warmup_url, true));
  links.push(linkButton("Training", entry.training_url, !entry.warmup_url));
  return links;
}

function renderCard(entry, { vorschauBase }) {
  const section = el("section", "check-viewport-item check-viewport-item--scroll-card");
  section.id = `check-${entry.nummer}`;
  section.dataset.checkId = entry.check_id;

  const card = el("article", "check-card check-card--video vid-card");
  const header = el("div", "check-card__header");
  header.innerHTML = renderCheckMetaRowMarkup({
    numberText: formatCheckNumber(entry.nummer),
    titleText: entry.titel || "Video",
    prefix: "Video",
    rowClass: "check-card__header-left",
    titleTag: "span",
  });
  const youtubeLink = el("a", "vid-youtube-link", 'Auf YouTube <span aria-hidden="true">↗</span>');
  youtubeLink.href = `https://www.youtube.com/shorts/${entry.video}`;
  youtubeLink.target = "_blank";
  youtubeLink.rel = "noopener";
  header.firstElementChild.appendChild(youtubeLink);

  const body = el("div", "check-card__body vid-body");
  const frame = el("div", "vid-frame");
  const host = el("div", "vid-player");
  const poster = buildPoster(entry, vorschauBase);
  const status = el("p", "vid-status");
  status.setAttribute("role", "status");
  status.hidden = true;

  const ende = el("div", "vid-end");
  ende.hidden = true;
  const replay = el("button", "vid-btn vid-btn--ghost", `${REPLAY_ICON} Nochmal`);
  replay.type = "button";
  const endeLinks = el("div", "vid-end__links");
  endeLinks.append(...buildNextLinks(entry));
  ende.append(el("span", "vid-end__kicker", "Jetzt bist du dran."), endeLinks, replay);

  frame.append(host, poster, ende, status);

  body.appendChild(frame);
  card.append(header, body);
  section.appendChild(card);

  let player = null;
  let ended = false;

  const showEnd = (visible) => {
    ended = visible;
    ende.hidden = !visible;
    frame.classList.toggle("is-ended", visible);
  };

  async function start() {
    if (player) {
      player.playVideo();
      return;
    }
    frame.classList.add("is-loading");
    poster.disabled = true;
    let YT;
    try {
      YT = await loadYouTubeApi();
    } catch (error) {
      frame.classList.remove("is-loading");
      poster.disabled = false;
      status.hidden = false;
      status.textContent = `${error.message} Bitte später erneut versuchen oder das Video direkt auf YouTube ansehen.`;
      return;
    }
    const target = el("div");
    host.appendChild(target);
    player = new YT.Player(target, {
      host: "https://www.youtube-nocookie.com",
      videoId: entry.video,
      width: "100%",
      height: "100%",
      playerVars: {
        autoplay: 1,
        playsinline: 1,
        rel: 0,
        iv_load_policy: 3,
        origin: window.location.origin,
      },
      events: {
        onReady: (event) => {
          event.target.playVideo();
          frame.classList.remove("is-loading");
          frame.classList.add("is-active");
        },
        onStateChange: (event) => {
          if (event.data === YT.PlayerState.PLAYING) pauseOthers(player);
          if (event.data === YT.PlayerState.ENDED) showEnd(true);
          else if (event.data === YT.PlayerState.PLAYING && ended) showEnd(false);
        },
        onError: () => {
          frame.classList.remove("is-loading");
          status.hidden = false;
          status.textContent = "Das Video kann hier nicht abgespielt werden. Bitte direkt auf YouTube ansehen.";
        },
      },
    });
    players.add(player);
  }

  poster.addEventListener("click", start);
  replay.addEventListener("click", () => {
    showEnd(false);
    player?.seekTo(0, true);
    player?.playVideo();
  });

  frame.pauseVideo = () => pausePlayer(player);
  return section;
}

// Video pausieren, sobald es größtenteils aus dem Bild gescrollt ist
function bindPauseWhenHidden(frames) {
  if (typeof IntersectionObserver !== "function") return;
  const observer = new IntersectionObserver(
    (records) => {
      records.forEach((record) => {
        if (record.intersectionRatio < VISIBLE_RATIO) record.target.pauseVideo?.();
      });
    },
    { threshold: [0, VISIBLE_RATIO] }
  );
  frames.forEach((frame) => observer.observe(frame));
}

/* ───────────────────────── Modul: Auswahl pro Lernbereich ───────────────────────── */

function readWarmupIds() {
  try {
    const ids = JSON.parse(document.getElementById(WARMUP_IDS_ID)?.textContent || "[]");
    return new Set(Array.isArray(ids) ? ids.map(String) : []);
  } catch {
    return new Set();
  }
}

function buildEntries(checks, warmupIds) {
  return checks
    .map((check) => {
      const video = String(check?.video || "").trim();
      if (!YOUTUBE_ID.test(video)) return null;
      const nummer = Number(check.Nummer);
      const checkId = String(check.check_id || "");
      return {
        check_id: checkId,
        video,
        nummer,
        titel: String(check.Schlagwort || "").trim(),
        kompetenz: String(check["Ich kann"] || "").trim(),
        training_url: `training.html#check-${nummer}`,
        warmup_url: warmupIds.has(checkId) ? `warmup.html#check-${nummer}` : "",
      };
    })
    .filter(Boolean)
    .sort((a, b) => a.nummer - b.nummer);
}

function scrollModMainToEl(target) {
  const container = document.querySelector(".mod-main");
  if (!container) {
    target.scrollIntoView({ behavior: "auto", block: "start" });
    return;
  }
  const tabNav = container.querySelector(".mod-tab-nav");
  const jumpNavWrap = container.querySelector(".check-jump-nav-wrap");
  const offset = (tabNav ? tabNav.offsetHeight : 0) + (jumpNavWrap ? jumpNavWrap.offsetHeight : 0);
  const y = container.scrollTop + target.getBoundingClientRect().top - container.getBoundingClientRect().top - offset;
  container.scrollTo({ top: Math.max(0, y), behavior: "auto" });
}

function setJumpNavActive(navNode, checkId) {
  if (!navNode) return;
  navNode.querySelectorAll(".check-jump-tab").forEach((tab) => {
    const active = tab.dataset.checkId === checkId;
    tab.classList.toggle("active", active);
    if (active) tab.setAttribute("aria-current", "true");
    else tab.removeAttribute("aria-current");
  });
}

function renderJumpNav(navNode, entries) {
  if (!navNode) return;
  navNode.innerHTML = "";
  entries.forEach((entry) => {
    const tab = el("a", "check-jump-tab");
    tab.href = `#check-${entry.nummer}`;
    tab.dataset.checkId = entry.check_id;
    tab.textContent = `${entry.nummer}. ${entry.titel || "Check"}`;
    navNode.appendChild(tab);
  });
  navNode.addEventListener("click", (event) => {
    const tab = event.target.closest(".check-jump-tab");
    if (!tab) return;
    event.preventDefault();
    const target = document.getElementById(tab.getAttribute("href").slice(1));
    if (!target) return;
    setJumpNavActive(navNode, tab.dataset.checkId);
    scrollModMainToEl(target);
  });
  enhanceCheckJumpNav(navNode);
}

// Aktiven Reiter beim Scrollen mitführen (wie in Feynman und Recall)
function bindJumpNavScrollSync(navNode, sections) {
  if (!navNode || !sections.length) return;
  const update = () => {
    const offsetTop = 210;
    let passed = null;
    let upcoming = null;
    let upcomingDistance = Number.POSITIVE_INFINITY;
    sections.forEach((section) => {
      const distance = section.getBoundingClientRect().top - offsetTop;
      if (distance <= 0) {
        passed = section;
      } else if (distance < upcomingDistance) {
        upcomingDistance = distance;
        upcoming = section;
      }
    });
    setJumpNavActive(navNode, (passed || upcoming || sections[0]).dataset.checkId);
  };
  let ticking = false;
  const onChange = () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(() => {
      ticking = false;
      update();
    });
  };
  (document.querySelector(".mod-main") || window).addEventListener("scroll", onChange, { passive: true });
  window.addEventListener("resize", onChange);
  update();
}

export async function initVideoModule({ root, lernbereich, preferredCheckId = "" } = {}) {
  if (!root) return;
  const navNode = document.getElementById(JUMP_NAV_ID);
  const options = {
    vorschauBase: root.dataset.vorschauBase || "/assets/img/videos/",
  };

  let checks = [];
  try {
    checks = await getChecksByLernbereich(lernbereich);
  } catch (error) {
    root.innerHTML = `<p class="module-status">${escapeHtml(error.message)}</p>`;
    return;
  }

  const entries = buildEntries(checks, readWarmupIds());
  if (!entries.length) {
    root.innerHTML = '<p class="module-status">Für diesen Lernbereich gibt es noch keine Videos.</p>';
    return;
  }

  renderJumpNav(navNode, entries);
  const sections = entries.map((entry) => renderCard(entry, options));
  root.replaceChildren(...sections);
  window.MathJax?.typesetPromise?.([root]).catch(() => {});
  bindPauseWhenHidden(sections.map((section) => section.querySelector(".vid-frame")));
  bindJumpNavScrollSync(navNode, sections);

  // Sprung per #check-<Nummer> übernimmt app.js (scrollToTargetId)
  const preferred = String(preferredCheckId || "").trim();
  const preferredSection = preferred ? sections.find((section) => section.dataset.checkId === preferred) : null;
  if (preferredSection) {
    setJumpNavActive(navNode, preferred);
    scrollModMainToEl(preferredSection);
  }
}
