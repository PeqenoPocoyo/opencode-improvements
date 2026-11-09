# Beat sheets by length

Time unit: beat = 60/bpm. Choose bpm from the DNA. Hits on beat/4 (16ths) or beat/2. `cutRate` in the DNA decides the number of beats.

## 6-8 s loop (logo, sting, art piece)
| t | beat |
|---|---|
| 0.0-0.3 | hook image appears already in motion (not black) |
| 0.3-2.0 | build: elements arrive on stagger |
| 2.0-2.4 | HIT: the one big moment (impact event) |
| 2.4-5.5 | hold with ambient motion, one secondary reveal |
| 5.5-7.5 | return: the end state equals frame 0 (loop) |

## 15 s short (one idea)
| t | beat | purpose |
|---|---|---|
| 0-1.0 | HOOK | strongest image/number/question, movement at frame 0-10 |
| 1-4 | SETUP | name the problem/claim, one object + one line |
| 4-8 | TURN | the surprise, the metaphor lands, camera changes |
| 8-12 | PROOF | number/chart/demo/second example, rhythm accelerates |
| 12-15 | PAYOFF | the claim in 3-6 words + end frame (loop or card) |
5 scenes x 3 s. Transition per seam from the DNA.

## 30 s explainer
Hook 0-2 | Context 2-8 | Problem 8-14 | Idea 14-20 | Proof 20-26 | CTA/payoff 26-30. 8-10 scenes, each 2.5-4 s; one "breather" beat of 1.5-2 s hold at ~60 %.

## 60 s film (product/story)
Hook 0-4 | Problem 4-14 | Insight 14-22 | Demo A 22-34 | Demo B 34-46 | Result 46-54 | CTA 54-60. A "chapter" every 12-15 s: change palette accent, background tone and camera move at each chapter.

## Talking-head with cutaways
Plan from word timestamps (live-action-compositing/scripts/plan_cutaways.py): cutaway every 4-8 s on nouns/claims, 1.2-3 s long, never on emotional lines; voice continues across cuts.

## Loop piece
Choose cycle = 2-4 bars. All periodic values complete an integer number of cycles in `duration`. See motion-canvas-artwork/reference/loops.md.

## Rhythm architecture (three levels)
| level | period | what |
|---|---|---|
| macro | 2-4 s | scene/beat change (camera, background, object) |
| meso | 0.3-0.6 s | a word/object/number arrives |
| micro | 0.1-0.25 s | glow/shake/scale pulse after each hit |
Every second of the film should have at least one meso event; every 2-4 s a macro event; no more than 3 simultaneous micro pulses.

## Dynamics
- One hero hit per 6-8 s. Everything else is smaller.
- Holds of 0.7-1.6 s after every hero hit so the viewer reads.
- Acceleration into the final third (shorter holds, faster stagger), then a deliberate settle on the last frame.

## Text timing
Reading speed 12-17 characters per second; hold time = max(0.8 s, chars/15). Never swap text faster than that. Big words (<= 3) can be 0.4-0.6 s.

## Captions
One word at a time (centered, lowercase) for voice-led; 2-4 word chunks for dense; karaoke highlight for music videos. Safe area y 220-1560 (9:16).
