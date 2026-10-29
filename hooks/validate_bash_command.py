#!/usr/bin/env python3
"""PreToolUse hook para Bash - Valida comandos perigosos ANTES de executar.

Bloqueia: rm -rf /, curl | bash, wget | sh, chmod 777, mkfs, dd, path traversal, etc.
Fail-open: se houver erro na validacao, permite a execucao (saida 0).

Baseado nas best practices de hooks (Claude Code docs + OWASP Agentic Top 10 2026).
"""
import sys
import os
import json
import re

DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"curl\s+.*\|\s*bash",
    r"wget\s+.*\|\s*sh",
    r"chmod\s+777",
    r"mkfs\.",
    r"dd\s+if=",
    r">\s*/dev/(sda|hda|vda)",
    r":\s*\(\s*\)\s*{\s*:\s*\|\s*:\s*&\s*}\s*;\s*",
    # Path traversal (OWASP / Claude Code hooks security best practices)
    r"\.\./",
    r"\.\.\\",
    # Command injection via eval/exec
    r"\beval\s*\(",
    r"\bexec\s*\(",
    # Exfiltration via curl/wget with data payload
    r"curl\s+.*-d\s+.*@",
]


def main():
    try:
        raw = sys.stdin.read()
        if not raw:
            sys.exit(0)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            sys.exit(0)

        command = data.get("command", "") or data.get("tool_input", {}).get("command", "")

        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                print(f"BLOQUEADO: comando perigoso detectado (padrao: {pattern})", file=sys.stderr)
                sys.exit(1)

    except Exception:
        pass

    # Fail-open: permite execucao
    sys.exit(0)


if __name__ == "__main__":
    main()