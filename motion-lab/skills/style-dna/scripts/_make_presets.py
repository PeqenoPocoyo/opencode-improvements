#!/usr/bin/env python3
"""Writes the 12 reference-derived DNA presets to ../dna/*.json. Presets are TECHNIQUE starting points, never to be used unmodified
(use dna_generate.py --preset NAME --mutate SEED). Run once; the JSON files are what ships and what you edit."""
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dna")
os.makedirs(OUT, exist_ok=True)

def T(display, body, mono="JetBrains Mono", accent=None, case="sentence", td=0.0, tl=.18, wd=800, wb=400, scale=(1, 1.6, 2.6)):
    return dict(display=display, body=body, mono=mono, accentSerif=accent, case=case, tracking=dict(display=td, body=0.0, label=tl), weights=dict(display=wd, body=wb), scale=list(scale))

def X(grain=0, vignette=0, halftone=0, paper=0, scan=0, bloom=0, dust=0, chromatic=0, lightleak=0):
    return dict(grain=grain, vignette=vignette, halftone=halftone, paper=paper, scan=scan, bloom=bloom, dust=dust, chromatic=chromatic, lightleak=lightleak)

def M(personality, ease, curves, w, z, stagger, cutRate, hitStyle, hold):
    return dict(personality=personality, ease=ease, curves=curves, spring=dict(w=w, z=z), stagger=stagger, cutRate=cutRate, hitStyle=hitStyle, hold=hold)

def S(pal, bpm, key, scale, reverb, brightness, profile="social"):
    return dict(palette=[pal], bpm=bpm, key=key, scale=scale, reverb=reverb, brightness=brightness, mix=dict(music=-18, sfx=-9, voice=-6), profile=profile)

def C(move, drift=.01, parallax=True, shake=0, dof=False):
    return dict(move=move, drift=drift, parallax=parallax, shake=shake, dof=dof, overscan=.04)

def PAL(mode, dark, hue, bg, bg2, ink, ink2, accent, accent2, support):
    return dict(mode=mode, dark=dark, hue=hue, bg=bg, bg2=bg2, ink=ink, ink2=ink2, accent=accent, accent2=accent2, support=support)

COMMON_FORBID = ["Math.random / Date.now / CSS transitions in scene code", "system fonts", "centered card on a purple-blue gradient", "the same easing on everything", "more than one new idea per beat", "text outside the 9:16 safe area"]

P = []

P.append(dict(name="neon-mono-night", family="neon-mono", refs=["v01", "v07"], mood=["focused", "nocturnal", "earnest"],
    constraint="ONE hue (green) on near-black; every other colour is neutral; figures are flat silhouettes lit only by a rim",
    palette=PAL("mono", True, 150, "#04120a", "#0c4a22", "#eafff1", "#9fd9b4", "#39ff7a", "#b9ffd2", ["#0e5a2a", "#6fe39a"]),
    type=T("Anton", "Inter Tight", accent=None, case="upper", td=.01, wd=400), texture=X(grain=.06, vignette=.5, scan=.1, bloom=.85, dust=.35, chromatic=.1),
    motion=M("calm-precise", ["outExpo", "inOutSine"], ["glide", "settle"], 9, .85, .07, .5, "glow-pulse", [.7, 1.6]),
    transitions=["focusPull", "frameCarry", "dipToColor"], camera=C("slow-push", .012, True, .15),
    layout=dict(grid="center-stack", margins=64, density="sparse", aspect="9:16"), sound=S("neon-mono", 70, "A", "minor", "large-dark", .4),
    signatureMoves=["numerals bigger than the figure, glowing, half-covered by the subject", "vertical single-hue gradient with floor reflection", "dashed frame rotates to open the next scene", "word-by-word captions that scale in on the voice", "dust motes drifting through the light cone"],
    forbidden=COMMON_FORBID + ["a second hue", "photographic images"]))

P.append(dict(name="live-3d-icon-arc", family="live-3d", refs=["v02"], mood=["tactile", "premium", "quiet"],
    constraint="the footage owns the colour; CG objects are glossy neutrals with one rim hue; no text except one tiny label",
    palette=PAL("neutral-pop", False, 250, "#d7dbe0", "#aeb6c0", "#101418", "#4c5560", "#3a6bff", "#9cc0ff", ["#f4f6f8", "#7c8794"]),
    type=T("Inter Tight", "Inter Tight", case="lower", td=-.03, wd=700), texture=X(grain=.05, vignette=.2, bloom=.15, chromatic=.03),
    motion=M("fluid-liquid", ["inOutSine", "outCirc"], ["glide", "whip"], 7, .9, .06, .3, "soft-ripple", [.8, 2.0]),
    transitions=["objectCarry", "whipPan", "crossfade"], camera=C("static-shallow-dof", .004, False, 0, True),
    layout=dict(grid="arc-over-subject", margins=64, density="sparse", aspect="9:16"), sound=S("live-3d", 90, "C", "minor-pentatonic", "medium-room", .5),
    signatureMoves=["glossy objects ride a parametric arc above the footage", "scroll-linked index with a velocity curve and motion blur", "contact shadow + shallow DoF + grain match the footage", "the next icon set slides in along the same arc"],
    forbidden=COMMON_FORBID + ["flat icons without highlight", "CG without a shadow on the real surface"]))

P.append(dict(name="halftone-poster-loop", family="halftone-poster", refs=["v03"], mood=["loud", "retro", "kinetic"],
    constraint="duotone (blue + red on cream) with halftone on every layer; the last frame equals the first",
    palette=PAL("duotone", False, 255, "#efe9dc", "#c9d4f2", "#14206b", "#4b5aa8", "#2a3fd6", "#e5372b", ["#9fb2f0", "#f19b92"]),
    type=T("Alfa Slab One", "Archivo", accent="Permanent Marker", case="upper", wd=400, tl=.1), texture=X(grain=.12, vignette=.15, halftone=.9, paper=.2, dust=.1),
    motion=M("snappy-punchy", ["outQuart", "outBack"], ["punch", "snap"], 16, .55, .035, 1.1, "scale-punch+shake", [.25, .7]),
    transitions=["zoomThrough", "whiteFlash", "halftoneDissolve"], camera=C("push-through", .015, True, .2),
    layout=dict(grid="layer-stack", margins=64, density="dense", aspect="9:16"), sound=S("halftone-collage", 100, "D", "minor-pentatonic", "small-room", .52),
    signatureMoves=["camera pushes THROUGH a stack of cutout layers", "signs fly in with rotation overshoot, then settle", "white sticker border + hard shadow on every cutout", "duotone map on every layer", "loop: end frame == first frame"],
    forbidden=COMMON_FORBID + ["more than two ink colours", "smooth gradients"]))

P.append(dict(name="talking-head-designed-broll", family="editorial", refs=["v04"], mood=["intimate", "smart", "warm"],
    constraint="one shared palette (deep green, cream, highlighter yellow) across very different cutaway worlds; captions are one lowercase word at a time",
    palette=PAL("analogous", True, 150, "#0f2a1f", "#1d4a37", "#f4efdf", "#bcd0c2", "#f6d84a", "#e8553d", ["#2f6b50", "#f4efdf"]),
    type=T("Instrument Serif", "Inter Tight", accent="Instrument Serif", case="lower", td=-.02, wd=400), texture=X(grain=.06, vignette=.3, paper=.3, dust=.2),
    motion=M("calm-precise", ["outCubic", "inOutSine"], ["settle", "glide"], 9, .85, .06, .45, "soft-settle", [1.0, 2.5]),
    transitions=["hardCutOnWord", "dipToColor", "crossfade"], camera=C("gentle-push", .01, True, .05),
    layout=dict(grid="center-stack", margins=64, density="medium", aspect="9:16"), sound=S("editorial", 100, "G", "major-pentatonic", "small-bright", .5, "conservative"),
    signatureMoves=["cutaways every 4-8 s on nouns or claims, 1.2-3 s long", "spotlight cone on dark green with a pinned paper note", "centered word-by-word lowercase captions", "serif italic words scattered on a white page", "hard cut on the word, voice continues across the cut"],
    forbidden=COMMON_FORBID + ["cutaways on emotional lines", "hit-synced sound over the voice"]))

P.append(dict(name="glass-icon-universe", family="glass-dark", refs=["v05"], mood=["premium", "futuristic", "calm"],
    constraint="pure black; every object is dark glass with a thin coloured gradient rim and bloom; text is thin and small",
    palette=PAL("complementary", True, 25, "#020204", "#10121c", "#f3f4f8", "#8f93a5", "#ff7a2f", "#6a4bff", ["#2a6bff", "#1b1d29"]),
    type=T("Outfit", "Inter Tight", case="sentence", td=-.02, wd=300), texture=X(grain=.04, vignette=.55, bloom=.7, dust=.2, chromatic=.2, lightleak=.1),
    motion=M("fluid-liquid", ["inOutSine", "outCirc"], ["glide", "whip"], 7, .9, .06, .45, "soft-ripple", [.8, 1.8]),
    transitions=["glassRefract", "ringFormation", "blurSwap"], camera=C("slow-dolly-dof", .01, True, 0, True),
    layout=dict(grid="ring-around-title", margins=64, density="sparse", aspect="9:16"), sound=S("glass-dark", 96, "F#", "major-pentatonic", "large-hall", .68),
    signatureMoves=["icons float in a ring at different depths, far ones blurred", "coloured rim light gradient on every glass plate", "text swaps with a blur cross-fade", "ring forms, dissolves, reforms around a single hero"],
    forbidden=COMMON_FORBID + ["flat fills without rim light", "bright backgrounds"]))

P.append(dict(name="product-film-ui", family="product-film", refs=["v06"], mood=["clear", "confident", "calm"],
    constraint="warm light-grey canvas; the UI is the hero; colour appears only on data and one accent",
    palette=PAL("neutral-pop", False, 25, "#efece6", "#e2ded5", "#1c1a17", "#6c675f", "#ff6a3d", "#2b2825", ["#f9f7f3", "#bdb8ad"]),
    type=T("Inter Tight", "Inter Tight", accent="Instrument Serif", case="sentence", td=-.02, wd=600), texture=X(grain=.015, vignette=.06, bloom=.05),
    motion=M("calm-precise", ["outExpo", "inOutSine"], ["glide", "settle"], 9, .85, .07, .35, "soft-settle", [1.0, 2.2]),
    transitions=["uiExpand", "objectCarry", "crossfade"], camera=C("ui-push", .006, False, 0),
    layout=dict(grid="12-col", margins=96, density="medium", aspect="16:9"), sound=S("product-film", 96, "F", "major", "small-room", .5, "conservative"),
    signatureMoves=["rebuilt UI as clean vectors with a choreographed cursor (click ripple, drag)", "UI element expands into the next scene", "2D data points lift into a 3D grid with tilt-shift", "camera pushes into the UI region that matters"],
    forbidden=COMMON_FORBID + ["fake brand logos", "invented metrics presented as real"]))

P.append(dict(name="radial-neon-burst", family="radial-burst", refs=["v07"], mood=["focused", "kinetic", "minimal"],
    constraint="black, one glow hue + white; a single node and rays; words ride the rays",
    palette=PAL("mono", True, 150, "#000000", "#04170c", "#ffffff", "#9aa8a0", "#3dff7a", "#7fffe0", ["#0c5a2c", "#d8fff0"]),
    type=T("Outfit", "Outfit", mono="Space Mono", case="lower", td=0.0, wd=300), texture=X(grain=.04, vignette=.4, bloom=.9, chromatic=.06),
    motion=M("mechanical-steps", ["inOutQuart", "linear"], ["snap", "whip"], 20, 1.0, .12, .9, "tick-step", [.3, .9]),
    transitions=["loopRing", "dipToColor"], camera=C("locked", 0, False, 0),
    layout=dict(grid="radial", margins=64, density="sparse", aspect="9:16"), sound=S("radial-burst", 124, "D", "minor-pentatonic", "medium-room", .5),
    signatureMoves=["one node, twelve rays drawn with outExpo", "words fly along rays rotated to the ray angle, clockwise stagger 0.12 s", "one ray extends and carries the key word", "ends where it began (loop)"],
    forbidden=COMMON_FORBID + ["a second node", "filled shapes"]))

P.append(dict(name="editorial-explainer", family="editorial", refs=["v08"], mood=["smart", "playful", "clear"],
    constraint="light grid paper; three accents only (purple, orange, lime); grotesk + serif-italic mixed in ONE sentence",
    palette=PAL("tri-accent", False, 285, "#f6f5f0", "#e9e7df", "#14121a", "#8a8794", "#6a2cf0", "#ff7a1a", ["#b8f03a", "#d6d3ca"]),
    type=T("Inter Tight", "Inter Tight", accent="Instrument Serif", case="mixed", td=-.03, wd=800), texture=X(grain=.03, vignette=.08, paper=.35, bloom=.12),
    motion=M("elastic-pop", ["outBack", "outElastic"], ["settle", "punch"], 13, .4, .05, .8, "overshoot-pop", [.4, 1.0]),
    transitions=["sparkleSweep", "arcWipe", "crossfade"], camera=C("gentle-push", .01, True, 0),
    layout=dict(grid="12-col", margins=64, density="medium", aspect="9:16"), sound=S("editorial", 108, "G", "major-pentatonic", "small-bright", .55),
    signatureMoves=["grotesk + serif-italic inside one sentence", "dashed selection box with corner handles around a label", "count-up numbers with a soft glow", "4-point sparkle stars sweep in with a big arc", "bars rise while a line draws across"],
    forbidden=COMMON_FORBID + ["a fourth accent", "dark backgrounds"]))

P.append(dict(name="glass-folder-render", family="glass-dark", refs=["v09"], mood=["glossy", "satisfying", "slow"],
    constraint="dark radial green studio; one glossy translucent object; no text; slow orbit with a moving specular sweep",
    palette=PAL("mono", True, 150, "#031009", "#0a3a22", "#e8fff2", "#8fc9a5", "#27e07a", "#9dffcb", ["#0b6a3a", "#d9ffe9"]),
    type=T("Outfit", "Inter Tight", case="sentence", wd=400), texture=X(grain=.04, vignette=.5, bloom=.5, chromatic=.1, lightleak=.1),
    motion=M("heavy-cinematic", ["inOutCubic", "outQuint"], ["drop", "glide"], 6, 1.0, .09, .25, "slow-slam", [1.2, 2.4]),
    transitions=["lightLeakWipe", "crossfade"], camera=C("orbit-slow", .02, True, 0, True),
    layout=dict(grid="hero-center", margins=64, density="sparse", aspect="9:16"), sound=S("glass-dark", 92, "F#", "major-pentatonic", "large-hall", .65),
    signatureMoves=["front plate + back plate with cards sandwiched and parallaxed", "light-sweep gradient mask travelling across the glass", "one controller group owns the rotation", "cards pop up with a spring when the lid opens"],
    forbidden=COMMON_FORBID + ["opaque materials", "text"]))

P.append(dict(name="clay-mono-editorial", family="clay-mono", refs=["v10"], mood=["calm", "premium", "thoughtful"],
    constraint="cream paper with a strong vignette; objects are black/grey clay 3D; the only emphasis is a grey-to-black tone shift",
    palette=PAL("neutral-pop", False, 25, "#f1eee6", "#e4dfd2", "#141311", "#8a867c", "#141311", "#9b968a", ["#ffffff", "#2a2823"]),
    type=T("Inter Tight", "Inter Tight", accent="Instrument Serif", case="sentence", td=-.03, wd=800), texture=X(grain=.05, vignette=.45, paper=.25, dust=.08),
    motion=M("heavy-cinematic", ["inOutCubic", "outQuint"], ["drop", "glide"], 6, 1.0, .09, .35, "slow-slam", [1.0, 2.2]),
    transitions=["objectCarry", "slidePush", "dipToColor"], camera=C("slow-push", .01, True, 0),
    layout=dict(grid="center-stack", margins=72, density="sparse", aspect="9:16"), sound=S("clay-mono", 88, "C", "major-pentatonic", "small-room", .38),
    signatureMoves=["grey-to-black tone shift on the emphasized word", "soft contact shadows under every object", "pill labels stack with a soft shadow", "strikethrough draws across a word", "dark end card"],
    forbidden=COMMON_FORBID + ["saturated colours", "glow"]))

P.append(dict(name="torn-paper-collage", family="torn-paper", refs=["v11"], mood=["raw", "loud", "handmade"],
    constraint="off-white paper + black ink + ONE red; everything is paper, tape or ink; halftone for photos",
    palette=PAL("paper-ink", False, 25, "#ece6d8", "#dcd3bf", "#15130f", "#5b564b", "#e2331f", "#15130f", ["#bfb6a2", "#35c7e0"]),
    type=T("Alfa Slab One", "Archivo", accent="Permanent Marker", case="upper", wd=400, tl=.12), texture=X(grain=.1, vignette=.2, halftone=.55, paper=.9, dust=.25, lightleak=.1),
    motion=M("jittery-handmade", ["outCubic", "steps"], ["snap"], 14, .5, .045, 1.4, "slap+flash", [.2, .6]),
    transitions=["whiteFlash", "paperTear", "slidePush"], camera=C("handheld", .01, True, .35),
    layout=dict(grid="off-axis", margins=64, density="dense", aspect="9:16"), sound=S("torn-paper", 96, "A", "blues", "small-room", .56),
    signatureMoves=["window-blind shadows drift across the paper", "words on tape/label strips at slight angles", "hand-drawn scribble circle around the key word", "torn edge reveal and a 3-frame white flash cut", "stepped handheld jitter at 12 Hz"],
    forbidden=COMMON_FORBID + ["smooth vector gradients", "perfectly aligned elements"]))

P.append(dict(name="terminal-brutalist", family="terminal-brutal", refs=[], mood=["technical", "cold", "urgent"],
    constraint="monospace only; black + one acid colour; scanlines and RGB split; text is the interface",
    palette=PAL("neutral-pop", True, 100, "#0a0b09", "#161812", "#e8ecd9", "#8a9078", "#c8ff00", "#ff3b5c", ["#2a2d22", "#5d6450"]),
    type=T("JetBrains Mono", "JetBrains Mono", mono="JetBrains Mono", case="upper", td=.01, wd=800), texture=X(grain=.09, vignette=.35, scan=.6, bloom=.5, chromatic=.25),
    motion=M("mechanical-steps", ["inOutQuart", "linear"], ["snap", "whip"], 20, 1.0, .03, .9, "tick-step", [.3, .9]),
    transitions=["glitchSwap", "scanlineWipe", "vhsRewind"], camera=C("locked", 0, False, .1),
    layout=dict(grid="12-col", margins=48, density="dense", aspect="9:16"), sound=S("default", 108, "E", "minor", "small-room", .55),
    signatureMoves=["text types out with a block cursor", "scanline sweep wipes between beats", "RGB split on every hit", "monospace tables fill row by row", "status chips flip OK/ERR"],
    forbidden=COMMON_FORBID + ["proportional fonts", "soft shadows", "rounded corners"]))

for d in P:
    d["version"] = 1
    json.dump(d, open(os.path.join(OUT, d["name"] + ".json"), "w"), indent=1)
print(len(P), "presets ->", os.path.abspath(OUT))
