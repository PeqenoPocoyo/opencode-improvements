#!/usr/bin/env python3
"""
Reasoning Prime — SessionStart Hook.

Injeta instrucoes de raciocinio profundo no inicio da sessao.
Nao usa matchers: todo o contexto e considerado.
Fail-open: qualquer erro resulta em saida 0.
"""
import sys
import json
import os

def main():
    try:
        # Carregar indice de skills se disponivel
        skills_context = ""
        index_paths = [
            os.path.join(os.getcwd(), "configs", "skills-index.json"),
            os.path.expanduser("~/.config/opencode/skills-index.json"),
        ]
        for p in index_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        index = json.load(f)
                    if isinstance(index, list):
                        cats = {}
                        for s in index[:200]:  # primeiras 200 para contexto
                            sid = s.get("id", "")
                            desc = s.get("description", "")[:80]
                            cats[sid] = desc
                        skills_context = json.dumps(cats, ensure_ascii=False)[:3000]
                except Exception:
                    pass
                break

        additional = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    "MODO RACIOCINIO PROFUNDO ATIVADO. "
                    "Voce NAO deve responder rapidamente. Sempre: "
                    "1) Releia a mensagem do usuario multiplas vezes. "
                    "2) Navegue pelas skills disponiveis (configs/skills-index.json ou ~/.config/opencode/skills/) e carregue as relevantes. "
                    "3) Raciocine em multiplas etapas sem ordem definida: interpretar -> questionar -> testar hipotese -> reconsiderar -> reaprimorar -> revalidar. "
                    "4) Se suspeitar minimamente que precisa melhorar em algo, pesquise se alguma skill/hook/instrucao cobre essa lacuna. "
                    "5) Nao filtre por matchers — todo o contexto importa: verbos, adjetivos, area, historico. "
                    "6)Se reconhecer que esta desprovido de capacidade, mentalize um teste unitario para confirmar e depois desenvolva a melhoria. "
                    "7) Questione seus proprios argumentos E os do usuario antes de cada resposta. "
                    "Indice de skills disponiveis (amostra): " + skills_context
                )
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
