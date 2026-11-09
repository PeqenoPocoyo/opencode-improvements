#!/usr/bin/env python3
"""musicgen.py - procedural SCRATCH music bed (numpy + scipy only, deterministic). Licensed / user-supplied music beats this.

It exists so a video can be timed, mixed and checked end to end when no licensed track is available, and so the bed can sit exactly
on the video's bar grid (bar 1 beat 1 at t = 0, or shifted). It is a bed, not a song: drums + sub bass + pad + pluck/keys, sidechain pump,
8-32 bars. Do NOT present it as finished music; say "scratch bed" in the hand-over.

CLI
  python3 musicgen.py --genre lofi --bpm 84 --key A --scale minor --bars 8 --seed 3 --out bed.wav
  python3 musicgen.py --genre techno --bpm 124 --bars 16 --drop-bar 4 --end hit --out bed.wav     # breakdown for 4 bars, drop on bar 5
  python3 musicgen.py --list
Python
  from musicgen import make_music
  audio, info = make_music('boom-bap', bpm=92, key='D', scale='minor-pentatonic', bars=8, seed=1)
  info['bar_len'], info['beats'], info['downbeats'], info['kicks']   # the exact grid (seconds), for sync and checks

Genres (families): techno, house, boom-bap, lofi, trap, pop-pluck, cinematic, ambient. Aliases: edm->house, hiphop->boom-bap,
chill->lofi, drill->trap, corporate->pop-pluck, epic->cinematic, pad->ambient.
Arc: flat (default) | build (drums enter progressively) ; drop_bar=N -> bars before N are a breakdown (pad + soft hats + riser), bar N
starts with a crash/sub hit and the full groove. end: 'hit' (final downbeat stab at bar `bars`), 'fade' (last bar fades), 'none', 'loop'
(overhang wraps to the start; length is exactly `bars` bars).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audiolib as A  # noqa: E402
import sfxgen as G  # noqa: E402
from audiolib import SR  # noqa: E402

ALIASES = {"edm": "house", "hiphop": "boom-bap", "hip-hop": "boom-bap", "chill": "lofi", "drill": "trap", "corporate": "pop-pluck",
           "pop": "pop-pluck", "epic": "cinematic", "pad": "ambient", "tech-house": "house", "club": "techno"}

# 16-step patterns, x = hit, o = soft/ghost, . = rest. Several kick variants per genre; one is picked per 2-bar phrase from the seed.
GENRES = {
    "techno": dict(
        kick=["x...x...x...x...", "x...x...x...x..o"], clap=["....x.......x..."], snare=[], hat=["..x...x...x...x."], chat=["x.o.x.o.x.o.x.o."],
        bass=["..x...x...x...x.", ".xx..xx..xx..xx."], arp=[], swing=0.0, side=12, bass_kind="sub", pad="dark", lp=3800, kick_tail=0.38, level=dict(kick=1.0, clap=.5, hat=.38, chat=.2, bass=.8, pad=.5, arp=.0)),
    "house": dict(
        kick=["x...x...x...x..."], clap=["....x.......x..."], snare=[], hat=["..x...x...x...x."], chat=["x.xox.xox.xox.xo"],
        bass=["..x...x...x...x.", ".x..x..x.x..x..."], arp=["x.x.x.x.x.x.x.x."], swing=0.04, side=10, bass_kind="sub", pad="chord", lp=5200, kick_tail=0.3, level=dict(kick=1.0, clap=.5, hat=.4, chat=.22, bass=.7, pad=.45, arp=.3)),
    "boom-bap": dict(
        kick=["x.....x..x......", "x.......x.x.....", "x..o..x..x.o...."], clap=[], snare=["....x.......x..."], hat=[], chat=["x.x.x.x.x.x.x.x.", "x.x.xox.x.x.xox."],
        bass=["x.....x..x......", "x.......x.x....."], arp=["x...o...x...o..."], swing=0.30, side=6, bass_kind="sub", pad="chord", lp=5200, kick_tail=0.3, level=dict(kick=1.0, snare=.8, chat=.28, bass=.8, pad=.4, arp=.35)),
    "lofi": dict(
        kick=["x.....x..x......", "x.......x.x....."], clap=[], snare=["....x.......x..."], hat=[], chat=["x.x.x.x.x.x.x.x.", "x.o.x.o.x.o.x.o."],
        bass=["x.....x..x......", "x.......x......."], arp=["x.....x.....x..."], swing=0.34, side=5, bass_kind="sub", pad="keys", lp=3600, kick_tail=0.26, level=dict(kick=.85, snare=.6, chat=.2, bass=.75, pad=.55, arp=.42)),
    "trap": dict(
        kick=["x.......x..x....", "x.....x.x......."], clap=["........x......."], snare=[], hat=[], chat=["xxxxxxxxxxxxxxxx", "x.x.xxx.x.x.xxx."], ohat=["......x.......x."],
        bass=["x.......x..x....", "x.....x.x......."], arp=[], swing=0.0, side=0, bass_kind="808", pad="dark", lp=4200, kick_tail=0.18, level=dict(kick=.5, clap=.6, chat=.26, bass=1.0, pad=.35, arp=.0)),
    "pop-pluck": dict(
        kick=["x.......x.x.....", "x...x...x...x..."], clap=["....x.......x..."], snare=[], hat=["x.x.x.x.x.x.x.x."], chat=[],
        bass=["x...x..x..x.....", "x.......x.x....."], arp=["x.xxx.xxx.xxx.xx", "x.x.x.x.x.x.x.x."], swing=0.06, side=7, bass_kind="sub", pad="chord", lp=6000, kick_tail=0.28, level=dict(kick=.9, clap=.45, hat=.25, bass=.7, pad=.32, arp=.5)),
    "cinematic": dict(
        kick=[], clap=[], snare=[], hat=[], chat=[], taiko=["x...............", "x.......x......."], bass=["x..............."], arp=["x.......x.......", "x...x...x...x..."],
        swing=0.0, side=0, bass_kind="drone", pad="strings", lp=2600, kick_tail=0.4, level=dict(taiko=.9, bass=.8, pad=.8, arp=.28, hat=0.0)),
    "ambient": dict(
        kick=[], clap=[], snare=[], hat=[], chat=[], pulse=["x...............", "x.......x......."], bass=["x..............."], arp=["x.......x.....x.", "..x.......x....."],
        swing=0.0, side=0, bass_kind="drone", pad="glass", lp=3000, kick_tail=0.4, level=dict(pulse=.5, bass=.7, pad=.9, arp=.35)),
}

PROGRESSIONS = {
    "minor": [[0, 5, 2, 6], [0, 3, 5, 4], [0, 6, 5, 6], [0, 2, 6, 3]],
    "major": [[0, 4, 5, 3], [0, 5, 3, 4], [0, 3, 4, 3], [0, 2, 5, 4]],
}


def parent_scale(scale):
    """7-note parent scale for chords: minorish -> minor, majorish -> major."""
    st = G.SCALES.get(scale, G.SCALES["minor"])
    if len(st) == 7:
        return scale, "minor" if 3 in st else "major"
    return ("minor" if 3 in st else "major"), "minor" if 3 in st else "major"


def chord_midis(key, scale, deg, octave=3, seventh=False):
    name, mode = parent_scale(scale)
    notes = [G.scale_midi(key, name, deg + k, octave) for k in ((0, 2, 4, 6) if seventh else (0, 2, 4))]
    return notes


def bass_midi(key, scale, deg):
    name, _ = parent_scale(scale)
    m = G.scale_midi(key, name, deg, 1)
    while m < 28:
        m += 12
    while m > 40:
        m -= 12
    return m


# ----------------------------------------------------------------------------- instruments (mono arrays)
def _n(s):
    return G.nsamp(s)


def inst_kick(rng, tail=0.3, punch=1.0, soft=False):
    n = _n(tail + 0.15)
    f = 44 + (150 - 44) * np.exp(-G.tarr(n) / 0.022)
    body = np.sin(G.phase(f)) * G.exp_env(n, tail * 0.55, 0.0006)
    body = G.sat(body, 2.0 if not soft else 1.3)
    k = body
    if not soft:
        c = G.noise_burst(_n(0.006), rng, 0.0012, lo=2500, order=2, attack=0.00005)
        k = k.copy(); k[: len(c)] += 0.18 * punch * c / (np.max(np.abs(c)) + 1e-9)
    return k / (np.max(np.abs(k)) + 1e-9)


def inst_clap(rng, size=1.0):
    n = _n(0.28)
    out = np.zeros(n)
    for d, g in ((0.0, 1.0), (0.011, 0.8), (0.021, 0.7), (0.033, 1.0)):
        b = G.filt(G.noise(_n(0.03), rng), "bp", 1500 * size, 1.1, order=2) * G.exp_env(_n(0.03), 0.007, 0.0004)
        i = _n(d); out[i:i + len(b)] += g * b
    tail = G.filt(G.noise(n, rng), "bp", 1300 * size, 1.0, order=2) * G.exp_env(n, 0.07, 0.034)
    out = out + 0.45 * tail
    return out / (np.max(np.abs(out)) + 1e-9)


def inst_snare(rng, dusty=False):
    n = _n(0.26)
    tone = np.sin(G.phase(185 + 75 * np.exp(-G.tarr(n) / 0.02))) * G.exp_env(n, 0.06, 0.0006)
    nz = G.filt(G.noise(n, rng), "bp", 2400, 0.8, order=1) * G.exp_env(n, 0.1, 0.0004)
    y = 0.7 * tone + 0.9 * nz
    if dusty:
        y = G.filt(y, "lp", 5000, 0.7, order=2)
    return y / (np.max(np.abs(y)) + 1e-9)


def inst_hat(rng, open_=False, bright=1.0):
    n = _n(0.22 if open_ else 0.05)
    y = G.filt(G.noise(n, rng), "hp", 6500 * bright, 0.8, order=2)
    y = G.filt(y, "lp", 11000, 0.7) * G.exp_env(n, 0.09 if open_ else 0.012, 0.0004)
    return y / (np.max(np.abs(y)) + 1e-9)


def inst_808(f, dur, glide_from=None):
    n = _n(dur)
    ff = np.full(n, f)
    if glide_from:
        ff = f + (glide_from - f) * np.exp(-G.tarr(n) / 0.05)
    y = np.sin(G.phase(ff)) * G.exp_env(n, dur * 0.6, 0.003)
    y = G.sat(y, 2.6)
    return y * np.minimum(1.0, (dur - G.tarr(n)) / 0.05)


def inst_sub(f, dur):
    n = _n(dur)
    ph = G.phase(np.full(n, f))
    y = np.sin(ph) + 0.28 * np.sin(2 * ph + 0.3) + 0.08 * np.sin(3 * ph)
    env = np.minimum(1.0, G.tarr(n) / 0.008) * np.minimum(1.0, np.maximum(dur - G.tarr(n), 0) / 0.05)
    return y * env


def inst_pad(notes, dur, rng, kind="chord", lp=1500.0, lfo_rate=0.15):
    n = _n(dur)
    t = G.tarr(n)
    y = np.zeros(n)
    detune = (-9, 0, 9) if kind != "glass" else (-4, 0, 4)
    for k, m in enumerate(notes):
        f = G.midi_hz(m)
        for c in detune:
            y += G.osc_saw(np.full(n, f * 2 ** (c / 1200)), rng.random())
    y /= max(1, len(notes) * len(detune)) ** 0.7
    lfo = 0.5 + 0.5 * np.sin(2 * math.pi * lfo_rate * t + rng.random() * 6.28)
    y = G.sweep(y, "lp", lp * (0.45 + 0.55 * lfo) if kind in ("dark", "strings") else lp * (0.6 + 0.4 * lfo), 0.9, 256)
    att = {"dark": 0.5, "strings": 0.9, "glass": 0.6, "chord": 0.04, "keys": 0.01}[kind]
    rel = {"dark": 0.5, "strings": 0.6, "glass": 0.8, "chord": 0.25, "keys": 0.6}[kind]
    env = np.minimum(1.0, t / att) * np.minimum(1.0, np.maximum(dur - t, 0) / rel)
    if kind in ("chord",):
        env *= 0.55 + 0.45 * np.exp(-t / 0.35)
    return y * env


def inst_keys(f, dur, rng):
    """FM electric piano (Rhodes-ish) with soft tremolo."""
    n = _n(dur)
    t = G.tarr(n)
    idx = 1.6 * np.exp(-t / 0.18) + 0.25
    y = np.sin(G.TAU * f * t + idx * np.sin(G.TAU * f * t)) + 0.25 * np.sin(G.TAU * f * 4 * t) * np.exp(-t / 0.03)
    y *= G.exp_env(n, dur * 0.7, 0.004) * (1 + 0.12 * np.sin(G.TAU * 5.2 * t))
    return y * np.minimum(1.0, np.maximum(dur - t, 0) / 0.06)


def inst_pluck(f, dur, bright=1.0):
    n = _n(dur)
    y = G._pluck(n, f, min(0.16, dur * 0.8), 0.002, 0.3)
    return G.filt(y, "lp", 3200 * bright, 0.8)


def inst_taiko(rng, size=1.0):
    n = _n(1.3)
    f = 48 + 70 * np.exp(-G.tarr(n) / 0.05)
    body = G.sat(np.sin(G.phase(f)) * G.exp_env(n, 0.5, 0.002), 1.6)
    skin = G.filt(G.noise(n, rng), "bp", 220, 0.8, order=2) * G.exp_env(n, 0.09, 0.0015)
    y = body + 0.35 * skin / (np.max(np.abs(skin)) + 1e-9)
    return y / (np.max(np.abs(y)) + 1e-9)


def inst_crash(rng, dur=1.4):
    n = _n(dur)
    y = G.filt(G.noise(n, rng), "hp", 1800, 0.7, order=2)
    y = G.sweep(y, "lp", 9000 * np.exp(-G.tarr(n) / 0.5) + 2500, 0.8, 64) * G.exp_env(n, 0.42, 0.001)
    return y / (np.max(np.abs(y)) + 1e-9)


def inst_riser(rng, dur):
    n = _n(dur)
    x = np.linspace(0, 1, n)
    y = G.sweep(G.noise(n, rng, "pink"), "bp", 300 * (7000 / 300) ** x, 1.2, 32)
    return y / (np.max(np.abs(y)) + 1e-9) * x ** 2.2


def inst_bell(f, rng):
    return G.modal(_n(1.8), f, [1, 2.32, 4.25, 6.63], [1, 0.4, 0.2, 0.08], [0.9, 0.5, 0.3, 0.2])


def inst_crackle(n, rng, density=14.0):
    out = np.zeros(n)
    k = int(density * n / SR)
    idx = rng.integers(0, n - 80, size=k)
    amp = rng.random(k) ** 3
    for i, a in zip(idx, amp):
        out[i] += a * (1 if rng.random() > 0.5 else -1)
    return G.filt(out, "bp", 3200, 0.5, order=1)


# ----------------------------------------------------------------------------- composition
def _place(buf, x, at_s, gain=1.0, wrap=False):
    i = int(round(at_s * SR))
    n = len(buf)
    if i >= n and not wrap:
        return
    L = len(x)
    if i + L <= n:
        buf[i:i + L] += x * gain
    elif wrap:
        a = n - i
        buf[i:] += x[:a] * gain
        j = 0
        rest = x[a:] * gain
        while len(rest) > 0:
            m = min(len(rest), n)
            buf[:m] += rest[:m]
            rest = rest[m:]
    else:
        buf[i:] += x[: n - i] * gain


def _steps(pat, bar, step, swing, bar_len):
    """times (s) and velocities for a 16-step pattern in bar `bar`."""
    out = []
    for s, ch in enumerate(pat):
        if ch == ".":
            continue
        sw = swing * step * 2 / 3 if s % 2 == 1 else 0.0
        out.append((bar * bar_len + s * step + sw, 1.0 if ch == "x" else 0.45, s))
    return out


def make_music(genre="pop-pluck", bpm=108.0, key="C", scale="minor-pentatonic", bars=8, seed=1, intensity=0.8, arc="flat",
               drop_bar=None, end="fade", swing=None, sr=SR, beats_per_bar=4):
    """Returns (stereo float32 audio, info). Bar 1 beat 1 is at t = 0."""
    genre = ALIASES.get(genre, genre)
    if genre not in GENRES:
        raise KeyError(f"unknown genre '{genre}'. Valid: {', '.join(GENRES)}")
    g = GENRES[genre]
    rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 424242])
    beat = 60.0 / bpm
    bar_len = beat * beats_per_bar
    step = beat / 4.0
    sw = g["swing"] if swing is None else swing
    loop = end == "loop"
    tail = 0.0 if loop else (2.2 if end == "hit" else 0.8)
    total = bars * bar_len + tail
    n = int(round(total * SR))
    L = {k: np.zeros(n) for k in ("kick", "clap", "hat", "bass", "pad", "arp", "perc", "fx")}
    lev = g["level"]
    parent, mode = parent_scale(scale)
    prog = PROGRESSIONS[mode][int(rng.integers(0, len(PROGRESSIONS[mode])))]
    slow = g["pad"] in ("strings", "glass", "dark") and genre in ("cinematic", "ambient")
    chord_bars = 2 if slow else 1
    kick_t = []
    pre_drop = lambda b: drop_bar is not None and b < drop_bar
    kick_variants = [inst_kick(np.random.default_rng([seed, 1, k]), g["kick_tail"], 1.0, soft=(genre in ("lofi",))) for k in range(3)]
    clap_variants = [inst_clap(np.random.default_rng([seed, 2, k]), 1.0 + 0.1 * k) for k in range(3)]
    hat_c = [inst_hat(np.random.default_rng([seed, 3, k]), False, 0.9 + 0.1 * k) for k in range(4)]
    hat_o = [inst_hat(np.random.default_rng([seed, 4, k]), True) for k in range(2)]
    snare_v = [inst_snare(np.random.default_rng([seed, 5, k]), genre in ("lofi", "boom-bap")) for k in range(3)]
    kc = 0
    for b in range(bars):
        drums_on = True
        bass_on = True
        pad_on = True
        arp_on = True
        if pre_drop(b):                                      # breakdown: pad + soft hats only
            drums_on = bass_on = arp_on = False
        elif arc == "build":
            if b == 0:
                drums_on = False
                bass_on = False
            elif b == 1:
                arp_on = False
        ph = b // 2
        ks = g["kick"]
        if drums_on and ks:
            pat = ks[ph % len(ks)] if len(ks) > 1 else ks[0]
            for t, v, s_ in _steps(pat, b, step, 0.0, bar_len):
                if genre == "trap" and rng.random() < 0.0:
                    continue
                _place(L["kick"], kick_variants[kc % 3], t, lev["kick"] * v * (0.95 + 0.1 * rng.random()), loop)
                kick_t.append(t); kc += 1
        if drums_on and g.get("clap"):
            for t, v, s_ in _steps(g["clap"][0], b, step, 0.0, bar_len):
                _place(L["clap"], clap_variants[int(rng.integers(0, 3))], t + 0.002, lev.get("clap", .5) * v, loop)
        if drums_on and g.get("snare"):
            for t, v, s_ in _steps(g["snare"][0], b, step, 0.0, bar_len):
                _place(L["clap"], snare_v[int(rng.integers(0, 3))], t, lev.get("snare", .7) * v * (0.9 + 0.2 * rng.random()), loop)
        hat_gain = lev.get("chat", 0.0) * (0.35 if pre_drop(b) else 1.0)
        if (drums_on or pre_drop(b)) and g.get("chat") and hat_gain > 0:
            pat = g["chat"][ph % len(g["chat"])] if len(g["chat"]) > 1 else g["chat"][0]
            for t, v, s_ in _steps(pat, b, step, sw, bar_len):
                vel = v * (0.75 + 0.25 * (1 if s_ % 4 == 0 else rng.random()))
                _place(L["hat"], hat_c[int(rng.integers(0, 4))], t, hat_gain * vel, loop)
        if drums_on and g.get("hat"):
            for t, v, s_ in _steps(g["hat"][0], b, step, sw, bar_len):
                _place(L["hat"], hat_o[s_ % 2], t, lev.get("hat", .3) * v, loop)
        if drums_on and g.get("ohat"):
            for t, v, s_ in _steps(g["ohat"][0], b, step, 0.0, bar_len):
                _place(L["hat"], hat_o[s_ % 2], t, 0.3, loop)
        if drums_on and g.get("taiko"):
            pat = g["taiko"][ph % len(g["taiko"])]
            for t, v, s_ in _steps(pat, b, step, 0.0, bar_len):
                _place(L["perc"], inst_taiko(np.random.default_rng([seed, 6, b, s_])), t, lev["taiko"] * v, loop)
        if g.get("pulse") and not pre_drop(b):
            pat = g["pulse"][ph % len(g["pulse"])]
            for t, v, s_ in _steps(pat, b, step, 0.0, bar_len):
                _place(L["perc"], inst_kick(np.random.default_rng([seed, 7, b]), 0.5, soft=True), t, lev["pulse"] * v, loop)
        # chords
        cdeg = prog[(b // chord_bars) % len(prog)]
        if b % chord_bars == 0 and pad_on:
            cm = chord_midis(key, scale, cdeg, 3, seventh=(g["pad"] in ("keys", "glass", "strings")))
            dur = chord_bars * bar_len + (0.25 if g["pad"] in ("strings", "glass", "dark") else 0.0)
            if g["pad"] == "keys":
                for k, m in enumerate(cm):
                    _place(L["pad"], inst_keys(G.midi_hz(m), min(dur * 0.9, 2.2), rng), b * bar_len + k * 0.012 + 0.003 * rng.random(), lev["pad"] * 0.5, loop)
            else:
                pdur = min(dur, total - b * bar_len)
                y = inst_pad(cm, pdur, rng, g["pad"], lp=g["lp"] * (0.6 if pre_drop(b) else 1.0))
                _place(L["pad"], y, b * bar_len, lev["pad"] * 0.55 / (1.0 + 0.5 * (g["pad"] == "chord")), loop)
        # bass
        bm = bass_midi(key, scale, cdeg)
        if bass_on and g.get("bass"):
            bp = g["bass"][ph % len(g["bass"])]
            hits = _steps(bp, b, step, 0.0, bar_len)
            for k, (t, v, s_) in enumerate(hits):
                nxt = hits[k + 1][0] if k + 1 < len(hits) else (b + 1) * bar_len
                dur_n = max(0.08, min(nxt - t - 0.01, 1.8 if g["bass_kind"] in ("drone",) else 0.5 if genre in ("techno", "house") else 1.2))
                if g["bass_kind"] == "808":
                    y = inst_808(G.midi_hz(bm), min(dur_n + 0.15, 1.4), G.midi_hz(bm) * 2 if s_ % 3 == 0 else None)
                elif g["bass_kind"] == "drone":
                    y = inst_sub(G.midi_hz(bm), bar_len * (chord_bars)) if b % chord_bars == 0 else np.zeros(1)
                else:
                    y = inst_sub(G.midi_hz(bm), dur_n)
                _place(L["bass"], y, t, lev["bass"] * v, loop)
        # arp / plucks
        if arp_on and g.get("arp") and lev.get("arp", 0) > 0:
            ap = g["arp"][ph % len(g["arp"])]
            notes = chord_midis(key, scale, cdeg, 4)
            seq = [notes[0], notes[1], notes[2], notes[1] + 12 if len(notes) > 1 else notes[0] + 12]
            ai = 0
            for t, v, s_ in _steps(ap, b, step + 0.0, sw, bar_len):
                m = seq[ai % len(seq)]; ai += 1
                if genre == "cinematic":
                    y = inst_pluck(G.midi_hz(m + 12), 0.5, 0.7)
                elif genre == "ambient":
                    y = inst_bell(G.midi_hz(m + 12), rng)
                elif genre in ("lofi",):
                    y = inst_keys(G.midi_hz(m), 0.6, rng)
                else:
                    y = inst_pluck(G.midi_hz(m), 0.22)
                _place(L["arp"], y, t, lev["arp"] * v * (0.7 + 0.3 * rng.random()), loop)
        # fill on the bar before the drop / last bar
        if drop_bar is not None and b == drop_bar - 1:
            nb = _n(bar_len / 2)
            _place(L["fx"], inst_riser(np.random.default_rng([seed, 9]), bar_len * 0.5), b * bar_len + bar_len / 2, 0.55, loop)
            for k in range(8):
                _place(L["fx"], snare_v[k % 3], b * bar_len + bar_len / 2 + k * (bar_len / 16) + (bar_len / 16) * 4 * 0 + 0.0, 0.25 + 0.5 * k / 8, loop)
        if drop_bar is not None and b == drop_bar:
            _place(L["fx"], inst_crash(np.random.default_rng([seed, 10])), b * bar_len, 0.6, loop)
            _place(L["fx"], inst_kick(np.random.default_rng([seed, 11]), 0.8, soft=False) * 1.0, b * bar_len, 1.0, loop)
    # ending
    if end == "hit":
        t = bars * bar_len
        cm = chord_midis(key, scale, prog[0], 3)
        stab = inst_pad(cm, 1.6, rng, "chord", lp=2600)
        _place(L["pad"], stab, t, 0.55)
        _place(L["fx"], inst_crash(np.random.default_rng([seed, 12]), 1.8), t, 0.5)
        _place(L["kick"], inst_kick(np.random.default_rng([seed, 13]), 0.8), t, 1.0)
        _place(L["bass"], inst_sub(G.midi_hz(bass_midi(key, scale, prog[0])), 1.8), t, 0.9)
        kick_t.append(t)
    # sidechain pump on everything except drums
    side = g["side"]
    if side and kick_t:
        regs = [(t, t + 0.02, float(side) * (0.8 + 0.4 * intensity)) for t in kick_t]
        gc = A.gain_curve(n, sr, regs, attack=0.004, release=0.16, lookahead=0.0, ctrl=1000)
        for k in ("bass", "pad", "arp"):
            L[k] *= gc
    # per-stem tone shaping, summed with a gentle stereo spread
    def hp(x, f): return A.biquad(x, "hp", f, 0.7071, sr=sr)
    stems = []
    stems.append(("kick", L["kick"], 0.0))
    stems.append(("clap", L["clap"], 0.15))
    stems.append(("hat", hp(L["hat"], 6000.0 * 0.0 + 4000), -0.3))
    stems.append(("perc", L["perc"], 0.0))
    stems.append(("bass", L["bass"], 0.0))
    stems.append(("pad", G.filt(L["pad"], "lp", g["lp"] * 2.0, 0.7), 0.0))
    stems.append(("arp", G.filt(L["arp"], "lp", min(g["lp"] * 2.5, 8000), 0.7), 0.25))
    stems.append(("fx", L["fx"], 0.0))
    out = np.zeros((n, 2))
    mixg = dict(kick=0.62, clap=1.2, hat=1.5, perc=0.8, bass=0.5, pad=1.7, arp=1.5, fx=1.0)    # stem balance: keeps music ~70-88 % below 400 Hz
    for name, x, pan in stems:
        if not np.any(x):
            continue
        x = x * mixg[name]
        if name in ("pad", "arp", "hat") and not loop:
            st = G.widen(x, 0.8 if name == "pad" else 0.5, np.random.default_rng([seed, 20]), 13.0 if name == "pad" else 9.0)
        else:
            st = G.pan2(x, pan)
        out += st
    # reverb send on pad/arp/clap (wet only); in loop mode the reverb overhang wraps to the start so the loop seam is clean
    send = (L["arp"] * 0.5 + L["clap"] * 0.35 + L["pad"] * 0.25)
    wet = G.reverb(send, 0.9 if genre in ("cinematic", "ambient") else 0.5, -9.0, 0.6, 0.012, 7)
    out += wet[:n] * 0.6
    if loop and len(wet) > n:
        over = wet[n:] * 0.6
        out[: len(over)] += over[: n]
    if genre == "lofi":                                                    # warmth: tape lowpass + vinyl crackle
        out = np.stack([G.filt(out[:, c], "lp", 6200, 0.7) for c in range(2)], axis=1)
        cr = inst_crackle(n, np.random.default_rng([seed, 30]), 9.0)
        out += G.pan2(cr * 0.012, 0.0)
    if g["lp"] and genre in ("cinematic", "ambient"):
        out = np.stack([G.filt(out[:, c], "lp", 9000, 0.7) for c in range(2)], axis=1)
    # drop in 'pre-drop' breakdown: gently lower the whole bus
    if drop_bar is not None and drop_bar > 0:
        env = np.ones(n)
        env[: int(drop_bar * bar_len * SR)] = 0.8
        out *= env[:, None]
    if end == "fade":
        f0 = max(0.0, bars * bar_len - bar_len * 0.9)
        t = np.arange(n) / SR
        out *= np.clip(1.0 - (t - f0) / (bar_len * 0.9 + tail), 0.0, 1.0)[:, None] ** 1.3
    out = A.biquad(out, "hp", 28.0, 0.7071, sr=sr)
    pk = np.max(np.abs(out)) + 1e-9
    out = out / pk * 0.89
    info = dict(genre=genre, bpm=float(bpm), key=key, scale=scale, bars=int(bars), bar_len=bar_len, beat=beat, seed=int(seed), arc=arc, drop_bar=drop_bar,
                end=end, progression=prog, swing=sw, duration=n / SR,
                beats=[round(k * beat, 5) for k in range(int(bars * beats_per_bar) + 1)],
                downbeats=[round(k * bar_len, 5) for k in range(int(bars) + 1)], kicks=[round(t, 5) for t in kick_t])
    return out.astype(np.float32), info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--genre", default="pop-pluck")
    ap.add_argument("--bpm", type=float, default=108)
    ap.add_argument("--key", default="C")
    ap.add_argument("--scale", default="minor-pentatonic")
    ap.add_argument("--bars", type=int, default=8)
    ap.add_argument("--duration", type=float, help="seconds: sets --bars = ceil(duration / bar_len) (end=fade)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--arc", default="flat", choices=["flat", "build"])
    ap.add_argument("--drop-bar", type=int)
    ap.add_argument("--end", default="fade", choices=["fade", "hit", "none", "loop"])
    ap.add_argument("--out")
    ap.add_argument("--png", action="store_true")
    a = ap.parse_args()
    if a.list:
        for k, v in GENRES.items():
            print(f"{k:<10} swing {v['swing']:.2f}  bass {v['bass_kind']:<6} pad {v['pad']:<8} sidechain {v['side']} dB")
        return 0
    bars = a.bars
    if a.duration:
        bars = int(math.ceil(a.duration / (240.0 / a.bpm)))
    audio, info = make_music(a.genre, a.bpm, a.key, a.scale, bars, a.seed, arc=a.arc, drop_bar=a.drop_bar, end=a.end)
    if not a.out:
        ap.error("--out required")
    A.write_wav(a.out, audio, SR)
    L = A.loudness(audio)
    print(json.dumps({k: info[k] for k in ("genre", "bpm", "key", "scale", "bars", "bar_len", "duration", "progression")}, indent=1))
    print(f"LUFS {L['lufs']:.1f}  TP {A.true_peak_db(audio):.1f} dBTP  below400 {100 * A.band_shares(audio)['below400']:.0f} %  above2k {100 * A.band_shares(audio)['above2k']:.1f} %")
    if a.png:
        import analyze_sfx as AN
        AN.sheet([a.out], os.path.splitext(a.out)[0] + ".png", 1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
