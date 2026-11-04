# /fix-nvidia — Corrigir/fallback quando modelos NVIDIA falham

Uso: /fix-nvidia [modelo-alternativo]

## Passos
1. Tente reenviar a última mensagem (retry).
2. Se falhar, troque o modelo default no OpenCode (`~/.config/opencode/opencode.jsonc`) por:
   - Padrão estável: `openrouter/anthropic/claude-3.5-sonnet`
   - Alternativas: `openrouter/google/gemini-2.5-flash`, `openrouter/openai/gpt-5.4-mini`
3. Se não houver cota/key para alternativa, mantenha o item original e re-tente com NVIDIA no modo /raw (sem tools pesados).
4. Reporte: "Modelo trocado para X e tentando novamente".

## Config global (exemplo)
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openrouter/anthropic/claude-3.5-sonnet",
  "providers": { ... },
  "skills": { ... }
}

## Variant com parâmetros
- `/fix-nvidia gemini` → tenta `openrouter/google/gemini-2.5-flash`
- `/fix-nvidia gpt` → tenta `openrouter/openai/gpt-5.4-mini`
- `/fix-nvidia reset` → volta para o modelo NVDIA original guardado em `configs/model-original.txt`

## Comportamento fail-open
- Se não existir arquivo de config, não tentar mudar provider fora do modelo.
- Se não houver key para o fallback, avisar e seguir.
- Nunca apagar segredos existentes.

Princípio: o comando não modifica lógica de negócio quando o provider cair; apenas troca o backend e refaz o envio.