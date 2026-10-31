#!/usr/bin/env python3
"""
Skill Evolver Hook — PostToolUse/PreToolUse hook.

Dispara quando uma skill é usada (skill tool) ou quando SKILL.md é editado.
Injeta contexto para o agente considerar evolução contínua da skill.

Também registra uso em skill-usage.log para auto-expansão de triggers.

Fail-open: qualquer erro resulta em saída 0.
"""
import sys
import os
import json
import re
from datetime import datetime

WORKSPACE = os.environ.get("WORKSPACE", os.getcwd())
LOGS_DIR = os.path.join(WORKSPACE, ".claude", "logs")
USAGE_LOG = os.path.join(LOGS_DIR, "skill-usage.log")
EVOLVER = os.path.join(WORKSPACE, "scripts", "skill-evolver.py")


def log_usage(skill_id, tool_name):
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "skill": skill_id,
            "tool": tool_name,
        }
        with open(USAGE_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def detect_skill_from_input(data):
    """Detecta skill_id a partir do input da tool."""
    # skill tool
    if isinstance(data, dict):
        # skill tool call
        if data.get("skill") or data.get("id"):
            return data.get("skill") or data.get("id")
        # Write/Edit em SKILL.md
        path = data.get("file_path") or data.get("path") or ""
        if "SKILL.md" in str(path):
            # extrai nome do diretório pai
            parts = str(path).replace("\\", "/").split("/")
            for i, p in enumerate(parts):
                if p == "skills" and i + 1 < len(parts):
                    return parts[i + 1]
    return None


def main():
    try:
        raw = sys.stdin.read()
        if not raw:
            sys.exit(0)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"raw": raw}

        tool_name = data.get("tool_name", data.get("tool", ""))
        tool_input = data.get("tool_input", data)
        skill_id = detect_skill_from_input(tool_input if isinstance(tool_input, dict) else data)

        # Registra uso se for skill tool
        if skill_id and ("skill" in tool_name.lower()):
            log_usage(skill_id, tool_name)

        # Se editou SKILL.md, sugere rodar evolver
        edited_skill_md = False
        path = ""
        if isinstance(tool_input, dict):
            path = tool_input.get("file_path") or tool_input.get("path") or ""
        if "SKILL.md" in str(path):
            edited_skill_md = True

        # Construir contexto
        msgs = []
        if skill_id:
            msgs.append(
                f"[SKILL EVOLVER] Skill '{skill_id}' detectada. "
                f"Considere: (1) a skill está atualizada? (2) faltam seções (exemplos, anti-padrões, triggers)? "
                f"(3) rode `python scripts/skill-evolver.py --evolve {skill_id}` para auditar/evoluir. "
            )
        if edited_skill_md:
            msgs.append(
                f"[SKILL EVOLVER] SKILL.md editado ({path}). "
                f"Rode `python scripts/skill-evolver.py --evolve <id> --apply` para validar e registrar a evolução. "
            )

        if not msgs:
            sys.exit(0)

        additional = {
            "hookSpecificOutput": {
                "hookEventName": data.get("hook_event_name", "PostToolUse"),
                "additionalContext": " ".join(msgs) + " Melhoria contínua: cada skill deve crescer com o uso.",
            }
        }
        print(json.dumps(additional, ensure_ascii=False))
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
