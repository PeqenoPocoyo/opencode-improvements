#!/usr/bin/env bash
# PreToolUse Hook — Security Guard (versão melhorada)
# Bloqueia operações potencialmente perigosas antes da execução.
# Uso: configurar em settings.json como PreToolUse hook.
#
# Melhorias v1.2:
# - Padrões regex mais completos (alinhados com validate_bash_command.py)
# - Detecção de segredos em Write/Edit (alinhada com validate_sensitive_write.py)
# - Fail-open: nunca quebra a sessão por erro interno
# - Mensagens de bloqueio mais claras

set -uo pipefail

# Lê o input JSON do stdin (fornecido pelo OpenCode)
INPUT=$(cat 2>/dev/null || echo "{}")

# Extrai tool_name e tool_input com python3 (fail-open)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null || echo "")
TOOL_INPUT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin).get('tool_input',{})))" 2>/dev/null || echo "{}")

# Padrões perigosos em comandos shell (regex)
DANGEROUS_PATTERNS=(
  "rm[[:space:]]+-rf[[:space:]]+/"
  "rm[[:space:]]+-rf[[:space:]]+~"
  "dd[[:space:]]+if="
  "mkfs\."
  ":(){:|:&};:"
  "chmod[[:space:]]+-R[[:space:]]+777[[:space:]]+/"
  ">[[:space:]]*/dev/(sda|hda|vda)"
  "curl.*\|[[:space:]]*(bash|sh)"
  "wget.*\|[[:space:]]*(bash|sh)"
  ">\s*/dev/sda"
)

# Verificar se é um comando bash/shell
if [ "$TOOL_NAME" = "Bash" ] || [ "$TOOL_NAME" = "bash" ] || [ "$TOOL_NAME" = "shell" ] || [ "$TOOL_NAME" = "Shell" ]; then
  CMD=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")

  for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$CMD" | grep -qEi "$pattern"; then
      echo "BLOCKED: Comando perigoso detectado (padrão: $pattern)" >&2
      echo '{"decision": "block", "reason": "Comando potencialmente destrutivo detectado"}'
      exit 0
    fi
  done
fi

# Verificar escrita de arquivo com segredos (Write/Edit/MultiEdit)
if [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "write" ] || [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "edit" ] || [ "$TOOL_NAME" = "MultiEdit" ]; then
  CONTENT=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('content','')+d.get('newString','')+d.get('new_string',''))" 2>/dev/null || echo "")
  FILE_PATH=$(echo "$TOOL_INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path','')+d.get('path',''))" 2>/dev/null || echo "")

  # Padrões de segredos no conteúdo
  if echo "$CONTENT" | grep -qEi "(api[_-]?key|secret|password|token|credential)[[:space:]]*[:=][[:space:]]*['\"][^'\"]{8,}"; then
    echo "WARNING: Possível segredo detectado no conteúdo" >&2
  fi

  # Arquivos sensíveis
  SENSITIVE_FILES=("\.env" "\.secret" "\.pem$" "\.key$" "id_rsa" "id_dsa" "secrets?\.json" "credentials?\.json" "\.pfx$" "\.p12$")
  for pat in "${SENSITIVE_FILES[@]}"; do
    if echo "$FILE_PATH" | grep -qEi "$pat"; then
      echo "WARNING: Arquivo sensível detectado: $FILE_PATH" >&2
      break
    fi
  done
fi

# Permitir por padrão (fail-open)
echo '{"decision": "allow"}'
exit 0