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

// Beim Verlassen Scrollposition speichern
/*window.addEventListener("beforeunload", () => {
  sessionStorage.setItem("scrollPos_" + location.pathname, window.scrollY);
});


window.addEventListener("load", () => {
  const savedPos = sessionStorage.getItem("scrollPos_" + location.pathname);
  if (savedPos !== null) {
    window.scrollTo(0, parseInt(savedPos, 10));
  }
});*/
