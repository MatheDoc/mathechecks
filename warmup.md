---
layout: shell
title: "Warm-Ups – Übersicht"
description: Übersicht der Warm-Ups pro Check (nicht verlinkt).
page_context: Warm-Up
nav: dashboard
body_class: page-module
noindex: true
published: true
page_css: /assets/css/warmup.css?v=20261014-warmup-zahlenstrahl
permalink: /warmup.html
---
{% comment %}
Isolierte Übersicht aller Warm-Ups: bewusst nirgends verlinkt, noindex, nicht in der Sitemap.
Wird vollständig aus _data/warmup/<gebiet>/<lernbereich>/<NN>-<sammlung>.yml und _data/checks.json erzeugt.
Reihenfolge: Lernbereiche wie in _data/lernbereiche.yml, darin nach Check-Nummer.
{% endcomment %}
<div class="page-shell w-wide">
  <section class="cw-root">
    <header class="cw-index-head">
      <div><span class="cw-chip">Warm-Up pro Check</span> <span class="cw-proto">nicht verlinkt</span></div>
      <h1>Geführter Einstieg in einen Check</h1>
      <p class="cw-goal"><span class="cw-goal__text">Drei Phasen: <strong>Idee</strong> → <strong>Zuschauen</strong> (vorgerechnetes Beispiel) → <strong>Mitmachen</strong> (Fading nach Rechenmuster), danach weiter ins Training. Nicht im Feed und nirgends verlinkt.</span></p>
    </header>

    <ul class="cw-index">
      {%- for lb in site.data.lernbereiche -%}
      {%- assign lb_warmups = site.data.warmup[lb.gebiet][lb.slug] -%}
      {%- unless lb_warmups -%}{%- continue -%}{%- endunless -%}
      {%- assign gebiet = site.data.gebiete | where: "key", lb.gebiet | first -%}
      {%- assign lb_checks = site.data.checks | where: "Lernbereich", lb.slug | sort: "Nummer" -%}
      {%- for check in lb_checks -%}
      {%- assign nn = check.Nummer | prepend: "0" | slice: -2, 2 -%}
      {%- assign warmup_key = nn | append: "-" | append: check.Sammlung -%}
      {%- assign w = lb_warmups[warmup_key] -%}
      {%- unless w -%}{%- continue -%}{%- endunless -%}
      {%- assign url = "/lernbereiche/" | append: lb.gebiet | append: "/" | append: lb.slug | append: "/warmup.html#check-" | append: check.Nummer %}
      <li>
        <a href="{{ url | relative_url }}">
          <strong>{{ gebiet.name | default: lb.gebiet }} · {{ check.LernbereichAnzeigename }} · Check {{ nn }}: {{ check.Schlagwort }}</strong>
          <small>Ich kann {{ check["Ich kann"] }} · {{ w.karten | size }} Karten</small>
        </a>
      </li>
      {%- endfor -%}
      {%- endfor %}
    </ul>
  </section>
</div>
