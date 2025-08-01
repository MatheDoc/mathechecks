let aufgabenZaehler = 1; // Initialisiere den Zähler für die Aufgaben
let questionId = 1; // Eindeutige Frage-ID für jede Aufgabe

let aktuelleEinträge = []; // global
let aktuellerLernbereich = ""; // global

async function ladeAufgabenFürLernbereich(lernbereich) {
  try {
    aktuellerLernbereich = lernbereich;
    const responseKompetenzliste = await fetch("/kompetenzliste.json"); // Liquid wird nicht in js aufgelöst, daher ohne relative_url;
    const daten = await responseKompetenzliste.json();

    aktuelleEinträge = daten.filter(
      (eintrag) => eintrag.Lernbereich === lernbereich && eintrag.Typ
    );

    const pfad = window.location.pathname.toLowerCase();

    // Fallunterscheidung für die Seite: uebungen.html oder skript.html
    for (const [index, eintrag] of aktuelleEinträge.entries()) {
      const aufgabeDiv = await erstelleAufgabe(eintrag, index);

      if (pfad.includes("uebungen.html")) {
        zeigeOderErsetzeAufgabe(aufgabeDiv);
      } else if (pfad.includes("skript.html")) {
        zeigeInSkript(aufgabeDiv);
      } else {
        console.warn("Unbekannte Seite – Aufgabe nicht angezeigt.");
      }
    }
  } catch (err) {
    console.error("Fehler beim Laden der Kompetenzliste:", err);
  }
}

function zeigeOderErsetzeAufgabe(aufgabeDiv) {
  const bestehend = document.getElementById(aufgabeDiv.id);
  if (bestehend) {
    bestehend.replaceWith(aufgabeDiv);
  } else {
    document.querySelector("main").appendChild(aufgabeDiv);
  }
}

function zeigeInSkript(aufgabeDiv) {
  const zielId = aufgabeDiv.id.replace("aufgabe-", "skript-aufgabe-");
  const zielDiv = document.getElementById(zielId);
  if (!zielDiv) return;

  zielDiv.classList.add("aufgabe");

  // Entferne vorher das durch Select2 generierte DOM im Quell-Div
  $(aufgabeDiv).find("select.mch").select2("destroy");

  // Jetzt nur den ursprünglichen HTML-Code übernehmen
  zielDiv.innerHTML = aufgabeDiv.innerHTML;

  // Danach kannst du wieder interaktive Elemente initialisieren
  applyInteractivity(zielDiv);
}

async function erstelleAufgabe(eintrag, index = 0) {
  const aufgabeDiv = document.createElement("div");
  aufgabeDiv.classList.add("aufgabe");
  aufgabeDiv.id = `aufgabe-${index + 1}`;

  const titel = document.createElement("h4");
  titel.textContent = `${index + 1}. Check`;
  aufgabeDiv.appendChild(titel);

  const wrapper = document.createElement("div");
  aufgabeDiv.appendChild(wrapper);
  wrapper.classList.add("wrapper");

  const einleitung = document.createElement("div");
  einleitung.classList.add("einleitung");
  //const titel = document.createElement("h4");
  //titel.textContent = `${index + 1}. Check`;
  //einleitung.appendChild(titel);
  //einleitung.innerHTML = `<h4>Ich kann ${eintrag["Ich kann"]}</h4>`;

  const symbolContainer = document.createElement("div");
  symbolContainer.classList.add("symbolleiste");
  symbolContainer.innerHTML = `<i
            class="fas fa-eye icon eye-icon"
            title="Lösungen anzeigen"
            onclick="toggleAllAnswers(this)"
          ></i>
          <i
            class="fas fa-file-pdf icon pdf-icon"
            title="PDF erstellen"
            onclick="printSingleTask(this)"
          ></i>
          <i
            class="fas fa-redo icon reload-icon"
            title="Neue Aufgabe anzeigen"
            onclick="reloadSingleTask(this)"
          ></i>
          <i
            class="fab fa-whatsapp icon whatapp-icon"
            title="Auf WhatsApp teilen"
            onclick="shareWhatsApp(this)"
          ></i>
           <i
            class="fas fa-copy icon copy-icon"
            title="Als Bild kopieren"
            onclick="kopiereAufgabeAlsBild(this)"
          ></i>
          <i
            class="fa fa-scroll icon skript-icon"
            title="Skriptabschnitt anzeigen"
            onclick="zeigeSkript(this)"
          ></i>`;
  einleitung.appendChild(symbolContainer);

  /* Check-all und Asistenz für später
  <i
            class="fas fa-paper-plane icon check-all-icon"
            title="Alle Fragen abschicken"
            onclick="checkAllQuestions(this)"
          ></i>  
  <i
            class="fas fa-user-graduate icon assistenz-icon"
            title="Assistenz anzeigen"
            onclick="zeigeAssistenz(this)"
          ></i>
  */

  try {
    const responseSammlung = await fetch(`/json/${eintrag["Sammlung"]}.json`);
    const sammlung = await responseSammlung.json();
    const zufall = Math.floor(Math.random() * sammlung.length);
    const aufgabe = sammlung[zufall];

    einleitung.innerHTML += `<p>${aufgabe.einleitung}</p>`;
    wrapper.appendChild(einleitung);

    const ol = document.createElement("ol");
    if (aufgabe.fragen.length === 1) {
      ol.style.listStyleType = "none";
    }

    /*
    aufgabe.fragen.forEach((frage, i) => {
      const li = document.createElement("li");
      if (eintrag["Typ"] === "interaktiv") {
        li.innerHTML = `<span class="frage">${frage}</span><br><span class="antwort-interaktiv">${aufgabe.antworten[i]}</span>`;
      } else {
        li.innerHTML = `<span class="frage">${frage} <i class="fas fa-eye eye-icon icon" onclick="antwortToggle(this)"></i></span><br><span class="antwort-statisch" style="display: none;">${aufgabe.antworten[i]}</span>`;
      }

      //li.innerHTML = `<span class="frage">${frage}</span><br><span class="antwort">${aufgabe.antworten[i]}</span>`;
      ol.appendChild(li);
    });*/

    // Fragen und Antworten gemeinsam verpacken
    let frageAntwortPaare = aufgabe.fragen.map((frage, i) => ({
      frage: frage,
      antwort: aufgabe.antworten[i],
    }));

    // Paare mischen, falls Anktityp = einzeln
    if (eintrag["Ankityp"] === "einzeln") {
      shuffleArray(frageAntwortPaare);
    }

    // Liste dynamisch erstellen
    frageAntwortPaare.forEach((paar) => {
      const li = document.createElement("li");
      if (eintrag["Typ"] === "interaktiv") {
        li.innerHTML = `<span class="frage">${paar.frage}</span><br><span class="antwort-interaktiv">${paar.antwort}</span>`;
      } else {
        li.innerHTML = `<span class="frage">${paar.frage} <i class="fas fa-eye eye-icon icon" onclick="antwortToggle(this)"></i></span><br><span class="antwort-statisch" style="display: none;">${paar.antwort}</span>`;
      }
      ol.appendChild(li);
    });

    wrapper.appendChild(ol);

    if (typeof applyInteractivity === "function") {
      applyInteractivity(aufgabeDiv);
    }

    if (typeof MathJax !== "undefined" && MathJax.typesetPromise) {
      await MathJax.typesetPromise([aufgabeDiv]);
    }

    if (typeof adjustSelect2Width === "function") {
      adjustSelect2Width(`#${aufgabeDiv.id} select.mch`);
    }

    // Listener für Icons hinzufügen
    addCheckIconListeners(aufgabeDiv);
    return aufgabeDiv;
  } catch (err) {
    einleitung.innerHTML += `<p style="color:red;">Fehler beim Laden der Aufgabe.</p>`;
    aufgabeDiv.appendChild(einleitung);
    console.error(
      `Fehler beim Laden der Sammlung für ${eintrag["Sammlung"]}:`,
      err
    );
    return aufgabeDiv;
  }
}

// Funktion zur Umwandlung der Antwort-Platzhalter in Eingabefelder oder Dropdowns
function applyInteractivity(container) {
  container.innerHTML = replaceNumericalWithInteractive(container.innerHTML);
  container.innerHTML = replaceMultipleChoiceWithDropdown(container.innerHTML);
  container.innerHTML = replaceTiktokidWithUrl(container.innerHTML);
  container.innerHTML = replaceYoutubeidWithUrl(container.innerHTML);

  // Initialisiere Select2 für alle Select-Felder
  $(container).find("select.mch").select2({
    placeholder: "Antwort",
    minimumResultsForSearch: Infinity,
    width: "auto",
    dropdownAutoWidth: true,
    templateResult: renderWithMathJax,
    templateSelection: renderWithMathJax,
  });
}

// Ersetze Tiktok-Platzhalter durch URLs
function replaceTiktokidWithUrl(htmlContent) {
  // RegExp für das TikTok-ID-Muster
  const pattern = /\{TIKTOK:id=([A-Za-z0-9_-]+)}/g;

  // Replacer-Funktion mit den richtigen Parametern
  function replacer(match, id) {
    const url = `<i class="fab fa-tiktok clip-icon" title="Clip" onclick="window.open('https://www.tiktok.com/@mathechecks/video/${id}', '_blank')"></i>`;
    return url;
  }
  // Ersetze das Muster im Text
  return htmlContent.replace(pattern, replacer);
}

// Ersetze Youtube-Platzhalter durch URLs
function replaceYoutubeidWithUrl(htmlContent) {
  // RegExp für das TikTok-ID-Muster
  const pattern = /\{YOUTUBE:id=([A-Za-z0-9_-]+)}/g;

  // Replacer-Funktion mit den richtigen Parametern
  function replacer(match, id) {
    const url = `<i class="fab fa-youtube clip-icon" title="Clip" onclick="window.open('https://youtube.com/shorts/${id}', '_blank')"></i>`;
    return url;
  }
  // Ersetze das Muster im Text
  //return htmlContent.replace(pattern, replacer);
  // aktuell keine Youtube-Verlinkung
  return htmlContent.replace(pattern, "");
}

// Ersetze numerische Aufgaben mit interaktiven Eingabefeldern
function replaceNumericalWithInteractive(htmlContent) {
  const pattern = /\{\d+:NUMERICAL:=(-?[0-9.,]+):([0-9.,]+)\}/g;
  function replacer(match, correctAnswer, tolerance) {
    const interactiveHtml = `
            <input type="text" id="answer${questionId}" placeholder="Antwort" autocomplete="off" aria-label="Frage ${questionId}" data-correct-answer="${correctAnswer.replace(
      ",",
      "."
    )}" data-tolerance="${tolerance.replace(",", ".")}">
            <i class="fas fa-paper-plane check-icon icon " title="Frage abschicken" onclick="checkNumericalAnswer(${questionId}, ${correctAnswer.replace(
      ",",
      "."
    )}, ${tolerance.replace(",", ".")})"></i>
            <span id="feedback${questionId}"></span>
        `;
    questionId++; // Eindeutige ID für jede Frage
    return interactiveHtml;
  }
  return htmlContent.replace(pattern, replacer);
}

// Ersetze Multiple-Choice-Fragen mit Dropdowns
function replaceMultipleChoiceWithDropdown(htmlContent) {
  const result = [];
  let index = 0;

  while (index < htmlContent.length) {
    const start = htmlContent.indexOf("{", index);

    // Kein weiterer Platzhalter
    if (start === -1) {
      result.push(htmlContent.slice(index));
      break;
    }

    // Prüfe, ob es ein MC-Platzhalter ist
    const pre = htmlContent.slice(index, start);
    const maybeMC = htmlContent.slice(start);

    const mcMatch = maybeMC.match(/^\{(\d+):MC:/);
    if (!mcMatch) {
      result.push(pre + "{");
      index = start + 1;
      continue;
    }

    // Suche balanciertes Ende
    let braceLevel = 1;
    let end = start + 1;
    while (end < htmlContent.length && braceLevel > 0) {
      if (htmlContent[end] === "{") braceLevel++;
      if (htmlContent[end] === "}") braceLevel--;
      end++;
    }

    const fullMatch = htmlContent.slice(start, end);
    const innerContent = fullMatch.replace(/^\{\d+:MC:/, "").slice(0, -1); // Nur das Innere

    // Verarbeite Optionen
    const options = innerContent.split(/(?<!\\)~/); // `~` als Trenner, kein Escaping davor
    const correctOption = options.find((opt) => opt.startsWith("="));
    const correctAnswer = correctOption
      ? correctOption.substring(1).trim()
      : null;

    const optionsHtml = options
      .map((option) => {
        const isCorrect = option.startsWith("=");
        const trimmed = isCorrect ? option.substring(1).trim() : option.trim();
        return `<option value="${trimmed}" data-html="${trimmed}">${trimmed}</option>`;
      })
      .join("");

    const selectHtml = `
            <div style="margin-top: 10px;display: inline">
            <select id="answer${questionId}" class="mch" aria-label="Multiple Choice Frage ${questionId}" data-correct-answer="${correctAnswer}">
                ${optionsHtml}
            </select>
            <i class="fas fa-paper-plane check-icon icon" onclick="checkMultipleChoiceAnswer(${questionId})"></i>
            <span id="feedback${questionId}"></span>
            </div>
        `;

    result.push(pre + selectHtml);
    index = end;
    questionId++;
  }

  return result.join("");
}

// Hilfsfunktion zum Mischen eines Arrays (Fisher-Yates-Algorithmus)
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

// Funktion, um Breite der Select2 Options anzupassen
function adjustSelect2Width(selectElementSelector) {
  const $select2 = $(selectElementSelector);
  const $select2Container = $select2.next(".select2-container");
  let maxWidth = 0;

  $select2.find("option").each(function () {
    const optionText = $(this).text();
    const tempSpan = $("<span>").text(optionText).appendTo("body");
    maxWidth = Math.max(maxWidth, tempSpan.width());
    tempSpan.remove();
  });

  $select2Container.width(maxWidth + 30);
}

// Funktion zur Darstellung mit gerendertem LaTeX
function renderWithMathJax(data) {
  if (!data.element) return data.text;

  const latexHtml = data.element.getAttribute("data-html") || data.text;
  const span = document.createElement("span");
  span.innerHTML = latexHtml;

  MathJax.typesetPromise([span]).catch((err) => {
    console.error("MathJax Error:", err);
  });

  return span;
}

function scrollZuHash(hash) {
  if (!hash.startsWith("#")) {
    hash = "#" + hash;
  }
  const zielElement = document.querySelector(hash);
  if (!zielElement) {
    console.warn("Ziel-Element nicht gefunden für Hash:", hash);
    return;
  }

  const header = document.querySelector("header");
  const headerHeight = header ? header.offsetHeight : 0;

  let scrollZiel = zielElement;

  const y =
    scrollZiel.getBoundingClientRect().top + window.pageYOffset - headerHeight;

  window.scrollTo({ top: y, behavior: "smooth" });
}

/*Zzz
function highlightElement(element) {
  element.classList.add("highlight-border");
  setTimeout(() => {
    element.classList.remove("highlight-border");
  }, 1500);
}

  // scroll Ziel entweder hash oder nächstes H2-Element
  /*if (window.location.pathname.includes("skript")) {
    const h2 = findeNaechstenH2Ueber(zielElement);
   
    if (h2) scrollZiel = h2;
  }

function findeNaechstenH2Ueber(element) {
  let current = element.previousElementSibling;
  while (current) {
    if (current.tagName === "H2") return current;
    current = current.previousElementSibling;
  }

  return null;
}
*/
