---
name: collage-paper-texture
description: Paper-cutout / scrapbook / stop-motion collage videos with NO image files - torn and scissor-cut shapes, paper fibre, tape, stamps, ransom-note type, halftone and newsprint fills, boil jitter, paper-slap timing. Use when the DNA/brief says collage, craft, zine, analog, handmade, editorial-poster, "paper", "cutout", "scrapbook".
---

# collage-paper-texture — analog warmth from pure code

Runtime: `runtime/collage.js` → global `Collage` (needs `lab.js`; optional `art.js` for art-filled cutouts, `kinetic-typography/fonts` for type).
Look first at `examples/collage-gallery.html` (every shape, fill, decoration) and `examples/collage-film.html` (a 12 s vertical film).

## Why collage reads as "handmade" (the 6 ingredients — use ALL, otherwise it looks like flat vector)
1. **Edges are imperfect:** torn edge with a pale fibre rim (`edge:'torn'`) or scissor edge with few straight vertices (`edge:'scissors'`). Mix both in one scene.
2. **Paper has grain:** every fill gets a multiplied fibre tile. Background is paper too (`Collage.paperBg`).
3. **Thickness shadow:** a soft shadow opposite the light. Lifted paper = bigger, softer shadow; landed paper = tight. (`arrival()` does this automatically.)
4. **Boil:** edges and positions change on 3 variants at 8 fps ("on 3s"). Keeps pieces alive when nothing moves. `boil:false` for text you must read.
5. **Things holding paper:** tape, staples, pins, stains, creases, stamps. A collage with no fasteners looks like stickers.
6. **Mixed material:** at least one pattern (grid/lined/dots/halftone/news/kraft), one flat colour, one art-filled (`fill:{art:'flowField',...}`).

## Fast path (data-driven)
```js
const P = [ {shape:'strip', x:540,y:520,w:900,h:210, fill:'#171310', edge:'scissors', rot:-4, t0:1.2, anim:'slap',
             text:'MADE', font:'900 190px "Anton"', ink:'#f3ecd9', tape:'both'}, ... ];
Collage.register(P);                               // Lab.ev for each landing: paper-slap / whoosh / pop / tape / stamp  -> sound-design-pro
function render(t){ Collage.draw(ctx, t, P, {paper:'#e9dfc8', boilFps:8}); }
Lab.init({w:1080,h:1920,duration:12,fps:30,loop:true,render});
```
`anim`: `slap` (scale-down landing, shadow tightens) · `pop` (overshoot) · `drop` (falls from above) · `slideL/R/U/D` (whoosh) · `peel` (rotates in) · `none`. Exit with `t1` + `out:'fade'|'shrink'|'slideL'…`. `z` = draw order.

## Rules for weak models (non-negotiable)
- **Loop exactness:** `duration * boilFps` must be a multiple of 3 (6 s @8 fps OK, 12 s @8 OK, 10 s @6 OK). Otherwise the loop seam jumps.
- **Text on busy fills is unreadable** (see stripes/halftone in the gallery). Put text on flat or lightly patterned paper, or set `fill.bias:-.5` so the halftone dots are small.
- **No more than ~9 pieces on screen** in a 1080x1920 frame; at 12+ it turns to noise. Let old pieces exit (`t1`).
- **Hierarchy:** one hero piece (largest, highest contrast, arrives first or last), 3–4 supporting, the rest tiny fasteners.
- **Rotation:** every piece gets a rotation between −8° and 8° (not 0, not > 15° except confetti). Headline strips alternate −4° / +3°.
- **Palette:** 4–5 flat colours + cream + ink from `dna.json`. Never pure white or pure black paper (use `#f3ecd9` / `#171310`).
- **Light direction** is one vector for the whole scene (`opts.light`, default top-left). Don't mix.
- **Timing:** land pieces on beats (`BEAT*k`); `slap` duration .3–.4 s; stagger headline strips by one beat; leave 0.3 s after the last landing before the next beat so the eye can read.
- Lots of full-frame paper multiply is slow-ish (≈20 ms/frame at 1080x1920). Don't add a second full-frame multiply.

## Sound mapping (already registered by `Collage.register`)
`slap`→`paper-slap` · `pop`→`pop` · `drop`→`paper-slap` · `peel`→`paper-rip` · `slide*`→`whoosh` · `tape`→`tape` · `stamp`→`stamp`. Override with `Collage.register(P,{slap:'impact'})`. Pass `hit:0..1` on a piece for custom intensity; `silent:true` to skip.

## Decorations (all pure functions)
`Collage.tape(ctx,x,y,w,h,rotDeg,color,seed)` · `staple(ctx,x,y,rot)` · `pin(ctx,x,y,color)` · `stain(ctx,x,y,r,color,seed)` (coffee ring) · `crease(ctx,x1,y1,x2,y2)` · `stitch(ctx,pts,{color,dash})` · `stamp(ctx,text,x,y,{size,rot,color})` · `ransom(ctx,text,x,y,{size,stagger,t,t0})` (each letter its own chip) · `paperBg` · `paperTile(seed)` · `stepTime(t,fps)`.

## Recipes → `reference/recipes.md`
Poster reveal · zine page-turn series · ransom headline · map-with-pins explainer · sticker-sheet end card · stop-motion product tour · "cut-out character" built from shapes.

## Techniques & why → `reference/technique.md`
## Mix with other skills
Art-filled cutouts (`motion-canvas-artwork`), kinetic type on a strip (`kinetic-typography` — render letters to a canvas and use `deco`), FX grain/bloom (`scene-runtime/fx.js`), transitions between collage scenes: `Trans` "paperTear"-style wipes (`transitions-projections`).
## QA
Contact sheet at 4 times; check: any piece clipped by frame edge unintentionally? text legible (contrast ≥ 4:1)? shadow direction consistent? two pieces identical in colour+shape? fingerprint vs previous video.
