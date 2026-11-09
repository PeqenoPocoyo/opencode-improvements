---
name: video-orchestration
description: Edit grammar and professional pacing for short-form and explainer videos built from code - how to plan cuts, holds, scene order, hierarchy, 9:16 safe areas, captions, B-roll and cutaways, loops, chapter changes, callbacks and endings so the whole video is orchestrated rather than a pile of scenes. Use when planning or critiquing the structure and rhythm of a video, when a video feels flat, rushed, cluttered or random, when adding captions or cutaways to voice-over, or when asked to make it "more professional".
---

# video-orchestration — the grammar of a well-edited video

Orchestration = what happens when, how much, and why. Motion libraries give you tools; this gives you the score.

## 1. Hierarchy: one hero per beat
Each beat has ONE hero (largest, brightest, moving), 1-2 supporters (smaller, calmer), and a background (slowest). Rules:
- Hero is 2-4x the size of supporters; contrast in luminance or saturation >= 0.25.
- Supporters arrive after the hero (+0.15-0.3 s) and settle sooner.
- Background moves at 10-20 % of hero speed (slow drift, parallax).
- If two things want to be hero, split them into two beats.

## 2. The cut grammar
| Cut type | When | Numbers |
|---|---|---|
| Hard cut on action | energetic, rhythmic beats | cut on the frame an object hits/starts moving |
| Match cut | carry an element across | same position/scale/colour in both frames; 0 overlap |
| Whip | fast pan between ideas | 8-14 frames, motion blur on both sides |
| Zoom-through | going deeper into a subject | last 0.4 s of A scales 1 -> 3, first 0.4 s of B starts 0.33 -> 1 |
| Flash | energy spike, section change | 2-4 frames white, max 3 per second |
| Dip to colour | chapter change | 6-10 frames to accent or bg tone |
| J/L cut | voice-led | sound leads/follows picture by 4-8 frames |
| Jump cut (talking head) | tighten speech | remove > 0.25 s silences; punch-in 6-10 % on every second cut |
Do not use the same cut type twice in a row. Crossfade is the weakest; use for dreamy only.

## 3. Pacing
- Beat length by style: calm 3-4.5 s, normal 2-3 s, energetic 1-1.8 s, frantic 0.5-1 s.
- Within a beat: arrival (0.3-0.5 s) -> hold (>= 0.7 s) -> exit (0.2-0.3 s, often overlapping the next arrival).
- Accelerate into the last third (shorter holds), then settle the final frame for 0.8-1.5 s.
- A breather (1.5-2 s of slow motion) at ~60 % of the length prevents fatigue.
- Reading time: hold >= max(0.8 s, chars/15).

## 4. Chapter changes (videos over 20 s)
Every 10-15 s change at least two of: background tone, accent colour (within DNA), camera move, object family. Mark with a different transition and a `riser -> reveal` or `scene-cut` sound.

## 5. 9:16 safe areas and layout
- Canvas 1080x1920. Text inside x 64-1016, y 220-1560 (platform UI covers top 220 and bottom 360).
- Hero text block centre at y 760-1000; captions at y 1250-1400 (above the bottom UI).
- Keep faces/objects away from the right-hand button column (x > 900, y 900-1500) when possible.
- 16:9: margins 96 px; lower-third zone y 800-980.

## 6. Captions (voice-led videos)
- Source: word timestamps `[{w,t0,t1}]` (faster-whisper `word_timestamps=True`) or a script + manual timings.
- Styles: clean-lowercase one word at a time centre (v04); bold-pop 2-4 words; boxed highlight; karaoke fill.
- Show each word from t0-0.05 to t1+0.1; chunk by punctuation or 3-4 words; reading speed <= 17 chars/s.
- Emphasis word: scale 1.15 + accent colour for its duration.
- PT-BR: keep accents; use the font's verified glyphs (fonts.json `ptBR`).
- Captions never overlap the hero object's eyes/face; move up/down by 120 px if needed.

## 7. Cutaways / B-roll for voice-over
- A cutaway every 4-8 s on nouns or claims; 1.2-3 s long; one idea each; shared palette across cutaways but a different "world" per cutaway (v04).
- Never cut away on emotional lines or direct address.
- Voice continues across the cut; music ducks under the voice.
- Plan: `skills/live-action-compositing/scripts/plan_cutaways.py words.json`.

## 8. Callbacks, motifs and endings
- A motif (shape, colour, motion) introduced in beat 1 returns in the last beat transformed.
- Ending = payoff line (3-6 words) + hold + (loop to frame 0 | end card | hard cut on the last beat).
- No fade to black as the default ending.

## 9. Loops
Loop if the video is <= 15 s and platform autoplays. Build: end frame = start frame; transitions out of the last beat equal transitions into the first; music loop-safe; `loop-point` event.

## 10. Density budget
Per 10 s: <= 3 hero hits, <= 8 meso events, <= 12 words on screen in total for 9:16 short-form (excluding captions), <= 2 transitions that cost > 0.3 s.

## Orchestration checklist (use on the storyboard and on the draft)
1. Hook in the first second? 2. One hero per beat? 3. Holds present? 4. Variation between consecutive beats (>= 2 dims)? 5. Transitions varied and carried by an object? 6. Chapter changes? 7. Text readable and in safe areas? 8. Breather and final settle? 9. Motif callback? 10. Every hit registered as an event?

## Weak-model protocol
1. Put the checklist answers in storyboard.md under each beat.
2. When a beat is boring: increase size contrast, add a camera move, or cut its length by 30 %; do not add more objects.
3. When a video feels rushed: lengthen holds, not the arrivals.
4. When it feels flat: add one hero hit and one breather; vary texture between chapters.

## Failure modes
| Symptom | Cause | Fix |
|---|---|---|
| "Pile of scenes" | no motif, no chapters | callbacks; chapter change rules |
| Exhausting | no holds | hold >= 0.7 s after hero |
| Boring | same size everywhere | hero 2-4x, background slow |
| Captions fight picture | overlap | move captions or object |
| Weak ending | fade to black | payoff + loop or hard cut |
