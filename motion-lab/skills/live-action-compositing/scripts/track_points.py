#!/usr/bin/env python3
"""track_points.py - planar tracking for pinning a screen/sticker/title onto a surface in footage.
  python3 track_points.py footage.mp4 --quad "x1,y1;x2,y2;x3,y3;x4,y4" --out track.json [--start 0] [--end 8] [--fps 30] [--smooth 5]
The quad (TL,TR,BR,BL, pixel coordinates in the first frame used) is the surface. Features inside it are tracked with Lucas-Kanade; a RANSAC homography
per step moves the quad. Output: per-frame quads + `reproj_err` (px) + `lost` flags. Use proxy video for speed and pass --scale if you tracked the proxy.
Consume in a scene:  quad = TRACK.frames[Math.round(t*fps)].quad  ->  Trans.matrix3dFromQuad(w,h,quad)  (or UI placed with CSS matrix3d).
Honest limits: fails on motion blur, occlusion > 40 %, textureless surfaces. When `lost` appears, re-seed with --start at that time or use manual keyframes.
"""
import argparse, json, sys
import numpy as np, cv2

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--quad", required=True); ap.add_argument("--out", required=True); ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float, default=1e9); ap.add_argument("--smooth", type=int, default=5); ap.add_argument("--scale", type=float, default=1.0, help="multiply output coords (proxy -> full-res)"); a = ap.parse_args()
    quad0 = np.array([[float(v) for v in p.split(",")] for p in a.quad.split(";")], np.float32)
    cap = cv2.VideoCapture(a.video); fps = cap.get(cv2.CAP_PROP_FPS) or 30; cap.set(cv2.CAP_PROP_POS_FRAMES, int(a.start * fps)); ok, f = cap.read()
    if not ok: sys.exit("cannot read start frame")
    g0 = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); mask = np.zeros_like(g0); cv2.fillConvexPoly(mask, quad0.astype(np.int32), 255)
    pts = cv2.goodFeaturesToTrack(g0, 200, .01, 7, mask=mask); 
    if pts is None or len(pts) < 8: sys.exit("not enough texture inside the quad (need >= 8 features)")
    quad = quad0.copy(); frames = [dict(t=round(a.start, 4), quad=quad.tolist(), err=0.0, lost=False)]; idx = int(a.start * fps); prev = g0; Hacc = np.eye(3)
    while True:
        ok, f = cap.read(); idx += 1
        if not ok or idx / fps > a.end: break
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, g, pts, None, winSize=(21, 21), maxLevel=3); good = st.reshape(-1) == 1; lost = False; err = 0.0
        if good.sum() >= 6:
            H, inl = cv2.findHomography(pts[good], nxt[good], cv2.RANSAC, 3.0)
            if H is not None:
                quad = cv2.perspectiveTransform(quad.reshape(-1, 1, 2), H).reshape(-1, 2); pr = cv2.perspectiveTransform(pts[good], H); err = float(np.linalg.norm(pr - nxt[good], axis=2).mean()); lost = (inl.sum() < 5) or err > 4
            else: lost = True
        else: lost = True
        # re-seed features every 20 frames inside the current quad
        if (idx % 20 == 0 or good.sum() < 25) and not lost:
            m = np.zeros_like(g); cv2.fillConvexPoly(m, quad.astype(np.int32), 255); p2 = cv2.goodFeaturesToTrack(g, 200, .01, 7, mask=m); pts = p2 if p2 is not None and len(p2) > 8 else nxt[good].reshape(-1, 1, 2)
        else: pts = nxt[good].reshape(-1, 1, 2) if good.sum() >= 6 else pts
        prev = g; frames.append(dict(t=round(idx / fps, 4), quad=quad.tolist(), err=round(err, 2), lost=bool(lost)))
    Q = np.array([fr["quad"] for fr in frames]); k = a.smooth
    if k > 1 and len(Q) > k:  # centred moving average on corner positions (removes tracker jitter)
        pad = k // 2; P = np.pad(Q, ((pad, pad), (0, 0), (0, 0)), mode="edge"); Q = np.mean([P[i:i + len(Q)] for i in range(k)], 0)
    for fr, q in zip(frames, Q): fr["quad"] = (q * a.scale).round(2).tolist()
    json.dump(dict(fps=fps, frames=frames, lost_frames=sum(fr["lost"] for fr in frames)), open(a.out, "w")); print(f"tracked {len(frames)} frames, lost {sum(fr['lost'] for fr in frames)}, mean err {np.mean([fr['err'] for fr in frames]):.2f}px -> {a.out}")
main()
