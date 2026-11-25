#!/usr/bin/env python3
"""va_sheets.py - STEP 3. Render the contact sheets listed in plan.json (overview + one per chunk) with burned-in timestamps, scene-start markers and a timeline strip.
  python3 va_sheets.py analysis/ [--only C03] [--width 1568] [--tile-width 640]
Each tile is labelled  t=mm:ss.s  <id>; red border = first frame of a scene; grey = context from the previous chunk. Sheets are JPEG, long side <= --width (agent image limits).
"""
import argparse, json, os, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from va_lib import *

def timeline_strip(tl, man, t0, t1, tiles, W=1568, H=120):
    img = np.full((H, W, 3), 30, np.uint8); af = man["analysis"]["analysis_fps"]; dur = man["video"]["duration"]; span = max(1e-3, t1 - t0)
    X = lambda t: int((t - t0) / span * (W - 20)) + 10
    i0, i1 = int(t0 * af), max(int(t0 * af) + 2, int(t1 * af)); d = tl["diff"][i0:i1]; tt = tl["t"][i0:i1]
    if len(d):
        sc = max(np.percentile(tl["diff"], 99), 1e-3)
        pts = np.array([[X(t), int(H - 32 - min(1, v / sc) * (H - 52))] for t, v in zip(tt, d)], np.int32)
        if len(pts) > 1: cv2.polylines(img, [pts], False, (40, 150, 250), 2, cv2.LINE_AA)
    adb = tl["adb"]
    if len(adb):
        win = float(tl["awin"]); j0, j1 = int(t0 / win), max(int(t0 / win) + 2, int(t1 / win)); a = adb[j0:j1]
        pts = np.array([[X((j0 + k) * win + win / 2), int(H - 32 - np.clip((v + 70) / 70, 0, 1) * (H - 52))] for k, v in enumerate(a)], np.int32)
        if len(pts) > 1: cv2.polylines(img, [pts], False, (90, 210, 110), 1, cv2.LINE_AA)
    for c in man["cuts"]:
        if t0 <= c <= t1: cv2.line(img, (X(c), 4), (X(c), H - 30), (60, 60, 235), 1)
    for k, t in enumerate(tiles):
        x = X(t["t"]); col = KIND_COLOR.get(t["kind"], (200, 200, 200)); cv2.line(img, (x, H - 30), (x, H - 18), col, 2); cv2.putText(img, t["id"].split("-")[-1] if "-" in t["id"] else t["id"][1:], (x - 8, H - 4), cv2.FONT_HERSHEY_SIMPLEX, .42, (230, 230, 230), 1, cv2.LINE_AA)
    cv2.putText(img, fmt_t(t0), (6, 14), cv2.FONT_HERSHEY_SIMPLEX, .45, (200, 200, 200), 1, cv2.LINE_AA); cv2.putText(img, fmt_t(t1), (W - 90, 14), cv2.FONT_HERSHEY_SIMPLEX, .45, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(img, "orange=motion  green=loudness  red=cut  ticks=tiles", (W // 2 - 200, 14), cv2.FONT_HERSHEY_SIMPLEX, .42, (150, 150, 150), 1, cv2.LINE_AA)
    return img

def build(video, man, tl, name, tiles, t0, t1, out, width, tile_w, title):
    ims = grab_many(video, [t["t"] for t in tiles], width=tile_w)
    sheet = render_sheet(ims, [f"t={fmt_t(t['t'])} {t['id']}" for t in tiles], [t["kind"] for t in tiles], long_side=width, strip=timeline_strip(tl, man, t0, t1, tiles, W=width), title=title)
    return save_jpg(sheet, out)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("analysis"); ap.add_argument("--only"); ap.add_argument("--width", type=int, default=1568); ap.add_argument("--tile-width", type=int, default=640); a = ap.parse_args()
    plan = json.load(open(os.path.join(a.analysis, "plan.json"))); man = json.load(open(os.path.join(a.analysis, "manifest.json"))); tl = np.load(os.path.join(a.analysis, "timeline.npz")); video = plan["video"]["path"]; done = []
    jobs = [("overview", plan["overview"]["tiles"], 0.0, plan["video"]["duration"], plan["overview"]["sheet"], "OVERVIEW")] + [(c["id"], c["tiles"], c["t0"], c["t1"], c["sheet"], f"{c['id']}  {fmt_t(c['t0'])}-{fmt_t(c['t1'])}") for c in plan["chunks"]]
    for name, tiles, t0, t1, rel, title in jobs:
        if a.only and name != a.only: continue
        done.append(build(video, man, tl, name, tiles, t0, t1, os.path.join(a.analysis, rel), a.width, a.tile_width, title))
    print(f"{len(done)} sheets written:"); [print("  " + d) for d in done]
main()
