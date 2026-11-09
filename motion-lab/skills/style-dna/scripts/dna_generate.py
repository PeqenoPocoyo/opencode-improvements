#!/usr/bin/env python3
"""dna_generate.py - make, mutate, validate and ledger Style DNA (dna.json) so no two videos share a "soul".

A video's look is DATA. This tool produces that data, and refuses to let a new video be too close to the previous ones.

USAGE
  python3 dna_generate.py --list                                   # presets and what they are
  python3 dna_generate.py --candidates 3 --out-dir dnas/           # 3 DIVERGENT DNAs (motion-director step "3 concepts")
  python3 dna_generate.py --generate --seed 7 --out dna.json       # one fresh DNA, distinct from history
  python3 dna_generate.py --generate --mood "calm,nocturnal" --family neon-mono --dark --out dna.json
  python3 dna_generate.py --preset torn-paper-collage --mutate 3 --out dna.json   # a preset, re-hued and re-timed (never a copy)
  python3 dna_generate.py --check dna.json                         # schema + contrast + distance to the last 5 videos  (exit 1 = fail)
  python3 dna_generate.py --add dna.json --name my-video           # append to the variety ledger
  python3 dna_generate.py --distance a.json b.json                 # numeric distance 0..1

History file: <project>/.motion/style-history.json  ->  {"version":1,"entries":[{"name","date","dna":{...}|null,"fingerprint":{...}|null}]}
(qa-critique/fingerprint.py writes the "fingerprint" half of the same entries. Never delete this file.)
The generator may use randomness: it runs OUTSIDE the scene. The scene itself must stay deterministic.
"""
import argparse, copy, datetime, glob, json, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRESET_DIR = os.path.join(HERE, "..", "dna")
FONTS_JSON = os.path.join(HERE, "..", "..", "kinetic-typography", "fonts", "fonts.json")
SOUND_PALETTES = ["default", "neon-mono", "glass-dark", "halftone-collage", "clay-mono", "editorial", "product-film", "radial-burst", "torn-paper", "live-3d"]
VALID_EASE = {"linear", "inSine", "outSine", "inOutSine", "inQuad", "outQuad", "inOutQuad", "inCubic", "outCubic", "inOutCubic", "inQuart", "outQuart",
              "inOutQuart", "inQuint", "outQuint", "inOutQuint", "inExpo", "outExpo", "inOutExpo", "inCirc", "outCirc", "inOutCirc", "inBack", "outBack",
              "inOutBack", "inElastic", "outElastic", "inOutElastic", "inBounce", "outBounce", "inOutBounce"}
VALID_CURVES = {"snap", "punch", "whip", "glide", "settle", "drop"}

# ------------------------------------------------------------------------------------------------ OKLCH -> sRGB hex
def _lin2srgb(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

def _oklch_rgb(L, C, h):
    a = C * math.cos(math.radians(h)); b = C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)

def oklch(L, C, h):
    """-> '#rrggbb', reducing chroma until the colour is inside sRGB."""
    for _ in range(80):
        r, g, b = _oklch_rgb(L, C, h)
        if min(r, g, b) >= -0.0005 and max(r, g, b) <= 1.0005:
            break
        C *= 0.95
    return "#%02x%02x%02x" % tuple(int(round(_lin2srgb(v) * 255)) for v in (r, g, b))

def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def hex2oklch(hx):
    r, g, b = [(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for c in hex2rgb(hx)]
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360

def luminance(hx):
    r, g, b = [(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4) for c in hex2rgb(hx)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    if la < lb: la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)

def hue_dist(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d) / 180.0

# ------------------------------------------------------------------------------------------------ palette strategies
def palette(strategy, dark, hue, rng):
    """Return palette dict. strategy: mono | duotone | neutral-pop | tri-accent | analogous | complementary | paper-ink"""
    h = hue % 360
    if strategy == "mono":
        if dark:
            p = dict(bg=oklch(.14, .035, h), bg2=oklch(.32, .10, h), ink=oklch(.97, .025, h), ink2=oklch(.78, .06, h), accent=oklch(.86, .25, h), accent2=oklch(.94, .09, h + 18),
                     support=[oklch(.46, .13, h), oklch(.70, .18, h)])
        else:
            p = dict(bg=oklch(.96, .025, h), bg2=oklch(.90, .06, h), ink=oklch(.20, .04, h), ink2=oklch(.45, .05, h), accent=oklch(.58, .22, h), accent2=oklch(.74, .14, h + 15),
                     support=[oklch(.82, .08, h), oklch(.35, .12, h)])
    elif strategy == "duotone":
        h2 = (h + rng.choice([110, 140, 180, 210])) % 360
        if dark:
            p = dict(bg=oklch(.17, .05, h), bg2=oklch(.30, .09, h), ink=oklch(.95, .03, h2), ink2=oklch(.75, .06, h2), accent=oklch(.70, .22, h), accent2=oklch(.76, .20, h2), support=[oklch(.45, .12, h), oklch(.58, .14, h2)])
        else:
            p = dict(bg=oklch(.95, .03, 85), bg2=oklch(.88, .05, h2), ink=oklch(.24, .08, h), ink2=oklch(.48, .08, h), accent=oklch(.55, .22, h), accent2=oklch(.64, .22, h2), support=[oklch(.78, .10, h), oklch(.70, .14, h2)])
    elif strategy == "neutral-pop":
        warm = rng.choice([75, 85, 95, 245])
        if dark:
            p = dict(bg=oklch(.16, .008, warm), bg2=oklch(.24, .01, warm), ink=oklch(.95, .01, warm), ink2=oklch(.66, .01, warm), accent=oklch(.72, .21, h), accent2=oklch(.50, .01, warm), support=[oklch(.35, .01, warm), oklch(.58, .12, h)])
        else:
            p = dict(bg=oklch(.955, .014, warm), bg2=oklch(.90, .014, warm), ink=oklch(.19, .008, warm), ink2=oklch(.52, .008, warm), accent=oklch(.60, .22, h), accent2=oklch(.30, .01, warm), support=[oklch(.78, .01, warm), oklch(.68, .13, h)])
    elif strategy == "tri-accent":
        dh = rng.choice([100, 120, 140])
        if dark:
            p = dict(bg=oklch(.17, .015, 270), bg2=oklch(.25, .02, 270), ink=oklch(.96, .01, 270), ink2=oklch(.70, .02, 270), accent=oklch(.72, .20, h), accent2=oklch(.82, .20, h + dh), support=[oklch(.74, .19, h + 2 * dh), oklch(.45, .02, 270)])
        else:
            p = dict(bg=oklch(.965, .008, 100), bg2=oklch(.92, .01, 100), ink=oklch(.18, .01, 280), ink2=oklch(.55, .01, 280), accent=oklch(.52, .24, h), accent2=oklch(.72, .19, h + dh), support=[oklch(.84, .22, h + 2 * dh), oklch(.80, .01, 100)])
    elif strategy == "analogous":
        s = rng.choice([22, 30, 38])
        if dark:
            p = dict(bg=oklch(.16, .05, h), bg2=oklch(.28, .09, h + s), ink=oklch(.95, .03, h + s), ink2=oklch(.74, .07, h + s), accent=oklch(.74, .21, h + s), accent2=oklch(.80, .19, h + 2 * s), support=[oklch(.55, .15, h), oklch(.65, .17, h - s)])
        else:
            p = dict(bg=oklch(.95, .035, h), bg2=oklch(.88, .07, h + s), ink=oklch(.22, .06, h), ink2=oklch(.46, .08, h), accent=oklch(.56, .21, h + s), accent2=oklch(.66, .20, h + 2 * s), support=[oklch(.78, .10, h), oklch(.60, .15, h - s)])
    elif strategy == "complementary":
        if dark:
            p = dict(bg=oklch(.15, .04, h), bg2=oklch(.26, .08, h), ink=oklch(.96, .015, h + 180), ink2=oklch(.74, .04, h + 180), accent=oklch(.78, .20, h + 180), accent2=oklch(.70, .22, h), support=[oklch(.42, .10, h), oklch(.60, .13, h + 180)])
        else:
            p = dict(bg=oklch(.955, .02, h + 180), bg2=oklch(.90, .04, h + 180), ink=oklch(.22, .05, h), ink2=oklch(.46, .06, h), accent=oklch(.56, .22, h), accent2=oklch(.68, .18, h + 180), support=[oklch(.80, .08, h + 180), oklch(.36, .10, h)])
    else:  # paper-ink
        p = dict(bg=oklch(.93, .025, 85), bg2=oklch(.86, .035, 80), ink=oklch(.18, .01, 60), ink2=oklch(.42, .02, 60), accent=oklch(.55, .22, h), accent2=oklch(.30, .02, 60), support=[oklch(.80, .03, 80), oklch(.64, .16, h + 150)])
    p["mode"] = strategy; p["dark"] = bool(dark); p["hue"] = round(h)
    return p

# ------------------------------------------------------------------------------------------------ building blocks
FAMILIES = {
    # family -> allowed palette strategies, display font choices, texture presets, motion personalities, transitions, camera, sound palette, extras
    "neon-mono": dict(strategies=["mono"], dark=True, hues=[140, 185, 20, 330, 60, 205], display=["Anton", "Bebas Neue", "Oswald", "Unbounded"], body=["Inter Tight", "Outfit"], mono=["JetBrains Mono", "Space Mono"], accent_font=None,
                      case="upper", textures=["neon"], motion=["calm-precise", "heavy-cinematic"], transitions=[["focusPull", "frameCarry", "dipToColor"], ["zoomThrough", "radialBlurSpin", "dipToColor"]], camera=["slow-push", "drift-parallax"], sound="neon-mono"),
    "live-3d": dict(strategies=["neutral-pop", "mono"], dark=False, hues=[250, 30, 160, 340], display=["Inter Tight", "Outfit"], body=["Inter Tight"], mono=["JetBrains Mono"], accent_font=None, case="lower",
                    textures=["footage"], motion=["fluid-liquid", "calm-precise"], transitions=[["objectCarry", "whipPan", "crossfade"]], camera=["static-shallow-dof"], sound="live-3d"),
    "halftone-poster": dict(strategies=["duotone"], dark=False, hues=[255, 20, 150, 330, 45], display=["Alfa Slab One", "Anton", "Black Ops One", "Archivo"], body=["Archivo", "Inter Tight"], mono=["Space Mono"], accent_font="Permanent Marker", case="upper",
                            textures=["halftone"], motion=["snappy-punchy", "jittery-handmade"], transitions=[["zoomThrough", "whiteFlash", "halftoneDissolve"], ["whiteFlash", "paperTear", "slidePush"]], camera=["push-through", "handheld"], sound="halftone-collage"),
    "glass-dark": dict(strategies=["mono", "complementary", "analogous"], dark=True, hues=[255, 195, 330, 20, 150], display=["Outfit", "Inter Tight", "Syne"], body=["Inter Tight", "Outfit"], mono=["JetBrains Mono"], accent_font=None, case="sentence",
                       textures=["glass"], motion=["fluid-liquid", "calm-precise"], transitions=[["glassRefract", "ringFormation", "crossfade"], ["blurSwap", "zoomThrough", "crossfade"]], camera=["slow-dolly-dof", "orbit-slow"], sound="glass-dark"),
    "editorial": dict(strategies=["tri-accent", "neutral-pop"], dark=False, hues=[285, 40, 130, 340, 220], display=["Inter Tight", "Bricolage Grotesque", "Archivo", "Outfit"], body=["Inter Tight"], mono=["JetBrains Mono"], accent_font="Instrument Serif", case="mixed",
                      textures=["grid-paper"], motion=["elastic-pop", "snappy-punchy"], transitions=[["sparkleSweep", "arcWipe", "crossfade"], ["scribbleWipe", "slidePush", "irisCircle"]], camera=["gentle-push"], sound="editorial"),
    "product-film": dict(strategies=["neutral-pop"], dark=False, hues=[25, 155, 255, 330], display=["Inter Tight", "Outfit", "Bricolage Grotesque"], body=["Inter Tight"], mono=["JetBrains Mono"], accent_font="Instrument Serif", case="sentence",
                         textures=["clean"], motion=["calm-precise", "fluid-liquid"], transitions=[["uiExpand", "objectCarry", "crossfade"]], camera=["ui-push"], sound="product-film"),
    "radial-burst": dict(strategies=["mono", "complementary"], dark=True, hues=[150, 190, 50, 320, 10], display=["Outfit", "Syne", "Unbounded"], body=["Outfit"], mono=["Space Mono"], accent_font=None, case="lower",
                         textures=["neon"], motion=["mechanical-steps", "snappy-punchy"], transitions=[["loopRing", "dipToColor"]], camera=["locked"], sound="radial-burst"),
    "clay-mono": dict(strategies=["neutral-pop"], dark=False, hues=[25, 250, 150, 340], display=["Inter Tight", "Archivo", "Bricolage Grotesque"], body=["Inter Tight"], mono=["JetBrains Mono"], accent_font="Instrument Serif", case="sentence",
                      textures=["clay"], motion=["heavy-cinematic", "calm-precise"], transitions=[["objectCarry", "slidePush", "dipToColor"]], camera=["slow-push"], sound="clay-mono"),
    "torn-paper": dict(strategies=["paper-ink", "duotone"], dark=False, hues=[25, 10, 200, 60, 150], display=["Alfa Slab One", "Anton", "Black Ops One", "Oswald"], body=["Archivo", "Oswald"], mono=["Space Mono"], accent_font="Permanent Marker", case="upper",
                       textures=["paper"], motion=["jittery-handmade", "snappy-punchy"], transitions=[["whiteFlash", "paperTear", "slidePush"]], camera=["handheld"], sound="torn-paper"),
    "terminal-brutal": dict(strategies=["neutral-pop", "mono"], dark=True, hues=[100, 55, 330, 20], display=["JetBrains Mono", "Space Mono", "Rubik Mono One"], body=["JetBrains Mono", "Space Mono"], mono=["JetBrains Mono"], accent_font=None, case="upper",
                            textures=["scan"], motion=["mechanical-steps", "snappy-punchy"], transitions=[["glitchSwap", "scanlineWipe", "vhsRewind"], ["pixelDissolve", "glitchSwap", "dipToColor"]], camera=["locked", "handheld"], sound="default"),
    "swiss-poster": dict(strategies=["neutral-pop", "complementary", "duotone"], dark=False, hues=[25, 255, 150, 340, 85], display=["Archivo", "Inter Tight", "Bricolage Grotesque", "Anton"], body=["Archivo", "Inter Tight"], mono=["Space Mono"], accent_font="Instrument Serif", case="upper",
                         textures=["print"], motion=["mechanical-steps", "heavy-cinematic"], transitions=[["slidePush", "barnDoors", "blinds"], ["wipeLinear", "irisCircle", "dipToColor"]], camera=["locked", "gentle-push"], sound="editorial"),
    "soft-3d-toy": dict(strategies=["analogous", "tri-accent", "duotone"], dark=False, hues=[340, 20, 160, 255, 90], display=["Fredoka", "Outfit", "Unbounded"], body=["Nunito", "Outfit"], mono=["Space Mono"], accent_font="Caveat", case="sentence",
                        textures=["soft"], motion=["elastic-pop", "fluid-liquid"], transitions=[["zoomThrough", "rippleDissolve", "irisCircle"]], camera=["orbit-slow", "gentle-push"], sound="clay-mono"),
}

TEXTURES = {
    "neon": dict(grain=.06, vignette=.5, halftone=0, paper=0, scan=.12, bloom=.85, dust=.35, chromatic=.12, lightleak=0),
    "footage": dict(grain=.05, vignette=.2, halftone=0, paper=0, scan=0, bloom=.15, dust=0, chromatic=.03, lightleak=0),
    "halftone": dict(grain=.12, vignette=.15, halftone=.9, paper=.2, scan=0, bloom=0, dust=.1, chromatic=0, lightleak=0),
    "glass": dict(grain=.04, vignette=.55, halftone=0, paper=0, scan=0, bloom=.7, dust=.2, chromatic=.2, lightleak=.1),
    "grid-paper": dict(grain=.03, vignette=.08, halftone=0, paper=.35, scan=0, bloom=.12, dust=0, chromatic=0, lightleak=0),
    "clean": dict(grain=.015, vignette=.06, halftone=0, paper=0, scan=0, bloom=.05, dust=0, chromatic=0, lightleak=0),
    "clay": dict(grain=.05, vignette=.45, halftone=0, paper=.25, scan=0, bloom=.05, dust=.08, chromatic=0, lightleak=0),
    "paper": dict(grain=.1, vignette=.2, halftone=.55, paper=.9, scan=0, bloom=0, dust=.25, chromatic=0, lightleak=.1),
    "scan": dict(grain=.09, vignette=.35, halftone=0, paper=0, scan=.6, bloom=.5, dust=0, chromatic=.25, lightleak=0),
    "print": dict(grain=.07, vignette=.04, halftone=.25, paper=.5, scan=0, bloom=0, dust=0, chromatic=0, lightleak=0),
    "soft": dict(grain=.03, vignette=.18, halftone=0, paper=0, scan=0, bloom=.25, dust=.05, chromatic=0, lightleak=.2),
}

MOTION = {
    "calm-precise": dict(ease=["outExpo", "inOutSine"], curves=["glide", "settle"], spring=dict(w=9, z=.85), stagger=.07, cutRate=.5, hitStyle="glow-pulse", hold=[.7, 1.6]),
    "snappy-punchy": dict(ease=["outQuart", "outBack"], curves=["punch", "snap"], spring=dict(w=16, z=.55), stagger=.035, cutRate=1.1, hitStyle="scale-punch+shake", hold=[.25, .7]),
    "elastic-pop": dict(ease=["outBack", "outElastic"], curves=["settle", "punch"], spring=dict(w=13, z=.4), stagger=.05, cutRate=.8, hitStyle="overshoot-pop", hold=[.4, 1.0]),
    "heavy-cinematic": dict(ease=["inOutCubic", "outQuint"], curves=["drop", "glide"], spring=dict(w=6, z=1.0), stagger=.09, cutRate=.35, hitStyle="slow-slam", hold=[1.0, 2.2]),
    "jittery-handmade": dict(ease=["outCubic", "steps"], curves=["snap"], spring=dict(w=14, z=.5), stagger=.045, cutRate=1.4, hitStyle="slap+flash", hold=[.2, .6]),
    "fluid-liquid": dict(ease=["inOutSine", "outCirc"], curves=["glide", "whip"], spring=dict(w=7, z=.9), stagger=.06, cutRate=.55, hitStyle="soft-ripple", hold=[.6, 1.5]),
    "mechanical-steps": dict(ease=["inOutQuart", "linear"], curves=["snap", "whip"], spring=dict(w=20, z=1.0), stagger=.03, cutRate=.9, hitStyle="tick-step", hold=[.3, .9]),
}

MOVES = {  # signature moves a family can draw from (each is a recipe idea a weak model can implement)
    "neon-mono": ["numerals bigger than the figure, glowing, half-covered by the subject", "vertical single-hue gradient with floor reflection", "dashed frame rotates to open the next scene", "word-by-word captions that scale in on the voice", "dust motes drifting through the light cone", "a lens-like focus pull between scenes"],
    "live-3d": ["glossy objects ride a parametric arc above the footage", "scroll-linked index with velocity curve and motion blur", "contact shadow + shallow DoF match the footage", "icon set swaps by sliding the next arc in"],
    "halftone-poster": ["camera pushes THROUGH a stack of cutout layers", "signs fly in with rotation overshoot, then settle", "white sticker border + hard shadow on every cutout", "last frame equals first frame (loop)", "duotone map on every layer"],
    "glass-dark": ["icons float in a ring at different depths, far ones blurred", "coloured rim light gradient on every glass plate", "text swaps with blur cross-fade", "ring forms, dissolves, reforms as a single hero"],
    "editorial": ["grotesk + serif-italic inside one sentence", "dashed selection box with corner handles around a label", "count-up numbers with soft glow", "4-point sparkle stars sweep in with a big arc", "bars rise while a line draws across"],
    "product-film": ["rebuilt UI as clean vectors with a choreographed cursor", "UI element expands into the next scene", "2D data points lift into a 3D grid", "camera pushes into the UI region that matters"],
    "radial-burst": ["one node, twelve rays, words fly along rays", "clockwise stagger 0.12 s", "one ray extends and carries the key word", "ends where it began (loop)"],
    "clay-mono": ["grey-to-black tone shift on the emphasized word", "soft contact shadows under every object", "pill labels stack with a soft shadow", "strikethrough draws across a word", "strong vignette on cream"],
    "torn-paper": ["window-blind shadows drift across the paper", "words on tape/label strips at slight angles", "hand-drawn scribble circle around the key word", "torn edge reveal and white flash cut", "stepped handheld jitter at 12 Hz"],
    "terminal-brutal": ["text types out with a block cursor", "scanline sweep wipes between beats", "RGB split on every hit", "monospace tables fill row by row", "error/ok status chips flip"],
    "swiss-poster": ["huge type cropped by the frame edge", "strict 12-column grid with one rotated element", "flat colour fields slide as wipes", "numerals as images"],
    "soft-3d-toy": ["rounded inflatable letters bounce in", "pastel studio floor with soft contact shadows", "objects squash and stretch on landing", "confetti baked from a seed on success"],
}
FORBID_COMMON = ["Math.random / Date.now / CSS transitions in scene code", "system fonts", "centered card on a purple-blue gradient", "the same easing on everything", "more than one new idea per beat", "text outside the 9:16 safe area"]

MOODS = {  # mood word -> hint on hue / dark / motion; used by --mood
    "calm": dict(motion=["calm-precise", "fluid-liquid"]), "nocturnal": dict(dark=True), "energetic": dict(motion=["snappy-punchy", "jittery-handmade"]), "playful": dict(motion=["elastic-pop"], family=["soft-3d-toy", "editorial"]),
    "luxury": dict(motion=["heavy-cinematic"], dark=True), "tech": dict(family=["terminal-brutal", "glass-dark", "product-film"]), "warm": dict(hues=[25, 45, 85]), "cold": dict(hues=[205, 230, 255]),
    "gritty": dict(family=["torn-paper", "halftone-poster"]), "clean": dict(family=["product-film", "swiss-poster", "clay-mono"]), "retro": dict(family=["halftone-poster", "terminal-brutal"]), "cinematic": dict(motion=["heavy-cinematic"], dark=True),
}

# ------------------------------------------------------------------------------------------------ fonts
def load_fonts():
    try:
        return {f["family"]: f for f in json.load(open(FONTS_JSON))["families"]}
    except Exception:
        return {}

def pick_type(fam, rng, fonts):
    d = rng.choice([x for x in fam["display"] if not fonts or x in fonts] or fam["display"])
    b = rng.choice([x for x in fam["body"] if not fonts or x in fonts] or fam["body"])
    m = rng.choice(fam["mono"])
    case = fam["case"]
    if d in ("Anton", "Bebas Neue", "Black Ops One", "Rubik Mono One") and case in ("lower", "sentence", "mixed"):
        case = "upper"  # these faces are caps faces
    track_d = {"upper": rng.choice([.0, .01, .03, .06]), "lower": rng.choice([-.04, -.03, -.02]), "sentence": rng.choice([-.03, -.02, -.01]), "mixed": rng.choice([-.03, -.02])}[case]
    scale = rng.choice([[1, 1.6, 2.6], [1, 1.5, 3.2], [1, 1.8, 2.4]])
    return dict(display=d, body=b, mono=m, accentSerif=fam["accent_font"], case=case, tracking=dict(display=track_d, body=0.0, label=rng.choice([.12, .18, .24])),
                weights=dict(display=400 if d in ("Anton", "Bebas Neue", "Alfa Slab One", "Black Ops One", "Rubik Mono One", "Permanent Marker") else rng.choice([700, 800, 900]), body=rng.choice([400, 500])), scale=scale)

# ------------------------------------------------------------------------------------------------ generation
def generate(rng, family=None, dark=None, hue=None, mood=None, name=None):
    hints = {}
    for w in (mood or "").replace(";", ",").split(","):
        w = w.strip().lower()
        if w in MOODS: hints.update({k: v for k, v in MOODS[w].items()})
    fam_name = family or rng.choice(hints.get("family", list(FAMILIES)))
    fam = FAMILIES[fam_name]
    d = fam["dark"] if dark is None else dark
    if "dark" in hints and dark is None: d = hints["dark"]
    hue = rng.choice(hints.get("hues", fam["hues"])) + rng.randint(-12, 12) if hue is None else hue
    strat = rng.choice(fam["strategies"])
    pal = palette(strat, d, hue, rng)
    fonts = load_fonts()
    typ = pick_type(fam, rng, fonts)
    mname = rng.choice(hints.get("motion", fam["motion"]))
    mo = copy.deepcopy(MOTION[mname]); mo["personality"] = mname
    mo["cutRate"] = round(mo["cutRate"] * rng.uniform(.8, 1.25), 2); mo["stagger"] = round(mo["stagger"] * rng.uniform(.8, 1.25), 3)
    mo["spring"] = dict(w=round(mo["spring"]["w"] * rng.uniform(.9, 1.15), 1), z=round(min(1.2, mo["spring"]["z"] * rng.uniform(.9, 1.1)), 2))
    tex = copy.deepcopy(TEXTURES[rng.choice(fam["textures"])])
    for k in tex:
        if tex[k]: tex[k] = round(tex[k] * rng.uniform(.75, 1.25), 3)
    cam = rng.choice(fam["camera"])
    spal = fam["sound"]
    from_pal = {"neon-mono": (61, 124), "glass-dark": (88, 108), "halftone-collage": (92, 110), "clay-mono": (78, 98), "editorial": (100, 116), "product-film": (88, 108), "radial-burst": (116, 140), "torn-paper": (88, 106), "live-3d": (80, 100), "default": (96, 116)}[spal]
    bpm = rng.randint(*from_pal)
    key = rng.choice(["A", "C", "D", "E", "F", "G", "F#", "Bb"])
    scale = rng.choice(["minor", "minor-pentatonic"] if d else ["major-pentatonic", "minor-pentatonic", "major"])
    moves = rng.sample(MOVES[fam_name], k=min(3, len(MOVES[fam_name])))
    nm = name or f"{fam_name}-{strat}-{int(hue) % 360:03d}-{rng.randint(100, 999)}"
    dna = dict(
        name=nm, version=1, family=fam_name, mood=[w.strip() for w in (mood or "").split(",") if w.strip()] or [pal["mode"], "dark" if d else "light"],
        constraint=f"{strat} palette, hue {int(hue) % 360} deg, {'dark' if d else 'light'} base; " + (f"accent face '{typ['accentSerif']}' allowed for emphasis words" if typ["accentSerif"] else "one display family only"),
        palette=pal, type=typ, texture=tex, motion=mo,
        transitions=list(rng.choice(fam["transitions"])), camera=dict(move=cam, drift=round(rng.uniform(.006, .02), 3), parallax=cam not in ("locked", "static-shallow-dof"), shake=round(rng.uniform(0, .35) if mname in ("jittery-handmade", "snappy-punchy") else rng.uniform(0, .1), 2),
                                                                          dof=cam in ("static-shallow-dof", "slow-dolly-dof"), overscan=.04),
        layout=dict(grid=rng.choice(["center-stack", "left-heavy", "split-vertical", "full-bleed-type", "12-col"]), margins=64, density=rng.choice(["sparse", "medium", "dense"]), aspect="9:16"),
        sound=dict(palette=[spal], bpm=bpm, key=key, scale=scale, reverb="large-dark" if d else "small-bright", brightness=round(rng.uniform(.35, .7), 2), mix=dict(music=-18, sfx=-9, voice=-6), profile="social"),
        signatureMoves=moves, forbidden=FORBID_COMMON + [f"hue outside {int(hue) % 360} +/- 40 deg except neutrals" if strat == "mono" else "a fourth accent colour"], refs=[],
    )
    return dna

# ------------------------------------------------------------------------------------------------ distance + checks
def _g(d, *path, default=None):
    for p in path:
        if not isinstance(d, dict) or p not in d: return default
        d = d[p]
    return d

def tex_sig(d):
    t = _g(d, "texture", default={}) or {}
    return {k for k, v in t.items() if isinstance(v, (int, float)) and v >= .25}

def jacc(a, b):
    a, b = set(a), set(b)
    return 1 - (len(a & b) / len(a | b) if (a | b) else 1)

def dna_distance(a, b):
    """0 = same soul, 1 = nothing in common. Weighted over the choices a viewer actually perceives."""
    ha = _g(a, "palette", "hue"); hb = _g(b, "palette", "hue")
    if ha is None: ha = hex2oklch(_g(a, "palette", "accent", default="#888888"))[2]
    if hb is None: hb = hex2oklch(_g(b, "palette", "accent", default="#888888"))[2]
    la = hex2oklch(_g(a, "palette", "bg", default="#000000"))[0]; lb = hex2oklch(_g(b, "palette", "bg", default="#000000"))[0]
    parts = [
        (.16, hue_dist(ha, hb)), (.10, min(1, abs(la - lb) * 1.6)),
        (.08, 0 if _g(a, "palette", "mode") == _g(b, "palette", "mode") else 1),
        (.15, 0 if _g(a, "type", "display") == _g(b, "type", "display") else 1), (.04, 0 if _g(a, "type", "body") == _g(b, "type", "body") else 1),
        (.04, 0 if _g(a, "type", "accentSerif") == _g(b, "type", "accentSerif") else 1),
        (.10, jacc(tex_sig(a), tex_sig(b))),
        (.15, 0 if _g(a, "motion", "personality") == _g(b, "motion", "personality") else 1),
        (.10, jacc(_g(a, "transitions", default=[]), _g(b, "transitions", default=[]))),
        (.04, 0 if _g(a, "camera", "move") == _g(b, "camera", "move") else 1),
        (.04, 0 if _g(a, "family") == _g(b, "family") else 1),
    ]
    return round(sum(w * v for w, v in parts) / sum(w for w, _ in parts), 3)

def load_history(path):
    try:
        h = json.load(open(path))
        return h if isinstance(h, dict) and "entries" in h else {"version": 1, "entries": []}
    except Exception:
        return {"version": 1, "entries": []}

def history_dnas(path, n=5):
    return [e["dna"] for e in load_history(path)["entries"] if e.get("dna")][-n:]

def validate(dna):
    errs, warns = [], []
    for k in ("name", "palette", "type", "texture", "motion", "transitions", "camera", "sound", "signatureMoves", "forbidden"):
        if k not in dna: errs.append(f"missing field: {k}")
    p = dna.get("palette", {})
    for k in ("bg", "ink", "accent", "accent2"):
        v = p.get(k)
        if not (isinstance(v, str) and len(v) == 7 and v.startswith("#")): errs.append(f"palette.{k} must be #rrggbb, got {v!r}")
    if not errs:
        c1 = contrast(p["ink"], p["bg"]); c2 = contrast(p["accent"], p["bg"])
        if c1 < 4.5: errs.append(f"ink vs bg contrast {c1:.1f}:1 < 4.5")
        if c2 < 2.2: warns.append(f"accent vs bg contrast {c2:.1f}:1 is weak (use accent for shapes, ink for text)")
        L, C, h = hex2oklch(p["accent"]); Lb = hex2oklch(p["bg"])[0]
        if Lb < .22 and 245 <= h <= 305 and _g(dna, "palette", "mode") not in ("mono",):
            warns.append("purple/blue accent on a dark base is the AI default look; choose another hue unless the brief demands it")
        if contrast(p["accent"], "#ff4f1a") < 1.12 and contrast(p["bg"], "#0b0b10") < 1.12: errs.append("palette equals the old toolkit default (#0b0b10 + #ff4f1a)")
    t = dna.get("type", {})
    fonts = load_fonts()
    for k in ("display", "body"):
        if fonts and t.get(k) and t[k] not in fonts: warns.append(f"type.{k} '{t[k]}' is not in the shipped fonts (embed it yourself)")
    if not t.get("display"): errs.append("type.display missing")
    for e in _g(dna, "motion", "ease", default=[]):
        if e not in VALID_EASE and e != "steps": warns.append(f"motion.ease '{e}' is not a Lab.ease name")
    for e in _g(dna, "motion", "curves", default=[]):
        if e not in VALID_CURVES: warns.append(f"motion.curves '{e}' is not a Lab.curves name")
    sp = _g(dna, "sound", "palette", default=[])
    if not sp or sp[0] not in SOUND_PALETTES: warns.append(f"sound.palette[0] should be one of {SOUND_PALETTES}")
    if len(dna.get("signatureMoves", [])) < 2: warns.append("add at least 2 signatureMoves (what makes this video recognisable)")
    if len(dna.get("transitions", [])) < 2: warns.append("list at least 2 transitions; assign one per seam in the storyboard")
    return errs, warns

# ------------------------------------------------------------------------------------------------ CLI
def load_presets():
    out = {}
    for f in sorted(glob.glob(os.path.join(PRESET_DIR, "*.json"))):
        try:
            d = json.load(open(f)); out[d["name"]] = d
        except Exception as e:
            print("bad preset", f, e, file=sys.stderr)
    return out

def mutate(dna, rng):
    """Same family, different soul: shift hue, swap display font within the family pool, re-time."""
    d = copy.deepcopy(dna)
    fam = FAMILIES.get(d.get("family"))
    shift = rng.choice([-120, -75, -40, 40, 75, 120, 180])
    new_h = ((_g(d, "palette", "hue", default=hex2oklch(d["palette"]["accent"])[2]) or 0) + shift) % 360
    if fam:
        newp = palette(d["palette"].get("mode", "mono"), d["palette"].get("dark", True), new_h, rng)
        d["palette"] = newp
        pool = [x for x in fam["display"] if x != d["type"]["display"]]
        if pool: d["type"]["display"] = rng.choice(pool)
        if d["type"]["display"] in ("Anton", "Bebas Neue", "Black Ops One", "Rubik Mono One"): d["type"]["case"] = "upper"
    d["motion"]["cutRate"] = round(d["motion"]["cutRate"] * rng.uniform(.75, 1.3), 2)
    d["motion"]["stagger"] = round(d["motion"]["stagger"] * rng.uniform(.75, 1.3), 3)
    d["sound"]["key"] = rng.choice(["A", "C", "D", "E", "F", "G", "F#", "Bb"]); d["sound"]["bpm"] = int(d["sound"]["bpm"] * rng.uniform(.9, 1.12))
    d["name"] = f"{dna['name']}-m{rng.randint(10, 99)}"
    return d

def divergent(n, rng, hist, min_d, **kw):
    """n DNAs, pairwise and vs history >= min_d where possible; families all different."""
    chosen, fams = [], set()
    for _ in range(n):
        best, bestd = None, -1
        for _t in range(400):
            fam = rng.choice([f for f in FAMILIES if f not in fams] or list(FAMILIES)) if not kw.get("family") else kw["family"]
            c = generate(rng, family=fam, dark=kw.get("dark"), mood=kw.get("mood"))
            ds = [dna_distance(c, o) for o in chosen + hist] or [1]
            m = min(ds)
            if m > bestd: best, bestd = c, m
            if m >= min_d: break
        chosen.append(best); fams.add(best["family"])
    return chosen

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true"); ap.add_argument("--generate", action="store_true"); ap.add_argument("--candidates", type=int)
    ap.add_argument("--preset"); ap.add_argument("--mutate", type=int); ap.add_argument("--check"); ap.add_argument("--add"); ap.add_argument("--name")
    ap.add_argument("--distance", nargs=2); ap.add_argument("--seed", type=int); ap.add_argument("--mood"); ap.add_argument("--family")
    ap.add_argument("--dark", action="store_true"); ap.add_argument("--light", action="store_true"); ap.add_argument("--hue", type=float)
    ap.add_argument("--history", default=".motion/style-history.json"); ap.add_argument("--min-distance", type=float, default=.45)
    ap.add_argument("--out"); ap.add_argument("--out-dir")
    a = ap.parse_args()
    rng = random.Random(a.seed if a.seed is not None else random.SystemRandom().randrange(1 << 30))
    dark = True if a.dark else (False if a.light else None)
    hist = history_dnas(a.history)

    if a.list:
        for n, d in load_presets().items():
            print(f"{n:<28} family={d.get('family','?'):<16} {d.get('constraint','')}")
        print("\nfamilies for --generate/--family:", ", ".join(FAMILIES)); return 0
    if a.distance:
        print(dna_distance(json.load(open(a.distance[0])), json.load(open(a.distance[1])))); return 0
    if a.check:
        dna = json.load(open(a.check)); errs, warns = validate(dna)
        for e in errs: print("ERROR  ", e)
        for w in warns: print("WARN   ", w)
        bad = False
        for i, h in enumerate(reversed(hist)):
            d = dna_distance(dna, h)
            flag = "SAME_SOUL" if d < a.min_distance else "ok"
            print(f"distance to {h.get('name','?'):<30} {d:.2f}  {flag}")
            if d < a.min_distance:
                bad = True
                diff = []
                for k, path in (("palette hue", ("palette", "hue")), ("display font", ("type", "display")), ("motion personality", ("motion", "personality")), ("transitions", ("transitions",)), ("camera move", ("camera", "move"))):
                    if _g(dna, *path) == _g(h, *path): diff.append(k)
                print("   change at least:", ", ".join(diff) or "palette mode, texture set")
        if not hist: print("(no history yet: first video of this project)")
        print("RESULT:", "FAIL" if errs or bad else "PASS"); return 1 if errs or bad else 0
    if a.add:
        dna = json.load(open(a.add)); h = load_history(a.history); nm = a.name or dna.get("name", "video")
        ent = next((e for e in h["entries"] if e.get("name") == nm), None)
        if ent: ent["dna"] = dna
        else: h["entries"].append(dict(name=nm, date=datetime.date.today().isoformat(), dna=dna, fingerprint=None))
        os.makedirs(os.path.dirname(os.path.abspath(a.history)), exist_ok=True); json.dump(h, open(a.history, "w"), indent=1)
        print("ledger now has", len(h["entries"]), "entries ->", a.history); return 0
    if a.candidates:
        out = divergent(a.candidates, rng, hist, a.min_distance, family=a.family, dark=dark, mood=a.mood)
        od = a.out_dir or "."; os.makedirs(od, exist_ok=True)
        for i, d in enumerate(out):
            fp = os.path.join(od, f"dna-candidate-{i + 1}.json"); json.dump(d, open(fp, "w"), indent=1)
            print(f"{fp}: {d['name']}  [{d['family']}]  {d['constraint']}")
        for i in range(len(out)):
            for j in range(i + 1, len(out)): print(f"distance {i + 1}-{j + 1}: {dna_distance(out[i], out[j]):.2f}")
        return 0
    if a.preset:
        pre = load_presets()
        if a.preset not in pre: print("unknown preset; use --list"); return 2
        d = pre[a.preset]
        if a.mutate is not None: d = mutate(d, random.Random(a.mutate))
    elif a.generate:
        best = None
        for _ in range(300):
            c = generate(rng, family=a.family, dark=dark, hue=a.hue, mood=a.mood, name=a.name)
            m = min([dna_distance(c, h) for h in hist] or [1])
            if best is None or m > best[0]: best = (m, c)
            if m >= a.min_distance: break
        d = best[1]; print(f"min distance to the last {len(hist)} videos: {best[0]:.2f}")
    else:
        ap.print_help(); return 2
    errs, warns = validate(d)
    for e in errs: print("ERROR", e)
    for w in warns: print("WARN ", w)
    text = json.dumps(d, indent=1)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); open(a.out, "w").write(text); print("wrote", a.out, "->", d["name"])
    else:
        print(text)
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main())
