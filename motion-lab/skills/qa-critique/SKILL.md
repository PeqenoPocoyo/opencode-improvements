---
name: qa-critique
description: Quality gate for motion videos - lint the scene source, render a contact sheet and LOOK at it, run technical QA on the mp4 (size/fps, dead time, black/flash, hook strength, loudness, clipping, event density), prove the video does not share the previous videos' "soul" with a numeric fingerprint, and run a structured revision loop (max 3 passes). Use before delivering ANY video, after every render, when the user says the result is "paia/meh/igual ao anterior", or to review/critique a video.
---

# qa-critique — never deliver what you have not looked at

Weak models skip checking. This skill makes checking a fixed ritual with commands and a rubric.

## The ritual (every render)
```bash
python3 skills/qa-critique/scripts/lint_scene.py scene.html --dna dna.json     # 1. static lint (exit 1 = fix first)
node skills/scene-runtime/scripts/render.mjs scene.html out/s.png --stills <6 times at beat ends> --cols 3 --scale 540   # 2. stills; READ the png
node skills/scene-runtime/scripts/render.mjs scene.html out/draft.mp4 --fps 30 --sub 1 --workers 4 --audio audio/mix.wav  # 3. draft (≈0.45 s/frame at 1080x1920 DOM scenes)
python3 skills/qa-critique/scripts/qa_video.py out/draft.mp4 --expect-w 1080 --expect-h 1920 --expect-fps 30 --expect-dur 15 --events out/events.json
python3 skills/qa-critique/scripts/contact_sheet.py out/draft.mp4 out/sheet.png --n 24     # 4. READ the sheet with the Read tool
python3 skills/qa-critique/scripts/frame_diff.py out/draft.mp4                              # 5. pacing strip, dead zones
python3 skills/qa-critique/scripts/fingerprint.py out/draft.mp4 --name <project> --add      # 6. soul check vs last 5 videos (exit 1 = too close)
```
Then score with `reference/rubric.md`, apply `reference/slop-kill-list.md`, and follow `reference/revision-loop.md`.

## What each tool catches
| Tool | Catches |
|---|---|
| `lint_scene.py` | non-deterministic code (Math.random, Date, rAF, timers, CSS animation), blocked fonts/URLs, missing `VIDEO/seek/EVENTS/__ready`, stock AI palette, DNA ignored, one easing everywhere, tiny text |
| `qa_video.py` | wrong size/fps/pix_fmt, odd dimensions, duration drift, dead time, black/flash/flicker, **weak hook**, loudness outside −20…−11 LUFS, true-peak clipping, silence gaps, event density |
| `contact_sheet.py` | what the film actually looks like: composition, legibility, repeated frames, clutter, consistency |
| `frame_diff.py` | motion energy per second; still stretches; hard cuts |
| `fingerprint.py` | "same soul": hue/sat/contrast/texture/motion/cuts signature distance to the last 5 videos |

## Honest limits
- Nobody (model or script) can *hear* the video: sound is verified by numbers + the 5 timestamps for a human (see sound-design-pro/honesty-and-human-check).
- Fingerprint threshold 0.18 is a tripwire, not a proof of quality.
- QA proves "no obvious defects", not "good". The rubric + a human look decide "good".

## Files
`scripts/{lint_scene,qa_video,contact_sheet,frame_diff,fingerprint}.py` · `reference/{rubric,slop-kill-list,revision-loop}.md`
