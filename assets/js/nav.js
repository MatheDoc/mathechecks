// Toggle visibility of the main menu
function toggleMenu() {
  const menu = document.getElementById("main-menu");
  menu.classList.toggle("hidden");
}

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
