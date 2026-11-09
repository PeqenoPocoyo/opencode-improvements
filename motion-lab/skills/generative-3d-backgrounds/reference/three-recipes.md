# three.js recipes (three-kit.mjs)

```js
import * as THREE from './lab/vendor/three.module.min.js';
import { Stage, clay, glass, metal, plastic, emissive, roundedBox, iconFromPath, ICONS, ring, scatter } from './lab/three-kit.mjs';
const st = new Stage(THREE, { w:1080, h:1920, bg:'#d9cdb8', fov:30, env:{ top:'#fff7ea', mid:'#cdbfa6', bottom:'#6b5b49' } });
st.cam([0,1.6,14],[0,.1,0]);
```
Module scripts load after the page; render inside `Lab.init({render})` — it is called after load, so the module must finish import first (the example shows the pattern: `<script type="module">` that calls `Lab.init`).

## Scale rule
With `fov 30` at distance D the frame height is ≈ `0.536·D` world units. Objects of size 1.6 want D ≈ 14 for a 3-object composition; D ≈ 7 for a single hero.

## Looks
| Look | Material | Lighting/env | Notes |
|---|---|---|---|
| Clay | `clay(T,color,.7)` | warm env (`top` cream, `bottom` brown), key from upper-left | roundedBox r ≥ .2, soft floor plane same colour family |
| Glass icon | `glass(T,'#9fd0ff')` over a contrasting colour bg | bright softbox strips in env | `iconFromPath` bevel .08–.12; put coloured light shapes behind to be refracted |
| Chrome/metal | `metal(T,'#d8dbe4',.18)` | high-contrast env (dark bottom, white strips) | reflections need contrast in the env, otherwise grey |
| Glossy plastic | `plastic(T,'#ff6fa3',.25)` | any | clearcoat gives the candy look |
| Emissive/neon | `emissive(T,'#ff4d2e',2.2)` | dark bg + FX `bloom` | bloom after render (fx.js) |

## Animation patterns (pure functions of t)
- **Idle float:** `y = y0 + .12·sin(2π t/4)`, rotation `±.4` with a different period (4 & 2 → loops in 4 s).
- **Hero entrance:** scale `0→1` with `Lab.spring`, rotation from −.8 rad settling with `Lab.curves.settle`.
- **Orbiting cluster:** items from `scatter(n, seed)` rotating around the hero at different speeds/radii.
- **Camera dolly:** interpolate `st.cam(pos,target)` with `Lab.curves.glide`; add `Lab.handheld` micro-shake in 3D by offsetting pos by ±.02.
- **Depth of field fake:** render at 1× then FX `tiltshift`/`blur` pass masked by depth band.

## Compositing with a shader background
`new Stage(THREE,{transparent:true,w,h})` → draw `bg.canvas` first, `st.canvas` on top. Add a soft contact shadow (blurred dark ellipse in 2D) under objects. Finish with FX (`bloom`, `grain`).

## Pitfalls
- Flat-shaded bevels (stair-step bands): use `roundedBox` (smooth) and `iconFromPath` (creased normals) from the kit — never `computeVertexNormals()` on ExtrudeGeometry.
- Transmission (glass) is expensive in software GL: keep one or two glass meshes per frame.
- Shadows: avoid shadow maps; use fake blob shadows.
- Don't mix `antialias:true` in SwiftShader (slow); render at `scale:1.5` and downscale if you need smoother edges.
