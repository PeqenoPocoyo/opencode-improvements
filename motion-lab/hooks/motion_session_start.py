#!/usr/bin/env python3
"""SessionStart hook: injects the 12 non-negotiable motion rules + current project state, so weak models start every session oriented."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_motion import *

def main():
    inp = read_input(); root = project_root(inp.get("cwd")); hist = os.path.join(root, ".motion", "style-history.json"); dna = os.path.join(root, "dna.json")
    n = 0
    try: n = len(json.load(open(hist)).get("entries", []))
    except Exception: pass
    state = f"Project: {root}\n- dna.json: {'present' if os.path.exists(dna) else 'MISSING (create it with skills/style-dna/scripts/dna_generate.py before any scene)'}\n- previous videos in ledger: {n}"
    context(f"""[motion-lab] Rules for video work (read skills/motion-director/SKILL.md first):
1. CONCEPT BEFORE CODE: one-sentence idea + 3 divergent DNAs (dna_generate.py --candidates 3). Pick one. No scene before dna.json.
2. Every scene obeys seek(t): no Math.random/Date/rAF/timers/CSS animation. Use Lab.*.
3. Colours, fonts, easing, textures, transitions, sound palette come from dna.json, never from habit. Do not use purple->cyan gradients or Inter-only type.
4. Max 3 different transitions; every cut has a reason (transitions-projections SKILL).
5. Declare Lab.ev(t,type) for every hit/transition so sound can be frame-locked (sound-design-pro).
6. Render stills first and LOOK at them (Read the png) before rendering video.
7. After each render: lint_scene -> qa_video -> contact_sheet (read it) -> fingerprint. Max 3 revision passes.
8. Hook in the first second: motion + subject + sound within 0.3 s.
9. Large jobs: split by file ownership with the agent-orchestration skill (max 2-3 parallel agents; verify files on disk).
10. You cannot hear audio: judge sound by sound-report numbers and give the user the 5 timestamps to check.
11. Never claim you saw/heard something you did not.
12. Finish with: file path, what it is in one sentence, known issues.
{state}""")
safe_main(main)
