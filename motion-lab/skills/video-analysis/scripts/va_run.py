#!/usr/bin/env python3
"""va_run.py - one command for steps 1-3 (prepare -> plan -> sheets) and a printed dispatch list for the judging agents.
  python3 va_run.py video.mp4 --question "..." [--lens motion] [--budget standard|quick|deep] [--out analysis]
"""
import argparse, os, subprocess, sys, json
H = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--question", default="Describe what happens in this video, scene by scene, and what stands out."); ap.add_argument("--lens", default="general"); ap.add_argument("--budget", default="standard"); ap.add_argument("--out", default="analysis"); ap.add_argument("--chunks", type=int); a = ap.parse_args()
def run(*c):
    r = subprocess.run([sys.executable, *c]); 
    if r.returncode: sys.exit(r.returncode)
run(os.path.join(H, "va_prepare.py"), a.video, "--out", a.out)
run(os.path.join(H, "va_plan.py"), a.out, "--question", a.question, "--lens", a.lens, "--budget", a.budget, *(["--chunks", str(a.chunks)] if a.chunks is not None else []))
run(os.path.join(H, "va_sheets.py"), a.out)
plan = json.load(open(os.path.join(a.out, "plan.json")))
print("\n=== DISPATCH (judging agents: one brief + one image each; reports go to reports/) ===")
print(f"1. overview : {a.out}/briefs/overview.md  + {a.out}/sheets/overview.jpg  -> {a.out}/reports/overview.json   (run FIRST)")
for c in plan["chunks"]: print(f"2. {c['id']}      : {a.out}/briefs/{c['id']}.md + {a.out}/{c['sheet']}  -> {a.out}/reports/{c['id']}.json")
print(f"3. then     : python3 {H}/va_merge.py {a.out}   ->  zoom: python3 {H}/va_zoom.py {a.video} --followups {a.out}/followups.json --out-dir {a.out}/zoom   ->  merge again -> verify briefs -> synth brief")
