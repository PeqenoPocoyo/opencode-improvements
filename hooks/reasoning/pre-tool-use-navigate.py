#!/usr/bin/env python3
"""
Reasoning Navigate — PreToolUse Hook.

Antes de cada tool call, injeta lembrete cognitivo para:
- Verificar se existe skill/hook/instrucao que cobre a acao
- Raciocinar sobre multiplas abordagens
- Reconsiderar se a tool escolhida e a melhor

Sem matchers: dispara em qualquer tool.
Fail-open: qualquer erro resulta em saida 0.
"""
import sys
import json

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            data = {"raw": input_data}

        tool_name = data.get("tool_name", data.get("tool", ""))
        tool_input = json.dumps(data.get("tool_input", data.get("input", {})))[:500]

        additional = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    f"[RACIOCINIO] Antes de executar '{tool_name}', pergunte-se: "
                    f"(1) Existe skill/hook/instrucao dedicada para isto? Verifique configs/skills-index.json. "
                    f"(2) Ha abordagem alternativa que eu nao considerei? "
                    f"(3) Meus argumentos anteriores ainda se sustentam apos esta nova informacao? "
                    f"(4) O resultado desta acao muda minha conclusao? Se sim, RECONSIDERE antes de prosseguir. "
                    f"(5) Input analisado: {tool_input}"
                )
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
