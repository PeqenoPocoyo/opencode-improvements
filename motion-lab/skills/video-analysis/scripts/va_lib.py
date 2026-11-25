"""va_lib.py - shared helpers for video-analysis (ffprobe, frame grab, labels, sheet rendering). Needs ffmpeg/ffprobe, numpy, opencv-python."""
import json, os, subprocess, math
import numpy as np, cv2

def sh(cmd, **kw): return subprocess.run(cmd, capture_output=True, **kw)

def probe(path):
    r = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path], text=True); j = json.loads(r.stdout or "{}")
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), None); a = next((s for s in j.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v: raise SystemExit(f"no video stream in {path}")
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd: rot = int(sd["rotation"])
    rot = rot or int((v.get("tags") or {}).get("rotate", 0))
    w, h = int(v["width"]), int(v["height"])
    if abs(rot) in (90, 270): w, h = h, w
    num, den = (str(v.get("avg_frame_rate", "30/1")).split("/") + ["1"])[:2]; fps = float(num) / float(den or 1) if float(den or 1) else 30.0
    dur = float(j.get("format", {}).get("duration") or v.get("duration") or 0)
    return dict(path=os.path.abspath(path), duration=dur, fps=round(fps, 3), width=w, height=h, rotation=rot, has_audio=bool(a), vcodec=v.get("codec_name"), size_mb=round(os.path.getsize(path) / 1e6, 2))

def fmt_t(t, ms=True):
    t = max(0.0, float(t)); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    body = f"{m:02d}:{s:04.1f}" if ms else f"{m:02d}:{int(s):02d}"
    return f"{h}:{body}" if h else body

def parse_t(x):
    """'83.4' | '1:23.4' | '1:02:03' -> seconds"""
    if isinstance(x, (int, float)): return float(x)
    p = str(x).split(":"); v = 0.0
    for q in p: v = v * 60 + float(q)
    return v

def grab(video, t, width=None, crop=None, info=None):
    """One BGR frame at time t (seconds). crop = (x,y,w,h) in 0..1 fractions of the (rotated) frame. width = output width px (aspect kept)."""
    vf = []
    if crop:
        x, y, w, h = crop; vf.append(f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y}")
    if width: vf.append(f"scale={int(width)}:-2:flags=lanczos")
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0, t):.3f}", "-i", video, "-frames:v", "1"] + (["-vf", ",".join(vf)] if vf else []) + ["-f", "image2pipe", "-vcodec", "png", "-"]
    r = sh(cmd)
    if not r.stdout:  # past the end: try slightly earlier
        r = sh(["ffmpeg", "-v", "error", "-ss", f"{max(0, t - .5):.3f}", "-i", video, "-frames:v", "1"] + (["-vf", ",".join(vf)] if vf else []) + ["-f", "image2pipe", "-vcodec", "png", "-"])
    im = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR) if r.stdout else None
    return im

def grab_many(video, times, width=None, crop=None, workers=8):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(workers) as ex: return list(ex.map(lambda t: grab(video, t, width, crop), times))

def put_label(img, text, pos="tl", color=(255, 255, 255), bg=(0, 0, 0), scale=None, alpha=.72):
    h, w = img.shape[:2]; sc = scale or max(.45, w / 700); th = max(1, int(sc * 2)); (tw, tx), base = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, sc, th); pad = int(6 * sc + 3)
    x = pad if "l" in pos else w - tw - 3 * pad; y = pad + tx if "t" in pos else h - pad
    ov = img.copy(); cv2.rectangle(ov, (x - pad // 2, y - tx - pad // 2), (x + tw + pad // 2, y + base + pad // 2), bg, -1); cv2.addWeighted(ov, alpha, img, 1 - alpha, 0, img)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, sc, color, th, cv2.LINE_AA); return img

KIND_COLOR = {"scene_start": (60, 60, 235), "end": (200, 160, 60), "peak": (40, 170, 250), "fill": (140, 140, 140), "ctx": (110, 110, 110), "zoom": (90, 200, 90)}  # BGR

def pick_cols(n, aspect, long_side=1568):
    best = None
    for c in range(1, n + 1):
        r = math.ceil(n / c); a = (c * aspect) / r
        score = abs(math.log(a / 1.35)) + (c * r - n) * .06
        if best is None or score < best[0]: best = (score, c)
    return best[1]

def render_sheet(tiles, labels, kinds=None, cols=None, long_side=1568, strip=None, pad=4, title=None):
    """tiles: list of BGR images (None = missing). labels: list of str. kinds: list of KIND_COLOR keys. strip: optional BGR image appended under the grid (timeline)."""
    ok = [t for t in tiles if t is not None]
    if not ok: raise SystemExit("no frames could be extracted")
    ar = ok[0].shape[1] / ok[0].shape[0]; n = len(tiles); cols = cols or pick_cols(n, ar); rows = math.ceil(n / cols)
    tw = int((long_side - pad * (cols + 1)) / cols); th = int(tw / ar); W = pad + cols * (tw + pad); H = pad + rows * (th + pad)
    sheet = np.full((H, W, 3), 24, np.uint8)
    for i, im in enumerate(tiles):
        r, c = divmod(i, cols); x, y = pad + c * (tw + pad), pad + r * (th + pad)
        if im is None: cv2.putText(sheet, "no frame", (x + 8, y + th // 2), cv2.FONT_HERSHEY_SIMPLEX, .6, (80, 80, 255), 1); continue
        t = cv2.resize(im, (tw, th), interpolation=cv2.INTER_AREA); k = (kinds or [None] * n)[i]
        if k: cv2.rectangle(t, (0, 0), (tw - 1, th - 1), KIND_COLOR.get(k, (140, 140, 140)), 3 if k != "ctx" else 1)
        put_label(t, labels[i] + (f"  [{k.replace('_', ' ').upper()}]" if k in ("scene_start", "ctx") else ""), "tl", scale=max(.42, tw / 520))
        sheet[y:y + th, x:x + tw] = t
    if strip is not None:
        s = cv2.resize(strip, (W, int(strip.shape[0] * W / strip.shape[1]))); sheet = np.vstack([sheet, s])
    if title:
        hb = np.full((34, sheet.shape[1], 3), 14, np.uint8); cv2.putText(hb, title, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, .7, (255, 255, 255), 2, cv2.LINE_AA); sheet = np.vstack([hb, sheet])
    return sheet

def save_jpg(img, path, q=88):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True); cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, q]); return path
