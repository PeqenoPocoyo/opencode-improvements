---
name: generative-3d-backgrounds
description: Builds 3D-looking backgrounds, worlds and 3D objects with ZERO images - 28 tested procedural WebGL shaders (neon horizon, liquid chrome, raymarched dunes/ocean/neon city/crystal field, tunnels, bokeh, caustics, halftone, aurora...), a Bg3D engine with palette/loop/camera helpers, a three.js kit (clay, glass, metal, extruded icons, studio lighting), and the method to invent NEW shaders from a mood or reference. Use whenever a video needs a background, environment, 3D icon, product-hero render, depth, or the user says "fundo 3D", "sem imagem", "background procedural", "estilo clay/glass/neon", or backgrounds look flat/repeated.
---

# generative-3d-backgrounds — worlds from math, not from files

No stock images, no downloads. Every pixel is a pure function of `(shader, t, params)`, so it obeys the seek(t) purity contract (CONVENTIONS.md).

## Decide in this order
1. **Idea → technique** (`reference/idea-to-technique.md`): say the world in one sentence ("a calm dusk ocean", "a glass folder floating in a lit studio") and map it to a technique family: *2D layered shader* (cheap, great), *raymarched SDF* (real depth, expensive), *three.js meshes* (hero objects, glass/clay/metal), *canvas-2D fake 3D* (isometric, parallax).
2. **Pick from the catalog or invent.** `reference/shader-catalog.md` has 28 entries with mood/use/params. **Do not use the default palette:** take colours from `dna.json` (`palette`) → `palette: [P0..P4]` (see roles below). If nothing fits, write a new shader (`reference/glsl-cookbook.md`) — copy the nearest one and change structure, not just colours.
3. **Place text/objects in the safe zone** (shader keeps the focal third calm; headlines in the upper third for portrait).
4. **Loop it** if the video loops: `loopPeriod` = loop length (seconds).
5. **Render a still and LOOK** before building scenes on top (`--at 1.5`).

## Bg3D in 10 lines
```html
<script src="lab/lab.js"></script><script src="lab/bg3d.js"></script><script src="lab/shaders.js"></script><script src="lab/shaders2.js"></script><script src="lab/shaders3.js"></script>
<script>
const bg = Bg3D.create(540, 960);                        // render small, upscale (ray-* shaders are costly in software GL)
function render(t){
  bg.draw('grid-horizon', t, { seed: 7, loopPeriod: 6, speed: 1, grain: .04, vig: .25,
          palette: ['#07030f','#2a0a4a','#ff2d95','#ffb3d9','#fff1f8'] });   // P0 bg … P4 highlight
  ctx.drawImage(bg.canvas, 0, 0, W, H);                  // then draw text/UI on top
}
</script>
```
Params: `seed` (different world each seed), `speed`, `loopPeriod`, `loopFade`, `intensity`, `vig`, `grain`, `palette`, `camera:{pos,target,fov,roll}`, plus each shader's own params (catalog). Camera helpers: `Bg3D.cam.between(t,t0,t1,a,b,ease)`, `.orbit(t,{center,radius,height,t0,t1})`, `.drift(t,{amp,period,seed})` + `.withDrift`. `Bg3D.list()`, `Bg3D.describe(name)`, `Bg3D.register(name, glsl)`.

## Palette roles (every shader)
P0 deepest background · P1 secondary background · P2 main accent · P3 second accent / light · P4 highlight. A one-hue palette (all five from the same hue, varying lightness) reads as "designed"; two hues max; keep P4 near-white or near-black tinted by the hue.

## three.js (hero objects)
`runtime/three-kit.mjs` + vendored three r160: `Stage` (renderer, studio env, 3-light rig), materials `clay/glass/metal/plastic/emissive`, geometry `roundedBox`, `iconFromPath` + `ICONS` (bolt, heart, star, check, play, chat), `ring`, `scatter` (seeded), `creased` (smooth normals). Recipes and lighting: `reference/three-recipes.md`. Example: `examples/three-clay.html`. Layer a Bg3D shader behind a transparent-background Stage render for objects-in-world shots (`new Stage(THREE,{transparent:true})`).

## Rules
- Objects' transforms are pure functions of `t`; never `Math.random`/`Date`/`requestAnimationFrame`; `Stage.render()` after setting all transforms.
- Ray-* shaders: ≤540×960 (or half the final size), scale up; budget one raymarched layer per scene.
- Never ship a shader unseen: render stills at t=0.5, 2.5 and one palette swap. If a still looks muddy, raise contrast (P0 darker, P4 brighter) before adding effects.
- Compose with FX passes (`bloom`, `grain`, `vignette`, `chromatic` from the `fx` skill) rather than baking everything into the shader.
- Variety: a video uses 1 world + at most 1 contrast world; consecutive videos must not reuse the same shader+palette (ledger in `.motion/style-history.json` stores `bg3d:<name>`).

## Files
`runtime/{bg3d.js,shaders.js,shaders2.js,shaders3.js,three-kit.mjs,vendor/}` · `reference/{idea-to-technique,glsl-cookbook,three-recipes,shader-catalog}.md` · `examples/{shader-gallery.html,three-clay.html}`
