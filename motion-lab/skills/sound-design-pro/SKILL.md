---
name: sound-design-pro
description: Procedural, layered, frame-locked sound design for videos made from seek(t) scenes. Turns the scene's EVENTS (events.json) into designed multi-layer sound effects (sub + transient + body + tail), aligns each transient to the visual frame, ducks and masters the mix (-14 LUFS social or -16 conservative), and checks the final file with numbers. Use when a video needs sound effects, a music bed, SFX timing fixes, "sound feels cheap / strange / late", whoosh/impact/riser/click/typing/glass/paper sounds, voice-over mixing, or an audio QA pass. Replaces the old fixed six-sample SFX kit.
---

# sound-design-pro — sound that lands on the frame

**Read this first.** Nobody in this toolchain can listen. You judge sound with spectrograms, numbers and the human's 5-timestamp check (last step). Never write "it sounds great". Write what you measured.

## Why the old kit sounded cheap and late (and what this skill does instead)
| Old behaviour | Effect | Here |
|---|---|---|
| Six fixed samples reused for every cue | everything sounds the same | 40+ procedural recipes, seeded variants, pitch/gain jitter, never the same variant twice in a row per type |
| File START placed at the cue time | whoosh/riser "late": the audible peak is 100-300 ms after the file start | every sound has a designed ANCHOR (the moment the listener hears "the hit"); the anchor is put on the frame boundary + 6 ms |
| One sound per cue | thin, "beepy" | every event is a STACK: sub + transient click + body + tail (+ lead whoosh, anticipation) |
| Oscillator beeps | cheap tone | tonal sounds are scale-tuned plucks/marimba/glass with envelopes, filtered, with reverb |
| Timbre unrelated to the look | sound and picture feel from different videos | a sound PALETTE per style (`palettes.py`), chosen by `dna.sound.palette[0]` |
| Only loudness measured | wrong spectrum slipped through | balance, alignment, clipping, structure all measured on the FINAL file |

## Scripts (all numpy/scipy; ffmpeg only for loudness cross-check and muxing)
| Script | Does |
|---|---|
| `scripts/sfxgen.py` | the designer. `--list`, `--recipe impact --intensity .9 --out x.wav`; importable `render`. Recipes: impact, hit-soft, slam, boom, bass-drop, reveal, stamp, whoosh, whip, swipe, riser, reverse, glitch, zap, shimmer, glass-ding, chime, success, error, pop, appear, disappear, click, tick, key (typing), blip family (scale-tuned), paper-rip, paper-slap, tape, camera-shutter, heartbeat, dial-tick, stinger, drone |
| `scripts/palettes.py` | style palettes: which recipe plays for which event type, extra layers, key, scale, BPM range, brightness, room. `python3 palettes.py` lists them |
| `scripts/sync_cues.py` | THE tool. events.json → cues.json + mix.wav + sound-report.md/json |
| `scripts/musicgen.py` | scratch music bed (drums, sub bass, pad, pluck, sidechain pump) in key at bpm. Licensed or user music beats it |
| `scripts/analyze_sfx.py` | measures one sound: onset, ANCHOR, attack, band shares, centroid; warns when a HIT has a slow attack |
| `scripts/qa_audio.py` | final MP4/WAV: LUFS, true peak, clipping, spectral balance, structure, per-event alignment error. Exit 1 on fail |

## Protocol (do these in order)
1. **Events exist?** Your scene must register `Lab.ev(t, type, {intensity, dur, ...})` for every hit, whoosh, reveal, type run, cut. No events → go back and add them (CONVENTIONS §5). Without them nothing can be tight.
2. **Dump:** `node skills/scene-runtime/scripts/render.mjs scene.html - --events out/events.json` (for a stitched film use the stitched page, so times are final).
3. **Pick the palette:** `dna.sound.palette[0]` (`neon-mono`, `glass-dark`, `halftone-collage`, `clay-mono`, `editorial`, `product-film`, `radial-burst`, `torn-paper`, `live-3d`, `default`). Key, scale and BPM come from the DNA.
4. **Run:**
   `python3 skills/sound-design-pro/scripts/sync_cues.py out/events.json --out audio/ --dna dna.json --fps 30 --music-gen` (scratch bed)
   or `--music bed.mp3` (the user's/licensed music), `--voice vo.wav` (ducks music + sustained SFX), `--no-music`, `--profile conservative`, `--variants 3` (A/B alternatives), `--stems`.
5. **Read `audio/sound-report.md`.** Fix every WARNING: (a) spectral balance (too sub-heavy → add body/harmonics, lower `--sfx-db` of boom/bass-drop layers or swap palette), (b) density (> 10 onsets/s is mush: remove cues in the scene, keep the big ones), (c) silence at start (hook inside the first second).
6. **Mux:** `node render.mjs scene.html out/final.mp4 --audio audio/mix.wav` (copies the already-mastered WAV; never re-normalise afterwards).
7. **Verify the final file:** `python3 skills/sound-design-pro/scripts/qa_audio.py out/final.mp4 --events out/events.json --png out/audio-qa.png`.
   Read: median alignment error should be +0…+20 ms; worst within 1 frame; `unmeasured` events are masked by louder sound (a measurement limit, not a pass).
8. **Human gate:** give the user the 5 timestamps from the report and say exactly what to listen for ("0:01.6 slam: transient on the title hit? 0:04.7 whip into cut: peak on the cut frame?"). Offer `--variants` if they dislike a sound.

## The timing rules in one screen (full text: reference/timing-rules.md)
- Frame boundary = `round(t*fps)/fps`. Anchor = boundary + 6 ms. Polished references measure +7…+19 ms; never early, never later than +45 ms.
- **Hits**: the transient is the anchor. **Whoosh/swipe/whip**: anchor at 35-60 % of the motion (the peak). **Risers/reverses END on the anchor** (they need `dur` = the build length, so give `dur` to Lab.ev). **Typing**: one key per step on its own frame.
- Add an **anticipation**: 3 frames before a hero hit a whip/reverse (sync_cues does it for `scene-cut`, `slam`, `riser`). 120 ms of near-silence before a hero hit is a tool: music and sustained layers dip.
- Priority: voice > hits > music. Big hits duck music 3.5 dB for 150 ms. Voice ducks music + sustained SFX 8 dB.
- Hook: a sound inside the first second (frame 0-10). Silence is allowed mid-video (10-20 %) but not at the start.

## Decision tables
**Which event type for what?**
| On screen | Event | Notes |
|---|---|---|
| Title/number slams in, shake | `slam` (once per video) / `impact` | intensity 0.8-1.0 |
| Small object lands, card settles | `hit-soft` | no crack |
| Element pops in / text word appears | `pop` or `appear` | tonal walk if palette has `tonal` |
| Whip pan, fast slide, swipe | `whoosh` `swipe` `whip` | pass `dur` = motion length |
| Scene change | `scene-cut` | auto pre-whip + soft hit |
| Build-up before a reveal | `riser` (dur) | ENDS on the reveal hit |
| Count-up / dial | `tick` repeated or `dial-tick` | pitch rises with value |
| Typing | `type` with `dur` | one key per step |
| Success / done | `success` `chime` | key-tuned |
| Glitch / RGB split | `glitch` `zap` | |
| Paper / tape / stamp looks | `paper-slap` `paper-rip` `tape` `stamp` | torn-paper, halftone palettes |
| Loop seam | `loop-point` | reverse swell into frame 0 |

**Which profile?** `social` (-14 LUFS, TP -1.0) for TikTok/Reels/Shorts. `conservative` (-16 LUFS, TP -4) for broadcast-ish, YouTube long form, anything re-encoded twice.

## Variation knobs (so two videos never share a sound)
| Knob | Where |
|---|---|
| palette | `--palette` or `dna.sound.palette[0]` |
| key / scale | `--key A --scale minor` (tonal blips, chimes, risers follow) |
| brightness 0..1 | `--brightness` (shifts transient and air) |
| bpm | `--bpm` (music + beat-snapped cues if `--bpm-fixed`) |
| variants | `--variants N`, `--seed` |
| layer trim | palette `drop`, `swap`, `add` entries (edit `palettes.py`) |
| room size | palette `room` multiplier |

## Weak-model protocol
1. Do not write your own synth code. Call `sync_cues.py`.
2. Do not hand-place sounds on a timeline. Register events in the scene.
3. If a warning says "sub-heavy", lower sfx level or choose a brighter palette; do not mute the sub entirely.
4. Always run `qa_audio.py` on the FINAL mp4 and quote the numbers.
5. Always end with the 5-timestamp human check. Never say it sounds good.

## Failure modes
| Symptom | Cause | Fix |
|---|---|---|
| Sound feels late | scene registered the event at the END of the motion, or mux offset | event time = frame the picture hits; check `audio start vs video start` in qa_audio |
| Whoosh peaks after the hit | `dur` missing → default 0.6 s | pass the real motion length as `dur` |
| Mush | > 10 events/s or long tails over each other | thin out events; use `hit-soft` for small ones; palette `drop` |
| Harsh, thin | `brightness` too high / too many `click` layers | lower `--brightness`, `swap` pop→hit-soft |
| Booming on phone speakers | 75 %+ under 120 Hz | add body: `--brightness .55`, or lower boom/bass-drop layers |
| Voice buried | no `--voice` passed | pass `--voice`: sidechain ducking applies |
| Clipping after encode | TP too hot | use `--profile conservative` |

References: `reference/event-vocabulary.md` · `reference/layering-recipes.md` · `reference/timing-rules.md` · `reference/mix-targets.md` · `reference/style-sound-palettes.md` · `reference/music-beds.md` · `reference/honesty-and-human-check.md`.
