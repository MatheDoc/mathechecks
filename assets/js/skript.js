/*document.addEventListener("DOMContentLoaded", () => {
  const toc = document.getElementById("toc");
  const leftBtn = document.querySelector(".scroll-btn.left");
  const rightBtn = document.querySelector(".scroll-btn.right");

  const scrollAmount = 250;

  leftBtn.addEventListener("click", () => {
    toc.scrollBy({ left: -scrollAmount, behavior: "smooth" });
  });

  rightBtn.addEventListener("click", () => {
    toc.scrollBy({ left: scrollAmount, behavior: "smooth" });
  });

  toc.addEventListener("wheel", (e) => {
    if (e.deltaY !== 0) {
      e.preventDefault();
      toc.scrollBy({ left: e.deltaY, behavior: "smooth" });
    }
  });
  
  // Dynamische Überschriftenebene basierend auf der URL
    const path = window.location.pathname;
    let headingLevel = "h2"; // Standard für "skript"

    if (path.includes("uebungen") || path.includes("übungen")) {
      headingLevel = "h4";
    }

    tocbot.init({
      tocSelector: "#toc",
      contentSelector: "#main-content",
      headingSelector: headingLevel,
      scrollSmoothOffset: 180,
    });

});


const tocbotLinks = document.querySelectorAll('#toc a');
tocbotLinks.forEach(link => link.classList.remove('is-active-link'));

*/


