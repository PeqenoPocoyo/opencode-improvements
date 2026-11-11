#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse Write/Edit - bloqueia relatorio final sem budget.json valido ou com orcamento estourado (exceto exhaustive). Fail-open em erros internos."""
import sys, os, json

REPORT_NAMES = ("research-report.md", "knowledge-map.md")

def main():
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
        base = os.path.basename(path)
        ws = os.environ.get("WORKSPACE") or os.getcwd()
        if base == "budget.json":
            sys.exit(0)
        if base not in REPORT_NAMES:
            sys.exit(0)
        budget_path = os.path.join(ws, "budget.json")
        if not os.path.exists(budget_path):
            sys.stderr.write("[research-lab] BLOQUEADO: budget.json ausente. Rode depth-router primeiro (niveis: quick/standard/deep/exhaustive).\n")
            sys.exit(2)
        b = json.load(open(budget_path, encoding="utf-8"))
        level = str(b.get("level", "standard")).lower()
        if level == "exhaustive":
            sys.exit(0)
        bud = b.get("budget", {})
        used = b.get("consumed", {})
        ms, us = int(bud.get("max_searches", 0) or 0), int(used.get("searches", 0) or 0)
        if ms and us >= ms:
            sys.stderr.write("[research-lab] BLOQUEADO: orcamento de buscas esgotado (%d/%d). Sintetize com o knowledge-map ou suba o nivel explicitamente.\n" % (us, ms))
            sys.exit(2)
        mc, uc = int(bud.get("max_context_tokens", 0) or 0), int(used.get("context_tokens", 0) or 0)
        if mc and uc >= mc:
            sys.stderr.write("[research-lab] BLOQUEADO: orcamento de contexto esgotado (%d/%d tokens). Sintetize.\n" % (uc, mc))
            sys.exit(2)
    except SystemExit:
        raise
    except Exception:
        pass
    sys.exit(0)

if __name__ == "__main__":
    main()
