// Toggle visibility of the main menu
function toggleMenu() {
  const menu = document.getElementById("main-menu");
  menu.classList.toggle("hidden");
}

function toggleCalculatorOverlay(forceOpen) {
  const overlay = document.getElementById("calculator-overlay");
  if (!overlay) return;

  const hasOpenOverride = typeof forceOpen === "boolean";
  const isOpen = overlay.classList.contains("open");

  const shouldOpen = hasOpenOverride ? forceOpen : !isOpen;

  overlay.classList.toggle("open", shouldOpen);
  overlay.setAttribute("aria-hidden", shouldOpen ? "false" : "true");

  const toggleButton = document.querySelector(".calculator-toggle");
  if (toggleButton) {
    toggleButton.classList.toggle("is-active", shouldOpen);
    toggleButton.setAttribute("aria-pressed", shouldOpen ? "true" : "false");
  }

  // Focus main input when opening
  if (shouldOpen) {
    setTimeout(() => {
      const mainInput = document.getElementById('mainInput');
      if (mainInput) {
        mainInput.focus();
      }
    }, 100);
  }
}

document.addEventListener("click", function (event) {
  const menu = document.getElementById("main-menu");
  const authModal = document.getElementById("auth-modal-overlay");

  // Check if menu exists
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
