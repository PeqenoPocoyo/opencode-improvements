# CONVENTIONS — the contract every skill, script and hook in motion-lab obeys

Read this file once before touching anything. Every other file assumes it.

## 1. The one rule that makes everything renderable: `seek(t)` is a pure function of time

A scene is a single HTML page. It exposes:

```js
window.VIDEO  = { w: 1080, h: 1920, duration: 12, fps: 30 };   // pixels, seconds, frames per second
window.seek   = (t) => { /* draw the exact frame at time t (seconds) */ };
window.EVENTS = [ { t: 2.4, type: 'impact', intensity: 0.9, dur: 0.4, label: 'title slam' }, ... ]; // optional, feeds sound
```

`seek(t)` must obey:

1. **Deterministic.** Same `t` → same pixels, in any order, any number of times. No state carried from the previous frame.
2. **No clocks.** Never use `Date.now`, `performance.now`, `requestAnimationFrame` timing, `setTimeout`, `setInterval`, CSS `transition` or CSS `animation` to drive visuals. (The preview player may call `seek` from rAF; the scene itself may not.)
3. **No `Math.random()`.** Use `Lab.rng(seed)` or `Lab.noise(seed)`. A seed is a number written in the source.
4. **History is baked.** Anything that needs history (a trail, a physics sim, a camera that lags) is computed once at load by stepping from 0 to `duration` at 1/240 s, stored in an array, and read back with interpolation.
5. **Loops.** If the piece loops, frame `duration` must equal frame 0. Use `Lab.loop` helpers, and make every periodic value an integer number of cycles per `duration`.
6. **Fonts are embedded** (base64 `@font-face` or served from the project folder). Never rely on system fonts. Run `document.fonts.ready` before the first render; `render.mjs` does this.
7. **Layout is measured in `seek`, never cached from a different state.** Measuring is allowed (it is deterministic).
8. **Heavy filters are baked.** Big CSS `blur()`/`drop-shadow` on moving elements are slow. Pre-render glows/gradients to a canvas at load and move that, or use the WebGL FX pass.

## 2. Project layout (what an agent creates for each video)

```
<project>/
  brief.md                 concept, audience, platform, length, the ONE idea (from motion-director)
  dna.json                 the Style DNA chosen/generated for THIS video (from style-dna)
  storyboard.md            beat sheet: time, what happens, camera, transition in, sound
  scene.html               the page (seek contract above)  — or scenes/NN-name.html + stitch.html
  assets/                  fonts, svg, images the user supplied or that were generated
  audio/                   cues.json, mix.wav, music.* (from sound-design-pro)
  out/
    stills/                contact sheets for review
    draft.mp4              review copy (30 fps, no motion blur)
    final.mp4
    qa.json  qa.md         output of qa-critique scripts
  .motion/
    style-history.json     fingerprints of previous videos (variety ledger — never delete)
```

## 3. Style DNA — a style is DATA, not code

A video never hard-codes a look. The look comes from `dna.json` (schema in `skills/style-dna/SKILL.md`). The scene reads it:

```js
const DNA = await fetch('dna.json').then(r => r.json());   // or inline the JSON in the page
```

Fields: `name`, `mood[]`, `palette{bg, ink, accent, accent2, support[]}`, `type{display, body, mono, case, tracking}`, `texture{grain, vignette, halftone, paper, scan, bloom, ...}`, `motion{personality, ease, spring, stagger, cutRate, hitStyle}`, `transitions[]`, `camera{...}`, `sound{bpm, key, palette[], mix}`, `signatureMoves[]`, `forbidden[]`.

## 4. Naming and units

- Time is **seconds** (float). Frames are `round(t * fps)`.
- Beat grid: `beat = 60 / bpm`. Put hits on `k * beat/4` (16ths) or `k * beat/2` (8ths) unless the DNA says "free time".
- Colors are authored in **OKLCH** (`Lab.oklch(l, c, h)`), shipped as hex in dna.json.
- Coordinates: origin top-left, +y down, pixels at `VIDEO.w × VIDEO.h`.
- Safe areas for 9:16 (1080×1920): keep text inside x 64–1016 and y 220–1560. Top 220 and bottom 360 px are covered by platform UI.

## 5. Events (the bridge to sound)

Whenever a visual hit, movement or reveal happens, the scene registers it with `Lab.ev(t, type, opts)` **at build time**. Types (shared vocabulary with sound-design-pro):

`impact` `hit-soft` `slam` `whoosh` `whip` `swipe` `pop` `appear` `disappear` `click` `tick` `type` `riser` `reverse` `glitch` `zap` `shimmer` `chime` `success` `error` `reveal` `drop` `boom` `bass-drop` `stinger` `scene-cut` `loop-point`

`opts`: `intensity` 0–1, `dur` seconds (motion length for whoosh/riser/type), `pitch` semitones offset, `pan` −1..1, `label` text. `render.mjs --events out/events.json` dumps them; sound-design-pro reads that file. **A scene without EVENTS cannot get tight sound.** Do not skip this.

## 6. Quality gates (nothing ships without them)

1. Concept gate — `brief.md` + 3 divergent concepts considered (motion-director).
2. DNA gate — `dna.json` exists and differs from previous videos (style-dna `dna_generate.py --check`).
3. Storyboard gate — every beat has a time, a camera, a transition, a sound.
4. Stills gate — contact sheet at every beat viewed and fixed.
5. Motion gate — `qa_video.py` reports no dead time > 0.6 s, no clipped audio, no black frames, loop seam clean.
6. Sound gate — transient of each cue within ±1 frame of its visual event; LUFS/true-peak in range (sound-design-pro).
7. Variety gate — fingerprint distance to the previous 5 videos above threshold (qa-critique).
8. Human gate — give the user 5 timestamps to check with headphones; never claim "it sounds good".

## 7. Honesty rules

- Never invent facts, numbers, quotes, logos. Placeholder bars/skeleton lines instead.
- Never reproduce someone else's brand, character, logo or watermark. Reference videos teach **technique**.
- A model cannot hear and cannot feel motion. It checks with numbers (QA scripts) and stills, and says so.
- Answer the user in the language they write in.

## 8. File locations, script paths, how pages load the runtime

Each skill ships its browser code in `skills/<skill>/runtime/`. Pages in a skill's `examples/` load runtime with relative paths:

```html
<script src="../../scene-runtime/runtime/lab.js"></script>      <!-- core, always -->
<script src="../../scene-runtime/runtime/fx.js"></script>       <!-- WebGL post-FX (bloom, halftone, grain...) -->
<script src="../runtime/<this-skill>.js"></script>
```

In a real project, run `bash skills/scene-runtime/scripts/setup.sh <project>`: it copies every `skills/*/runtime/*` into `<project>/lab/` and npm-installs three.js + fonts locally. Project pages then use `<script src="lab/lab.js">` etc.

Rendering from the pack (examples): `node skills/scene-runtime/scripts/render.mjs <page.html> <out> --root <pack root> ...` (`--root` must be a folder that contains both the page and the runtime files). Run with `NODE_PATH=$(npm root -g)` if playwright is installed globally.

Browser globals (one per runtime file, all optional except `Lab`): `Lab` (lab.js) · `FX` (fx.js) · `Trans` (transitions.js) · `Bg3D` (bg3d.js) · `Art` (art.js) · `Type` (type.js) · `UI` (ui-kit.js) · `Rig` (rig.js) · `Collage` (collage.js).

Every runtime function that draws takes explicit time/seed arguments. None reads the clock, `Math.random`, or global mutable state that changes between frames.
