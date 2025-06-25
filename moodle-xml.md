---
layout: zusatzmaterial
title: Moodle XML-Dateien
description: Moodle XML zum Download
---

<div id="xml-list">
  <!-- Liste wird dynamisch mit JavaScript eingefügt -->
</div>

<script>
fetch('/xml/xml-liste.json')
  .then(response => response.json())
  .then(dateien => {
    const ul = document.createElement('ul');
    dateien.forEach(name => {
      const li = document.createElement('li');
      li.innerHTML = `<a href="/xml/${name}" download>${name}</a>`;
      ul.appendChild(li);
    });
    document.getElementById('xml-list').appendChild(ul);
  })
  .catch(() => {
    document.getElementById('xml-list').innerText = 'Fehler beim Laden der Datei-Liste.';
  });

</script>
