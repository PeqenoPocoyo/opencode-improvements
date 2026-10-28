#!/usr/bin/env bash
# PreToolUse Hook — Security Guard
# Bloqueia operações potencialmente perigosas antes da execução.
# Uso: configurar em settings.json como PreToolUse hook.

set -euo pipefail

# Lê o input JSON do stdin (fornecido pelo OpenCode)
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null || echo "")
TOOL_INPUT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin).get('tool_input',{})))" 2>/dev/null || echo "{}")

# Padrões perigosos em comandos shell
DANGEROUS_PATTERNS=(
  "rm -rf /"
  "rm -rf ~"
  "dd if="
  "mkfs"
  ":(){ :|:& };:"
  "chmod -R 777 /"
  "> /dev/sda"
  "curl.*|.*bash"
  "wget.*|.*sh"
)

# Verificar se é um comando bash
if [ "$TOOL_NAME" = "Bash" ] || [ "$TOOL_NAME" = "bash" ] || [ "$TOOL_NAME" = "shell" ]; then
  CMD=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")
  
  for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$CMD" | grep -qE "$pattern"; then
      echo "BLOCKED: Comando perigoso detectado: $pattern" >&2
      echo '{"decision": "block", "reason": "Comando potencialmente destrutivo detectado"}'
      exit 0
    fi
  done
fi

# Verificar se é uma escrita de arquivo com segredos
if [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "write" ] || [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "edit" ]; then
  CONTENT=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('content','')+d.get('newString',''))" 2>/dev/null || echo "")
  
  # Padrões de segredos
  if echo "$CONTENT" | grep -qE "(api[_-]?key|secret|password|token|credential)\s*[:=]\s*['\"][^'\"]{8,}"; then
    echo "WARNING: Possível segredo detectado no conteúdo" >&2
  fi
fi

# Permitir por padrão
echo '{"decision": "allow"}'
exit 0
