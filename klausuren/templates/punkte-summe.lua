-- Pandoc-Lua-Filter: summiert \punkte{n} je Aufgabe (H2-Abschnitt) und
-- haengt die Summe an die jeweilige Ueberschrift an; setzt ausserdem
-- die Gesamtpunktzahl aller gefundenen \punkte{n} als Metadatenfeld
-- "gesamtpunkte" (fuer den Klausurkopf).
-- Wahlaufgaben: Enthaelt eine Aufgaben-Ueberschrift "Wahlaufgabe", zaehlen davon
-- nur so viele (die punktreichsten) zur Gesamtpunktzahl, wie das Metadatenfeld
-- "wahlaufgaben" (Frontmatter, z. B. wahlaufgaben: 2) angibt; ohne Feld zaehlen alle.
-- Abschnitte ohne \punkte{n} (z.B. die Loesungen) bleiben unveraendert.

local function punkte_in(block)
  local sum = 0
  local function count(el)
    if el.format == "tex" then
      local n = el.text:match("\\punkte{(%d+)}")
      if n then sum = sum + tonumber(n) end
    end
  end
  -- Allein stehendes \punkte{n} (z. B. nach einer Tabelle) wird als RawBlock geparst
  if block.t == "RawBlock" then count(block) end
  pandoc.walk_block(block, { RawInline = count, RawBlock = count })
  return sum
end

function Pandoc(doc)
  local blocks = doc.blocks
  local total = 0
  local wahl = {}
  local i = 1
  while i <= #blocks do
    local header = blocks[i]
    if header.t == "Header" and header.level == 2 then
      local sum = 0
      local j = i + 1
      while j <= #blocks and not (blocks[j].t == "Header" and blocks[j].level <= 2) do
        sum = sum + punkte_in(blocks[j])
        j = j + 1
      end
      if sum > 0 then
        local ist_wahl = pandoc.utils.stringify(header.content):find("Wahlaufgabe", 1, true) ~= nil
        header.content:insert(pandoc.Space())
        header.content:insert(pandoc.Str("(" .. sum .. " Punkte)"))
        if ist_wahl then
          table.insert(wahl, sum)
        else
          total = total + sum
        end
      end
      i = j
    else
      i = i + 1
    end
  end
  table.sort(wahl, function(a, b) return a > b end)
  local anzahl = doc.meta.wahlaufgaben and tonumber(pandoc.utils.stringify(doc.meta.wahlaufgaben)) or #wahl
  for k = 1, math.min(anzahl, #wahl) do
    total = total + wahl[k]
  end
  doc.meta.gesamtpunkte = pandoc.MetaString(tostring(total))
  return doc
end
