#!/usr/bin/env python3
"""play_make.py - generate N *different* loopable generative pieces (scene.html each) by crossbreeding DNA presets, backgrounds, artwork, type and FX.
Free/recreational mode: no brief needed. Every piece is a pure seek(t) scene (1080x1080 or --size WxH, 6 s loop).

  python3 play_make.py --project myproj --n 6 --seed 11            # writes myproj/play/p01..p06/scene.html + piece.json
  python3 play_make.py --project myproj --n 4 --recipe type-poster --size 1080x1350
  python3 play_make.py --list                                       # recipes
  python3 play_make.py --project myproj --repeat myproj/play/p03/piece.json --seed 99     # same recipe, new seed/palette (a "series")

Then render a sheet:  node skills/scene-runtime/scripts/render.mjs myproj/play/p01/scene.html - ...   (see SKILL.md) 
Needs a project made by scene-runtime/scripts/setup.sh (lab/ with all runtimes). Randomness lives here (generator), never in the scene.
"""
import argparse, glob, json, os, random, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); PACK = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DNA_GEN = os.path.join(PACK, "skills", "style-dna", "scripts", "dna_generate.py")
PRESETS = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(PACK, "skills", "style-dna", "dna", "*.json")))
ART = re.findall(r"add\('(\w+)'", open(os.path.join(PACK, "skills", "motion-canvas-artwork", "runtime", "art.js")).read())
SHADERS = [s for s in re.findall(r"^## `([\w-]+)`", open(os.path.join(PACK, "skills", "generative-3d-backgrounds", "reference", "shader-catalog.md")).read(), re.M)]
STYLES = ["slam", "slideUp", "fadeBlur", "blurFocus", "scramble", "widthMorph", "weightMorph", "glitchIn", "pop", "elastic", "maskWipe", "flip3d", "zoomThrough", "stampDown", "trackIn", "wave"]
WORDS = ["FLOW", "SIGNAL", "DRIFT", "BLOOM", "PULSE", "ORBIT", "STATIC", "GRAIN", "HALO", "TIDE", "ECHO", "FORM", "LOOP", "SPARK", "HUSH", "NOVA", "RIPPLE", "MOSS", "VOLT", "ATLAS", "FABLE", "DUSK", "PRISM", "KILN"]
HEAVY_ART = {"flowField", "voronoi", "plexus", "memphis", "glyphField", "isoBars", "confetti", "lightning", "scribble"}
FOCAL = ["lissajous", "mandala", "radialBars", "spiral", "rings", "polyRipples", "tunnelRects", "sunburst", "orbits", "blobs", "stringArt", "sineBraid", "voronoi", "flowField", "hexPulse", "truchet", "isoBars", "stripesWarp", "waveLines", "bubbles", "plexus", "brushStrokes", "memphis", "lowPoly"]
FIELD = ["contours", "warpGrid", "dotGrid", "moire", "hexPulse", "pixelMosaic", "waveLines", "truchet", "stripesWarp", "flowField", "glyphField"]
RECIPES = {
    "world-and-field": "3D shader world + one low-alpha art field + big word",
    "art-poster": "soft gradient ground + focal art + word filled with a second art (clip)",
    "pure-generative": "flat ground + focal art + field art, no text",
    "shader-solo": "just a shader world with grain/vignette (cleanest)",
    "type-poster": "flat ground + giant kinetic type + small art accent",
    "halftone-print": "focal art run through halftone/risograph FX",
    "terminal": "glyph field + plexus + CRT",
    "orbit-system": "light paper ground + orbits/rings infographic mood",
}

def make_dna(preset, seed):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "d.json")
        r = subprocess.run([sys.executable, DNA_GEN, "--preset", preset, "--mutate", str(seed), "--out", out], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(out): raise SystemExit("dna_generate failed: " + r.stderr[-400:])
        return json.load(open(out))

def pal5(d):
    p = d["palette"]; sup = p.get("support") or []
    return dict(bg3d=[p["bg"], p.get("bg2", p["bg"]), p["accent"], p.get("accent2", p["accent"]), p["ink"]],
                art=[p["bg"], p["accent"], p.get("accent2", p["accent"]), (sup[0] if sup else p.get("ink2", p["ink"])), p["ink"]], dark=p.get("dark", True))

def build(recipe, seed, size, preset=None):
    rnd = random.Random(seed); preset = preset or rnd.choice(PRESETS); dna = make_dna(preset, seed); P = pal5(dna)
    heavy = [a for a in FOCAL if a in HEAVY_ART]; calm = [a for a in FOCAL if a not in HEAVY_ART]
    cfg = dict(recipe=recipe, seed=seed, preset=preset, size=size, palette=P, texture=dna.get("texture", {}), font=dna["type"]["display"], fontBody=dna["type"].get("body"), word=rnd.choice(WORDS),
               style=rnd.choice(STYLES), art_seed=rnd.randint(1, 99), shader=rnd.choice([s for s in SHADERS if not s.startswith("ray-")] or SHADERS), shader_seed=rnd.randint(1, 99))
    cfg["focal"] = rnd.choice(calm if recipe != "pure-generative" else FOCAL); cfg["field"] = rnd.choice([a for a in FIELD if a != cfg["focal"]]); cfg["fieldAlpha"] = round(rnd.uniform(.14, .32), 2)
    cfg["clipArt"] = rnd.choice(["flowField", "stripesWarp", "contours", "dotGrid", "sineBraid", "voronoi", "moire"]); cfg["ground"] = rnd.choice(["gradientBlobs", "flat"])
    cfg["fxchain"] = rnd.choice(["neonBloom", "filmWarm", "glassDark", "riso", "cleanEditorial"]) if recipe in ("halftone-print",) else None
    cfg["caseUpper"] = dna["type"].get("case", "upper") == "upper"
    return cfg, dna

TEMPLATE = r'''<!doctype html><html><head><meta charset="utf-8"><title>__TITLE__</title>
<link rel="stylesheet" href="../../lab/fonts/fonts.css"><style>html,body{margin:0;background:#000}canvas{display:block}#t{position:absolute;left:0;top:0;width:__W__px;height:__H__px;pointer-events:none}</style></head><body>
<div style="position:relative;width:__W__px;height:__H__px"><canvas id="c" width="__W__" height="__H__"></canvas><div id="t"><div id="w" style="position:absolute;left:0;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;text-align:center"></div></div></div>
<script src="../../lab/lab.js"></script><script src="../../lab/art.js"></script><script src="../../lab/bg3d.js"></script><script src="../../lab/shaders.js"></script><script src="../../lab/shaders2.js"></script><script src="../../lab/shaders3.js"></script><script src="../../lab/fx.js"></script><script src="../../lab/type.js"></script>
<script>
// Generated by play_make.py. Config below is the whole piece: edit values and re-render. Pure function of t; loops every DUR seconds.
const CFG = __CFG__;
const W = __W__, H = __H__, DUR = 6, c = document.getElementById('c'), ctx = c.getContext('2d'), P = CFG.palette;
const lum = h => { const n = parseInt(h.slice(1), 16); return .2126 * (n >> 16 & 255) + .7152 * (n >> 8 & 255) + .0722 * (n & 255); };
const PAPER = lum(P.art[0]) > lum(P.art[4]) ? P.art[0] : P.art[4], INKC = PAPER === P.art[0] ? P.art[4] : P.art[0];
const lay = document.createElement('canvas'); lay.width = W; lay.height = H; const lc = lay.getContext('2d');
const txt = document.createElement('canvas'); txt.width = W; txt.height = H; const tc = txt.getContext('2d');
const bg = (CFG.recipe === 'world-and-field' || CFG.recipe === 'shader-solo') ? Bg3D.create(Math.round(W / 2), Math.round(H / 2)) : null;
const fx = FX.create(W, H), T = CFG.texture || {};
const word = document.getElementById('w'), wspan = document.createElement('div'); word.appendChild(wspan);
const nW = CFG.word.length, size = Math.min(Math.min(W, H) * (CFG.recipe === 'type-poster' ? .34 : .26), W * .86 / (nW * .66));
wspan.style.cssText = `font:${CFG.recipe === 'type-poster' ? 900 : 800} ${size}px '${CFG.font}', 'Archivo', sans-serif;color:${P.art[4]};letter-spacing:-.02em;line-height:.9;white-space:nowrap;opacity:0`;
const TY = Type.make(wspan, CFG.caseUpper ? CFG.word : CFG.word[0] + CFG.word.slice(1).toLowerCase(), { by: 'chars', mask: ['slideUp'].includes(CFG.style) });
function finish(t) {
  const passes = [];
  if ((T.bloom || 0) > .35) passes.push({ pass: 'bloom', intensity: Math.min(1.2, T.bloom), threshold: .6, radius: 16 });
  if ((T.chromatic || 0) > .05) passes.push({ pass: 'chromatic', amount: .0015 + T.chromatic * .004 });
  if (CFG.recipe === 'halftone-print' || (T.halftone || 0) > .4) passes.push({ pass: 'halftone', size: 8, mode: CFG.recipe === 'halftone-print' ? 2 : 0, ink: INKC, paper: PAPER, blend: CFG.recipe === 'halftone-print' ? 1 : .5 });
  if ((T.scan || 0) > .2 || CFG.recipe === 'terminal') passes.push({ pass: 'crt', curvature: .05, scan: .2 });
  passes.push({ pass: 'grain', amount: Math.max(.05, T.grain || .08) }); passes.push({ pass: 'vignette', amount: Math.max(.25, T.vignette || .4) });
  fx.apply(c, passes, t, 30); ctx.drawImage(fx.canvas, 0, 0);
}
function render(t) {
  const o = (extra) => Object.assign({ w: W, h: H, pal: P.art, seed: CFG.art_seed, loop: DUR }, extra || {});
  const A = (n, extra) => Art.draw(ctx, n, t, o(extra));
  const r = CFG.recipe;
  if (r === 'world-and-field' || r === 'shader-solo') { bg.draw(CFG.shader, t, { seed: CFG.shader_seed, loopPeriod: DUR, palette: P.bg3d, grain: .02, vig: .2 }); ctx.drawImage(bg.canvas, 0, 0, W, H); }
  else if (CFG.ground === 'gradientBlobs' && r !== 'terminal' && r !== 'orbit-system') A('gradientBlobs', { count: 4 });
  else { ctx.fillStyle = (r === 'orbit-system') ? P.art[4] : P.art[0]; ctx.fillRect(0, 0, W, H); }
  if (r === 'world-and-field') { A(CFG.field, { bg: false, alpha: CFG.fieldAlpha }); wspan.style.opacity = 1; Type.apply(TY, CFG.style, t % DUR, { t0: .3, dur: .8, stagger: .06, exit: { t1: 5.2, style: 'fadeBlur', dur: .5 } }); }
  if (r === 'pure-generative') { A(CFG.field, { bg: false, alpha: CFG.fieldAlpha }); A(CFG.focal, { bg: false }); }
  if (r === 'art-poster') {
    A(CFG.field, { bg: false, alpha: CFG.fieldAlpha });
    tc.clearRect(0, 0, W, H); tc.fillStyle = '#fff'; tc.textAlign = 'center'; tc.textBaseline = 'middle'; tc.font = `900 ${Math.min(size * 1.25, W * .9 / (nW * .66))}px '${CFG.font}', 'Archivo', sans-serif`; tc.fillText(CFG.caseUpper ? CFG.word : CFG.word[0] + CFG.word.slice(1).toLowerCase(), W / 2, H / 2);
    lc.clearRect(0, 0, W, H); Art.draw(lc, CFG.clipArt, t, o({ pal: [P.art[4], P.art[0], P.art[1], P.art[2], P.art[3]], bg: true })); lc.globalCompositeOperation = 'destination-in'; lc.drawImage(txt, 0, 0); lc.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = Lab.ease.outCubic(Math.min(1, (t % DUR) / .8)); ctx.drawImage(lay, 0, 0); ctx.globalAlpha = 1; A(CFG.focal, { x: 0, y: H * .72, w: W, h: H * .28, bg: false });
  }
  if (r === 'type-poster') { A(CFG.field, { bg: false, alpha: .16 }); wspan.style.opacity = 1; Type.apply(TY, CFG.style, t % DUR, { t0: .2, dur: .9, stagger: .07, exit: { t1: 5.1, style: 'fade', dur: .6 } }); A(CFG.focal, { x: W * .6, y: H * .62, w: W * .36, h: H * .32, bg: false }); }
  if (r === 'halftone-print') { ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H); const hp = [PAPER, P.art[1], P.art[2], P.art[3], INKC]; A(CFG.field, { bg: false, alpha: .3, pal: hp }); A(CFG.focal, { bg: false, pal: hp }); }
  if (r === 'terminal') { A('glyphField', { alpha: .8, font: "'JetBrains Mono', monospace" }); A('plexus', { bg: false, nodes: 40 }); wspan.style.opacity = 1; Type.apply(TY, 'scramble', t % DUR, { t0: .4, dur: 1, stagger: .05 }); }
  if (r === 'orbit-system') { A('orbits', { pal: [P.art[4], P.art[0], P.art[1], P.art[2], P.art[0]], bg: true, rings: 8 }); A('rings', { bg: false, origins: 1, pal: [P.art[4], P.art[1], P.art[2], P.art[3], P.art[0]], alpha: .5, count: 10 }); wspan.style.opacity = 1; wspan.style.color = P.art[0]; Type.apply(TY, CFG.style, t % DUR, { t0: .3, dur: .8, stagger: .06 }); }
  finish(t);
}
Lab.init({ w: W, h: H, duration: DUR, fps: 30, bg: '#000', loop: true, render });
</script></body></html>
'''

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--project"); ap.add_argument("--n", type=int, default=6); ap.add_argument("--seed", type=int, default=1); ap.add_argument("--recipe"); ap.add_argument("--size", default="1080x1080"); ap.add_argument("--list", action="store_true"); ap.add_argument("--repeat")
    a = ap.parse_args()
    if a.list:
        for k, v in RECIPES.items(): print(f"{k:16} {v}")
        print("\npresets:", ", ".join(PRESETS)); print("art generators:", len(ART), " shaders:", len(SHADERS)); return
    if not a.project: sys.exit("--project required")
    W, H = (int(x) for x in a.size.lower().split("x")); recs = list(RECIPES); rnd = random.Random(a.seed); out_root = os.path.join(a.project, "play"); os.makedirs(out_root, exist_ok=True)
    existing = len(glob.glob(os.path.join(out_root, "p*")))
    for i in range(a.n):
        seed = a.seed * 100 + i
        if a.repeat:
            base = json.load(open(a.repeat)); cfg, dna = build(base["recipe"], seed, [W, H]); cfg["recipe"] = base["recipe"]
        else:
            rec = a.recipe or recs[(rnd.randint(0, 99) + i) % len(recs)]; cfg, dna = build(rec, seed, [W, H])
        d = os.path.join(out_root, f"p{existing + i + 1:02d}"); os.makedirs(d, exist_ok=True)
        html = TEMPLATE.replace("__CFG__", json.dumps(cfg)).replace("__W__", str(W)).replace("__H__", str(H)).replace("__TITLE__", f"play {cfg['recipe']} {cfg['preset']}")
        open(os.path.join(d, "scene.html"), "w").write(html); json.dump(dict(cfg, dna=dna), open(os.path.join(d, "piece.json"), "w"), indent=1)
        print(f"{d}: {cfg['recipe']:16} preset={cfg['preset']:26} focal={cfg['focal']:12} field={cfg['field']:12} shader={cfg['shader']:20} type={cfg['font']}/{cfg['style']} word={cfg['word']}")

if __name__ == "__main__": main()
