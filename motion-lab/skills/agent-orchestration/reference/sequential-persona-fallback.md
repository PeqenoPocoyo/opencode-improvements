# Mode C — sequential personas (no subagents needed)

For harnesses without a subagent tool (many open-source CLIs), and for small models that cannot reliably delegate. The same partition, executed by ONE model, one role at a time. The discipline is the point: each persona has a narrow job, a write boundary and an exit checklist, and you do not cross it.

## How it works
1. Create `ORCHESTRATION.md` with the ownership table and a checklist per persona (see `templates/ORCHESTRATION.md`).
2. Run personas in order. At the start of each, write one line to `ORCHESTRATION.md`: `[PERSONA: scene-engineer 02] start`. Re-read only the files that persona needs (DNA, its storyboard row). This keeps context small and the look consistent.
3. At the end of each: run the exit checklist (lint, still, events). Mark done.
4. Switching persona = switch mindset: the QA persona is allowed to be harsh; the scene persona is not allowed to touch DNA.

## Persona order for a video
1. DIRECTOR — brief, 3 concepts, choose, DNA, storyboard, seam table. Exit: storyboard has times, camera, transition, sound for every row.
2. ART DIRECTOR — one look-test still. Exit: palette, fonts, texture visible; contrast fine.
3. SCENE ENGINEER #1..N — one scene per pass. Exit: lint, 4–5 stills looked at, EVENTS dumped, duration = slot.
4. INTEGRATOR — stitch, draft render, whole-video events. Exit: seams checked by stills at each boundary ±3 frames.
5. SOUND DESIGNER — sound-design-pro on events.json. Exit: qa_audio, 5 timestamps.
6. QA CRITIC — read the rubric cold. Score each criterion with evidence from stills/numbers. Exit: ≤ 5 fixes.
7. DIRECTOR — apply fixes, change one axis at a time, final render, deliver.

## Anti-collapse tricks for small models
- **Write before you think far.** Persist the plan to disk after each persona; do not rely on memory.
- **One page of context per persona.** Paste into your own scratch the 15 DNA lines and the one storyboard row; ignore the rest.
- **Force divergence.** At DIRECTOR, write 3 concepts with different palette family, type pair, texture, and motion personality; pick the one least like the last video in `.motion/style-history.json`.
- **Stills are mandatory.** If you can't render, say so and ask the user for a screenshot instead of declaring success.
- **Checklist, not vibes.** Exit checklists are literal: tick each line only after running its command.
- **Do not stack all scenes in one file.** One scene = one file; that is your anti-drift boundary.

## Delegating inside a harness that has SOME subagent support (hybrid)
Use subagents only for the self-contained heavy jobs (sound, QA, a procedural 3D prop). Do the Director, Art Director and stitching yourself. This is the most reliable hybrid.
