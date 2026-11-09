#!/usr/bin/env python3
"""PreToolUse hook (matcher: Write|Edit|MultiEdit): blocks scene files that break the seek(t) contract or ignore the DNA gate.
 - lint ERRORs in the new content -> block with the exact lines to fix
 - writing a NEW scene while dna.json is missing -> block ("generate the DNA first")
Warnings are passed to the model as stderr text only when blocking; otherwise silent (exit 0)."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_motion import *

def main():
    inp = read_input(); ti = inp.get("tool_input") or {}; path = ti.get("file_path") or ti.get("path") or ""
    content = ti.get("content")
    if content is None and ti.get("new_string") is not None:
        # Edit: reconstruct only if the file exists; otherwise lint the fragment loosely
        try:
            old = open(path, encoding="utf-8").read(); content = old.replace(ti.get("old_string", ""), ti["new_string"], 1) if ti.get("old_string") else old
        except Exception: content = ti.get("new_string")
    if content is None: sys.exit(0)
    if not is_scene_file(path, content): sys.exit(0)
    root = project_root(inp.get("cwd") or os.path.dirname(path))
    msgs = []
    if not os.path.exists(os.path.join(root, "dna.json")) and not os.path.exists(path):
        msgs.append("No dna.json in the project: write the Style DNA first (python3 skills/style-dna/scripts/dna_generate.py --candidates 3 --out-dir dnas/ ; choose ; --check), then create the scene.")
    try:
        from lint_scene import lint_text
        dna = None
        try:
            import json; dna = json.load(open(os.path.join(root, "dna.json")))
        except Exception: pass
        errs = [i for i in lint_text(content, path, dna) if i["level"] == "ERROR" and i["code"] not in ("NO_VIDEO", "NO_SEEK") ]
        # NO_VIDEO/NO_SEEK only matter for the final file; partial edits would false-positive
        full = ti.get("content") is not None
        if full: errs = [i for i in lint_text(content, path, dna) if i["level"] == "ERROR"]
        for e in errs[:8]: msgs.append(f"{e['code']} (line {e['line']}): {e['msg']}")
    except Exception as ex:
        sys.stderr.write(f"[lint skipped: {ex}]\n")
    if msgs: block("[motion-lab guard] Fix before writing this scene:\n- " + "\n- ".join(msgs))
safe_main(main)
