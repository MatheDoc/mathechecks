---
layout: shell
title: "Konzept"
description: "Die Lernarchitektur von MatheChecks: Check-Ketten aus Training, Recall, Feynman und Kompetenzliste, Erfolgsquoten, KI-Rückmeldung mit vorbereitetem Kontext und Spaced Repetition."
permalink: /konzept.html
body_class: page-legal page-static-narrow page-konzept
page_css: /assets/css/info-pages.css?v=20260817-h1-margin
show_footer: true
---

# Idee

Mit MatheChecks entwickle ich eine moderne Lernplattform, die digitale Möglichkeiten gezielt für den Lernprozess nutzt. Die Plattform stützt sich auf gut belegte Erkenntnisse der Lernpsychologie: Lernen gelingt besser durch aktive Auseinandersetzung statt passives Lesen, durch formatives Feedback, durch Wiederholung in wachsenden Abständen und durch das Erleben der eigenen Kompetenz. Diese Prinzipien sind bei MatheChecks nicht nachträglich aufgesetzt, sondern bestimmen den Aufbau der Plattform von Grund auf.



# Inhalt

MatheChecks deckt aktuell Teile des Mathematikstoffs der Sekundarstufe II ab, von der Analysis über die Stochastik bis zur Linearen Algebra.

Die Inhalte gliedern sich in [Lernbereiche]({{ '/material.html' | relative_url }}). Ein Lernbereich besteht aus mehreren Checks, die didaktisch sinnvoll aufeinander aufbauen. Zu jedem Check gehören Aktivitäten, die unterschiedliche kognitive Prozesse ansprechen: Aufgaben rechnen, Kernpunkte aus dem Gedächtnis abrufen und Zusammenhänge mit eigenen Worten erklären.

Ergänzend zu den Check-Aktivitäten begleiten drei weitere Module jeden Lernbereich:

<div class="konzept-cards">
    <article class="konzept-card" style="--kc-color: var(--mt-start, #245f43)">
        <h3>Start</h3>
        <p>Ziele, Voraussetzungen und der empfohlene Lernpfad geben Orientierung für den Einstieg in den Lernbereich.</p>
    </article>
    <article class="konzept-card" style="--kc-color: var(--mt-skript, #4ade80)">
        <h3>Skript</h3>
        <p>Die Inhalte des Lernbereichs zusammengefasst und vertieft, mit Beispielen und interaktiven Widgets zum Ausprobieren.</p>
    </article>
    <article class="konzept-card" style="--kc-color: var(--mt-flashcards, #f472b6)">
        <h3>Flashcards</h3>
        <p>Zentrale Begriffe und Verfahren gezielt wiederholen, damit das Gelernte langfristig im Gedächtnis bleibt.</p>
    </article>
</div>

Ich baue MatheChecks so, wie ich es mir für meine eigenen Kurse wünsche. Dadurch liegt ein Schwerpunkt aktuell auf dem beruflichen Gymnasium in NRW, Fachbereich Wirtschaft und Verwaltung.


# Feed

Nach der Registrierung stellst du dir eine individuelle Lernsession zusammen, die aus Lernbereichen und Checks deiner Wahl besteht. MatheChecks führt dich anschließend über einen intelligenten Feed durch deine Session und zeigt dir dabei, wie du dich entwickelst. So entsteht mit der Zeit ein verlässlicher Überblick über den eigenen Lernstand und die eigene Kompetenzentwicklung.

## Die Check-Kette

Jeder Check durchläuft eine Kette aus vier Aktivitäten: Training, Recall, Feynman und Kompetenzliste.

<div class="konzept-cards">
    <article class="konzept-card" style="--kc-color: var(--mt-training, #2f7fe6)">
        <h3>Training</h3>
        <p>Interaktive Aufgaben zur Kompetenz des Checks, mit direkter Rückmeldung zu jeder Eingabe.</p>
    </article>
    <article class="konzept-card" style="--kc-color: var(--mt-recall, #a78bfa)">
        <h3>Recall</h3>
        <p>Kernpunkte aus dem Gedächtnis abrufen. Eine KI bewertet die Antworten und meldet zurück, was fehlt oder unpräzise ist.</p>
    </article>
    <article class="konzept-card" style="--kc-color: var(--mt-feynman, #31cda8)">
        <h3>Feynman</h3>
        <p>Ein Konzept in eigenen Worten erklären, als würde man es jemandem beibringen. Die KI liest gegen und benennt Lücken und Denkfehler.</p>
    </article>
    <article class="konzept-card" style="--kc-color: var(--mt-kompetenzliste, #378ea3)">
        <h3>Kompetenzliste</h3>
        <p>Der Abschluss jeder Kette. Hier wird festgehalten, ob die Kompetenz sitzt. Check für Check entsteht so der Überblick über den Lernbereich.</p>
    </article>
</div>

Bei Recall und Feynman bewertet eine KI die Antworten. Sie erhält zu jedem Check gezielt vorbereitetes Kontextwissen, damit die Rückmeldungen fachlich verlässlich sind.


## Quantitativer Fortschritt

Der Feed gibt jederzeit eindeutig vor, welche Aktivität als Nächstes ansteht. So lässt sich die Session gleichmäßig verteilt bis zum gewünschten Zieldatum absolvieren.

Die Ketten mehrerer Checks laufen zeitlich leicht versetzt und überlappen sich. Dadurch liegen die Glieder einer Kette mit zeitlichem Abstand auseinander. Zwischen den Aktivitäten darf ein Teil des Gelernten wieder verblassen, denn gerade das erneute Erinnern verankert Wissen nachhaltig.

## Qualitativer Fortschritt

Bei jeder Aktivität entsteht eine Erfolgsquote. Sie wird übersichtlich im Dashboard dargestellt und lässt sich jederzeit und unabhängig vom Feed verbessern. Auch hier gibt MatheChecks Hinweise, wann sich eine Wiederholung lohnt.

## Übersicht

<div class="konzept-panel">
    <div class="konzept-controls">
        <button class="konzept-play" id="konzeptPlayBtn" type="button">▶ Ablauf abspielen</button>
        <span class="konzept-status" id="konzeptStatus">bereit</span>
    </div>
    <div class="konzept-scroll">
        <svg class="konzept-svg" id="konzeptSvg" viewBox="0 0 726 597" role="img"
            aria-label="Animierte Grafik: drei zeitlich versetzte Check-Ketten aus Training, Recall, Feynman und Kompetenzliste, darunter drei beispielhafte Erfolgsquoten-Ringe"></svg>
    </div>
    <div class="konzept-legend">
        <div class="konzept-legend__item"><span class="konzept-legend__dot konzept-legend__dot--training"></span> Training</div>
        <div class="konzept-legend__item"><span class="konzept-legend__dot konzept-legend__dot--recall"></span> Recall</div>
        <div class="konzept-legend__item"><span class="konzept-legend__dot konzept-legend__dot--feynman"></span> Feynman</div>
        <div class="konzept-legend__item"><span class="konzept-legend__dot konzept-legend__dot--kompetenz"></span> Kompetenzliste</div>
    </div>
    <p class="konzept-note">Oben: drei Check-Ketten im zeitlichen Ablauf. Unten: drei beispielhafte Erfolgsquoten. Sie füllen sich, sobald der Ablauf ihren Knoten passiert, und steigen danach unabhängig weiter. Klick auf einen Ring: nochmal üben.</p>
</div>



# Feed-unabhängiges Lernen

Der Feed führt dich klug durch deine Session. Du kannst MatheChecks aber auch feed-unabhängig nutzen, zum Beispiel um gezielt einzelne Aufgaben zu bearbeiten oder im Skript etwas nachzulesen.

<script src="{{ '/assets/js/konzept-grafik.js?v=20260816-recall-check2' | relative_url }}" defer></script>
