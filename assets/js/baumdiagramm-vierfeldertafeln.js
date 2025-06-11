
 // Event-Handler für Inputs
      function updateFromInputs() {
        const pa = parseFloat(document.getElementById("paSlider").value);
        const pba = parseFloat(document.getElementById("pbaSlider").value);
        const pbna = parseFloat(document.getElementById("pbnaSlider").value);

        document.getElementById("paWert").innerText = pa.toFixed(2);
        document.getElementById("pbaWert").innerText = pba.toFixed(2);
        document.getElementById("pbnaWert").innerText = pbna.toFixed(2);

        zeichneBaumdiagramm(pa, pba, pbna, "baum", "Baumdiagramm");
        const pb = pa * pba + (1 - pa) * pbna;
        const pab = (pa * pba) / pb;
        const panb = (pa * (1 - pba)) / (1 - pb);
        zeichneBaumdiagramm(
          pb,
          pab,
          panb,
          "invers",
          "Inverses Baumdiagramm",
          "B",
          "B\u0305",
          "A",
          "A\u0305"
        );

        // Vierfeldertafel berechnen
        const a_b = pa * pba;
        const a_nb = pa * (1 - pba);
        const na_b = (1 - pa) * pbna;
        const na_nb = (1 - pa) * (1 - pbna);

        // Zellen füllen
        document.getElementById("cell_a_b").innerText = a_b
          .toFixed(4)
          .replace(".", ",");
        document.getElementById("cell_a_nb").innerText = a_nb
          .toFixed(4)
          .replace(".", ",");
        document.getElementById("cell_na_b").innerText = na_b
          .toFixed(4)
          .replace(".", ",");
        document.getElementById("cell_na_nb").innerText = na_nb
          .toFixed(4)
          .replace(".", ",");

        // Randsummen
        document.getElementById("cell_a_sum").innerText = (a_b + a_nb)
          .toFixed(2)
          .replace(".", ",");
        document.getElementById("cell_na_sum").innerText = (na_b + na_nb)
          .toFixed(2)
          .replace(".", ",");
        document.getElementById("cell_sum_b").innerText = (a_b + na_b)
          .toFixed(2)
          .replace(".", ",");
        document.getElementById("cell_sum_nb").innerText = (a_nb + na_nb)
          .toFixed(2)
          .replace(".", ",");
        document.getElementById("cell_sum_sum").innerText = "1";

        // Unabhängigkeitstext aktualisieren
        const unabhaengig = Math.abs(pba - pbna) < 1e-6;
        document.getElementById("unabhaengigkeitText").innerText = unabhaengig
          ? "unabhängig."
          : "abhängig.";
      }

      // Inputs mit Handler verbinden
      document
        .getElementById("paSlider")
        .addEventListener("input", updateFromInputs);
      document
        .getElementById("pbaSlider")
        .addEventListener("input", updateFromInputs);
      document
        .getElementById("pbnaSlider")
        .addEventListener("input", updateFromInputs);

      // Mausradsteuerung für alle Slider aktivieren
      ["paSlider", "pbaSlider", "pbnaSlider"].forEach((id) => {
        const slider = document.getElementById(id);
        slider.addEventListener("wheel", function (e) {
          e.preventDefault();
          const step = parseFloat(slider.step) || 0.01;
          let value = parseFloat(slider.value);
          if (e.deltaY < 0) {
            value = Math.min(parseFloat(slider.max), value + step);
          } else {
            value = Math.max(parseFloat(slider.min), value - step);
          }
          slider.value = value.toFixed(2);
          slider.dispatchEvent(new Event("input"));
        });
      });

      // Initiales Diagramm
      updateFromInputs();
