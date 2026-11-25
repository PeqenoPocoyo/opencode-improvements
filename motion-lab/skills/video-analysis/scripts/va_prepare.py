#!/usr/bin/env python3
"""va_prepare.py - STEP 1. Scan a video of ANY length in constant memory and write analysis/ (manifest.json + timeline.npz).
  python3 va_prepare.py video.mp4 [--out analysis] [--max-frames 4000] [--fast auto|on|off]
It measures (never judges): scene cuts, per-moment visual change ("novelty"), brightness, audio loudness/silences/peaks, container facts.
Cost is bounded: analysis frames <= --max-frames (the sampling rate is lowered for long videos). --fast on decodes keyframes only (auto: only for videos > 20 min whose keyframes are <= ~10 s apart; otherwise every frame is decoded).
"""
import argparse, json, os, sys, time
import numpy as np, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from va_lib import *

AW, AH = 64, 36

def scan_video(path, dur, max_frames, fast):
    af = min(8.0, max_frames / max(dur, 1e-3)); af = max(af, 0.02)
    cmd = ["ffmpeg", "-v", "error"] + (["-skip_frame", "nokey"] if fast else []) + ["-i", path, "-an", "-vf", f"fps={af:.6f},scale={AW}:{AH}:flags=area,format=rgb24", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=AW * AH * 3 * 64); sz = AW * AH * 3; prev = None; luma, diff, hd, hists = [], [], [], []; prevh = None
    while True:
        b = p.stdout.read(sz)
        if len(b) < sz: break
        f = np.frombuffer(b, np.uint8).reshape(AH, AW, 3); g = f.astype(np.float32).mean(2) / 255
        h = np.concatenate([np.histogram(f[:, :, c], bins=12, range=(0, 256))[0] for c in range(3)]).astype(np.float32); h /= h.sum() / 3
        luma.append(float(g.mean())); diff.append(float(np.abs(g - prev).mean()) if prev is not None else 0.0); hd.append(float(0.5 * np.abs(h - prevh).sum() / 3) if prevh is not None else 0.0); prev, prevh = g, h
    p.wait(); return af, np.array(luma), np.array(diff), np.array(hd)

def keyframe_dense(path):
    """keyframe-only decoding is only trustworthy when keyframes are frequent (<= ~10 s apart); check the first 2 minutes."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-skip_frame", "nokey", "-read_intervals", "%+120", "-show_entries", "frame=pts_time", "-of", "csv=p=0", path], capture_output=True, text=True)
    return len([x for x in r.stdout.split() if x.strip()]) >= 12

def scan_audio(path, dur, win=0.5):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"]; p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1 << 20); n = int(8000 * win) * 4; db = []
    while True:
        b = p.stdout.read(n)
        if len(b) < 8: break
        x = np.frombuffer(b[:len(b) // 4 * 4], np.float32); db.append(20 * np.log10(max(1e-5, float(np.sqrt((x * x).mean())))))
    p.wait(); return np.array(db), win

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--out", default="analysis"); ap.add_argument("--max-frames", type=int, default=4000); ap.add_argument("--fast", default="auto"); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); info = probe(a.video); dur = info["duration"]; t0 = time.time()
    fast = (a.fast == "on") or (a.fast == "auto" and dur > 1200 and keyframe_dense(a.video))
    af, luma, diff, hd = scan_video(a.video, dur, a.max_frames, fast); n = len(luma)
    if n < 2: sys.exit("could not decode frames")
    tt = np.arange(n) / af
    # --- cuts: both the histogram and the pixel change must spike (robust vs motion / flicker)
    s = hd.copy(); med = np.median(s); mad = np.median(np.abs(s - med)) + 1e-4; thr = max(.22, med + 9 * mad)
    cuts = [i for i in range(1, n) if hd[i] > thr and diff[i] > .06 and hd[i] >= hd[max(0, i - 1)] and (i + 1 >= n or hd[i] >= hd[i + 1] * .8)]
    merged = []
    for i in cuts:
        if not merged or tt[i] - merged[-1] > 0.6: merged.append(float(tt[i]))   # at least 0.6 s between cuts
    cut_t = [round(c, 2) for c in merged]
    # --- novelty mass (information to look at): robust to cut spikes
    nov = diff + hd; cap = np.percentile(nov, 97) if n > 20 else nov.max(); mass = np.clip(nov, 0, cap) + .12 * nov.mean() + 1e-6
    bounds = [0.0] + cut_t + [dur]; scenes = []
    for k in range(len(bounds) - 1):
        a0, b0 = bounds[k], bounds[k + 1]
        if b0 - a0 < 0.05: continue
        i0, i1 = int(a0 * af), max(int(a0 * af) + 1, int(b0 * af)); scenes.append(dict(i=len(scenes), t0=round(a0, 2), t1=round(b0, 2), mean_motion=round(float(diff[i0:i1].mean()), 4), mean_luma=round(float(luma[i0:i1].mean()), 3)))
    audio = None; adb = None
    if info["has_audio"]:
        adb, win = scan_audio(a.video, dur); sil = []; run = None
        for i, v in enumerate(adb):
            if v < -50:
                run = i if run is None else run
            else:
                if run is not None and (i - run) * win >= 1.0: sil.append([round(run * win, 1), round(i * win, 1)])
                run = None
        if run is not None and (len(adb) - run) * win >= 1.0: sil.append([round(run * win, 1), round(len(adb) * win, 1)])
        jumps = np.diff(adb); top = np.argsort(-jumps)[:12] if len(jumps) else []
        peaks = sorted([round(float((int(i) + 1) * win), 1) for i in top if jumps[i] > 8])
        audio = dict(window_s=win, mean_db=round(float(adb.mean()), 1), max_db=round(float(adb.max()), 1), silences=sil[:200], peak_onsets=peaks, note="numbers only: nobody here can hear; see reference/failure-modes.md")
    np.savez_compressed(os.path.join(a.out, "timeline.npz"), t=tt, luma=luma, diff=diff, hd=hd, mass=mass, adb=adb if adb is not None else np.array([]), awin=0.5)
    # downsampled timeline for humans/agents (<= 600 points)
    k = max(1, n // 600); ds = lambda x: [round(float(v), 4) for v in x[:len(x) // k * k].reshape(-1, k).mean(1)]
    man = dict(version=1, video=info, analysis=dict(analysis_fps=round(af, 4), frames=int(n), fast_keyframes_only=fast, seconds_to_analyse=round(time.time() - t0, 1)), cuts=cut_t, scenes=scenes,
               stats=dict(mean_motion=round(float(diff.mean()), 4), p95_motion=round(float(np.percentile(diff, 95)), 4), mean_luma=round(float(luma.mean()), 3), cuts_per_minute=round(len(cut_t) / max(dur / 60, 1e-3), 2), static_share=round(float((diff < .004).mean()), 3)),
               audio=audio, timeline=dict(step_s=round(k / af, 3), motion=ds(diff), luma=ds(luma)))
    json.dump(man, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    print(f"{info['duration']:.1f}s video, {len(scenes)} scenes, {len(cut_t)} cuts, motion {man['stats']['mean_motion']}, analysed {n} frames in {man['analysis']['seconds_to_analyse']}s{' (keyframes only)' if fast else ''} -> {a.out}/manifest.json")
main()
