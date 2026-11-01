#!/usr/bin/env bash
# Install Global Skills — auto-configure imported skills into $USER/.config/opencode
# Uso: bash scripts/install-global-skills.sh  (apos sync opencode)
# Idempotente: copia skills/imported-global/* -> ~/.config/opencode/skills/
#             e skills/imported-agents/*      -> ~/.agents/skills/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SRC_GLOBAL="$REPO_ROOT/skills/imported-global"
SRC_AGENTS="$REPO_ROOT/skills/imported-agents"
DST_GLOBAL="$HOME/.config/opencode/skills"
DST_AGENTS="$HOME/.agents/skills"

echo "=== Install Global Skills ==="
echo "Repo: $REPO_ROOT"

mkdir -p "$DST_GLOBAL" "$DST_AGENTS"

COPIED_GLOBAL=0
COPIED_AGENTS=0

if [ -d "$SRC_GLOBAL" ]; then
  for d in "$SRC_GLOBAL"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    cp -r "$d" "$DST_GLOBAL/$name"
    COPIED_GLOBAL=$((COPIED_GLOBAL+1))
  done
  echo "[OK] Skills globais instaladas: $COPIED_GLOBAL"
else
  echo "[SKIP] $SRC_GLOBAL nao existe"
fi

if [ -d "$SRC_AGENTS" ]; then
  for d in "$SRC_AGENTS"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    cp -r "$d" "$DST_AGENTS/$name"
    COPIED_AGENTS=$((COPIED_AGENTS+1))
  done
  echo "[OK] Skills agents instaladas: $COPIED_AGENTS"
else
  echo "[SKIP] $SRC_AGENTS nao existe"
fi

echo ""
echo "=== Concluido ==="
echo "Skills instaladas em: $DST_GLOBAL"
echo "Reinicie o OpenCode para carregar as novas skills."
