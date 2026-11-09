#!/usr/bin/env python3
"""palettes.py - sound palettes (DATA) and the default layer stacks per event type.

A palette makes the SOUND match the look: key, scale, brightness, room size, which recipe plays for which event, which extra layers
are added. sync_cues.py reads a palette by name (--palette) or from dna.json -> sound.palette[0].

Layer spec L(...):
  r      recipe name in sfxgen.RECIPES
  g      gain in dB relative to the event's level
  at     'anchor' (default: the layer's anchor lands on the event anchor)
         'lead'   (anchor lands `off_f` frames BEFORE the event anchor; negative off_f)
         'after'  (anchor lands `off_f` frames AFTER the event anchor)
  off_f  frames (at the video fps) for lead/after
  p      recipe params overriding the defaults (variant, length, direction ...). A p['intensity'] is a MULTIPLIER on the event intensity
         (so dynamics always follow the scene); same for palette params[recipe]['intensity']
  min_i  only when event intensity >= min_i
  role   'hit' (never ducked), 'sus' (sustained: ducked under voice and faded before the next big hit), 'tex' (texture, ducked lightly)
  dur    True -> pass the event's dur to the recipe (whoosh, riser, reverse, whip, swipe...)
  tail   True -> the sound has a long tail that may be faded early before the next big hit
"""
import copy


def L(r, g=0.0, at="anchor", off_f=0, p=None, min_i=0.0, role="hit", dur=False, tail=False, max_i=1.01):
    return dict(r=r, g=g, at=at, off_f=off_f, p=p or {}, min_i=min_i, max_i=max_i, role=role, dur=dur, tail=tail)


# ----------------------------------------------------------------------------- default stacks: what plays for every event type
DEFAULT_STACKS = {
    "impact": [L("impact", 0, tail=True), L("boom", -9, p=dict(intensity=0.55, length=1.3), min_i=0.75, tail=True, role="sus")],
    "hit-soft": [L("hit-soft", 0), L("tick", -13, p=dict(variant=1))],
    "slam": [L("slam", 0, tail=True), L("whip", -9, at="lead", off_f=-3, p=dict(dur=0.12), role="sus")],
    "whoosh": [L("whoosh", 0, dur=True, role="sus"), L("swipe", -9, dur=True, p=dict(brightness=0.8), min_i=0.0, role="sus")],
    "whip": [L("whip", 0, dur=True, role="sus")],
    "swipe": [L("swipe", 0, dur=True, role="sus")],
    "pop": [L("pop", 0), L("tick", -13, p=dict(variant=2))],
    "appear": [L("appear", 0)],
    "disappear": [L("disappear", 0)],
    "click": [L("click", 0)],
    "tick": [L("tick", 0)],
    "type": [L("key", 0)],                 # special-cased: one key per step, see sync_cues.type_times()
    "riser": [L("riser", 0, dur=True, role="sus"), L("reverse", -10, dur=True, p=dict(variant=0), role="sus", min_i=0.5)],
    "reverse": [L("reverse", 0, dur=True, role="sus")],
    "glitch": [L("glitch", 0)],
    "zap": [L("zap", 0)],
    "shimmer": [L("shimmer", 0, tail=True, role="sus")],
    "chime": [L("chime", 0, tail=True, role="sus")],
    "success": [L("success", 0, tail=True, role="sus"), L("shimmer", -7, at="after", off_f=3, tail=True, role="sus")],
    "error": [L("error", 0)],
    "reveal": [L("reveal", 0, tail=True), L("shimmer", -10, at="after", off_f=1, tail=True, role="sus", min_i=0.6)],
    "drop": [L("bass-drop", 0, tail=True), L("impact", -3, tail=True, p=dict(length=0.8))],
    "boom": [L("boom", 0, tail=True)],
    "bass-drop": [L("bass-drop", 0, tail=True)],
    "stinger": [L("stinger", 0, tail=True)],
    "scene-cut": [L("whip", -5, at="lead", off_f=-3, p=dict(dur=0.18), role="sus"), L("hit-soft", -2), L("tick", -14, p=dict(variant=1))],
    "loop-point": [L("reverse", -14, dur=True, p=dict(variant=1, dur=0.6), role="sus")],
}
# every other recipe name is accepted as an event type and plays as a single layer (stamp, paper-rip, paper-slap, tape, camera-shutter,
# heartbeat, glass-ding, drone, dial-tick, blip, blip-up, blip-down, blip-double, ...)
TYPE_ALIASES = {"hit": "impact", "thud": "hit-soft", "cut": "scene-cut", "transition": "scene-cut", "typing": "type", "keystroke": "type",
                "build": "riser", "build-up": "riser", "sparkle": "shimmer", "ding": "glass-ding", "notification": "chime", "complete": "success",
                "fail": "error", "warning": "error", "text-in": "pop", "word": "pop", "count": "tick", "dial": "dial-tick", "shutter": "camera-shutter",
                "loop": "loop-point", "sweep": "whoosh", "swoosh": "whoosh", "bass": "bass-drop", "logo": "stinger", "end": "boom"}

# ----------------------------------------------------------------------------- palettes
PALETTES = {
    "default": dict(
        drop=[], max_above2k=0.07,
        desc="Neutral: balanced, medium room. Use only when the DNA gives no sound palette.",
        key="C", scale="minor-pentatonic", bpm=(96, 116), brightness=0.5, room=1.0, music="pop-pluck",
        swap={}, params={}, add={}, tonal={}),
    "neon-mono": dict(
        desc="One-hue neon on black: deep sub, long dark tails, tonal blips, sweeping risers. Matches v01/v07 (sub 70+ %).",
        key="A", scale="minor", bpm=(96, 124), brightness=0.42, room=1.35, music="cinematic",
        swap={"pop": "blip", "tick": "blip", "appear": "blip-up", "disappear": "blip-down"},
        params={"blip": dict(variant=1), "riser": dict(variant=2), "whoosh": dict(direction="in"), "click": dict(variant=0), "impact": dict(brightness=0.4)},
        add={"impact": [L("bass-drop", -7, p=dict(intensity=0.45, length=1.1), min_i=0.6, tail=True, role="sus")]},
        tonal={"tick": "walk", "pop": "walk", "appear": "walk"}),
    "glass-dark": dict(
        desc="Black + glossy glass icons: glass dings and 6-11 kHz air shimmers over soft sub pulses. Matches v05 (the only reference with real air band).",
        key="F#", scale="major-pentatonic", bpm=(88, 108), brightness=0.68, room=1.5, music="ambient",
        swap={"pop": "glass-ding", "tick": "glass-ding", "appear": "shimmer", "click": "click", "chime": "glass-ding", "impact": "hit-soft"}, max_above2k=0.12,
        params={"click": dict(variant=2), "glass-ding": dict(brightness=0.7), "hit-soft": dict(intensity=0.7)},
        add={"impact": [L("boom", -8, p=dict(intensity=0.4, length=1.4), tail=True, role="sus")],
             "pop": [L("hit-soft", -9, p=dict(intensity=0.35))], "tick": [L("hit-soft", -14, p=dict(intensity=0.3))],
             "whoosh": [L("shimmer", -12, at="after", off_f=0, tail=True, role="sus", min_i=0.5)]},
        tonal={"pop": "walk", "tick": "walk"}),
    "halftone-collage": dict(
        desc="Poster collage: paper slaps, stamps, bass hits on every layer arrival. Matches v03 (10 onsets/s, sub 65 %).",
        key="D", scale="minor-pentatonic", bpm=(92, 110), brightness=0.52, room=0.8, music="boom-bap",
        swap={"pop": "paper-slap", "appear": "paper-slap", "click": "stamp", "tick": "tape", "whoosh": "whoosh", "impact": "impact"},
        params={"paper-slap": dict(intensity=0.7), "stamp": dict(intensity=0.7)},
        add={"impact": [L("paper-slap", -6, p=dict(intensity=0.9))], "pop": [L("bass-drop", -12, p=dict(intensity=0.3, length=0.5), role="sus")],
             "scene-cut": [L("paper-rip", -9, at="lead", off_f=-4, p=dict(dur=0.2), role="sus")]},
        tonal={}),
    "clay-mono": dict(
        desc="Cream paper + black clay 3D objects: soft thuds, wooden ticks, matte whooshes, restrained. Matches v10 (whoosh + soft impact + 2-3 ticks per scene).",
        key="C", scale="major-pentatonic", bpm=(78, 98), brightness=0.38, room=0.6, music="lofi",
        swap={"impact": "hit-soft", "pop": "tick", "appear": "tick", "click": "tick", "chime": "dial-tick"}, drop=["boom", "bass-drop"],
        params={"tick": dict(variant=1), "hit-soft": dict(intensity=0.85), "whoosh": dict(brightness=0.35)},
        add={"hit-soft": [L("stamp", -9, p=dict(intensity=0.4))]},
        tonal={}),
    "editorial": dict(
        desc="Grid-paper explainer: marimba blips, count-up dial ticks, pad under, sparkle chime on stars. Matches v08 (mid-heavy, 5.8 onsets/s).",
        key="G", scale="major-pentatonic", bpm=(100, 116), brightness=0.55, room=0.9, music="pop-pluck",
        swap={"pop": "blip", "tick": "dial-tick", "appear": "blip-up", "chime": "chime", "impact": "hit-soft"},
        params={"blip": dict(variant=2), "hit-soft": dict(intensity=0.8)},
        add={"impact": [L("stamp", -8, p=dict(intensity=0.5))], "reveal": [L("chime", -8, tail=True, role="sus", at="after", off_f=2)]},
        tonal={"pop": "walk", "appear": "walk"}),
    "product-film": dict(
        desc="UI as hero: tactile clicks, soft swipes, light chime on success. Sparse; no big impacts. Matches v06 advice (it shipped silent).",
        key="F", scale="major", bpm=(88, 108), brightness=0.5, room=0.7, music="ambient",
        swap={"impact": "hit-soft", "slam": "hit-soft", "pop": "click", "appear": "click", "tick": "tick", "whoosh": "swipe"}, drop=["boom", "bass-drop", "whip"],
        params={"click": dict(variant=0), "hit-soft": dict(intensity=0.55), "swipe": dict(brightness=0.5)},
        add={}, tonal={}),
    "radial-burst": dict(
        desc="Single node + rays + words: one tonal tick per word walking up the scale + soft sub tap; rising sweep for the extension; low thud at the end. Matches v07.",
        key="D", scale="minor-pentatonic", bpm=(116, 140), brightness=0.5, room=1.1, music="techno",
        swap={"pop": "blip", "tick": "blip", "appear": "blip", "type": "blip", "impact": "boom"},
        params={"blip": dict(variant=0), "riser": dict(variant=2)},
        add={"pop": [L("hit-soft", -8, p=dict(intensity=0.4))], "tick": [L("hit-soft", -10, p=dict(intensity=0.35))]},
        tonal={"pop": "walk", "tick": "walk", "appear": "walk", "type": "walk"}),
    "torn-paper": dict(
        desc="Torn-paper typography: rips, slaps, tape, stamps, a bass thump per word, snare-roll risers. Matches v11 (5 onsets/s, 11 % silence).",
        key="A", scale="blues", bpm=(88, 106), brightness=0.56, room=0.75, music="boom-bap",
        swap={"pop": "paper-slap", "appear": "tape", "whoosh": "paper-rip", "click": "stamp", "glitch": "paper-rip", "tick": "tape", "swipe": "paper-rip"},
        params={"riser": dict(variant=3), "stamp": dict(intensity=0.75)},
        add={"pop": [L("bass-drop", -11, p=dict(intensity=0.35, length=0.45), role="sus")],
             "impact": [L("paper-slap", -5, p=dict(intensity=0.9)), L("stamp", -7)]},
        tonal={}),
    "live-3d": dict(
        desc="Live footage + 3D objects: mechanical wheel clicks, soft panning whooshes, one shutter, gentle sub. Matches v02 (3.4 onsets/s, 20 % silence).",
        key="C", scale="minor-pentatonic", bpm=(80, 100), brightness=0.5, room=1.0, music="ambient",
        swap={"impact": "hit-soft", "pop": "click", "tick": "click", "appear": "pop"},
        params={"click": dict(variant=1), "whoosh": dict(direction="lr", brightness=0.55), "hit-soft": dict(intensity=0.7)},
        add={"whoosh": [L("hit-soft", -14, at="after", off_f=0, p=dict(intensity=0.3), min_i=0.8)]},
        tonal={}),
}

# dna.json sound.palette[] may contain free words; map them to a palette name
PALETTE_HINTS = {
    "neon": "neon-mono", "mono": "neon-mono", "cyber": "neon-mono", "glass": "glass-dark", "icons": "glass-dark", "halftone": "halftone-collage",
    "collage": "halftone-collage", "poster": "halftone-collage", "clay": "clay-mono", "cream": "clay-mono", "editorial": "editorial",
    "explainer": "editorial", "grid": "editorial", "product": "product-film", "ui": "product-film", "saas": "product-film", "radial": "radial-burst",
    "burst": "radial-burst", "typographic": "radial-burst", "torn": "torn-paper", "paper": "torn-paper", "tape": "torn-paper", "live": "live-3d",
    "3d": "live-3d", "footage": "live-3d",
}


def _fill(p):
    p.setdefault("drop", []); p.setdefault("max_above2k", 0.08); p.setdefault("tonal", {}); p.setdefault("add", {})
    p.setdefault("swap", {}); p.setdefault("params", {})
    return p


def get_palette(name_or_list):
    """name | list of words -> (name, palette dict deep copy)."""
    n, p = _get_palette(name_or_list)
    return n, _fill(p)


def _get_palette(name_or_list):
    words = [name_or_list] if isinstance(name_or_list, str) else list(name_or_list or [])
    for w in words:
        w = str(w).lower()
        if w in PALETTES:
            return w, copy.deepcopy(PALETTES[w])
    for w in words:
        for k, v in PALETTE_HINTS.items():
            if k in str(w).lower():
                return v, copy.deepcopy(PALETTES[v])
    return "default", copy.deepcopy(PALETTES["default"])


if __name__ == "__main__":
    for k, v in PALETTES.items():
        print(f"{k:<18} key {v['key']:<3}{v['scale']:<18} bpm {v['bpm']}  bright {v['brightness']}  room {v['room']}  music {v['music']}\n   {v['desc']}")
