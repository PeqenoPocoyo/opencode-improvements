# Anti-sameness: the diagnosis and the cure

## Why AI videos share a soul (observed in the toolkit output)
| Cause | Symptom | Cure here |
|---|---|---|
| Fixed palette baked in the skill | every video orange-on-black | palette is generated per video (style-dna) |
| Fixed fonts | Inter/Geist everywhere | type character chosen from 20+ families |
| One easing (spring) for everything | all motion feels the same | motion personalities (7) with different ease sets |
| Fixed scene list (title, 3 cards, CTA) | same story shape | concept methods + beat sheets |
| No texture | "template" look | texture block required; FX/paper/halftone/grain |
| Ban lists instead of options | models avoid, but do not invent | variation knobs and generators |
| Same six sound samples; sound starts at the cue | all videos sound alike and late | procedural layered sound, anchor-aligned |
| No memory between videos | drift back to the mean | ledger + fingerprint + distance check |

## The ledger
`.motion/style-history.json` {entries:[{name,date,dna,fingerprint}]}. Consulted at gate 3 (DNA distance) and gate 9 (visual/audio fingerprint). Never delete. Pass it between sessions (it lives in the project folder).

## How to tell "same soul" (checklist for the QA critic)
1. Squint at the contact sheets of two videos: same dominant colours and layout? -> same.
2. Same display font + same case? -> same.
3. Same easing feel (everything overshoots / everything glides)? -> same.
4. Same transitions in same order? -> same.
5. Same texture (or none)? -> same.
6. Same sound palette and key? -> same.
Two or more yes = SAME_SOUL. Rewrite the DNA, not just the colours.

## Forcing divergence on weak models
- Give them the generator output, not a blank page.
- Give a menu with numbers (families, dials), not "be creative".
- Make them write 3 concepts and the divergence table.
- Make them list `forbidden` for the current video.
- Run `--check`; show them the failing fields.

## Creative range exercises (use in generative-play)
1. Re-skin: same storyboard, three DNAs; compare stills.
2. Constraint swap: remove colour, then remove type, then remove camera moves.
3. Material swap: re-render the same scene as paper, glass, clay.
4. Tempo swap: 70 bpm vs 130 bpm.
5. Crossbreed: take palette of A, motion of B, texture of C (dna_generate `--preset A --mutate`, then hand-edit).
