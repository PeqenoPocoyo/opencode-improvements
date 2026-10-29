# Sincronização multi-dispositivo — OpenCode Improvements
# Uso: .\scripts\sync.ps1
# Puxa as últimas mudanças de origin/main e restaura mudanças locais.

$ErrorActionPreference = "Stop"
$repo = "https://github.com/PeqenoPocoyo/opencode-improvements.git"

if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositório..." -ForegroundColor Cyan
    git init
    git remote add origin $repo
}

Write-Host "Buscando atualizações de origin..." -ForegroundColor Cyan
git fetch origin

# Se houver mudanças locais não commitadas, stashear
$changes = git status --porcelain
if ($changes) {
    Write-Host "Mudanças locais detectadas — stasheando..." -ForegroundColor Yellow
    git stash
    $stashed = $true
} else {
    $stashed = $false
}

# Garantir que estamos na main
git checkout main 2>$null

# Pull da main
Write-Host "Puxando origin/main..." -ForegroundColor Cyan
git pull origin main

# Restaurar stash se houver
if ($stashed) {
    git stash pop
    Write-Host "Mudanças locais restauradas. Revise e commite." -ForegroundColor Yellow
}

Write-Host "Sincronizado com origin/main" -ForegroundColor Green
Write-Host "Último commit:" -ForegroundColor Gray
git log --oneline -1
