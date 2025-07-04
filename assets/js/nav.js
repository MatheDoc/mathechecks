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

/*document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll(".nav-materialtyp .nav-link");
  const currentPath = window.location.href.split("#")[0]; // ohne Anker

  links.forEach((link) => {
    link.classList.remove("ausgewählt");

    const linkHref = link.href.split("#")[0]; // ohne Anker

    if (linkHref === currentPath) {
      link.classList.add("ausgewählt");
    }
  });
});*/

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
