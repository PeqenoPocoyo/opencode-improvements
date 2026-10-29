#!/bin/bash
# Sincronização multi-dispositivo — OpenCode Improvements
# Uso: bash scripts/sync.sh
# Puxa as últimas mudanças de origin/main e restaura mudanças locais.

set -e
REPO="https://github.com/PeqenoPocoyo/opencode-improvements.git"

if [ ! -d ".git" ]; then
    echo "Inicializando repositório..."
    git init
    git remote add origin "$REPO"
fi

echo "Buscando atualizações de origin..."
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
echo "Puxando origin/main..."
git pull origin main

if [ "$STASHED" = "1" ]; then
    git stash pop
    echo "Mudanças locais restauradas. Revise e commite."
fi

echo "Sincronizado com origin/main"
git log --oneline -1
