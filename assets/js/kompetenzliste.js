fetch("/kompetenzliste.json")
  .then((response) => response.json())
  .then((daten) => {
    const tbody = document.getElementById("tabellenkoerper");
    const gefiltert = daten.filter(
      (eintrag) => eintrag.Lernbereich === lernbereich
    );

    gefiltert.forEach((eintrag) => {
      const zeile = document.createElement("tr");
      zeile.innerHTML = `<td>${eintrag["Ich kann"]}</td>`;
      tbody.appendChild(zeile);
    });
  });
