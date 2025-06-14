// Toggle visibility of the main menu
  function toggleMenu() {
    const menu = document.getElementById("main-menu");
    menu.classList.toggle("hidden");
  }


document.addEventListener('DOMContentLoaded', function() {
  const links = document.querySelectorAll('.nav-materialtyp .nav-link');
  const current = window.location.pathname.split('/').pop();

  links.forEach(link => {
    // Entferne ggf. vorhandene Klasse
    link.classList.remove('ausgewählt');
    // Vergleiche Dateinamen
    if (link.getAttribute('href') === current) {
      link.classList.add('ausgewählt');
    }
  });
});
