# Sincronização multi-dispositivo — OpenCode Improvements

## Como conectar um novo dispositivo (ou outro projeto) a este repositório

### Passo 1 — No dispositivo novo (terminal dentro da pasta do projeto dele)

```powershell
# Windows (PowerShell)
cd <pasta-do-projeto>
git init
git remote add origin https://github.com/PeqenoPocoyo/opencode-improvements.git
git fetch origin
git checkout -b device-<nome>       # ex: device-notebook, device-desktop
git add -A
git commit -m "chore: import content from <nome>"
git push -u origin device-<nome>
```

```bash
# Mac/Linux (bash)
cd <pasta-do-projeto>
git init
git remote add origin https://github.com/PeqenoPocoyo/opencode-improvements.git
git fetch origin
git checkout -b device-<nome>
git add -A
git commit -m "chore: import content from <nome>"
git push -u origin device-<nome>
```

### Passo 2 — Neste dispositivo (unificação)

```powershell
git fetch --all
git merge origin/device-<nome> --no-edit   # repita para cada dispositivo
# resolver conflitos se houver
git push origin main
```

### Passo 3 — Em TODOS os dispositivos (receber a versão unificada)

```powershell
git checkout main
git pull origin main
```

A partir daí, cada dispositivo está na `main` unificada e pode:
- `git pull` para receber atualizações de outros dispositivos
- Criar branches para experimentos
- Commitar e pushar mudanças que outros dispositivos receberão

---

## Auto-atualização (script de sync)

### Windows — `scripts/sync.ps1`

```powershell
# Executar: .\scripts\sync.ps1
$ErrorActionPreference = "Stop"
$repo = "https://github.com/PeqenoPocoyo/opencode-improvements.git"

if (-not (Test-Path ".git")) {
    git init
    git remote add origin $repo
}

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

# Pull da main
git checkout main 2>$null
git pull origin main

# Restaurar stash se houver
if ($stashed) {
    git stash pop
    Write-Host "Mudanças locais restauradas. Revise e commite." -ForegroundColor Yellow
}

Write-Host "Sincronizado com origin/main" -ForegroundColor Green
```

### Mac/Linux — `scripts/sync.sh`

```bash
#!/bin/bash
set -e
REPO="https://github.com/PeqenoPocoyo/opencode-improvements.git"

if [ ! -d ".git" ]; then
    git init
    git remote add origin "$REPO"
fi

git fetch origin

# Stash se houver mudanças locais
if [ -n "$(git status --porcelain)" ]; then
    echo "Mudanças locais detectadas — stasheando..."
    git stash
    STASHED=1
else
    STASHED=0
fi

git checkout main 2>/dev/null || true
git pull origin main

if [ "$STASHED" = "1" ]; then
    git stash pop
    echo "Mudanças locais restauradas. Revise e commite."
fi

echo "Sincronizado com origin/main"
```

---

## Fluxo de auto-atualização contínua

```
Dispositivo A (este)     Dispositivo B          Dispositivo C
       |                      |                      |
   git commit + push        git pull              git pull
       |                      |                      |
       v                      v                      v
   origin/main  <--------  origin/main  -------->  origin/main
```

1. Qualquer dispositivo commita e pusha → `origin/main` atualiza
2. Os outros dispositivos rodam `git pull` (ou `scripts/sync.ps1`) → recebem tudo
3. Skills, hooks, instruções, artefatos e configs ficam unificados

### Dica: automatizar o pull

- **Windows**: Agendar `scripts/sync.ps1` no Agendador de Tarefas (ex: a cada hora)
- **Mac/Linux**: Cron job: `0 * * * * cd ~/OpenCode && bash scripts/sync.sh`

---

## O que vai "piscar" (notificar) no outro dispositivo

Quando o outro dispositivo conectar ao repositório e rodar `git fetch`, ele verá:
- Novas branches (`device-*`) dos outros dispositivos
- Novos commits em `main` (artefatos, skills, hooks, instruções adicionados aqui)
- Mensagem de "Your branch is behind 'origin/main' by X commits"

O script `sync.ps1` / `sync.sh` faz o `pull` automaticamente e avisa se houver mudanças locais para revisar.
