# Weak-model playbook — how to get strong video work from small/fast models

For GLM Flash / Step / other fast models. They are good at following checklists and writing code in small pieces; they are bad at taste, long plans and self-checking. So we **externalise** taste (DNA, tables), **chunk** the work, and **force** checking.

## The 8 operating rules
1. **One file, one job, ≤ 250 lines.** Build `scene.html` in sections (setup → layers → timeline → events). After each section run the lint.
2. **Never write from memory what a runtime provides.** Copy the example closest to the job (`examples/` in each skill) and change content + DNA values.
3. **Decide with tables, not with feelings.** Every skill has a "need → use" table. Pick the row, don't invent.
4. **Numbers over adjectives.** Durations in frames/seconds, sizes in px, eases by name. "Fast" = 8–12 frames; "calm" = 20–30 frames; "slam" = `Lab.curves.snap`.
5. **Look after every visual change.** Render one still, Read it, name 2 problems. (Models that skip this ship broken frames.)
6. **Variation by force.** Before each video, change at least 3 axes vs the previous one (palette hue family, type pairing, motion personality, texture, transition set, camera behaviour, sound palette). The ledger and `fingerprint.py` enforce it.
7. **Small, named steps in the final answer.** The user wants a file, not a story.
8. **When stuck for 2 attempts: simplify** (remove an effect), don't pile on more.

## Creativity procedures (use these instead of "be creative")
**A. Forced divergence (concepts).** Write 3 concepts that differ in: *metaphor* (what the video is "like": a machine, a garden, a newspaper, a map, a radio), *camera* (static/orbit/zoom-through/handheld), *material* (paper, glass, neon, clay, ink, screen), *tempo* (slow build / staccato / single long move). No two concepts may share a metaphor or material.
**B. Constraint cards.** Pick ONE and obey it for the whole video: "only 2 colours + black" · "no gradients" · "everything on a 12-col grid" · "all motion along diagonals" · "one continuous camera move" · "type is the only graphic" · "monochrome + one accent that appears 3 times" · "everything loops".
**C. Reference decomposition** (from a video/screenshot the user likes): write 6 lines — palette (5 hex), type character, layout grid, motion personality (ease names + speed), texture/finish, sound feel. Then **change two** of them and build. (Never copy all six.)
**D. Mutation.** Take a preset DNA (`dna_generate.py --preset X --mutate SEED`) or a generator/shader and change ONE structural thing (coordinate system, symmetry, scale, direction, material).
**E. Crossbreeding.** Take layout from preset A, palette from preset B, motion from preset C (`--cross` in generative-play).
**F. The "so what" test.** After the beat sheet: for each scene write "the viewer learns/feels ___". Delete scenes without an answer.

## Timing cheat-sheet (30 fps)
| Thing | Frames |
|---|---|
| Text pop/slam | 6–10 |
| Text slide/mask reveal | 10–16 |
| Card/UI rise | 12–18 |
| Camera punch | 20–40 |
| Transition (fast) | 8–12 |
| Transition (hero) | 18–24 |
| Hold on payoff | ≥ 30 |
| Stagger between items | 2–5 (letters 1–2) |
| Anticipation (pull back before a slam) | 3–5 |
| Sound anchor offset | event at frame boundary, +6 ms (sync_cues does it) |
Rule: **fast in, slow out** (snap/outExpo in; glide for exits). Overlap actions by 20–30%. Never start 3 things on the same frame.

## Sound cheat-sheet
Hit on every cut; whoosh peaks at the cut (not start); impact = sub + transient + body + tail (sfxgen does it); music ducks 4–6 dB under hits; one silence before the drop; loudness −14 LUFS social. Never trust you heard it: give the 5 timestamps.

## Failure → fix table
| Symptom | Fix |
|---|---|
| Video looks like the last one | `fingerprint.py` → change palette family + motion personality + texture + transitions |
| Everything enters at once | `Lab.stagger`, priority order (hero first), 2–5 frame offsets |
| Flat/boring background | `generative-3d-backgrounds` shader + grain + vignette; or `motion-canvas-artwork` field layer |
| Text feels generic | pick another `Type` style from the meaning table; vary weight/width; crop huge type |
| UI looks fake | real copy + numbers, state changes with motion, cursor with arc + click, camera punch |
| Cuts feel arbitrary | give each cut a reason (transition table); match cut / carried object; cut on beat |
| Sound is "meio pá" | use sync_cues layers, correct palette, anchor, duck music; remove stock sample at t=0 |
| Render hangs/blank | lint; check `window.__ready`; fonts local; run stills first |
| Context getting long | write a handoff note (`.motion/NOTES.md`) and continue from files, not memory |

## Voice of the director (how to talk to the user)
Short, concrete, no hype. Offer 2–3 clearly different options before building when the brief is open. After building: what it is, what to check, what to change next.

## Using sub-agents (Claude-style orchestration)
If the harness has an Agent/Task tool: read `skills/agent-orchestration/SKILL.md`. Rules: partition by **file ownership**; give each agent a brief from `templates/briefs/`; max 2–3 in parallel; verify the files on disk after each wave; if rate-limited, switch to sequential-persona mode (`reference/sequential-persona-fallback.md`).
If there is NO sub-agent tool: simulate roles sequentially — Director (concept/DNA) → Scene engineer (one scene per pass) → Sound designer → QA critic (fresh eyes: read only the sheet + rubric).
