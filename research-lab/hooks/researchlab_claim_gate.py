#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse Write - bloqueia research-report.md sem secao Fontes ou sem sources.json (gate de citacao). Fail-open."""
import sys, os, json

def main():
    try:
        raw = sys.stdin.read()
        if not raw:
            sys.exit(0)
        data = json.loads(raw)
        payload = data.get("tool_input", data) or {}
        path = str(payload.get("file_path") or payload.get("path") or "")
        if os.path.basename(path) != "research-report.md":
            sys.exit(0)
        content = str(payload.get("content") or payload.get("new_string") or "")
        if content and "## Fontes" not in content:
            sys.stderr.write("[research-lab] BLOQUEADO: relatorio sem secao '## Fontes'. Toda entrega precisa de apendice de fontes.\n")
            sys.exit(2)
        ws = os.environ.get("WORKSPACE") or os.getcwd()
        sources = os.path.join(ws, "sources.json")
        if not os.path.exists(sources):
            sys.stderr.write("[research-lab] BLOQUEADO: sources.json ausente (nenhuma fonte coletada). Rode source-hunter.\n")
            sys.exit(2)
        s = json.load(open(sources, encoding="utf-8"))
        if len(s.get("sources", [])) < 1:
            sys.stderr.write("[research-lab] BLOQUEADO: 0 fontes em sources.json.\n")
            sys.exit(2)
    except SystemExit:
        raise
    except Exception:
        pass
    sys.exit(0)

if __name__ == "__main__":
    main()
