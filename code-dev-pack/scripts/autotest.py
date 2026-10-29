#!/usr/bin/env python3
"""Autotest Runner — Executa testes de recursos do pacote.

Valida que skills, hooks, instruções e scripts funcionam
conforme seus cenários de teste.

Uso:
    python autotest.py --all
    python autotest.py --skill code-tdd
    python autotest.py --hook pre-write-quality
    python autotest.py --resource skills/code-tdd/SKILL.md
"""

import sys
import os
import json
import argparse
import subprocess
from datetime import datetime

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

PACK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_skill(skill_path):
    """Testa se uma skill tem a estrutura correta."""
    full_path = os.path.join(PACK_ROOT, skill_path)
    if not os.path.exists(full_path):
        return False, f"Arquivo não encontrado: {full_path}"
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # Verificar frontmatter
    if content.startswith('---'):
        checks.append(("Frontmatter presente", True))
    else:
        checks.append(("Frontmatter presente", False))
    
    # Verificar nome
    if 'name:' in content:
        checks.append(("Nome definido", True))
    else:
        checks.append(("Nome definido", False))
    
    # Verificar descrição
    if 'description:' in content:
        checks.append(("Descrição definida", True))
    else:
        checks.append(("Descrição definida", False))
    
    # Verificar princípio central
    if 'Princípio Central' in content or 'Principio Central' in content:
        checks.append(("Princípio central presente", True))
    else:
        checks.append(("Princípio central presente", False))
    
    # Verificar teste de reinterpretação
    if 'Teste de Reinterpretação' in content or 'Teste de Reinterpretacao' in content:
        checks.append(("Teste de reinterpretação presente", True))
    else:
        checks.append(("Teste de reinterpretação presente", False))
    
    # Verificar metadata
    if 'Metadata' in content:
        checks.append(("Metadata presente", True))
    else:
        checks.append(("Metadata presente", False))
    
    passed = all(c[1] for c in checks)
    details = "\n".join(f"  {'✅' if c[1] else '❌'} {c[0]}" for c in checks)
    return passed, details

def test_hook(hook_path):
    """Testa se um hook funciona (fail-open)."""
    full_path = os.path.join(PACK_ROOT, hook_path)
    if not os.path.exists(full_path):
        return False, f"Arquivo não encontrado: {full_path}"
    
    try:
        # Testar com input vazio (fail-open)
        result = subprocess.run(
            ['python', full_path],
            input='',
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "Hook fail-open OK (exit 0 com input vazio)"
        else:
            return False, f"Hook retornou exit {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "Timeout na execução do hook"
    except Exception as e:
        return False, str(e)

def test_all():
    """Testa todos os recursos do pacote."""
    results = []
    
    # Testar skills
    skills_dir = os.path.join(PACK_ROOT, 'skills')
    if os.path.exists(skills_dir):
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name, 'SKILL.md')
            if os.path.exists(skill_path):
                rel_path = os.path.relpath(skill_path, PACK_ROOT)
                passed, details = test_skill(rel_path)
                results.append((rel_path, passed, details))
    
    # Testar hooks
    hooks_dir = os.path.join(PACK_ROOT, 'hooks')
    if os.path.exists(hooks_dir):
        for hook_name in os.listdir(hooks_dir):
            if hook_name.endswith('.py'):
                rel_path = os.path.join('hooks', hook_name)
                passed, details = test_hook(rel_path)
                results.append((rel_path, passed, details))
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Autotest Runner')
    parser.add_argument('--all', action='store_true', help='Testar todos os recursos')
    parser.add_argument('--skill', type=str, help='Testar uma skill específica')
    parser.add_argument('--hook', type=str, help='Testar um hook específico')
    parser.add_argument('--resource', type=str, help='Testar um recurso específico')
    args = parser.parse_args()
    
    if args.all:
        results = test_all()
        print(f"\n{'='*60}")
        print(f"AUTOTEST — {len(results)} recursos testados")
        print(f"{'='*60}\n")
        passed_count = sum(1 for r in results if r[1])
        for path, passed, details in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {path}")
            print(details)
            print()
        print(f"{'='*60}")
        print(f"Resultado: {passed_count}/{len(results)} PASS")
        print(f"{'='*60}")
        sys.exit(0 if passed_count == len(results) else 1)
    
    elif args.skill:
        skill_path = f"skills/{args.skill}/SKILL.md"
        passed, details = test_skill(skill_path)
        print(f"{'✅ PASS' if passed else '❌ FAIL'} {skill_path}")
        print(details)
        sys.exit(0 if passed else 1)
    
    elif args.hook:
        hook_path = f"hooks/{args.hook}.py" if not args.hook.endswith('.py') else f"hooks/{args.hook}"
        passed, details = test_hook(hook_path)
        print(f"{'✅ PASS' if passed else '❌ FAIL'} {hook_path}")
        print(details)
        sys.exit(0 if passed else 1)
    
    elif args.resource:
        if args.resource.endswith('SKILL.md'):
            passed, details = test_skill(args.resource)
        elif args.resource.endswith('.py'):
            passed, details = test_hook(args.resource)
        else:
            print(f"Tipo de recurso não suportado: {args.resource}")
            sys.exit(1)
        print(f"{'✅ PASS' if passed else '❌ FAIL'} {args.resource}")
        print(details)
        sys.exit(0 if passed else 1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()