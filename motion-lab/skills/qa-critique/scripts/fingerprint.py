#!/usr/bin/env python3
"""fingerprint.py - numeric "soul" of a finished video, to prove a new video does not look/feel like the previous ones.

  python3 fingerprint.py video.mp4 [--name my-video] [--history .motion/style-history.json] [--add] [--threshold 0.18] [--json out.json]
Fingerprint = dominant palette (hue histogram 12 bins + saturation + lightness), contrast, edge density (texture), motion energy mean/variance (rhythm),
cut rate, centre-vs-edge brightness (composition), and colourfulness. Distance 0..1 between two fingerprints. Exit 1 if any of the last 5 entries is closer than --threshold.
History format is shared with style-dna/dna_generate.py:  {"version":1,"entries":[{"name","date","dna","fingerprint"}]}  (an entry may carry only dna, only fingerprint, or both).
CALIBRATION NOTE: the threshold 0.18 is heuristic (not tuned on a large corpus). Treat it as a tripwire: <0.10 almost surely "same soul", 0.10-0.18 look at the contact sheets, >0.25 clearly different.
"""
import argparse, colorsys, datetime, json, os, subprocess, sys
import numpy as np

def frames(video, fps=3, size=(108, 192), maxn=120):
    w, h = size
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps},scale={w}:{h}:flags=area,format=rgb24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    n = w * h * 3; out = []
    while len(out) < maxn:
        b = p.stdout.read(n)
        if len(b) < n: break
        out.append(np.frombuffer(b, np.uint8).reshape(h, w, 3))
    p.kill(); return out

def fingerprint(video):
    fr = frames(video)
    if len(fr) < 3: raise SystemExit("video too short / unreadable")
    A = np.stack(fr).astype(np.float32) / 255; mx = A.max(-1); mn = A.min(-1); v = mx; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = A[..., 0], A[..., 1], A[..., 2]; d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    w8 = (s * v).ravel(); hb = np.histogram(hue.ravel(), bins=12, range=(0, 1), weights=w8)[0]; hb = hb / max(hb.sum(), 1e-6)
    luma = (0.2126 * r + 0.7152 * g + 0.0722 * b); gx = np.abs(np.diff(luma, axis=2)).mean(); gy = np.abs(np.diff(luma, axis=1)).mean()
    mot = np.abs(np.diff(luma, axis=0)).mean(axis=(1, 2)); H, W = luma.shape[1:]; c = luma[:, H // 4:3 * H // 4, W // 4:3 * W // 4].mean(); edge = luma.mean()
    rg = r - g; yb = .5 * (r + g) - b; colorful = float(np.sqrt(rg.std() ** 2 + yb.std() ** 2) + .3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2))
    cuts = float((mot > max(.05, mot.mean() + 3 * mot.std())).sum()) / (len(fr) / 3)
    return dict(hue=[round(float(x), 4) for x in hb], sat=round(float(s.mean()), 4), light=round(float(v.mean()), 4), contrast=round(float(luma.std()), 4), edges=round(float((gx + gy) / 2), 4), motion_mean=round(float(mot.mean()), 4),
                motion_var=round(float(mot.std()), 4), cuts_per_s=round(cuts, 3), centre_bias=round(float(c - edge), 4), colorful=round(colorful, 4), frames=len(fr))

def distance(a, b):
    ha, hb = np.array(a["hue"]), np.array(b["hue"]); hd = 0.5 * np.abs(ha - hb).sum()                  # 0..1 total variation on hue bins
    sc = lambda k, s: min(1.0, abs(a[k] - b[k]) / s)
    parts = [(hd, 3.0), (sc("sat", .5), 1.0), (sc("light", .6), 1.5), (sc("contrast", .3), 1.0), (sc("edges", .08), 1.0), (sc("motion_mean", .06), 1.5), (sc("motion_var", .08), 1.0), (sc("cuts_per_s", 1.5), 0.7), (sc("centre_bias", .2), 0.5), (sc("colorful", .5), 0.8)]
    return float(sum(x * w for x, w in parts) / sum(w for _, w in parts))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--name"); ap.add_argument("--history", default=".motion/style-history.json"); ap.add_argument("--add", action="store_true"); ap.add_argument("--threshold", type=float, default=.18); ap.add_argument("--json")
    a = ap.parse_args(); fp = fingerprint(a.video); print(json.dumps(fp))
    if a.json: json.dump(fp, open(a.json, "w"), indent=1)
    hist = json.load(open(a.history)) if os.path.exists(a.history) else {"version": 1, "entries": []}; bad = []
    for e in hist["entries"][-5:]:
        if e.get("fingerprint"): d = distance(fp, e["fingerprint"]); print(f"  distance to {e.get('name')}: {d:.3f}"); (bad.append((e.get("name"), d)) if d < a.threshold else None)
    if a.add:
        os.makedirs(os.path.dirname(a.history) or ".", exist_ok=True); nm = a.name or os.path.basename(a.video)
        ex = next((e for e in hist["entries"] if e.get("name") == nm), None)
        if ex: ex["fingerprint"] = fp
        else: hist["entries"].append(dict(name=nm, date=datetime.date.today().isoformat(), dna=None, fingerprint=fp))
        json.dump(hist, open(a.history, "w"), indent=1); print("added to", a.history)
    if bad: print("TOO CLOSE to:", ", ".join(f"{n} ({d:.2f})" for n, d in bad), "-> change palette family, motion personality or texture; re-render."); sys.exit(1)
    print("OK: sufficiently different from recent videos." if any(e.get("fingerprint") for e in hist["entries"]) else "No previous fingerprints to compare.")

if __name__ == "__main__": main()
