#!/usr/bin/env python3
"""
Skill Quality Gate — PreToolUse hook para Write/Edit em SKILL.md.

Bloqueia (com warning) a escrita de uma SKILL.md se o score de qualidade
estiver abaixo do mínimo configurado. Permite override via env SKILL_GATE_OVERRIDE=1.

Fail-open: qualquer erro resulta em allow.
"""
import sys
import os
import json
import subprocess

WORKSPACE = os.environ.get("WORKSPACE", os.getcwd())
EVOLVER = os.path.join(WORKSPACE, "scripts", "skill-evolver.py")
MIN_SCORE = int(os.environ.get("SKILL_MIN_SCORE", "50"))


def main():
    try:
        raw = sys.stdin.read()
        if not raw:
            sys.exit(0)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            sys.exit(0)

        tool_input = data.get("tool_input", data)
        path = ""
        if isinstance(tool_input, dict):
            path = tool_input.get("file_path") or tool_input.get("path") or ""

        if "SKILL.md" not in str(path):
            sys.exit(0)

        # override
        if os.environ.get("SKILL_GATE_OVERRIDE") == "1":
            sys.exit(0)

        # extrair skill id do path
        parts = str(path).replace("\\", "/").split("/")
        skill_id = None
        for i, p in enumerate(parts):
            if p == "skills" and i + 1 < len(parts):
                skill_id = parts[i + 1]
                break
        if not skill_id:
            sys.exit(0)

        # rodar quality gate
        try:
            out = subprocess.run(
                [sys.executable, EVOLVER, "--gate", skill_id, "--min-score", str(MIN_SCORE), "--json"],
                capture_output=True, text=True, timeout=15, cwd=WORKSPACE,
            )
            res = json.loads(out.stdout) if out.stdout else {}
        except Exception:
            sys.exit(0)

        if res.get("pass"):
            # injeta contexto informativo
            additional = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": f"[QUALITY GATE] Skill '{skill_id}' score={res.get('score')} >= {MIN_SCORE}. OK.",
                }
            }
            print(json.dumps(additional))
            sys.exit(0)
        else:
            # não bloqueia (fail-open por padrão), mas avisa fortemente
            print(f"WARNING: Skill '{skill_id}' score={res.get('score')} < {MIN_SCORE}. {res.get('reason')}", file=sys.stderr)
            additional = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        f"[QUALITY GATE] ATENÇÃO: skill '{skill_id}' score={res.get('score')} < {MIN_SCORE}. "
                        f"Recomenda-se rodar `python scripts/skill-evolver.py --evolve {skill_id} --apply` antes de commitar. "
                        f"Override: SKILL_GATE_OVERRIDE=1."
                    ),
                }
            }
            print(json.dumps(additional))
            sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
