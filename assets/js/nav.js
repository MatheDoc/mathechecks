// Toggle visibility of the main menu
function toggleMenu() {
  const menu = document.getElementById("main-menu");
  menu.classList.toggle("hidden");
}

document.addEventListener("click", function (event) {
  const menu = document.getElementById("main-menu");
  const isClickInsideMenu = menu.contains(event.target);
  const isButtonClick = event.target.closest("button"); // Button direkt oder Icon darin

  if (!isClickInsideMenu && !isButtonClick) {
    menu.classList.add("hidden");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll(".nav-materialtyp .nav-link");
  const currentPath = window.location.href.split("#")[0]; // ohne Anker

  links.forEach((link) => {
    link.classList.remove("ausgewählt");

    const linkHref = link.href.split("#")[0]; // ohne Anker

    if (linkHref === currentPath) {
      link.classList.add("ausgewählt");
    }
  });
});

// Service Worker Registration
if ("serviceWorker" in navigator) {
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

let deferredPrompt;

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;

  const installButton = document.getElementById("install-button");
  if (!installButton) return;

  installButton.style.display = "inline-block";

  installButton.addEventListener("click", () => {
    installButton.style.display = "none";
    deferredPrompt.prompt();

    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === "accepted") {
        console.log("✅ Benutzer hat die Installation akzeptiert");
      } else {
        console.log("❌ Benutzer hat die Installation abgelehnt");
      }
      deferredPrompt = null;
    });
  });
});
