#!/usr/bin/env python3
"""
Deep Research Loop — PreToolUse/PostToolUse Hook.

Incentiva pesquisas profundas REPETIDAS com fontes DIFERENTES.
Nunca acessar a mesma pagina duas vezes na mesma rodada.
Objetivo: amplo entendimento por triangulacao de fontes.

Regras injetadas no contexto do modelo:
- A cada tool call de busca/fetch, verificar se a fonte e nova.
- Se a fonte ja foi usada, DESCARTA-LA e buscar outra.
- Minimo de 3 fontes independentes antes de concluir.
- Apresentar perspectivas divergentes, nao apenas consenso.

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

        hook_event = data.get("hook_event_name", data.get("hookSpecificOutput", {}).get("hookEventName", ""))
        tool_name = data.get("tool_name", data.get("tool", ""))
        tool_input = json.dumps(data.get("tool_input", data.get("input", {})))[:600]

        event_name = hook_event if hook_event else "PreToolUse"

        if event_name == "PreToolUse":
            context = (
                "[DEEP RESEARCH] Antes de buscar: "
                "(1) Esta fonte e NOVA nesta rodada? Se ja acessou, DESCARTE e escolha outra. "
                "(2) Quantas fontes independentes ja coletou? Minimo recomendado: 3. "
                "(3)Esta fonte cobre um angulo DIFERENTE das anteriores? "
                "(4) Ha vies obvio nesta fonte (comercial, oficial, opinativa)? Busque contraponto. "
                "Input da tool: " + tool_input
            )
        else:
            context = (
                "[DEEP RESEARCH — POS] Apos coletar: "
                "(1) As fontes convergent ou divergem? Se divergem, APRESENTE AMBAS as perspectivas. "
                "(2) Ainda ha lacuna de entendimento? Se sim, Nova rodada de busca com fonte diferente. "
                "(3) Voce repetiu alguma fonte? Se sim, provavelmente ha vies de confirmacao — corrija. "
                "(4) Antes de concluir: triangulou (>=3 fontes independentes)? "
                "Resultado da tool: " + tool_input
            )

        additional = {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": context
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
