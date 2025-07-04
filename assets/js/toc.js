// Entfernen der Klasse 'is-active-link' von allen ToC-Links, Klassen werden stattdessen in nav.js gesetzt
const tocbotLinks = document.querySelectorAll("#toc a");
tocbotLinks.forEach((link) => link.classList.remove("is-active-link"));

// Laden der Aufgaben für den Lernbereich
async function ladeUndScrolle(lernbereich) {
  await ladeAufgabenFürLernbereich(lernbereich);

  // Dynamische Überschriftenebene basierend auf der URL
  const path = window.location.pathname;
  let headingLevel = "h2"; // Standard für "skript"
  //
  if (path.includes("uebungen") || path.includes("übungen")) {
    //ids manuell setzen, funktioniert nicht mit tocbot
    document.querySelectorAll("h4").forEach((h4) => {
      const match = h4.textContent.trim().match(/^(\d+)\.\s*Check$/i);
      if (match) {
        const nummer = match[1];
        h4.id = `check-${nummer}`;
      }
    });

    headingLevel = "h4";
  }
  console.log("Überschriftenebene:", headingLevel);
  tocbot.init({
    tocSelector: "#toc",
    contentSelector: "#main-content",
    headingSelector: headingLevel,
    scrollSmoothOffset: 180,
  });

  // 1. Bei initialem Seitenaufruf mit #hash
  const hash = window.location.hash;
  if (hash) {
    scrollZuHash(hash);
  }

  // 2. Event-Handler für spätere Klicks im Inhaltsverzeichnis
  document.querySelectorAll(".toc-link").forEach((link) => {
    link.addEventListener("click", function (event) {
      event.preventDefault(); // Das hier soll das Standardverhalten verhindern
      event.stopImmediatePropagation();
      // Führe nur diesen Teil aus, wenn preventDefault funktionieren SOLLTE
      const ziel = this.getAttribute("href").substring(1);
      scrollZuHash(ziel);
    });
  });
}

ladeUndScrolle(lernbereich);

// Spy für Toc n(wegen Header)
const HEADER_OFFSET = 180;

function scrollSpy() {
  const links = document.querySelectorAll("#toc a");
  const sections = Array.from(links)
    .map((link) => {
      const hash = link.getAttribute("href");
      if (!hash) return null;
      const section = document.querySelector(hash);
      return section;
    })
    .filter(Boolean);

  window.addEventListener("scroll", () => {
    const scrollPosition = window.scrollY + HEADER_OFFSET + 1; // +1 um kleine Rundungsfehler zu vermeiden

    let activeIndex = 0;

    for (let i = 0; i < sections.length; i++) {
      const sectionTop = sections[i].offsetTop;

      if (scrollPosition >= sectionTop) {
        activeIndex = i;
      } else {
        break;
      }
    }

    links.forEach((link) => link.classList.remove("aktiver-link"));
    if (links[activeIndex]) {
      links[activeIndex].classList.add("aktiver-link");
    }
  });
}

// Nach DOM- und Inhalt-Laden aufrufen
document.addEventListener("DOMContentLoaded", () => {
  scrollSpy();
});

document.addEventListener("DOMContentLoaded", () => {
  // Scroll-Buttons für die ToC
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
});
