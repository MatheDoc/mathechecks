-- Pandoc-Lua-Filter: rendert alle Markdown-Tabellen mit
-- vertikalen Trennlinien, gleicher Spaltenbreite und zentriertem Text.
-- Hinweis: zusammengeführte Zellen (row-/colspan) werden nicht unterstützt.

local function render_cell(cell)
  local text = pandoc.write(pandoc.Pandoc(cell.contents), "latex")
  return (text:gsub("%s+$", ""))
end

local function render_row(cells, ncols)
  local parts = {}
  for i = 1, ncols do
    parts[i] = cells[i] and render_cell(cells[i]) or ""
  end
  return "  " .. table.concat(parts, " & ") .. " \\\\ \\hline"
end

function Table(tbl)
  local ncols = #tbl.colspecs
  if ncols == 0 then return nil end

  -- exakte Spaltenbreite: \linewidth minus Zellenabstand (2 * \tabcolsep je Spalte)
  -- und Rahmenlinien (ncols+1 * \arrayrulewidth), gleichmäßig auf alle Spalten verteilt
  local width = "\\dimexpr(\\linewidth-" .. (2 * ncols) .. "\\tabcolsep-" ..
      (ncols + 1) .. "\\arrayrulewidth)/" .. ncols .. "\\relax"
  local col = ">{\\centering\\arraybackslash}m{" .. width .. "}"
  local colspec = "|" .. string.rep(col .. "|", ncols)

  local out = {}
  table.insert(out, "\\begin{longtable}{" .. colspec .. "}")
  table.insert(out, "\\hline")

  if tbl.caption and tbl.caption.long and #tbl.caption.long > 0 then
    local captext = pandoc.write(pandoc.Pandoc(tbl.caption.long), "latex")
    -- \caption{} ist ein "moving argument": erzwungene Zeilenumbrüche (\\) sind dort ungueltig
    captext = captext:gsub("\\\\", " "):gsub("%s+$", "")
    table.insert(out, "\\caption{" .. captext .. "} \\\\ \\hline")
  end

  if tbl.head and #tbl.head.rows > 0 then
    for _, row in ipairs(tbl.head.rows) do
      table.insert(out, render_row(row.cells, ncols))
    end
    table.insert(out, "\\endhead")
  end

  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      table.insert(out, render_row(row.cells, ncols))
    end
  end

  table.insert(out, "\\end{longtable}")

  return pandoc.RawBlock("latex", table.concat(out, "\n"))
end
