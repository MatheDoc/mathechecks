let aufgabenZaehler = 1; // Initialisiere den Zähler für die Aufgaben
let questionId = 1; // Eindeutige Frage-ID für jede Aufgabe

let aktuelleEinträge = []; // global
let aktuellerLernbereich = ""; // global
let persistenzPausiert = false;

const AUFGABEN_STATE_PREFIX = "aufgaben-zustand-v1";
const AUFGABEN_STATE_VERSION = 2;

function erzeugeLeerenAufgabenState() {
  return {
    version: AUFGABEN_STATE_VERSION,
    tasks: {},
  };
}

function migriereTaskState(taskState) {
  const migriert = {
    selectedTaskIndex:
      Number.isInteger(taskState?.selectedTaskIndex)
        ? taskState.selectedTaskIndex
        : null,
    shuffleOrder: Array.isArray(taskState?.shuffleOrder)
      ? taskState.shuffleOrder
      : null,
    feedbackByKey: {},
    solutionsVisible: Boolean(taskState?.solutionsVisible),
  };

  if (taskState?.feedbackByKey && typeof taskState.feedbackByKey === "object") {
    migriert.feedbackByKey = { ...taskState.feedbackByKey };
  }

  if (
    Object.keys(migriert.feedbackByKey).length === 0 &&
    Array.isArray(taskState?.responses)
  ) {
    taskState.responses.forEach((response) => {
      if (!response?.key) return;
      migriert.feedbackByKey[response.key] = {
        value: response.value ?? "",
        feedbackHtml: response.feedbackHtml ?? "",
        feedbackColor: response.feedbackColor ?? "",
        feedbackOpacity: response.feedbackOpacity ?? "",
      };
    });
  }

  return migriert;
}

function migriereAufgabenState(state) {
  const basis =
    state && typeof state === "object" ? state : erzeugeLeerenAufgabenState();

  const tasksQuelle =
    basis.tasks && typeof basis.tasks === "object" ? basis.tasks : {};

  const tasks = {};
  Object.entries(tasksQuelle).forEach(([index, taskState]) => {
    tasks[index] = migriereTaskState(taskState);
  });

  return {
    version: AUFGABEN_STATE_VERSION,
    tasks,
  };
}

function istUebungenSeite() {
  const pfad = window.location.pathname.toLowerCase();
  return (
    pfad.includes("/uebungen") ||
    pfad.includes("/übungen") ||
    pfad.includes("uebungen.html") ||
    pfad.includes("übungen.html")
  );
}

function istSkriptSeite() {
  const pfad = window.location.pathname.toLowerCase();
  return pfad.includes("/skript") || pfad.includes("skript.html");
}

function holeStorageKey() {
  const lernbereich = aktuellerLernbereich || window.lernbereich || "default";
  return `${AUFGABEN_STATE_PREFIX}:${lernbereich}`;
}

function ladeAufgabenState() {
  try {
    const storageKey = holeStorageKey();
    const raw = localStorage.getItem(storageKey);
    if (!raw) return erzeugeLeerenAufgabenState();
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") {
      return erzeugeLeerenAufgabenState();
    }

    const migriert = migriereAufgabenState(parsed);
    if (
      parsed.version !== AUFGABEN_STATE_VERSION ||
      JSON.stringify(parsed) !== JSON.stringify(migriert)
    ) {
      localStorage.setItem(storageKey, JSON.stringify(migriert));
    }

    return migriert;
  } catch (error) {
    console.warn("Aufgaben-Zustand konnte nicht gelesen werden:", error);
    return erzeugeLeerenAufgabenState();
  }
}

function speichereAufgabenState(state) {
  try {
    localStorage.setItem(holeStorageKey(), JSON.stringify(state));
  } catch (error) {
    console.warn("Aufgaben-Zustand konnte nicht gespeichert werden:", error);
  }
}

function holeTaskState(index) {
  const state = ladeAufgabenState();
  return state.tasks?.[index] || null;
}

function aktualisiereTaskState(index, updater) {
  const state = ladeAufgabenState();
  if (!state.tasks[index]) {
    state.tasks[index] = {};
  }
  updater(state.tasks[index]);
  speichereAufgabenState(state);
}

function parseTaskIndex(aufgabeDiv) {
  if (!aufgabeDiv?.id) return null;
  const id = aufgabeDiv.id;
  if (!id.startsWith("aufgabe-")) return null;
  const index = parseInt(id.split("-").pop(), 10) - 1;
  return Number.isNaN(index) ? null : index;
}

function setzeAufgabenIndexZurueck(index) {
  aktualisiereTaskState(index, (taskState) => {
    taskState.selectedTaskIndex = null;
    taskState.shuffleOrder = null;
    taskState.feedbackByKey = {};
    taskState.solutionsVisible = false;
  });
}

function holeControlKey(control) {
  const li = control.closest("li");
  const frageKey = li?.dataset?.frageKey || "";
  const controlsInLi = li
    ? Array.from(li.querySelectorAll('input[id^="answer"], select.mch'))
    : [];
  const indexInLi = controlsInLi.indexOf(control);
  const typ = control.tagName === "SELECT" ? "select" : "input";
  return `${frageKey}||${typ}||${indexInLi}`;
}

function holeFeedbackElementZuControl(control) {
  if (!control) return null;
  const questionId = control.id.replace("answer", "");
  const aufgabeDiv = control.closest(".aufgabe");
  if (!aufgabeDiv) return null;
  return aufgabeDiv.querySelector(`[id="feedback${questionId}"]`);
}

function speichereGerendertenTaskZustand(aufgabeDiv) {
  if (persistenzPausiert) return;

  const index = parseTaskIndex(aufgabeDiv);
  if (index === null) return;

  const controls = Array.from(
    aufgabeDiv.querySelectorAll('input[id^="answer"], select.mch')
  );

  const eyeIcon = aufgabeDiv.querySelector(".symbolleiste .eye-icon");
  const solutionsVisible = !!eyeIcon?.classList.contains("fa-eye-slash");

  const feedbackByKey = {};
  controls.forEach((control) => {
    const feedback = holeFeedbackElementZuControl(control);
    const key = holeControlKey(control);
    if (key) {
      feedbackByKey[key] = {
        value: control.value ?? "",
        feedbackHtml: feedback ? feedback.innerHTML : "",
        feedbackColor: feedback ? feedback.style.color || "" : "",
        feedbackOpacity: feedback ? feedback.style.opacity || "" : "",
      };
    }
  });

  aktualisiereTaskState(index, (taskState) => {
    taskState.feedbackByKey = feedbackByKey;
    taskState.solutionsVisible = solutionsVisible;
  });
}

function stelleGerendertenTaskZustandWiederHer(aufgabeDiv, index) {
  const taskState = holeTaskState(index);
  if (!taskState) return;

  const controls = Array.from(
    aufgabeDiv.querySelectorAll('input[id^="answer"], select.mch')
  );

  const gespeichertesFeedbackByKey = taskState.feedbackByKey || {};

  controls.forEach((control) => {
    const key = holeControlKey(control);
    const response = gespeichertesFeedbackByKey[key];
    if (!response) return;

    if (response.value !== undefined) {
      control.value = response.value;
      if (control.tagName === "SELECT") {
        $(control).val(response.value).trigger("change");
      }
    }

    const feedback = holeFeedbackElementZuControl(control);
    if (feedback) {
      feedback.innerHTML = response.feedbackHtml || "";
      feedback.style.color = response.feedbackColor || "";
      feedback.style.opacity = response.feedbackOpacity || "";
      if (feedback.innerHTML && typeof MathJax !== "undefined") {
        MathJax.typesetPromise([feedback]);
      }
    }
  });

  if (taskState.solutionsVisible) {
    const eyeIcon = aufgabeDiv.querySelector(".symbolleiste .eye-icon");
    if (eyeIcon && !eyeIcon.classList.contains("fa-eye-slash")) {
      toggleAllAnswers(eyeIcon);
    }
  }
}

function initialisiereAufgabenStateSync() {
  document.addEventListener("input", (event) => {
    const target = event.target;
    if (!target.matches('input[id^="answer"]')) return;
    const aufgabeDiv = target.closest(".aufgabe");
    if (!aufgabeDiv) return;
    speichereGerendertenTaskZustand(aufgabeDiv);
  });

  document.addEventListener("change", (event) => {
    const target = event.target;
    if (!target.matches("select.mch")) return;
    const aufgabeDiv = target.closest(".aufgabe");
    if (!aufgabeDiv) return;
    speichereGerendertenTaskZustand(aufgabeDiv);
  });

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest(
      ".check-icon, .eye-icon, .check-all-icon"
    );
    if (!trigger) return;
    const aufgabeDiv = trigger.closest(".aufgabe");
    if (!aufgabeDiv) return;

    setTimeout(() => {
      speichereGerendertenTaskZustand(aufgabeDiv);
    }, 0);
  });
}

initialisiereAufgabenStateSync();

async function ladeAufgabenFürLernbereich(lernbereich) {
  try {
    if (!istUebungenSeite() && !istSkriptSeite()) {
      return;
    }

    aktuellerLernbereich = lernbereich;
    const responseKompetenzliste = await fetch("/kompetenzliste.json"); // Liquid wird nicht in js aufgelöst, daher ohne relative_url;
    const daten = await responseKompetenzliste.json();

    aktuelleEinträge = daten.filter(
      (eintrag) => eintrag.Lernbereich === lernbereich
    );

    for (const [index, eintrag] of aktuelleEinträge.entries()) {
      const aufgabeDiv = await erstelleAufgabe(eintrag, index);
      zeigeOderErsetzeAufgabe(aufgabeDiv);
    }
  } catch (err) {
    console.error("Fehler beim Laden der Kompetenzliste:", err);
  }
}

function zeigeOderErsetzeAufgabe(aufgabeDiv) {
  const bestehend = document.getElementById(aufgabeDiv.id);
  if (bestehend) {
    bestehend.replaceWith(aufgabeDiv);
    return;
  }

  if (istSkriptSeite()) {
    const index = parseTaskIndex(aufgabeDiv);
    if (index === null) return;

    const findeEinfuegeAnker = (element) => {
      if (!element) return null;
      const listenpunkt = element.closest("li");
      return listenpunkt || element;
    };

    const infoBlock = document.getElementById(`check-${index + 1}`);
    if (infoBlock) {
      const anker = findeEinfuegeAnker(infoBlock);
      anker.insertAdjacentElement("afterend", aufgabeDiv);
      return;
    }

    const alleInfoBloecke = document.querySelectorAll('[id^="check-"].info');
    if (alleInfoBloecke[index]) {
      const anker = findeEinfuegeAnker(alleInfoBloecke[index]);
      anker.insertAdjacentElement("afterend", aufgabeDiv);
      return;
    }

    document.querySelector("main").appendChild(aufgabeDiv);
    return;
  }

  document.querySelector("main").appendChild(aufgabeDiv);
}

async function erstelleAufgabe(eintrag, index = 0, options = {}) {
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
  const istSkript = istSkriptSeite();
  const sprungIconClass = istSkript ? "fa-pen-to-square" : "fa-scroll";
  const sprungTitle = istSkript
    ? "Zum passenden Training"
    : "Skriptabschnitt anzeigen";
  const sprungOnclick = istSkript ? "zeigeTraining(this)" : "zeigeSkript(this)";
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
            class="fa ${sprungIconClass} icon skript-icon"
            title="${sprungTitle}"
            onclick="${sprungOnclick}"
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
    persistenzPausiert = true;

    const responseSammlung = await fetch(`/json/${eintrag["Sammlung"]}.json`);
    const sammlung = await responseSammlung.json();

    let zufall;
    const gespeicherterState = holeTaskState(index);
    const gespeicherterIndex = gespeicherterState?.selectedTaskIndex;
    const hatGueltigenGespeichertenIndex =
      Number.isInteger(gespeicherterIndex) &&
      gespeicherterIndex >= 0 &&
      gespeicherterIndex < sammlung.length;

    if (!options.erzwingeNeu && hatGueltigenGespeichertenIndex) {
      zufall = gespeicherterIndex;
    } else {
      zufall = Math.floor(Math.random() * sammlung.length);
    }

    aktualisiereTaskState(index, (taskState) => {
      taskState.selectedTaskIndex = zufall;
      if (options.erzwingeNeu) {
        taskState.shuffleOrder = null;
        taskState.solutionsVisible = false;
        taskState.feedbackByKey = {};
      }
    });

    const aufgabe = sammlung[zufall];

    einleitung.innerHTML += `<p>${aufgabe.einleitung}</p>`;
    wrapper.appendChild(einleitung);

    const ol = document.createElement("ol");
    if (aufgabe.fragen.length === 1) {
      ol.style.listStyleType = "none";
    }

    // Fragen und Antworten gemeinsam verpacken
    let frageAntwortPaare = aufgabe.fragen.map((frage, i) => ({
      frage: frage,
      antwort: aufgabe.antworten[i],
      originalIndex: i,
    }));

    // Paare mischen, falls Anktityp = einzeln
    if (eintrag["Ankityp"] === "einzeln") {
      const gespeicherteReihenfolge = gespeicherterState?.shuffleOrder;
      const istGueltigeReihenfolge =
        Array.isArray(gespeicherteReihenfolge) &&
        gespeicherteReihenfolge.length === frageAntwortPaare.length &&
        new Set(gespeicherteReihenfolge).size === frageAntwortPaare.length;

      if (istGueltigeReihenfolge) {
        const indexMap = new Map(
          frageAntwortPaare.map((paar) => [paar.originalIndex, paar])
        );
        frageAntwortPaare = gespeicherteReihenfolge
          .map((originalIndex) => indexMap.get(originalIndex))
          .filter(Boolean);
      } else {
        shuffleArray(frageAntwortPaare);
        aktualisiereTaskState(index, (taskState) => {
          taskState.shuffleOrder = frageAntwortPaare.map(
            (paar) => paar.originalIndex
          );
        });
      }
    }

    // Liste dynamisch erstellen
    frageAntwortPaare.forEach((paar) => {
      const li = document.createElement("li");
      li.dataset.frageKey = String(paar.originalIndex);
      li.innerHTML = `<span class="frage">${paar.frage}</span><br><span class="antwort-interaktiv">${paar.antwort}</span>`;
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

    stelleGerendertenTaskZustandWiederHer(aufgabeDiv, index);

    persistenzPausiert = false;

    return aufgabeDiv;
  } catch (err) {
    persistenzPausiert = false;

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

  // Füge Enter-Listener zu allen Input-Feldern hinzu
  const inputs = container.querySelectorAll('input[id^="answer"]');
  inputs.forEach(input => {
    input.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        const checkIcon = input.nextElementSibling;
        if (checkIcon && checkIcon.classList.contains('check-icon')) {
          checkIcon.click();
        }
      }
    });
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
