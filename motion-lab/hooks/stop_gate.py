#!/usr/bin/env python3
"""Stop hook: if a video was rendered in this session but the QA ritual was not completed (QA run, contact sheet, fingerprint), block the stop ONCE with a precise checklist.
Uses stop_hook_active to prevent infinite loops. Fails open."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_motion import *

def main():
    inp = read_input()
    if inp.get("stop_hook_active"): sys.exit(0)
    root = project_root(inp.get("cwd")); st = load_state(root)
    if not st.get("rendered"): sys.exit(0)
    missing = [n for k, n in (("qa", "qa_video.py"), ("sheet", "contact_sheet.py (and READ the PNG)"), ("fingerprint", "fingerprint.py --add")) if not st.get(k)]
    if not missing: sys.exit(0)
    block("[motion-lab stop gate] A video was rendered but these QA steps are missing: " + ", ".join(missing) + ". Run them, apply rubric.md (max 3 passes), then finish. In the final message include: file path, one-line description, known issues, and the 5 sound timestamps for the user to listen to.")
safe_main(main)
