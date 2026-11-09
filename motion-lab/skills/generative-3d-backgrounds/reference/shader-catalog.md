# Bg3D shader catalog (generated from runtime/shaders*.js)

`bg.draw(name, t, {seed, palette:[5 hex], speed, intensity, vig, grain, <params>})`. Palette roles: P0 deepest bg · P1 secondary bg · P2 main accent · P3 second accent/light · P4 highlight. Ray-* shaders are expensive: render at ≤540x960 and upscale.

## `neon-gradient-reflect`
- **mood:** neon monochrome, cinematic, night, sci-fi, hopeful (single hue + black)
- **use:** One-hue world behind silhouettes / glowing numerals: dark-to-bright vertical gradient, a glossy floor that mirrors it, drifting haze and dust. Pick ONE hue (palette P1..P3 all from the same hue).
- **default palette:** `#010503 #04281a #0fbf6b #6dffb0 #eafff3`
- **params:** `horizon`=-0.12 (horizon height (short-side units, y up)); `haze`=0.6 (drifting haze amount); `streak`=0.6 (horizontal ripple streaks in the floor reflection); `dust`=0.7 (dust motes); `sun`=0.35 (bright core at the horizon)

## `aurora-mesh`
- **mood:** soft, premium, calm, modern product / SaaS, dreamy
- **use:** Backdrop behind titles, UI cards and product shots. Slow breathing colour fields, never busy. Safe default for "a nice gradient background".
- **default palette:** `#0a0d1f #3a2d9c #ff5fa8 #ffb36b #7fe4ff`
- **params:** `warp`=0.7 (liquid warp of the colour field (0 clean blobs .. 1.5 very liquid)); `blobs`=5 (number of colour blobs (3..6)); `soft`=1.0 (blob size/softness (0.6 tight .. 2 diffuse)); `sheen`=0.5 (silky highlight ridges (0 none))

## `clay-studio`
- **mood:** warm, tactile, editorial, clay render, calm, monochrome
- **use:** Backdrop for clay / monochrome editorial scenes (cream paper stage), under big grotesk headings. uObjects adds soft clay primitives with real shadows; uShadowA/B draw contact shadows for objects you overlay yourself.
- **default palette:** `#efe7d6 #cfc4ad #8a7f6d #2a2927 #ffffff`
- **params:** `objects`=0 (0..3 soft clay primitives: sphere, rounded block, torus); `grid`=0 (0..1 faint editorial grid over everything); `shadowA`=0 0 0 (fake contact shadow: x, y (short-side units, y up), width (0 = off)); `shadowB`=0 0 0 (second contact shadow); `lightX`=-0.7 (key light direction x (negative = from the left)); `cove`=1.3 (softness of the wall/floor curve)

## `studio-radial`
- **mood:** dark, premium, product hero stage, tech launch, quiet
- **use:** Behind glass icons, app icons, a device or one hero object. Quiet on purpose: the foreground carries the light. Turn uHalo on for a ring halo behind the subject.
- **default palette:** `#030407 #0a1224 #2f6bff #86b0ff #f4f8ff`
- **params:** `glowY`=0.08 (height of the light pool centre (-0.5 bottom .. 0.5 top)); `halo`=0.0 (0..1 ring halo behind the subject); `haloR`=0.3 (halo radius (short-side units)); `floor`=0.6 (glossy floor reflection (0 none)); `haze`=0.5 (fine haze layered over the stage)

## `liquid-chrome`
- **mood:** chrome, liquid metal, glossy, premium, futuristic, calm
- **use:** Hero backdrop behind a logo/product/number: slow molten-metal surface with studio reflections. Single hue + white reads most expensive.
- **default palette:** `#04050a #141a2c #6d8dff #cfdcff #ffffff`
- **params:** `warp`=1.0 (domain-warp strength (more = more molten)); `feat`=1.5 (feature scale (bigger = smaller ripples)); `bump`=0.55 (surface relief)

## `ink-in-water`
- **mood:** organic, smoky, elegant, mysterious, slow
- **use:** Billowing ink/smoke clouds as a mood backdrop for titles, quotes, music and fashion; looks hand-made, not geometric.
- **default palette:** `#05050a #17122b #7b3fe4 #ff7ac6 #fff1f8`
- **params:** `flow`=1.0 (how far the smoke is folded); `dens`=1.0 (cloud density)

## `topographic-lines`
- **mood:** technical, cartographic, calm, data-art, minimal
- **use:** Contour-map backdrop for data/finance/tech explainers; lines slowly breathe. Works light or dark.
- **default palette:** `#07120f #0e2a22 #2fd69a #9affd2 #eafff6`
- **params:** `levels`=14 (number of contour levels); `zoom`=1.6 (feature scale); `thick`=1.0 (line thickness)

## `grid-horizon`
- **mood:** retro-futuristic, synthwave, night, driving, energetic
- **use:** Infinite perspective grid floor under a striped sun; strong depth for titles floating above the horizon. Speed param drives the feeling of travel.
- **default palette:** `#0a0320 #2a0a4e #ff2e93 #ffb02e #fff3c4`
- **params:** `speed`=1.0 (travel speed); `hor`=0.0 (horizon height in p units (relative to frame centre)); `sunR`=0.28 (sun radius)

## `tunnel-rings`
- **mood:** hypnotic, tunnel, fast, club, sci-fi
- **use:** Infinite ring tunnel for energy beats, countdowns and transitions; speed up on hits via params.speed. Centre is the vanishing point: keep the hero there.
- **default palette:** `#020208 #0b1a4a #3d7bff #ff3dcb #ffffff`
- **params:** `sides`=8 (segments around); `depth`=1.0 (ring spacing (1 = default)); `twist`=0.25 (twist along depth)

## `starfield-warp`
- **mood:** space, hyperspace, speed, awe
- **use:** Parallax stars or warp streaks. streak=0 gives a calm drifting starfield, streak=1 hyperspace; animate params.streak with a hit curve for jump moments.
- **default palette:** `#010208 #060b24 #5b8cff #bfe3ff #ffffff`
- **params:** `streak`=0.35 (0 = dots, 1+ = long streaks); `speedF`=0.35 (travel speed); `neb`=0.6 (nebula glow amount)

## `bokeh-lights`
- **mood:** warm, dreamy, night city, celebratory, cinematic
- **use:** Out-of-focus lights drifting behind a hero (portrait, product, quote). Soft and expensive; use few, large discs for calm, many small for party.
- **default palette:** `#07060d #1a1030 #ff7a3d #ffc46b #fff2d6`
- **params:** `count`=1.0 (density multiplier); `soft`=0.35 (edge softness (0 = crisp discs with ring)); `drift`=1.0 (drift speed)

## `caustics-pool`
- **mood:** underwater, summer, fresh, calm, liquid
- **use:** Light patterns on a pool floor / underwater. Great under product shots or text for "clean, fresh, water". Palette: teal to white.
- **default palette:** `#02202e #0a5a7a #19b7d6 #7fe9ff #ffffff`
- **params:** `cells`=4.0 (caustic cell scale); `sharp`=1.0 (sharpness of bright lines)

## `metaball-gel`
- **mood:** playful, gel, soft-3d, friendly, candy
- **use:** Glossy blobs merging and splitting, lit like gel/clay. Good for app/product/kids and "friendly tech". Palette: 2 hues + light.
- **default palette:** `#fbe9ff #f7c6ff #7a5cff #ff6fb5 #ffffff`
- **params:** `blobs`=6 (number of blobs (<= 8)); `size`=1.0 (blob size); `gloss`=1.0 (highlight strength)

## `halftone-field`
- **mood:** print, pop, poster, editorial, riso, tactile
- **use:** Flat halftone dot field on paper, slowly swelling. Pairs with the halftone/poster DNA; misregistered second ink gives riso feel.
- **default palette:** `#f2ead8 #ece2cc #e8412c #1d3fbf #151515`
- **params:** `cell`=0.034 (dot spacing (p units)); `mis`=0.012 (misregistration of the second ink); `angle`=0.26 (screen angle (rad))

## `isometric-cubes`
- **mood:** graphic, isometric, playful, architectural, bold
- **use:** Isometric cube lattice with shaded faces, each cube breathing in height-colour; strong 3D feel without 3D. Great behind bold type or icons.
- **default palette:** `#14122b #3b2f8f #7c6cff #ffd166 #fff6df`
- **params:** `tile`=7.0 (tiles across the short side); `height`=1.0 (colour breathing amount)

## `light-rays`
- **mood:** divine, cinematic, hopeful, epic, dusty
- **use:** Volumetric god-rays from a point (top by default) through haze and dust. Put the hero in the beam. Move the source with params.src (x,y in p units).
- **default palette:** `#05070e #101a2e #ffb347 #ffe2a8 #ffffff`
- **params:** `rays`=1.0 (ray contrast); `src`=0.0 0.75 (light source position (p units)); `dustF`=1.0 (dust amount)

## `ray-glass-spheres`
- **mood:** glossy, calm, 3d, product, marble-run, modern
- **use:** Endless field of glossy spheres on a mirror floor, camera gliding forward. Premium "3D render" backdrop; keep headlines in the upper third.
- **default palette:** `#06070c #1a2036 #5a7dff #b9c8ff #ffffff`
- **params:** `floorY`=0.9 (floor depth below camera axis); `speedS`=0.6 (glide speed); `glass`=0.6 (refraction vs reflection mix)

## `ray-twisted-pillars`
- **mood:** architectural, cathedral, mysterious, premium, slow
- **use:** Corridor of twisted columns receding into fog; strong one-point perspective for titles, trailers, luxury. Dolly forward by speed param.
- **default palette:** `#04040a #14122a #6a4cff #ff8ad8 #ffffff`
- **params:** `speedP`=0.8 (dolly speed); `twistP`=0.9 (column twist)

## `ray-dunes`
- **mood:** desert, warm, vast, quiet, cinematic, golden hour
- **use:** Endless sand dunes at low sun, camera drifting forward. Vast, calm; good for travel, wellness, "journey" and slow reveals. Change palette for snow or alien planet.
- **default palette:** `#2a1020 #8a3b3a #f0a060 #ffd9a0 #fff6e0`
- **params:** `speedD`=0.5 (drift speed); `sunH`=0.22 (sun height)

## `ray-gel-orbit`
- **mood:** soft-3d, playful, tactile, hero object, friendly tech
- **use:** A single glossy gel/clay blob (metaball cluster) orbiting over a soft floor with real shadow and AO. The "3D hero object" without a model: place text beside or below.
- **default palette:** `#efe6ff #cbb8ff #7a5cff #ff7ac0 #ffffff`
- **params:** `blobsG`=5 (number of orbs (<= 7)); `sizeG`=1.0 (size)

## `ray-neon-city`
- **mood:** cyberpunk, night, flythrough, energetic, urban
- **use:** Camera skimming above a neon block city at night, windows glowing. High energy; combine with fast whooshes. Speed param raises the pace; add fog with params.
- **default palette:** `#05040c #160a35 #ff2fa0 #26e6ff #fff5ff`
- **params:** `speedC`=2.0 (flight speed); `heightC`=1.0 (building height multiplier)

## `ray-ocean`
- **mood:** sea, open, serene, epic, travel, dusk
- **use:** Open ocean to the horizon with a low sun glint. Camera bobs on the swell. Good for calm intros, "journey", climate and wellness; swap palette for tropical or arctic.
- **default palette:** `#0a1a30 #1f5a86 #ff9966 #ffd7a8 #fffbe8`
- **params:** `chop`=1.0 (wave height); `sunE`=0.12 (sun height)

## `ray-hex-tunnel`
- **mood:** sci-fi, tech, corridor, fast, clinical
- **use:** Flight down a hexagonal tech tunnel with glowing seams and ribs; one-point perspective, hero in the centre. Speed up on hits.
- **default palette:** `#03060c #0e1c33 #19c4ff #7dffe0 #ffffff`
- **params:** `speedH`=2.0 (flight speed); `radH`=1.5 (tunnel radius)

## `ray-monolith`
- **mood:** cinematic, ominous, minimal, 2001, monumental, luxury
- **use:** A black monolith on a mirror floor in mist, slow dolly. The most "film" of the set: product reveals, trailers, titles that must feel heavy. Single hue palette (P3 = edge light).
- **default palette:** `#020204 #0b0f1a #44506e #9fb2e0 #ffffff`
- **params:** `heightM`=1.0 (monolith height); `dolly`=0.5 (camera dolly amount)

## `layered-mountains`
- **mood:** serene, layered, atmospheric, dawn, calm, adventure
- **use:** Layered ridge silhouettes fading into mist with a low sun and gentle parallax. Cheap (no raymarch) and always pretty: use for calm intros, "journey", wellness, travel. Palette sets time of day.
- **default palette:** `#14102e #4a2f6b #e0607e #ffb38a #fff0d6`
- **params:** `layers`=6 (layer count (<= 7)); `mist`=1.0 (mist between layers); `sunM`=0.62 (sun height (0..1 of frame))

## `dotted-globe`
- **mood:** global, tech, explainer, data, network
- **use:** Rotating dot-matrix Earth-like globe (procedural continents, no texture) with atmosphere and star field. Core of "global/network/users worldwide" explainers; place markers by projecting lat/lon yourself (see reference).
- **default palette:** `#02050d #08193a #1f6bff #6fd3ff #ffffff`
- **params:** `tiltG`=0.35 (axial tilt (rad)); `sizeGl`=1.0 (globe size); `land`=0.5 (land fraction (0.35..0.6))

## `plasma-silk`
- **mood:** luxurious, satin, fabric, soft, fashion, beauty
- **use:** Flowing satin/silk folds with soft anisotropic highlights. Quiet luxury backdrop for beauty, fashion, finance-premium, quotes. Two close hues + warm white.
- **default palette:** `#1a0612 #5a1030 #c93a6b #ff9ab8 #fff0f3`
- **params:** `fold`=1.0 (fold strength); `freq`=1.0 (fold frequency)

## `ray-crystal-field`
- **mood:** crystalline, iridescent, magical, premium tech, awe
- **use:** Endless field of tumbling faceted crystals with iridescent reflections, camera gliding through. Bright, rich and obviously "3D" - for product reveals, gaming, jewellery, AI "magic" moments.
- **default palette:** `#05040f #1b1450 #6a5cff #4de3ff #ffd0f4`
- **params:** `speedK`=0.5 (glide speed); `sizeK`=1.0 (crystal size)
