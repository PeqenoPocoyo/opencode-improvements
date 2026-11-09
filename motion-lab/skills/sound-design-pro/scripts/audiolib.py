#!/usr/bin/env python3
"""audiolib.py - shared audio helpers for sound-design-pro (numpy + scipy only; ffmpeg optional).

Everything here is deterministic. Imported by sfxgen, analyze_sfx, sync_cues, qa_audio, musicgen.

  read_audio(path, sr=48000)      -> float32 (n, 2) stereo at sr (WAV via scipy; anything else via ffmpeg)
  write_wav(path, x, sr, bits=16) -> PCM16 (TPDF dither) or float32 WAV
  loudness(x, sr)                 -> dict(lufs, momentary_max, short_term_max, lra)   (ITU BS.1770-4 / EBU R128 gating)
  true_peak_db(x, sr)             -> dBTP via 4x oversampling
  ffmpeg_ebur128(path)            -> dict(lufs, lra, tp) measured by ffmpeg (the reference measurement)
  band_shares(x, sr)              -> dict of energy shares: sub, low, mid, high, air, below400, above2k
  envelope(x, sr, smooth_ms)      -> amplitude envelope (RMS-like) at sample rate
  onsets(x, sr)                   -> list of dict(t, strength) = steepest-rise onset times
  anchor_time(x, sr)              -> time (s) of the max of a 1-3 ms smoothed envelope (what sync aligns to the visual hit)
  limiter(x, sr, ceiling_db)      -> look-ahead peak limiter (offline)
  master(x, sr, lufs, tp)         -> measure -> gain -> limiter loop; returns (y, info)
  frame_snap(t, fps)              -> time of the frame that shows an event at t
"""
import json
import math
import os
import re
import shutil
import subprocess
import tempfile

import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

SR = 48000
EPS = 1e-12


# ----------------------------------------------------------------------------- units
def db(x):
    return 20.0 * np.log10(np.maximum(np.abs(x), EPS))


def undb(d):
    return 10.0 ** (np.asarray(d, dtype=float) / 20.0)


def semis(st):
    return 2.0 ** (np.asarray(st, dtype=float) / 12.0)


def frame_snap(t, fps, mode="round"):
    """Time of the frame that first shows an event registered at t. CONVENTIONS: frame = round(t*fps)."""
    x = t * fps
    f = {"round": math.floor(x + 0.5 + 1e-9), "ceil": math.ceil(x - 1e-9), "floor": math.floor(x + 1e-9)}[mode]
    return f / fps


# ----------------------------------------------------------------------------- io
def _to_stereo(x):
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    elif x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    elif x.shape[1] > 2:
        x = x[:, :2]
    return x


def resample(x, sr_in, sr_out):
    if sr_in == sr_out:
        return x
    g = math.gcd(int(sr_in), int(sr_out))
    return signal.resample_poly(x, int(sr_out) // g, int(sr_in) // g, axis=0).astype(np.float32)


def read_audio(path, sr=SR):
    """Return float32 (n, 2) at `sr`. WAV is read directly; anything else (mp3, ogg, mp4, m4a...) goes through ffmpeg."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".wav":
        try:
            r, d = wavfile.read(path)
            if d.dtype == np.int16:
                d = d.astype(np.float32) / 32768.0
            elif d.dtype == np.int32:
                d = d.astype(np.float32) / 2147483648.0
            elif d.dtype == np.uint8:
                d = (d.astype(np.float32) - 128.0) / 128.0
            else:
                d = d.astype(np.float32)
            return resample(_to_stereo(d), r, sr)
        except Exception:
            pass  # 24-bit etc: fall through to ffmpeg
    if not shutil.which("ffmpeg"):
        raise RuntimeError(f"cannot read {path}: not a plain WAV and ffmpeg is not installed")
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "x.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vn", "-ac", "2", "-ar", str(sr),
                        "-c:a", "pcm_f32le", out], check=True)
        r, d = wavfile.read(out)
    return _to_stereo(d.astype(np.float32))


def write_wav(path, x, sr=SR, bits=16, dither=True, seed=1):
    """bits=16 -> PCM16 with TPDF dither (never wraps: clipped at +-1). bits=32 -> float32 WAV (no clipping)."""
    x = _to_stereo(x) if np.ndim(x) == 1 else np.asarray(x, dtype=np.float32)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if bits == 32:
        wavfile.write(path, sr, x.astype(np.float32))
        return
    y = np.clip(x, -1.0, 1.0).astype(np.float64)
    if dither:
        rng = np.random.default_rng(seed)
        y = y + (rng.random(y.shape) - rng.random(y.shape)) / 32768.0
    wavfile.write(path, sr, np.clip(np.round(y * 32767.0), -32768, 32767).astype(np.int16))


def mono(x):
    x = np.asarray(x, dtype=np.float32)
    return x if x.ndim == 1 else x.mean(axis=1)


# ----------------------------------------------------------------------------- filters (RBJ)
def biquad_coefs(kind, f, q=0.7071, gain_db=0.0, sr=SR):
    f = float(np.clip(f, 10.0, sr * 0.49))
    w0 = 2 * math.pi * f / sr
    cw, sw = math.cos(w0), math.sin(w0)
    al = sw / (2.0 * max(q, 1e-3))
    A = 10 ** (gain_db / 40.0)
    if kind == "lp":
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == "hp":
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == "bp":  # constant 0 dB peak gain
        b = [al, 0, -al]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == "notch":
        b = [1, -2 * cw, 1]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == "peak":
        b = [1 + al * A, -2 * cw, 1 - al * A]; a = [1 + al / A, -2 * cw, 1 - al / A]
    elif kind == "ls":
        s = 2 * math.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * cw + s), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - s)]
        a = [(A + 1) + (A - 1) * cw + s, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - s]
    elif kind == "hs":
        s = 2 * math.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * cw + s), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - s)]
        a = [(A + 1) - (A - 1) * cw + s, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - s]
    else:
        raise ValueError(kind)
    b = np.array(b) / a[0]; a = np.array(a) / a[0]
    return b, a


def biquad(x, kind, f, q=0.7071, gain_db=0.0, sr=SR, order=1):
    b, a = biquad_coefs(kind, f, q, gain_db, sr)
    y = x
    for _ in range(order):
        y = signal.lfilter(b, a, y, axis=0)
    return y


# ----------------------------------------------------------------------------- loudness (BS.1770-4)
def _kweight(x, sr):
    # stage 1: high shelf +3.99 dB @ 1681.97 Hz (Q .7072); stage 2: high-pass 38.14 Hz (Q .5003)
    b1, a1 = biquad_coefs("hs", 1681.974450955533, 0.7071752369554196, 3.999843853973347, sr)
    b2, a2 = biquad_coefs("hp", 38.13547087602444, 0.5003270373238773, 0.0, sr)
    y = signal.lfilter(b1, a1, x, axis=0)
    return signal.lfilter(b2, a2, y, axis=0)


def loudness(x, sr=SR):
    x = _to_stereo(x).astype(np.float64)
    n = x.shape[0]
    blk, step = int(0.4 * sr), int(0.1 * sr)
    if n < blk:
        x = np.pad(x, ((0, blk - n), (0, 0)))
        n = blk
    z = _kweight(x, sr) ** 2
    cs = np.vstack([np.zeros((1, 2)), np.cumsum(z, axis=0)])
    idx = np.arange(0, n - blk + 1, step)
    ms = (cs[idx + blk] - cs[idx]) / blk                      # (blocks, 2)
    pw = ms.sum(axis=1)                                       # channel weights 1.0
    with np.errstate(divide="ignore"):
        lk = -0.691 + 10 * np.log10(np.maximum(pw, 1e-20))
    absg = lk > -70.0
    if not absg.any():
        return dict(lufs=-120.0, momentary_max=-120.0, short_term_max=-120.0, lra=0.0)
    rel = -0.691 + 10 * np.log10(pw[absg].mean()) - 10.0
    g = absg & (lk > rel)
    lufs = -0.691 + 10 * np.log10(pw[g].mean()) if g.any() else -120.0
    # short-term (3 s) max and LRA
    sblk = int(3.0 * sr)
    st = []
    if n >= sblk:
        sidx = np.arange(0, n - sblk + 1, step)
        sms = ((cs[sidx + sblk] - cs[sidx]) / sblk).sum(axis=1)
        st = -0.691 + 10 * np.log10(np.maximum(sms, 1e-20))
    lra = 0.0
    if len(st):
        sa = st[st > -70]
        if len(sa):
            r = -0.691 + 10 * np.log10(np.mean(10 ** ((sa + 0.691) / 10))) - 20.0
            sg = sa[sa > r]
            if len(sg) > 1:
                lra = float(np.percentile(sg, 95) - np.percentile(sg, 10))
    return dict(lufs=float(lufs), momentary_max=float(lk.max()), short_term_max=float(np.max(st)) if len(st) else float(lk.max()),
                lra=lra)


def true_peak_db(x, sr=SR):
    x = _to_stereo(x)
    up = signal.resample_poly(x, 4, 1, axis=0)
    return float(db(np.max(np.abs(up))))


def sample_peak_db(x):
    return float(db(np.max(np.abs(x)))) if np.size(x) else -120.0


def ffmpeg_ebur128(path):
    """Reference measurement by ffmpeg's ebur128 filter on a file (WAV/MP4). Returns {} if ffmpeg is missing."""
    if not shutil.which("ffmpeg"):
        return {}
    r = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    s = r.stderr.split("Summary:")[-1]
    out = {}
    m = re.search(r"I:\s+(-?[\d.]+)\s+LUFS", s)
    if m: out["lufs"] = float(m.group(1))
    m = re.search(r"LRA:\s+(-?[\d.]+)\s+LU", s)
    if m: out["lra"] = float(m.group(1))
    m = re.search(r"Peak:\s+(-?[\d.]+)\s+dBFS", s)
    if m: out["tp"] = float(m.group(1))
    return out


# ----------------------------------------------------------------------------- spectrum
BANDS = dict(sub=(20, 120), low=(120, 400), mid=(400, 2000), high=(2000, 6000), air=(6000, 16000))


def band_shares(x, sr=SR, ignore_silence_db=-70.0):
    """Energy share per band (sums to 1) from a Welch PSD of the mono sum, silent frames excluded."""
    m = mono(x).astype(np.float64)
    if len(m) < 16384:
        m = np.pad(m, (0, 16384 - len(m)))                     # zero padding adds no energy: shares stay valid
    f, p = signal.welch(m, sr, nperseg=8192, noverlap=4096, window="hann")
    tot = sum(p[(f >= lo) & (f < hi)].sum() for lo, hi in BANDS.values()) + EPS
    out = {k: float(p[(f >= lo) & (f < hi)].sum() / tot) for k, (lo, hi) in BANDS.items()}
    out["below400"] = out["sub"] + out["low"]
    out["above2k"] = out["high"] + out["air"]
    cent = float((f[(f >= 20)] * p[(f >= 20)]).sum() / (p[(f >= 20)].sum() + EPS))
    out["centroid_hz"] = cent
    return out


# ----------------------------------------------------------------------------- envelope / onsets / anchor
def envelope(x, sr=SR, smooth_ms=2.0):
    m = mono(x).astype(np.float64)
    n = max(1, int(sr * smooth_ms / 1000.0))
    return np.sqrt(np.maximum(uniform_filter1d(m * m, n, mode="nearest"), 0.0))


def anchor_time(x, sr=SR, smooth_ms=2.0, search_s=None):
    """Time (s) of the maximum of a short (default 2 ms) smoothed envelope. This is the instant a listener
    perceives as 'the hit'; sync aligns it to the frame of the visual event. search_s limits the search window."""
    e = envelope(x, sr, smooth_ms)
    if search_s:
        e = e[: int(search_s * sr)]
    return float(np.argmax(e) / sr)


def sound_anchor(x, sr=SR, kind="transient", smooth_ms=1.5, window_ms=60.0, frac=0.35):
    """Measured anchor of a standalone sound = the instant the listener hears the hit begin (this is what sync aligns to the frame).
      transient: first time the 1.5 ms envelope reaches 35 % of its maximum inside the first `window_ms` after the sound first
                 exceeds 5 % of its global peak. (The max of the envelope is NOT used: in a sub-heavy hit the low body peaks 10-30 ms
                 after the click and would make sync early by that much.)
      peak:      global max of a 2 ms envelope (whoosh)
      end:       last time the envelope is above 35 % of its peak (riser / reverse: they END on the visual event)"""
    if kind == "peak":
        return float(np.argmax(envelope(x, sr, 2.0)) / sr)
    e = envelope(x, sr, smooth_ms)
    pk = e.max() + 1e-12
    if kind == "end":
        idx = np.where(e > 0.35 * pk)[0]
        return float((idx[-1] if len(idx) else len(e) - 1) / sr)
    start = int(np.argmax(e > 0.05 * pk))
    w = int(window_ms * sr / 1000.0)
    seg = e[start:start + w]
    return float((start + int(np.argmax(seg > frac * seg.max()))) / sr)


def onsets(x, sr=SR, hop_ms=1.0, min_gap_ms=30.0, rise_db=8.0, floor_db=-60.0, ref_db=None):
    """Onset = instant of the steepest log-envelope rise (after 1 ms smoothing) whose rise is >= rise_db within 12 ms
    and whose level is above floor_db relative to full scale (or ref_db when given). Returns [{t, strength_db, level_db}]."""
    m = mono(x).astype(np.float64)
    hop = max(1, int(sr * hop_ms / 1000.0))
    e = envelope(m, sr, 1.5)[::hop]
    ed = 20 * np.log10(np.maximum(e, 1e-6))
    k = int(round(12.0 / hop_ms))
    base = np.concatenate([np.full(k, ed[0]), ed[:-k]]) if len(ed) > k else ed
    base = minimum_filter1d(base, 3)
    rise = ed - base
    cand = np.where((rise >= rise_db) & (ed > floor_db))[0]
    res = []
    gap = int(min_gap_ms / hop_ms)
    i = 0
    while i < len(cand):
        j = i
        while j + 1 < len(cand) and cand[j + 1] - cand[j] <= gap:
            j += 1
        seg = np.arange(cand[i], cand[j] + 1)
        # steepest rise inside this cluster: start of the rise = first sample where the envelope exceeded base+3 dB
        grad = np.diff(ed, prepend=ed[0])
        gs = uniform_filter1d(grad, 3)
        s0 = max(0, seg[0] - k)
        win = slice(s0, seg[-1] + 1)
        t_idx = s0 + int(np.argmax(gs[win]))
        res.append(dict(t=t_idx * hop / sr, strength_db=float(rise[seg].max()), level_db=float(ed[seg].max())))
        i = j + 1
    return res


# ----------------------------------------------------------------------------- dynamics
def _ar_follow(g, sr_ctrl, attack, release):
    """One-pole attack/release follower on a control-rate array (python loop; control rate is ~1 kHz so this is cheap)."""
    out = np.empty_like(g)
    ca = math.exp(-1.0 / max(attack * sr_ctrl, 1e-3)); cr = math.exp(-1.0 / max(release * sr_ctrl, 1e-3))
    y = 0.0
    for i, v in enumerate(g):
        c = ca if v > y else cr
        y = c * y + (1 - c) * v
        out[i] = y
    return out


def ar_follow(g, sr_ctrl, attack, release):
    return _ar_follow(np.asarray(g, dtype=np.float64), sr_ctrl, attack, release)


def limiter(x, sr=SR, ceiling_db=-1.0, lookahead_ms=3.0, release_ms=80.0):
    """Offline look-ahead peak limiter. Zero-latency (the gain curve is computed non-causally).
    Peak is guaranteed <= ceiling in the SAMPLE domain; use master() to also bound the true peak."""
    x = np.asarray(x, dtype=np.float64)
    c = 10 ** (ceiling_db / 20.0)
    pk = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    need = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    if need.min() >= 1.0:
        return x.astype(np.float32)
    A = max(1, int(lookahead_ms * sr / 1000.0))
    g1 = minimum_filter1d(need, 2 * A + 1)
    g1 = uniform_filter1d(g1, 2 * A + 1)                       # smooth attack, never above `need`
    # release: reduction decays slowly (recursive max-decay evaluated on a 24-sample grid, then expanded)
    D = 24
    red = 1.0 - g1
    nb = int(math.ceil(len(red) / D))
    padded = np.pad(red, (0, nb * D - len(red)))
    blk = padded.reshape(nb, D).max(axis=1)
    coef = math.exp(-D / (release_ms * sr / 1000.0))
    env = np.empty(nb); y = 0.0
    for i in range(nb):
        y = max(blk[i], y * coef)
        env[i] = y
    red2 = np.repeat(env, D)[: len(red)]
    red2 = maximum_filter1d(red2, 1)                           # keep as is (already >= block max)
    g = np.minimum(g1, 1.0 - red2)
    # hard safety so the sample peak never exceeds the ceiling
    g = np.minimum(g, need)
    y = x * (g[:, None] if x.ndim == 2 else g)
    return y.astype(np.float32)


def master(x, sr=SR, target_lufs=-14.0, tp_limit=-1.0, max_iter=10, tol=0.15, lookahead_ms=3.0, release_ms=80.0):
    """measure -> gain -> limiter loop. Returns (y, info). y has integrated loudness within `tol` of target (when the
    limiter allows) and true peak <= tp_limit (4x oversampled). info lists every iteration."""
    x = _to_stereo(x).astype(np.float64)
    L0 = loudness(x, sr)["lufs"]
    if L0 < -100:
        return x.astype(np.float32), dict(note="silent input", iterations=[], lufs=L0, tp=-120.0)
    gain = target_lufs - L0
    ceiling = tp_limit - 0.3
    best = None
    its = []
    for k in range(max_iter):
        y = limiter(x * undb(gain), sr, ceiling, lookahead_ms, release_ms).astype(np.float64)
        L = loudness(y, sr)["lufs"]
        tp = true_peak_db(y, sr)
        its.append(dict(iter=k, gain_db=round(float(gain), 2), ceiling_db=round(float(ceiling), 2), lufs=round(L, 2), tp=round(tp, 2)))
        ok_tp = tp <= tp_limit + 0.01
        ok_l = abs(L - target_lufs) <= tol
        if ok_tp and (best is None or abs(L - target_lufs) < abs(best[1] - target_lufs)):
            best = (y.copy(), L, tp)
        if ok_tp and ok_l:
            break
        if not ok_tp:
            ceiling -= (tp - tp_limit) + 0.05
        if not ok_l:
            gain += (target_lufs - L) * 0.9
    if best is None:                                            # fall back: force TP
        y = limiter(x * undb(gain), sr, ceiling - 1.0, lookahead_ms, release_ms)
        best = (y.astype(np.float64), loudness(y, sr)["lufs"], true_peak_db(y, sr))
    y, L, tp = best
    return y.astype(np.float32), dict(lufs=round(L, 2), tp=round(tp, 2), target_lufs=target_lufs, tp_limit=tp_limit, iterations=its,
                                      reached_target=abs(L - target_lufs) <= tol)


# ----------------------------------------------------------------------------- event timing rules (shared by sync + qa)
HIT_TYPES = {"impact", "hit-soft", "slam", "boom", "bass-drop", "drop", "stinger", "reveal", "scene-cut", "stamp", "thud"}
BIG_TYPES = {"impact", "slam", "boom", "bass-drop", "drop", "stinger", "reveal"}
END_ANCHORED = {"riser", "reverse"}            # the sound ENDS on the anchor: anchor = t + dur
PEAK_ANCHORED = {"whoosh", "swipe", "whip"}     # t = start of the motion, dur = its length; the sound peaks at PEAK_FRAC of dur
PEAK_FRAC = dict(whoosh=0.45, swipe=0.40, whip=0.82)
DEFAULT_DUR = dict(whoosh=0.6, riser=1.6, reverse=0.9, type=1.2, whip=0.22, swipe=0.25, drone=6.0)
TYPE_ALIASES_AUDIO = {"typing": "type", "keystroke": "type", "sweep": "whoosh", "swoosh": "whoosh", "build": "riser", "build-up": "riser"}


def event_type(ev):
    t = str(ev.get("type", "")).lower().strip()
    return TYPE_ALIASES_AUDIO.get(t, t)


def event_dur(ev):
    return float(ev.get("dur") or DEFAULT_DUR.get(event_type(ev), 0.0))


def event_peak_frac(ev):
    """Where inside [t, t+dur] the whoosh/swipe/whip peaks. Whoosh and swipe are clamped to 0.35-0.60 (peak of an eased move), whip 0.6-0.95."""
    typ = event_type(ev)
    f = float(ev.get("peak", PEAK_FRAC.get(typ, 0.45)))
    if typ == "whip":
        return min(0.95, max(0.6, f))
    return min(0.60, max(0.35, f))


def event_anchor_time(ev, fps, whoosh_peak=None, lag=0.0, snap="round"):
    """Where the perceived 'hit' of an event must land, in seconds: frame-snapped (CONVENTIONS: frame = round(t*fps)) + lag.
    riser/reverse: t + dur (they END on the hit). whoosh/swipe/whip: t + peak_frac * dur. Everything else: t."""
    t = float(ev["t"])
    typ = event_type(ev)
    d = event_dur(ev)
    if typ in END_ANCHORED:
        t = t + d
    elif typ in PEAK_ANCHORED:
        t = t + (event_peak_frac(ev) if whoosh_peak is None else whoosh_peak) * d
    return frame_snap(t, fps, snap) + lag


def load_events(path):
    """events.json from render.mjs ({video:{...}, events:[...]}) or a bare list. Returns (events, video_dict)."""
    d = json.load(open(path))
    if isinstance(d, list):
        return d, {}
    return d.get("events", []), d.get("video", {})


# ----------------------------------------------------------------------------- ducking / activity / silence
def gain_curve(n, sr, regions, attack=0.03, release=0.25, lookahead=None, ctrl=1000):
    """Linear gain curve (n,) from regions [(t0, t1, depth_db), ...]. Overlaps take the deepest. The reduction follows
    attack/release one-pole smoothing; `lookahead` (default = attack, offline so it is free) starts every region earlier so the
    duck is complete when the event begins."""
    la = attack if lookahead is None else lookahead
    m = int(math.ceil(n / sr * ctrl)) + 2
    red = np.zeros(m)
    for t0, t1, d in regions:
        i0 = max(0, int((t0 - la) * ctrl)); i1 = min(m, int(math.ceil(t1 * ctrl)) + 1)
        if i1 > i0:
            red[i0:i1] = np.maximum(red[i0:i1], d)
    red = ar_follow(red, ctrl, attack, release)
    g = 10.0 ** (-red / 20.0)
    return np.interp(np.arange(n) / sr * ctrl, np.arange(m), g)


def voice_regions(voice, sr=SR, thresh_db=-42.0, rel_db=-32.0, hold=0.18, min_len=0.05):
    """Speech-active regions [(t0, t1)] of a voice track: 20 ms RMS above max(thresh_db, peak_env + rel_db), gaps < hold bridged."""
    e = envelope(voice, sr, 20.0)[:: int(sr * 0.005)]                    # 5 ms hop
    ed = 20 * np.log10(np.maximum(e, 1e-7))
    thr = max(thresh_db, float(np.percentile(ed, 98)) + rel_db)
    on = ed > thr
    k = max(1, int(hold / 0.005))
    on = maximum_filter1d(on.astype(np.uint8), k) > 0
    regs, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j + 1 < len(on) and on[j + 1]:
                j += 1
            if (j - i) * 0.005 >= min_len:
                regs.append((i * 0.005, (j + 1) * 0.005 - hold * 0.5))
            i = j + 1
        else:
            i += 1
    return regs


def silence_ratio(x, sr=SR, thresh_db=-50.0, win=0.05):
    """Fraction of 50 ms windows whose RMS is below thresh_db (dBFS). 'Silence' in the references is measured on the final mix."""
    m = mono(x).astype(np.float64)
    w = int(win * sr)
    k = len(m) // w
    if k == 0:
        return 0.0
    r = np.sqrt(np.mean(m[: k * w].reshape(k, w) ** 2, axis=1))
    return float(np.mean(20 * np.log10(np.maximum(r, 1e-9)) < thresh_db))


# ----------------------------------------------------------------------------- alignment measurement (shared by sync_cues + qa_audio)
def align_errors(audio, anchors, sr=SR, window=(-0.05, 0.08), rise_db=7.0, floor_db=-62.0):
    """For each anchor time (s) return the signed offset in ms of the NEAREST audio onset inside `window` (onset - anchor; positive = sound
    late), or None when no onset is found there. Onsets come from onsets(): steepest rise of the 1.5 ms log envelope."""
    ons = onsets(audio, sr, rise_db=rise_db, floor_db=floor_db)
    ts = np.array([o["t"] for o in ons]) if ons else np.array([])
    out = []
    for a in anchors:
        if len(ts) == 0:
            out.append(None); continue
        d = ts - a
        ok = (d >= window[0]) & (d <= window[1])
        if not ok.any():
            out.append(None); continue
        j = np.where(ok)[0][np.argmin(np.abs(d[ok]))]
        out.append(float(d[j] * 1000.0))
    return out


# ----------------------------------------------------------------------------- beat grid detection (for supplied music)
def detect_grid(x, sr=SR, bpm_hint=None, lo=70.0, hi=180.0):
    """Estimate tempo and the time of a beat. Onset curve = summed positive log-envelope rises in 3 bands (<150 Hz, 150-1500, 1.5-8 kHz,
    3 ms smoothing, 1 ms hop) so a kick counts through both its body and its click. Returns dict(bpm, offset_s, confidence, beat_s).
    offset_s = time of the first beat inside [0, beat). confidence = comb score / mean of the curve (> 2.5 = clear grid; < 1.6 = do not trust).
    With bpm_hint the search is limited to +-4 % of it (always pass the producer's BPM if known: tempo guesses can be off by an octave)."""
    m = mono(x).astype(np.float64)
    hop = int(sr * 0.001)
    d = None
    for kind_lo, kind_hi in ((None, 150.0), (150.0, 1500.0), (1500.0, 8000.0)):
        y = m
        if kind_lo:
            y = signal.lfilter(*biquad_coefs("hp", kind_lo, 0.7071, 0.0, sr), y)
        y = signal.lfilter(*biquad_coefs("lp", kind_hi, 0.7071, 0.0, sr), y)
        e = np.sqrt(np.maximum(uniform_filter1d(y * y, int(sr * 0.003)), 0))[::hop]
        le = np.log(e + 1e-4)
        r = np.maximum(np.diff(le, prepend=le[0]), 0.0)
        r = r / (np.percentile(r, 99.5) + 1e-9)
        d = r if d is None else d + np.minimum(r, 1.5)
    d = maximum_filter1d(d, 3)
    fs = 1000.0
    cands = np.arange(lo, hi, 0.25) if not bpm_hint else np.arange(bpm_hint * 0.96, bpm_hint * 1.04, 0.05)
    best = (-1, None, None)
    for bpm in cands:
        per = 60.0 / bpm * fs
        k = int(len(d) / per)
        if k < 4:
            continue
        idx0 = np.arange(k) * per
        for ph in np.arange(0, per, 2.0):
            idx = np.round(idx0 + ph).astype(int)
            idx = idx[idx < len(d)]
            sc = d[idx].mean()
            if sc > best[0]:
                best = (sc, bpm, ph)
    sc, bpm, ph = best
    if bpm is None:
        return dict(bpm=bpm_hint or 0.0, offset_s=0.0, confidence=0.0, beat_s=60.0 / (bpm_hint or 100.0))
    return dict(bpm=float(bpm), offset_s=float(ph / fs), confidence=float(sc / (d.mean() + 1e-12)), beat_s=float(60.0 / bpm))
