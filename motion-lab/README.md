# motion-lab — a training pack for weaker models that make motion graphics

Built on top of **Claude Motion + the "Motion Graphics" skill pack** (kept intact; fixed copies in `patched-existing-skills/`).
Goal: models like GLM 5.3 Flash or Step 5 Preview (harness "Beam") must stop producing videos with "the same soul", odd SFX and poor timing — by being **very explicitly instructed**, by **machines that create diversity** (DNA generator, crossbreeding), by **procedural runtimes** (no stock images needed) and by **gates/hooks** that force a QA ritual.

## 30-second tour
```
CONVENTIONS.md                 the contract (seek(t) purity, project layout, events, quality gates)  <- read first
instructions/                  system-prompt rules, weak-model playbook, 7 ready prompts (new-video, ui-film, sound-pass, orchestrate-big-video, fix-same-soul, ...)
hooks/                         5 hooks + guard.sh fallback + tests (12 pass)
skills/
  motion-director              concept + gates + beat sheets + hooks/openers  (START HERE)
  style-dna                    12 presets + generator + variety ledger ("soul" fingerprint)
  scene-runtime                lab.js (timing/ease/noise/camera/events) + fx.js (WebGL post) + render.mjs (stills/mp4/--alpha) + setup.sh
  generative-3d-backgrounds    28 GLSL worlds + three.js kit (clay, creased geometry)  - no images
  motion-canvas-artwork        34 generative 2D art generators (Art.draw)
  kinetic-typography           Type runtime + 32 embedded fonts + style catalog
  ui-in-video                  app interfaces (dashboard, chat, cursor, toasts, charts) as film
  transitions-projections      43 GLSL transitions + perspective warp / projection mapping
  collage-paper-texture        paper cutouts, torn edges, tape, stamps, ransom type, boil           (new)
  vector-characters            biped (IK), blob, bot, faces (blink/look/talk), footsteps events      (new)
  live-action-compositing      graphics over real footage: prep, tracking, grade/grain/light match, alpha overlay (new)
  sound-design-pro             events -> layered procedural SFX + music + mix (-14 LUFS social), qa_audio
  qa-critique                  lint, qa_video, contact sheet, frame_diff, fingerprint, rubric, slop kill list
  generative-play              "no brief" mode: crossbreed -> 8 pieces -> choose -> deepen
  video-orchestration / agent-orchestration   big jobs split across <=3 sub-agents, verified on disk
patched-existing-skills/       overlay + fixes for the ORIGINAL explainer-*/motion-broll/sound-effects skills (+ patch script)
reference-analysis/            what the 11 reference videos teach (technique, not copying)
examples/previews/             rendered previews of the example pages
```

## Install
1. Copy the folder anywhere (e.g. `~/motion-lab`). Requirements: Node 18+, `npm i -g playwright && npx playwright install chromium`, ffmpeg, Python 3.9+ with numpy, Pillow, opencv-python (for live-action only).
2. Make the skills visible to your harness: copy/symlink `skills/*` into its skills folder (e.g. `~/.config/opencode/skills/`, `.claude/skills/`), or point the harness at `skills/`.
3. Paste `instructions/MOTION-LAB-RULES.md` into the system prompt / AGENTS.md of the weak model (it is short on purpose).
4. Hooks (optional but strongest): see `hooks/README.md`. Without hooks the model runs `hooks/guard.sh` by hand (the rules tell it when).
5. Optional: apply the patches to the original skills: `python3 patched-existing-skills/patch_old_skills.py <orig skills dir> --out patched`.

## Use
```bash
bash skills/scene-runtime/scripts/setup.sh myvideo            # project skeleton + all runtimes + fonts + three.js
python3 skills/style-dna/scripts/dna_generate.py --candidates 3 --out-dir myvideo/dnas   # pick ONE, write dna.json
# write scene.html (seek(t) contract), then:
node skills/scene-runtime/scripts/render.mjs myvideo/scene.html myvideo/out/stills.png --stills 0.5,2,4,6 --root myvideo
node skills/scene-runtime/scripts/render.mjs myvideo/scene.html myvideo/out/draft.mp4 --fps 30 --workers 4 --root myvideo
node skills/scene-runtime/scripts/render.mjs myvideo/scene.html - --events myvideo/out/events.json --root myvideo
python3 skills/sound-design-pro/scripts/sync_cues.py myvideo/out/events.json --out myvideo/audio --dna myvideo/dna.json --music-gen --profile social
python3 skills/qa-critique/scripts/qa_video.py myvideo/out/draft.mp4
```
"Surprise me" mode: `python3 skills/generative-play/scripts/play_make.py --project myvideo --n 8 --seed 42`.

## Honest limits
- Models (and this pack) **cannot hear**. Sound is built from layered procedural recipes, checked by numbers (LUFS, true peak, alignment ±1 frame, spectral balance); the report gives **5 timestamps for a human to listen to**.
- The "same soul" fingerprint threshold (0.18) is a heuristic; the 11 reference videos were not on disk when the pack was calibrated. Tune it in `qa-critique/scripts/fingerprint.py` after you compare real outputs.
- DOM scenes render ≈0.45 s/frame at 1080x1920 in software (SwiftShader): a 12 s draft takes minutes. WebGL-heavy scenes are slower. Use draft stills first.
- Tracking is planar only (no 3D solve, no rotoscope/keying). Collage/rig/ui are 2D procedural looks, not photo-real.
- Google Fonts are blocked in sandboxes: fonts are bundled (OFL, see `kinetic-typography/fonts/LICENSES.md`).
