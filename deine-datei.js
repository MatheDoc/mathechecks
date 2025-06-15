const header = document.querySelector('header'); // Passe ggf. den Selektor an
const headerHeight = header ? header.offsetHeight : 0;
const y = zielElement.getBoundingClientRect().top + window.pageYOffset - headerHeight;
window.scrollTo({ top: y, behavior: "smooth" });