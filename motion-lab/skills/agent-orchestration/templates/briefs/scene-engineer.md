# Brief — scene engineer: scene {NN} "{name}"

You are the SCENE ENGINEER for ONE scene of a video. You may write ONLY `scenes/{NN}-{name}.html` and the folder `scenes/{NN}-{name}.assets/`. Do not edit any other file.

## The video (so you can make judgment calls)
Idea: {one sentence}. Audience/platform: {…}. Total length {…} s; your slot is {start}–{end} s ({slot} s long).

## Your storyboard row
{paste the row: what happens, camera, events, transition in/out, entry state, exit state}

## Style DNA (do not change; use these values)
```json
{paste: palette, type, texture, motion.{personality,ease,spring,stagger,hitStyle}, signatureMoves, forbidden}
```

## Contract
- Obey /home/claude/motion-lab/CONVENTIONS.md (seek(t) pure; no Math.random/Date.now/CSS animation; fonts embedded).
- Page exposes `window.VIDEO = {w:{w},h:{h},duration:{slot},fps:{fps}}`, `seek(t)` for LOCAL time 0..{slot}, `EVENTS` via `Lab.ev` with LOCAL times for every hit/whoosh/reveal/type.
- First frame = entry state; last frame = exit state (see row). Draw 4% overscan.
- Runtimes: {list: lab.js, fx.js, type.js, …} loaded as in CONVENTIONS §8.

## Creative latitude
You MAY choose: composition, element shapes, which signatureMoves to use, camera path inside the row's description, secondary motion.
You MUST NOT: add colours/fonts/easings outside the DNA, add scenes, change the slot length, or add sound files.

## Test (required)
`python3 skills/qa-critique/scripts/lint_scene.py scenes/{NN}-{name}.html`
`node skills/scene-runtime/scripts/render.mjs scenes/{NN}-{name}.html out/stills/s{NN}.png --stills 0,{t1},{t2},{t3},{last} --cols 3 --scale 360 --root .` then LOOK at the sheet and fix.
`node skills/scene-runtime/scripts/render.mjs scenes/{NN}-{name}.html - --events out/ev-{NN}.json --root .`

## Report (<= 20 lines)
Files written · hooks (event list) · what you verified (which stills) · known issues · anything the director should change in DNA/storyboard.
