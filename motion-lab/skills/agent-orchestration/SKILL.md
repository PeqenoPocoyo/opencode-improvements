---
name: agent-orchestration
description: How to split a video (or any multi-part build) across sub-agents or across sequential "roles" so each worker does ONE well-briefed task and nothing collides. Covers partitioning by file ownership, brief templates, handoff contracts, parallel vs sequential waves, verification of each handoff, rate-limit and context-limit recovery, and a no-subagent fallback for harnesses or models that cannot spawn agents. Use when a request is big (several scenes, many assets, sound + visuals + QA), when the harness offers Agent/Task/subagent tools, when the user says "orchestrate", "use agents", "split the work", "parallel", or when a single context is getting too long to hold the whole video.
---

# agent-orchestration — one worker, one job, one folder

A video is several jobs that look like one: concept, look, scenes, sound, QA. One model doing all of it in one context drifts toward its defaults (the "same soul" problem) and runs out of room. Splitting the work fixes both, **if** the split is clean. A bad split is worse than none: two agents editing the same file, or an agent guessing what another one meant.

This skill teaches the split. It works in three modes. Pick by what the harness gives you:

| Harness offers | Mode | Read |
|---|---|---|
| An Agent / Task / subagent tool that runs several workers | **A. Parallel waves** | this file + `reference/wave-plans.md` |
| A subagent tool, but limits are tight (usage caps, 429, slow) | **B. Small waves, you write the spine** | this file + `reference/rate-limits-and-recovery.md` |
| No subagent tool, or the model is weak at delegating | **C. Sequential personas in ONE context** | `reference/sequential-persona-fallback.md` |

If unsure, start in mode B. It degrades gracefully into C.

## The six rules (memorize these)

1. **Partition by ownership, not by topic.** Every file in the project has exactly ONE owner for the whole job. Write the ownership table first (`templates/ownership-table.md`). An agent may read anything, write only what it owns.
2. **The brief is the whole world.** A worker knows only what is in its brief plus the files you point to. Say the goal, the inputs (paths), the outputs (paths), the contract it must obey (`CONVENTIONS.md`), the test it must run, and the report format. A one-line "make the intro scene" brief produces default-looking output.
3. **Contracts before code.** Before any worker starts, the spine exists: `brief.md`, `dna.json`, `storyboard.md` with a time grid, the scene-file API (`window.VIDEO`, `seek`, `EVENTS`) and the shared event vocabulary. Workers build to the contract, so their parts snap together.
4. **Waves, with a gate between them.** Work that depends on earlier output runs later. Within a wave, workers are independent. After each wave YOU verify on disk (files exist, render a still, run the linter) before launching the next. Never trust a report you did not check.
5. **Small fan-out.** 2–3 workers per wave is the sweet spot. More workers cost tokens in a burst and can hit usage limits, leaving half-written files. Checkpoint to disk after every wave.
6. **The director integrates; workers never decide the look.** Look = `dna.json`. If a worker wants to change the look, it writes a note in its report; the director decides.

## Roles for a video

| Role | Owns (writes) | Reads | Output contract |
|---|---|---|---|
| **Director** (you) | `brief.md`, `dna.json`, `storyboard.md`, `stitch.html`, final delivery | everything | Beat sheet with times; picks style via style-dna; integrates |
| **Art director / look dev** | `lookdev/` (palette tests, type specimen, texture stills), proposed DNA edits | brief, DNA | A still sheet proving the look; DNA tweaks as a diff in its report |
| **Scene engineer** (one per scene) | `scenes/NN-name.html` ONLY | DNA, storyboard row(s), runtimes | A page honoring seek(t), registering EVENTS, duration = its storyboard slot |
| **Asset builder** | `assets/` (svg, generated textures, procedural 3D props, fonts subset) | DNA, storyboard | Files + a manifest listing each asset, size, intended scene |
| **Sound designer** | `audio/` | `out/events.json`, DNA.sound | `cues.json`, `mix.wav`, `sound-report.md` with 5 human-check timestamps |
| **QA critic** | `out/qa/` (reports only; never edits scenes) | final/draft video, rubric | Rubric scores + max 5 ordered fixes naming file and parameter |
| **Researcher** | `research/` | web | Notes with sources; never invented facts |

A short video (≤ 15 s, one idea) usually needs only: director + 1–2 scene engineers + sound designer + QA. Do not spawn a role just because it exists.

## The protocol

### Step 0 — decide whether to split at all
Split when ANY is true: more than 3 scenes; sound design plus heavy visuals; the work will not fit in one context; user asked for it. Do NOT split a single 6-second logo sting. Overhead beats benefit.

### Step 1 — build the spine yourself (never delegate this)
1. `brief.md` (idea, audience, platform, length, tone). Use motion-director.
2. Three divergent concepts, choose one. Use motion-director.
3. `dna.json` via style-dna (`dna_generate.py --check`).
4. `storyboard.md`: a table `# | start | end | what happens | camera | transition in | events | owner`. Times on the beat grid. Every scene slot has an exact duration — workers must hit it.
5. Ownership table (`templates/ownership-table.md`). Write it into `storyboard.md` or `ORCHESTRATION.md`.
6. Shared stitching contract: scene files are standalone pages (each `seek(t)` local time from 0 to its duration) and `stitch.html` plays them with `Lab.chain` / `Trans`. See `reference/handoff-contracts.md`.

### Step 2 — write briefs from the templates
Use `templates/briefs/*.md`. Fill every blank. Paste the DNA JSON into the brief (do not say "see dna.json" — say it AND paste the 15 lines that matter). Give the exact test command. Give the report format. Keep the brief under ~120 lines; link to files for the rest.

### Step 3 — launch a wave
Send all independent workers of the wave in ONE message (parallel tool calls). Tell each worker its folder boundary in the first line of the brief: "You may write only under `scenes/02-*.html`."

### Step 4 — verify the handoff (you, every time)
Run `python3 skills/agent-orchestration/scripts/manifest.py diff <project>` (shows what changed since the snapshot taken before the wave, and flags writes outside the owner's area), then:
- the files named in the report exist and are non-empty;
- `python3 skills/qa-critique/scripts/lint_scene.py scenes/NN.html` passes;
- render a contact sheet of the scene; LOOK at it;
- the scene's duration equals its slot; EVENTS present (`render.mjs scene.html - --events -`).
A worker that fails verification gets ONE correction message with the exact defect, not a rewrite of the brief.

### Step 5 — integrate
Stitch (`stitch.html`), render a draft, dump events for the whole video, hand to the sound designer (sequential — it needs final timing), then QA critic, then fix list, then final. Run the quality gates in `CONVENTIONS.md §6`.

### Step 6 — deliver with honesty
Report what was built, the 5 timestamps for the human sound check, and known issues. Never claim it sounds good.

## Parallel or sequential? Decision table

| Question | Yes → | No → |
|---|---|---|
| Does B need A's output file to start? | sequential (A then B) | parallel |
| Do A and B write the same file? | merge them into one worker, or split the file | parallel |
| Does it need the final timing (sound, captions)? | after the stitched draft | can start from storyboard |
| Is it a check (QA, lint)? | after the thing it checks | — |
| Is it cheap (< 5 min for you)? | do it yourself | consider delegating |

Typical dependency graph:

```
spine (you) ──► [scene A] [scene B] [scene C] [assets]   ← wave 1, parallel
                     └────────┬────────┘
                       stitch + draft (you)
                              │
                       events.json
                              │
                       [sound designer]  ← wave 2
                              │
                       mux + [QA critic] ← wave 3
                              │
                         fix list → you or one engineer → final
```

## What to put in a worker brief (checklist)
1. First line: role + the ONE task + the write boundary.
2. Why (one sentence of the video's concept) so it can make judgment calls.
3. Inputs: exact paths, and the 15 DNA lines inline.
4. Output: exact paths, duration, resolution, fps.
5. Contract: "obey /…/CONVENTIONS.md; seek(t) pure; register Lab.ev for every hit".
6. Creative latitude: what it MAY choose (within DNA) and what it MUST NOT (palette, fonts, tempo).
7. Test command and what "done" looks like (still sheet looked at, linter clean).
8. Report format (≤ 20 lines: files, public hooks, what was verified, caveats, anything for the director).
9. Anti-sameness line: "Do not use any easing/transition/motion not listed in the DNA's `motion` / `transitions`."

## Failure modes
| Symptom | Cause | Fix |
|---|---|---|
| Scenes look like different videos | Workers chose their own palette/type | Paste DNA in every brief; lint for hard-coded hex not in DNA |
| Seams: pop at scene boundaries | No handoff contract for first/last frame | Specify entry/exit states in storyboard (`reference/handoff-contracts.md`) |
| Two workers overwrote one file | Shared file | Ownership table; one file, one owner |
| Worker returned prose, no files | Brief had no output path | Always give paths; verify on disk |
| 429 / usage limit, half-written files | Fan-out too wide | `reference/rate-limits-and-recovery.md`: shrink waves, checkpoint, resume from disk |
| Reports claim success, render is blank | You trusted the report | Step 4 verification, always |
| Sound out of sync | Sound written from storyboard, not final timing | Sound designer runs on the stitched draft's `events.json` |
| All scenes have the same transition | Workers each picked the "safe" one | Director assigns the transition per seam in the storyboard |

## Variation knobs (so orchestration itself does not make videos alike)
| Knob | Range |
|---|---|
| Scene count | 3–12 by length and cut rate in DNA |
| Who owns the transition seams | the engineer of the incoming scene (carry elements) or the director (stitch-level transitions) |
| Look-dev first | skip for tiny jobs; do a still sheet for new styles |
| Parallel width | 1–3 workers per wave |
| Critic strictness | rubric pass threshold 20/30 (draft) or 24/30 (final) |

## Weak-model protocol (if YOU are the weak model)
1. Read `reference/sequential-persona-fallback.md` first. Default to mode C unless the harness clearly has subagents.
2. Write the spine files before anything else. Do not start scene code before `storyboard.md` has times.
3. One scene per turn. After each scene: render a still, look, fix, then the next.
4. Keep a running `ORCHESTRATION.md` (done / next / blocked). If your context resets, you resume from it.
5. When delegating, copy the brief template verbatim and fill blanks; do not improvise a shorter one.
6. After every worker, verify on disk. If you cannot render, say so and ask the user for a still.

Files: `reference/roles.md` (deep role cards) · `reference/brief-template.md` (the real worked example) · `reference/handoff-contracts.md` · `reference/wave-plans.md` · `reference/rate-limits-and-recovery.md` · `reference/sequential-persona-fallback.md` · `templates/` · `scripts/manifest.py`.
