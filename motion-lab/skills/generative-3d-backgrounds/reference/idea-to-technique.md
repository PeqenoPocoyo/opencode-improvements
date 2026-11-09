# From an idea (or a reference video) to a technique

Look at a reference and ask **what is physically happening in the picture?** then pick the cheapest technique that fakes it.

| You see / want | Technique | Start from |
|---|---|---|
| Glowing horizon, reflective floor, neon night | 2D layered shader, gradient + mirrored sky | `neon-gradient-reflect`, `grid-horizon` |
| Soft colour fields (premium SaaS) | domain-warped gradient noise | `aurora-mesh`, `plasma-silk` |
| Liquid metal / oil / marble | fbm-warped normal → fake environment lookup | `liquid-chrome`, `ink-in-water` |
| Clay/plaster studio set | radial light falloff on a seamless backdrop + soft floor shadow | `clay-studio`, `studio-radial` |
| Tunnel, hyperspace, "travelling" | polar coordinates + depth = 1/r | `tunnel-rings`, `starfield-warp`, `ray-hex-tunnel` |
| Terrain, topographic map, data-land | height field, iso-lines or ridged layers | `topographic-lines`, `layered-mountains`, `ray-dunes` |
| Water, pool, caustics | voronoi/worley edges + refraction offset | `caustics-pool`, `ray-ocean` |
| Bokeh, depth-of-field lights | discs with size ∝ depth, additive | `bokeh-lights` |
| Print / halftone poster | dot grid whose radius = luminance of a field | `halftone-field` |
| Isometric toys, cube worlds | rhombus tiling with 3 face tints | `isometric-cubes` |
| Real 3D scene (cities, glass spheres, crystals) | raymarched SDF, camera flythrough | `ray-neon-city`, `ray-glass-spheres`, `ray-crystal-field` |
| Soft blobs / gel / goo | metaballs: sum of falloffs, threshold | `metaball-gel`, `ray-gel-orbit` |
| Globe, data viz sphere | sphere SDF + lat/long dot grid | `dotted-globe` |
| God rays, light shafts | radial streak accumulation from a source | `light-rays` |
| Hero icon/object with glass, clay, metal | three.js mesh + env lighting | `three-kit` |
| Paper / collage / texture | not shader: canvas 2D (see collage-paper-texture skill) | — |

## 6 questions that make any background feel designed
1. **Where is the light?** One dominant source direction; everything shades from it.
2. **What is the depth cue?** Pick one: fog, scale, blur, parallax, overlap, atmospheric colour shift.
3. **What is the motion?** One slow global drift + one small fast detail (dust/sparkle). Never everything moving at the same speed.
4. **What is the focal gap?** Leave a calm area where the headline will sit.
5. **What is the palette story?** one hue + neutral, or complementary pair — decided from `dna.json`.
6. **What is the texture?** Add grain 0.03–0.06 and a gentle vignette to remove the "CG-clean" look.

## From a reference video frame (no image files allowed in the project)
Write 5 lines: (1) dominant colours as hex, (2) light direction, (3) 3 layers front→back, (4) motion of each layer, (5) material words (matte, glossy, translucent, metallic). Then pick the catalog entry closest to the 3 layers and modify; if two or more layers differ, compose: shader A as backdrop + three.js objects + FX chain.

## Mixing (how to get a world nobody has seen)
- **Shader × shader:** draw two shaders into two canvases, blend with a mask (radial or luminance); e.g. `topographic-lines` lines over `aurora-mesh` colour.
- **Shader + 2D layer:** add `art.js`-style generative layers on top (particles, rings, lines).
- **Shader + FX:** `halftonePoster`, `riso`, `vhs` chains turn a clean shader into a style.
- **Swap the palette to an unexpected role:** a night shader with a warm pale palette = new mood.
