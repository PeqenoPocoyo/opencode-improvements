#!/usr/bin/env python3
"""Post-Write Test Hook — Roda testes após mudança.

Executa os testes correspondentes ao arquivo modificado e reporta
o resultado. Fail-open: nunca quebra a sessão.

Uso: echo '{"file_path": "src/module.py"}' | python post-write-test.py
"""
import sys
import os
import json
import subprocess
from datetime import datetime

def find_test_file(file_path):
    """Encontra o arquivo de teste correspondente."""
    base = os.path.basename(file_path)
    name, ext = os.path.splitext(base)
    dir_path = os.path.dirname(file_path)
    
    # Possíveis localizações
    candidates = [
        os.path.join(dir_path, f"test_{name}{ext}"),
        os.path.join(dir_path, f"{name}_test{ext}"),
        os.path.join(dir_path, "tests", f"test_{name}{ext}"),
        os.path.join("tests", f"test_{name}{ext}"),
    ]
    
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None

def run_tests(test_file):
    """Executa os testes e retorna o resultado."""
    try:
        # Detectar framework de teste
        if test_file.endswith('.py'):
            cmd = ['python', '-m', 'pytest', test_file, '-v', '--tb=short']
        elif test_file.endswith('.js') or test_file.endswith('.ts'):
            cmd = ['npx', 'jest', test_file, '--verbose']
        else:
            return None, "Framework de teste não detectado"
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout na execução dos testes"
    except Exception as e:
        return None, str(e)

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)
        
        try:
            data = json.loads(input_data)
            file_path = data.get('file_path', '')
        except json.JSONDecodeError:
            file_path = input_data.strip()
        
        if not file_path:
            sys.exit(0)
        
        test_file = find_test_file(file_path)
        if not test_file:
            print(f"⚠️ Nenhum teste encontrado para {file_path}", file=sys.stderr)
            sys.exit(0)
        
        success, output = run_tests(test_file)
        if success is None:
            print(f"⚠️ {output}", file=sys.stderr)
        elif success:
            print(f"✅ Testes passaram: {test_file}", file=sys.stderr)
        else:
            print(f"❌ Testes falharam: {test_file}", file=sys.stderr)
            print(output[:500], file=sys.stderr)
        
        sys.exit(0)
        
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()