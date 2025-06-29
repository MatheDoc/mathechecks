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

<button id="install-button" style="display: none;">App installieren</button>

<main style="padding-top: 1rem">
<div id="ichkann-box" style="display: flex; justify-content: center; align-items: center; font-size: 2em; text-align: center; color: var(--hauptfarbe);">
</div>
</main>

<script>
async function ladeKompetenzBox() {
  try {
    const responseKompetenzliste = await fetch("/kompetenzliste.json");
    const daten = await responseKompetenzliste.json();

    if (!Array.isArray(daten) || daten.length === 0) {
      document.getElementById("ichkann-box").innerText = "Keine Kompetenzdaten verfügbar.";
      return;
    }

    const zufall = daten[Math.floor(Math.random() * daten.length)];
    const frage = zufall["Ich kann"].replace(/\.$/, "?");
    const nummer = parseFloat(zufall.Nummer).toString();
    const ziel = `lernbereiche/${zufall.Gebiet}/${zufall.Lernbereich}/uebungen.html#aufgabe-${nummer}`;

    const div = document.getElementById("ichkann-box");

    // Erstelle ein <span> als Container für Text + Icon
    const spanContainer = document.createElement('span');
    div.innerHTML = ''; // Inhalt leeren
    div.appendChild(spanContainer);

    const vollerText = `Kannst du ${frage} `;

    function typeWriter(text, element, delay = 50, callback) {
      let i = 0;
      element.textContent = ''; // Text leeren (keine HTML, nur Text)

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

    typeWriter(vollerText, spanContainer, 50, () => {
      // Icon als Inline-Element ans Ende des Textes (innerhalb von spanContainer)
      const icon = document.createElement('i');
      icon.className = "fas fa-arrow-circle-right icon";
      spanContainer.appendChild(icon);
    });

    div.onclick = () => window.location.href = ziel;

  } catch (err) {
    document.getElementById("ichkann-box").innerText = "Fehler beim Laden der Kompetenzen.";
    console.error(err);
  }
}

ladeKompetenzBox();
</script>
