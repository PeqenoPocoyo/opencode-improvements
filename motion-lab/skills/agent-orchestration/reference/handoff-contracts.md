# Handoff contracts

Workers snap together only if the seams are specified before they start.

## 1. Scene file contract
Every `scenes/NN-name.html`:
```js
window.VIDEO  = { w: 1080, h: 1920, duration: SLOT_SECONDS, fps: 30 };   // identical w/h/fps across scenes
window.seek   = t => {...};           // local time, 0..duration
window.EVENTS = [ {t: LOCAL_SECONDS, type, intensity, dur, label} ];     // via Lab.ev
```
- Fonts embedded or served from the project's `lab/` or `assets/` folders. Same families as DNA.
- Colours only from DNA (use `Lab.mixColor` for tints).
- Overscan: every scene draws 4% beyond the frame so camera moves and whip transitions never reveal edges.

## 2. Entry / exit states (kills seam pops)
In `storyboard.md` give each seam a row:

| seam | out-state of scene N (last frame) | in-state of scene N+1 (first frame) | transition | overlap |
|---|---|---|---|---|
| 1→2 | big white numeral "7" centered, scale 1.0 | "7" centered scale 1.0 on new bg | match-cut (carry) | 0 |
| 2→3 | blank dark frame, grain only | blank dark frame | whip pan 10 frames | 10f both scenes held |

Rules: a carried element has identical position/scale/colour in both pages at the seam; a whip/dissolve needs both scenes to keep drawing during the overlap (scene A holds its last pose, scene B starts 'pre-rolled' by overlap seconds).

## 3. Event time offsets
Stitched time = scene start + local t. `stitch.html` registers all events with the offset when it composes. Workers use local times only. Do not let a worker offset its own events.

## 4. Stitch options
| Option | How | Use when |
|---|---|---|
| Iframes | `stitch.html` has N iframes, calls `contentWindow.seek(local)` | simplest; transitions via CSS/canvas snapshots |
| Canvas snapshots | each scene exposes `window.drawTo(ctx,t)`; stitch composites with `Trans` shaders | shader transitions between scenes |
| Single page | engineers write functions `scene02(t)` instead of pages; director concatenates | tiny jobs, one engineer |
| ffmpeg | render each scene to mp4, then `xfade`/concat | scenes are huge/independent; no shader transitions needed |

Pick one in the spine and state it in every brief.

## 5. Data contracts
- `dna.json` — immutable during the job (director edits only).
- `storyboard.md` — director edits only; workers propose changes in reports.
- `assets/MANIFEST.md` — asset builder; scene engineers read.
- `out/events.json` — produced by `render.mjs --events` on stitched draft; sound designer reads.
- `audio/cues.json`, `audio/mix.wav` — sound designer; director muxes.

## 6. Verification commands (run after each wave)
```bash
python3 skills/agent-orchestration/scripts/manifest.py diff <project>      # who touched what
python3 skills/qa-critique/scripts/lint_scene.py <project>/scenes/*.html
node skills/scene-runtime/scripts/render.mjs <scene.html> <project>/out/stills/sNN.png --stills 0,0.3,0.6,0.9 --root <project>
node skills/scene-runtime/scripts/render.mjs <scene.html> - --events <project>/out/ev-NN.json --root <project>
```
