#!/usr/bin/env python3
"""
Capability Audit — PostToolUse Hook.

Auditoria CONTINUA de capacidades durante a conversa.
Mentaliza testes unitarios AGENDADOS identificados durante a conversa
para reconsiderar se o modelo ainda esta desprovido de certa capacidade.

Regras:
- A cada resultado de tool, perguntar: "estou 100% provido desta capacidade?"
- Se NAO: mentalizar um teste unitario e AGENDA-LO (registrar em arquivo).
- Reconsiderar capacidades repetidamente, sem limite de ciclos.
- Nao esperar ordem definida: reinterpretar, testar, validar, reaprimorar, reavaliar.

Sem matchers: dispara em qualquer tool.
Fail-open: qualquer erro resultado em saida 0.
"""
import sys
import json
import os
from datetime import datetime

STATE_DIR = os.path.expanduser("~/.config/opencode/reasoning-state")
TESTS_FILE = os.path.join(STATE_DIR, "scheduled-capability-tests.json")

def load_state():
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        if os.path.exists(TESTS_FILE):
            with open(TESTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"scheduled_tests": [], "audit_round": 0}

def save_state(state):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(TESTS_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

CAPABILITY_DIMENSIONS = [
    "interpretacao de contexto",
    "navegacao de skills",
    "raciocinio multi-etapa",
    "teste de hipoteses",
    "reconsideracao de argumentos",
    "auto-pesquisa (deep research)",
    "triangulacao de fontes",
    "geracao de artefatos visuais",
    "auto-melhoria continua",
    "execucao e automacao",
]

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            data = {"raw": input_data}

        state = load_state()
        state["audit_round"] += 1

        # A cada rodada, auditar uma dimensao ciclicamente (sem ordem rigida)
        idx = state["audit_round"] % len(CAPABILITY_DIMENSIONS)
        dimension = CAPABILITY_DIMENSIONS[idx]

        # Mentalizar teste
        test = {
            "id": f"cap-test-{state['audit_round']}",
            "dimension": dimension,
            "scheduled_at": datetime.utcnow().isoformat() + "Z",
            "status": "mentalized",
            "hypothesis": (
                f"O modelo esta plenamente provido da capacidade '{dimension}' "
                "no contexto atual?"
            ),
            "if_fail": (
                "Se reconhecer que NAO esta provido: desenvolver melhoria "
                "(hook/instrucao/skill), testar, validar e commitar."
            ),
        }
        state["scheduled_tests"].append(test)

        # Manter apenas ultimos 50 testes agendados
        state["scheduled_tests"] = state["scheduled_tests"][-50:]
        save_state(state)

        additional = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"[CAPABILITY AUDIT] Rodada {state['audit_round']}: "
                    f"voce esta plenamente provido da capacidade '{dimension}'? "
                    "Se HOUVER duvida minima, nao ignore — mentalize teste e desenvolva. "
                    f"Teste mentalizado: {test['id']}. Registrado em scheduled-capability-tests.json. "
                    "Reconsidere capacidades repetidamente; sem ordem definida, sem limite de ciclos."
                )
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
