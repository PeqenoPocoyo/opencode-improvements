param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = "Continue"

$src = Join-Path $RepoRoot "commands"
$dst = Join-Path $env:USERPROFILE ".config\opencode\commands"

New-Item -ItemType Directory -Path $dst -Force | Out-Null

$copied = 0
Get-ChildItem -Path $src -Filter "*.md" | ForEach-Object {
    try {
        Copy-Item -Path $_.FullName -Destination (Join-Path $dst $_.Name) -Force
        $copied++
    } catch {
        Write-Warning ("Failed to copy " + $_.Name + ": " + $_.Exception.Message)
    }
}

Write-Host ("Install Global Commands: copied $copied .md files to $dst")
Write-Host "Slashes available after restart: $(@(Get-ChildItem -Path $dst -Filter '*.md' | Select -ExpandProperty BaseName) -join ', ')"