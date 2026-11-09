#!/usr/bin/env python3
"""qa_video.py - one-command technical QA of a rendered mp4: format, duration, black/frozen/flash frames, motion pacing, audio levels, clipping, silence, A/V sync hints.
  python3 qa_video.py video.mp4 [--expect-w 1080 --expect-h 1920 --expect-fps 30 --expect-dur 15] [--events events.json] [--json report.json]
Exit 1 if any FAIL. WARN = review. Needs ffmpeg/ffprobe + numpy. Output is also written as <video>.qa.md next to the file.
"""
import argparse, json, os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def sh(cmd): return subprocess.run(cmd, capture_output=True, text=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--expect-w", type=int); ap.add_argument("--expect-h", type=int); ap.add_argument("--expect-fps", type=float); ap.add_argument("--expect-dur", type=float); ap.add_argument("--events"); ap.add_argument("--json")
    a = ap.parse_args(); R = []; add = lambda lv, k, m: R.append((lv, k, m))
    j = json.loads(sh(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels,duration:format=duration,size,bit_rate", "-of", "json", a.video]).stdout or "{}")
    vs = next((s for s in j.get("streams", []) if s["codec_type"] == "video"), None); au = next((s for s in j.get("streams", []) if s["codec_type"] == "audio"), None)
    if not vs: print("FAIL no video stream"); sys.exit(1)
    n, d = vs["r_frame_rate"].split("/"); fps = float(n) / float(d); dur = float(j["format"]["duration"]); w, h = vs["width"], vs["height"]
    add("INFO", "format", f"{w}x{h} @ {fps:g} fps, {dur:.2f}s, {vs['codec_name']} {vs.get('pix_fmt')}, {int(j['format'].get('size', 0)) / 1e6:.1f} MB")
    if a.expect_w and w != a.expect_w or a.expect_h and h != a.expect_h: add("FAIL", "size", f"expected {a.expect_w}x{a.expect_h}")
    if a.expect_fps and abs(fps - a.expect_fps) > .01: add("FAIL", "fps", f"expected {a.expect_fps}")
    if a.expect_dur and abs(dur - a.expect_dur) > 0.12: add("WARN", "duration", f"expected {a.expect_dur}s, got {dur:.2f}s")
    if vs.get("pix_fmt") not in ("yuv420p", "yuvj420p"): add("WARN", "pix_fmt", "pix_fmt is not yuv420p: some players/social apps will reject or show wrong colours")
    if w % 2 or h % 2: add("FAIL", "even-dims", "odd dimensions break H.264")
    # picture
    try:
        from frame_diff import energy_series
        t, E, Lm = energy_series(a.video, 10)
        dead_thr = max(.0015, np.percentile(E, 90) * .03); run = 0; longest = 0; at = 0
        for i, e in enumerate(E):
            run = run + 1 if e < dead_thr else 0
            if run > longest: longest, at = run, i
        if longest / 10 > 1.5: add("WARN", "dead-time", f"{longest / 10:.1f}s with almost no motion ending at {at / 10:.1f}s (idle holds feel amateur; add drift/typing/camera)")
        bl = int((Lm < .03).sum()); fl = int((Lm > .93).sum())
        if bl > 3: add("WARN", "black", f"{bl / 10:.1f}s of near-black frames (intentional?)")
        if fl > 3: add("WARN", "flash", f"{fl / 10:.1f}s near-white frames (photosensitivity: flashes > 3/s are unsafe)")
        flick = int(((np.abs(np.diff(Lm)) > .18).sum()))
        if flick > 6: add("WARN", "flicker", f"{flick} large luminance jumps: check strobing")
        if len(E) > 12:
            add("INFO", "motion", f"mean motion {E.mean():.4f}; first-second energy {E[:10].mean():.4f} vs rest {E[10:].mean():.4f}" + ("" if E[:10].mean() > E[10:].mean() * .6 else "  -> weak hook: first second is calmer than the rest"))
            if E[:10].mean() < E[10:].mean() * .6: add("WARN", "hook", "first second has less motion than the rest: the opening needs a stronger hook")
        else: add("INFO", "motion", f"mean motion {E.mean():.4f} (clip shorter than ~1.2 s: hook check skipped)")
    except Exception as ex: add("WARN", "picture", f"motion analysis failed: {ex}")
    # audio
    if au:
        r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
        I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
        if I: lufs = float(I[-1]); add("INFO", "loudness", f"{lufs:.1f} LUFS" + (f", true peak {TP[-1]} dBFS" if TP else ""));  add("WARN", "loudness-range", "outside -20..-11 LUFS: too quiet/loud for social") if not -20 <= lufs <= -11 else None
        if TP and float(TP[-1]) > -0.5: add("FAIL", "clipping", f"true peak {TP[-1]} dBFS > -0.5: distortion risk")
        sd = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-af", "silencedetect=n=-50dB:d=0.7", "-f", "null", "-"]).stderr; sil = re.findall(r"silence_start: ([\d.]+)", sd)
        if sil and len(sil) > 3: add("WARN", "silence", f"{len(sil)} silent gaps (starts {', '.join(sil[:5])}s): intentional?")
        # first-second audio presence
        s0 = sh(["ffmpeg", "-hide_banner", "-nostats", "-t", "1.0", "-i", a.video, "-af", "volumedetect", "-f", "null", "-"]).stderr; mv = re.findall(r"max_volume: (-?[\d.]+) dB", s0)
        if mv and float(mv[0]) < -40: add("WARN", "audio-hook", "no audible sound in the first second")
    else: add("WARN", "audio", "no audio stream")
    # events <-> picture sync hint
    if a.events and os.path.exists(a.events):
        ev = json.load(open(a.events)); evs = ev if isinstance(ev, list) else ev.get("events", []); times = sorted(float(e["t"]) for e in evs if "t" in e)
        if times:
            fr = 1 / fps; off = [round((x / fr) - round(x / fr), 2) for x in times]; bad = [x for x, o in zip(times, off) if abs(o) > .35]
            add("INFO", "events", f"{len(times)} events, density {len(times) / dur:.1f}/s")
            if len(times) / dur > 5: add("WARN", "event-density", "more than 5 events/s: sound will mush; thin out")
            if bad: add("INFO", "event-frame-alignment", f"{len(bad)} events fall mid-frame (sync_cues aligns them +6 ms to the next frame boundary)")
    out = [f"# QA report - {os.path.basename(a.video)}\n"] + [f"- **{lv}** `{k}` {m}" for lv, k, m in R]
    open(a.video + ".qa.md", "w").write("\n".join(out)); print("\n".join(f"{lv:5} {k:18} {m}" for lv, k, m in R))
    if a.json: json.dump([dict(level=lv, key=k, msg=m) for lv, k, m in R], open(a.json, "w"), indent=1)
    sys.exit(1 if any(lv == "FAIL" for lv, _, _ in R) else 0)

if __name__ == "__main__": main()
