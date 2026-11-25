#!/usr/bin/env python3
"""selftest.py - synthetic 24 s video with known cuts (6,12,18 s) -> run the pipeline -> assert. Usage: python3 selftest.py [--keep]"""
import json, os, subprocess, sys, tempfile, shutil
import numpy as np, cv2
H = os.path.dirname(os.path.abspath(__file__)); tmp = tempfile.mkdtemp(prefix="va_selftest_"); ok = True
def check(c, m):
    global ok; print(("PASS " if c else "FAIL ") + m); ok = ok and bool(c)
W, Hh, FPS = 640, 360, 30; raw = os.path.join(tmp, "raw.mp4"); vw = cv2.VideoWriter(raw, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, Hh))
for i in range(24 * FPS):
    t = i / FPS; f = np.zeros((Hh, W, 3), np.uint8)
    if t < 6: f[:] = (160, 70, 30); cv2.circle(f, (int(60 + t / 6 * 500), 180), 40, (60, 220, 250), -1)
    elif t < 12: g = np.tile(np.linspace(60, 200, W, dtype=np.uint8), (Hh, 1)); f[:] = np.dstack([g, g // 2 + 40, 255 - g]); cv2.putText(f, "Big Title", (150, 190), cv2.FONT_HERSHEY_DUPLEX, 1.6, (255, 255, 255), 3)
    elif t < 18:
        f[:] = (40, 40, 200)
        for k in range(8): x = int((t * 400 + k * 90) % W); cv2.rectangle(f, (x, k * 44), (x + 50, k * 44 + 30), (255, 255, 255), -1)
    else: f[:] = (30, 30, 30); cv2.rectangle(f, (40, 40), (600, 320), (60, 60, 60), -1); cv2.putText(f, "Save" if t < 21 else "Saved!", (470, 297), cv2.FONT_HERSHEY_SIMPLEX, .7, (200, 200, 200), 2)
    vw.write(f)
vw.release(); vid = os.path.join(tmp, "v.mp4"); subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", vid], check=True)
out = os.path.join(tmp, "an"); r = subprocess.run([sys.executable, os.path.join(H, "va_run.py"), vid, "--out", out, "--question", "selftest"], capture_output=True, text=True); check(r.returncode == 0, "pipeline runs (prepare, plan, sheets)")
man = json.load(open(os.path.join(out, "manifest.json"))); check(all(any(abs(c - k) < .5 for c in man["cuts"]) for k in (6, 12, 18)) and len(man["cuts"]) == 3, f"cuts at 6/12/18 s (got {man['cuts']})")
plan = json.load(open(os.path.join(out, "plan.json"))); check(len(plan["overview"]["tiles"]) >= 12 and os.path.exists(os.path.join(out, "sheets", "overview.jpg")), "overview sheet written")
check(any(t["kind"] == "scene_start" for t in plan["chunks"][0]["tiles"]), "scene-start tiles forced")
rep = {"chunk_id": "C01", "summary": "s", "events": [{"t": 6.2, "tile": plan["chunks"][0]["tiles"][2]["id"], "kind": "scene", "what": "title scene", "confidence": .9, "seen": True}, {"t": 99, "tile": "x", "kind": "ui", "what": "bad", "confidence": .9, "seen": True}, {"t": 14, "tile": plan["chunks"][0]["tiles"][3]["id"], "kind": "action", "what": "bars move", "confidence": .4, "seen": False}], "unknowns": [], "needs_zoom": [{"t0": 20, "t1": 22, "mode": "pair", "why": "button"}]}
os.makedirs(os.path.join(out, "reports"), exist_ok=True); json.dump(rep, open(os.path.join(out, "reports", "C01.json"), "w")); json.dump({"summary": "s", "structure": []}, open(os.path.join(out, "reports", "overview.json"), "w"))
r = subprocess.run([sys.executable, os.path.join(H, "va_merge.py"), out], capture_output=True, text=True); fu = json.load(open(os.path.join(out, "followups.json")))
check(any(p["level"] == "error" and "outside chunk" in p["msg"] for p in fu["problems"]), "referee rejects out-of-range event")
check(len(fu["zoom_requests"]) >= 2, "weak/inferred events + needs_zoom become zoom requests")
r = subprocess.run([sys.executable, os.path.join(H, "va_zoom.py"), vid, "--followups", os.path.join(out, "followups.json"), "--out-dir", os.path.join(out, "zoom")], capture_output=True, text=True); check(r.returncode == 0, "zoom requests rendered")
r = subprocess.run([sys.executable, os.path.join(H, "va_merge.py"), out], capture_output=True, text=True); check(any(f.startswith("verify-") for f in os.listdir(os.path.join(out, "briefs"))), "verify briefs written after zoom")
print("ALL PASS" if ok else "SOME FAILED"); 
if "--keep" in sys.argv: print("kept", tmp)
else: shutil.rmtree(tmp, ignore_errors=True)
sys.exit(0 if ok else 1)
