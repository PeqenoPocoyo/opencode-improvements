# Collage technique notes

## How real paper-collage animation is made (and how we imitate it)
| Real world | Cue the viewer reads | Our implementation |
|---|---|---|
| Animator moves pieces by hand every 2–3 frames | "on 3s" stutter, edges shimmer | `boilFps` 8: 3 geometry variants cycle; ±1.6 px position jitter |
| Paper slaps onto the table | shadow shrinks, tiny overshoot, crack of sound | `anim:'slap'`: scale 1.28→1, shadow `lift` 1→0, then 2% squash; sound `paper-slap` at landing |
| Torn paper shows white fibres | pale rim following edge | `rim` fill 3.2 px outside the coloured edge, with its own noise |
| Scissors cut | straight, slightly off segments, sharp corners | `edge:'scissors'`: ~1 vertex per 4 % of perimeter + tiny offsets |
| Tape/staples | pieces are physically attached | `tape` option or decoration fns |
| Cheap printing | halftone dots, misregistration | `fill.pattern:'halftone'/'news'`; for misregistration draw the same shape twice offset 2–3 px in ink colour with `multiply` |
| Paper slightly curled | highlight on one edge | 3 px light stroke offset toward the light |

## Composition rules
- Rule of 3 sizes: one XL (≥ 45 % of frame width), 2–3 M, rest S.
- Overlap deliberately: ≥ 25 % of the hero is covered by something; the stack gives depth without 3D.
- Colour blocking: strips of flat colour behind text; text colour = cream or ink only.
- Negative space: keep one quadrant calm (paper only) so the eye rests there.
- Rhythm: arrivals every 1 beat or every 1.5 beats; never equal intervals for more than 4 pieces — insert one pause.
- Camera: a slow 2–4 % scale push on the whole table (wrap in `ctx.translate/scale` around `Collage.draw`) or tiny handheld (`Lab.handheld`). Not both.

## Style variations (swap parameters, get a different "soul")
- **Punk zine:** `edge:'scissors'`, black/red/cream, ransom headline, halftone + news, stamps, rotation up to ±10°, boil 8 fps, harsh shadow (`shadow:.9`).
- **Soft craft:** `edge:'torn'` rough 9, pastel palette, blob + circle shapes, kraft, stitches, shadow .35, boil 6 fps, hand font (Caveat).
- **Editorial museum:** clean (`edge:'clean'`) rects on cream, one torn accent, serif headline, grid/lined fills, no boil, thin stains only.
- **Retro travel:** big circle sun, arrows/tags, dots/stripes, kraft, stamps ("AIRMAIL"), slideL/slideR whooshes.
- **Cut-out science:** blob/circle bodies, stitched orbit lines, Art generators inside circles, tags with mono text.

## Performance
Cache is by geometry key; avoid creating new `w/h` values every frame (animate with `scale`, not `w`). `Collage.draw` allocates nothing per frame except path commands.

## Known limits
No real 3D curl. Shadows are a canvas shadowBlur (cheap) not raytraced. Fonts must be loaded (`document.fonts.ready` handled by render.mjs).
