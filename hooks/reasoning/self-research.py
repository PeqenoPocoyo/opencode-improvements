#!/usr/bin/env python3
"""
Self Research — Dispara em QUALQUER evento.

QUANDO SEMPRE QUE o modelo PERCEBE OU SOMENTE SUSPEITA MINIMAMENTE
que precisa melhorar em algo, PASSA A CONSIDERAR UMA TAREFA para
pesquisar se alguma hook, instrucao ou habilidade cobre essa
discrepancia (mensuravel ou imensuravel).

Se nao houver cobertura, desenvolve a melhoria e mentaliza testes.

Sem matchers: TODO evento e avaliado.
Fail-open: qualquer erro resulta em saida 0.
"""
import sys
import json
import os
from datetime import datetime

# Estado persistente de research tasks
STATE_DIR = os.path.expanduser("~/.config/opencode/reasoning-state")
STATE_FILE = os.path.join(STATE_DIR, "self-research-tasks.json")

def load_tasks():
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"tasks": [], "round": 0}

def save_tasks(state):
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def detect_discrepancy(payload):
    """Detecta qualquer sinal de discrepancia, por menor que seja."""
    text = json.dumps(payload).lower()
    signals = []
    # Sinais mensuraveis
    measurable = {
        "erro": "erro encontrado",
        "falhou": "falha encontrada",
        "nao passou": "teste falhou",
        "nao encontrado": "recurso ausente",
        "404": "recurso nao encontrado",
        "nao suporta": "limitacao de ferramenta",
        "timeout": "timeout",
    }
    # Sinais imensuraveis / subjetivos
    immeasurable = {
        "nao tenho certeza": "incerteza",
        "talvez": "hipotese nao validada",
        "acho que": "suposicao",
        "possivelmente": "ambiguidade",
        "poderia ser melhor": "oportunidade de melhoria",
        "nao e ideal": "satisfacao parcial",
        "confuso": "entendimento incompleto",
        "complicado": "complexidade nao dominada",
        "nao consegui": "capacidade ausente",
        "dificil": "dificuldade reconhecida",
    }
    for k, v in measurable.items():
        if k in text:
            signals.append({"type": "mensuravel", "signal": k, "meaning": v})
    for k, v in immeasurable.items():
        if k in text:
            signals.append({"type": "imensuravel", "signal": k, "meaning": v})
    return signals

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            data = {"raw": input_data}

        discrepancies = detect_discrepancy(data)
        if not discrepancies:
            sys.exit(0)

        state = load_tasks()
        state["round"] += 1

        # Criar tarefa de pesquisa
        task = {
            "id": f"task-{state['round']}-{int(datetime.utcnow().timestamp())}",
            "created": datetime.utcnow().isoformat() + "Z",
            "discrepancies": discrepancies,
            "status": "pending",
            "protocol": [
                "1. Verificar se alguma skill cobre (configs/skills-index.json)",
                "2. Verificar se algum hook cobre (hooks/reasoning/)",
                "3. Verificar se alguma instrucao cobre (instructions/)",
                "4. Se nao houver cobertura: DESENVOLVER a melhoria",
                "5. Mentalizar teste unitario para a melhoria",
                "6. Executar teste; se passar, promover para validated",
                "7. Commit + push para o repo unificado",
            ],
        }
        state["tasks"].append(task)
        save_tasks(state)

        desc = "; ".join(f"{d['meaning']} ({d['type']})" for d in discrepancies)

        additional = {
            "hookSpecificOutput": {
                "hookEventName": data.get("hook_event_name", "PreToolUse"),
                "additionalContext": (
                    "[SELF-RESEARCH] DISCREPANCIA DETECTADA (minima que seja): " + desc + ". "
                    "TAREFA OBRIGATORIA CRIADA: " + task["id"] + ". "
                    "Acoes: " + " | ".join(task["protocol"]) + ". "
                    "REGRA: se reconhecer que esta desprovido de capacidade, nao ignore — "
                    "pesquise, desenvolva, teste, valide e aprimore. Hook atualizado em self-research-tasks.json."
                )
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
