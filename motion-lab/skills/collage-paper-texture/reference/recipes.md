# Collage recipes (copy the skeleton, change content, then DIVERGE: palette, shapes, timing)

## 1. Poster reveal (6–8 s, loop)
Paper bg → XL circle `pop` → 2 headline strips `slap` (−4°, +3°) one beat apart → date tag `slideR` → tape/pin/stain static → hold 2 s with boil.
## 2. Ransom headline
`Collage.ransom(ctx,'WORD',x,y,{size:110,stagger:.07,t,t0:1})` letters drop in; register each letter as `Lab.ev(t0+i*.07,'tick')` manually (ransom does not auto-register). Follow with one plain strip carrying the subtitle (readable).
## 3. Zine page series (3 × 5 s)
Same grid (3 columns); each page changes ONE variable (palette family). Transition: the whole page `slideU` out with `out:'slideU'`, next page `drop`s.
## 4. Map with pins
Kraft rectangle (large) + torn blob "regions" + `Collage.stitch` route + `pin` at each stop, pins pop with `Lab.ev(...,'pop')`; callout tags `slideL`.
## 5. Sticker-sheet end card
6–9 small shapes (`pop`, stagger .12 s) around a CTA tag. Each sticker a different shape AND fill. Sound: pop pitch rising +1 semitone each.
## 6. Stop-motion product tour (UI-in-video combo)
Render UI screens with `ui-kit.js` into offscreen canvases, then place as `deco` inside a `rect` piece with `tape:'both'`; tilt −3°; pieces slide between like cards on a table.
## 7. Cut-out character
Build from pieces: `blob` torso, `circle` head, `strip` limbs, `star` hands. Parent transforms by hand: compute child positions from a root (x,y,rot) per frame. Use `Lab.spring` on rot for secondary motion. (For real rigs use `vector-characters`.)
