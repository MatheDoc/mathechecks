// Toggle visibility of the main menu
function toggleMenu() {
  const menu = document.getElementById("main-menu");
  menu.classList.toggle("hidden");
}

function toggleCalculatorOverlay(forceOpen) {
  const overlay = document.getElementById("calculator-overlay");
  const toggleButton = document.querySelector(".calculator-toggle");
  if (!overlay) return;
  const shouldOpen = typeof forceOpen === "boolean" ? forceOpen : !overlay.classList.contains("open");
  overlay.classList.toggle("open", shouldOpen);
  overlay.setAttribute("aria-hidden", shouldOpen ? "false" : "true");
  if (toggleButton) {
    toggleButton.classList.toggle("is-active", shouldOpen);
    toggleButton.setAttribute("aria-pressed", shouldOpen ? "true" : "false");
  }
  if (shouldOpen) {
    const width = Number(overlay.dataset.calcWidth || 0);
    const height = Number(overlay.dataset.calcHeight || 0);
    if (!width || !height) {
      applyCalculatorSize(520, 720);
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
  modal: null,
  iframe: null,
};


const setCalculatorOffsets = (modal, x, y) => {
  if (!modal) return;
  modal.dataset.offsetX = String(x);
  modal.dataset.offsetY = String(y);
  modal.style.transform = `translate(${x}px, ${y}px)`;
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

  if (!calculatorDragState.modal || !calculatorDragState.iframe) return;
  const iframeRect = calculatorDragState.iframe.getBoundingClientRect();

  if (data.type === "calculatorDragStart") {
    if (typeof data.clientX !== "number" || typeof data.clientY !== "number") return;
    const { x, y } = getCalculatorOffsets(calculatorDragState.modal);
    calculatorDragState.active = true;
    calculatorDragState.startOffsetX = x;
    calculatorDragState.startOffsetY = y;
    calculatorDragState.startX = iframeRect.left + data.clientX;
    calculatorDragState.startY = iframeRect.top + data.clientY;
    return;
  }

  if (data.type === "calculatorDragMove") {
    if (!calculatorDragState.active) return;
    if (typeof data.clientX !== "number" || typeof data.clientY !== "number") return;
    const currentX = iframeRect.left + data.clientX;
    const currentY = iframeRect.top + data.clientY;
    const dx = currentX - calculatorDragState.startX;
    const dy = currentY - calculatorDragState.startY;
    setCalculatorOffsets(
      calculatorDragState.modal,
      calculatorDragState.startOffsetX + dx,
      calculatorDragState.startOffsetY + dy
    );
    return;
  }

  if (data.type === "calculatorDragEnd") {
    calculatorDragState.active = false;
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
