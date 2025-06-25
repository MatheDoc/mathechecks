---
layout: zusatzmaterial
title: Moodle XML-Dateien
description: Moodle XML zum Download
---

<div id="xml-list">
  <!-- Liste wird dynamisch mit JavaScript eingefügt -->
</div>

<script>
fetch('xml/')
  .then(response => response.text())
  .then(html => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const links = [...doc.querySelectorAll('a')];
    const ul = document.createElement('ul');

    links.forEach(link => {
      const href = link.getAttribute('href');
      if (href && href.endsWith('.xml')) {
        const li = document.createElement('li');
        li.innerHTML = `<a href="/xml/${href}" download>${href}</a>`;
        ul.appendChild(li);
      }
    });

    document.getElementById('xml-list').appendChild(ul);
  })
  .catch(err => {
    document.getElementById('xml-list').innerText = 'Fehler beim Laden der XML-Dateien.';
  });
</script>
