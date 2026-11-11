#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionEnd/Stop - registra fim de pesquisa e avisa se pipeline ficou aberto sem relatorio. Fail-open."""
import sys, os, json
from datetime import datetime

def main():
    try:
        ws = os.environ.get("WORKSPACE", os.getcwd())
        log_dir = os.path.join(ws, ".research-lab")
        os.makedirs(log_dir, exist_ok=True)
        has_budget = os.path.exists(os.path.join(ws, "budget.json"))
        has_report = os.path.exists(os.path.join(ws, "research-report.md"))
        with open(os.path.join(log_dir, "session_end.log"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"hook": "researchlab_stop", "ts": datetime.utcnow().isoformat() + "Z",
                                "has_budget": has_budget, "has_report": has_report}, ensure_ascii=False) + "\n")
        if has_budget and not has_report:
            sys.stderr.write("[research-lab] AVISO: pipeline de pesquisa aberto (budget.json) sem research-report.md. Faltou sintetizar?\n")
    except Exception:
        pass
    sys.exit(0)

if __name__ == "__main__":
    main()
