---
name: scene-runtime
description: The deterministic engine every motion-lab video runs on - the seek(t) page contract, the Lab library (easing, springs, keyframes, seeded noise, OKLCH colour, camera, shake, loops, text splitting, events), the WebGL post-FX layer, and render.mjs which turns a page into contact sheets, frames, events.json or an MP4 with sub-frame motion blur and muxed audio. Use whenever you write or render a scene page, need exact frames, a loop, motion blur, an events dump for sound, or hit "it flickers", "it differs each run", "fonts fall back", "render hangs".
---

# scene-runtime — one HTML page, one pure function of time

A scene is a page that exposes `window.VIDEO`, `window.seek(t)`, `window.EVENTS`, `window.__ready`. The renderer sets `t` frame by frame, screenshots, and encodes. Because every frame is a pure function of `t`, you can render any frame, in any order, and get the same pixels. That is what makes stills review, loops, motion blur and sound sync possible.

## Setup (once per project)
```bash
bash skills/scene-runtime/scripts/setup.sh my-video      # copies lab/ (all runtimes + fonts + three.js), template scene.html, folders
cd my-video && export NODE_PATH=$(npm root -g)           # playwright is installed globally
```
Needs: node 18+, ffmpeg, playwright + chromium (`npm i -g playwright && npx playwright install chromium`).

## The contract (CONVENTIONS.md §1 — read it)
1. `seek(t)` is pure: same `t` -> same pixels. No state from the previous frame.
2. No clocks: no `Date.now`, `performance.now`, `setTimeout/Interval`, CSS `transition/animation/@keyframes`, rAF-driven visuals.
3. No `Math.random()`: `Lab.rng(seed)` / `Lab.noise(seed)`.
4. History (trails, physics, lag) is baked at load by stepping 0..duration at 1/240 s into an array.
5. Loops: frame `duration` equals frame 0 (integer cycles; `Lab.loop`).
6. Fonts embedded/served from the project; `document.fonts.ready` is awaited by render.mjs.
7. Heavy filters baked or done by FX.js.

## Page skeleton (the template: `templates/scene.html`)
```html
<div id="stage">
  <div id="world" class="abs" style="width:1080px;height:1920px"> <canvas id="bg"></canvas> ...DOM content... </div>
  <canvas id="fx" class="abs"></canvas>           <!-- post: vignette/grain/bloom on top of everything -->
</div>
<script src="lab/lab.js"></script>
<script>
  const DNA = {...};                                // inline dna.json
  Lab.ev(1.2, 'impact', {intensity:.9});            // events at BUILD time
  function render(t){ /* set every style/draw call from t */ }
  Lab.init({ w:1080, h:1920, duration:6, fps:30, bg:DNA.palette.bg, render });
</script>
```
`Lab.init` defines `VIDEO`, `seek`, `__ready`, and (unless the URL has `?render`) a preview player with a scrubber.

## Lab cheat sheet (all pure functions of arguments)
| Group | API |
|---|---|
| math | `clamp lerp map seg(t,a,b) smoothstep smootherstep mix mod snap fract dist deg rotate sat` — `seg` gives 0..1 progress of t between a and b |
| easing | `Lab.ease.<name>(x)` names: linear, in/out/inOut + Quad Cubic Quart Quint Sine Expo Circ Back, Elastic, Bounce; `Lab.ease.get('outExpo')`; `Lab.bezier(x1,y1,x2,y2)`; `Lab.steps(n)` |
| named curves | `Lab.curves.{snap,punch,whip,glide,settle,drop}` — "feels" (see below) |
| physics-ish | `Lab.spring(t,w,z)` 0->1 step response; `Lab.track(v0,[[t,v,w?,z?],...])` retargeting spring value; `Lab.kf([[t,v,ease?],..])`, `Lab.kfv` for vectors |
| random | `Lab.rng(seed)` -> r() with `.range .int .pick .gauss .shuffle .weighted .onCircle .inCircle`; `Lab.noise(seed)` -> `{n2,n3,fbm2,fbm3,curl2,loop1}`; `Lab.hash(n)` |
| colour | `Lab.oklch(l,c,h,a)` css string; `oklchHex`, `oklch2rgb`, `rgb2oklch`, `hex2rgb`, `rgb2hex`, `mixColor(a,b,k)` perceptual mix, `rgba`, `luminance`, `contrast` |
| reactions | `Lab.hit(t,t0,tau)` jump to 1 then decay; `bump(t,t0,atk,dec)`; `win(t,a,b,fi,fo)`; `adsr`; `beat(t,bpm,offset,tau)` -> {i,phase,pulse,bar,step16}; `beatTimes(bpm,dur,offset,sub)`; `stagger(i,n,each,total)` |
| text | `Lab.split(el,'chars'|'words'|'lines')` spans; `typed(str,t,t0,cps)`; `scramble(str,p,seed)`; `countUp(a,b,p,decimals,ease)`; `fmt(n,decimals)` |
| SVG | `pathAt(pathEl,p)` -> {x,y,angle}; `drawStroke(pathEl,p)`; `sketchPath(pts,seed,jitter,closed)` hand-drawn |
| camera | `const cam = Lab.camera(worldEl,{w,h,persp}); cam.set({x,y,zoom,rot,rx,ry})`; `Lab.shake(t,{t0,amp,decay,freq,seed})` -> {x,y,r}; `Lab.handheld(t,amp,seed)` |
| loops | `Lab.loop.phase(t,dur,cycles)`, `cycles`, `blend` (cross-fade the end into the start) |
| events | `Lab.ev(t,type,{intensity,dur,pitch,pan,label})`, `Lab.evBeats(type,bpm,dur,offset,sub,opts)` |
| timeline | `Lab.sequence(list)`, `Lab.chain(durs,overlap)` -> [{start,dur}] |
| init | `Lab.init({w,h,duration,fps,bg,render,loop,audio})` |

Named curves: **snap** fast out, tiny settle (UI); **punch** quick overshoot (hits); **whip** accelerate then stop hard (pans); **glide** long gentle ease (camera); **settle** soft landing with a tiny bounce; **drop** gravity-like fall with bounce.

## Rendering (render.mjs)
```bash
R=skills/scene-runtime/scripts/render.mjs     # run from the project: node lab/../ ... or use the pack path
node $R scene.html out/stills/sheet.png --stills 0.2,1.0,2.0,3.5,5 --cols 3 --scale 360   # ALWAYS first
node $R scene.html out/frame.png --at 2.4                                                  # one full-size frame
node $R scene.html - --events out/events.json                                              # dump events for sound
node $R scene.html out/draft.mp4 --fps 30 --sub 1 --workers 4                              # review copy
node $R scene.html out/final.mp4 --fps 60 --sub 8 --workers 4 --audio audio/mix.wav        # motion blur + audio
node $R scene.html out/part.mp4 --range 3.0-6.5                                            # a slice
```
Flags: `--root <dir>` (folder served over http; must contain the page and lab/), `--crf 16`, `--preset veryfast`, `--proxy http://..` (opt-in only). Warnings printed: fonts not loaded (fallback in use), 0 EVENTS. Page console errors appear as `[page error]`.

Motion blur: `--sub N` renders N sub-frames across a 180 degree shutter and averages (`tmix`). `--sub 8` at 60 fps is "final" quality; `--sub 1` for drafts. Cost: N x render time.

## Patterns that work
- **Layers:** bg canvas (shader or gradient) < DOM/SVG content in `#world` (camera applies to it) < fx canvas (post, not camera-moved).
- **Camera:** every scene sets `cam.set({...})` every frame (push 1.0 -> 1.06 over the beat, drift via `Lab.handheld`, shake on hits).
- **Hit reactions:** `const h = Lab.hit(t, T.slam, .3)`; scale `1 + .08*h`, glow `1 + .8*h`, shake from `Lab.shake`.
- **Stagger:** `p = ease(Lab.seg(t, t0 + i*stagger, t0 + i*stagger + dur))`.
- **Baking history:** `const trail = []; for(let s=0;s<=DUR*240;s++){ ... trail.push(...) }` then `trail[Math.round(t*240)]`.
- **Looping value:** `Lab.noise(7).loop1(t, DUR)`; integer cycles of sin: `Math.sin(Lab.TAU * 3 * t / DUR)`.

## Weak-model protocol
1. Start from `templates/scene.html`; keep its structure.
2. Never put visual state in variables that survive between `seek` calls.
3. Render a stills sheet after each beat; look at it; fix.
4. Register events as you place each hit.
5. If a render hangs: check `NODE_PATH`, ffmpeg on PATH, page errors; do not use a proxy for localhost.
6. If fonts fall back: link `lab/fonts/fonts.css` and use the exact family names.

## Failure modes
| Symptom | Cause | Fix |
|---|---|---|
| Frames differ per run | `Math.random`, `Date.now`, unseeded noise, CSS animation | `Lab.rng/noise`, remove clocks |
| Flicker between frames | state from previous frame; sub-pixel layout from measuring in a different state | pure `render(t)`, fixed sizes |
| Blurry text under camera zoom | CSS transform scale on DOM text with `will-change` | no `will-change`; render at the final scale or use `zoom` on the camera helper |
| Slow render | big CSS blur/box-shadow on moving elements; WebGL at 4k in SwiftShader | pre-bake glows, FX bloom, smaller canvas, fewer raymarch steps |
| Black canvas | WebGL shader error | read `[page error]`, check shader compile logs |
| Loop pops | not an integer number of cycles | `Lab.loop.blend` or fix cycles |
| Audio shifted | muxed with an offset | `render.mjs --audio` (copies mastered WAV); check qa_audio `audio start vs video start` |

Files: `runtime/lab.js` (core) · `runtime/fx.js` (WebGL post, see `reference/fx.md`) · `scripts/render.mjs` · `scripts/setup.sh` · `templates/scene.html` · `examples/`.
