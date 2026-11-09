---
name: motion-canvas-artwork
description: Generative 2D motion artwork on Canvas - 34 deterministic generators (flow fields, contour maps, joy-division waves, warped grids, Lissajous, mandalas, truchet, hex pulse, voronoi, plexus networks, memphis shapes, confetti, brush strokes, gradient blobs...), a 5-layer composition method, art-inside-type and beat-reactive recipes. Use for animated backgrounds, posters, motion canvases, "artwork", abstract/loopable visuals, texture layers, or when a scene feels empty or generic and no images are available.
---

# motion-canvas-artwork — procedural art with intent

All generators are in `runtime/art.js` (global `Art`). Pure functions of `(name, t, options)`: no images, no clock, no `Math.random`; with `loop: seconds` they repeat **exactly**.

## 60-second workflow
1. Read `dna.json` → take `palette` and `texture`. `const pal = Art.palette(dna.palette)` (or hand-write 5 colours: `[bg, ink1, ink2, ink3, highlight]`).
2. Choose a **mood row** in `reference/composition-recipes.md` (pairings table) and the 5 layers (ground, field, focal, accent, finish).
3. Look up generators in `reference/generator-catalog.md` (mood/use/params). Pick the focal one first.
4. Build the scene; **render stills** at 3 times and look. Remove one busy layer if it feels noisy.
5. Add a finish: `FX` grain + vignette (always), bloom for neon.
6. If nothing fits, write a new generator (recipe + mutation prompts in the same file).

## API
```html
<script src="lab/lab.js"></script><script src="lab/art.js"></script>
<script>
const pal = ['#0e0a1f','#ff5d8f','#ffb86b','#6be3ff','#fff6ea'];
function render(t){
  Art.draw(ctx,'gradientBlobs',t,{w:W,h:H,pal,seed:5,loop:6});                     // ground
  Art.draw(ctx,'contours',t,{w:W,h:H,pal,bg:false,alpha:.22,seed:9,loop:6});        // field (bg:false = transparent)
  Art.draw(ctx,'orbits',t,{x:0,y:H*.7,w:W,h:H*.3,pal,bg:false,loop:6});             // windowed accent
}
</script>
```
Common options: `x,y,w,h` (clip rect), `pal`, `bg:false`, `seed`, `loop`, `speed`, `alpha`, `weight` (line width), plus per-generator params. `Art.list()`, `Art.meta`, `Art.describe(name)`.

## Rules that stop "same soul"
- **Seed and generator choice come from the DNA**, not habit: different video → different focal generator (ledger records `art:<name>`).
- Never use a generator with its default palette; never two focal generators in one frame.
- Use `loop` on every background so the file loops cleanly; confetti/lightning are event-driven (`t0`, `Lab.ev`).
- Keep the headline area calm: lower alpha/density behind text or use `destination-out` to carve a hole.
- Performance (software GL render): `flowField` ≤ 900 trails at 1080p, `voronoi` block ≥ 6, `contours` cell ≥ 12. Heavy generators: max 2 per frame.
- Always finish with grain (0.08–0.15) so it feels printed, not rendered.

## Files
`runtime/art.js` · `reference/{generator-catalog,composition-recipes}.md` · `examples/{art-gallery.html,art-poster.html}` (poster = art inside headline, loops 6 s)
