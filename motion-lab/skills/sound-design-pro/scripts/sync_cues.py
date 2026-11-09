#!/usr/bin/env python3
"""sync_cues.py - turn a scene's events.json into a LAYERED, frame-locked sound design + mastered mix.

  python3 sync_cues.py out/events.json --out audio/ --palette neon-mono --bpm 108 --key A --scale minor --music-gen
  python3 sync_cues.py out/events.json --out audio/ --dna dna.json --music bed.mp3 --voice vo.wav --profile social
  python3 sync_cues.py out/events.json --out audio/ --palette editorial --no-music --variants 3

Outputs (in --out):  cues.json (per event: ordered layers with source, gain, start, anchor)   mix.wav (stereo 48 kHz, mastered)
                     sound-report.md / sound-report.json (alignment, loudness, spectral balance, warnings, 5 riskiest timestamps)
                     [--stems] sfx.wav music.wav voice.wav (pre-master)    [--variants N] mix_v2.wav cues_v2.json ... for human A/B

What it does for every event (the timing rules live in reference/timing-rules.md):
  * ANCHOR = the instant the listener hears "the hit". It is placed on the frame boundary of the event (round(t*fps)/fps) + --lag-ms
    (default +6 ms: the polished references measure +7..+19 ms, never early). Hits: the transient. Whoosh/swipe/whip: t + peak_frac*dur
    (peak at 35-60 % of the motion). Risers/reverses END on t+dur. Typing: one key per step on its own frame.
  * every event becomes a STACK (palette -> stack_for): sub + transient + body + tail ..., not one file. Lead layers (pre-whoosh 3 frames
    early) and anticipation (reverse swell before a hero hit) are added by rule.
  * variety: seed and variant rotate per type, pitch +-1 st (non-tonal), gain +-1 dB, tonal walk through the key.
  * priority: voice > hits > music. Voice ducks music and sustained SFX 8 dB (30 ms / 250 ms); big hits duck music 3.5 dB for 150 ms;
    hero hits get a 120 ms dip of music/sustained layers just before; long tails are faded before the next big hit.
  * master: social -14 LUFS / TP -1.0 dBTP, conservative -16 LUFS / TP -4.0 dBTP, measure -> gain -> limiter loop, verified on the written file.
"""
import argparse
import copy
import json
import math
import os
import shutil
import sys
import time
import zlib

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audiolib as A  # noqa: E402
import palettes as PL  # noqa: E402
import sfxgen as G  # noqa: E402
from audiolib import SR  # noqa: E402

PROFILES = {"social": dict(lufs=-14.0, tp=-1.0), "conservative": dict(lufs=-16.0, tp=-4.0)}
TONAL = {"blip", "blip-up", "blip-down", "blip-double", "dial-tick", "chime", "success", "glass-ding", "shimmer", "error", "stinger", "reveal",
         "drone", "riser", "reverse", "heartbeat"}
NO_VARIANT = {"typing", "key", "dial-tick", "heartbeat", "camera-shutter", "drone"}
VARIANT_N = {"click": 4, "tick": 3, "riser": 4, "reverse": 3, "blip": 4, "key": 3, "glitch": 3, "impact": 3, "hit-soft": 3, "pop": 3, "whoosh": 3,
             "stamp": 3, "paper-slap": 3, "paper-rip": 3, "shimmer": 2, "success": 2, "chime": 2, "swipe": 2, "boom": 2, "slam": 2, "bass-drop": 2}
GENRE_FOR_MUSIC = {"pop-pluck": "pop-pluck", "cinematic": "cinematic", "ambient": "ambient", "boom-bap": "boom-bap", "lofi": "lofi", "techno": "techno", "house": "house",
                   "trap": "trap"}
LIB_CATEGORY = {"impact": "impact", "slam": "impact", "boom": "impact", "bass-drop": "impact", "drop": "impact", "reveal": "impact", "hit-soft": "impact",
                "whoosh": "whoosh", "whip": "whoosh", "swipe": "whoosh", "scene-cut": "whoosh", "pop": "pop", "appear": "pop", "click": "click", "tick": "tick",
                "riser": "riser", "glitch": "glitch", "zap": "glitch", "chime": "ding", "success": "ding", "glass-ding": "ding"}
LIB_KIND = {"riser": "end", "whoosh": "peak"}
COUNT_NAMES = {"count", "count-up", "countup", "counter", "dial"}


# ============================================================================= small helpers
def frames(t, fps):
    return int(math.floor(t * fps + 0.5 + 1e-9))


def place(buf, x, start):
    """add x into buf at sample `start` (may be negative: the head is cut; may overrun: the tail is cut). Returns samples actually clipped at the head."""
    n = len(buf)
    cut = 0
    if start < 0:
        cut = -start
        if cut >= len(x):
            return cut
        x = x[cut:]
        start = 0
    if start >= n:
        return cut
    m = min(len(x), n - start)
    buf[start:start + m] += x[:m]
    return cut


def pan_data(x, p):
    """constant-power pan of the highs only; <150 Hz stays centred (bass mono rule)."""
    if abs(p) < 1e-3:
        return x
    low = np.stack([A.biquad(x[:, c].astype(np.float64), "lp", 150.0, 0.7071) for c in range(2)], axis=1)
    hi = x - low
    a = (float(np.clip(p, -1, 1)) + 1) * math.pi / 4
    return (low + np.stack([hi[:, 0] * math.cos(a), hi[:, 1] * math.sin(a)], axis=1) * math.sqrt(2)).astype(np.float32)


def fade_tail(x, start_idx, length_idx):
    """cosine fade to zero beginning at start_idx over length_idx samples (in place copy)."""
    y = x.copy()
    s = max(0, int(start_idx)); m = int(max(1, length_idx))
    if s >= len(y):
        return y
    e = min(len(y), s + m)
    y[s:e] *= (np.cos(np.linspace(0, math.pi / 2, e - s)) ** 2)[:, None]
    y[e:] = 0
    return y


def seed_of(base, typ, k):
    return (int(base) * 7919 + zlib.crc32(typ.encode()) % 100003 * 31 + k * 104729) & 0x7FFFFFFF


def load_dna_sound(path):
    d = json.load(open(path))
    return d.get("sound", {}) if isinstance(d, dict) else {}


# ============================================================================= event -> layer plan
class Layer:
    __slots__ = ("ev_i", "etype", "r", "kw", "anchor_t", "gain_db", "role", "tail", "rise", "src", "data", "start", "snd", "lib", "pan", "cut", "faded", "note")

    def __init__(self, **k):
        for s in self.__slots__:
            setattr(self, s, k.get(s))


class Planner:
    """Expands events into layers. Holds the per-type rotation state so that no sample/seed repeats in a row."""

    def __init__(self, palette, fps, args, seed):
        self.pal = palette
        self.fps = fps
        self.a = args
        self.seed = seed
        self.count = {}
        self.last_variant = {}
        self.walk = {"deg": None, "t": -9.0}
        self.rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 99])

    # -- stack selection ---------------------------------------------------------------------------------
    def stack_for(self, typ, intensity):
        pal = self.pal
        base = copy.deepcopy(PL.DEFAULT_STACKS.get(typ) or [PL.L(typ, 0.0)])
        sw = pal.get("swap", {}).get(typ)
        if sw:
            for l in base:
                if l["r"] == typ:
                    l["r"] = sw
        for l in base:                                                    # swapped recipe may differ from layer recipe: apply swap per recipe too
            s2 = pal.get("swap", {}).get(l["r"]) if l["r"] != typ else None
            if s2 and l["r"] in ("pop", "tick", "appear", "click", "disappear") and l["r"] != typ:
                l["r"] = s2
        for l in copy.deepcopy(pal.get("add", {}).get(typ, [])):
            base.append(l)
        out = []
        for l in base:
            if l["r"] in pal.get("drop", []):
                continue
            if intensity < l["min_i"] or intensity > l.get("max_i", 1.01):
                continue
            if l["r"] not in G.RECIPES:
                continue
            out.append(l)
        return out

    def next_variant(self, r, base_params):
        n = VARIANT_N.get(r, 1)
        c = self.count.get(r, 0)
        if "variant" in base_params:
            return int(base_params["variant"])
        if r in NO_VARIANT or n <= 1:
            return 0
        v = (c + int(self.rng.integers(0, n))) % n
        if self.last_variant.get(r) == v:
            v = (v + 1) % n
        self.last_variant[r] = v
        return v

    def degree(self, ev, t):
        if "degree" in ev:
            return int(ev["degree"])
        w = self.walk
        if w["deg"] is None or t - w["t"] > 0.9:
            w["deg"] = int(self.rng.choice([0, 2, 4]))
        else:
            step = int(self.rng.choice([1, 1, 2, -1, 2, -2, 0]))
            w["deg"] = int(np.clip(w["deg"] + step, 0, 9))
            if w["deg"] == 0 and self.rng.random() < 0.5:
                w["deg"] = 1
        w["t"] = t
        return w["deg"]

    # -- main --------------------------------------------------------------------------------------------
    def layers_for(self, i, ev, anchor_t, hero, prev_anchor):
        a, pal, fps = self.a, self.pal, self.fps
        raw = str(ev.get("type", "")).lower()
        typ = "count" if raw in COUNT_NAMES else PL.TYPE_ALIASES.get(raw, raw)
        typ = A.event_type(dict(type=typ))
        inten = float(np.clip(ev.get("intensity", 0.7), 0.0, 1.0))
        out = []
        if typ == "type":
            return self._typing(i, ev, anchor_t, inten)
        if typ == "count":
            return self._count(i, ev, anchor_t, inten)
        stack = self.stack_for(typ, inten)
        if not stack and typ not in G.RECIPES:
            return None
        for l in stack:
            out.append(self._make(i, ev, typ, l, anchor_t, inten))
        # anticipation: reverse swell that ENDS on a hero hit when the lead-in is free
        if hero and a.anticipation and typ in A.BIG_TYPES and "reverse" not in pal.get("drop", []):
            gap = anchor_t - prev_anchor
            if gap >= 0.45:
                d = float(np.clip(gap * 0.8, 0.35, 0.7))
                l = PL.L("reverse", -12, p=dict(variant=0, dur=d), role="sus", dur=True)
                lay = self._make(i, ev, "reverse", l, anchor_t, inten)
                lay.rise = True; lay.note = "auto-anticipation (reverse swell ends on the hero hit)"
                lay.kw["dur"] = d
                out.append(lay)
        return out

    def _make(self, i, ev, typ, l, anchor_t, inten):
        a, pal, fps = self.a, self.pal, self.fps
        r = l["r"]
        params = dict(pal.get("params", {}).get(r, {}))
        params.update(l.get("p", {}))
        k = self.count.get(r, 0)
        self.count[r] = k + 1
        kw = dict(key=a.key, scale=a.scale, brightness=pal.get("brightness", 0.5), room=pal.get("room", 1.0))
        mul = float(params.pop("intensity", 1.0))
        kw["intensity"] = float(np.clip(float(ev.get("intensity", 0.7)) * mul, 0.05, 1.0))
        for kk in ("variant", "direction", "length", "brightness", "dur", "peak", "degree", "value", "key", "scale", "room", "pitch", "count", "bpm", "cps"):
            if kk in params:
                kw[kk] = params.pop(kk)
        for kk in ("direction", "brightness", "variant", "degree", "value", "length", "pitch", "key", "scale", "room"):
            if kk in ev and r == (ev.get("recipe") or r):
                kw[kk] = ev[kk]
        if ev.get("dir") and "direction" not in kw:
            kw["direction"] = ev["dir"]
        dur = A.event_dur(ev)
        if l.get("dur") and dur > 0 and "dur" not in kw:
            kw["dur"] = dur
        if r in ("whoosh", "swipe", "whip") and "peak" not in kw:
            kw["peak"] = A.event_peak_frac(ev) if A.event_type(ev) == r or A.event_type(ev) in ("whoosh", "swipe", "whip") else None
            if kw["peak"] is None:
                kw.pop("peak")
        v = self.next_variant(r, kw)
        if r not in NO_VARIANT:
            kw["variant"] = v
        kw["seed"] = int(ev["seed"]) if "seed" in ev else seed_of(self.seed, r, k)
        jit = self.rng.uniform(-1.0, 1.0) * a.pitch_jitter
        pitch = float(ev.get("pitch", 0.0)) + (0.0 if r in TONAL else jit)
        if r in TONAL and ev.get("pitch"):
            kw["pitch"] = float(ev["pitch"])
        elif "pitch" not in kw:
            kw["pitch"] = pitch
        if r in ("blip", "blip-up", "blip-down", "blip-double", "glass-ding") and pal.get("tonal", {}).get(typ) == "walk" and "degree" not in kw:
            kw["degree"] = self.degree(ev, float(ev["t"]))
        if r == "dial-tick" and "value" not in kw:
            kw["value"] = float(ev.get("value", self.rng.random()))
        gain = float(l["g"]) + float(ev.get("gain", 0.0)) + float(self.rng.uniform(-1.0, 1.0)) * a.gain_jitter
        at = anchor_t
        if l["at"] == "lead":
            at = anchor_t + l["off_f"] / self.fps
        elif l["at"] == "after":
            at = anchor_t + l["off_f"] / self.fps
        role = l["role"]
        return Layer(ev_i=i, etype=typ, r=r, kw=kw, anchor_t=at, gain_db=gain, role=role, tail=l["tail"], rise=(r in ("riser", "reverse")),
                     src="synth", pan=float(ev.get("pan", 0.0)), note="")

    def _typing(self, i, ev, t0, inten):
        a, fps = self.a, self.fps
        rng = np.random.default_rng([int(self.seed) & 0xFFFFFFFF, i, 5])
        times = ev.get("times")
        if times is None:
            dur = A.event_dur(ev) or 1.2
            cps = float(ev.get("cps", 11.0))
            n = int(ev.get("n") or ev.get("chars") or max(1, round(dur * cps)))
            t = float(ev["t"]); times = []
            for _ in range(n):
                times.append(t)
                t += (dur / max(n, 1)) * float(np.clip(rng.normal(1.0, 0.25), 0.55, 1.7))
                if rng.random() < 0.05:
                    t += 0.1 + 0.15 * rng.random()
            scale = dur / max(times[-1] - times[0] + dur / max(n, 1), 1e-6)
            times = [times[0] + (x - times[0]) * min(1.0, scale) for x in times]
        out = []
        for k, tk in enumerate(times):
            ta = A.frame_snap(float(tk), fps, a.snap) + a.lag_ms / 1000.0
            v = 1 if (k % 7 == 6) else 0
            if ev.get("enter") and k == len(times) - 1:
                v = 2
            kw = dict(variant=v, seed=seed_of(self.seed, "key", self.count.get("key", 0)), brightness=self.pal.get("brightness", 0.5), room=self.pal.get("room", 1.0),
                      pitch=float(rng.uniform(-1.0, 1.0)) * a.pitch_jitter, intensity=inten)
            self.count["key"] = self.count.get("key", 0) + 1
            out.append(Layer(ev_i=i, etype="type", r="key", kw=kw, anchor_t=ta, gain_db=float(rng.uniform(-2.5, 0.0)) + float(ev.get("gain", 0.0)), role="tex", tail=False,
                             rise=False, src="synth", pan=float(ev.get("pan", 0.0)), note=f"key {k + 1}/{len(times)}"))
        return out

    def _count(self, i, ev, t0, inten):
        a, fps = self.a, self.fps
        dur = A.event_dur(ev) or 1.0
        n = int(ev.get("steps") or ev.get("n") or 10)
        v0, v1 = float(ev.get("from", 0.0)), float(ev.get("to", 1.0))
        times = ev.get("times") or [float(ev["t"]) + dur * (k / max(n - 1, 1)) ** 0.8 for k in range(n)]
        recipe = self.pal.get("swap", {}).get("count") or "dial-tick"
        out = []
        for k, tk in enumerate(times):
            ta = A.frame_snap(float(tk), fps, a.snap) + a.lag_ms / 1000.0
            val = v0 + (v1 - v0) * (k / max(len(times) - 1, 1))
            kw = dict(value=val, key=a.key, scale=a.scale, seed=seed_of(self.seed, "dial", k), intensity=inten, brightness=self.pal.get("brightness", 0.5))
            out.append(Layer(ev_i=i, etype="count", r=recipe, kw=kw, anchor_t=ta, gain_db=-1.0 * (1 - k / max(len(times) - 1, 1)) + float(ev.get("gain", 0.0)),
                             role="tex", tail=False, rise=False, src="synth", pan=float(ev.get("pan", 0.0)), note=f"step {k + 1}/{len(times)} value {val:.2f}"))
        return out


# ============================================================================= optional library layer
class Library:
    """Optional extra layer source: a folder with manifest.json (old toolkit format). Only bundled files with a known licence are used; credits are collected."""

    def __init__(self, folder, seed):
        self.dir = folder
        m = json.load(open(os.path.join(folder, "manifest.json")))
        self.items = {}
        for e in m.get("bundled", []):
            if e.get("bundled", True) and os.path.exists(os.path.join(folder, e["file"])):
                self.items.setdefault(e["category"], []).append(e)
        self.rng = np.random.default_rng([int(seed) & 0xFFFFFFFF, 1234])
        self.last = {}
        self.used = {}
        self.cache = {}

    def pick(self, typ):
        cat = LIB_CATEGORY.get(typ)
        if not cat or cat not in self.items:
            return None
        pool = [e for e in self.items[cat] if e["file"] != self.last.get(cat) and e.get("duration_s", 1.0) <= (5.0 if cat == "riser" else 2.5)] or self.items[cat]
        e = pool[int(self.rng.integers(0, len(pool)))]
        self.last[cat] = e["file"]
        self.used[e["file"]] = e
        return e

    def load(self, e, kind):
        key = (e["file"], kind)
        if key in self.cache:
            return self.cache[key]
        x = A.read_audio(os.path.join(self.dir, e["file"]), SR)
        pk = np.max(np.abs(x)) + 1e-9
        i0 = int(np.argmax(A.envelope(x, SR, 2.0) > 10 ** (-50 / 20) * pk)) if kind != "end" else 0
        x = x[max(0, i0 - int(0.002 * SR)):]
        x = x / (np.max(np.abs(x)) + 1e-9) * A.undb(-6.0)
        x = np.stack([A.biquad(x[:, c].astype(np.float64), "hp", 35.0) for c in range(2)], axis=1).astype(np.float32)
        anchor = A.sound_anchor(x, SR, kind)
        self.cache[key] = (x, anchor)
        return x, anchor


# ============================================================================= grid / music helpers
def fit_bpm(anchors, weights, t0, lo, hi, sub=2):
    """BPM in [lo, hi] (0.5 steps) that puts most weight on the 8th (sub=2) / 16th (sub=4) grid anchored at t0."""
    best = (1e9, (lo + hi) / 2)
    for bpm in np.arange(lo, hi + 1e-6, 0.5):
        step = 60.0 / bpm / sub
        d = np.abs(((np.asarray(anchors) - t0) / step + 0.5) % 1.0 - 0.5) * step
        cost = float(np.sum(np.asarray(weights) * np.minimum(d, 0.06)))
        if cost < best[0] - 1e-9:
            best = (cost, float(bpm))
    return best[1], best[0]


def grid_report(anchors, bpm, t0, sub=2):
    step = 60.0 / bpm / sub
    d = (((np.asarray(anchors) - t0) / step + 0.5) % 1.0 - 0.5) * step * 1000.0
    return d


# ============================================================================= risk scoring
def risk_list(events_info, layers, bus_hits_total, duration, voice_regs):
    rows = []
    anchors = sorted(e["anchor_t"] for e in events_info)
    for e in events_info:
        ta = e["anchor_t"]
        score, why = 0.0, []
        typ = e["type"]
        if e["hero"]:
            score += 4.0; why.append("hero hit: the one moment everyone judges")
        elif typ in A.BIG_TYPES:
            score += 2.5; why.append("big hit")
        if typ in ("riser", "reverse"):
            score += 2.0; why.append("end-anchored build: must END on the hit, a 40 ms error is audible")
        if typ in ("whoosh", "whip", "swipe"):
            score += 1.2; why.append("sweep: peak placed by rule at %.0f %% of the motion, check against the eased velocity peak" % (100 * A.event_peak_frac(e["ev"])))
        if typ in ("type", "count"):
            score += 1.0 + 0.04 * e["n_layers"]; why.append(f"{e['n_layers']} individually placed steps: check rhythm vs on-screen reveal")
        near = [x for x in anchors if x != ta and abs(x - ta) < 0.09]
        if near:
            score += 1.5; why.append("another event within 90 ms: layers can smear or mask each other")
        if e.get("faded"):
            score += 1.0; why.append("a long tail was faded to make room for the next hit")
        if e.get("head_cut"):
            score += 1.5; why.append("lead layer cut at t=0 (event too close to the start)")
        if any(a <= ta <= b for a, b in voice_regs):
            score += 1.5; why.append("overlaps speech: check intelligibility")
        if e["loc_snr_db"] is not None and e["loc_snr_db"] < 3.0:
            score += 1.5; why.append(f"only {e['loc_snr_db']:.1f} dB above the surrounding mix: may be inaudible")
        if abs(e["snap_ms"]) > 12:
            score += 0.6; why.append(f"frame snap moved it {e['snap_ms']:+.0f} ms")
        if e["err_ms"] is not None and abs(e["err_ms"]) > 1000.0 / 30 * 0.5:
            score += 2.0; why.append(f"measured offset {e['err_ms']:+.1f} ms")
        score += 0.4 * e["intensity"]
        rows.append((score, ta, e, why))
    rows.sort(key=lambda r: -r[0])
    chosen = []
    for sc, ta, e, why in rows:
        if all(abs(ta - c[1]) >= 0.8 for c in chosen):
            chosen.append((sc, ta, e, why))
        if len(chosen) == 5:
            break
    return [dict(t=round(ta, 3), frame=e["frame"], type=e["type"], label=e["label"], score=round(sc, 2), why=why) for sc, ta, e, why in chosen]


# ============================================================================= main build
def build(events, video, args, variant_k=0):
    fps = float(args.fps or video.get("fps") or 30)
    duration = float(args.duration or video.get("duration") or (max([e["t"] for e in events] + [0]) + 1.5))
    seed = int(args.seed) + 1000 * variant_k
    n = int(round(duration * SR))
    name, pal = PL.get_palette(args.palette or args.dna_palette or "default")
    if args.key is None:
        args.key = pal["key"]
    if args.scale is None:
        args.scale = pal["scale"]
    if args.brightness is not None:
        pal["brightness"] = args.brightness
    warnings = []
    lag = args.lag_ms / 1000.0
    pl = Planner(pal, fps, args, seed)

    # ---- order + normalise events
    evs = []
    for i, e in enumerate(events):
        e = dict(e)
        if "t" not in e or "type" not in e:
            warnings.append(f"event {i} has no t/type, skipped")
            continue
        if e["t"] < 0 or e["t"] > duration + 0.02:
            warnings.append(f"event {i} ({e['type']} @ {e['t']}) is outside 0..{duration:.2f} s, skipped")
            continue
        evs.append(e)
    evs.sort(key=lambda e: e["t"])
    info = []
    for i, e in enumerate(evs):
        rawt = str(e["type"]).lower()
        typ = "count" if rawt in COUNT_NAMES else A.event_type(dict(type=PL.TYPE_ALIASES.get(rawt, rawt)))
        e2 = dict(e); e2["type"] = typ
        at = A.event_anchor_time(e2, fps, lag=lag, snap=args.snap)
        hero = bool(e.get("hero")) or (typ in A.BIG_TYPES and float(e.get("intensity", 0.7)) >= 0.85)
        info.append(dict(i=i, ev=e2, type=typ, t=float(e["t"]), anchor_t=at, frame=frames(float(e["t"]), fps), snap_ms=(A.frame_snap(float(e["t"]), fps, args.snap) - float(e["t"])) * 1000,
                         hero=hero, intensity=float(e.get("intensity", 0.7)), label=e.get("label", ""), layers=[], n_layers=0, faded=False, head_cut=False, err_ms=None, loc_snr_db=None))
    hero_t = [x["anchor_t"] for x in info if x["hero"]]
    big_t = sorted(x["anchor_t"] for x in info if x["type"] in A.BIG_TYPES)

    # ---- music (decided first: its bpm/grid is reported against the events)
    music = None
    music_info = {}
    hit_x = [x for x in info if x["type"] in A.HIT_TYPES or x["type"] in ("pop", "click", "tick")]
    anchor_hits = [x["anchor_t"] for x in hit_x]
    if not args.no_music and (args.music or args.music_gen is not None):
        genre = args.music_gen if isinstance(args.music_gen, str) and args.music_gen != "auto" else GENRE_FOR_MUSIC.get(pal.get("music", "pop-pluck"), "pop-pluck")
        if args.music:
            mus = A.read_audio(args.music, SR)
            off = float(args.music_offset or 0.0)
            gridinfo = None
            if args.bpm or args.music_detect:
                gridinfo = A.detect_grid(mus, SR, args.bpm)
                music_info["grid_detected"] = {k: round(float(v), 4) for k, v in gridinfo.items()}
                if gridinfo["confidence"] < 1.8:
                    warnings.append(f"music beat grid confidence {gridinfo['confidence']:.1f} < 1.8: kick grid unclear, do not trust automatic alignment (check by eye on a waveform)")
            if args.music_align == "hero" and hero_t and gridinfo is not None:
                T = hero_t[0]
                beat = gridinfo["beat_s"]
                # music-time of the nearest beat to (T - off); we shift so that beat lands exactly on T
                tm = T - off
                k = round((tm - gridinfo["offset_s"]) / beat)
                off = off + (tm - (gridinfo["offset_s"] + k * beat))
                music_info["aligned_to_hero_s"] = round(T, 4)
            music_info.update(source=args.music, offset_s=round(off, 4), licence=args.music_license or "NOT CONFIRMED", credit=args.music_source or "")
            mbuf = np.zeros((n, 2), dtype=np.float64)
            m = mus.astype(np.float64)
            start = int(round(off * SR))
            place(mbuf, m, start)
            if start + len(m) < n - SR * 0.05:
                warnings.append(f"music ends at {(start + len(m)) / SR:.1f} s but the video is {duration:.1f} s: loop or extend it")
            if start > 0:
                mbuf[start:start + int(0.03 * SR)] *= np.linspace(0, 1, min(int(0.03 * SR), n - start))[:, None]
            music = mbuf
        else:
            pr = pal["bpm"]
            bpm = args.bpm
            t0 = hero_t[0] if hero_t else (anchor_hits[0] if anchor_hits else 0.0)
            if bpm is None or str(bpm) == "auto":
                bpm = (pr[0] + pr[1]) / 2
                if anchor_hits and not args.bpm_fixed:
                    ws = [3.0 if x["hero"] else 1.0 for x in hit_x]
                    bpm, cost = fit_bpm(anchor_hits, ws, t0, pr[0], pr[1], 2)
                    music_info["bpm_fit_cost_ms"] = round(cost * 1000, 2)
            bpm = float(bpm)
            import musicgen as MG
            bar_len = 240.0 / bpm
            if hero_t and args.music_align == "hero":
                T = hero_t[0]
                k = max(0, int(round(T / bar_len)))
                shift = T - k * bar_len
            else:
                k, shift = 0, float(args.music_offset or 0.0)
            drop_bar = k if (hero_t and args.music_align == "hero" and k >= 1 and args.music_drop != "off") else None
            bars_needed = int(math.ceil((duration - shift) / bar_len - 1e-6)) + (1 if shift < 0 else 0)
            end = "hit" if abs(shift + bars_needed * bar_len - duration) < 0.02 * duration else "fade"
            mus, mi = MG.make_music(genre, bpm, args.key, args.scale, bars_needed, seed + 5, arc=args.music_arc, drop_bar=drop_bar, end=end)
            mbuf = np.zeros((n, 2), dtype=np.float64)
            place(mbuf, mus.astype(np.float64), int(round(shift * SR)))
            music = mbuf
            music_info.update(source=f"musicgen:{genre}", bpm=bpm, bar_len=round(bar_len, 4), shift_s=round(shift, 4), drop_bar=drop_bar, end=end, bars=bars_needed,
                              licence="procedural scratch bed (no third-party material)", credit="", note="scratch bed: swap for licensed/user music before delivery")
            gd = grid_report(anchor_hits, bpm, (hero_t[0] if hero_t else 0.0), 2) if anchor_hits else []
            if len(gd):
                music_info["hits_off_8th_grid_ms"] = dict(median_abs=round(float(np.median(np.abs(gd))), 1), worst=round(float(np.max(np.abs(gd))), 1))
        music_info["bpm"] = music_info.get("bpm") or (args.bpm and float(args.bpm))

    # ---- library
    lib = Library(args.use_library, seed) if args.use_library else None

    # ---- plan + render layers
    layers = []
    t_render = time.time()
    prev_anchor = -9.0
    for x in info:
        ev = x["ev"]
        lays = pl.layers_for(x["i"], ev, x["anchor_t"], x["hero"], prev_anchor)
        if lays is None:
            warnings.append(f"event {x['i']} type '{ev['type']}' has no recipe or alias: skipped (valid: {', '.join(sorted(G.RECIPES))}; aliases in palettes.TYPE_ALIASES)")
            continue
        if lib is not None and x["type"] in LIB_CATEGORY and x["type"] not in ("type", "count"):
            e = lib.pick(x["type"])
            if e:
                kind = LIB_KIND.get(LIB_CATEGORY[x["type"]], "transient")
                lays.append(Layer(ev_i=x["i"], etype=x["type"], r="lib:" + os.path.basename(e["file"]), kw=dict(file=e["file"], kind=kind), anchor_t=x["anchor_t"],
                                  gain_db=args.library_gain, role="tex", tail=False, rise=(kind == "end"), src="library", lib=e, pan=0.0, note=f"{e.get('license', '?')} / {e.get('source_url', '')}"))
        for l in lays:
            l.ev_i = x["i"]
            if l.src == "synth":
                snd = G.render(l.r, **{k: v for k, v in l.kw.items() if v is not None})
                data = snd.data.astype(np.float64)
                anchor = snd.anchor
                l.snd = snd
            else:
                xdat, anchor = lib.load(l.lib, l.kw["kind"])
                data = xdat.astype(np.float64)
            if abs(l.pan) > 1e-3:
                data = pan_data(data, l.pan).astype(np.float64)
            data = data * A.undb(l.gain_db)
            l.data = data
            l.start = int(round(l.anchor_t * SR)) - int(round(anchor * SR))
            x["layers"].append(l)
            layers.append(l)
        x["n_layers"] = len(x["layers"])
        prev_anchor = x["anchor_t"]
    render_s = time.time() - t_render

    # ---- smother rule + head cut accounting
    for l in layers:
        xi = info[l.ev_i]
        if (l.role in ("sus", "tex") or l.tail) and not l.rise:
            nxt = [b for b in big_t if b > l.anchor_t + 0.03]
            if nxt:
                tn = nxt[0]
                end_t = (l.start + len(l.data)) / SR
                if end_t > tn - 0.02:
                    fs = int(round((tn - 0.09) * SR)) - l.start
                    if fs > int(0.02 * SR) and not (l.etype in A.BIG_TYPES and abs(l.anchor_t - tn) < 1e-6 and l.role == "hit"):
                        l.data = fade_tail(l.data, fs, int(0.06 * SR))
                        l.faded = True
                        xi["faded"] = True
        if l.start < 0:
            l.cut = -l.start
            if l.cut > int(0.004 * SR) and l.anchor_t - l.start / SR * 0 > 0:
                xi["head_cut"] = True
                warnings.append(f"event {xi['i']} ({xi['type']} @ {xi['t']:.2f}s): layer '{l.r}' starts {-l.start / SR * 1000:.0f} ms before t=0 and is cut (move the event later or shorten the lead)")

    # ---- buses
    bus = {k: np.zeros((n, 2)) for k in ("hit", "sus", "tex", "rise")}
    for l in layers:
        place(bus[l.role if l.role in ("hit", "sus", "tex") else "tex"] if not l.rise else bus["rise"], l.data, l.start)

    voice = None
    voice_regs = []
    if args.voice:
        v = A.read_audio(args.voice, SR).astype(np.float64)
        vL = A.loudness(v)["lufs"]
        v = v * A.undb(-20.0 - vL)
        voice = np.zeros((n, 2)); place(voice, v, int(round(float(args.voice_offset) * SR)))
        voice_regs = A.voice_regions(voice, SR)

    # ---- priority / ducking
    sfx_db = args.sfx_db if args.sfx_db is not None else (-4.0 if voice is not None else 0.0)
    gv = lambda regs, d, atk=0.03, rel=0.25: A.gain_curve(n, SR, [(a, b, d) for a, b in regs], atk, rel)
    if voice_regs:
        g_s = gv(voice_regs, 8.0)
        g_t = gv(voice_regs, 5.0)
        bus["sus"] *= g_s[:, None]; bus["tex"] *= g_t[:, None]; bus["rise"] *= gv(voice_regs, 4.0)[:, None]
    dip = args.dip_ms / 1000.0
    if hero_t and dip > 0:
        regs = [(t - dip, t - 0.004, 9.0) for t in hero_t]
        g = A.gain_curve(n, SR, regs, 0.012, 0.18, lookahead=0.012)
        bus["sus"] *= g[:, None]; bus["tex"] *= g[:, None]
    if music is not None:
        mv = args.music_db if args.music_db is not None else (-28.0 if voice is not None else -22.0)
        mL = A.loudness(music)["lufs"]
        music = music * A.undb(mv - mL)
        regs_music = []
        if voice_regs:
            music *= gv(voice_regs, 8.0)[:, None]
        big = [(t, t + 0.15, 3.5) for t in big_t]
        if big:
            music *= A.gain_curve(n, SR, big, 0.008, 0.25, lookahead=0.008)[:, None]
        if hero_t and dip > 0:
            music *= A.gain_curve(n, SR, [(t - dip, t - 0.004, 10.0) for t in hero_t], 0.012, 0.18, lookahead=0.012)[:, None]
        music_fade = min(float(args.music_fade_out), duration * 0.4)
        if music_fade > 0 and music_info.get("end") != "hit":
            f = int(music_fade * SR)
            music[n - f:] *= (np.cos(np.linspace(0, math.pi / 2, f)) ** 2)[:, None]
    sfx = (bus["hit"] + bus["sus"] + bus["tex"] + bus["rise"]) * A.undb(sfx_db)
    if args.loop:
        pass
    sfx_hit_only = bus["hit"] * A.undb(sfx_db)
    mix_pre = sfx.copy()
    if music is not None:
        mix_pre += music
    if voice is not None:
        mix_pre += voice
    # end click guard
    fe = int(0.03 * SR)
    mix_pre[n - fe:] *= np.linspace(1, 0, fe)[:, None]

    # ---- alignment measurement: every event's own hit/tex layers summed ALONE (so neighbours and tails cannot mask it), onset nearest the anchor
    meas_types = A.HIT_TYPES | {"pop", "click", "tick", "appear", "glitch", "zap", "stamp", "paper-slap", "paper-rip", "tape", "camera-shutter", "chime", "success", "shimmer", "error", "type", "count", "disappear"}
    meas = [x for x in info if x["type"] in meas_types]
    errs = []
    for x in meas:
        own = [l for l in x["layers"] if l.role in ("hit", "tex") and not l.rise and abs(l.anchor_t - x["anchor_t"]) < 1e-6]
        if not own:
            errs.append(None); continue
        t0 = x["anchor_t"] - 0.12
        L = int(0.6 * SR)
        mini = np.zeros((L, 2))
        for l in own:
            place(mini, l.data, l.start - int(round(t0 * SR)))
        if x["type"] in ("type", "count"):                                   # many steps: measure the first step only
            first = min(own, key=lambda l: l.anchor_t); mini = np.zeros((L, 2)); t0 = first.anchor_t - 0.12
            place(mini, first.data, first.start - int(round(t0 * SR)))
            e = A.align_errors(mini, [first.anchor_t - t0], SR, window=(-0.045, 0.06))[0]
        else:
            e = A.align_errors(mini, [x["anchor_t"] - t0], SR, window=(-0.045, 0.06))[0]
        errs.append(e)
    for x, e in zip(meas, errs):
        x["err_ms"] = e
    for x in info:                                                           # local SNR of the event vs the rest of the mix (sfx-only part vs the bed)
        a0 = int(max(0, (x["anchor_t"] - 0.02) * SR)); a1 = int(min(n, (x["anchor_t"] + 0.12) * SR))
        s_rms = float(np.sqrt(np.mean(sfx[a0:a1] ** 2)) + 1e-9)
        bed = mix_pre[a0:a1] - sfx[a0:a1]
        b_rms = float(np.sqrt(np.mean(bed ** 2)) + 1e-9)
        x["loc_snr_db"] = None if b_rms < 1e-6 else float(20 * np.log10(s_rms / b_rms))

    return dict(info=info, layers=layers, evs=evs, n=n, duration=duration, fps=fps, mix_pre=mix_pre, sfx=sfx, music=music, voice=voice, music_info=music_info,
                warnings=warnings, pal=pal, pal_name=name, seed=seed, render_s=render_s, lib=lib, voice_regs=voice_regs, hero_t=hero_t, sfx_db=sfx_db,
                meas=meas, errs=errs, lag=lag)


# ============================================================================= mastering + checks
def master_mix(x, profile, max_limiting_db):
    prof = PROFILES[profile]
    L0 = A.loudness(x)["lufs"]
    pk0 = A.true_peak_db(x)
    notes = []
    target = prof["lufs"]
    if L0 < -100:
        return x.astype(np.float32), dict(lufs=L0, tp=-120.0, target=target, notes=["silent mix"], limiting_db=0.0)
    reduction = pk0 + (target - L0) - (prof["tp"] - 0.3)
    if reduction > max_limiting_db:
        newt = target - (reduction - max_limiting_db)
        notes.append(f"target {target:.1f} LUFS would need {reduction:.1f} dB of peak limiting (> {max_limiting_db:.0f}); relaxed to {newt:.1f} LUFS. "
                     "Cause: peaks far above the average (sparse SFX, no music bed). Add music / a sustained bed, or accept the quieter master.")
        target = newt
    y, mi = A.master(x, SR, target, prof["tp"])
    mi["notes"] = notes
    mi["target"] = target
    mi["limiting_db"] = round(max(0.0, reduction), 1)
    return y, mi


def balance_warnings(y, pal, voice_present):
    sh = A.band_shares(y, SR)
    w = []
    b4, sub, a2, air = sh["below400"], sh["sub"], sh["above2k"], sh["air"]
    if b4 < 0.60:
        w.append(f"THIN: only {100 * b4:.0f} % of the energy is below 400 Hz (references 65-90 %). Raise sub/boom layers, a bass music bed, or lower brightness.")
    if b4 > 0.94 and not voice_present:
        w.append(f"BOOMY: {100 * b4:.0f} % below 400 Hz. Phones will lose it; add saturation/harmonics (mid layers) or raise body/click.")
    if sub > 0.75:
        w.append(f"SUB-HEAVY: {100 * sub:.0f} % below 120 Hz (references 30-73 %). Small speakers reproduce none of it: add 150-400 Hz body or harmonics.")
    if sub < 0.25 and not voice_present:
        w.append(f"NO WEIGHT: sub 20-120 Hz is only {100 * sub:.0f} % (references 30-73 %). Add boom/bass-drop or a bass bed.")
    lim = pal.get("max_above2k", 0.08)
    if a2 > lim:
        w.append(f"BRIGHT/CHEAP: {100 * a2:.1f} % above 2 kHz (limit for this palette {100 * lim:.0f} %; references 2-7 %). Lower brightness, drop tick/click layers, or add low body.")
    if a2 < 0.012 and not voice_present:
        w.append(f"DULL: {100 * a2:.1f} % above 2 kHz (references 2-7 %). Raise crack/click layers a little or brightness +0.1.")
    if air > 0.07 and "glass" not in str(pal.get("desc", "")).lower():
        w.append(f"AIR BAND {100 * air:.1f} % (6-16 kHz): only the glass reference had that (6.8 %). Harsh on phones; lower shimmer/hat gain.")
    return w, sh


def write_outputs(R, args, out, k):
    sfx_name = "mix.wav" if k == 0 else f"mix_v{k + 1}.wav"
    cues_name = "cues.json" if k == 0 else f"cues_v{k + 1}.json"
    y, mi = master_mix(R["mix_pre"], args.profile, args.max_limiting_db)
    path = os.path.join(out, sfx_name)
    A.write_wav(path, y, SR, 16)
    # verify on the FINAL FILE (reads back the PCM16 we wrote, plus ffmpeg's independent meter)
    yr = A.read_audio(path, SR)
    mine = A.loudness(yr)
    tp = A.true_peak_db(yr)
    ff = A.ffmpeg_ebur128(path)
    prof = PROFILES[args.profile]
    ver = dict(file=sfx_name, lufs=round(mine["lufs"], 2), tp=round(tp, 2), lra=round(mine["lra"], 1), ffmpeg=ff, target_lufs=round(mi.get("target", prof["lufs"]), 1),
               tp_limit=prof["tp"], limiting_db=mi.get("limiting_db"), notes=mi.get("notes", []))
    w = list(R["warnings"])
    if tp > prof["tp"] + 0.05:
        w.append(f"TRUE PEAK {tp:.2f} dBTP is above the limit {prof['tp']} on the written file")
    if abs(mine["lufs"] - ver["target_lufs"]) > 0.5:
        w.append(f"loudness {mine['lufs']:.1f} LUFS differs from target {ver['target_lufs']:.1f} by > 0.5 LU")
    ver["notes"].append(f"measured twice: own BS.1770 {mine['lufs']:.2f} LUFS" + (f", ffmpeg {ff['lufs']:.1f} LUFS / peak {ff.get('tp', 0):.1f} dBFS" if ff else ""))
    bw, sh = balance_warnings(yr, R["pal"], R["voice"] is not None)
    w += bw
    sil = A.silence_ratio(yr, SR)
    ons = A.onsets(yr, SR, rise_db=8.0, floor_db=-60.0)
    dens = len(ons) / max(R["duration"], 1e-6)
    if dens > 12.0:
        w.append(f"BUSY: {dens:.1f} onsets/s (references 5-10 in busy videos). Cut ticks/typing layers or raise min intensity.")
    if sil > 0.35 and R["music"] is None:
        w.append(f"SPARSE: {100 * sil:.0f} % of the mix is silent. Intentional? (references: 10-20 % in sparse videos)")
    errs = [e for e in R["errs"] if e is not None]
    tol = 1000.0 / R["fps"]
    al = dict(n_measured=len(R["meas"]), n_detected=len(errs), lag_ms=R["lag"] * 1000.0, tolerance_ms=round(tol, 1))
    if errs:
        raw = np.array(errs)                                               # onset - planned anchor (planned anchor = frame boundary + lag)
        al.update(median_vs_plan_ms=round(float(np.median(raw)), 2), worst_vs_plan_ms=round(float(raw[np.argmax(np.abs(raw))]), 2),
                  within_1ms=int(np.sum(np.abs(raw) <= 1.0)), within_2ms=int(np.sum(np.abs(raw) <= 2.0)),
                  median_vs_frame_ms=round(float(np.median(raw)) + R["lag"] * 1000.0, 2))
    # anchor placement integrity: planned anchor sample vs measured on the layer itself (hit-class, synth)
    placed = []
    for l in R["layers"]:
        if l.src == "synth" and l.etype in A.HIT_TYPES and l.role == "hit" and l.start >= 0:
            kind = "transient"
            placed.append(((A.sound_anchor(l.data, SR, kind) + l.start / SR) - l.anchor_t) * 1000.0)
    if placed:
        al["layer_anchor_error_ms"] = dict(max_abs=round(float(np.max(np.abs(placed))), 3), n=len(placed))
    ver_rows = ver
    # top-5 risk
    risks = risk_list(R["info"], R["layers"], None, R["duration"], R["voice_regs"])
    # cues.json
    cues = dict(video=dict(fps=R["fps"], duration=R["duration"], sr=SR), settings=dict(palette=R["pal_name"], key=args.key, scale=args.scale, profile=args.profile, lag_ms=args.lag_ms,
                                                                                         snap=args.snap, seed=R["seed"], sfx_db=R["sfx_db"]), music=R["music_info"], events=[])
    for x in R["info"]:
        cues["events"].append(dict(i=x["i"], t=x["t"], frame=x["frame"], type=x["type"], label=x["label"], intensity=x["intensity"], hero=x["hero"], anchor_t=round(x["anchor_t"], 5),
                                   anchor_frame_offset_ms=round((x["anchor_t"] - x["t"]) * 1000, 2),
                                   layers=[dict(source=(l.r if l.src == "synth" else l.r), kind=l.src, role=l.role, gain_db=round(l.gain_db, 2), start_s=round(l.start / SR, 5),
                                                anchor_s=round(l.anchor_t, 5), dur_s=round(len(l.data) / SR, 3), params={kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in (l.kw or {}).items()},
                                                note=l.note, faded=bool(l.faded)) for l in x["layers"]],
                                   measured_offset_ms=None if x["err_ms"] is None else round(x["err_ms"], 2)))
    json.dump(cues, open(os.path.join(out, cues_name), "w"), indent=1)
    if args.stems and k == 0:
        A.write_wav(os.path.join(out, "sfx.wav"), R["sfx"], SR, 32, False)
        if R["music"] is not None:
            A.write_wav(os.path.join(out, "music.wav"), R["music"], SR, 32, False)
        if R["voice"] is not None:
            A.write_wav(os.path.join(out, "voice.wav"), R["voice"], SR, 32, False)
    return dict(variant=k + 1, seed=R["seed"], mix=sfx_name, cues=cues_name, loudness=ver_rows, balance=dict(shares={a: round(100 * b, 1) for a, b in sh.items() if a != "centroid_hz"},
                centroid_hz=round(sh["centroid_hz"])), silence_ratio=round(sil, 3), onset_density=round(dens, 2), alignment=al, risks=risks, warnings=w, n_events=len(R["info"]),
                n_layers=len(R["layers"]), music=R["music_info"], render_s=round(R["render_s"], 1)), cues


def md_report(rep, args, R_list):
    r = rep["variants"][0]
    L = r["loudness"]
    lines = [f"# Sound report ({os.path.basename(args.events)})", "",
             "> Nobody in this toolchain can listen. Everything below is measured (numbers, spectrograms) or rule-based. It is NOT a claim that the mix sounds good. "
             "Check the 5 timestamps at the end with headphones, and on a phone speaker.", "",
             f"- palette `{rep['palette']}`, key {rep['key']} {rep['scale']}, profile `{args.profile}`, fps {rep['fps']}, duration {rep['duration']:.2f} s, seed {rep['seed']}",
             f"- events {r['n_events']}, layers {r['n_layers']}, lag {args.lag_ms:+.0f} ms after the frame boundary",
             f"- music: {r['music'].get('source', 'none')}" + (f" (licence: {r['music'].get('licence')})" if r["music"] else ""), "",
             "## Loudness (measured on the written mix.wav)", "",
             f"- integrated {L['lufs']} LUFS (target {L['target_lufs']}), true peak {L['tp']} dBTP (limit {L['tp_limit']}), LRA {L['lra']} LU, peak limiting needed ~{L['limiting_db']} dB"] + [f"- {n}" for n in L["notes"]]
    if L.get("ffmpeg"):
        lines.append(f"- ffmpeg ebur128 cross-check: {L['ffmpeg']}")
    b = r["balance"]["shares"]
    lines += ["", "## Spectral balance (final mix)", "",
              f"| sub 20-120 | low 120-400 | mid 0.4-2k | high 2-6k | air 6-16k | below 400 | above 2k | centroid |", "|---|---|---|---|---|---|---|---|",
              f"| {b['sub']} % | {b['low']} % | {b['mid']} % | {b['high']} % | {b['air']} % | {b['below400']} % | {b['above2k']} % | {r['balance']['centroid_hz']} Hz |",
              "", "Targets from the 10 polished references: 65-90 % below 400 Hz, sub 30-73 %, 2-7 % above 2 kHz, -13..-15 LUFS.",
              f"silence {100 * r['silence_ratio']:.0f} %, onset density {r['onset_density']}/s", "", "## Alignment", ""]
    al = r["alignment"]
    if al.get("n_detected"):
        lines.append(f"- {al['n_detected']}/{al['n_measured']} events measured (each event's own layers rendered alone, onset nearest the anchor): median {al['median_vs_plan_ms']:+.2f} ms vs plan "
                     f"= {al['median_vs_frame_ms']:+.1f} ms after the frame boundary (lag {al['lag_ms']:+.0f} ms); worst {al['worst_vs_plan_ms']:+.2f} ms vs plan; "
                     f"{al['within_1ms']} within 1 ms, {al['within_2ms']} within 2 ms; tolerance +-{al['tolerance_ms']} ms (1 frame).")
    if al.get("layer_anchor_error_ms"):
        lines.append(f"- placement integrity: max anchor error of {al['layer_anchor_error_ms']['n']} placed hit layers = {al['layer_anchor_error_ms']['max_abs']} ms (sample rounding).")
    lines.append("- risers/reverses END on t+dur; whooshes peak at 35-60 % of dur; typing/count steps sit on their own frames (see cues.json).")
    lines += ["", "## Warnings", ""] + ([f"- {w}" for w in r["warnings"]] or ["- none from the automatic checks (that still proves nothing about taste)"])
    lines += ["", "## Check these 5 timestamps with headphones", ""]
    for k, x in enumerate(r["risks"]):
        lines.append(f"{k + 1}. **{x['t']:.2f} s** (frame {x['frame']}) `{x['type']}` {x['label']} - " + "; ".join(x["why"]))
    if len(rep["variants"]) > 1:
        lines += ["", "## Variants for A/B", ""]
        for v in rep["variants"]:
            lines.append(f"- variant {v['variant']}: `{v['mix']}` seed {v['seed']} ({v['loudness']['lufs']} LUFS, {v['balance']['shares']['below400']} % < 400 Hz)")
    if R_list and R_list[0]["lib"] is not None and R_list[0]["lib"].used:
        lines += ["", "## Library credits (optional layer source)", ""]
        for e in R_list[0]["lib"].used.values():
            lines.append(f"- {e['file']}: {e.get('attribution', e.get('source_url', ''))} ({e.get('license', 'licence unknown')})")
    if r["music"] and r["music"].get("licence", "").startswith("NOT"):
        lines += ["", "**MUSIC LICENCE NOT CONFIRMED.** Pass --music-source and --music-license, or do not publish."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("events", help="events.json from render.mjs --events (or a bare list)")
    ap.add_argument("--out", default="audio")
    ap.add_argument("--fps", type=float)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--palette", help="palette name or free word (see palettes.py); default: dna.json sound.palette[0]")
    ap.add_argument("--dna", help="dna.json: reads sound.{bpm,key,scale,palette[]}")
    ap.add_argument("--key")
    ap.add_argument("--scale")
    ap.add_argument("--bpm", default=None, help="number, or 'auto' (music-gen only: fit the grid to the hits inside the palette range)")
    ap.add_argument("--bpm-fixed", action="store_true", help="never fit the bpm to the events")
    ap.add_argument("--brightness", type=float, help="override palette brightness 0..1")
    ap.add_argument("--profile", default="social", choices=list(PROFILES))
    ap.add_argument("--max-limiting-db", type=float, default=7.0)
    ap.add_argument("--music", help="music file (licensed / user supplied: preferred)")
    ap.add_argument("--music-gen", nargs="?", const="auto", default=None, help="procedural scratch bed; optional genre (techno house boom-bap lofi trap pop-pluck cinematic ambient)")
    ap.add_argument("--music-offset", type=float, default=0.0, help="seconds: + starts the music later, - skips its head")
    ap.add_argument("--music-align", default="hero", choices=["hero", "none"], help="hero: shift the music grid so a beat (gen: a downbeat) lands on the first hero hit")
    ap.add_argument("--music-detect", action="store_true", help="detect the beat grid of --music even without --bpm")
    ap.add_argument("--music-drop", default="auto", choices=["auto", "off"])
    ap.add_argument("--music-arc", default="flat", choices=["flat", "build"])
    ap.add_argument("--music-db", type=float, help="pre-master loudness of the music bed (LUFS), default -22 (-28 with voice)")
    ap.add_argument("--music-fade-out", type=float, default=0.6)
    ap.add_argument("--music-source")
    ap.add_argument("--music-license")
    ap.add_argument("--no-music", action="store_true")
    ap.add_argument("--voice")
    ap.add_argument("--voice-offset", type=float, default=0.0)
    ap.add_argument("--sfx-db", type=float, help="gain of the whole SFX bus (default 0, -4 with voice)")
    ap.add_argument("--use-library", metavar="DIR", help="folder with manifest.json (old CC0 library) as an extra texture layer under the synthesized stacks")
    ap.add_argument("--library-gain", type=float, default=-9.0)
    ap.add_argument("--lag-ms", type=float, default=6.0, help="anchor lands this many ms AFTER the frame boundary (0..10)")
    ap.add_argument("--snap", default="round", choices=["round", "floor", "ceil"])
    ap.add_argument("--dip-ms", type=float, default=120.0, help="dip of music/sustained layers before hero hits (0 = off)")
    ap.add_argument("--no-anticipation", dest="anticipation", action="store_false")
    ap.add_argument("--pitch-jitter", type=float, default=1.0)
    ap.add_argument("--gain-jitter", type=float, default=1.0)
    ap.add_argument("--variants", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--stems", action="store_true")
    ap.add_argument("--loop", action="store_true")
    a = ap.parse_args(argv)
    a.events_path = a.events
    if a.bpm is not None and a.bpm != "auto":
        a.bpm = float(a.bpm)
    elif a.bpm == "auto":
        a.bpm = None
    a.dna_palette = None
    if a.dna:
        s = load_dna_sound(a.dna)
        a.dna_palette = s.get("palette")
        a.key = a.key or s.get("key")
        a.scale = a.scale or s.get("scale")
        if a.bpm is None and s.get("bpm") and not a.music_gen == "auto-x":
            a.bpm = float(s["bpm"]) if not isinstance(s["bpm"], (list, tuple)) else None
        if s.get("profile") in PROFILES and "--profile" not in (argv or sys.argv):
            a.profile = s["profile"]
    evs, video = A.load_events(a.events)
    a.events = a.events_path
    out = a.out
    os.makedirs(out, exist_ok=True)
    if not evs:
        print("ERROR: no events. A scene without EVENTS cannot get tight sound: register them with Lab.ev(t, type, opts), then render.mjs --events.", file=sys.stderr)
        return 2
    reps, Rs = [], []
    for k in range(max(1, a.variants)):
        R = build(evs, video, a, k)
        rep, cues = write_outputs(R, a, out, k)
        reps.append(rep); Rs.append(R)
    R0 = Rs[0]
    report = dict(events_file=a.events, palette=R0["pal_name"], key=a.key, scale=a.scale, fps=R0["fps"], duration=R0["duration"], seed=a.seed, variants=reps)
    json.dump(report, open(os.path.join(out, "sound-report.json"), "w"), indent=1)
    open(os.path.join(out, "sound-report.md"), "w").write(md_report(report, a, Rs))
    r = reps[0]
    print(f"mix: {os.path.join(out, r['mix'])}  {r['loudness']['lufs']} LUFS  TP {r['loudness']['tp']} dBTP  events {r['n_events']} layers {r['n_layers']}  render {r['render_s']} s")
    for w in r["warnings"]:
        print("WARNING:", w)
    print("5 timestamps to check:", ", ".join(f"{x['t']:.2f}s {x['type']}" for x in r["risks"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
