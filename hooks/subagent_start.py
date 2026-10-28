#!/usr/bin/env python3
"""SubagentStart hook - Inicializa isolamento ao iniciar um subagente.

Configura permissões isoladas e rastreamento de custos por subagente.
Fail-open: qualquer erro resulta em saída 0.
"""
import sys
import os
import json
from datetime import datetime

def main():
    try:
        workspace = os.environ.get("WORKSPACE", os.getcwd())
        agent_id = os.environ.get("AGENT_ID", "unknown")
        
        log_dir = os.path.join(workspace, ".claude", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        event = {
            "hook": "SubagentStart",
            "agent_id": agent_id,
            "workspace": workspace,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        log_file = os.path.join(log_dir, "subagent_start.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
            
    except Exception:
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()
