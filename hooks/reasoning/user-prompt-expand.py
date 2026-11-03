#!/usr/bin/env python3
"""
Reasoning Expand — UserPromptSubmit Hook.

Analisa a mensagem do usuario SEM matchers restritivos.
Todo o contexto e considerado: verbos, adjetivos, area, historico, tom.

Injeta sugestoes de skills relevantes e incentiva raciocinio profundo
antes de responder.

Fail-open: qualquer erro resulta em saida 0.
"""
import sys
import json
import os

def load_skill_index():
    for p in [
        os.path.join(os.getcwd(), "configs", "skills-index.json"),
        os.path.expanduser("~/.config/opencode/skills-index.json"),
    ]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
    return []

def suggest_skills(prompt, index):
    """Busca skills semanticamente relacionadas ao prompt (sem matchers rigidos)."""
    prompt_lower = prompt.lower()
    words = [w for w in prompt_lower.split() if len(w) > 3]
    scored = []
    for s in index:
        sid = s.get("id", "")
        sdesc = s.get("description", "").lower()
        score = 0
        # score por palavra em comum (nome + descricao)
        for w in words:
            if w in sid.lower():
                score += 3
            if w in sdesc:
                score += 1
        if score > 0:
            scored.append((score, sid, s.get("description", "")[:100]))
    scored.sort(reverse=True)
    return scored[:5]

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)

        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            data = {"raw": input_data}

        prompt = data.get("prompt", data.get("message", data.get("user_message", "")))
        if not prompt and isinstance(input_data, str):
            prompt = input_data

        index = load_skill_index()
        suggestions = suggest_skills(prompt, index)

        suggestion_text = ""
        if suggestions:
            lines = [f"  - {sid}: {desc}" for _, sid, desc in suggestions]
            suggestion_text = "\nSkills candidatas (verifique e carregue as aplicaveis):\n" + "\n".join(lines)

        # Detectar sinais amplos de necessidade
        broad_signals = {
            "pesquise": "deep research",
            "busque": "busca web/fetch",
            "crie": "criacao de artefato/recurso",
            "melhore": "auto-upgrade",
            "aprimore": "auto-upgrade",
            "corrija": "debugging sistematico",
            "explique": "explicacao (+ visual inline)",
            "mostre": "visualizacao (artefato + panel)",
            "teste": "TDD/autoteste",
            "valide": "validacao/reinterpretacao",
            "instale": "instalacao de skill",
            "baixe": "download/fetch",
            "hook": "desenvolvimento de hooks",
            "skill": "gestao de skills",
        }
        detected = []
        prompt_lower = prompt.lower()
        for signal, capability in broad_signals.items():
            if signal in prompt_lower:
                detected.append(capability)
        detected = list(dict.fromkeys(detected))

        detected_text = ""
        if detected:
            detected_text = f"\nCapacidades acionadas pelo contexto: {', '.join(detected)}."

        additional = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    "[EXPANSAO DE CONTEXTO] Analise a mensagem do usuario amplamente. "
                    "Nao filtre por matchers rigidos: considere verbos, adjetivos, area, tom, historico. "
                    "ANTES de responder: "
                    "1) Releia a mensagem pelo menos 2x. "
                    "2) Raciocine em ciclos sem ordem definida. "
                    "3) Se ha skill aplicavel, CARREGUE-A e aplique. "
                    "4) Se suspeita de gap de capacidade, registre tarefa de pesquisa. "
                    "5) Se o usuario foi vago, faca a escolha mais razoavel e depois PecA feedback."
                    + suggestion_text
                    + detected_text
                )
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
