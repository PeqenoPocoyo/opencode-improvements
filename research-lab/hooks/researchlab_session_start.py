#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionStart hook - injeta regras do research-lab + estado do pipeline. Fail-open."""
import sys, os, json
from datetime import datetime

def main():
    try:
        ws = os.environ.get("WORKSPACE", os.getcwd())
        log_dir = os.path.join(ws, ".research-lab")
        os.makedirs(log_dir, exist_ok=True)
        event = {
            "hook": "researchlab_session_start",
            "workspace": ws,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "has_budget": os.path.exists(os.path.join(ws, "budget.json")),
            "has_knowledge_map": os.path.exists(os.path.join(ws, "knowledge-map.md")),
        }
        with open(os.path.join(log_dir, "session_start.log"), "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        rules = os.path.join(os.path.dirname(__file__), "..", "instructions", "RESEARCH-LAB-RULES.md")
        if os.path.exists(rules):
            sys.stdout.write("[research-lab] regras em instructions/RESEARCH-LAB-RULES.md | "
                             "pipeline: depth-router -> question-graph -> source-hunter -> "
                             "context-weaver -> reasoning-chain -> claim-verifier -> synthesis-writer -> self-critique\n")
    except Exception:
        pass
    sys.exit(0)

if __name__ == "__main__":
    main()
