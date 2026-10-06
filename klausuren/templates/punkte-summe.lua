-- Pandoc-Lua-Filter: summiert \punkte{n} je Aufgabe (H2-Abschnitt) und
-- haengt die Summe an die jeweilige Ueberschrift an; setzt ausserdem
-- die Gesamtpunktzahl aller gefundenen \punkte{n} als Metadatenfeld
-- "gesamtpunkte" (fuer den Klausurkopf).
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
        header.content:insert(pandoc.Space())
        header.content:insert(pandoc.Str("(" .. sum .. " Punkte)"))
        total = total + sum
      end
      i = j
    else
      i = i + 1
    end
  end
  doc.meta.gesamtpunkte = pandoc.MetaString(tostring(total))
  return doc
end
