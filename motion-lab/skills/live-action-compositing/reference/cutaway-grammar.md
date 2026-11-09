# Cutaway grammar for talking-head / tutorial footage

| Speech cue | Overlay | Duration | Sound |
|---|---|---|---|
| Number / % / money | stat card with count-up (`Lab.countUp`) | 1.8–2.5 s | `pop` at arrival, `tick` on count, `success` if growth |
| "first / step / click / open" | UI cutaway (`ui-in-video`) or screen-capture crop with cursor | 2–3 s | `click` on each cursor click |
| Question | kinetic type (`kinetic-typography`) over the face's lower third | 1.5 s | `appear` |
| List of 3+ | bullet build | stagger 0.35 s | `tick` each |
| Proper noun | lower-third (name + 1 line) | 2.5 s | `swipe` |
| Emphasis word | punch-in zoom 1.00→1.08 in 0.25 s, hold, ease back | 0.8 s | `hit-soft` |
| Topic change | wipe/transition (`transitions-projections`) | 0.4–0.6 s | `whoosh` peaking at the cut |

## Cut timing (J/L)
- J-cut: next visual begins 0.2–0.3 s BEFORE its line starts. L-cut: visual lingers 0.25 s after the line ends.
- Do not cut on a word's first syllable: cut 2–4 frames before the stressed vowel.
- Hold shots ≥ 1.2 s unless it is a montage; max hold 2.8 s for cutaways, 4 s for graphics with reading.
- Alternate scale: wide → punch-in → cutaway → wide. Never the same framing twice in a row.
- Keep the speaker's face visible ≥ 55 % of runtime.

## Reading time (graphics)
Words × 0.28 s + 0.6 s (e.g. 6-word label = 2.3 s). Numbers: 1.2 s minimum after the count-up completes.

## Captions
If burning captions: max 2 lines, 32 chars/line, safe area y 1350–1560 (above platform UI), highlight the spoken word with the DNA accent, never cover lower thirds (move captions up 140 px when a lower third is on).
