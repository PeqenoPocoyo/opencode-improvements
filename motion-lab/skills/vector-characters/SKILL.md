---
name: vector-characters
description: Procedural 2D characters with NO image assets - biped figure with 2-bone IK (walk, run, idle, wave, jump, point, dance), squash-and-stretch blob creature, hovering robot, expressive face (blink, look, moods, lip-flap talk), footstep events. Use for mascots, explainers with a guide character, sticker animations, cutout puppets.
---

# vector-characters — a cast in 3 kB of code

Runtime: `runtime/rig.js` → global `Rig` (needs `lab.js`). See `examples/rig-gallery.html` (every action on one sheet, loops 6 s).

## Pick a character (don't draw a "person" if a blob will do)
| Need | Use | Why |
|---|---|---|
| Friendly mascot, simple emotion | `Rig.blob` | squash/stretch reads instantly, cheap to make charming |
| Tech/AI assistant, narrator | `Rig.bot` | LED face = talking without lip-sync trouble |
| Human guide, walks across scenes | `Rig.biped` | IK legs/arms, needs ground line |
| Reaction only | `Rig.face` alone, scaled huge | most expressive thing per line of code |

## Fast path
```js
const pal = Rig.pal(DNA.palette);                         // maps dna.json -> skin, cloth, cloth2, accent, line...
Rig.biped(ctx, t, {x:300, y:1500, scale:1.1, action:'walk', speed:1, pal, style:'cutout', hat:'cap', seed:2});
Rig.blob (ctx, t, {x:700, y:1500, action:'hop', period:1.2, pal});
Rig.bot  (ctx, t, {x:540, y:1400, mouth: Rig.talk(t, 2.0, 5.5, 4), pal});
Rig.steps(0, 6, 1, {type:'tick'});                       // one event per foot-down for sound
```

## Rules (each one fixes a classic weak-model failure)
1. **Loop maths:** walk/dance cycles: `speed * loopSeconds` must be an integer (speed 1 or 2 in a 6 s loop). Blob hop: `period` must divide the duration.
2. **Ground line:** always pass the ground y as `y`; draw a floor/ground shadow (done inside). Characters floating above nothing look broken.
3. **Move the character through the world with x**, not by changing `speed`. Walk speed to match ground travel: stride 80 px per half-cycle at scale 1 → at `speed:1` moves ≈160 px/s; set `x = x0 + 160*scale*speed*t` or the feet "skate".
4. **Anticipation + follow-through:** before a jump leave 0.15 s crouch (built in); after landing leave 0.2 s squash. Never start an action on frame 0 of a scene — idle first.
5. **Eyes lead:** change `look` 0.1–0.2 s before the head/body turns. Blink is automatic (`Rig.blink`), never turn it off.
6. **Face moods:** `happy` default; `surprised` on arrival/impact; `angry`/`sad` only with a story reason. Mouth: `Rig.talk(t,t0,t1,seed)` opens in syllables; do not loop one open/close.
7. **Style** must match the rest of the scene: `outline` for flat vector/UI scenes, `cutout` (white rim) for collage (pair with `collage-paper-texture`), `flat` for minimal.
8. **Scale hierarchy:** hero ≥ 35 % of frame height; companions 60 %. A 1080×1920 frame fits a biped at `scale 1.4` (≈ 330 px wide by 520 tall).
9. **No random:** `seed` picks blink timing & talk syllables, never `Math.random`.
10. **Cast sheet first:** render the gallery with YOUR palette before building the scene. If two characters share colour+silhouette, change one.

## Sound hooks
Footsteps `Rig.steps`; jump takeoff → `Lab.ev(t0+.18*dur,'whoosh')`, landing → `Lab.ev(t0+.85*dur,'hit-soft')`; blob hop landing every `period*1.0` → `pop`/`hit-soft`; bot talking → quiet `blip` stream or no SFX (music ducking handled in sound-design-pro).

## Extending (when you need a new look)
Add parts by drawing extra shapes inside the character's local transform: copy `R.blob` (it is 15 lines), keep `ctx.save/translate/scale/restore`. Use `Rig.ik2` for any 2-segment limb (tentacles: chain 3–4 `ik2`s with phase offsets). Palette changes alone give new characters: swap `cloth/cloth2/accent`.

## Reference
`reference/animation-principles.md` (12 principles mapped to the functions, timing table, walk/run numbers, squash maths, acting beats, cheap secondary motion).
