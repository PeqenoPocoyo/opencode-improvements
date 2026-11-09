# Timing rules (frame math, anchors, lead and lag)

## 1. Measured facts from the reference videos
- Audio onset nearest a visual change: median +7 to +19 ms in the polished videos (v03, v09, v10, v11) = within ONE frame at 30 fps (33.3 ms). In the loose-feeling ones (v01, v04) +46 to +92 ms. v09 measured -22 ms.
- Rule: the transient lands on the frame the picture changes, +0...+10 ms; never later than +45 ms; never early by more than a frame (early reads as "anticipation", only allowed on purpose).
- Onset density: 3-10 per second. Busy videos 7-10/s. Sparse videos have 10-20 % silence.

## 2. Frame math
```
frame      = round(t * fps)
boundary   = frame / fps                       (seconds)
anchor_t   = boundary + lag                    lag = 0.006 s  (--lag-ms 6)
file_start = anchor_t - anchor_offset(sound)   anchor_offset is measured per sound (analyze_sfx.py "anchor")
```
Sync = put the ANCHOR on the boundary, not the file start. Examples of anchor offsets: impact 0.1 ms (transient is the start); whoosh 65 ms (peak at 35-60 % of dur); riser = its full length (it ENDS on the anchor); reverse = its length; chime 2 ms.

## 3. Which moment of the picture is the event time?
| Picture | Event time |
|---|---|
| Object lands / stops | first frame it touches/stops |
| Text slams in | the frame it reaches full scale (end of the fast part), not the start of the ease |
| Pop with overshoot | the frame of first appearance |
| Whip pan | start of the move; pass `dur`; the sound peaks at the middle |
| Cut | the first frame of the new shot |
| Reveal after build-up | the reveal frame; the riser event starts `dur` earlier |
| Cursor click | the frame the button shows pressed |
| Count-up ticks | each integer change (or every 3rd for fast counts) |
| Flash | the first white frame |

## 4. Anticipation and silence
- 3 frames (100 ms) before a hero hit: a `whip` or `reverse` (sync_cues adds it for slam/scene-cut/riser).
- 120 ms dip: music and sustained layers drop 6 dB right before a hero hit, then the hit is heard clean.
- After a hero hit, leave 150-250 ms before the next event > 0.7 intensity.
- Do not stack more than 3 simultaneous layers above 2 kHz; they smear.

## 5. Voice, L and J cuts
- Voice-over leads: sync to words, not beats (v04). Cutaway sounds sit under the voice at -12 dB, ducked 8 dB while speaking.
- J-cut: sound of the next shot starts 4-8 frames before the picture; L-cut: sound of the old shot continues 4-8 frames after. Register the whoosh/ambience event at `t - 0.15` (J) or `t + 0.15` (L) and say so in the label.

## 6. Loops
For a looping video, the last 0.5 s ends with a `loop-point` (reverse swell) and the music bed is loop-safe (`musicgen.py --loop` / `sync_cues.py --loop`). Frame N = frame 0 sonically: no tail ringing across the seam.

## 7. Dense passages
- Events < 60 ms apart merge in the ear: thin them (keep the strongest).
- Rhythmic runs (ticks, pops): tonal walk through the scale makes them musical; pitch rises with value for counters.
- Cap total onset density at ~10/s.

## 8. What can go wrong with the mux
Check `audio start vs video start` in qa_audio. AAC adds ~21 ms priming; render.mjs/ffmpeg normally compensates. If the report shows a constant offset, apply `--music-offset`/`-itsoffset` once, not per cue.
