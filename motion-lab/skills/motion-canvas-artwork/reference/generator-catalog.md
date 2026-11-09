# Art generator catalog (generated from runtime/art.js)

`Art.draw(ctx, name, t, {x,y,w,h, pal:[bg,ink1,ink2,ink3,hi], seed, loop, speed, alpha, bg:false, ...params})`. `loop` = seconds; the animation repeats exactly. Params below show defaults.

| generator | mood | use | params (defaults) |
|---|---|---|---|
| `flowField` | organic, silky, generative-art classic | Thousands of thin trails following a noise field; hero texture behind type. Scale controls swirl size. | `{ count: 700, steps: 36, scale: 1.6, step: .012, width: 1 }` |
| `contours` | topographic, scientific, calm | Iso-lines of a moving noise field (marching squares). Map/data feel; very clean on dark bg. | `{ levels: 12, cell: 12, width: 1.4 }` |
| `waveLines` | unknown-pleasures, signal, moody | Stacked ridge lines occluding each other (joy-division). Headline sits above or inside the calm band. | `{ rows: 38, amp: .09, bump: 1 }` |
| `warpGrid` | tech, spatial, blueprint | A square grid bent by noise; looks like a fabric of space. Pair with glow. | `{ cells: 22, warp: .06 }` |
| `lissajous` | oscilloscope, harmonic, hypnotic | Layered Lissajous/harmonograph curves with phase drift. Great centrepiece loop. | `{ curves: 5, a: 3, b: 4, size: .42 }` |
| `sineBraid` | fluid, ribbon, hair | Bundles of parallel sine strands that braid and cross. Horizontal band or full bleed. | `{ strands: 26, amp: .16, freq: 1.4 }` |
| `stringArt` | geometric, delicate, mathematical | Chords between points on two edges/circle producing envelope curves. | `{ n: 90, mode: 0 }` |
| `moire` | op-art, vibrating, optical | Two rotating line gratings interfering. Instantly "designed"; strong at low density. | `{ lines: 70, angle: .06 }` |
| `stripesWarp` | op-art, 60s, psychedelic | Parallel stripes displaced by sine/noise into 3D-looking folds. | `{ stripes: 46, fold: .12 }` |
| `dotGrid` | pulsing, techno, clean | Grid of dots whose size follows a travelling wave. Style: circle|square|ring|plus. Use as a calm texture or a reveal. | `{ cell: 36, style: 'circle', wave: 6, rings: 1 }` |
| `truchet` | maze, tile, bauhaus | Quarter-arc tiles that flip in a stagger. Reads as pattern design, not "AI noise". | `{ cell: 90, width: .28 }` |
| `hexPulse` | sci-fi, honeycomb, shield | Hexagon lattice where a light wave travels; edges glow when the wave passes. | `{ size: 44, wave: 1.6 }` |
| `pixelMosaic` | retro, 8-bit, data | Grid of squares quantised from a noise field into the palette (stepwise colour change). | `{ cell: 40, gap: 2 }` |
| `isoBars` | isometric, city, data-viz | Isometric columns whose heights ripple. Three-face shading from the palette. | `{ cell: 54, height: 2.4 }` |
| `rings` | sonar, ripple, calm | Concentric rings expanding from one or several centres with interference. | `{ origins: 3, count: 16, width: 2 }` |
| `orbits` | planetary, system, infographic | Concentric orbits with dots travelling at different speeds (all whole cycles per loop). | `{ rings: 7, dots: 2 }` |
| `sunburst` | retro, rising, optimistic | Alternating rays from a point, slowly rotating. Pair with a hero object in front. | `{ rays: 28, cx: .5, cy: .5 }` |
| `radialBars` | audio, pulse, energy | Bars around a circle whose length is driven by noise or by an explicit array o.levels(t). | `{ bars: 96, inner: .22, length: .22 }` |
| `mandala` | ornamental, symmetrical, meditative | N-fold symmetric petals and rings built from layers; each layer rotates at a different whole-number speed. | `{ folds: 12, layers: 6 }` |
| `polyRipples` | geometric, tunnel, hypnotic | Nested polygons (sides 3..8) rotating and scaling outwards; very "motion-poster". | `{ sides: 6, count: 14 }` |
| `tunnelRects` | zoom, perspective, brutalist | Rounded rectangles scaling past the camera; instant depth without 3D. | `{ count: 12, radius: .08 }` |
| `spiral` | sunflower, natural, hypnotic | Phyllotaxis dots (golden angle) breathing in size; reads as organic maths. | `{ dots: 900, size: 7 }` |
| `blobs` | soft, friendly, flat-design | Morphing organic shapes with flat fills and optional offset shadow; "Notion/Stripe" illustration backdrops. | `{ count: 6, size: .28, wobble: .35 }` |
| `gradientBlobs` | dreamy, grainy-gradient, premium | Big soft colour clouds (radial gradients) + fine grain specks; the 2023 "grainy gradient" look, procedural. | `{ count: 5, grain: 1 }` |
| `lowPoly` | crystalline, vector, facets | Triangulated jittered grid, each facet coloured by a drifting noise through the palette. | `{ cell: 110, jitter: .35 }` |
| `voronoi` | cellular, stained-glass, biological | Moving seed points; each cell flat-filled from the palette with thin borders. Coarse pixel blocks keep it fast. | `{ seeds: 22, block: 6 }` |
| `bubbles` | playful, fresh, underwater | Rising translucent bubbles with highlights, wobble and parallax sizes. | `{ count: 60 }` |
| `plexus` | network, ai, data | Drifting nodes connected by fading lines when close. The "AI network" look; keep node count low for elegance. | `{ nodes: 70, link: .16 }` |
| `lightning` | electric, tension, sci-fi | Jagged branching arcs between two points, re-rolled at 12 fps (set o.from/o.to as 0..1 points). | `{ bolts: 3 }` |
| `scribble` | hand-drawn, sketchy, human | Rough hatch/scribble fills and wobbly outlines (rough.js style) for hand-made brands. Draws N shapes. | `{ shapes: 8, hatch: 14 }` |
| `memphis` | playful, 80s, pop | Scattered Memphis primitives (squiggle, triangle, ring, plus, dots, half-circle) drifting and rotating. | `{ count: 34, size: 1 }` |
| `confetti` | celebration, burst, pop | Deterministic confetti burst from o.origin at time o.t0 (gravity + drag + flutter). Call every frame; before t0 draws nothing. | `{ count: 120, t0: 0, power: 1 }` |
| `brushStrokes` | painterly, expressive, analog | Thick translucent brush strokes with dry-edge bristle lines sweeping across the frame. | `{ strokes: 7, bristles: 22 }` |
| `glyphField` | terminal, data, brutalist | Grid of characters that flip/scramble in waves. Pass font family via `font`, symbol set via `chars`. | `{ cell: 38, chars: '01<>/\{}+=*#', font: 'monospace' }` |
