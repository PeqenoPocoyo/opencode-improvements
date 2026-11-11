# -*- coding: utf-8 -*-
"""Testes basicos dos hooks research-lab: python3 hooks/tests/test_hooks.py"""
import json, os, subprocess, sys, tempfile

HOOKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

def run(hook, payload=None, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run([PY, os.path.join(HOOKS, hook)], input=json.dumps(payload or {}),
                       capture_output=True, text=True, env=e)
    return p.returncode, p.stderr

def test_session_start_fail_open():
    rc, _ = run("researchlab_session_start.py", {})
    assert rc == 0, "session start deve ser fail-open"

def test_budget_guard_blocks_without_budget():
    d = tempfile.mkdtemp()
    rc, err = run("researchlab_budget_guard.py",
                  {"tool_input": {"file_path": os.path.join(d, "research-report.md"), "content": "x"}},
                  {"WORKSPACE": d})
    assert rc == 2, "deve bloquear sem budget.json: " + err
    assert "budget.json" in err

def test_budget_guard_allows_other_files():
    d = tempfile.mkdtemp()
    rc, err = run("researchlab_budget_guard.py",
                  {"tool_input": {"file_path": os.path.join(d, "outro.md"), "content": "x"}},
                  {"WORKSPACE": d})
    assert rc == 0

def test_budget_guard_exhaustive_never_blocks():
    d = tempfile.mkdtemp()
    json.dump({"level": "exhaustive", "budget": {"max_searches": 1}, "consumed": {"searches": 99}},
              open(os.path.join(d, "budget.json"), "w", encoding="utf-8"))
    rc, _ = run("researchlab_budget_guard.py",
                {"tool_input": {"file_path": os.path.join(d, "research-report.md"), "content": "x"}},
                {"WORKSPACE": d})
    assert rc == 0, "exhaustive nao tem teto"

def test_budget_guard_blocks_when_exhausted():
    d = tempfile.mkdtemp()
    json.dump({"level": "standard", "budget": {"max_searches": 5}, "consumed": {"searches": 5}},
              open(os.path.join(d, "budget.json"), "w", encoding="utf-8"))
    rc, err = run("researchlab_budget_guard.py",
                  {"tool_input": {"file_path": os.path.join(d, "research-report.md"), "content": "x"}},
                  {"WORKSPACE": d})
    assert rc == 2 and "esgotado" in err

def test_claim_gate_blocks_without_sources():
    d = tempfile.mkdtemp()
    rc, err = run("researchlab_claim_gate.py",
                  {"tool_input": {"file_path": os.path.join(d, "research-report.md"),
                                  "content": "# R\n\n## Fontes\n(nada)"}},
                  {"WORKSPACE": d})
    assert rc == 2 and "sources.json" in err

def test_claim_gate_blocks_without_fontes_section():
    d = tempfile.mkdtemp()
    json.dump({"sources": [{"id": 1}]}, open(os.path.join(d, "sources.json"), "w", encoding="utf-8"))
    rc, err = run("researchlab_claim_gate.py",
                  {"tool_input": {"file_path": os.path.join(d, "research-report.md"), "content": "# R sem fontes"}},
                  {"WORKSPACE": d})
    assert rc == 2 and "Fontes" in err

def test_claim_gate_allows_valid_report():
    d = tempfile.mkdtemp()
    json.dump({"sources": [{"id": 1}, {"id": 2}]}, open(os.path.join(d, "sources.json"), "w", encoding="utf-8"))
    rc, err = run("researchlab_claim_gate.py",
                  {"tool_input": {"file_path": os.path.join(d, "research-report.md"),
                                  "content": "# R\n\n## Fontes\n[1] x\n[2] y"}},
                  {"WORKSPACE": d})
    assert rc == 0, err

def test_stop_gate_fail_open():
    rc, _ = run("researchlab_stop_gate.py", {})
    assert rc == 0

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn(); print("PASS", fn.__name__)
        except AssertionError as e:
            failed += 1; print("FAIL", fn.__name__, "-", e)
    print("%d/%d pass" % (len(fns) - failed, len(fns)))
    sys.exit(1 if failed else 0)
