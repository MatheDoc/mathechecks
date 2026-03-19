param(
    [string]$Root = ".",
    [switch]$StagedOnly,
    [int]$MaxHitsToPrint = 200
)

# Typical mojibake fragments seen when UTF-8 text is decoded as cp1252/ibm850.
$patterns = @(
    "Ã[\x80-\xBF]",   # e.g. Ã¼, Ã¶
    "â€[\x80-\xBF]",  # e.g. smart quotes/dashes
    "âˆ’",             # minus sign corruption
    "Â[\x80-\xBF ]",  # stray nbsp/spacing marker
    [string][char]0xFFFD # replacement character '�'
)

$regex = [string]::Join("|", $patterns)
$extensions = @(
    ".md", ".markdown", ".html", ".htm", ".css", ".js", ".ts",
    ".json", ".yml", ".yaml", ".xml", ".txt", ".py", ".rb", ".liquid"
)

# Exclude generated/legacy areas to avoid noisy findings outside maintained source content.
$excludeRegex = "(^|/)\.git/|(^|/)_site/|(^|/)node_modules/|(^|/)aufgaben/exports/|(^|/)html/|(^|/)xml_alt/|(^|/)xml/|(^|/)json/"

function Test-IsExcludedPath {
    param([string]$Path)

    # Normalize separators so filtering behaves identically on Windows and Linux runners.
    $normalizedPath = $Path.Replace('\\', '/')
    return $normalizedPath -match $excludeRegex
}

if ($StagedOnly) {
    $stagedPaths = git diff --cached --name-only --diff-filter=ACMR
    $files = @()
    foreach ($path in $stagedPaths) {
        if (-not $path) {
            continue
        }

        $fullPath = Join-Path $Root $path
        if (-not (Test-Path -Path $fullPath -PathType Leaf)) {
            continue
        }

        $item = Get-Item -Path $fullPath
        if (Test-IsExcludedPath -Path $item.FullName) {
            continue
        }

        if ($extensions -contains $item.Extension.ToLowerInvariant()) {
            $files += $item
        }
    }
}
else {
    $files = Get-ChildItem -Path $Root -Recurse -File | Where-Object {
        -not (Test-IsExcludedPath -Path $_.FullName) -and
        $extensions -contains $_.Extension.ToLowerInvariant()
    }
}

$hits = @()
foreach ($file in $files) {
    $fileHits = Select-String -Path $file.FullName -Pattern $regex -AllMatches -Encoding UTF8
    if ($fileHits) {
        $hits += $fileHits
    }
}

if ($hits.Count -eq 0) {
    if ($StagedOnly) {
        Write-Output "No mojibake patterns found in staged files."
    }
    else {
        Write-Output "No mojibake patterns found."
    }
    exit 0
}

Write-Output "Potential mojibake found:"
$hitsToPrint = $hits | Select-Object -First $MaxHitsToPrint
foreach ($hit in $hitsToPrint) {
    $relative = Resolve-Path -Relative $hit.Path
    Write-Output ("{0}:{1}: {2}" -f $relative, $hit.LineNumber, $hit.Line.Trim())
}

if ($hits.Count -gt $MaxHitsToPrint) {
    Write-Output "... and $($hits.Count - $MaxHitsToPrint) more hit(s)."
}

exit 1
