#!/usr/bin/env python3
"""grain_measure.py - measure the camera's noise so synthetic layers can match it (FX grain amount, size, colour noise).
  python3 grain_measure.py video_or_image [--frames 8]
Method: take flat patches (lowest local gradient), high-pass them, measure std per channel and the noise correlation length.
Prints: luma_sigma (0..1), chroma_sigma, grain_size_px, and suggested  FX.apply(... {pass:'grain', amount:A, size:S})  numbers.
"""
import argparse, json, sys
import numpy as np, cv2

def frames(path, n):
    if path.lower().endswith((".png", ".jpg", ".jpeg")): yield cv2.imread(path); return
    cap = cv2.VideoCapture(path); N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in np.linspace(0, max(0, N - 1), n).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i)); ok, f = cap.read()
        if ok: yield f

def measure(f, P=32, keep=24):
    f = f.astype(np.float32) / 255; H, W = f.shape[:2]; g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); ycc = cv2.cvtColor(f, cv2.COLOR_BGR2YCrCb)
    cand = []
    for y in range(0, H - P, P):
        for x in range(0, W - P, P):
            p = g[y:y + P, x:x + P]; gr = np.abs(cv2.Sobel(cv2.GaussianBlur(p, (0, 0), 1.5), cv2.CV_32F, 1, 0)).mean() + np.abs(cv2.Sobel(cv2.GaussianBlur(p, (0, 0), 1.5), cv2.CV_32F, 0, 1)).mean()
            if .06 < p.mean() < .94: cand.append((gr, y, x))
    cand.sort(); sig, sigc, cors = [], [], []
    for _, y, x in cand[:keep]:
        for ch, store in ((0, sig), (1, sigc), (2, sigc)):
            p = ycc[y:y + P, x:x + P, ch]; hp = p - cv2.GaussianBlur(p, (0, 0), 2.5); store.append(float(hp.std()) * 1.07)
        hp = g[y:y + P, x:x + P] - cv2.GaussianBlur(g[y:y + P, x:x + P], (0, 0), 3); hp -= hp.mean()
        if hp.std() > 1e-5:
            ac = np.fft.irfft2(np.abs(np.fft.rfft2(hp)) ** 2, s=hp.shape); ac /= ac[0, 0]; cors.append(float((ac[0, :6] > .37).sum() or 1))
    return (np.median(sig) if sig else 0), (np.median(sigc) if sigc else 0), (np.median(cors) if cors else 1)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("--frames", type=int, default=8); a = ap.parse_args()
    R = [measure(f) for f in frames(a.src, a.frames) if f is not None]
    if not R: sys.exit("no frames")
    l, c, s = [float(np.median([r[i] for r in R])) for i in range(3)]
    out = dict(luma_sigma=round(l, 4), chroma_sigma=round(c, 4), grain_size_px=round(s, 2), note="sigma on 0..1 scale of the high-passed flat areas (denoised footage reads near 0.002; phone low light 0.02-0.05)",
               suggestion=dict(grain_amount=round(min(.35, l * 4.2), 3), grain_size=round(max(1, s), 1), chroma_amount=round(min(.3, c * 3), 3)))
    print(json.dumps(out, indent=1))
main()
