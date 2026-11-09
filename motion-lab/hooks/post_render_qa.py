#!/usr/bin/env python3
"""PostToolUse hook (matcher: Bash): after a render command, remind/force the QA ritual and record state.
 - render.mjs ... .png/--stills  -> reminder: Read the PNG and critique with rubric.md BEFORE rendering video
 - render.mjs ... .mp4           -> runs qa_video.py + frame_diff summary, prints results as context, marks state.rendered
 - qa_video.py / contact_sheet.py / fingerprint.py runs -> marks state so the Stop gate knows QA happened"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_motion import *

def main():
    inp = read_input(); ti = inp.get("tool_input") or {}; cmd = ti.get("command") or ""
    root = project_root(inp.get("cwd")); st = load_state(root); out = []
    if "contact_sheet.py" in cmd: st["sheet"] = True
    if "fingerprint.py" in cmd: st["fingerprint"] = True
    if "lint_scene.py" in cmd: st["lint"] = True
    if "qa_video.py" in cmd: st["qa"] = True
    if "render.mjs" in cmd:
        m = re.search(r"(\S+\.mp4)", cmd)
        if m and "--stills" not in cmd:
            st["rendered"] = True; st["qa"] = st.get("qa", False) if False else False; st["sheet"] = False; st["fingerprint"] = False
            vid = m.group(1)
            if not os.path.isabs(vid): vid = os.path.join(inp.get("cwd") or root, vid)
            final = vid if os.path.exists(vid) else None
            if final:
                try:
                    r = subprocess.run([sys.executable, os.path.join(PACK, "skills", "qa-critique", "scripts", "qa_video.py"), final], capture_output=True, text=True, timeout=120)
                    out.append("[motion-lab] auto QA of " + os.path.basename(final) + ":\n" + r.stdout.strip()); st["qa"] = True
                except Exception as e: out.append(f"[motion-lab] auto QA skipped: {e}")
            out.append("[motion-lab] NEXT: python3 skills/qa-critique/scripts/contact_sheet.py <video> sheet.png --n 24, then READ sheet.png and score with qa-critique/reference/rubric.md; then fingerprint.py. Do not deliver before.")
        elif "--stills" in cmd or re.search(r"\.png\b", cmd):
            out.append("[motion-lab] You just rendered stills: use the Read tool on the PNG now and critique legibility, hierarchy, palette vs dna.json. Fix before rendering video.")
    save_state(root, st)
    if out: context("\n".join(out))
safe_main(main)
