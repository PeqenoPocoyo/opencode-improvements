# Honesty and the human check

## What the model can and cannot know
| Can | Cannot |
|---|---|
| Place every sound within a frame of its event (measured) | Hear whether it feels good |
| Measure loudness, true peak, spectral shares, silence, density | Judge timbre taste, "punch", "warmth" |
| Compare spectrograms: sweeping band, falling sub, broadband click | Know whether a transient "sounds late" to a person at 60 fps on earbuds |
| Detect masking and clipping | Replace a listening pass |

## What to say to the user (template)
"Sound is procedural: I placed every transient within +0...+10 ms of its frame (isolated-event test: +5...+7 ms) and mastered to -14 LUFS / -1 dBTP. I cannot hear it. Please listen with headphones to these 5 moments and tell me what to change: 0:01.6 title slam (transient on the hit?), 0:04.7 whip into cut (peak on the cut frame?), 0:07.2 impact (weight ok on phone speakers?), 0:09.5 reveal (sparkle too bright?), 0:11.5 boom (tail too long?). I can render alternatives with --variants 3."

## Procedure
1. Take the 5 riskiest timestamps from `sound-report.md` (hero hits, cuts, riser ends, densest passage, quietest hook).
2. Write what to listen for in one short phrase per timestamp.
3. Offer a concrete lever for each likely complaint (brighter/darker, shorter tail, less sub, other variant).
4. After the user's reply, change ONE thing per round (`--brightness`, `--seed`, palette `swap`, `--sfx-db`) and re-run `qa_audio.py`.

## Do not
- Claim "sounds great", "perfectly synced", "professional quality".
- Report only the intermediate WAV; report the final MP4.
- Hide `unmeasured` events: say they were masked.
- Use samples or music without a licence note.
