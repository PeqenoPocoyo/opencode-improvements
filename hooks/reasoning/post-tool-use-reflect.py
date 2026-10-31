#!/usr/bin/env python3
"""
Reasoning Reflect — PostToolUse Hook.

Apos cada tool call, injeta lembrete cognitivo para:
- Reconsiderar o resultado obtido
- Questionar se a conclusao ainda e valida
- Identificar se surgiu nova habilidade/capacidade a investigar
- Reconhecer gaps mensuraveis ou imensuraveis

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
        result = json.dumps(data.get("tool_result", data.get("result", {})))[:400]

        gaps = []
        # Heuristicas para detectar gaps durante a conversa
        result_lower = result.lower()
        gap_signals = {
            "nao consigo": "capacidade ausente",
            "nao e possivel": "limitacao identificada",
            "nao encontrado": "skill/recurso ausente",
            "erro": "falha a investigar",
            "falhou": "falha a investigar",
            "nao suporta": "limitacao de ferramenta",
            "nao tenho certeza": "incerteza a sanar",
            "talvez": "hipotese a validar",
            "limitacao": "limitacao declarada",
        }
        for signal, meaning in gap_signals.items():
            if signal in result_lower:
                gaps.append(f"{signal} -> {meaning}")

        gap_text = ""
        if gaps:
            gap_text = (
                " DISCREPANCIA DETECTADA: " + "; ".join(gaps) + ". "
                "ACAO OBRIGATORIA: crie uma tarefa para pesquisar (deep research) se alguma skill/hook/instrucao "
                "cobre essa lacanca. Se nao cobrir, desenvolva a melhoria."
            )

        additional = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"[RECONSIDERACAO] Apos '{tool_name}': "
                    f"(1) O resultado confirma ou contradiz minha hipotese anterior? "
                    f"(2) Se contradiz, REVERTA o raciocinio anterior e reconstrua. "
                    f"(3) Surgiu nova variavel que eu nao tinha considerado? "
                    f"(4) Preciso de outro ciclo: reinterpretar -> testar -> validar -> aprimorar? "
                    f"Resultado (amostra): {result}" + gap_text
                )
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
