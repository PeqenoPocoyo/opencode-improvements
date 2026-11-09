# Wave plans (ready-made)

Notation: `[A | B | C]` = parallel in one message. `→` = verify on disk, then next wave. "You" = Director.

## 1. 15 s social short, 5 scenes
0. You: brief, 3 concepts, dna, storyboard (5 rows, 3 s each, seam table), ownership table. Snapshot manifest.
1. `[Scene 1-2 | Scene 3-4 | Scene 5 + asset builder]` (3 workers). → verify, render stills, stitch draft.
2. You: stitch, `render.mjs --events`. `[Sound designer]` (1 worker) or you.
3. `[QA critic]` (fresh context). → fix list.
4. You (or one engineer for one scene): apply ≤ 5 fixes; re-render only affected beats. Final.
Total workers: 5. Peak width 3.

## 2. 45 s product film, UI-in-video + 3D projection
0. You: spine; storyboard with 9 rows; seam table.
1. `[Look-dev | Asset builder (icons, 3D props, textures)]` → you review look sheet, update DNA.
2. `[UI scenes 1-3 | UI scenes 4-6]` → verify.
3. `[3D/projection scenes 7-8 | Typography+captions scene 9]` → verify.
4. You stitch. `[Sound designer]` → mux.
5. `[QA critic]` → fixes → final.
Peak width 2. Longer wall-clock, but safe against limits.

## 3. Looping generative art piece (12 s)
0. You: brief, dna (loop true), one concept.
1. `[Scene engineer (canvas art) | Sound designer (beat bed, loop-safe)]` — sound needs only the loop length and BPM, not final visuals; events come from the engineer later, so the sound designer builds the bed now and the cue layer after events.json exists.
2. You: dump events, `[Sound designer: cue layer]`. QA.

## 4. Series of 5 different videos (anti-sameness at scale)
Run each video as its own project. Before each, the Director reads `.motion/style-history.json` and states in the brief which DNA fields must differ from the previous 3 (palette family, type pair, texture, motion personality, transition set). Never run 5 videos through the same worker with the same DNA.

## 5. Building a new skill or runtime (as this pack was built)
One worker per skill folder; common brief (reference/brief-template.md); you own the spine files (CONVENTIONS, style-dna, motion-director). Waves of ≤ 3. Verify with real renders.

## Sizing guide
| Resource | Rule of thumb |
|---|---|
| Worker brief | 60–120 lines |
| Worker runtime | 5–20 min; if more, the task is too big — split |
| Wave width | 2–3 |
| Re-brief after a failure | 1 correction message; if it fails twice, do it yourself |
| Verification per worker | ≤ 3 minutes: files, lint, one still |

## When NOT to parallelize
- Anything that needs aesthetic coherence frame by frame (one hero shot): one worker.
- Tasks with a shared mutable resource (the same HTML file, the same DNA).
- When the harness is rate-limited: serialize, and prefer smaller briefs.
