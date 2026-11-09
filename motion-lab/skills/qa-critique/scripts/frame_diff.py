#!/usr/bin/env python3
"""frame_diff.py - motion energy over time: finds DEAD stretches (nothing moves), black/white frames, and jump cuts.
  python3 frame_diff.py video.mp4 [--fps 10] [--dead 1.2] [--json out.json]
Prints a per-second energy strip, dead zones (energy ~0 for > --dead seconds), black frames, and flash frames.
Importable: energy_series(video, fps) -> (times, energy 0..1, mean_luma)
"""
import argparse, json, subprocess, sys
import numpy as np

def read_frames(video, fps=10, size=(96, 170)):
    w, h = size
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps},scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    n = w * h
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield np.frombuffer(b, np.uint8).reshape(h, w).astype(np.float32) / 255
    p.wait()

def energy_series(video, fps=10):
    prev = None; E = []; Lm = []
    for f in read_frames(video, fps):
        Lm.append(float(f.mean())); E.append(0.0 if prev is None else float(np.abs(f - prev).mean())); prev = f
    t = np.arange(len(E)) / fps; return t, np.array(E), np.array(Lm)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--fps", type=float, default=10); ap.add_argument("--dead", type=float, default=1.2); ap.add_argument("--json")
    a = ap.parse_args(); t, E, Lm = energy_series(a.video, a.fps)
    if len(E) < 2: print("no frames"); sys.exit(1)
    dead_thr = max(0.0015, np.percentile(E, 90) * 0.03); dead = []; start = None
    for i, e in enumerate(E):
        if e < dead_thr and start is None: start = i
        if (e >= dead_thr or i == len(E) - 1) and start is not None:
            if (i - start) / a.fps >= a.dead: dead.append((round(start / a.fps, 2), round(i / a.fps, 2)))
            start = None
    black = [round(float(x), 2) for x in t[Lm < 0.03]][:20]; flash = [round(float(x), 2) for x in t[(Lm > 0.93)]][:20]
    spikes = [round(float(t[i]), 2) for i in range(1, len(E)) if E[i] > np.percentile(E, 97) * 1.0 and E[i] > 0.12][:20]
    sec = [float(E[int(s * a.fps):int((s + 1) * a.fps)].mean()) for s in range(int(t[-1]) + 1)]
    mx = max(sec) or 1; bars = "▁▂▃▄▅▆▇█"; strip = "".join(bars[min(7, int(v / mx * 7.99))] for v in sec)
    print(f"duration {t[-1]:.1f}s  mean motion {E.mean():.4f}  p90 {np.percentile(E, 90):.4f}\nenergy/sec: {strip}\ndead zones (> {a.dead}s still): {dead or 'none'}\nblack frames at: {black or 'none'}\nflash frames at: {flash or 'none'}\nhard-cut/spike times: {spikes or 'none'}")
    if a.json: json.dump(dict(duration=float(t[-1]), mean=float(E.mean()), p90=float(np.percentile(E, 90)), dead=dead, black=black, flash=flash, spikes=spikes, per_second=sec), open(a.json, "w"), indent=1)

if __name__ == "__main__": main()
