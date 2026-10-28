#!/usr/bin/env python3
"""Notification hook - Lida com notificações do agente OpenCode.

Exibe alertas, pedidos de aprovação e resumos de tarefas longas.
Fail-open: nunca bloqueia notificações.
"""
import sys
import os
import json
from datetime import datetime

def main():
    try:
        raw = sys.stdin.read()
        if not raw:
            sys.exit(0)
        
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            sys.exit(0)
        
        message = data.get("message", "") or data.get("tool_input", {}).get("message", "")
        level = data.get("level", "info")
        
        log_dir = os.path.join(os.environ.get("WORKSPACE", os.getcwd()), ".claude", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        event = {
            "hook": "Notification",
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        log_file = os.path.join(log_dir, "notifications.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
            
        # Exibe para o usuário (não bloqueante)
        if message:
            print(f"🔔 [{level.upper()}] {message}")
            
    except Exception:
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()
