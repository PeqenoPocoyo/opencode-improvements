---
name: motion-director
description: The entry point for making any motion graphic, intro, reel, short, explainer, product film, loop or animated art piece in code. Runs the full pipeline - brief, three divergent concepts, Style DNA, storyboard with a beat grid, scene building, stills review, motion QA, sound, variety check, human check - and decides which other motion-lab skills to load. Use FIRST for any request to make or improve a video, animation, motion design, kinetic type piece, 3D background, UI-in-video demo, or when videos come out generic, samey, badly paced or badly timed.
---

# motion-director — think like a director, then build

Weak models fail at video by jumping to code. A director decides the IDEA, the LOOK, the RHYTHM and the SOUND first, in writing, then builds. This skill is that order of work. It never produces code by itself; it routes to the skills that do.

## Pipeline (each gate must be passed in order; write the artifact named)
| # | Gate | Artifact | Tool/skill | Pass condition |
|---|---|---|---|---|
| 0 | Setup | project folder | `bash skills/scene-runtime/scripts/setup.sh <project>` | lab/ runtime + fonts copied |
| 1 | Brief | `brief.md` | this skill | idea, audience, platform, length, tone, must-include, what NOT |
| 2 | Concepts | `concepts.md` | `reference/concept-methods.md` | 3 divergent concepts (different metaphor, palette logic, motion personality); one chosen WITH a reason |
| 3 | DNA | `dna.json` | `style-dna` | `dna_generate.py --check` passes |
| 4 | Storyboard | `storyboard.md` | `reference/beat-sheets.md` + `storyboard-template.md` | every beat has time (on beat grid), what, camera, transition in, events/sound |
| 5 | Build | `scene.html` or `scenes/NN-*.html` | scene-runtime + the specialist skills | lint clean, events registered |
| 6 | Stills | `out/stills/*.png` | `render.mjs --stills` | contact sheet viewed at EVERY beat, defects fixed |
| 7 | Motion QA | `out/qa.json` | `qa-critique` | no dead time > 0.6 s, no black frames, loop seam clean |
| 8 | Sound | `audio/mix.wav` | `sound-design-pro` | alignment within 1 frame, LUFS/TP ok |
| 9 | Variety | ledger | `style-dna --check`, `fingerprint.py --check` | not SAME_SOUL |
| 10 | Human | message | `sound-design-pro/reference/honesty-and-human-check.md` | 5 timestamps given |

If the harness has sub-agents, load `agent-orchestration` after gate 4 to split the build. If not, use its sequential-persona mode. Never skip gates 2, 3, 6, 10.

## Step 1 — the brief (ask at most ONE question, only if the idea is truly missing)
Write `brief.md`:
```
IDEA (one sentence, a claim or feeling, not a topic): ...
AUDIENCE / PLATFORM: ... (9:16 Shorts/Reels/TikTok | 16:9 YouTube | 1:1 | loop | ...)   LENGTH: ... s   FPS: 30 (60 for UI/glass)
TONE (3 words): ...        MUST INCLUDE: ...        MUST NOT: ...
ASSETS GIVEN: logos? footage? voice? music? fonts? colours?   (if none: procedural only)
LANGUAGE of on-screen text: the user's language
SUCCESS TEST: after the first second a stranger knows ___; at the end they feel ___
```
Defaults if unspecified: 9:16, 1080x1920, 30 fps, 12-20 s, loop if <= 8 s.

## Step 2 — three divergent concepts
Use `reference/concept-methods.md`. Output `concepts.md` with three concepts that differ in at least three of: metaphor, material, palette logic, motion personality, camera, type character, structure. For each: one-line pitch, the opening image (frame 0), the signature move, the last frame, and why it serves the idea. Then choose with a written reason. If two concepts feel similar, replace one.

## Step 3 — DNA
`python3 skills/style-dna/scripts/dna_generate.py --candidates 3 ...` seeded by the mood words of the three concepts, or `--preset X --mutate N`. Validate with `--check`. Copy chosen to `dna.json`.

## Step 4 — storyboard
Beat sheet by length (`reference/beat-sheets.md`), table in `reference/storyboard-template.md`. Times on the beat grid of `dna.sound.bpm`. Rules:
- Frame 0-10 shows the hook (a shape, number, movement). Never a black frame or a logo.
- One new idea per beat; 2-4 s per beat for short-form (DNA `cutRate` decides).
- Each beat changes >= 2 of {background tone, object type, type treatment, camera move}.
- Each seam names its transition (from `dna.transitions`) and whether an element is carried across.
- Each beat lists `Lab.ev` events (type, time, dur) so sound can be built.
- Last beat: payoff + loop point or end card; the end frame is designed, not a fade to black.

## Step 5 — which skills build what
| Need | Load |
|---|---|
| runtime, render, seek contract | `scene-runtime` |
| text, captions, numerals | `kinetic-typography` |
| backgrounds, 3D, studio, environments without images | `generative-3d-backgrounds` |
| generative art, patterns, particles, flow fields | `motion-canvas-artwork` |
| transitions, 2D->3D projection, device mockups | `transitions-projections` |
| app interface in video, cursor, charts | `ui-in-video` |
| paper, halftone, collage, torn edges | `collage-paper-texture` |
| stylised people and props, silhouettes | `vector-characters` |
| real footage + CG, talking head + cutaways | `live-action-compositing` |
| edit grammar, pacing, captions planning | `video-orchestration` |
| free creative exploration, series, mutations | `generative-play` |
| sound | `sound-design-pro` |
| lint, QA, fingerprint | `qa-critique` |
| splitting work among agents | `agent-orchestration` |

## Step 6 — build loop (per beat, never all at once)
1. Build the beat. 2. `render.mjs scene.html out/stills/b03.png --stills <3-5 times in the beat>`. 3. LOOK. Fix: clipping, overlap, contrast, empty areas, alignment, safe area. 4. Next beat.
After all beats: full-video stills every 1.0 s, then `qa_video.py`.

## Step 7 — revision rules
Change ONE axis per revision (palette, type, timing, camera, texture). Re-render stills of the affected beats only. Max 3 loops, then deliver with known issues listed.

## Step 8 — delivery message (short)
What it is (one sentence), the DNA name and constraint, files (`final.mp4`, `scene.html`, `dna.json`), what was verified (lint, stills, QA numbers), what was NOT verified (sound heard by a human; real-device playback), the 5 timestamps to check, one next step. In the user's language.

## Quality bar (ask yourself before delivering)
1. Would a stranger describe it in one sentence? (idea clarity)
2. Is there a recognisable look that is not the previous video's? (DNA, fingerprint)
3. Does something change every 0.3-0.6 s and a bigger thing every 2-4 s? (rhythm)
4. Is there one big hit and are there holds? (dynamics)
5. Is every hit registered as an event and aligned? (sound)
6. Is every text readable in the safe area for >= its reading time? (12-17 chars/s)
7. Is texture visible? Is the camera never dead? (finish)

## Weak-model protocol
1. Never write scene code before gates 1-4 exist as files.
2. Never reuse a palette, font, easing or scene list from memory: they come from `dna.json`.
3. Never claim sound or smoothness you did not measure; quote numbers.
4. If stuck on creativity, run a concept-methods card (reference/concept-methods.md §3) instead of reaching for a default.
5. If the user gives a reference video, extract technique (reference-analysis style notes), not content or brand.

## Failure modes
| Symptom | Cause | Fix |
|---|---|---|
| "Looks like the last video" | skipped gate 2/3 or reused DNA | re-run candidates; `--check` |
| Pacing feels random | beats not on the beat grid, no holds | rewrite storyboard times; add holds |
| Hook is weak | opens on black/title card | move the strongest image to frame 0-10 |
| Everything moves all the time | no hierarchy | pick 1 hero element per beat; others settle |
| Text unreadable | too small/fast/outside safe area | sizes from type-character.md; hold = chars/15 s |
| Sound off | events missing | add `Lab.ev` per hit; rerun sound pipeline |

References: `reference/concept-methods.md` · `beat-sheets.md` · `hooks-and-openers.md` · `storyboard-template.md` · `anti-sameness.md`.
