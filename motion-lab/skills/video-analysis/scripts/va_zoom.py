#!/usr/bin/env python3
"""va_zoom.py - STEP 4 (on demand). Go deeper where a judging agent asked (needs_zoom) or where you are unsure. All modes write JPEG/PNG you can open.
  python3 va_zoom.py video.mp4 --at 83.4 [--crop 0.1,0.6,0.5,0.3] [--scale 2] -o z/at.png        one full-resolution frame (crop = x,y,w,h as fractions 0..1)
  python3 va_zoom.py video.mp4 --burst 83.4 --n 8 --step 0.0333 [--crop ...] -o z/burst.jpg      consecutive frames at a fixed step: SEE motion (speed, easing, overshoot)
  python3 va_zoom.py video.mp4 --window 80 90 --fps 4 [--max-tiles 20] -o z/win.jpg              dense look at a time window
  python3 va_zoom.py video.mp4 --pair 12.0 12.4 -o z/pair.jpg                                      two moments side by side + difference map (what changed?)
  python3 va_zoom.py video.mp4 --followups analysis/followups.json --out-dir analysis/zoom         run every needs_zoom request produced by va_merge.py
Burst/window frames carry labels  t=…  #k  and the pixel displacement of the biggest moving region between consecutive frames (px) when computable.
"""
import argparse, json, os, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from va_lib import *

def parse_crop(s): return tuple(float(x) for x in s.split(",")) if s else None

def disp(a, b):
    """rough displacement (px) of the dominant moving region between two frames: centroid shift of the absolute difference's two lobes is unreliable, so use phase correlation on gray."""
    try:
        g1 = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY).astype(np.float32); g2 = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY).astype(np.float32); (dx, dy), resp = cv2.phaseCorrelate(g1, g2); return (float(np.hypot(dx, dy)), float(resp))
    except Exception: return (0.0, 0.0)

def sheet_for(video, times, labels, crop, width, out, max_tiles, kinds=None, with_disp=False):
    ims = grab_many(video, times, width=width, crop=crop); outs = []
    for s in range(0, len(times), max_tiles):
        sl = slice(s, s + max_tiles); L = list(labels[sl])
        if with_disp:
            for i in range(s, min(len(times), s + max_tiles)):
                if i > 0 and ims[i] is not None and ims[i - 1] is not None and ims[i].shape == ims[i - 1].shape:
                    d, r = disp(ims[i - 1], ims[i]); L[i - s] += f"  d={d:.1f}px"
        sh_ = render_sheet(ims[sl], L, (kinds or ["zoom"] * len(times))[sl], long_side=1568)
        p = out if len(times) <= max_tiles else out.replace(".jpg", f"_{s // max_tiles + 1}.jpg"); outs.append(save_jpg(sh_, p))
    return outs

def do_pair(video, ta, tb, crop, out):
    A = grab(video, ta, crop=crop); B = grab(video, tb, crop=crop)
    if A is None or B is None: raise SystemExit("could not read frames")
    B = cv2.resize(B, (A.shape[1], A.shape[0])); d = cv2.absdiff(A, B).max(2); d = cv2.GaussianBlur(d, (0, 0), 2); hm = cv2.applyColorMap(np.clip(d.astype(np.float32) * 3, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
    tiles = [A, B, hm]; labs = [f"A t={fmt_t(ta)}", f"B t={fmt_t(tb)}", f"difference (bright = changed)  {100 * float((d > 25).mean()):.1f}% px"]
    return save_jpg(render_sheet(tiles, labs, ["zoom"] * 3, cols=3, long_side=1568), out)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--at", type=float); ap.add_argument("--burst", type=float); ap.add_argument("--n", type=int, default=8); ap.add_argument("--step", type=float, default=1 / 30)
    ap.add_argument("--window", nargs=2, type=float); ap.add_argument("--fps", type=float, default=4); ap.add_argument("--max-tiles", type=int, default=20); ap.add_argument("--pair", nargs=2, type=float)
    ap.add_argument("--crop"); ap.add_argument("--scale", type=float, default=1.0); ap.add_argument("--width", type=int, default=640); ap.add_argument("-o", "--out"); ap.add_argument("--followups"); ap.add_argument("--out-dir", default="zoom"); a = ap.parse_args()
    crop = parse_crop(a.crop); info = probe(a.video)
    if a.followups:
        fu = json.load(open(a.followups)); os.makedirs(a.out_dir, exist_ok=True)
        for f in fu.get("zoom_requests", []):
            fid, mode, t0, t1 = f["id"], f.get("mode", "burst"), f["t0"], f["t1"]; out = os.path.join(a.out_dir, f"{fid}.jpg"); cr = tuple(f["crop"]) if f.get("crop") else None
            if mode == "pair": do_pair(a.video, t0, t1, cr, out); f["images"] = [out]
            elif mode == "crop": t = (t0 + t1) / 2; im = grab(a.video, t, crop=cr or (.0, .0, 1., 1.)); cv2.imwrite(out.replace(".jpg", ".png"), im); f["images"] = [out.replace(".jpg", ".png")]
            else:
                span = max(t1 - t0, .1); n = 12; step = span / (n - 1); ts = [t0 + k * step for k in range(n)]; f["images"] = sheet_for(a.video, ts, [f"t={fmt_t(t, True)} #{k + 1}" for k, t in enumerate(ts)], cr, a.width, out, 12, with_disp=True)
        json.dump(fu, open(a.followups, "w"), indent=1); print(f"{len(fu.get('zoom_requests', []))} zoom requests rendered into {a.out_dir}"); return
    out = a.out or "zoom.jpg"
    if a.at is not None:
        im = grab(a.video, a.at, crop=crop, width=int(info["width"] * a.scale) if not crop else int(info["width"] * (crop[2]) * a.scale))
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); cv2.imwrite(out, im); print(out, im.shape[1], "x", im.shape[0])
    elif a.burst is not None:
        ts = [a.burst + k * a.step for k in range(a.n)]; print("\n".join(sheet_for(a.video, ts, [f"t={fmt_t(t)} #{k + 1}" for k, t in enumerate(ts)], crop, a.width, out, a.max_tiles, with_disp=True)))
    elif a.window:
        t0, t1 = a.window; ts = list(np.arange(t0, t1 + 1e-6, 1 / a.fps)); print("\n".join(sheet_for(a.video, ts, [f"t={fmt_t(t)}" for t in ts], crop, a.width, out, a.max_tiles)))
    elif a.pair: print(do_pair(a.video, a.pair[0], a.pair[1], crop, out))
    else: ap.error("choose one of --at / --burst / --window / --pair / --followups")
main()
