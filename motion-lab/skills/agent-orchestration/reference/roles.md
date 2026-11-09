# Role cards

Each card: mission, writes, reads, inputs it needs, definition of done, typical mistakes, a ready one-line mission you can paste at the top of a brief.

## Director (the orchestrator — you, never delegated)
- Mission: own the idea and the integration. Decide; do not draw.
- Writes: `brief.md`, `dna.json`, `storyboard.md`, `ORCHESTRATION.md`, `stitch.html`, final delivery message.
- Done: all quality gates in CONVENTIONS §6 pass or are waived with a reason; the user got 5 timestamps.
- Mistakes: delegating the concept (workers default to the average look); skipping verification; letting workers change DNA.

## Art director / look-dev
- Mission: prove the look before scenes exist.
- Writes: `lookdev/specimen.html`, `lookdev/sheet.png`, `lookdev/notes.md` (palette ramp, type specimen at real sizes, texture sample, one hero frame).
- Reads: brief, DNA seed, style-dna references.
- Done: one still that a stranger would call a *style*, not a template; contrast checks; a list of 3 DNA tweaks.
- Mistakes: gradient-on-dark default; fonts not embedded; no texture.
- Mission line: "Build a one-frame look test for this DNA at 1080x1920 and report 3 concrete DNA tweaks. Write only under lookdev/."

## Scene engineer (one worker per scene, or per 2 short scenes)
- Mission: deliver one scene exactly to the storyboard row.
- Writes: `scenes/NN-name.html` and, if needed, `scenes/NN-name.assets/`.
- Reads: DNA, storyboard row NN and its neighbours (entry/exit states), runtime docs.
- Contract: standalone page; local time 0..slot duration; `window.VIDEO` with the project's w/h/fps and `duration` = slot; EVENTS registered with LOCAL times; first and last frames match the entry/exit state in the storyboard; all colours from DNA.
- Done: lint clean; still sheet at 5+ times looked at; EVENTS dump non-empty.
- Mistakes: own palette; scene longer/shorter than slot; forgetting the entry state so the seam pops; heavy filters.
- Mission line: "Build scene 03 (3.0 s) of the storyboard as scenes/03-*.html. Write only that file and its .assets folder."

## Asset builder
- Mission: make things scenes need and nobody should build twice (a procedural 3D prop, a texture tile, an SVG icon set, a subsetted font).
- Writes: `assets/**` and `assets/MANIFEST.md`.
- Done: manifest lists name, size, intended scene, how to load; every asset renders on its own.
- Mistakes: raster images with no licence; unseeded randomness; huge files (keep total under 3 MB unless told).

## Sound designer
- Mission: tight, layered, style-matched sound from the final events.
- Needs: `out/events.json` from the STITCHED draft (final timing), `dna.json` (sound block), optional voice file.
- Writes: `audio/**`.
- Done: `cues.json`, `mix.wav`, `sound-report.md`; qa_audio passes; the report lists the 5 riskiest timestamps for a human.
- Mistakes: working from the storyboard instead of final timing; claiming it sounds good.
- Mission line: "Run sound-design-pro on out/events.json with the DNA sound palette; write only under audio/."

## QA critic (separate context — it must not have seen the work being made)
- Mission: judge honestly with numbers and stills.
- Writes: `out/qa/**` only. Never edits scenes.
- Reads: draft video, events, rubric, fingerprint history.
- Done: `qa.json`, `qa.md`, rubric scores, a fix list of at most 5 items ordered by impact, each naming file + parameter.
- Mistakes: praising; vague fixes ("improve pacing"). Say "scene 02 hold 0.9 s -> 0.4 s at storyboard row 2".
- Why separate: a worker grading its own output is lenient.

## Researcher
- Mission: gather facts or visual references the video must be correct about.
- Writes: `research/notes.md` with source URLs.
- Rule: facts without a source do not enter the video. If nothing is found, the video uses placeholders.

## Integrator (usually the Director)
- Mission: stitch, normalise, render, dump events, mux.
- Checks: seams (last frame of N vs first frame of N+1 under the chosen transition), total duration, event times offset by each scene's start (`start + local_t`).

## How many agents for which job
| Job | Roles |
|---|---|
| 6–10 s logo sting | Director only (+ QA at end) |
| 15 s social short, one idea | Director, 1–2 Scene engineers, Sound, QA |
| 30–60 s explainer / product film | Director, Art director, 3–5 Scene engineers, Asset builder, Sound, QA |
| Loopable art piece | Director + 1 Scene engineer + Sound |
| New skill/runtime for the pack | one worker per skill folder (this pack was built that way) |
