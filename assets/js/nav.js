// Toggle visibility of the main menu
function toggleMenu() {
  const menu = document.getElementById("main-menu");
  menu.classList.toggle("hidden");
}

function toggleCalculatorOverlay(forceOpen) {
  const overlay = document.getElementById("calculator-overlay");
  const toggleButton = document.querySelector(".calculator-toggle");
  if (!overlay) return;
  const modal = overlay.querySelector(".calculator-modal");
  const hasOpenOverride = typeof forceOpen === "boolean";
  const isOpen = overlay.classList.contains("open");
  const isTranslucent = modal ? modal.classList.contains("is-translucent") : false;
  let nextState = "closed";

  if (hasOpenOverride) {
    nextState = forceOpen ? "opaque" : "closed";
  } else if (!isOpen) {
    nextState = "opaque";
  } else if (!isTranslucent) {
    nextState = "translucent";
  }

  const shouldOpen = nextState !== "closed";
  overlay.classList.toggle("open", shouldOpen);
  overlay.setAttribute("aria-hidden", shouldOpen ? "false" : "true");

  if (modal) {
    modal.classList.toggle("is-translucent", nextState === "translucent");
    if (!shouldOpen) {
      modal.classList.remove("is-pending");
    }
  }

  if (toggleButton) {
    toggleButton.classList.toggle("is-active", shouldOpen);
    toggleButton.classList.toggle("is-translucent", nextState === "translucent");
    toggleButton.setAttribute("aria-pressed", shouldOpen ? "true" : "false");
  }

  if (shouldOpen) {
    const width = Number(overlay.dataset.calcWidth || 0);
    const height = Number(overlay.dataset.calcHeight || 0);
    const hasSize = Boolean(width && height);
    if (modal) {
      modal.classList.toggle("is-pending", !hasSize);
    }
    if (!width || !height) {
      applyCalculatorSize(520, 820);
    }
    const iframe = overlay.querySelector(".calculator-frame");
    if (iframe) {
      const sendFocus = () => {
        iframe.focus();
        if (iframe.contentWindow) {
          iframe.contentWindow.postMessage({ type: "calculatorFocus" }, window.location.origin);
          iframe.contentWindow.postMessage({ type: "calculatorRequestSize" }, window.location.origin);
        }
      };
      if (iframe.contentDocument && iframe.contentDocument.readyState === "complete") {
        setTimeout(sendFocus, 0);
      } else {
        iframe.addEventListener("load", sendFocus, { once: true });
      }
    }
  }
}

function applyCalculatorSize(width, height) {
  const overlay = document.getElementById("calculator-overlay");
  if (!overlay) return;
  const modal = overlay.querySelector(".calculator-modal");
  const iframe = overlay.querySelector(".calculator-frame");
  const drag = overlay.querySelector(".calculator-drag");
  if (!modal || !iframe) return;

  const dragHeight = drag ? drag.offsetHeight : 0;
  const maxWidth = Math.floor(window.innerWidth * 0.92);
  const maxHeight = Math.floor(window.innerHeight * 0.9);
  const targetWidth = Math.min(width, maxWidth);
  const targetHeight = Math.min(height + dragHeight, maxHeight);

  modal.style.width = `${targetWidth}px`;
  modal.style.height = `${targetHeight}px`;
  iframe.style.height = `${Math.max(targetHeight - dragHeight, 0)}px`;

  overlay.dataset.calcWidth = String(width);
  overlay.dataset.calcHeight = String(height);
}

let calculatorDragState = {
  active: false,
  startX: 0,
  startY: 0,
  startOffsetX: 0,
  startOffsetY: 0,
  pendingOffsetX: 0,
  pendingOffsetY: 0,
  rafId: 0,
  modal: null,
  iframe: null,
};


const setCalculatorOffsets = (modal, x, y) => {
  if (!modal) return;
  modal.dataset.offsetX = String(x);
  modal.dataset.offsetY = String(y);
  modal.style.transform = `translate3d(${x}px, ${y}px, 0)`;
};

const getCalculatorOffsets = (modal) => {
  const x = Number(modal?.dataset.offsetX || 0);
  const y = Number(modal?.dataset.offsetY || 0);
  return { x, y };
};

window.addEventListener("message", (event) => {
  if (event.origin !== window.location.origin && event.origin !== "null") return;
  const data = event.data;
  if (!data || typeof data.type !== "string") return;

  if (data.type === "calculatorSize") {
    if (typeof data.width !== "number" || typeof data.height !== "number") return;
    if (data.width > 0 && data.height > 0) {
      applyCalculatorSize(Math.round(data.width), Math.round(data.height));
      const overlay = document.getElementById("calculator-overlay");
      const modal = overlay ? overlay.querySelector(".calculator-modal") : null;
      if (overlay && overlay.classList.contains("open") && modal) {
        modal.classList.remove("is-pending");
      }
    }
    return;
  }

  if (!calculatorDragState.modal || !calculatorDragState.iframe) return;

  if (data.type === "calculatorDragStart") {
    if (typeof data.screenX !== "number" || typeof data.screenY !== "number") {
      if (typeof data.clientX !== "number" || typeof data.clientY !== "number") return;
    }
    const { x, y } = getCalculatorOffsets(calculatorDragState.modal);
    calculatorDragState.active = true;
    calculatorDragState.startOffsetX = x;
    calculatorDragState.startOffsetY = y;
    document.documentElement.classList.add("calculator-dragging");
    if (typeof data.screenX === "number" && typeof data.screenY === "number") {
      calculatorDragState.startX = data.screenX;
      calculatorDragState.startY = data.screenY;
      return;
    }
    const iframeRect = calculatorDragState.iframe.getBoundingClientRect();
    calculatorDragState.startX = iframeRect.left + data.clientX;
    calculatorDragState.startY = iframeRect.top + data.clientY;
    return;
  }

  if (data.type === "calculatorDragMove") {
    if (!calculatorDragState.active) return;
    if (typeof data.screenX !== "number" || typeof data.screenY !== "number") {
      if (typeof data.clientX !== "number" || typeof data.clientY !== "number") return;
    }
    let currentX;
    let currentY;
    if (typeof data.screenX === "number" && typeof data.screenY === "number") {
      currentX = data.screenX;
      currentY = data.screenY;
    } else {
      const iframeRect = calculatorDragState.iframe.getBoundingClientRect();
      currentX = iframeRect.left + data.clientX;
      currentY = iframeRect.top + data.clientY;
    }
    const dx = currentX - calculatorDragState.startX;
    const dy = currentY - calculatorDragState.startY;
    calculatorDragState.pendingOffsetX = calculatorDragState.startOffsetX + dx;
    calculatorDragState.pendingOffsetY = calculatorDragState.startOffsetY + dy;
    if (!calculatorDragState.rafId) {
      calculatorDragState.rafId = window.requestAnimationFrame(() => {
        calculatorDragState.rafId = 0;
        setCalculatorOffsets(
          calculatorDragState.modal,
          calculatorDragState.pendingOffsetX,
          calculatorDragState.pendingOffsetY
        );
      });
    }
    return;
  }

  if (data.type === "calculatorDragEnd") {
    calculatorDragState.active = false;
    document.documentElement.classList.remove("calculator-dragging");
  }
});

window.addEventListener("resize", () => {
  const overlay = document.getElementById("calculator-overlay");
  if (!overlay) return;
  const width = Number(overlay.dataset.calcWidth || 0);
  const height = Number(overlay.dataset.calcHeight || 0);
  if (width && height) {
    applyCalculatorSize(width, height);
  }
});


document.addEventListener("click", function (event) {
  const menu = document.getElementById("main-menu");
  const authModal = document.getElementById("auth-modal-overlay");

  // Prüfe ob das Menu existiert
  if (!menu) return;

  const isClickInsideMenu = menu.contains(event.target);
  const isClickInsideAuthModal = authModal && authModal.contains(event.target);
  const isButtonClick = event.target.closest("button");

  if (!isClickInsideMenu && !isClickInsideAuthModal && !isButtonClick) {
    menu.classList.add("hidden");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll(".nav-materialtyp .nav-link");
  const currentPath = window.location.href.split("#")[0];

  const overlay = document.getElementById("calculator-overlay");
  if (overlay) {
    const modal = overlay.querySelector(".calculator-modal");
    const iframe = overlay.querySelector(".calculator-frame");
    calculatorDragState.modal = modal || null;
    calculatorDragState.iframe = iframe || null;
  }

  links.forEach((link) => {
    link.classList.remove("ausgewählt");
    const linkHref = link.href.split("#")[0];
    if (linkHref === currentPath) {
      link.classList.add("ausgewählt");
    }
  });
});

// Service Worker Registration
if (
  "serviceWorker" in navigator &&
  !["localhost", "127.0.0.1"].includes(location.hostname)
) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/service-worker.js")
      .then((registration) => {
        console.log(
          "Service Worker registered with scope:",
          registration.scope
        );
      })
      .catch((error) => {
        console.error("Service Worker registration failed:", error);
      });
  });
}
