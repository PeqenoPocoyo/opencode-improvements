#!/usr/bin/env python3
"""SessionEnd hook - Captura estado no fim de cada sessão OpenCode.

Fail-open: qualquer erro resulta em saída 0 para nunca quebrar a sessão.
Roda assíncrono (async: true) para não bloquear o encerramento.
"""
import sys
import os
import json
from datetime import datetime

def main():
    try:
        workspace = os.environ.get("WORKSPACE", os.getcwd())
        session_id = os.environ.get("SESSION_ID", "unknown")
        
        log_dir = os.path.join(workspace, ".claude", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        event = {
            "hook": "SessionEnd",
            "session_id": session_id,
            "workspace": workspace,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        log_file = os.path.join(log_dir, "session_end.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
            
    except Exception:
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()
