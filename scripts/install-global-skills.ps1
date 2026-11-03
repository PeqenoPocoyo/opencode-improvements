# Install Global Skills - auto-configure imported skills into $USER/.config/opencode
# Uso: .\scripts\install-global-skills.ps1  (apos sync opencode)
# Idempotente: copia skills/imported-global/* -> ~/.config/opencode/skills/
#             e skills/imported-agents/*      -> ~/.agents/skills/

$ErrorActionPreference = "Continue"

$repoRoot = Split-Path -Parent $PSScriptRoot
$srcGlobal = Join-Path $repoRoot "skills\imported-global"
$srcAgents = Join-Path $repoRoot "skills\imported-agents"
$dstGlobal = Join-Path $env:USERPROFILE ".config\opencode\skills"
$dstAgents = Join-Path $env:USERPROFILE ".agents\skills"

Write-Host "=== Install Global Skills ===" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot"

New-Item -ItemType Directory -Path $dstGlobal -Force | Out-Null
New-Item -ItemType Directory -Path $dstAgents -Force | Out-Null

$copiedGlobal = 0; $copiedAgents = 0; $skipped = 0

if (Test-Path $srcGlobal) {
    Get-ChildItem -Path $srcGlobal -Directory | ForEach-Object {
        $target = Join-Path $dstGlobal $_.Name
        try {
            if (Test-Path $target) { Remove-Item -Path $target -Recurse -Force -ErrorAction SilentlyContinue }
            Copy-Item -Path $_.FullName -Destination $target -Recurse -Force -ErrorAction Stop
            $copiedGlobal++
        } catch {
            Write-Host ("  [WARN] skip " + $_.Name + ": " + $_.Exception.Message) -ForegroundColor Yellow
            $script:skipped++
        }
    }
    Write-Host ("[OK] Skills globais instaladas: " + $copiedGlobal) -ForegroundColor Green
} else {
    Write-Host ("[SKIP] " + $srcGlobal + " nao existe") -ForegroundColor Yellow
}

if (Test-Path $srcAgents) {
    Get-ChildItem -Path $srcAgents -Directory | ForEach-Object {
        $target = Join-Path $dstAgents $_.Name
        try {
            if (Test-Path $target) { Remove-Item -Path $target -Recurse -Force -ErrorAction SilentlyContinue }
            Copy-Item -Path $_.FullName -Destination $target -Recurse -Force -ErrorAction Stop
            $copiedAgents++
        } catch {
            Write-Host ("  [WARN] skip " + $_.Name + ": " + $_.Exception.Message) -ForegroundColor Yellow
            $script:skipped++
        }
    }
    Write-Host ("[OK] Skills agents instaladas: " + $copiedAgents) -ForegroundColor Green
} else {
    Write-Host ("[SKIP] " + $srcAgents + " nao existe") -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Concluido ===" -ForegroundColor Cyan
Write-Host ("Skills instaladas em: " + $dstGlobal)
Write-Host ("Total copiadas: " + ($copiedGlobal + $copiedAgents) + " | Puladas: " + $skipped)
Write-Host "Reinicie o OpenCode para carregar as novas skills."