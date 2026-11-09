# Composing artwork into a piece that has a point of view

A single generator is a texture. A *composition* has: **ground → field → focal → accent → finish**.

## The 5-layer stack
1. **Ground:** flat colour or `gradientBlobs` (soft). Decides mood in one glance.
2. **Field:** one structured generator at low alpha (`contours`, `warpGrid`, `dotGrid`, `moire`) → gives scale and rhythm.
3. **Focal:** the thing the eye lands on: headline, hero object, or ONE bold generator (`mandala`, `lissajous`, `radialBars`, `spiral`, `rings`).
4. **Accent:** 1–3 small contrasting marks (`orbits` dots, `memphis`, `lightning` on a beat, `confetti` burst).
5. **Finish (fx):** `grain` + `vignette`, optionally `bloom`/`chromatic`/`halftone` (fx.js). Without a finish, procedural art looks like a screensaver.

Rule: **max 2 "busy" layers** (flowField, voronoi, plexus, memphis, glyphField). Everything else calm.

## Techniques
- **Art inside type** (see `examples/art-poster.html`): draw the generator on an offscreen canvas, `globalCompositeOperation='destination-in'` with the text canvas, composite on top. Works with any shape (circle, blob, icon).
- **Art as mask for a reveal:** reveal generator B through the shape of generator A (`blobs` as a mask) while A is expanding.
- **Windowed art:** pass `x,y,w,h` to place a generator in a card/phone/panel; the clip is built in.
- **Layer blending:** `ctx.globalCompositeOperation = 'screen' | 'multiply' | 'overlay' | 'lighter'` before `Art.draw(…, {bg:false})`. `screen` for light-on-dark glow, `multiply` for ink on paper.
- **Echo/trails:** draw the same generator at `t, t-0.05, t-0.10` with decreasing alpha (pure function of t; no frame buffer).
- **Data-driven art:** `radialBars` takes `levels:(u,t)=>0..1`; feed it your own envelope (e.g. from `Lab.adsr`) so it hits on the beats of `Lab.beat`.
- **Beat reactivity:** multiply generator `speed`/`alpha`/size by `1 + 0.6*Lab.hit(t, tBeat, 0.25)` (see lab.js hit/bump). Emit `Lab.ev(tBeat,'tick')` so sound hits the same frame.
- **Palette-swap per scene:** same generator, different `pal` and `seed` = a different scene (but don't overuse; consistent grammar is what makes a video).

## Pairings that work (and why)
| Mood | Ground | Field | Focal | Accent |
|---|---|---|---|---|
| Editorial calm | paper flat | `contours` ink 20% | big serif | `scribble` underline |
| Techno night | near-black | `warpGrid` 15% | `lissajous` or `radialBars` | `lightning` on beats |
| Pop poster | saturated flat | `dotGrid` square | giant type | `memphis` |
| Dreamy product | `gradientBlobs` | `moire` 10% | 3D icon (three-kit) | `bubbles` |
| Data/AI | dark navy | `hexPulse` | `plexus` | `glyphField` corners |
| Craft/analog | cream | `stripesWarp` pale | `brushStrokes` | `truchet` frame |

## Making a NEW generator (when none fit)
Signature `(ctx, t, o, H) => void` with `H.ph` (loop phase), `H.ln(x,y,k)` (looping noise), `H.rng(k)` (seeded), `H.col(i)`, `H.a(color,alpha)`, `H.lw` (line weight). Rules: no `Math.random`/`Date`; every animated value from `H.ph`/`t`; random choices from `H.rng` **outside** the time dependence; sizes relative to `o.w/o.h`; register with `add(name, mood, use, params, fn)`. Test in `examples/art-gallery.html` at `t=0` and `t=loop` (must be identical).

## Mutation prompts (to get something nobody has seen)
Take any generator and change ONE structural thing: swap the coordinate system (cartesian → polar), replace the noise by a sum of sines, quantise to steps, mirror it N-fold, feed output into itself (domain warp), or invert what is drawn (lines where there were gaps). Name the result and add it to the catalog.
