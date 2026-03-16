param(
    [string]$HooksPath = ".githooks"
)

$repoRoot = (Resolve-Path ".").Path

git config core.hooksPath $HooksPath | Out-Null

Write-Output "Git hooks path set to: $HooksPath"
Write-Output "Active repo: $repoRoot"
