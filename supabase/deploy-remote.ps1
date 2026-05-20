[CmdletBinding()]
param(
  [string]$SupabaseExe = (Join-Path $env:USERPROFILE "bin\supabase.exe"),
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$DbPushArgs
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SupabaseExe)) {
  throw "Supabase CLI nicht gefunden: $SupabaseExe`nNutze den Parameter -SupabaseExe oder installiere die CLI an diesem Pfad."
}

$repoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $repoRoot
try {
  Write-Host "Nutze Supabase CLI: $SupabaseExe"
  & $SupabaseExe db push @DbPushArgs
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
}
finally {
  Pop-Location
}