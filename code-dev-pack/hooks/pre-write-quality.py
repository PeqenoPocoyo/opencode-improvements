#!/usr/bin/env python3
"""Pre-Write Quality Hook — Valida código antes de escrever.

Analisa o código que está prestes a ser escrito e verifica:
- Segurança (secrets, injection, etc.)
- Qualidade (complexidade, duplicação, etc.)
- Testes (se há testes correspondentes)

Fail-open: qualquer erro resulta em saída 0 para nunca quebrar a sessão.
"""
import sys
import os
import json
import re
from datetime import datetime

def check_secrets(code):
    """Verifica se há secrets no código."""
    patterns = [
        r'(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*["\'][^"\']{8,}["\']',
        r'(?i)(aws_access_key|aws_secret)\s*[=:]\s*["\'][^"\']+["\']',
        r'(?i)(private[_-]?key)\s*[=:]\s*["\'][^"\']+["\']',
    ]
    for pattern in patterns:
        if re.search(pattern, code):
            return True, "Possível secret detectado"
    return False, None

def check_complexity(code):
    """Verifica complexidade do código."""
    lines = code.split('\n')
    if len(lines) > 100:
        return True, f"Código muito longo ({len(lines)} linhas)"
    # Verificar aninhamento
    max_indent = 0
    for line in lines:
        indent = len(line) - len(line.lstrip())
        max_indent = max(max_indent, indent)
    if max_indent > 24:
        return True, f"Aninhamento muito profundo ({max_indent} espaços)"
    return False, None

def check_tests(code, file_path):
    """Verifica se há testes correspondentes."""
    # Extrair nome da função/classe
    func_match = re.search(r'def\s+(\w+)', code)
    class_match = re.search(r'class\s+(\w+)', code)
    name = (func_match or class_match)
    if name:
        test_name = f"test_{name.group(1)}"
        # Verificar se existe arquivo de teste
        test_file = file_path.replace('.py', '_test.py').replace('src/', 'tests/')
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            if test_name not in content:
                return True, f"Teste '{test_name}' não encontrado em {test_file}"
    return False, None

def main():
    try:
        # Ler input do stdin (código a ser escrito)
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)
        
        try:
            data = json.loads(input_data)
            code = data.get('code', '')
            file_path = data.get('file_path', '')
        except json.JSONDecodeError:
            code = input_data
            file_path = ''
        
        warnings = []
        
        # Verificar secrets
        has_secret, msg = check_secrets(code)
        if has_secret:
            warnings.append(f"⚠️ {msg}")
        
        # Verificar complexidade
        is_complex, msg = check_complexity(code)
        if is_complex:
            warnings.append(f"⚠️ {msg}")
        
        # Verificar testes
        has_no_test, msg = check_tests(code, file_path)
        if has_no_test:
            warnings.append(f"⚠️ {msg}")
        
        # Reportar warnings (fail-open: nunca bloqueia)
        if warnings:
            for w in warnings:
                print(w, file=sys.stderr)
        
        sys.exit(0)
        
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()