#!/usr/bin/env python3
"""Unit tests for the hooks: python3 hooks/tests/test_hooks.py  (runs each hook as a subprocess with JSON on stdin)."""
import json, os, subprocess, sys, tempfile
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
def run(hook, payload):
    r = subprocess.run([sys.executable, os.path.join(H, hook)], input=json.dumps(payload), capture_output=True, text=True); return r.returncode, r.stdout, r.stderr
ok = 0; fail = 0
def check(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print("PASS", name)
    else: fail += 1; print("FAIL", name, info)
with tempfile.TemporaryDirectory() as d:
    c, o, e = run("motion_session_start.py", {"cwd": d}); check("session_start prints rules", c == 0 and "CONCEPT BEFORE CODE" in o and "MISSING" in o, o)
    c, o, e = run("motion_prompt_router.py", {"prompt": "faz um vídeo de reels com interface de app", "cwd": d}); check("router fires on video prompt", c == 0 and "ui-in-video" in o and "motion-director" in o, o)
    c, o, e = run("motion_prompt_router.py", {"prompt": "qual a capital da França", "cwd": d}); check("router silent otherwise", c == 0 and o == "", o)
    bad = "<script>var x=Math.random();setInterval(f,1)</script>"
    c, o, e = run("pre_write_guard.py", {"cwd": d, "tool_name": "Write", "tool_input": {"file_path": d + "/scene.html", "content": "<html>window.VIDEO={};window.seek=t=>{};" + bad + "</html>"}}); check("guard blocks Math.random + no dna", c == 2 and "RANDOM" in e and "dna.json" in e, e)
    open(d + "/dna.json", "w").write("{}")
    good = "<html><script>Lab.init({render(t){}});Lab.ev(1,'tick')</script></html>"
    c, o, e = run("pre_write_guard.py", {"cwd": d, "tool_name": "Write", "tool_input": {"file_path": d + "/scene.html", "content": good}}); check("guard allows clean scene", c == 0, e)
    c, o, e = run("pre_write_guard.py", {"cwd": d, "tool_name": "Write", "tool_input": {"file_path": d + "/notes.md", "content": bad}}); check("guard ignores non-scene", c == 0, e)
    c, o, e = run("pre_write_guard.py", {}); check("guard fails open on empty input", c == 0)
    os.makedirs(d + "/.motion", exist_ok=True)
    c, o, e = run("stop_gate.py", {"cwd": d}); check("stop gate passes when nothing rendered", c == 0)
    json.dump({"rendered": True}, open(d + "/.motion/session-state.json", "w"))
    c, o, e = run("stop_gate.py", {"cwd": d}); check("stop gate blocks without QA", c == 2 and "contact_sheet" in e, e)
    c, o, e = run("stop_gate.py", {"cwd": d, "stop_hook_active": True}); check("stop gate no loop", c == 0)
    c, o, e = run("post_render_qa.py", {"cwd": d, "tool_input": {"command": "python3 contact_sheet.py a.mp4 s.png"}}); st = json.load(open(d + "/.motion/session-state.json")); check("post hook records sheet", st.get("sheet") is True, str(st))
    c, o, e = run("post_render_qa.py", {"cwd": d, "tool_input": {"command": "node render.mjs scene.html s.png --stills 1,2"}}); check("post hook reminds to read stills", "Read tool" in o, o)
print(f"\n{ok} passed, {fail} failed"); sys.exit(1 if fail else 0)
