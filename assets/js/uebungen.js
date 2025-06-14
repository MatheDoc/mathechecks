let questionId;

// Einmal beim Laden aufrufen
async function ladeAufgabenFürLernbereich(lernbereich) {
  // Funktion ist jetzt async
  // Holt die Kompetenzliste aus der JSON-Datei
  try {
    const responseKompetenzliste = await fetch("/kompetenzliste.json"); // Auf fetch warten
    const daten = await responseKompetenzliste.json(); // Auf JSON-Parsen warten

    // Filtert die Daten basierend auf dem übergebenen Lernbereich
    const gefiltert = daten.filter(
      (eintrag) => eintrag.Lernbereich === lernbereich
    );

    // Iteriert über jedes gefilterte Element und erstellt eine Aufgabe
    // Verwenden von for...of, um async/await in der Schleife zu ermöglichen
    for (const [index, eintrag] of gefiltert.entries()) {
      const aufgabeDiv = document.createElement("div"); // Erstellt ein div-Element für die Aufgabe
      aufgabeDiv.classList.add("aufgabe"); // Fügt die Klasse "aufgabe" hinzu
      aufgabeDiv.id = `aufgabe-${index + 1}`; // Setzt die ID der Aufgabe

      // Titel der Aufgabe
      const titel = document.createElement("h3"); // Erstellt ein h3-Element für den Titel
      titel.textContent = `${index + 1}. Aufgabe`; // Setzt den Text des Titels
      aufgabeDiv.appendChild(titel); // Fügt den Titel zum Aufgaben-Div hinzu

      const wrapper = document.createElement("div"); // Erstellt ein Wrapper-Div
      aufgabeDiv.appendChild(wrapper); // Fügt den Wrapper zum Aufgaben-Div hinzu

      // Einleitung
      const einleitung = document.createElement("div"); // Erstellt ein div-Element für die Einleitung
      einleitung.classList.add("einleitung"); // Fügt die Klasse "einleitung" hinzu
      einleitung.innerHTML = `<h4>Ich kann ${eintrag["Ich kann"]}</h4>`; // Fügt den "Ich kann"-Text hinzu

      // Symbolleiste
      const symbolContainer = document.createElement("div"); // Erstellt ein Container-Div für die Symbole
      symbolContainer.classList.add("symbolleiste");
      symbolContainer.innerHTML = `<i
            class="fas fa-paper-plane icon check-all-icon"
            title="Alle Fragen abschicken"
            onclick="checkAllQuestions(this)"
          ></i>
          <i
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
            class="fas fa-user-graduate icon assistenz-icon"
            title="Assistenz anzeigen"
            onclick="zeigeAssistenz(this)"
          ></i>`;
      einleitung.appendChild(symbolContainer);
      try {
        // Holt die Aufgabensammlung aus der angegebenen URL
        // Der Pfad wurde hier aktualisiert, um "json/" voranzustellen und ".json" anzuhängen
        const responseSammlung = await fetch(
          `/json/${eintrag["Sammlung"]}.json`
        ); // Auf fetch warten
        const sammlung = await responseSammlung.json(); // Auf JSON-Parsen warten

        const zufall = Math.floor(Math.random() * sammlung.length); // Wählt eine zufällige Aufgabe aus der Sammlung
        const aufgabe = sammlung[zufall]; // Die ausgewählte Aufgabe

        einleitung.innerHTML += `<p>${aufgabe.einleitung}</p>`; // Fügt die Einleitung der Aufgabe hinzu
        wrapper.appendChild(einleitung); // Fügt die Einleitung zum Aufgaben-Div hinzu

        // Fragen und Antworten
        const ol = document.createElement("ol"); // Erstellt eine geordnete Liste für Fragen/Antworten
        ol.setAttribute("aria-label", ""); // Setzt das aria-label-Attribut
        if (aufgabe.fragen.length === 1) {
          ol.style.listStyleType = "none"; // Entfernt die Aufzählungszeichen, wenn nur eine Frage vorhanden ist
        }

        // Iteriert über jede Frage und Antwort und fügt sie zur Liste hinzu
        aufgabe.fragen.forEach((frage, i) => {
          const li = document.createElement("li"); // Erstellt ein Listenelement
          li.innerHTML = `<span class="frage">${frage}</span><br><span class="antwort">${aufgabe.antworten[i]}</span>`; // Fügt Frage und Antwort hinzu
          ol.appendChild(li); // Fügt das Listenelement zur Liste hinzu
        });

        wrapper.appendChild(ol); // Fügt die Liste zum Aufgaben-Div hinzu

        // In den Hauptbereich einfügen
        // Stellt Interaktivität für das Aufgaben-Div her (Funktion muss definiert sein)
        if (typeof applyInteractivity === "function") {
          applyInteractivity(aufgabeDiv);
        } else {
          console.warn("Funktion 'applyInteractivity' ist nicht definiert.");
        }

        document.querySelector("main").appendChild(aufgabeDiv); // Fügt das Aufgaben-Div zum 'main'-Element hinzu

        // MathJax & Select2, falls verwendet:
        // Überprüft, ob MathJax verfügbar ist und verarbeitet mathematische Ausdrücke
        if (typeof MathJax !== "undefined" && MathJax.typesetPromise) {
          MathJax.typesetPromise([aufgabeDiv]);
        } else {
          console.warn(
            "MathJax ist nicht geladen oder MathJax.typesetPromise ist nicht verfügbar."
          );
        }

        // Initialisiert Select2 für die Dropdown-Elemente
        const $select = $(`#${aufgabeDiv.id} select.mch`);
        if ($select.length) {
          $select.select2({
            placeholder: "Antwort",
            minimumResultsForSearch: Infinity,
            width: "auto",
            dropdownAutoWidth: true,
            templateResult: renderWithMathJax,
            templateSelection: renderWithMathJax,
          });
          // Passt die Breite des Select2-Elements an (Funktion muss definiert sein)
          if (typeof adjustSelect2Width === "function") {
            adjustSelect2Width(`#${aufgabeDiv.id} select.mch`);
          } else {
            console.warn("Funktion 'adjustSelect2Width' ist nicht definiert.");
          }
        }
      } catch (err) {
        // Fehlerbehandlung beim Laden der Sammlung
        einleitung.innerHTML += `<p style="color:red;">Fehler beim Laden der Aufgabe.</p>`;
        console.error(
          `Fehler beim Laden der Sammlung für ${eintrag["Sammlung"]}:`,
          err
        );
        aufgabeDiv.appendChild(einleitung);
        document.querySelector("main").appendChild(aufgabeDiv);
      }
    }
  } catch (err) {
    // Fehlerbehandlung beim Laden der Kompetenzliste
    console.error("Fehler beim Laden der Kompetenzliste:", err);
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

  // Select2 Breite anpassen
  adjustSelect2Width(`#${container.id} select.mch`);
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
  return htmlContent.replace(pattern, replacer);
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
            <i class="fas fa-paper-plane check-icon " title="Frage abschicken" onclick="checkNumericalAnswer(${questionId}, ${correctAnswer.replace(
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
            <div style="margin-top: 10px;">
            <select id="answer${questionId}" class="mch" aria-label="Multiple Choice Frage ${questionId}" data-correct-answer="${correctAnswer}">
                ${optionsHtml}
            </select>
            <i class="fas fa-paper-plane check-icon" onclick="checkMultipleChoiceAnswer(${questionId})"></i>
            <span id="feedback${questionId}"></span>
            </div>
        `;

    result.push(pre + selectHtml);
    index = end;
    questionId++;
  }

  return result.join("");
}

// Funktion zum Zufällig-Mischen eines Arrays (Fisher-Yates Shuffle)
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]]; // Tauschen der Elemente
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

ladeAufgabenFürLernbereich(lernbereich);
