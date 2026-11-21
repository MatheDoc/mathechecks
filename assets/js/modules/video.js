// Erklärvideo pro Check (Modul „Video“). Quelle: Feld `video` (YouTube-ID) in checks.json.
// Zunächst nur das eigene Vorschaubild; erst der Klick lädt den YouTube-Player (youtube-nocookie) und startet ihn.
// Kein Fortschritt, kein Feed, keine XP. Einbindung und Datenschutz: videos/README.md
import { formatCheckNumber, renderCheckMetaRowMarkup } from "./ui/check-meta.js";
import { enhanceCheckJumpNav } from "./ui/check-jump-nav.js";
import { getChecksByLernbereich } from "../data/checks-repo.js?v=20260523-checks-url-fix";

const JUMP_NAV_ID = "video-jump-nav";
const WARMUP_IDS_ID = "video-warmup-ids";
const YOUTUBE_ID = /^[A-Za-z0-9_-]{11}$/;

let apiPromise = null;
let activePlayer = null;

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

function destroyActivePlayer() {
  try {
    activePlayer?.destroy();
  } catch {
    /* Player war noch nicht bereit */
  }
  activePlayer = null;
}

const PLAY_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.6-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5Z"/></svg>';
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

function renderPlayer(root, entry, { vorschauBase }) {
  destroyActivePlayer();
  root.innerHTML = "";

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
  root.appendChild(card);
  window.MathJax?.typesetPromise?.([card]).catch(() => {});

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
    if (!root.contains(frame)) return; // Check gewechselt, während die Schnittstelle lud
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
    activePlayer = player;
  }

  poster.addEventListener("click", start);
  replay.addEventListener("click", () => {
    showEnd(false);
    player?.seekTo(0, true);
    player?.playVideo();
  });
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

function resolveEntryFromLocation(entries, preferredCheckId = "") {
  const preferred = String(preferredCheckId || "").trim();
  if (preferred) {
    const byId = entries.find((entry) => entry.check_id === preferred);
    if (byId) return byId;
  }
  const rawHash = window.location.hash || "";
  const hash = decodeURIComponent(rawHash.startsWith("#") ? rawHash.slice(1) : rawHash);
  const match = /^check-(\d+)$/.exec(hash);
  if (match) {
    const byNummer = entries.find((entry) => entry.nummer === Number(match[1]));
    if (byNummer) return byNummer;
  }
  return entries[0] || null;
}

function renderJumpNav(navNode, entries, activeCheckId) {
  if (!navNode) return;
  navNode.innerHTML = "";
  entries.forEach((entry) => {
    const active = entry.check_id === activeCheckId;
    const tab = el("a", `check-jump-tab${active ? " active" : ""}`);
    tab.href = `#check-${entry.nummer}`;
    tab.dataset.checkId = entry.check_id;
    tab.textContent = `${entry.nummer}. ${entry.titel || "Check"}`;
    if (active) tab.setAttribute("aria-current", "true");
    navNode.appendChild(tab);
  });
  enhanceCheckJumpNav(navNode);
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

  let activeCheckId = "";
  const show = (entry) => {
    if (!entry || entry.check_id === activeCheckId) return;
    activeCheckId = entry.check_id;
    renderJumpNav(navNode, entries, activeCheckId);
    renderPlayer(root, entry, options);
  };

  show(resolveEntryFromLocation(entries, preferredCheckId));

  window.addEventListener("hashchange", () => {
    show(resolveEntryFromLocation(entries));
  });
}
