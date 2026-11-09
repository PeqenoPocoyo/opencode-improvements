# Shader transition catalog (generated from runtime/transitions.js)

Call: `tr.render(canvasA, canvasB, progress, name, params)`. `progress` must already be eased (column **ease** is the recommended `Lab.ease` name). **frames** is the typical duration at 30 fps (multiply by fps/30). **sound** is the event type to emit with `Lab.ev(tStart + dur*0.5, type)` (see sound-design-pro event vocabulary).


## Basic (wipes, irises, flashes)

| name | ease | frames@30 | sound | defaults | what it says |
|---|---|---|---|---|---|
| `crossfade` | inOutSine | 15 | swipe | `{}` | Plain dissolve. Weakest; dreamy or neutral only. |
| `dipToColor` | inOutCubic | 18 | whoosh | `{ color: '#000000', hold: .15 }` | Fade to a colour and out. Chapter changes (use an accent or bg tone, not black by default). |
| `whiteFlash` | linear | 4 | impact | `{ color: '#ffffff', width: .3 }` | Hard cut hidden by a 2-4 frame flash peaking at the cut. Energy spikes. Max 3 per second. |
| `wipeLinear` | inOutCubic | 14 | swipe | `{ angle: 0, soft: .05 }` | Straight wipe along angle (rad). 0 = left to right, 1.5708 = top to bottom. |
| `wipeRadial` | inOutSine | 18 | swipe | `{ soft: .02, start: 0 }` | Clock wipe from the top. Counters, timers, "time passes". |
| `irisCircle` | inOutCubic | 18 | whoosh | `{ cx: .5, cy: .5, soft: .01 }` | B grows as a circle from (cx,cy). Hero-object reveals; set cx,cy on the object. |
| `irisOut` | inOutCubic | 18 | whoosh | `{ cx: .5, cy: .5, soft: .01 }` | A shrinks to a circle that closes on (cx,cy) revealing B (classic cartoon iris). |
| `barnDoors` | inOutCubic | 16 | whoosh | `{ horizontal: 0 }` | A splits in two panels that slide apart (shadowed) revealing B. horizontal=1 splits top/bottom. |
| `blinds` | inOutCubic | 16 | swipe | `{ count: 10, angle: 0, soft: .08 }` | Venetian strips open one by one. |
| `bars` | inOutCubic | 18 | swipe | `{ count: 12, stagger: .5 }` | Vertical bars of A slide up/down alternately with a stagger, uncovering B. |

## Camera-motion (push, whip, zoom, spin)

| name | ease | frames@30 | sound | defaults | what it says |
|---|---|---|---|---|---|
| `slidePush` | inOutCubic | 14 | whoosh | `{ angle: 0 }` | A is pushed off by B. angle 0 = content moves left. |
| `parallaxSlide` | inOutCubic | 18 | whoosh | `{ angle: 0, shadow: .5 }` | A slides off fast, B arrives slower underneath with shadow = depth. |
| `whipPan` | whip | 10 | whip | `{ angle: 0, blur: 80 }` | Fast pan with directional motion blur on both scenes. 8-14 frames; use curve "whip". Pre-sound: whip. |
| `zoomThrough` | inCubic | 14 | whoosh | `{ strength: 2.6, blur: .28 }` | Camera flies through A into B: A zooms in with radial blur, B settles from zoomed-in. Match the zoom centre to an object. |
| `zoomOutIn` | inOutCubic | 18 | whoosh | `{ strength: 2.2 }` | A scales down and away revealing B that scales up into place (pull-back then push). |
| `spinZoom` | inOutCubic | 18 | whoosh | `{ turns: .25, strength: 1.7 }` | Rotate and zoom A out, B in with the opposite spin. |
| `radialBlurSpin` | inOutCubic | 16 | whoosh | `{ turns: .5, blur: .18 }` | Spin around the centre with rotational blur, swapping scenes mid-spin. |

## Pseudo-3D (perspective, cube, flip, peel, doors)

| name | ease | frames@30 | sound | defaults | what it says |
|---|---|---|---|---|---|
| `perspectiveTilt` | inOutCubic | 20 | whoosh | `{ tilt: 1.25, bg: '#0a0a0a' }` | A rotates away about a vertical axis in perspective while B rotates in from the other side. |
| `cubeRotate` | inOutCubic | 20 | whoosh | `{ bg: '#050505' }` | Fake cube turn: A and B are two faces squeezed with perspective and shaded at the seam. |
| `flip` | inOutCubic | 18 | whoosh | `{ bg: '#0a0a0a', axis: 0 }` | Card flip around the vertical (axis 0) or horizontal (axis 1) centre line. |
| `mirrorFold` | inOutCubic | 16 | whoosh | `{ }` | A squeezes into the vertical centre line, B opens from it. |
| `pagePeel` | inCubic | 22 | swipe | `{ }` | Page folds over from the right edge showing a darkened back side, then leaves B. |
| `doorOpen` | inOutCubic | 20 | whoosh | `{ bg: '#000000' }` | A is a double door hinged at the edges, swinging open in perspective onto B. |

## Dissolves and texture reveals

| name | ease | frames@30 | sound | defaults | what it says |
|---|---|---|---|---|---|
| `rippleDissolve` | inOutSine | 22 | shimmer | `{ cx: .5, cy: .5, freq: 22, amp: .03 }` | Ring wave expands from a point; B appears inside the ring (water, sonar, glass). |
| `liquidWarp` | inOutSine | 24 | whoosh | `{ amount: .12, scale: 2.5 }` | Both scenes melt with noise displacement while crossfading. |
| `pixelDissolve` | linear | 16 | glitch | `{ size: 18, pixelate: 1 }` | Blocks switch at random times; the swapping blocks show pixelated. |
| `halftoneDissolve` | inOutCubic | 20 | swipe | `{ size: 16, angle: .5236 }` | B appears as growing halftone dots until they merge (print/poster looks). |
| `noiseDissolve` | inOutCubic | 20 | riser | `{ scale: 3, edge: .07, color: '#ffb04a' }` | Organic fbm dissolve with a glowing burning edge. |
| `inkBleed` | inOutCubic | 24 | whoosh | `{ scale: 8 }` | B spreads like ink from several seeds with irregular edges. |
| `paperTear` | inOutCubic | 12 | paper-rip | `{ angle: 0, rough: .05, fiber: .014 }` | A is torn away along a ragged line: white fibre edge on A, soft shadow on B. Pair with a rip sound and a 3-frame flash. |
| `brushWipe` | inOutCubic | 18 | swipe | `{ angle: -.15, rough: .05, bands: 6 }` | Painted strokes sweep across in staggered bands with rough edges. |
| `hexGrid` | inOutCubic | 20 | tick | `{ size: 14 }` | Hexagonal cells open to B at random times (tech, honeycomb). |
| `gridFlip` | inOutCubic | 22 | tick | `{ cols: 6, rows: 10, bg: '#0a0a0a' }` | Tiles flip over one by one from the centre outward. |
| `shapeFlood` | inOutCubic | 20 | impact | `{ cx: .5, cy: .5, color: '#ff3b6b' }` | A flat colour floods from a point over A, then B opens from the same point (brand-colour transition). |

## Glitch / digital

| name | ease | frames@30 | sound | defaults | what it says |
|---|---|---|---|---|---|
| `glitchSwap` | linear | 10 | glitch | `{ blocks: 16, rgb: .02 }` | Rows switch at random times with horizontal tears and RGB split. |
| `dataMoshLite` | inOutCubic | 14 | glitch | `{ block: 48, amount: .5 }` | Blocks smear with random motion vectors while switching (datamosh look). |
| `vhsRewind` | inOutSine | 14 | glitch | `{ bands: 14, bleed: .02 }` | Tracking tears, colour bleed and noise like a tape rewind. |
| `scanlineWipe` | inOutCubic | 14 | zap | `{ angle: 1.5708, lines: 120, soft: .02 }` | Wipe whose edge is a band of interlaced scanlines and a bright line. |

## Light and optical

| name | ease | frames@30 | sound | defaults | what it says |
|---|---|---|---|---|---|
| `glassRefract` | inOutCubic | 20 | shimmer | `{ angle: 0, width: .2, ior: .07 }` | A glass edge sweeps across, refracting and dispersing colours; A on one side, B on the other. |
| `lightLeakWipe` | inOutSine | 20 | whoosh | `{ angle: 0, soft: .35, color: '#ff8a3d' }` | Soft wipe whose edge is a warm light leak. |
| `filmBurn` | inOutSine | 22 | riser | `{ color: '#ff7a1a', intensity: 1.6 }` | Film-burn bloom: orange-white burn swells over A and clears onto B. |
| `lumaWipe` | inOutSine | 20 | swipe | `{ invert: 0, soft: .1 }` | The luminance of A decides what changes first (dark areas first; invert=1 for bright first). |
| `kaleidoscope` | inOutSine | 20 | shimmer | `{ segments: 6 }` | Both scenes fold through a kaleidoscope mid-transition. |

## Non-shader transitions (do these in the scene itself; they usually beat any shader)

| name | how | when |
|---|---|---|
| **Match cut** | End scene A on a shape/position/colour that scene B starts with (circle→sun, bar→line, icon→icon). Same position, same size on the cut frame. | Strongest "professional" cut; zero cost. |
| **Object carry** | One element (card, cursor, logo) keeps moving across the cut while everything else swaps. | Story continuity; product films. |
| **Camera continuation** | Camera move starts in A and finishes in B (`Lab.camera` with continuous velocity). | Journeys, zoom-through. |
| **Typographic wipe** | A giant word/letter fills the screen (cover), next scene is revealed inside/after it. | Kinetic type films. |
| **Mask by shape** | A shape (circle, rounded rect, blob) grows from the focal object and contains B. | UI morphs, icon→screen. |
| **Hard cut on impact** | Cut exactly on a sound transient, with a 2-frame shake or flash. | Fast edits; cheapest and most rhythmic. |
| **Dip via element** | Fade through the page background colour or an accent, not black. | Chapters. |
| **J/L cut** | Sound of B starts 6–12 frames before the picture changes (or A's tail overlaps). | Dialogue/voice-over and talking head. |
| **Smash cut** | Silence + 1 frame black, then loud B. | Jokes, shock. |
