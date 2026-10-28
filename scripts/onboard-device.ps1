# Onboarding de novo dispositivo — OpenCode Improvements
# Uso: .\scripts\onboard-device.ps1 -DeviceName "notebook"
# Conecta o projeto local deste dispositivo ao repositório unificado.

param(
    [Parameter(Mandatory=$true)]
    [string]$DeviceName
)

$ErrorActionPreference = "Stop"
$repo = "https://github.com/PeqenoPocoyo/opencode-improvements.git"
$branch = "device-$DeviceName"

Write-Host "=== Onboarding do dispositivo: $DeviceName ===" -ForegroundColor Cyan

# 1. Inicializar git se necessário
if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositório git..." -ForegroundColor Yellow
    git init
    git remote add origin $repo
} else {
    # Garantir que o remote está correto
    $existingRemote = git remote get-url origin 2>$null
    if ($existingRemote -ne $repo) {
        git remote remove origin 2>$null
        git remote add origin $repo
    }
}

# 2. Buscar conteúdo remoto
Write-Host "Buscando conteúdo remoto..." -ForegroundColor Yellow
git fetch origin

# 3. Criar branch do dispositivo
Write-Host "Criando branch $branch..." -ForegroundColor Yellow
git checkout -b $branch 2>$null
if ($LASTEXITCODE -ne 0) {
    git checkout $branch
}

# 4. Adicionar todo o conteúdo local
Write-Host "Adicionando conteúdo local..." -ForegroundColor Yellow
git add -A

# 5. Commitar
$commitMsg = "chore: import content from $DeviceName"
git commit -m $commitMsg 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nada novo para commitar (ou já commitado)." -ForegroundColor Gray
}

# 6. Push da branch do dispositivo
Write-Host "Enviando branch $branch para origin..." -ForegroundColor Yellow
git push -u origin $branch

Write-Host ""
Write-Host "=== Onboarding concluído! ===" -ForegroundColor Green
Write-Host "Branch '$branch' enviada para origin." -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. No dispositivo principal: git fetch --all && git merge origin/$branch && git push origin main"
Write-Host "  2. Neste dispositivo: git checkout main && git pull origin main"
Write-Host "  3. Para sync contínuo: .\scripts\sync.ps1"
