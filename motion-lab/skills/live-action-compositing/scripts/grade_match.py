#!/usr/bin/env python3
"""grade_match.py - make a synthetic layer (render of a UI, cutout, title) sit inside live footage by matching colour statistics.
  python3 grade_match.py --ref footage_frame_or_video --layer layer.png --out layer_graded.png [--strength 0.6] [--keep-alpha] [--json grade.json]
Reinhard transfer in Lab: layer mean/std -> blended toward the footage's mean/std (strength 0..1). Black/white points are lifted to the footage's
(no pure black in live footage), and a gentle contrast match is applied. Prints the numbers so the same grade can be reproduced as canvas filters.
Footage-side measurement ignores the 5 % darkest and brightest pixels (clipping) and, if --mask is given, only that region.
"""
import argparse, json
import numpy as np, cv2

def load_ref(p):
    if p.lower().endswith((".png", ".jpg", ".jpeg")): return cv2.imread(p)
    cap = cv2.VideoCapture(p); N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fs = []
    for i in np.linspace(0, max(0, N - 1), 6).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i)); ok, f = cap.read(); fs.append(f) if ok else None
    return np.vstack([cv2.resize(f, (320, 180)) for f in fs])

def stats(lab, m=None):
    px = lab.reshape(-1, 3); 
    if m is not None: px = px[m.reshape(-1) > 0]
    L = px[:, 0]; lo, hi = np.percentile(L, 5), np.percentile(L, 95); k = (L >= lo) & (L <= hi); px = px[k] if k.sum() > 50 else px
    return px.mean(0), px.std(0) + 1e-3, float(np.percentile(L, 1)), float(np.percentile(L, 99))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ref", required=True); ap.add_argument("--layer", required=True); ap.add_argument("--out", required=True); ap.add_argument("--strength", type=float, default=.6); ap.add_argument("--json"); a = ap.parse_args()
    ref = cv2.cvtColor(load_ref(a.ref), cv2.COLOR_BGR2LAB).astype(np.float32); img = cv2.imread(a.layer, cv2.IMREAD_UNCHANGED); alpha = img[:, :, 3] if img.shape[2] == 4 else None; bgr = img[:, :, :3]
    lay = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32); mR, sR, loR, hiR = stats(ref); mL, sL, loL, hiL = stats(lay, alpha)
    s = a.strength; mean = mL + (mR - mL) * s; std = sL + (sR - sL) * s; out = (lay - mL) / sL * std + mean
    # lift blacks / roll whites toward the footage range
    L = out[:, :, 0]; lo2, hi2 = loL + (loR - loL) * s, hiL + (hiR - hiL) * s; out[:, :, 0] = lo2 + (L - loL) / max(1e-3, hiL - loL) * (hi2 - lo2)
    res = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    if alpha is not None: res = np.dstack([res, alpha])
    cv2.imwrite(a.out, res); rep = dict(layer_mean=[round(float(x), 1) for x in mL], ref_mean=[round(float(x), 1) for x in mR], layer_std=[round(float(x), 1) for x in sL], ref_std=[round(float(x), 1) for x in sR], black_point=[round(loL, 1), round(lo2, 1)], white_point=[round(hiL, 1), round(hi2, 1)], strength=s)
    if a.json: json.dump(rep, open(a.json, "w"), indent=1)
    print(json.dumps(rep, indent=1))
main()
