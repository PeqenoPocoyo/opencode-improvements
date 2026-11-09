---
name: transitions-projections
description: Scene transitions and projection mapping for scene-runtime videos - 43 tested GLSL transitions (wipes, irises, whip pans, zoom-throughs, pseudo-3D cube/flip/peel, dissolves, glitch, light leaks), non-shader cuts (match cut, object carry, J/L cut), carried transitions, and perspective warping of canvases/DOM onto quads (phone, screen, card, billboard) with matrix3d or WebGL. Use whenever one scene must change into another, when a flat UI/artwork must be tilted into 3D perspective, when transitions feel repetitive, or the user mentions transições, projeção, corte, whip, zoom through, tela inclinada, mockup.
---

# transitions-projections — a transition is a sentence, not a decoration

**Rule 0: a cut needs a REASON.** Before choosing, finish this sentence: "Scene B follows A because ___, so the cut should feel ___." Reason → transition:

| Reason (what the cut says) | Use |
|---|---|
| Same thing, closer/further | match cut, `zoomThrough`, `zoomOutIn` |
| Time passes / progress | `wipeRadial`, `wipeLinear`, `lumaWipe` |
| New chapter / breath | `dipToColor` (accent, not black), `shapeFlood`, `irisCircle` on the hero object |
| Energy spike / beat drop | `whiteFlash` (2–4 frames), hard cut on impact, `glitchSwap`, `whipPan` |
| Moving through space | `whipPan`, `slidePush`, `parallaxSlide`, `perspectiveTilt`, `cubeRotate` |
| Physical/craft world (paper, print, ink) | `paperTear`, `inkBleed`, `brushWipe`, `halftoneDissolve`, `pagePeel` |
| Digital/tech/error | `glitchSwap`, `dataMoshLite`, `vhsRewind`, `scanlineWipe`, `hexGrid`, `pixelDissolve` |
| Warm / cinematic / memory | `lightLeakWipe`, `filmBurn`, `glassRefract`, `rippleDissolve` |
| Dream, kaleidoscope, trip | `kaleidoscope`, `liquidWarp`, `radialBlurSpin` |

Full table with defaults/durations/sound: `reference/catalog.md`. Live look: `examples/trans-demo.html` (sheet of all 43 at progress `?p=0.5`).

## Hard rules (these kill the "same soul")
1. **Max 3 distinct shader transitions per video, and the DNA's `transitions` list decides which.** Everything else is hard cut / match cut / carried element. Use the same transition for the same *kind* of change (consistency = grammar).
2. **Never use `crossfade` as the default.** It means "I had no idea".
3. **Duration in frames, not seconds** (catalog column `frames@30`; scale by fps/30). Fast transitions: 8–14 frames. Never longer than 24 frames unless it is the hero moment.
4. **Ease the progress yourself:** `p = Lab.ease[Trans.ease(name)](localT)`; `whipPan` uses the `whip` curve; flashes use `linear`.
5. **Both scenes must be alive during the transition:** render scene A at its own time and scene B pre-rolled (starts 6–10 frames before the cut, already moving). A frozen B looks like a slideshow.
6. **Anchor the sound:** emit `Lab.ev(tCut, 'whoosh'|'impact'|…)` at the *visual peak* (mid-transition, not the start). `whip` and `slide*` get a `whoosh` that ends at the cut; `whiteFlash`/`paperTear` get an `impact`/`paper-rip` exactly at the flash frame. Column **sound** gives the default.
7. **Origin on the object:** for `irisCircle`, `irisOut`, `zoomThrough`, `shapeFlood`, `rippleDissolve` set `cx, cy` to the focal object's position (0..1) — a centre-screen default is the amateur tell.
8. **No transition on top of a transition:** if the scenes already move a lot (camera shake, whip), use a hard cut.

## Wiring (copy/paste)
```html
<script src="lab/lab.js"></script><script src="lab/transitions.js"></script>
<script>
const W=1080,H=1920, tr=Trans.create(W,H);
const cA=document.createElement('canvas'), cB=document.createElement('canvas'); cA.width=cB.width=W; cA.height=cB.height=H;
const out=document.getElementById('c').getContext('2d');
const CUT={t:3.0, dur:12/30, name:'whipPan', params:{angle:0}};
function renderScene(ctx,sceneFn,t){ sceneFn(ctx,t); }   // your scene functions draw into any 2D context
function render(t){
  const k=(t-CUT.t)/CUT.dur;
  if(k<=0){ sceneA(cA.getContext('2d'),t); out.drawImage(cA,0,0); return; }
  if(k>=1){ sceneB(cB.getContext('2d'),t-CUT.t); out.drawImage(cB,0,0); return; }
  sceneA(cA.getContext('2d'),t);            // A keeps playing under the transition
  sceneB(cB.getContext('2d'),t-CUT.t);      // B starts at local time 0 at the transition start (or pre-roll with +offset)
  tr.render(cA,cB,Lab.ease[Trans.ease(CUT.name)](k),CUT.name,CUT.params); out.drawImage(tr.canvas,0,0);
}
Lab.ev(CUT.t+CUT.dur*.5,'whoosh');
</script>
```
DOM-based scenes: rasterise first (draw the scene to a canvas) or keep the DOM scene and use a **CSS-only** transition (clip-path, transform) — do not mix a shader transition with live DOM unless the DOM is drawn into a canvas.

## Carried transitions (the pro ones)
- **Object carry:** the card/cursor/logo has the same position and scale on the last frame of A and the first of B; only the background changes (use `irisCircle` centred on it).
- **Zoom-through match:** at the end of A zoom towards a feature (a letter's counter, a screen, a ring); B starts from a tight crop of an equivalent feature and pulls back.
- **Colour hand-off:** last colour on screen in A = first background colour in B; the cut is invisible except for the shape change.
- **Rhythm cut:** put the cut on a beat of the music/sfx grid (`Lab.beat`), not "after 2 seconds".

## Projection mapping (flat → perspective)
See `reference/projection-mapping.md`: `Trans.matrix3dFromQuad(w,h,quad)` (DOM element → any quad), `Trans.warp(W,H).draw(canvas,quad,bg)` (canvas → quad in WebGL), device mockups, floor reflection, projector beam, UI-on-3D-plane, animating quads with springs. Demo: `examples/projection-demo.html`.

## Anti-patterns
- Same transition at every cut. Slow crossfades between energetic scenes. Transition that starts before the previous scene finished its own hit (steps on the beat). Spinning/ripple everywhere (reserve for ONE hero moment). Flash >4 frames. Black dips by default. Transition with the sound at its start instead of its peak.

## Verify
Render stills at progress 0.25/0.5/0.75: `node scripts/render.mjs scene.html out/s.png --stills 2.9,3.05,3.2` and LOOK at them (A and B both recognisable at 0.25/0.75; no black frames unless the transition is meant to dip).
