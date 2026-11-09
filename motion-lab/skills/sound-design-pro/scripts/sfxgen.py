#!/usr/bin/env python3
"""sfxgen.py - procedural, LAYERED sound-effect designer (numpy + scipy only, deterministic).

Every recipe builds a stack of layers like a sound designer would (sub body + transient click + tonal body +
texture/air + reverb tail), not a single oscillator beep. Output is stereo 48 kHz.

CLI
  python3 sfxgen.py --list
  python3 sfxgen.py --recipe impact --intensity 0.9 --pitch -2 --seed 3 --out impact.wav
  python3 sfxgen.py --recipe whoosh --dur 0.7 --direction lr --brightness 0.6 --out w.wav
  python3 sfxgen.py --recipe chime --key A --scale minor-pentatonic --out c.wav
  python3 sfxgen.py --all outdir/ [--png]         # every recipe at defaults + metadata.json (+ spectrogram sheet)

Python
  from sfxgen import render
  snd = render('impact', intensity=0.9, pitch=-2, seed=3, key='C', scale='minor-pentatonic')
  snd.data        # float32 (n, 2)
  snd.sr          # 48000
  snd.anchor      # seconds into the sound where the perceived hit / target instant is (what sync aligns to a visual event)
  snd.layers      # [(name, start_s, gain_db), ...]  the designed stack, for docs and reports

Common parameters (every recipe accepts all of them; unused ones are ignored)
  intensity 0..1 (level and weight)   pitch semitones   length seconds (tail/body length override)   dur seconds (motion length for
  whoosh/riser/reverse/typing/drone)   brightness 0..1 (0.5 default; moves filter cutoffs x0.5..x2)   seed int   variant int
  key 'C'..'B'   scale name (see SCALES)   direction in|out|lr|rl|up|down   value 0..1 (dial-tick)   degree int (blip)
  room 0..1 (reverb amount multiplier, default 1)   width 0..1 (stereo width of the dry layers)   cps keys/second (typing)
"""
import argparse
import json
import math
import os
import sys
import zlib

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audiolib import SR, biquad_coefs, write_wav, sound_anchor, db, undb, semis  # noqa: E402

TAU = 2 * math.pi

# ----------------------------------------------------------------------------- music theory
KEYS = {"C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4, "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11}
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10], "minor-pentatonic": [0, 3, 5, 7, 10],
    "major-pentatonic": [0, 2, 4, 7, 9], "dorian": [0, 2, 3, 5, 7, 9, 10], "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10], "phrygian": [0, 1, 3, 5, 7, 8, 10], "harmonic-minor": [0, 2, 3, 5, 7, 8, 11],
    "blues": [0, 3, 5, 6, 7, 10], "whole-tone": [0, 2, 4, 6, 8, 10], "chromatic": list(range(12)),
}


def key_pc(key):
    return KEYS.get(str(key).upper().replace("♯", "#").replace("♭", "B"), 0)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def scale_midi(key, scale, degree, octave=4):
    steps = SCALES.get(scale, SCALES["minor-pentatonic"])
    base = 12 * (octave + 1) + key_pc(key)
    return base + steps[degree % len(steps)] + 12 * (degree // len(steps))


def scale_hz(key, scale, degree, octave=4):
    return midi_hz(scale_midi(key, scale, degree, octave))


def chord_semis(scale):
    st = SCALES.get(scale, SCALES["minor-pentatonic"])
    third = 3 if 3 in st else (4 if 4 in st else st[1])
    fifth = 7 if 7 in st else st[min(len(st) - 1, 3)]
    return [0, third, fifth]


def quantize_midi(m, key, scale):
    steps = set(SCALES.get(scale, SCALES["chromatic"]))
    pc = key_pc(key)
    best = min(range(int(m) - 6, int(m) + 7), key=lambda c: (abs(c - m) + (0 if ((c - pc) % 12) in steps else 100)))
    return best


# ----------------------------------------------------------------------------- params
class P:
    defaults = dict(intensity=0.8, pitch=0.0, length=None, dur=None, brightness=0.5, seed=0, variant=0, key="C",
                    scale="minor-pentatonic", direction="in", value=0.5, degree=0, room=1.0, width=1.0, cps=12.0,
                    peak=None, bpm=66.0, count=None, loop=False)

    def __init__(self, name, **kw):
        self.name = name
        for k, v in self.defaults.items():
            setattr(self, k, kw.get(k, v) if kw.get(k, None) is not None else v)
        self.extra = {k: v for k, v in kw.items() if k not in self.defaults}
        self.intensity = float(np.clip(self.intensity, 0.0, 1.0))
        self.brightness = float(np.clip(self.brightness, 0.0, 1.0))
        self.pk = float(2 ** (self.pitch / 12.0))                       # pitch multiplier
        self.kb = float(2 ** ((self.brightness - 0.5) * 2.0))           # brightness multiplier on cutoffs (x0.5..x2)
        self.rng = np.random.default_rng([int(self.seed) & 0xFFFFFFFF, zlib.crc32(name.encode()), 7])

    def sub_rng(self, salt):
        return np.random.default_rng([int(self.seed) & 0xFFFFFFFF, zlib.crc32(self.name.encode()), int(salt) + 11])


# ----------------------------------------------------------------------------- primitives
def nsamp(sec):
    return max(1, int(round(sec * SR)))


def tarr(n):
    return np.arange(n) / SR


def noise(n, rng, color="white"):
    w = rng.standard_normal(n)
    if color == "white":
        return w
    if color == "pink":  # Paul Kellet's economy filter
        b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
        a = np.array([1, -2.494956002, 2.017265875, -0.522189400])
        y = signal.lfilter(b, a, w)
        return y / (np.std(y) + 1e-12)
    if color == "brown":
        y = signal.lfilter([1.0], [1.0, -0.999], w)
        return y / (np.std(y) + 1e-12)
    raise ValueError(color)


def filt(x, kind, f, q=0.7071, gain_db=0.0, order=1):
    b, a = biquad_coefs(kind, f, q, gain_db, SR)
    y = x
    for _ in range(order):
        y = signal.lfilter(b, a, y)
    return y


def sweep(x, kind, f, q=0.9, block=32):
    """Time-varying biquad (RBJ), coefficients updated every `block` samples. f, q: scalar or per-sample arrays."""
    n = len(x)
    f = np.broadcast_to(np.asarray(f, dtype=float), (n,))
    q = np.broadcast_to(np.asarray(q, dtype=float), (n,))
    y = np.empty(n)
    zi = np.zeros(2)
    for s in range(0, n, block):
        e = min(n, s + block)
        c = s + (e - s) // 2
        b, a = biquad_coefs(kind, f[c], q[c], 0.0, SR)
        y[s:e], zi = signal.lfilter(b, a, x[s:e], zi=zi)
    return y


def exp_env(n, tau, attack=0.0008, hold=0.0):
    t = tarr(n)
    e = np.exp(-np.maximum(t - hold, 0.0) / max(tau, 1e-5))
    if attack > 0:
        e = e * np.minimum(1.0, t / attack) ** 1.0
    return e


def fade(x, fin=0.0, fout=0.004):
    x = np.array(x, dtype=float, copy=True)
    n = len(x)
    if fin > 0:
        m = min(n, nsamp(fin)); x[:m] *= np.sin(np.linspace(0, math.pi / 2, m)) ** 2
    if fout > 0:
        m = min(n, nsamp(fout)); x[n - m:] *= np.cos(np.linspace(0, math.pi / 2, m)) ** 2
    return x


def glide(f0, f1, n, tau=None):
    """Exponential glide from f0 to f1 over n samples. tau (s): time constant of the approach (None = geometric)."""
    t = tarr(n)
    if tau is None:
        return f0 * (f1 / f0) ** (t / max(t[-1], 1e-9))
    return f1 + (f0 - f1) * np.exp(-t / tau)


def phase(f):
    return np.cumsum(TAU * np.asarray(f, dtype=float) / SR)


def osc_sin(f, ph0=0.0):
    return np.sin(phase(f) + ph0)


def _blep(ph, dt):
    out = np.zeros_like(ph)
    m = ph < dt
    x = ph[m] / dt[m]; out[m] = x + x - x * x - 1.0
    m = ph > 1 - dt
    x = (ph[m] - 1.0) / dt[m]; out[m] = x * x + x + x + 1.0
    return out


def osc_saw(f, ph0=0.0):
    dt = np.clip(np.asarray(f, dtype=float) / SR, 1e-6, 0.49)
    ph = (np.cumsum(dt) + ph0) % 1.0
    return 2 * ph - 1 - _blep(ph, dt)


def osc_square(f, pw=0.5, ph0=0.0):
    dt = np.clip(np.asarray(f, dtype=float) / SR, 1e-6, 0.49)
    ph = (np.cumsum(dt) + ph0) % 1.0
    y = np.where(ph < pw, 1.0, -1.0)
    y = y + _blep(ph, dt) - _blep((ph - pw) % 1.0, dt)
    return y


def osc_tri(f, ph0=0.0):
    return (2 / math.pi) * np.arcsin(np.sin(phase(f) + ph0))


def sat(x, drive=1.5, kind="tanh"):
    """Saturation, level-compensated so peak ~ input peak. drive 1..8."""
    if drive <= 0:
        return x
    pk = np.max(np.abs(x)) + 1e-12
    if kind == "tanh":
        y = np.tanh(x / pk * drive)
    elif kind == "fold":
        y = np.sin(x / pk * drive * 1.2)
    elif kind == "crush":
        steps = 2 ** max(2, int(8 - drive))
        y = np.round(x / pk * steps) / steps
    else:
        raise ValueError(kind)
    return y / (np.max(np.abs(y)) + 1e-12) * pk


def bitcrush(x, bits=6, hold=1):
    y = np.round(x * (2 ** (bits - 1))) / (2 ** (bits - 1))
    if hold > 1:
        y = np.repeat(y[::hold], hold)[: len(x)]
    return y


def pan2(x, p=0.0):
    """Mono -> stereo, constant power. p in -1..1."""
    a = (p + 1) * math.pi / 4
    return np.stack([x * math.cos(a), x * math.sin(a)], axis=1)


def widen(x, amount, rng, ms=11.0):
    """Mono -> stereo width. Content under 150 Hz stays centred (bass mono rule). amount 0..1."""
    if amount <= 0:
        return pan2(x, 0.0)
    low = filt(x, "lp", 150.0, 0.7071)
    hi = x - low
    d = nsamp(ms / 1000.0)
    hd = np.concatenate([np.zeros(d), hi])[: len(hi)]
    side = (hd - hi) * 0.5 * amount
    return np.stack([low + hi + side, low + hi - side], axis=1) * 0.85


_IR = {}


def make_ir(rt60, damping=0.5, predelay=0.0, seed=1, early=True):
    key = (round(rt60, 3), round(damping, 2), round(predelay, 4), seed, early)
    if key in _IR:
        return _IR[key]
    n = nsamp(rt60 * 1.1 + predelay)
    t = tarr(n) - predelay
    rng = np.random.default_rng([seed, 4242])
    chans = []
    for ch in range(2):
        nz = rng.standard_normal(n)
        lo = filt(nz, "lp", 3000.0 * (1 - 0.75 * damping) + 400.0, 0.7071)
        hi = nz - lo
        el = np.exp(-6.908 * np.maximum(t, 0) / rt60)
        eh = np.exp(-6.908 * np.maximum(t, 0) / max(rt60 * (1 - 0.8 * damping), 0.05))
        ir = (lo * el + 0.7 * hi * eh) * (t >= 0)
        ir *= np.minimum(1.0, np.maximum(t, 0) / 0.003)
        if early:
            for _ in range(7):
                d = nsamp(predelay + rng.uniform(0.004, 0.05))
                if d < n:
                    ir[d] += rng.uniform(-1, 1) * 0.9 * (1 - d / SR / 0.06)
        ir = signal.lfilter(*biquad_coefs("hp", 90.0, 0.7071, 0.0, SR), ir)
        chans.append(ir)
    ir = np.stack(chans, axis=1)
    ir /= math.sqrt(np.sum(ir ** 2) / 2) + 1e-12
    _IR[key] = ir
    return ir


def reverb(x, rt60=0.8, wet_db=-10.0, damping=0.5, predelay=0.0, seed=1, tail_only=False):
    """Convolution reverb from a generated IR. Returns the WET signal only, stereo, level `wet_db` relative to the input's energy.
    x: mono (n,) or stereo (n,2)."""
    ir = make_ir(rt60, damping, predelay, seed)
    if x.ndim == 1:
        wl = signal.fftconvolve(x, ir[:, 0]); wr = signal.fftconvolve(x, ir[:, 1])
    else:
        wl = signal.fftconvolve(x[:, 0], ir[:, 0]); wr = signal.fftconvolve(x[:, 1], ir[:, 1])
    return np.stack([wl, wr], axis=1) * undb(wet_db)


def smooth_noise(n, rng, cutoff):
    """Low-passed white noise normalised to std 1 (for irregular modulation)."""
    return _norm(filt(noise(n, rng), "lp", cutoff, 0.7071, order=2))


def _norm(x):
    return x / (np.std(x) + 1e-12)


def sub_thump(n, f0, f1, tau_f, tau_a, drive=1.5, attack=0.0015):
    """Pitch-dropping sine (kick/sub body) with a gentle saturation so it translates on small speakers."""
    f = f1 + (f0 - f1) * np.exp(-tarr(n) / tau_f)
    y = np.sin(phase(f)) * exp_env(n, tau_a, attack)
    return sat(y, drive) if drive > 0 else y


def noise_burst(n, rng, tau, lo=None, hi=None, color="white", attack=0.0003, order=1):
    y = noise(n, rng, color)
    if lo:
        y = filt(y, "hp", lo, 0.7071, order=order)
    if hi:
        y = filt(y, "lp", hi, 0.7071, order=order)
    return y * exp_env(n, tau, attack)


def bell(n, f, ratio=3.5, index=2.0, tau_a=0.5, tau_i=0.12, attack=0.001):
    """2-operator FM bell: carrier f, modulator f*ratio, modulation index decays faster than the amplitude."""
    t = tarr(n)
    idx = index * np.exp(-t / tau_i)
    return np.sin(TAU * f * t + idx * np.sin(TAU * f * ratio * t)) * exp_env(n, tau_a, attack)


def modal(n, f0, ratios, amps, taus, attack=0.0006):
    t = tarr(n)
    y = np.zeros(n)
    for r, a, tau in zip(ratios, amps, taus):
        if f0 * r < SR * 0.45:
            y += a * np.sin(TAU * f0 * r * t) * np.exp(-t / tau)
    return y * np.minimum(1.0, t / attack)


# ----------------------------------------------------------------------------- stack / sound
class Sound:
    def __init__(self, data, sr, anchor, recipe, params, layers, notes=""):
        self.data = data.astype(np.float32); self.sr = sr; self.anchor = float(anchor)
        self.recipe = recipe; self.params = params; self.layers = layers; self.notes = notes

    @property
    def duration(self):
        return len(self.data) / self.sr

    def meta(self):
        return dict(recipe=self.recipe, params=self.params, anchor_s=round(self.anchor, 5), duration_s=round(self.duration, 4),
                    layers=[dict(name=n, start_s=round(s, 4), gain_db=round(g, 1)) for n, s, g in self.layers], notes=self.notes)


class Stack:
    """Layer container. add() places a mono or stereo layer at `at` seconds with gain/pan/width; mix() sums, normalises, trims."""

    def __init__(self, p, level_db=-3.0, range_db=14.0):
        self.p = p; self.items = []; self.level = level_db; self.range = range_db
        self.anchor = None; self.anchor_search = 0.06; self.master_sat = 0.0; self.min_len = 0.0

    def add(self, x, at=0.0, gain_db=0.0, pan=0.0, width=None, name="layer", fade_out=0.012):
        """fade_out: seconds of cosine fade at the layer's end (prevents clicks when a decay is cut). 0 = keep the end abrupt."""
        x = np.asarray(x, dtype=float)
        if x.ndim == 1:
            w = self.p.width if width is None else width
            st = widen(x, w, self.p.sub_rng(len(self.items) + 100)) if (w and abs(pan) < 1e-6) else pan2(x, pan)
        else:
            st = x
        if fade_out > 0:
            m = min(len(st), nsamp(fade_out), max(1, len(st) // 3))
            st = st.copy(); st[len(st) - m:] *= (np.cos(np.linspace(0, math.pi / 2, m)) ** 2)[:, None]
        self.items.append((st * undb(gain_db), at, gain_db, name))
        return self

    def mix(self, peak_db=None, tail_trim_db=-68.0):
        p = self.p
        t0 = min(a for _, a, _, _ in self.items)
        total = max(int(round((a - t0) * SR)) + len(s) for s, a, _, _ in self.items)
        out = np.zeros((total, 2))
        for s, a, _, _ in self.items:
            i = int(round((a - t0) * SR))
            out[i:i + len(s)] += s
        out = out - out.mean(axis=0, keepdims=True) * 0.0
        out = signal.lfilter(*biquad_coefs("hp", 22.0, 0.7071, 0.0, SR), out, axis=0)  # DC / infrasonic cleanup
        if self.master_sat > 0:
            out = np.stack([sat(out[:, c], self.master_sat) for c in range(2)], axis=1)
        pk = np.max(np.abs(out)) + 1e-12
        target = peak_db if peak_db is not None else (self.level - (1 - p.intensity) * self.range)
        out = out / pk * undb(target)
        # trim silent tail
        e = np.max(np.abs(out), axis=1)
        idx = np.where(e > undb(tail_trim_db))[0]
        end = min(total, (idx[-1] + 1 if len(idx) else total) + nsamp(0.004))
        end = max(end, int(self.min_len * SR))
        out = out[:end]
        out[-nsamp(0.004):] *= np.linspace(1, 0, min(len(out), nsamp(0.004)))[:, None]
        if self.anchor is None:                                         # measured: the instant the hit starts to be heard (see audiolib.sound_anchor)
            anchor = sound_anchor(out, SR, "transient", window_ms=self.anchor_search * 1000)
        else:
            anchor = self.anchor - t0
        layers = [(n, a - t0, g) for _, a, g, n in self.items]
        return out, anchor, layers


# ----------------------------------------------------------------------------- registry
RECIPES = {}


def recipe(name, cat, desc, level=-3.0, rng_db=14.0, params="", aliases=()):
    def deco(fn):
        RECIPES[name] = dict(fn=fn, cat=cat, desc=desc, level=level, range=rng_db, params=params)
        for a in aliases:
            RECIPES[a] = RECIPES[name]
        return fn
    return deco


def render(recipe_name, **kw):
    """Render a recipe to a Sound. Unknown recipe -> KeyError listing valid names."""
    if recipe_name not in RECIPES:
        raise KeyError(f"unknown recipe '{recipe_name}'. Valid: {', '.join(sorted(RECIPES))}")
    info = RECIPES[recipe_name]
    p = P(recipe_name, **kw)
    stk = Stack(p, info["level"], info["range"])
    ret = info["fn"](p, stk)
    if isinstance(ret, Sound):
        return ret
    data, anchor, layers = stk.mix()
    params = {k: getattr(p, k) for k in P.defaults if k not in ("loop",)}
    params.update(p.extra)
    return Sound(data, SR, anchor, recipe_name, params, layers)


# ============================================================================= HITS
def _click_layer(p, rng, bright=1.0, n_ms=6.0, lo=1800.0):
    n = nsamp(n_ms / 1000)
    c = noise_burst(n, rng, tau=0.0013 + 0.0006 * p.brightness, lo=lo * p.kb * bright, order=2, attack=0.00005)
    return c / (np.max(np.abs(c)) + 1e-9)


@recipe("impact", "hit", "Hero impact: sub drop + thud body + noise body + broadband crack + reverb tail. Weight scales with intensity.", level=-3, params="intensity pitch brightness length")
def r_impact(p, s):
    i, pk, R = p.intensity, p.pk, p.rng
    L = p.length or (0.5 + 0.9 * i)
    n = nsamp(L)
    s.add(sub_thump(n, (92 + 40 * i) * pk, 43 * pk, 0.045, 0.12 + 0.24 * i, 1.4 + 1.2 * i), 0, 0, name="sub", fade_out=min(0.5, L * 0.5))
    s.add(sub_thump(nsamp(0.32), 220 * pk, 84 * pk, 0.028, 0.06 + 0.05 * i, 2.4), 0, -4.5, name="thud-body")
    nb = nsamp(0.26)
    nz = noise(nb, R, "pink")
    nz = sweep(nz, "lp", 260 + (1800 * p.kb + 1600 * i) * np.exp(-tarr(nb) / 0.05), 0.8) * exp_env(nb, 0.085, 0.0008)
    s.add(nz, 0, -9.0, name="noise-body")
    s.add(_click_layer(p, R, 1.0, 7), 0, -3.0 + 5 * (p.brightness - 0.5), name="crack")
    mid = noise_burst(nsamp(0.03), p.sub_rng(2), 0.007, lo=700 * p.kb, hi=5200 * p.kb, order=2)
    s.add(mid / (np.max(np.abs(mid)) + 1e-9), 0.0004, -6.0, name="mid-snap")
    d = sub_thump(nsamp(0.4), 160 * pk, 70 * pk, 0.03, 0.1, 1.5)
    s.add(reverb(d, 0.45 + 1.0 * i * p.room, -11 + 4 * i, 0.55, 0.008, seed=11 + p.variant) * p.room, 0.0, 0, name="tail-reverb")
    s.master_sat = 1.3


@recipe("hit-soft", "hit", "Soft thud for small objects landing: low sine + short lp noise thump, tiny room. No crack.", level=-8, params="intensity pitch brightness")
def r_hit_soft(p, s):
    pk, R, i = p.pk, p.rng, p.intensity
    s.add(sub_thump(nsamp(0.3), (105 + 25 * i) * pk, 52 * pk, 0.035, 0.07 + 0.05 * i, 1.4, attack=0.002), 0, 0, name="sub-thud")
    nb = nsamp(0.09)
    nz = filt(noise(nb, R, "pink"), "lp", 520 * p.kb * (1 + i), 0.9, order=2) * exp_env(nb, 0.025, 0.0015)
    s.add(nz, 0, -6.0, name="soft-body")
    s.add(_click_layer(p, R, 0.55, 3, lo=1200) * (0.4 + 0.4 * p.brightness), 0.0005, -12.0, name="felt-tick")
    s.add(reverb(sub_thump(nsamp(0.15), 130 * pk, 70 * pk, 0.03, 0.05, 1.2), 0.35 * p.room + 0.05, -13, 0.7, 0.004, 21), 0, 0, name="room")


@recipe("slam", "hit", "Heavy slam / door-hit: impact + gated crash noise + flam double-hit + long sub + big room. Use once per video.", level=-2, params="intensity pitch")
def r_slam(p, s):
    pk, R, i = p.pk, p.rng, max(p.intensity, 0.5)
    n = nsamp(p.length or 1.5)
    s.add(sub_thump(n, 120 * pk, 38 * pk, 0.06, 0.34 + 0.2 * i, 2.2), 0, 0, name="sub-long", fade_out=0.6)
    s.add(sub_thump(nsamp(0.4), 250 * pk, 80 * pk, 0.03, 0.09, 3.0), 0, -3.0, name="thud-body")
    cr = nsamp(0.2)
    crash = filt(noise(cr, R), "hp", 450 * p.kb, 0.7071, order=2) * exp_env(cr, 0.05, 0.0004)
    crash = sweep(crash, "lp", 9000 * p.kb * np.exp(-tarr(cr) / 0.08) + 1500, 0.8)
    s.add(crash / (np.max(np.abs(crash)) + 1e-9), 0, -2.5, name="crash-noise")
    s.add(_click_layer(p, R, 1.2, 8, lo=1500), 0, -1.0, name="crack")
    s.add(sub_thump(nsamp(0.25), 200 * pk, 70 * pk, 0.03, 0.06, 2.0), 0.024, -9.0, name="flam-second-hit")
    for k in range(5):                                                  # debris ticks after the slam
        r = p.sub_rng(30 + k)
        s.add(_click_layer(p, r, 0.7, 3, lo=2500) * r.uniform(0.15, 0.4), 0.06 + r.uniform(0, 0.28), -10, name="debris")
    src = sub_thump(nsamp(0.4), 160 * pk, 60 * pk, 0.03, 0.12, 1.5)
    s.add(reverb(src + 0.5 * crash[: len(src)] if len(crash) >= len(src) else src, 1.5 * p.room + 0.1, -7, 0.5, 0.012, 31 + p.variant), 0, 0, name="big-room")
    s.master_sat = 2.2


@recipe("boom", "hit", "Cinematic boom: 40 Hz sub with long decay, falling rumble noise, huge dark reverb. 2.5 s.", level=-3, params="intensity pitch length")
def r_boom(p, s):
    pk, R, i = p.pk, p.rng, p.intensity
    L = p.length or 2.6
    n = nsamp(L)
    s.add(sub_thump(n, 70 * pk, 36 * pk, 0.18, 0.7 + 0.5 * i, 1.8, attack=0.004), 0, 0, name="sub", fade_out=1.0)
    rumble = sweep(noise(n, R, "brown"), "lp", 700 * np.exp(-tarr(n) / 0.35) * p.kb + 60, 0.9) * exp_env(n, 0.5, 0.006)
    s.add(rumble / (np.max(np.abs(rumble)) + 1e-9), 0, -4, name="rumble", fade_out=0.8)
    s.add(_click_layer(p, R, 0.5, 5, lo=900) * 0.8, 0.0, -9, name="soft-click")
    src = sub_thump(nsamp(0.5), 90 * pk, 46 * pk, 0.05, 0.2, 1.5)
    s.add(reverb(src, 2.4 * p.room + 0.2, -6, 0.75, 0.02, 41), 0, 0, name="huge-room")
    s.master_sat = 1.5


@recipe("bass-drop", "hit", "Bass drop: sine falling 120 -> 34 Hz over 0.7 s with harmonics (saturated), sustained sub, pre-click.", level=-3, params="intensity pitch length")
def r_bass_drop(p, s):
    pk, R, i = p.pk, p.rng, p.intensity
    L = p.length or (1.2 + 0.6 * i)
    n = nsamp(L)
    f = glide(130 * pk, 33 * pk, n, tau=0.22)
    body = np.sin(phase(f)) * exp_env(n, 0.55 + 0.4 * i, 0.002)
    s.add(sat(body, 3.5), 0, 0, name="drop-sine-sat", fade_out=0.5)
    s.add(np.sin(phase(np.full(n, 36 * pk))) * exp_env(n, 0.9, 0.05) * 0.8, 0.0, -3, name="sub-sustain", fade_out=0.5)
    s.add(sub_thump(nsamp(0.25), 210 * pk, 80 * pk, 0.03, 0.07, 2.4), 0, -5, name="punch")
    s.add(_click_layer(p, R, 1.0, 6), 0, -4, name="click")
    s.add(reverb(sub_thump(nsamp(0.3), 140 * pk, 60 * pk, 0.04, 0.1, 1.5), 0.9 * p.room, -12, 0.6, 0.01, 51), 0, 0, name="tail")
    s.master_sat = 1.6


@recipe("stamp", "hit", "Ink stamp / thunk: dull wooden knock + short noise 'ka' + low thud. For labels, badges, tags landing.", level=-6, params="intensity pitch variant")
def r_stamp(p, s):
    pk, R, i = p.pk, p.rng, p.intensity
    s.add(sub_thump(nsamp(0.25), (130 + 20 * i) * pk, 68 * pk, 0.025, 0.07 + 0.04 * i, 1.8), 0, 0, name="thud")
    wood = bell(nsamp(0.12), 380 * pk, 2.76, 0.6, 0.03, 0.01)
    s.add(wood, 0, -6, name="wood-knock")
    nb = nsamp(0.05)
    s.add(filt(noise(nb, R), "bp", 1600 * p.kb, 1.2, order=2) * exp_env(nb, 0.01, 0.0004), 0, -4, name="ka-noise")
    s.add(_click_layer(p, R, 0.8, 4, lo=2200), 0, -5, name="click")
    s.add(reverb(sub_thump(nsamp(0.1), 140 * pk, 80 * pk, 0.02, 0.04, 1.2), 0.3 * p.room + 0.05, -11, 0.8, 0.003, 61), 0, 0, name="paper-room")


# ============================================================================= MOTION (noise sweeps)
def _bell_env(x, pk):
    return np.where(x < pk, np.sin(np.clip(x / max(pk, 1e-6), 0, 1) * math.pi / 2) ** 1.8,
                    np.cos(np.clip((x - pk) / max(1 - pk, 1e-6), 0, 1) * math.pi / 2) ** 1.5)


def _whoosh_core(p, dur, peak, lo, hi, direction, q=1.0):
    n = nsamp(dur)
    x = np.linspace(0, 1, n)
    env = _bell_env(x, peak)
    # center frequency path
    if direction in ("lr", "rl", "in", "out"):
        path = env ** 0.9 if direction in ("lr", "rl") else (0.3 + 0.7 * x if direction == "in" else 1.0 - 0.7 * x)
    elif direction == "up":
        path = x
    else:
        path = 1 - x
    fc = lo * (hi / lo) ** path
    Rl, Rr = p.sub_rng(1), p.sub_rng(2)
    chans = []
    for R in (Rl, Rr):
        w = noise(n, R, "pink")
        y = sweep(w, "bp", fc, q * (0.8 + 0.6 * env), block=24)
        y = sweep(y, "bp", fc * 1.15, q * 0.7, block=24)
        chans.append(y)
    y = np.stack(chans, axis=1)
    y = y / (np.max(np.abs(y)) + 1e-9) * env[:, None]
    return y, env, x


@recipe("whoosh", "motion", "Layered whoosh: band-passed pink noise sweeping through the motion (peak at 35-60 % of dur) + low rumble + air layer + pan sweep. anchor = peak.", level=-8, rng_db=12, params="dur direction(in|out|lr|rl|up|down) brightness peak")
def r_whoosh(p, s):
    dur = p.dur or p.length or 0.6
    d = p.direction
    peak = p.peak if p.peak is not None else {"in": 0.6, "out": 0.35}.get(d, 0.45)
    lo, hi = 170 * p.pk, 2300 * p.pk * p.kb
    y, env, x = _whoosh_core(p, dur, peak, lo, hi, d, 1.6)
    n = len(env)
    if d in ("lr", "rl"):
        pn = (x * x * (3 - 2 * x)) * 1.6 - 0.8
        pn = pn if d == "lr" else -pn
        a = (pn + 1) * math.pi / 4
        y = np.stack([y.mean(axis=1) * np.cos(a), y.mean(axis=1) * np.sin(a)], axis=1) * 1.2
    s.add(y, 0, 0, name="body-noise-sweep")
    R = p.sub_rng(3)
    air = filt(noise(n, R), "hp", 4200 * p.kb, 0.7071, order=2) * env ** 2.2
    s.add(air, 0, -18.0 + 8 * (p.brightness - 0.5), name="air")
    rum = filt(noise(n, p.sub_rng(4), "brown"), "lp", 240, 0.7, order=2) * env ** 1.3
    s.add(rum / (np.max(np.abs(rum)) + 1e-9), 0, -3, width=0, name="low-rumble")
    s.add(reverb(y[:, 0] if y.ndim == 2 else y, 0.4 * p.room + 0.05, -17, 0.7, 0.0, 71), 0, 0, name="tail")
    s.anchor = peak * dur
    s.min_len = dur


@recipe("whip", "motion", "Whip / fast pan: 0.2 s rising noise burst that stops abruptly with a crack at its peak (anchor). Scene-cut pre-sound.", level=-6, rng_db=12, params="dur direction")
def r_whip(p, s):
    dur = p.dur or p.length or 0.2
    peak = float(p.peak) if p.peak is not None else 0.82
    n = nsamp(dur)
    x = np.linspace(0, 1, n)
    env = np.where(x < peak, (x / peak) ** 2.6, np.exp(-(x - peak) / 0.05))
    fc = 500 * p.pk * (5000 * p.kb / 500) ** (x ** 0.8)
    chans = [sweep(noise(n, p.sub_rng(k), "pink"), "bp", fc, 1.0, 16) for k in (1, 2)]
    y = np.stack(chans, axis=1) * env[:, None]
    y /= np.max(np.abs(y)) + 1e-9
    if p.direction in ("lr", "rl"):
        g = x if p.direction == "lr" else 1 - x
        y = np.stack([y[:, 0] * np.cos(g * math.pi / 2), y[:, 1] * np.sin(g * math.pi / 2)], axis=1) * 1.3
    s.add(y, 0, 0, name="rising-noise", fade_out=0.02)
    pa = int(peak * n)
    s.add(_click_layer(p, p.rng, 0.9, 5, lo=2000), peak * dur, -5, name="end-crack")
    s.add(sub_thump(nsamp(0.1), 140 * p.pk, 60 * p.pk, 0.02, 0.04, 1.2), peak * dur, -11, name="end-thump")
    s.add(reverb(y[:, 0], 0.25 * p.room + 0.05, -16, 0.8, 0.0, 72), 0, 0, name="tail")
    s.anchor = peak * dur
    s.min_len = dur


@recipe("swipe", "motion", "UI swipe: short soft band-passed noise (0.18-0.3 s) rising or falling, very light. For cards/lists sliding.", level=-14, rng_db=10, params="dur direction(up|down|lr|rl)")
def r_swipe(p, s):
    dur = p.dur or p.length or 0.22
    d = p.direction if p.direction in ("up", "down", "lr", "rl") else "up"
    pkf = float(p.peak) if p.peak is not None else 0.4
    y, env, x = _whoosh_core(p, dur, pkf, 500 * p.pk, 3200 * p.pk * p.kb, "up" if d in ("up", "lr") else "down", 1.4)
    if d in ("lr", "rl"):
        pn = (x * 1.2 - 0.6) * (1 if d == "lr" else -1)
        a = (pn + 1) * math.pi / 4
        m = y.mean(axis=1)
        y = np.stack([m * np.cos(a), m * np.sin(a)], axis=1) * 1.3
    s.add(y, 0, 0, name="soft-noise")
    s.add(_click_layer(p, p.rng, 0.4, 3, lo=3500) * 0.25, 0.0, -14, name="start-tick")
    s.anchor = pkf * dur
    s.min_len = dur


@recipe("riser", "build", "Riser that ENDS exactly on its anchor (= dur): rising band noise + detuned saw glide + accelerating pulse. variant 0 mix, 1 pulse, 2 siren/tonal, 3 snare-roll.", level=-6, rng_db=10, params="dur variant key scale brightness")
def r_riser(p, s):
    dur = p.dur or p.length or 1.6
    n = nsamp(dur)
    x = np.linspace(0, 1, n)
    R = p.rng
    v = p.variant % 4
    root = scale_hz(p.key, p.scale, 0, 3) * p.pk
    pulse_rate = 3 + 20 * x ** 1.5
    pulse = 0.5 + 0.5 * np.sin(np.cumsum(TAU * pulse_rate / SR) - math.pi / 2)
    if v in (0, 1, 2):
        nz = noise(n, R, "pink")
        fc = 250 * (6000 * p.kb / 250) ** x
        y = sweep(nz, "bp", fc, 1.2 + 1.0 * x, 32)
        y = y / (np.max(np.abs(y)) + 1e-9)
        amp = x ** 2.2
        if v == 1:
            y *= (1 - 0.8 * (1 - pulse)) ; amp = x ** 1.6
        s.add(y * amp, 0, 0 if v != 2 else -8, name="noise-sweep", fade_out=0.003)
        hi = filt(noise(n, p.sub_rng(5)), "hp", 2500 + 4000 * p.kb, 0.7071, order=2) * x ** 3.2
        s.add(hi, 0, -15, name="air-build", fade_out=0.003)
        s.add(np.sin(phase(root * 0.5 * 2 ** (12 * x ** 1.3 / 12))) * x ** 2.0, 0, -7, width=0, name="low-swell", fade_out=0.003)
    if v in (0, 2):
        f = root * 2 ** ((24 if v == 2 else 18) * x ** 1.4 / 12)
        saw = sum(osc_saw(f * 2 ** (c / 1200)) for c in (-11, 0, 11)) / 3
        saw = sweep(saw, "lp", 300 + 5500 * p.kb * x ** 1.5, 1.4, 32)
        s.add(saw * x ** (2.0 if v == 0 else 1.2), 0, -7 if v == 0 else -2, name="saw-glide", fade_out=0.003)
    if v == 3:
        t, k, ts = 0.0, 0, []
        while t < dur:
            ts.append(t)
            t += 0.12 * (1 - 0.88 * (t / dur)) ** 1.4 + 0.012
            k += 1
        for k, tt in enumerate(ts):
            u = tt / dur
            r2 = p.sub_rng(200 + k)
            nb = nsamp(0.05)
            hit = filt(noise(nb, r2), "bp", (1800 + 3200 * u) * p.kb, 0.9, order=2) * exp_env(nb, 0.014 + 0.01 * (1 - u), 0.0003)
            s.add(hit / (np.max(np.abs(hit)) + 1e-9) * (0.25 + 0.75 * u ** 1.3), tt, 0, name="roll-hit", fade_out=0.004)
        s.add(np.sin(phase(root * 2 ** (12 * x / 12))) * x ** 2 * 0.5, 0, -10, name="tonal-bed", fade_out=0.003)
    s.anchor = dur
    s.master_sat = 0.0
    # tail: very short, so the hit that follows is not smothered
    s.min_len = dur


@recipe("reverse", "build", "Reverse swell that ENDS on the anchor (= dur): reversed bright crash/reverb (variant 0), reversed sub hit (1), reversed bell (2).", level=-8, rng_db=10, params="dur variant key")
def r_reverse(p, s):
    dur = p.dur or p.length or 0.9
    n = nsamp(dur)
    R = p.rng
    v = p.variant % 3
    t = tarr(n)
    if v == 0:
        nz = filt(noise(n, R), "hp", 900 * p.kb, 0.7071, order=2)
        nz = sweep(nz, "lp", 1200 + 5000 * p.kb * np.exp(-t / (dur * 0.35)), 0.9, 48)
        src = nz * np.exp(-t / (dur * 0.30))
        low = filt(noise(n, p.sub_rng(2), "pink"), "bp", 380, 0.7, order=1) * np.exp(-t / (dur * 0.3)) * 1.2 + sub_thump(n, 90 * p.pk, 50 * p.pk, 0.06, dur * 0.3, 1.4) * 0.8
        y = src + low
        wet = reverb(y, dur * 0.8, -4, 0.35, 0.0, 81)[:n]
        mono_ = (y[:, None] * 0.5 + wet)
    elif v == 1:
        sub = sub_thump(n, 100 * p.pk, 48 * p.pk, 0.05, dur * 0.3, 1.5)
        mono_ = reverb(sub + 0.3 * filt(noise(n, R), "lp", 900) * np.exp(-t / 0.05), dur * 0.8, -3, 0.7, 0, 82)[:n] + sub[:, None] * 0.7
    else:
        f = scale_hz(p.key, p.scale, 0, 5) * p.pk
        b = bell(n, f, 3.5, 1.5, dur * 0.4, 0.2) + 0.6 * bell(n, f * 1.5, 3.5, 1.0, dur * 0.3, 0.15)
        mono_ = reverb(b, dur * 0.8, -2, 0.4, 0, 83)[:n] + b[:, None] * 0.6
    rev = mono_[::-1]
    rev = rev / (np.max(np.abs(rev)) + 1e-9)
    s.add(rev, 0, 0, name="reversed-source", fade_out=0.003)
    s.anchor = dur
    s.min_len = dur


# ============================================================================= UI
@recipe("pop", "ui", "Pop: fast pitch-rising sine blip + noise click + low thock + tiny room. For elements popping in.", level=-10, rng_db=12, params="pitch intensity brightness variant")
def r_pop(p, s):
    pk, R, i = p.pk, p.rng, p.intensity
    f0 = (250 + 110 * R.random()) * pk
    n = nsamp(0.16)
    f = f0 * (1 + 1.1 * (1 - np.exp(-tarr(n) / 0.014)))
    body = np.sin(phase(f)) * exp_env(n, 0.032 + 0.02 * i, 0.001)
    s.add(sat(body, 1.3), 0, 0, name="blip-body")
    s.add(_click_layer(p, R, 0.9, 3, lo=2200), 0, -7 + 4 * (p.brightness - 0.5), name="click")
    s.add(sub_thump(nsamp(0.12), 150 * pk, 90 * pk, 0.02, 0.045, 1.4, 0.001), 0, -3, name="thock")
    s.add(sub_thump(nsamp(0.2), 80 * pk, 58 * pk, 0.04, 0.07, 1.2, 0.002), 0, -6, name="sub-bloom")
    s.add(reverb(body[: nsamp(0.06)], 0.28 * p.room + 0.05, -14, 0.7, 0.0, 91), 0, 0, name="room")


@recipe("appear", "ui", "Appear: upward chirp + airy sparkle + soft pop; element materialising. Opposite of disappear.", level=-10, rng_db=12, params="pitch intensity brightness")
def r_appear(p, s):
    pk, R = p.pk, p.rng
    n = nsamp(0.28)
    f = 520 * pk * 2 ** (1.6 * (1 - np.exp(-tarr(n) / 0.05)))
    s.add(sat(np.sin(phase(f)) * exp_env(n, 0.07, 0.003), 1.2), 0, 0, name="chirp-up")
    air = filt(noise(n, R), "hp", 5200 * p.kb, 0.7071, order=2) * exp_env(n, 0.05, 0.004)
    s.add(air, 0, -9, name="air")
    s.add(bell(nsamp(0.4), 1560 * pk * 1.0, 3.0, 1.0, 0.12, 0.05), 0.006, -14, name="glint")
    s.add(_click_layer(p, R, 0.8, 3, lo=2800), 0, -9, name="click")
    s.add(reverb(np.sin(phase(f))[: nsamp(0.1)] * exp_env(nsamp(0.1), 0.04), 0.5 * p.room + 0.1, -12, 0.5, 0.0, 92), 0, 0, name="room")


@recipe("disappear", "ui", "Disappear: downward chirp closing a low-pass + short dull pop. For elements leaving.", level=-11, rng_db=12, params="pitch intensity brightness")
def r_disappear(p, s):
    pk, R = p.pk, p.rng
    n = nsamp(0.26)
    f = 880 * pk * 2 ** (-1.3 * (1 - np.exp(-tarr(n) / 0.06)))
    y = np.sin(phase(f)) * exp_env(n, 0.07, 0.002)
    y = sweep(y, "lp", 5000 * p.kb * np.exp(-tarr(n) / 0.07) + 350, 0.9)
    s.add(y, 0, 0, name="chirp-down")
    nz = sweep(noise(n, R), "lp", 3500 * p.kb * np.exp(-tarr(n) / 0.05) + 300, 0.8) * exp_env(n, 0.04, 0.003)
    s.add(nz, 0, -10, name="air-close")
    s.add(sub_thump(nsamp(0.08), 150 * pk, 90 * pk, 0.015, 0.03, 1.2), 0.002, -9, name="thock")


@recipe("click", "ui", "UI click: crisp noise tick + resonant body + low thock. variant 0 soft, 1 mechanical (down+up), 2 glass, 3 key.", level=-12, rng_db=12, params="variant brightness pitch")
def r_click(p, s):
    pk, R = p.pk, p.rng
    v = p.variant % 4
    f_res = (1100, 1600, 3200, 950)[v] * pk * p.kb * (0.93 + 0.14 * R.random())
    n = nsamp(0.06)
    s.add(_click_layer(p, R, (0.7, 1.0, 1.3, 0.8)[v], 2.5, lo=(2000, 2600, 4200, 1800)[v]), 0, -2, name="noise-click")
    res = filt(noise(n, R), "bp", f_res, 6.0, order=2) * exp_env(n, (0.012, 0.014, 0.02, 0.011)[v], 0.0003)
    s.add(res / (np.max(np.abs(res)) + 1e-9), 0, -4, name="resonant-body")
    th = (170, 190, 260, 140)[v] * pk
    s.add(sub_thump(nsamp(0.07), th, th * 0.65, 0.012, 0.02 + 0.01 * (v == 3), 1.2, 0.0006), 0, -4 - 4 * (v == 2), name="thock")
    if v == 1:
        s.add(_click_layer(p, p.sub_rng(9), 0.7, 2, lo=2200), 0.055, -9, name="release-click")
    if v == 2:
        s.add(bell(nsamp(0.15), 4200 * pk, 2.76, 0.5, 0.05, 0.02), 0, -12, name="glass-ring")
    s.add(reverb(res[: nsamp(0.03)], 0.22 * p.room + 0.04, -15, 0.8, 0.0, 93), 0, 0, name="room")


@recipe("key", "ui", "Keyboard keystroke for typing: dull click + case knock + soft thock. variant 0 key, 1 space (deeper), 2 enter (heavy).", level=-16, rng_db=10, params="variant seed")
def r_key(p, s):
    pk, R = p.pk, p.rng
    v = p.variant % 3
    amp = 0.6 + 0.4 * R.random()
    s.add(_click_layer(p, R, 0.5, 3, lo=1500 + 600 * R.random()) * amp, 0, -3, name="switch-click")
    f_res = (900 + 500 * R.random()) * pk * (0.7 if v else 1.0)
    n = nsamp(0.05)
    r = filt(noise(n, R), "bp", f_res, 5.0, order=2) * exp_env(n, 0.011, 0.0003)
    s.add(r / (np.max(np.abs(r)) + 1e-9) * amp, 0, -5, name="case-knock")
    th = (165, 105, 90)[v] * pk * (0.92 + 0.16 * R.random())
    s.add(sub_thump(nsamp(0.09), th, th * 0.7, 0.015, (0.022, 0.04, 0.05)[v], 1.2, 0.0008) * amp, 0.0005, -2.5 - (v == 0) * 1.0, name="thock")
    s.add(reverb(r[: nsamp(0.03)], 0.18 * p.room + 0.03, -17, 0.9, 0.0, 94), 0, 0, name="room")


@recipe("tick", "ui", "Tick: tiny wood-block tick, bandpass ring 1-2 kHz + click. For small UI steps, ruler marks, hover.", level=-18, rng_db=10, params="pitch brightness variant")
def r_tick(p, s):
    pk, R = p.pk, p.rng
    f = (1500 + 500 * (p.variant % 3)) * pk * p.kb
    n = nsamp(0.05)
    ring = filt(noise(n, R), "bp", f, 9.0, order=2) * exp_env(n, 0.012, 0.0002)
    s.add(ring / (np.max(np.abs(ring)) + 1e-9), 0, 0, name="wood-ring")
    s.add(np.sin(phase(np.full(n, f * 0.55))) * exp_env(n, 0.006, 0.0003), 0, -7, name="sine-body")
    s.add(_click_layer(p, R, 0.6, 2, lo=3000), 0, -6, name="click")
    s.add(sub_thump(nsamp(0.04), 160 * pk, 110 * pk, 0.01, 0.015, 1.1, 0.0006), 0, -10, name="tiny-thock")


# ============================================================================= TONAL (key-tuned)
def _pluck(n, f, tau, attack=0.002, h2=0.25, glide_st=0.0):
    t = tarr(n)
    ff = f * 2 ** (glide_st * np.exp(-t / 0.02) / 12) if glide_st else np.full(n, f)
    y = np.sin(phase(ff)) + h2 * np.sin(phase(ff * 2)) + 0.06 * np.sin(phase(ff * 3))
    return y * exp_env(n, tau, attack)


@recipe("blip", "tonal", "Scale-tuned UI blip. degree = scale degree, variant 0 sine pluck, 1 triangle w/ pitch dip, 2 marimba, 3 bubble.", level=-14, rng_db=10, params="key scale degree variant")
def r_blip(p, s):
    pk = p.pk
    f = scale_hz(p.key, p.scale, p.degree, 5) * pk
    v = p.variant % 4
    n = nsamp(0.3)
    if v == 0:
        y = _pluck(n, f, 0.09, 0.002)
        y = filt(y, "lp", 3500 * p.kb, 0.7)
    elif v == 1:
        y = np.sin(phase(f * 2 ** (np.exp(-tarr(n) / 0.02) * 2 / 12))) * exp_env(n, 0.1, 0.002)
        y = filt(y + 0.5 * osc_tri(np.full(n, f)) * exp_env(n, 0.08), "lp", 4000 * p.kb)
    elif v == 2:
        y = modal(n, f, [1, 4.0, 9.9], [1, 0.35, 0.1], [0.14, 0.03, 0.012])
    else:
        ff = f * (1 + 0.7 * (1 - np.exp(-tarr(n) / 0.012)))
        y = np.sin(phase(ff)) * exp_env(n, 0.06, 0.001)
    s.add(y, 0, 0, name="note")
    s.add(_click_layer(p, p.rng, 0.5, 2, lo=3200), 0, -14, name="tick")
    s.add(np.sin(phase(np.full(nsamp(0.15), f / 2))) * exp_env(nsamp(0.15), 0.05, 0.003), 0, -9, name="octave-below")
    s.add(reverb(y[: nsamp(0.1)], 0.5 * p.room + 0.1, -12, 0.5, 0.0, 95), 0, 0, name="room")


@recipe("dial-tick", "tonal", "Count-up tick whose PITCH RISES with value (0..1) across one octave of the scale. Register one per number step with value=i/N.", level=-16, rng_db=8, params="value key scale")
def r_dial(p, s):
    pk = p.pk
    steps = SCALES.get(p.scale, SCALES["major-pentatonic"])
    m_lo = 12 * (4 + 1) + key_pc(p.key)
    m = m_lo + float(p.value) * 12.0
    m = quantize_midi(m, p.key, p.scale)
    f = midi_hz(m) * pk
    n = nsamp(0.14)
    y = modal(n, f, [1, 3.99, 7.8], [1, 0.3, 0.08], [0.06, 0.012, 0.006])
    s.add(y, 0, 0, name="tuned-mallet")
    s.add(_click_layer(p, p.rng, 0.5, 2, lo=3000), 0, -11, name="click")
    s.add(sub_thump(nsamp(0.05), 150 * pk, 100 * pk, 0.012, 0.02, 1.1), 0, -10, name="thock")


@recipe("chime", "tonal", "Key-tuned bell chime: root then fifth (FM bell) + octave-below body + soft room. For success-lite, notifications.", level=-9, rng_db=10, params="key scale pitch brightness")
def r_chime(p, s):
    pk, R = p.pk, p.rng
    f1 = scale_hz(p.key, p.scale, 0, 5) * pk
    f2 = f1 * 2 ** (7 / 12)
    n1 = nsamp(1.4)
    s.add(bell(n1, f1, 3.5, 1.6 * (0.6 + p.brightness), 0.55, 0.1), 0, 0, name="bell-root", fade_out=0.4)
    s.add(bell(n1, f2, 3.5, 1.6 * (0.6 + p.brightness), 0.7, 0.1), 0.085, -1.5, name="bell-fifth", fade_out=0.4)
    s.add(np.sin(phase(np.full(n1, f1 / 4))) * exp_env(n1, 0.35, 0.004), 0.0, -6, width=0, name="body-low", fade_out=0.4)
    s.add(_click_layer(p, R, 0.5, 2, lo=4200), 0, -14, name="strike")
    s.add(reverb(bell(nsamp(0.4), f1, 3.5, 1.0, 0.2, 0.05), 1.1 * p.room + 0.1, -8, 0.45, 0.012, 96), 0, 0, name="hall")


@recipe("success", "tonal", "Success: 4-note ascending arpeggio in the key + final sparkle + soft bass note + hall. anchor = first note.", level=-8, rng_db=10, params="key scale pitch brightness")
def r_success(p, s):
    pk = p.pk
    degs = [0, 1, 2, 4] if len(SCALES.get(p.scale, [0] * 5)) <= 6 else [0, 2, 4, 7]
    t = 0.0
    for k, dg in enumerate(degs):
        f = scale_hz(p.key, p.scale, dg, 5) * pk
        last = k == len(degs) - 1
        n = nsamp(1.2 if last else 0.5)
        s.add(bell(n, f, 3.5, 1.5, 0.5 if last else 0.18, 0.09), t, -(len(degs) - 1 - k) * 1.2, name=f"note-{k}")
        t += 0.075
    tl = t - 0.075
    fr = scale_hz(p.key, p.scale, 0, 3) * pk
    s.add(np.sin(phase(np.full(nsamp(1.0), fr))) * exp_env(nsamp(1.0), 0.4, 0.01), tl, -7, width=0, name="bass-note")
    ps = nsamp(0.9)
    st = filt(noise(ps, p.rng), "bp", 8200 * p.kb, 0.8, order=2) * exp_env(ps, 0.2, 0.002)
    s.add(st, tl, -16, name="air-sheen")
    s.add(reverb(bell(nsamp(0.5), scale_hz(p.key, p.scale, 4, 5) * pk, 3.5, 1.0, 0.25, 0.06), 1.3 * p.room + 0.1, -7, 0.45, 0.01, 97), tl, 0, name="hall")
    s.anchor = 0.0


@recipe("glass-ding", "tonal", "Glass ding: modal synthesis (inharmonic partials 1, 2.32, 4.25, 6.63, 9.38) + air click. Real 6-11 kHz content.", level=-10, rng_db=10, params="key scale pitch brightness")
def r_glass(p, s):
    pk = p.pk
    f0 = scale_hz(p.key, p.scale, p.degree, 6) * pk
    n = nsamp(1.3)
    s.add(modal(n, f0, [1, 2.32, 4.25, 6.63, 9.38], [1, 0.6, 0.35, 0.2, 0.1], [0.7, 0.45, 0.28, 0.18, 0.1]), 0, 0, name="glass-modes")
    s.add(noise_burst(nsamp(0.004), p.rng, 0.0012, lo=6000, order=2) * 0.7, 0, -6, name="air-click")
    s.add(sat(np.sin(phase(np.full(n, f0 / 4))) * exp_env(n, 0.12, 0.004), 1.5), 0, -12, width=0, name="body")
    s.add(reverb(modal(nsamp(0.3), f0, [1, 2.32], [1, 0.5], [0.15, 0.1]), 0.9 * p.room + 0.1, -9, 0.4, 0.008, 98), 0, 0, name="room")


@recipe("shimmer", "tonal", "Shimmer / sparkle: 6-9 scale-tuned high pings (descending/ascending walk) + 6-11 kHz air sheen + long hall. Gives the 'air band'.", level=-12, rng_db=10, params="key scale variant(0 down,1 up) brightness")
def r_shimmer(p, s):
    pk, R = p.pk, p.rng
    cnt = 6 + int(R.integers(0, 4))
    deg = 9 + int(R.integers(0, 3))
    t = 0.0
    for k in range(cnt):
        f = scale_hz(p.key, p.scale, deg, 5) * pk
        n = nsamp(0.9)
        y = np.sin(phase(np.full(n, f))) + 0.3 * np.sin(phase(np.full(n, f * 2.0))) + 0.08 * np.sin(phase(np.full(n, f * 3.01)))
        s.add(y * exp_env(n, 0.22 + 0.2 * R.random(), 0.0012), t, -k * 1.0, name="ping")
        t += 0.03 + 0.025 * R.random()
        deg += (1 if p.variant % 2 else -1) * int(R.integers(1, 3))
        deg = max(deg, 7)
    n = nsamp(1.0)
    sheen = filt(noise(n, R), "bp", 8400 * p.kb, 0.6, order=2) * exp_env(n, 0.3, 0.003)
    s.add(sheen, 0, -3, name="air-sheen", fade_out=0.3)
    s.add(filt(noise(n, p.sub_rng(5)), "hp", 6500, 0.7, order=2) * exp_env(n, 0.18, 0.001), 0, -14, name="air-sizzle")
    s.add(reverb(sheen[: nsamp(0.3)] * 0.5 + _pluck(nsamp(0.3), scale_hz(p.key, p.scale, 9, 5) * pk, 0.1), 1.6 * p.room + 0.2, -6, 0.35, 0.015, 99), 0, 0, name="hall")
    s.anchor = 0.001


@recipe("error", "tonal", "Error / deny: two falling low notes (minor third) with saturation + dull thump. Not a beep: lowpassed, short.", level=-8, rng_db=10, params="key pitch")
def r_error(p, s):
    pk = p.pk
    f = scale_hz(p.key, p.scale, 0, 3) * pk * 1.0
    for k, st in enumerate((0, -3)):
        n = nsamp(0.2)
        ff = f * 2 ** (st / 12)
        y = osc_saw(np.full(n, ff)) * 0.6 + osc_square(np.full(n, ff * 1.005), 0.4) * 0.4
        y = sweep(y, "lp", 1700 * p.kb * np.exp(-tarr(n) / 0.1) + 300, 1.1)
        s.add(sat(y * exp_env(n, 0.09, 0.004), 2.0), k * 0.13, 0, name=f"buzz-{k}", fade_out=0.06)
    s.add(sub_thump(nsamp(0.2), 100 * pk, 55 * pk, 0.03, 0.09, 1.6), 0, -4, name="thump")
    s.add(_click_layer(p, p.rng, 0.5, 3, lo=1600), 0, -9, name="click")
    s.add(reverb(sub_thump(nsamp(0.15), 110 * pk, 70 * pk, 0.03, 0.05), 0.4 * p.room + 0.05, -11, 0.8, 0.0, 100), 0, 0, name="room")


@recipe("stinger", "tonal", "Musical stinger: key chord stab (detuned saws, closing lowpass) over a soft impact + hall. Brand/section accent, 1.4 s.", level=-4, rng_db=12, params="key scale intensity")
def r_stinger(p, s):
    pk, R, i = p.pk, p.rng, p.intensity
    n = nsamp(p.length or 1.5)
    ch = chord_semis(p.scale) + [12]
    base = scale_midi(p.key, p.scale, 0, 3)
    chord = np.zeros(n)
    for k, st in enumerate(ch):
        f = midi_hz(base + st) * pk
        chord += sum(osc_saw(np.full(n, f * 2 ** (c / 1200))) for c in (-8, 8)) / 2
    chord = sweep(chord, "lp", 400 + 5200 * p.kb * np.exp(-tarr(n) / 0.18), 1.3) * exp_env(n, 0.55, 0.004)
    s.add(chord, 0, -3, name="chord-stab", fade_out=0.4)
    s.add(sub_thump(n, 90 * pk, 42 * pk, 0.04, 0.35, 1.6), 0, 0, name="sub", fade_out=0.5)
    s.add(sub_thump(nsamp(0.3), 210 * pk, 80 * pk, 0.03, 0.08, 2.2), 0, -5, name="body")
    s.add(_click_layer(p, R, 1.0, 6), 0, -4, name="crack")
    s.add(reverb(chord[: nsamp(0.5)], 1.4 * p.room + 0.1, -7, 0.5, 0.01, 101), 0, 0, name="hall")
    s.master_sat = 1.4


@recipe("reveal", "hit", "Reveal: short upward whoomph that lands on the anchor + soft sub thud + sparkle after. For 'ta-da' moments (lighter than impact).", level=-5, rng_db=12, params="intensity key scale brightness")
def r_reveal(p, s):
    pk, R, i = p.pk, p.rng, p.intensity
    lead = 0.14
    n = nsamp(lead)
    x = np.linspace(0, 1, n)
    w = sweep(noise(n, R, "pink"), "bp", 300 * (6500 * p.kb / 300) ** x, 1.2, 24) * x ** 2.0
    s.add(w / (np.max(np.abs(w)) + 1e-9), 0, -4, name="whoomph-lead")
    s.add(sub_thump(nsamp(0.7), 95 * pk, 46 * pk, 0.04, 0.2 + 0.1 * i, 1.5), lead, 0, name="sub-thud")
    s.add(sub_thump(nsamp(0.25), 200 * pk, 90 * pk, 0.03, 0.07, 2.0), lead, -5, name="body")
    s.add(_click_layer(p, R, 0.9, 5), lead, -5, name="click")
    f = scale_hz(p.key, p.scale, 4, 5) * pk
    s.add(bell(nsamp(1.0), f, 3.5, 1.2, 0.4, 0.1), lead + 0.01, -11, name="bell")
    sh = filt(noise(nsamp(0.7), p.sub_rng(8)), "bp", 8000 * p.kb, 0.8, order=2) * exp_env(nsamp(0.7), 0.2, 0.002)
    s.add(sh, lead, -12, name="air")
    s.add(reverb(sub_thump(nsamp(0.3), 130 * pk, 60 * pk, 0.04, 0.1), 1.1 * p.room + 0.1, -9, 0.55, 0.01, 102), lead, 0, name="hall")
    s.anchor = lead
    s.master_sat = 1.2


# ============================================================================= DIGITAL
@recipe("glitch", "digital", "Glitch: 5-9 stuttered slices of bit-crushed noise, square blips and ring-mod, hard gated. 0.25-0.5 s. variant changes the slice mix.", level=-9, rng_db=10, params="dur brightness variant")
def r_glitch(p, s):
    R = p.rng
    total = p.dur or p.length or 0.34
    t = 0.0
    k = 0
    while t < total:
        L = float(R.choice([0.012, 0.02, 0.03, 0.045]))
        n = nsamp(L)
        kind = int(R.integers(0, 4)) if p.variant == 0 else (p.variant % 4)
        f = float(R.choice([420, 640, 960, 1400, 2100, 3200])) * p.pk
        if kind == 0:
            y = bitcrush(filt(noise(n, R), "hp", 800 * p.kb), 4, int(R.integers(2, 8)))
        elif kind == 1:
            y = osc_square(np.full(n, f), 0.3 + 0.4 * R.random())
        elif kind == 2:
            y = np.sin(phase(np.full(n, f))) * np.sin(phase(np.full(n, f * 0.37 + 90)))
        else:
            y = bitcrush(osc_saw(glide(f, f * 0.5, n)), 5, 3)
        y = y * (np.hanning(n) ** 0.3)
        rep = 1 + int(R.integers(0, 3))
        for r in range(rep):
            s.add(y * (1.0 - 0.15 * r), t + r * L, -2 * k % 5 * 0.5, pan=float(R.uniform(-0.7, 0.7)), name="slice")
        t += L * rep + float(R.choice([0.0, 0.006, 0.014, 0.03]))
        k += 1
    s.add(_click_layer(p, R, 1.0, 3, lo=3000), 0, -4, name="click-in")
    s.add(sub_thump(nsamp(0.12), 130 * p.pk, 60 * p.pk, 0.02, 0.04, 1.6), 0, -8, name="thump")
    s.master_sat = 1.5
    s.anchor_search = 0.04


@recipe("zap", "digital", "Zap / laser: FM sweep 3.5 kHz -> 180 Hz in 0.16 s, closing filter, crackle band, small sub. Power-up/tech accent.", level=-8, rng_db=10, params="pitch brightness variant")
def r_zap(p, s):
    pk, R = p.pk, p.rng
    n = nsamp(0.32)
    t = tarr(n)
    fc = (180 + 3400 * p.kb) * pk * np.exp(-t / 0.05)
    fc = np.maximum(fc, 140 * pk)
    idx = 6.0 * np.exp(-t / 0.06)
    y = np.sin(phase(fc) + idx * np.sin(phase(fc * 2.0))) * exp_env(n, 0.1, 0.0008)
    s.add(sat(y, 1.6), 0, 0, name="fm-sweep")
    cr = filt(noise(n, R), "bp", 6500 * p.kb, 1.0, order=2) * exp_env(n, 0.03, 0.0005)
    s.add(cr, 0, -9, name="crackle")
    s.add(sub_thump(nsamp(0.15), 120 * pk, 55 * pk, 0.03, 0.06, 1.5), 0, -7, name="sub")
    s.add(reverb(y[: nsamp(0.1)], 0.4 * p.room + 0.05, -13, 0.6, 0.0, 103), 0, 0, name="room")


# ============================================================================= TEXTURE (paper, tape, camera ...)
def _crackle(n, rng, rate_curve, tau=0.0007, lo=900, hi=None):
    """Poisson impulse train with time-varying rate (events/s), each impulse a tiny decaying noise grain, band-limited."""
    r = np.asarray(rate_curve, dtype=float)
    imp = (rng.random(n) < r / SR).astype(float) * rng.uniform(0.2, 1.0, n)
    k = nsamp(tau * 6)
    g = np.exp(-tarr(k) / tau) * rng.standard_normal(k)
    y = signal.fftconvolve(imp, g)[:n]
    y = filt(y, "hp", lo, 0.7071)
    if hi:
        y = filt(y, "lp", hi, 0.7071)
    return y


@recipe("paper-rip", "texture", "Paper rip: irregular grain crackle with rising density + band-passed fibre noise + low tear. 0.35-0.9 s.", level=-9, rng_db=10, params="dur brightness")
def r_rip(p, s):
    dur = p.dur or p.length or 0.45
    n = nsamp(dur)
    R = p.rng
    x = np.linspace(0, 1, n)
    rate = 1600 * (0.35 + 0.65 * np.sin(np.pi * x ** 0.8)) * (0.6 + 0.4 * np.abs(_norm(smooth_noise(n, R, 35))))
    y = _crackle(n, R, rate, 0.0006, 1100 * p.kb, 9000 * p.kb)
    y = y / (np.max(np.abs(y)) + 1e-9)
    amp = np.sin(np.pi * np.clip(x, 0, 1)) ** 0.6 * (0.5 + 0.5 * np.clip(_norm(smooth_noise(n, p.sub_rng(4), 28)) * 0.5 + 0.7, 0, 1.4))
    s.add(y * amp, 0, 0, name="grain-crackle")
    fib = filt(noise(n, p.sub_rng(2)), "bp", 3200 * p.kb, 0.8, order=2) * amp * 0.5
    s.add(fib, 0, -7, name="fibre-noise")
    low = filt(noise(n, p.sub_rng(3), "pink"), "bp", 320, 0.8, order=2) * amp
    s.add(low / (np.max(np.abs(low)) + 1e-9), 0, -10, name="tear-body")
    s.add(reverb(y[: nsamp(0.2)], 0.3 * p.room + 0.05, -17, 0.8, 0.0, 104), 0, 0, name="room")
    s.anchor = 0.0 + dur * 0.12


@recipe("paper-slap", "texture", "Paper slap: broadband crack + low thump + short rattle/flutter. For cutouts landing on the table.", level=-6, rng_db=12, params="intensity brightness pitch")
def r_slap(p, s):
    pk, R, i = p.pk, p.rng, p.intensity
    s.add(noise_burst(nsamp(0.03), R, 0.0075, lo=500 * p.kb, order=1) * 1.0, 0, -1, name="slap-crack")
    s.add(_click_layer(p, R, 1.0, 3, lo=2500), 0, -4, name="click")
    s.add(sub_thump(nsamp(0.2), (150 + 20 * i) * pk, 78 * pk, 0.02, 0.05 + 0.03 * i, 1.8), 0, -3, name="thump")
    n = nsamp(0.16)
    flut = filt(noise(n, R), "bp", 3300 * p.kb, 0.8, order=2) * exp_env(n, 0.04, 0.003) * (0.55 + 0.45 * np.sin(phase(np.full(n, 46.0))))
    s.add(flut, 0.012, -9, name="flutter")
    s.add(reverb(sub_thump(nsamp(0.08), 160 * pk, 90 * pk, 0.02, 0.03), 0.3 * p.room + 0.05, -11, 0.8, 0.0, 105), 0, 0, name="room")


@recipe("tape", "texture", "Tape strip: short ripping zip (0.18 s dense grains) ending in a soft stick. For tape/label strips appearing.", level=-9, rng_db=10, params="dur brightness")
def r_tape(p, s):
    dur = p.dur or p.length or 0.2
    n = nsamp(dur)
    R = p.rng
    x = np.linspace(0, 1, n)
    rate = 2600 * (0.4 + 0.6 * x)
    y = _crackle(n, R, rate, 0.0004, 1800 * p.kb, 11000)
    y = y / (np.max(np.abs(y)) + 1e-9) * (x ** 0.5) * (1 - 0.4 * x)
    s.add(y, 0, 0, name="zip-grains")
    s.add(filt(noise(n, p.sub_rng(2)), "bp", 4800 * p.kb, 1.0, order=2) * x * 0.3, 0, -9, name="adhesive-hiss")
    s.add(_click_layer(p, R, 0.5, 3, lo=1400), dur, -6, name="stick-click")
    s.add(sub_thump(nsamp(0.08), 140 * p.pk, 85 * p.pk, 0.015, 0.03, 1.2), dur, -8, name="stick-thump")
    s.anchor = dur
    s.min_len = dur


@recipe("camera-shutter", "texture", "Camera shutter: two mechanical clacks (open strong, close softer 38 ms later) with body resonance.", level=-9, rng_db=10, params="brightness pitch")
def r_shutter(p, s):
    pk, R = p.pk, p.rng
    for k, (dt, g, f) in enumerate(((0.0, 0.0, 3400), (0.038, -5.0, 2600))):
        n = nsamp(0.05)
        a = filt(noise(n, p.sub_rng(k)), "bp", f * p.kb * pk, 1.6, order=2) * exp_env(n, 0.007, 0.0002)
        s.add(a / (np.max(np.abs(a)) + 1e-9), dt, g, name=f"clack-{k}")
        s.add(bell(nsamp(0.06), 780 * pk, 2.1, 0.5, 0.012, 0.01), dt, g - 8, name=f"mech-{k}")
        s.add(sub_thump(nsamp(0.05), 170 * pk, 110 * pk, 0.01, 0.018, 1.2), dt, g - 6, name=f"thock-{k}")
    s.add(reverb(noise_burst(nsamp(0.03), R, 0.006, lo=1500), 0.35 * p.room + 0.05, -13, 0.7, 0.0, 106), 0, 0, name="room")


@recipe("heartbeat", "texture", "Heartbeat lub-dub at `bpm` (default 66), `count` beats (default 2). Sub-heavy, dry. anchor = first thump.", level=-6, rng_db=10, params="bpm count intensity")
def r_heart(p, s):
    pk = p.pk
    beat = 60.0 / p.bpm
    for b in range(int(p.count or 2)):
        t0 = b * beat
        s.add(sub_thump(nsamp(0.35), 80 * pk, 46 * pk, 0.03, 0.12, 1.4, 0.004), t0, 0, name="lub")
        s.add(sub_thump(nsamp(0.3), 72 * pk, 42 * pk, 0.03, 0.09, 1.4, 0.004), t0 + 0.2, -3.5, name="dub")
        s.add(filt(noise(nsamp(0.06), p.sub_rng(b)), "lp", 300, 0.7) * exp_env(nsamp(0.06), 0.015, 0.002) * 0.5, t0, -10, name="skin")
    s.anchor = 0.003


@recipe("drone", "bed", "Sustained pad/drone on the key root (detuned saws + fifth + sub + slow filter LFO) with fades. Loop-safe when loop=true. Default 6 s. Use under a scene as a bed.", level=-14, rng_db=6, params="length key scale brightness loop")
def r_drone(p, s):
    L = p.length or p.dur or 6.0
    n = nsamp(L)
    root = scale_hz(p.key, p.scale, 0, 2) * p.pk
    t = tarr(n)
    cyc = max(1, int(round(L * 0.25)))                               # integer LFO cycles -> loop-safe
    lfo = 0.5 + 0.5 * np.sin(TAU * cyc * t / L)
    y = np.zeros(n)
    for k, (r, g) in enumerate(((1.0, 1.0), (1.5, 0.5), (2.0, 0.6), (3.0, 0.15))):
        for c in (-9, 0, 9):
            y += g * osc_saw(np.full(n, root * r * 2 ** (c / 1200)), p.sub_rng(k).random())
    y = sweep(y, "lp", 250 + (900 * p.kb) * (0.4 + 0.6 * lfo), 1.2, 128)
    s.add(y / (np.max(np.abs(y)) + 1e-9), 0, 0, name="saw-pad")
    s.add(np.sin(phase(np.full(n, root / 2))) * 0.9, 0, -3, width=0, name="sub")
    rum = filt(noise(n, p.rng, "brown"), "lp", 160, 0.7, order=2)
    s.add(rum / (np.max(np.abs(rum)) + 1e-9), 0, -12, name="rumble")
    snd_env = np.ones(n)
    if not p.loop:
        snd_env = np.minimum(1.0, t / 0.6) * np.minimum(1.0, (L - t) / 0.8)
    for k in range(len(s.items)):
        st, at, g, nm = s.items[k]
        s.items[k] = (st * snd_env[: len(st), None], at, g, nm)
    s.anchor = 0.0
    s.min_len = L


# ============================================================================= typing (standalone sequence)
@recipe("typing", "ui", "Typing sequence of `dur` seconds at `cps` keys/s with seeded irregular rhythm, occasional space/enter. (sync_cues places keys individually on frames.)", level=-16, rng_db=8, params="dur cps seed")
def r_typing(p, s):
    dur = p.dur or p.length or 1.2
    R = p.rng
    t = 0.0
    k = 0
    while t < dur:
        v = 1 if (k % 6 == 5) else 0
        key = render("key", seed=int(R.integers(0, 10 ** 6)), variant=v, brightness=p.brightness, pitch=p.pitch, room=p.room)
        s.add(key.data, t - key.anchor + 0.0, float(R.uniform(-2.5, 0)), name="key")
        t += (1.0 / p.cps) * float(np.clip(R.normal(1.0, 0.28), 0.5, 1.8))
        if R.random() < 0.06:
            t += 0.12 + 0.2 * R.random()
        k += 1
    s.anchor = 0.0
    s.min_len = dur


# ============================================================================= blip family (composites)
def _blip_seq(p, s, degs, gap, name):
    for k, d in enumerate(degs):
        b = render("blip", degree=d, key=p.key, scale=p.scale, pitch=p.pitch, variant=p.variant, brightness=p.brightness, seed=p.seed + k, room=p.room)
        s.add(b.data, k * gap - b.anchor, -1.0 * k, name=f"{name}-{k}")
    s.anchor = 0.0


@recipe("blip-up", "tonal", "Two scale-tuned blips rising (degree, degree+2). Confirm / next / toggle on.", level=-14, rng_db=10, params="key scale degree variant")
def r_blip_up(p, s):
    _blip_seq(p, s, [p.degree, p.degree + 2], 0.065, "up")


@recipe("blip-down", "tonal", "Two scale-tuned blips falling (degree+2, degree). Cancel / toggle off.", level=-14, rng_db=10, params="key scale degree variant")
def r_blip_down(p, s):
    _blip_seq(p, s, [p.degree + 2, p.degree], 0.065, "down")


@recipe("blip-double", "tonal", "Same scale-tuned blip twice, 75 ms apart. Notification / attention.", level=-14, rng_db=10, params="key scale degree variant")
def r_blip_double(p, s):
    _blip_seq(p, s, [p.degree, p.degree], 0.075, "double")


# ============================================================================= registry helpers
def _stereo_mono_check():
    pass


def list_recipes():
    rows = []
    for name, info in RECIPES.items():
        rows.append((name, info["cat"], info["desc"], info["params"]))
    return sorted(set(rows), key=lambda r: (r[1], r[0]))


def spectrogram_png(sound, path, title=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x = sound.data.mean(axis=1) if hasattr(sound, "data") else sound
    fig, ax = plt.subplots(2, 1, figsize=(8, 5), gridspec_kw=dict(height_ratios=[1, 2]), sharex=True)
    tt = np.arange(len(x)) / SR
    ax[0].plot(tt, x, lw=0.4); ax[0].axvline(sound.anchor, color="r", lw=0.8); ax[0].set_ylabel("amp")
    ax[0].set_title(title or f"{sound.recipe}  anchor={sound.anchor * 1000:.1f} ms  dur={sound.duration:.2f}s")
    f, t, S = signal.spectrogram(x, SR, nperseg=1024, noverlap=896, window="hann")
    ax[1].pcolormesh(t, f, 10 * np.log10(S + 1e-12), shading="auto", vmin=-110, vmax=-30, cmap="magma")
    ax[1].set_yscale("symlog", linthresh=500); ax[1].set_ylim(20, 16000); ax[1].set_ylabel("Hz"); ax[1].set_xlabel("s")
    ax[1].axvline(sound.anchor, color="c", lw=0.8)
    fig.tight_layout(); fig.savefig(path, dpi=90); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description="Procedural layered SFX designer", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--recipe")
    ap.add_argument("--out")
    ap.add_argument("--all", metavar="DIR")
    ap.add_argument("--png", action="store_true", help="also write a spectrogram PNG next to the WAV")
    ap.add_argument("--float", action="store_true", help="write float32 WAV instead of PCM16")
    for k, v in P.defaults.items():
        if v is None:
            ap.add_argument("--" + k, type=float)
        elif isinstance(v, bool):
            ap.add_argument("--" + k, action="store_true")
        else:
            ap.add_argument("--" + k, type=type(v), default=None)
    a = ap.parse_args()
    if a.list:
        cur = None
        for name, cat, desc, params in list_recipes():
            if cat != cur:
                print(f"\n[{cat}]"); cur = cat
            print(f"  {name:<15} {desc}\n  {'':<15} params: {params}")
        return 0
    kw = {k: getattr(a, k) for k in P.defaults if getattr(a, k, None) is not None and getattr(a, k) is not False}
    if a.all:
        os.makedirs(a.all, exist_ok=True)
        meta = {}
        for name in sorted(set(RECIPES) - {n for n, i in RECIPES.items() if i["fn"].__name__ != RECIPES[n]["fn"].__name__}):
            sn = render(name, **kw)
            write_wav(os.path.join(a.all, name + ".wav"), sn.data, SR, 32 if a.float else 16)
            if a.png:
                spectrogram_png(sn, os.path.join(a.all, name + ".png"))
            meta[name] = sn.meta()
        json.dump(meta, open(os.path.join(a.all, "metadata.json"), "w"), indent=1)
        print(f"{len(meta)} recipes -> {a.all}")
        return 0
    if not a.recipe or not a.out:
        ap.error("need --recipe and --out (or --list / --all DIR)")
    sn = render(a.recipe, **kw)
    write_wav(a.out, sn.data, SR, 32 if a.float else 16)
    if a.png:
        spectrogram_png(sn, os.path.splitext(a.out)[0] + ".png")
    print(json.dumps(sn.meta(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
