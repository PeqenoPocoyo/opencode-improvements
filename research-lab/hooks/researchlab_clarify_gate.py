#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse Write/Edit - bloqueia research-report.md quando clarify.json ausente
(o teste de clareza nao foi feito) e budget.json existe. Fail-open em erros internos."""
import sys, os, json

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
        if os.path.basename(path) != "research-report.md":
            sys.exit(0)
        ws = os.environ.get("WORKSPACE") or os.getcwd()
        has_budget = os.path.exists(os.path.join(ws, "budget.json"))
        if not has_budget:
            sys.exit(0)  # sem pipeline iniciado, deixa o budget_guard decidir
        if not os.path.exists(os.path.join(ws, "clarify.json")):
            sys.stderr.write("[research-lab] BLOQUEADO: clarify.json ausente. Rode clarify-engine (Passo 0): teste de clareza - pergunte ao usuario OU, se ele dispensou questionamentos, dissolva a nebulosidade em modo autonomo antes de sintetizar.\n")
            sys.exit(2)
        try:
            c = json.load(open(os.path.join(ws, "clarify.json"), encoding="utf-8"))
        except Exception:
            sys.stderr.write("[research-lab] BLOQUEADO: clarify.json invalido.\n")
            sys.exit(2)
        mode = str(c.get("mode", "")).lower()
        if mode == "interactive" and not c.get("nebulosities"):
            # interactive sem nebulosidade registrada e aceitavel (pedido cristalino)
            sys.exit(0)
        if mode == "autonomous":
            pending = [n for n in c.get("nebulosities", []) if n.get("status") == "open"]
            if pending:
                sys.stderr.write("[research-lab] BLOQUEADO: modo autonomo com %d nebulosidade(s) ainda aberta(s). Persiga os questionamentos ate dissolver.\n" % len(pending))
                sys.exit(2)
    except SystemExit:
        raise
    except Exception:
        pass
    sys.exit(0)

if __name__ == "__main__":
    main()
