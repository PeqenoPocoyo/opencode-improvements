---
name: live-action-compositing
description: Put generated graphics (UI, titles, cutouts, 3D cards, collage) on top of REAL footage so they look filmed - transparent overlay render, planar tracking, grade/grain/light matching, cutaway planning from a transcript. Use when the user supplies a video/photo and wants motion graphics added, or a talking-head/screen-recording enhanced.
---

# live-action-compositing — graphics that belong in the shot

Scripts (OpenCV + numpy + ffmpeg, all tested on synthetic footage): `scripts/`
`prep_footage.py` → `track_points.py` → render overlay with `render.mjs --alpha` → `grade_match.py`/`grain_measure.py`/`light_direction.py` inform the overlay → ffmpeg composite.

## The pipeline (do in this order)
1. **Prep:** `python3 scripts/prep_footage.py clip.mov --out prep --fps 30 --height 1920`. Gives normalised video (constant fps, rotation applied), a small proxy, 12-frame sheet (READ it), LUFS, scene cuts, luma/colour stats.
2. **Understand the shot:** `light_direction.py prep/clip.norm.mp4` (where shadows should fall, how soft) · `grain_measure.py` (noise to copy) · note camera motion (static / handheld / pan) from the sheet and from `frame_diff.py` energy.
3. **Plan what goes where:** talking head with a transcript → `plan_cutaways.py captions.srt` (cutaway table with sound events). No transcript → mark topic changes yourself every 4–7 s. Coverage target 20–40 % of runtime; never cover the face in the first 0.8 s of a line.
4. **Track if the graphic must stick to something:** `track_points.py prep/clip.proxy.mp4 --quad "x,y;x,y;x,y;x,y" --out track.json --scale <full/proxy>`. Check `lost_frames` (0 is the goal) and `err` (< 1.5 px). Textureless wall/sky = it will lose; then pin by hand with 3–5 keyframes and `Lab.kf`.
5. **Build the overlay scene** as a normal seek(t) page with a TRANSPARENT background (`html,body{background:transparent}`, `ctx.clearRect` not a fill). Use `examples/css3d-glass-folder.html` as a pattern for CSS-3D layers. If tracked, wrap the stage in `Trans.matrix3dFromQuad` / CSS `matrix3d` using `track.json` quads at `Math.round(t*fps)`.
6. **Render overlay:** `node skills/scene-runtime/scripts/render.mjs overlay.html out/overlay.mov --alpha --fps 30 --workers 4` (ProRes 4444 with alpha).
7. **Match:** apply grade & grain to the OVERLAY, not the footage: `grade_match.py --ref prep/clip.norm.mp4 --layer layer.png ...` for still layers (or copy its numbers into canvas filters), FX grain at the measured amount (`grain_measure.py` → `suggestion`), blur edges by the footage's softness (0.5–1.2 px), and cast shadows with `light_direction.py` `paste` values.
8. **Composite + audio:** `ffmpeg -i prep/clip.norm.mp4 -i out/overlay.mov -filter_complex "[0][1]overlay=format=auto,format=yuv420p" -map 0:a? -c:a copy out/comp.mp4` then run the sound pass (`sound-design-pro`, events from the overlay) and mix UNDER the dialogue: `sync_cues.py out/events.json --voice dialogue.wav ...` if the footage has speech (voice ducks music 8 dB; dialogue stays the loudest element).
9. **QA:** `qa_video.py`, contact sheet at the overlay's arrival times (READ), compare an overlay frame vs raw footage side by side: do blacks match? does the shadow agree with the real light? is the grain the same size?

## Rules (what makes it look filmed instead of pasted)
- **Never pure black (#000) or pure white** layers over footage: lift blacks to the footage's black point (`grade_match.py` does), roll off whites.
- **Same grain** as the footage; digital layers are too clean and give themselves away first.
- **Light agrees.** One light direction, one softness. A hard drop shadow on a soft-lit shot is the #1 giveaway.
- **Edge softness:** footage is never razor sharp; blur overlay edges 0.5–1.2 px, add 1 px chromatic offset if the footage has any.
- **Motion agrees.** If the camera is handheld, the overlay must share the sway (track it, or apply `Lab.handheld` at the footage's amplitude: measure with `frame_diff.py`). A pinned graphic on a moving camera must be tracked.
- **Occlusion:** if a hand/person crosses the pinned graphic, either cut at that moment or mask (rotoscope is not available: choose another time or place the graphic beside the subject).
- **Entrance on the beat of the speech, not the clock:** start cutaways 0.15 s before the keyword, end 0.25 s after the line (J-cut feel).
- **Don't change the footage's audio level;** duck music under it.
- **Honesty:** say which steps are measured (numbers) and which are your judgement; you cannot see motion, only stills.

## Dealing with different inputs
| Input | Special handling |
|---|---|
| Phone vertical clip | `prep_footage` handles rotation; keep safe areas from CONVENTIONS §4 |
| Screen recording | Likely static: no tracking; use zoom-ins (scale + crop of the footage in ffmpeg `zoompan` or canvas) and UI callouts from `ui-in-video` |
| Photo (still) | Treat as a 6 s clip: add Ken-Burns (`Lab.camera`) and parallax layers; light/grain scripts accept images |
| Green screen | Not handled (no keyer here). Ask the user for a pre-keyed ProRes/WebM with alpha |
| Long footage (> 2 min) | Prep once, work on the sections; never render the full length until the plan is approved |

## References
`reference/compositing-theory.md` (why layers look fake and each fix) · `reference/cutaway-grammar.md` (cutaway timing, J/L cuts, overlay types per sentence kind) · `reference/ffmpeg-recipes.md` (composite, zoom, speed ramp, crop-to-vertical, blur-behind, burn captions).
