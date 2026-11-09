#!/usr/bin/env python3
"""qa_audio.py - measure the FINAL file (MP4 or WAV) the way the sound gate needs it. Never judge the intermediate WAV: AAC encode, mux offsets
and platform limits happen after it.

  python3 qa_audio.py out/final.mp4 --events out/events.json --profile social --png out/audio-qa.png --json out/audio-qa.json
  python3 qa_audio.py audio/mix.wav --events out/events.json --fps 30

Checks
  loudness     integrated LUFS (own BS.1770 + ffmpeg ebur128), true peak (own 4x oversampled + ffmpeg), LRA   social -14 +-1.5 / TP <= -1.0 ; conservative -16 +-1.5 / TP <= -4.0
  clipping     samples at full scale, runs of >= 3 consecutive clipped samples (audible)
  balance      share of energy: sub 20-120, low 120-400, mid, high 2-6k, air 6-16k   vs the references (65-90 % < 400 Hz, sub 30-73 %, 2-7 % > 2 kHz)
  structure    leading silence (first sound later than 0.25 s = "sound starts late"), trailing silence, silence ratio, onset density, mono-compat loss, L/R balance,
               audio vs video duration, audio start vs video start (mux offset)
  alignment    for every event of a transient type: the audio onset nearest the frame boundary of the event (window -50..+90 ms); error in ms
               (+ = late). Reports median, worst, share beyond 1 frame, share later than +45 ms, and how many events could not be measured
               (masked by something louder: that is a measurement limit, not a pass).
Exit code 1 when: no audio stream, true peak over the profile limit, or > 10 % of MEASURED events are worse than +-1 frame. Warnings do not fail.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audiolib as A  # noqa: E402

PROFILES = {"social": dict(lufs=-14.0, tol=1.5, tp=-1.0), "conservative": dict(lufs=-16.0, tol=1.5, tp=-4.0)}
# event types whose audible onset is at the anchor (transient). Sweeps/builds are anchored on their peak/end and are not measured by onset.
MEASURE = A.HIT_TYPES | {"pop", "click", "tick", "appear", "disappear", "glitch", "zap", "stamp", "paper-slap", "paper-rip", "tape", "camera-shutter", "type", "count", "dial-tick",
                         "hit", "thud", "error", "blip"}


def probe(path):
    if not shutil.which("ffprobe"):
        return {}
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=index,codec_type,codec_name,start_time,duration,r_frame_rate,avg_frame_rate,sample_rate,channels",
                        "-of", "json", path], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def frac(s):
    try:
        a, b = s.split("/")
        return float(a) / float(b)
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--events")
    ap.add_argument("--fps", type=float)
    ap.add_argument("--profile", default="social", choices=list(PROFILES))
    ap.add_argument("--png")
    ap.add_argument("--json")
    ap.add_argument("--max-bad", type=float, default=0.10, help="allowed share of measured events beyond 1 frame (default 0.10)")
    ap.add_argument("--late-ms", type=float, default=45.0)
    a = ap.parse_args(argv)
    prof = PROFILES[a.profile]
    res = dict(file=a.file, profile=a.profile)
    fails, warns = [], []

    pr = probe(a.file)
    vfps = None
    vstart = astart = vdur = adur = None
    has_audio = True
    if pr.get("streams") is not None and os.path.splitext(a.file)[1].lower() not in (".wav", ".flac", ".mp3", ".ogg"):
        st = pr["streams"]
        vs = [s for s in st if s.get("codec_type") == "video"]
        au = [s for s in st if s.get("codec_type") == "audio"]
        if vs:
            vfps = frac(vs[0].get("avg_frame_rate", "")) or frac(vs[0].get("r_frame_rate", ""))
            vstart = float(vs[0].get("start_time", 0) or 0)
            vdur = float(vs[0].get("duration", 0) or 0)
        if not au:
            has_audio = False
        else:
            astart = float(au[0].get("start_time", 0) or 0)
            adur = float(au[0].get("duration", 0) or 0)
            res["audio_codec"] = au[0].get("codec_name")
    if not has_audio:
        print("FAIL: the file has no audio stream (nothing to check; a mux step was skipped)")
        res["fails"] = ["no audio stream"]
        if a.json:
            json.dump(res, open(a.json, "w"), indent=1)
        return 1
    x = A.read_audio(a.file, A.SR)
    n = len(x)
    dur = n / A.SR
    fps = a.fps or vfps or 30.0
    res.update(duration_s=round(dur, 3), fps=fps)
    if vdur and abs(vdur - dur) > 0.15:
        warns.append(f"audio duration {dur:.2f} s differs from video {vdur:.2f} s by {abs(vdur - dur):.2f} s")
    if vstart is not None and astart is not None:
        off = (astart - vstart) * 1000
        res["av_start_offset_ms"] = round(off, 1)
        if abs(off) > 25:
            warns.append(f"audio stream starts {off:+.0f} ms vs video: every sound will be shifted by that much unless the player honours it")

    # ---- loudness
    mine = A.loudness(x)
    tp = A.true_peak_db(x)
    ff = A.ffmpeg_ebur128(a.file)
    res["loudness"] = dict(lufs=round(mine["lufs"], 2), tp_dbtp=round(tp, 2), lra=round(mine["lra"], 1), momentary_max=round(mine["momentary_max"], 1), ffmpeg=ff)
    if abs(mine["lufs"] - prof["lufs"]) > prof["tol"]:
        warns.append(f"integrated loudness {mine['lufs']:.1f} LUFS is outside {prof['lufs']} +-{prof['tol']} for profile {a.profile}")
    if tp > prof["tp"] + 0.05:
        fails.append(f"true peak {tp:.2f} dBTP exceeds the profile limit {prof['tp']} dBTP")
    if ff.get("tp") is not None and ff["tp"] > prof["tp"] + 0.3:
        fails.append(f"ffmpeg reports peak {ff['tp']:.1f} dBFS above the limit {prof['tp']}")
    # ---- clipping
    clipped = np.abs(x) >= 0.999
    runs = 0
    for c in range(2):
        v = clipped[:, c].astype(np.int8)
        if v.any():
            d = np.diff(np.concatenate([[0], v, [0]]))
            s, e = np.where(d == 1)[0], np.where(d == -1)[0]
            runs += int(np.sum((e - s) >= 3))
    res["clipping"] = dict(samples=int(clipped.sum()), runs_ge3=runs)
    if runs:
        fails.append(f"{runs} runs of >= 3 clipped samples (audible distortion)")
    elif clipped.sum():
        warns.append(f"{int(clipped.sum())} samples at full scale (isolated, probably inaudible; lower the limiter ceiling)")
    # ---- balance
    sh = A.band_shares(x, A.SR)
    res["balance"] = {k: round(100 * v, 1) if k != "centroid_hz" else round(v) for k, v in sh.items()}
    if sh["below400"] < 0.60:
        warns.append(f"thin: {100 * sh['below400']:.0f} % below 400 Hz (reference 65-90 %)")
    if sh["below400"] > 0.94:
        warns.append(f"boomy: {100 * sh['below400']:.0f} % below 400 Hz")
    if sh["sub"] > 0.75:
        warns.append(f"sub-heavy: {100 * sh['sub']:.0f} % below 120 Hz (reference 30-73 %)")
    if sh["above2k"] > 0.09:
        warns.append(f"bright: {100 * sh['above2k']:.1f} % above 2 kHz (reference 2-7 %): the 'cheap beep' direction")
    if sh["above2k"] < 0.012:
        warns.append(f"dull: {100 * sh['above2k']:.1f} % above 2 kHz (reference 2-7 %)")
    # ---- structure
    env = A.envelope(x, A.SR, 20.0)
    ed = 20 * np.log10(np.maximum(env, 1e-9))
    first = np.argmax(ed > -45.0) / A.SR if (ed > -45.0).any() else None
    last = (len(ed) - np.argmax(ed[::-1] > -45.0)) / A.SR if (ed > -45.0).any() else None
    sil = A.silence_ratio(x, A.SR)
    ons = A.onsets(x, A.SR, rise_db=8.0, floor_db=-60.0)
    dens = len(ons) / max(dur, 1e-6)
    mid = (x[:, 0] + x[:, 1]) / 2
    side = (x[:, 0] - x[:, 1]) / 2
    mono_loss = float(10 * np.log10((np.sum(mid ** 2) + 1e-12) / (np.sum(x ** 2) / 2 + 1e-12)))
    lr = float(10 * np.log10((np.sum(x[:, 0] ** 2) + 1e-12) / (np.sum(x[:, 1] ** 2) + 1e-12)))
    res["structure"] = dict(first_sound_s=None if first is None else round(first, 3), last_sound_s=None if last is None else round(last, 3), silence_ratio=round(sil, 3),
                            onset_density_per_s=round(dens, 2), mono_sum_loss_db=round(mono_loss, 2), lr_balance_db=round(lr, 2), side_to_mid_db=round(float(10 * np.log10((np.sum(side ** 2) + 1e-12) / (np.sum(mid ** 2) + 1e-12))), 1))
    if first is None:
        fails.append("the audio is silent")
    elif first > 0.25:
        warns.append(f"first sound at {first:.2f} s: the opening frames are silent (references hit inside the first second, usually at frame 0-10)")
    if last is not None and dur - last > 1.2:
        warns.append(f"{dur - last:.1f} s of silence at the end")
    if mono_loss < -3.0:
        warns.append(f"mono sum loses {-mono_loss:.1f} dB: phase problems (phone speakers are mono)")
    if abs(lr) > 2.5:
        warns.append(f"L/R imbalance {lr:+.1f} dB")
    if dens > 12:
        warns.append(f"busy: {dens:.1f} onsets/s (references 5-10)")

    # ---- alignment
    if a.events:
        evs, video = A.load_events(a.events)
        efps = a.fps or float(video.get("fps") or 0) or fps
        items = []
        for e in evs:
            raw = str(e.get("type", "")).lower()
            typ = "count" if raw in ("count", "count-up", "counter", "dial") else A.event_type(e)
            if typ not in MEASURE:
                continue
            e2 = dict(e); e2["type"] = typ
            t_ev = A.event_anchor_time(e2, efps, lag=0.0)
            if typ in ("type", "count"):                                   # first step only: the rest are dense
                t_ev = A.frame_snap(float(e["t"]), efps)
            items.append((e, typ, t_ev))
        errs = A.align_errors(x, [t for _, _, t in items], A.SR, window=(-0.05, 0.09))
        rows = []
        for (e, typ, t_ev), er in zip(items, errs):
            rows.append(dict(t=round(float(e["t"]), 3), type=typ, label=e.get("label", ""), frame_t=round(t_ev, 4), err_ms=None if er is None else round(er, 1)))
        meas = [r for r in rows if r["err_ms"] is not None]
        tol = 1000.0 / efps
        bad = [r for r in meas if abs(r["err_ms"]) > tol]
        late = [r for r in meas if r["err_ms"] > a.late_ms]
        al = dict(events_total=len(evs), transient_events=len(rows), measured=len(meas), unmeasured=len(rows) - len(meas), frame_ms=round(tol, 1))
        if meas:
            v = np.array([r["err_ms"] for r in meas])
            al.update(median_ms=round(float(np.median(v)), 1), worst_ms=round(float(v[np.argmax(np.abs(v))]), 1), beyond_1_frame=len(bad), beyond_1_frame_share=round(len(bad) / len(meas), 3),
                      later_than_late_ms=len(late), early_count=int(np.sum(v < -tol * 0.5)))
            if len(bad) / len(meas) > a.max_bad:
                fails.append(f"{len(bad)}/{len(meas)} measured events are off by more than 1 frame ({tol:.0f} ms): worst {al['worst_ms']:+.0f} ms. Check mux offset and that sync_cues used the same fps.")
            if late:
                warns.append(f"{len(late)} events land later than +{a.late_ms:.0f} ms (the loose-feeling references were +46..+92 ms; polished ones +7..+19 ms)")
            if al["median_ms"] < -10:
                warns.append(f"median offset {al['median_ms']:+.0f} ms: sound is EARLY on average; check the AAC/mux offset")
        if len(rows) and len(meas) < 0.5 * len(rows):
            warns.append(f"only {len(meas)}/{len(rows)} events could be measured (masked by louder material): verify by ear/at the 5 timestamps; this is not a pass")
        res["alignment"] = al
        res["alignment_rows"] = rows
    res["fails"], res["warnings"] = fails, warns
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1)
    if a.png:
        png(x, a.png, res, evs if a.events else [], efps if a.events else fps)

    L = res["loudness"]
    print(f"{os.path.basename(a.file)}  {dur:.2f} s  profile {a.profile}")
    print(f"  loudness {L['lufs']} LUFS (ffmpeg {ff.get('lufs')})   true peak {L['tp_dbtp']} dBTP (limit {prof['tp']})   LRA {L['lra']}")
    b = res["balance"]
    print(f"  balance  sub {b['sub']} / low {b['low']} / mid {b['mid']} / high {b['high']} / air {b['air']} %   below400 {b['below400']} %  above2k {b['above2k']} %  centroid {b['centroid_hz']} Hz")
    s = res["structure"]
    print(f"  structure first sound {s['first_sound_s']} s, silence {100 * s['silence_ratio']:.0f} %, {s['onset_density_per_s']} onsets/s, mono loss {s['mono_sum_loss_db']} dB")
    if "alignment" in res:
        al = res["alignment"]
        if "median_ms" in al:
            print(f"  alignment {al['measured']}/{al['transient_events']} measured: median {al['median_ms']:+.1f} ms, worst {al['worst_ms']:+.1f} ms, beyond 1 frame (+-{al['frame_ms']} ms): {al['beyond_1_frame']}")
        else:
            print(f"  alignment nothing measurable ({al['transient_events']} transient events)")
    for w in warns:
        print("  WARNING:", w)
    for f in fails:
        print("  FAIL:", f)
    print("RESULT:", "FAIL" if fails else "PASS (numbers only; nobody has listened)")
    return 1 if fails else 0


def png(x, path, res, evs, fps):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy import signal
    m = A.mono(x)
    fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True, gridspec_kw=dict(height_ratios=[1, 2]))
    t = np.arange(len(m)) / A.SR
    ax[0].plot(t[::20], m[::20], lw=0.4)
    f, tt, S = signal.spectrogram(m, A.SR, nperseg=2048, noverlap=1792, window="hann")
    ax[1].pcolormesh(tt, f, 10 * np.log10(S + 1e-12), shading="auto", vmin=-110, vmax=-30, cmap="magma")
    ax[1].set_yscale("symlog", linthresh=500); ax[1].set_ylim(20, 16000)
    for e in evs:
        ty = A.event_type(e)
        ta = A.event_anchor_time(e, fps)
        col = "c" if ty in MEASURE else "lime"
        ax[0].axvline(ta, color=col, lw=0.5, alpha=0.7); ax[1].axvline(ta, color=col, lw=0.5, alpha=0.5)
    ax[0].set_title(f"{os.path.basename(res['file'])}  {res['loudness']['lufs']} LUFS  TP {res['loudness']['tp_dbtp']}  (cyan = transient event, green = sweep/build/other)")
    ax[1].set_xlabel("s"); ax[1].set_ylabel("Hz")
    fig.tight_layout(); fig.savefig(path, dpi=90); plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
