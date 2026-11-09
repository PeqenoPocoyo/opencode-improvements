#!/usr/bin/env python3
"""prep_footage.py - probe + normalise user footage so every later step is deterministic.
  python3 prep_footage.py clip.mp4 --out prep/ [--fps 30] [--height 1920] [--proxy 540] [--cuts 0.35]
Writes  prep/<name>.norm.mp4 (constant fps, rotation applied, yuv420p, square pixels)  prep/<name>.proxy.mp4 (small, for fast tracking)
        prep/<name>.thumbs.png (contact sheet of 12 frames)  prep/<name>.json (duration, fps, size, rotation, audio LUFS, scene cuts, luma/colour stats)
"""
import argparse, json, os, re, subprocess, sys
import numpy as np

def sh(cmd): return subprocess.run(cmd, capture_output=True, text=True)

def probe(path):
    r = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path]); j = json.loads(r.stdout or "{}")
    v = next((s for s in j.get("streams", []) if s["codec_type"] == "video"), None); a = next((s for s in j.get("streams", []) if s["codec_type"] == "audio"), None)
    if not v: sys.exit("no video stream")
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd: rot = int(sd["rotation"])
    rot = rot or int((v.get("tags") or {}).get("rotate", 0))
    num, den = (v.get("avg_frame_rate", "30/1").split("/") + ["1"])[:2]
    return dict(width=v["width"], height=v["height"], rotation=rot, fps=float(num) / float(den or 1), duration=float(j["format"].get("duration", 0)), has_audio=bool(a), vcodec=v.get("codec_name"))

def lufs(path):
    r = sh(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"]); m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); return float(m[-1]) if m else None

def cuts(path, thr):
    r = sh(["ffmpeg", "-i", path, "-vf", f"select='gt(scene,{thr})',metadata=print:file=-", "-an", "-f", "null", "-"]); return [round(float(x), 2) for x in re.findall(r"pts_time:([\d.]+)", r.stdout + r.stderr)]

def stats(path, n=12):
    import cv2
    cap = cv2.VideoCapture(path); N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fr = []; idx = np.linspace(0, max(0, N - 1), n).astype(int)
    for i in idx:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i)); ok, f = cap.read()
        if ok: fr.append(f)
    if not fr: return {}, None
    lab = [cv2.cvtColor(f, cv2.COLOR_BGR2LAB).reshape(-1, 3).mean(0) for f in fr]; luma = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).mean() / 255 for f in fr]
    h = fr[0].shape[0] // 3; w = int(fr[0].shape[1] * h / fr[0].shape[0]); sheet = np.vstack([np.hstack([cv2.resize(f, (w, h)) for f in fr[r * 4:(r + 1) * 4]]) for r in range(len(fr) // 4)]) if len(fr) >= 4 else fr[0]
    return dict(luma_mean=round(float(np.mean(luma)), 3), luma_range=[round(float(min(luma)), 3), round(float(max(luma)), 3)], lab_mean=[round(float(x), 1) for x in np.mean(lab, 0)]), sheet

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("clip"); ap.add_argument("--out", default="prep"); ap.add_argument("--fps", type=float, default=30); ap.add_argument("--height", type=int, default=1920); ap.add_argument("--proxy", type=int, default=540); ap.add_argument("--cuts", type=float, default=.35)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); name = os.path.splitext(os.path.basename(a.clip))[0]; info = probe(a.clip)
    norm = os.path.join(a.out, name + ".norm.mp4"); prox = os.path.join(a.out, name + ".proxy.mp4")
    sh(["ffmpeg", "-y", "-v", "error", "-i", a.clip, "-vf", f"fps={a.fps},scale=-2:{a.height},setsar=1,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", norm])
    sh(["ffmpeg", "-y", "-v", "error", "-i", norm, "-vf", f"scale=-2:{a.proxy}", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", prox])
    st, sheet = stats(norm)
    if sheet is not None:
        import cv2; cv2.imwrite(os.path.join(a.out, name + ".thumbs.png"), sheet)
    info.update(norm=norm, proxy=prox, loudness_lufs=lufs(a.clip) if info["has_audio"] else None, cuts=cuts(norm, a.cuts), **st)
    json.dump(info, open(os.path.join(a.out, name + ".json"), "w"), indent=1); print(json.dumps(info, indent=1))
main()
