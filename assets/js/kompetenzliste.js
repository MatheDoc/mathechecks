// This script fetches a JSON file containing competencies and filters them based on the selected learning area.

fetch("/kompetenzliste.json") // Liquid wird nicht in js aufgelöst, daher ohne relative_url
  .then((response) => response.json())
  .then((daten) => {
    const tbody = document.getElementById("tabellenkoerper");
    const gefiltert = daten.filter(
      (eintrag) => eintrag.Lernbereich === lernbereich
    );

    gefiltert.forEach((eintrag, index) => {
      const uebungUrl = `uebungen.html#aufgabe-${index + 1}`;
      const zeile = document.createElement("tr");
      zeile.innerHTML = `<td>${index + 1}</td>
      <td>
      ${eintrag["Ich kann"]}
       <i class="fas fa-edit" style="color: var(--hauptfarbe);" title="Training starten" onclick="window.location.href='${uebungUrl}'"></i>
      </td>`;
      tbody.appendChild(zeile);
    });
  });

// Muss noch entfernt / überarbeitet werden
function addButtons() {
  table.rows().every(function (rowIdx) {
    var data = this.data();
    var ichKannText = data[5];
    var aufgaben = data[6];
    var infoButton =
      '<i class="fas fa-info-circle icon info-icon" id="infoIcon" title="Info anzeigen"></i>';
    // var copyButton =  '<i class="fas fa-copy copy-icon" id="copyIcon" title="Prompt kopieren"></i>';
    var xmlButton =
      '<i class="fas fa-file-code icon xml-icon" id="xmlIcon" title="als Moodle-XML exportieren"></i>';
    var testButton =
      '<i class="fas fa-edit icon test-icon" id="testIcon" title="Einzeltest starten"></i>';
    // Testbutoon ausblenden, falls kein Test vorhanden
    if (aufgaben === "") {
      testButton = " ";
      xmlButton = " ";
    }
    // Infobutoon ausblenden, falls keine Info vorhanden
    if (data[7] === "") {
      infoButton = " ";
    }
    // xml-button ausblenden wenn listonly
    const urlParams = new URLSearchParams(window.location.search);
    const listonly = urlParams.get("listonly");
    if (listonly) {
      xmlButton = " ";
    }
    // xmlButton ausblenden für: Venn
    if (data[8] === "187" || data[8] === "188") {
      xmlButton = " ";
    }

    table
      .cell(rowIdx, 5)
      .data(
        ichKannText + " " + infoButton + " " + xmlButton + " " + testButton
      );
  });
}
