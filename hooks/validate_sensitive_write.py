#!/usr/bin/env python3
"""PreToolUse hook para Write - Valida escrita de arquivos sensíveis.

Bloqueia/alerta para escrita em .env, .secret, chaves privadas, id_rsa, etc.
Fail-open: se houver erro na validacao, permite a escrita (saída 0).
"""
import sys
import os
import json
import re

SENSITIVE_PATTERNS = [
    r"\.env(\.[\w-]+)?$",
    r"\.secret",
    r"\.pem$",
    r"\.key$",
    r"id_rsa",
    r"id_dsa",
    r"secrets?\.json$",
    r"credentials?\.json$",
    r"\.pfx$",
    r"\.p12$",
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
        
        # Tenta extrair o caminho do arquivo de diferentes estruturas
        file_path = ""
        if isinstance(data, dict):
            file_path = data.get("file_path", "") or data.get("path", "") or data.get("tool_input", {}).get("file_path", "")
        
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, file_path, re.IGNORECASE):
                print(f"⚠️  Arquivo sensível detectado: {file_path}", file=sys.stderr)
                # Não bloqueia, apenas alerta (fail-open permissivo)
                break
                
    except Exception:
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()
