#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse Write/Edit - exige decision.json antes do primeiro codigo. Fail-open em erros internos; bloqueia so violacao de regra."""
import sys, os, json
try:
    raw = sys.stdin.read()
    if not raw:
        sys.exit(0)
    try:
        data = json.loads(raw)
    except Exception:
        sys.exit(0)
    payload = data.get("tool_input", data) or {}
    path = str(payload.get("file_path") or payload.get("path") or "")
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".cs", ".rb", ".php", ".c", ".cpp", ".h", ".html", ".css"):
        sys.exit(0)
    ws = os.environ.get("WORKSPACE") or os.getcwd()
    if os.path.exists(os.path.join(ws, "decision.json")):
        sys.exit(0)
    sys.stderr.write("[dev-handler] BLOQUEADO: decision.json ausente. Escreva o trace de Avaliando e o decision.json (chosen/rejected/risks/verify) antes do primeiro arquivo de codigo.\n")
    sys.exit(2)
except SystemExit:
    raise
except Exception:
    pass
sys.exit(0)
