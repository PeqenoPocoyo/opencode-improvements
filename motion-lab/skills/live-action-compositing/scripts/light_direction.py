#!/usr/bin/env python3
"""light_direction.py - estimate where the light comes from in a frame, so cutouts/UI layers cast shadows the same way.
  python3 light_direction.py video_or_image [--frames 6]
Output: light_vec (unit vector pointing TOWARD the light, image coords x right / y down), angle_deg, softness (0 hard..1 very soft),
        key_to_fill (brightness ratio between lit and unlit halves), warmth (+warm/-cool), and ready-to-paste Collage/UI options.
Method: blurred luminance field -> intensity-weighted gradient (low-frequency shading), plus brightest-region centroid. Rough but consistent; a model cannot 'see' this reliably.
"""
import argparse, json, sys, math
import numpy as np, cv2

def frames(path, n):
    if path.lower().endswith((".png", ".jpg", ".jpeg")): yield cv2.imread(path); return
    cap = cv2.VideoCapture(path); N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in np.linspace(0, max(0, N - 1), n).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i)); ok, f = cap.read()
        if ok: yield f

def one(f):
    g = cv2.cvtColor(cv2.resize(f, (320, int(320 * f.shape[0] / f.shape[1]))), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255; b = cv2.GaussianBlur(g, (0, 0), 18)
    gx = cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=3).mean(); gy = cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=3).mean()
    ys, xs = np.mgrid[0:b.shape[0], 0:b.shape[1]]; w = np.clip(b - np.percentile(b, 80), 0, None); cx = (w * xs).sum() / (w.sum() + 1e-9) - b.shape[1] / 2; cy = (w * ys).sum() / (w.sum() + 1e-9) - b.shape[0] / 2
    v = np.array([gx * 40 + cx / b.shape[1] * 2, gy * 40 + cy / b.shape[0] * 2]); n = np.linalg.norm(v)
    h, wd = b.shape; halves = [b[:, :wd // 2].mean(), b[:, wd // 2:].mean(), b[:h // 2].mean(), b[h // 2:].mean()]
    edge = np.abs(cv2.Laplacian(cv2.GaussianBlur(g, (0, 0), 1), cv2.CV_32F)).mean(); mean = cv2.cvtColor(f, cv2.COLOR_BGR2RGB).reshape(-1, 3).mean(0)
    return v, n, max(halves) / max(1e-3, min(halves)), edge, float(mean[0] - mean[2])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("--frames", type=int, default=6); a = ap.parse_args()
    R = [one(f) for f in frames(a.src, a.frames) if f is not None]
    if not R: sys.exit("no frames")
    v = np.mean([r[0] for r in R], 0); n = float(np.linalg.norm(v)); u = v / n if n > 1e-6 else np.array([-.5, -.8]); u = u / np.linalg.norm(u)
    ratio = float(np.mean([r[2] for r in R])); soft = float(np.clip(1 - (ratio - 1) / 1.2, 0, 1)); warm = float(np.mean([r[4] for r in R]))
    out = dict(light_vec=[round(float(u[0]), 3), round(float(u[1]), 3)], angle_deg=round(math.degrees(math.atan2(-u[1], u[0])), 1), confidence=round(min(1, n / .25), 2), softness=round(soft, 2), key_to_fill=round(ratio, 2), warmth=round(warm, 1),
               paste=dict(collage_light=[round(float(u[0]), 2), round(float(u[1]), 2)], shadow_blur=round(10 + soft * 40), shadow_offset=round(8 + (1 - soft) * 26), shadow_alpha=round(.45 - soft * .2, 2)),
               note="confidence < 0.3 means flat/ambiguous lighting: use a soft shadow straight down and say so.")
    print(json.dumps(out, indent=1))
main()
