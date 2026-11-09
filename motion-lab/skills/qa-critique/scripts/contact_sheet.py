#!/usr/bin/env python3
"""contact_sheet.py - sample N frames of a video into one labelled PNG so a model (or human) can LOOK at the whole film at once.
  python3 contact_sheet.py video.mp4 out.png [--n 24] [--cols 6] [--tile 270] [--times 0.5,1.2,...]
Needs ffmpeg + PIL. Frames are labelled with their timestamp. Read the PNG with the Read tool and critique with rubric.md.
"""
import argparse, json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,duration:format=duration", "-of", "json", path], capture_output=True, text=True)
    j = json.loads(r.stdout); s = j["streams"][0]; n, d = s["r_frame_rate"].split("/")
    dur = float(s.get("duration") or j["format"]["duration"]); return int(s["width"]), int(s["height"]), float(n) / float(d), dur

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("out"); ap.add_argument("--n", type=int, default=24); ap.add_argument("--cols", type=int, default=6); ap.add_argument("--tile", type=int, default=270); ap.add_argument("--times")
    a = ap.parse_args(); w, h, fps, dur = probe(a.video)
    ts = [float(x) for x in a.times.split(",")] if a.times else [dur * (i + .5) / a.n for i in range(a.n)]
    th = int(a.tile * h / w) if h >= w else int(a.tile * h / w); tw = a.tile; tiles = []
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate(ts):
            f = os.path.join(td, f"{i}.png"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1", "-vf", f"scale={tw}:{th}", f], check=False)
            tiles.append((t, Image.open(f).convert("RGB") if os.path.exists(f) else Image.new("RGB", (tw, th), (40, 0, 0))))
    rows = (len(tiles) + a.cols - 1) // a.cols; sheet = Image.new("RGB", (a.cols * tw, rows * th), (20, 20, 24)); d = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(tiles):
        x, y = (i % a.cols) * tw, (i // a.cols) * th; sheet.paste(im, (x, y)); d.rectangle([x, y, x + 62, y + 16], fill=(0, 0, 0)); d.text((x + 4, y + 2), f"{t:.2f}s", fill=(255, 255, 255))
    sheet.save(a.out); print(f"{a.out}: {len(tiles)} frames, {w}x{h} @ {fps:.2f} fps, {dur:.2f}s")

if __name__ == "__main__": main()
