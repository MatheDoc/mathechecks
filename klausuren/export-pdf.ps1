# export-pdf.ps1 — Klausur-PDF aus Markdown erzeugen
# Aufruf: .\export-pdf.ps1 lernbereiche\gravitation\klausur.md

param(
    [string]$InputFile
)

$root = Split-Path $MyInvocation.MyCommand.Path
# Ohne Parameter: Auswahldialog anzeigen
if (-not $InputFile) {
    Add-Type -AssemblyName System.Windows.Forms
    $dlg = New-Object System.Windows.Forms.OpenFileDialog
    $dlg.Title = "Markdown-Datei auswaehlen"
    $dlg.Filter = "Markdown (*.md)|*.md|Alle Dateien (*.*)|*.*"
    $dlg.InitialDirectory = $root
    if ($dlg.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { exit 0 }
    $InputFile = $dlg.FileName
}

$InputFile = Resolve-Path $InputFile

# Pandoc und MiKTeX in PATH sicherstellen
$env:Path = "$env:LOCALAPPDATA\Pandoc;$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64;" + $env:Path

function Resolve-RequiredTool {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name,
        [string[]]$CandidatePaths = @()
    )

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    foreach ($candidate in $CandidatePaths) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    return $null
}

$pandocExe = Resolve-RequiredTool -Name "pandoc" -CandidatePaths @(
    "$env:LOCALAPPDATA\Pandoc\pandoc.exe",
    "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\JohnMacFarlane.Pandoc_Microsoft.Winget.Source_8wekyb3d8bbwe\pandoc-3.10\pandoc.exe",
    "$env:ProgramFiles\Pandoc\pandoc.exe",
    "$env:ProgramFiles(x86)\Pandoc\pandoc.exe"
)

if (-not $pandocExe) {
    Write-Host "Fehler: Pandoc wurde nicht gefunden." -ForegroundColor Red
    Write-Host "Installiere Pandoc und fuehre das Skript erneut aus, z.B. mit: winget install --id JohnMacFarlane.Pandoc -e" -ForegroundColor Yellow
    exit 1
}

# YAML-Frontmatter lesen
$content = [System.IO.File]::ReadAllText($InputFile, [System.Text.Encoding]::UTF8)
$logo = $null
if ($content -match '(?s)^---\s*\r?\n(.*?)\r?\n---') {
    foreach ($line in ($matches[1] -split '\r?\n')) {
        if ($line -match '^logo:\s*(.+?)\s*$') {
            $logo = $matches[1].Trim([char]39, [char]34)
        }
    }
}

# Logo nur einbinden, wenn die Datei tatsaechlich existiert (Pfad mit Vorwaertsschraegstrichen fuer LaTeX)
if ($logo -and (Test-Path $logo)) {
    $logoOverride = ($logo -replace "\\", "/")
} else {
    $logoOverride = "false"
}

# Klausurkopf per Pandoc-Template rendern: fach/klasse/datum/thema kommen direkt
# aus der YAML-Frontmatter; gesamtpunkte wird vom Lua-Filter aus den \punkte{n}
# im Dokument berechnet und in die Metadaten geschrieben (keine manuelle Angabe noetig)
$punkteFilter = "$root\templates\punkte-summe.lua"
$headerFile = "$root\templates\klausurkopf-header.tex"
$tableFilter = "$root\templates\table-style.lua"
$inputDir = Split-Path $InputFile

if (-not ('MatheChecks.RestartManager' -as [type])) {
Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

namespace MatheChecks {
    public static class RestartManager {
        [StructLayout(LayoutKind.Sequential)]
        private struct FILETIME {
            public uint LowDateTime;
            public uint HighDateTime;
        }

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        private struct RM_UNIQUE_PROCESS {
            public int ProcessId;
            public FILETIME ProcessStartTime;
        }

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        private struct RM_PROCESS_INFO {
            public RM_UNIQUE_PROCESS Process;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)]
            public string ApplicationName;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 64)]
            public string ServiceShortName;
            public int ApplicationType;
            public uint ApplicationStatus;
            public uint TerminalSessionId;
            [MarshalAs(UnmanagedType.Bool)]
            public bool Restartable;
        }

        [DllImport("rstrtmgr.dll", CharSet = CharSet.Unicode)]
        private static extern int RmStartSession(out uint sessionHandle, int flags, StringBuilder sessionKey);

        [DllImport("rstrtmgr.dll", CharSet = CharSet.Unicode)]
        private static extern int RmRegisterResources(
            uint sessionHandle,
            uint fileCount,
            string[] fileNames,
            uint applicationCount,
            RM_UNIQUE_PROCESS[] applications,
            uint serviceCount,
            string[] serviceNames);

        [DllImport("rstrtmgr.dll")]
        private static extern int RmGetList(
            uint sessionHandle,
            out uint processInfoNeeded,
            ref uint processInfoCount,
            [In, Out] RM_PROCESS_INFO[] affectedApplications,
            ref uint rebootReasons);

        [DllImport("rstrtmgr.dll")]
        private static extern int RmEndSession(uint sessionHandle);

        public static int[] GetLockingProcessIds(string path) {
            uint sessionHandle;
            int result = RmStartSession(out sessionHandle, 0, new StringBuilder(Guid.NewGuid().ToString()));
            if (result != 0) throw new Win32Exception(result, "RmStartSession");

            try {
                result = RmRegisterResources(sessionHandle, 1, new[] { Path.GetFullPath(path) }, 0, null, 0, null);
                if (result != 0) throw new Win32Exception(result, "RmRegisterResources");

                uint needed;
                uint count = 0;
                uint rebootReasons = 0;
                result = RmGetList(sessionHandle, out needed, ref count, null, ref rebootReasons);
                if (result == 0) return new int[0];
                if (result != 234) throw new Win32Exception(result, "RmGetList");

                RM_PROCESS_INFO[] processes = new RM_PROCESS_INFO[needed];
                count = needed;
                result = RmGetList(sessionHandle, out needed, ref count, processes, ref rebootReasons);
                if (result != 0) throw new Win32Exception(result, "RmGetList");

                return processes.Take((int)count).Select(process => process.Process.ProcessId).Distinct().ToArray();
            }
            finally {
                RmEndSession(sessionHandle);
            }
        }
    }
}
'@
}

function Export-Pdf {
    param(
        [string]$Source,
        [string]$OutputFile
    )

    $beforeFile = [System.IO.Path]::GetTempFileName() + ".tex"
    & $pandocExe $Source `
        -o $beforeFile `
        --template="$root\templates\klausurkopf-before.tpl.tex" `
        --lua-filter=$punkteFilter `
        -M "logo=$logoOverride" | Out-Host

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Fehler beim Rendern des Klausurkopfs." -ForegroundColor Red
        return $false
    }

    # Gesperrte alte PDF vorab entfernen
    if (Test-Path $OutputFile) {
        $lockingProcessIds = @()
        try {
            $lockingProcessIds = [MatheChecks.RestartManager]::GetLockingProcessIds($OutputFile)
        } catch [System.Management.Automation.MethodInvocationException] {
            Write-Host "Hinweis: Der PDF-Viewer konnte nicht automatisch ermittelt werden: $($_.Exception.Message)" -ForegroundColor Yellow
        }

        foreach ($processId in $lockingProcessIds) {
            if ($processId -eq $PID) { continue }

            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($process) {
                try {
                    if ($process.CloseMainWindow()) {
                        Write-Host "Schliesse PDF-Viewer '$($process.ProcessName)' fuer '$OutputFile'..."
                        $process.WaitForExit(5000) | Out-Null
                    }
                } catch [System.Management.Automation.MethodInvocationException] {
                    Write-Host "Hinweis: PDF-Viewer '$($process.ProcessName)' konnte nicht automatisch geschlossen werden: $($_.Exception.Message)" -ForegroundColor Yellow
                }
            }
        }

        Remove-Item $OutputFile -ErrorAction SilentlyContinue
        if (Test-Path $OutputFile) {
            Write-Host "Fehler: '$OutputFile' ist noch geoeffnet (z.B. im PDF-Viewer). Bitte schliessen und erneut ausfuehren." -ForegroundColor Yellow
            Remove-Item $beforeFile -ErrorAction SilentlyContinue
            return $false
        }
    }

    & $pandocExe $Source `
        -o $OutputFile `
        --pdf-engine=xelatex `
        --resource-path="$inputDir" `
        -H $headerFile `
        -B $beforeFile `
        --lua-filter=$punkteFilter `
        --lua-filter=$tableFilter `
        -V "geometry:a4paper, top=2cm, bottom=2.5cm, left=2.5cm, right=2.5cm" `
        -V lang=de-DE `
        -V colorlinks=false | Out-Host

    $ok = ($LASTEXITCODE -eq 0)
    Remove-Item $beforeFile -ErrorAction SilentlyContinue

    if ($ok) {
        Write-Host "PDF erstellt: $OutputFile"
    } else {
        Write-Host "Fehler beim Erstellen der PDF." -ForegroundColor Red
    }
    return $ok
}

$basePath = [System.IO.Path]::ChangeExtension($InputFile, $null).TrimEnd('.')

# _L: komplette Klausur inkl. Loesungen
$okL = Export-Pdf -Source $InputFile -OutputFile "${basePath}_L.pdf"

# _S: Klausur ohne Loesungen (alles ab der Ueberschrift "# Loesungen" entfaellt)
$okS = $false
$marker = [regex]::Match($content, '(?m)^# L(\u00f6|oe)sungen\s*$')
if ($marker.Success) {
    $aufgabenOnly = $content.Substring(0, $marker.Index)
    $aufgabenOnly = ($aufgabenOnly -replace '(?s)(\s*\\newpage)?\s*$', '') + "`n"
    $tmpSource = Join-Path $inputDir "~klausur_S_tmp.md"
    [System.IO.File]::WriteAllText($tmpSource, $aufgabenOnly, (New-Object System.Text.UTF8Encoding($false)))
    try {
        $okS = Export-Pdf -Source $tmpSource -OutputFile "${basePath}_S.pdf"
    } finally {
        Remove-Item $tmpSource -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "Hinweis: Keine Ueberschrift '# Loesungen' gefunden - _S-Version wird nicht erstellt." -ForegroundColor Yellow
}

if (-not ($okL -and $okS)) { exit 1 }
