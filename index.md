---
layout: zusatzmaterial
title: ""
description: "Entdecke allen Themen der Mathematik: interaktiv und kostenlos."
---

<style>
  #ichkann-box .icon:hover {
  color: var(--hauptfarbe-hover); 
  transform: scale(1.2);
}
</style>

<main style="padding-top: 1rem">
  <div id="ichkann-box" style="
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2em;
  color: var(--hauptfarbe);
  text-align: center;
  padding: 0 1rem;
  max-width: 90vw;
  flex-wrap: wrap;
  word-break: normal;
  overflow-wrap: break-word;
  hyphens: auto;
  ">
    <span id="ichkann-text" style="display: inline-block;pointer-events: none;"></span>
     <span id="ichkann-icon" style="margin-left: 0.5rem;"></span>
  </div>
</main>

<script>
async function ladeKompetenzBox() {
  try {
    const response = await fetch("/kompetenzliste.json");
    const daten = await response.json();

    if (!Array.isArray(daten) || daten.length === 0) {
      document.getElementById("ichkann-text").innerText = "Keine Kompetenzdaten verfügbar.";
      return;
    }

    const zufall = daten[Math.floor(Math.random() * daten.length)];
    const frage = zufall["Ich kann"].replace(/\.$/, "?");
    const nummer = parseFloat(zufall.Nummer).toString();
    const ziel = `lernbereiche/${zufall.Gebiet}/${zufall.Lernbereich}/uebungen.html#aufgabe-${nummer}`;

    const span = document.getElementById("ichkann-text");
    span.textContent = ""; // leeren

    const vollerText = `Kannst du ${frage} `;

    function typeWriter(text, element, delay = 50, callback) {
      let i = 0;
      function schreiben() {
        if (i < text.length) {
          element.textContent += text.charAt(i);
          i++;
          setTimeout(schreiben, delay);
        } else if (callback) {
          callback();
        }
      }
      schreiben();
    }

typeWriter(vollerText, span, 50, () => {
  const icon = document.createElement("i");
  icon.className = "fas fa-arrow-circle-right icon";
  icon.style.cursor = "pointer";
  icon.onclick = () => {
    window.location.href = ziel;
  };
  document.getElementById("ichkann-icon").appendChild(icon);
});


  
  } catch (err) {
    document.getElementById("ichkann-text").innerText = "Fehler beim Laden der Kompetenzen.";
    console.error(err);
  }
}

ladeKompetenzBox();
</script>
