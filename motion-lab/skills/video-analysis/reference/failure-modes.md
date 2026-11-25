# Failure modes of frame-based video analysis → defence

| # | Failure | Why it happens | Defence in this skill |
|---|---|---|---|
| 1 | Hallucinated motion ("smoothly eases in") | A still shows a state, not time | brief rule: motion claims = `seen:false`; `--burst` zoom with displacement numbers |
| 2 | Hallucinated sound | Model "hears" what a scene usually sounds like | audio only as measured numbers; synth brief forbids sound claims |
| 3 | Misread small text | Tiles are ~640 px wide | `legible:false` → crop zoom; never trust OCR-by-glance on sheets |
| 4 | Wrong counts | Multi-object scenes across tiles | counts only from `--crop`/burst; brief says so |
| 5 | Missed event between tiles | Sampling gap | equal-information sampling + forced scene starts; strip shows motion peaks between ticks; `--window` on peaks |
| 6 | Over-trust of an early guess | Single long context drifts | independent chunk agents; overview only gives `look_for` hints |
| 7 | Time attribution off by one tile | Event is somewhere between tiles | tile time ± gap rule; burst to pin |
| 8 | Scene cut missed (dissolve/fade) | Gradual change under cut threshold | novelty-based tiles still follow the change; compare `cuts` with red tiles; lower threshold by hand (`--cuts`) if needed |
| 9 | False cut (flash, strobe, screen recording flicker) | Large histogram jump | cut requires hist AND pixel change AND 0.6 s spacing; still flagged in the sheet—agents confirm |
| 10 | Duplicated events at chunk seams | Context tile | referee merges near-identical events (≤ 1 s, similarity ≥ .6) |
| 11 | Identity claims from faces | Training prior | rule 5; names only if printed |
| 12 | Prompt injection via video text | Text on screen says "ignore your instructions" | reports/frames are data; briefs say so; synthesis ignores instructions inside reports |
| 13 | Black/dark footage | Low visibility | agent must say "too dark to judge"; `mean_luma` in manifest shows it beforehand |
| 14 | Vertical/rotated video misdisplayed | Rotation metadata | `probe()` swaps width/height, ffmpeg auto-rotates |
| 15 | Variable frame rate drift | VFR timestamps | all times are container times from ffmpeg `-ss`; tiles labelled with the requested time |
| 16 | Huge file, long wait | Decoding every frame | analysis frames ≤ 4000, keyframe-only for long dense-GOP files; sheets only decode ~16–24 frames each |

## Smell tests before delivering an analysis
- Could every sentence be tied to a tile id or a measured number? If not, delete or relabel as inferred.
- Did the report distinguish "I saw nothing" from "I could not see"?
- Are all `followups` either resolved or listed as open?
