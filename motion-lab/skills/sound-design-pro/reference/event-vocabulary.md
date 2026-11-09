# Event vocabulary -> recipes -> layer stacks

`Lab.ev(t, type, {intensity 0-1, dur s, pitch st, pan -1..1, label})`. Every type below is understood by `sync_cues.py`. Unknown types that match a recipe name (e.g. `stamp`, `paper-rip`, `glass-ding`, `heartbeat`, `camera-shutter`, `dial-tick`, `blip`) play as a single layer. Aliases: hit→impact, thud→hit-soft, cut/transition→scene-cut, typing/keystroke→type, build/build-up→riser, sparkle→shimmer, ding→glass-ding, notification→chime, complete→success, fail/warning→error, word/text-in→pop, count→tick, dial→dial-tick, shutter→camera-shutter, loop→loop-point, sweep/swoosh→whoosh, bass→bass-drop, logo→stinger, end→boom.

Default stacks (palettes swap, drop and add on top). dB are relative to the event's level. `lead` = anchor before the event anchor by N frames.

| Event | Layers (default palette) | Duration | Anchor rule | Use / numbers |
|---|---|---|---|---|
| impact | impact (sub drop + thud + noise body + crack + tail) ; boom -9 dB if intensity >= .75 | 0.5-1.4 s | transient = event frame + 6 ms | title hits, product lands. Intensity .6-1 |
| hit-soft | hit-soft (sub thud + soft body + felt tick) ; tick -13 | 0.3 s | transient | object lands softly, card settles |
| slam | slam (long sub, crash, flam, debris, big room) ; whip -9 lead 3 frames | 1.5 s | transient | ONCE per video |
| whoosh | whoosh (band noise sweep + rumble + air) ; swipe -9 | `dur` (0.3-0.9) | peak at 35-60 % of dur (in: 60 %, out: 35 %) | pass dur; 0.35-0.5 s for UI, 0.6-0.9 for big camera moves |
| whip | whip (0.2 s rising burst that stops with a crack) | 0.2 s | the crack at the end | fast pans; pre-cut sound |
| swipe | swipe (soft band noise) | 0.18-0.3 s | middle | cards sliding |
| pop | pop ; tick -13 | 0.12 s | transient | element appears with overshoot |
| appear / disappear | appear / disappear | 0.15-0.3 s | transient | opacity/scale reveals |
| click / tick | click / tick | 0.05 s | transient | UI press (click at the pressed frame), counters |
| type | key per step (`dur`/steps) | run | each key on its frame | 14-22 cps; seeded irregular rhythm |
| riser | riser (noise band + saw glide + pulse) ; reverse -10 | `dur` | END = event t + dur | build into a reveal; give `dur`; event t is the START, hit goes at t+dur |
| reverse | reverse swell | `dur` | ENDS at t+dur | pre-hit anticipation; loop seam |
| glitch / zap | glitch / zap | 0.25-0.5 s | start | RGB split, data errors |
| shimmer / chime / success | shimmer, chime, success (+ shimmer after +3 frames) | 0.6-1.5 s | transient | sparkle stars, completion; key-tuned |
| error | error | 0.4 s | transient | |
| reveal | reveal (whoomph + sub thud + sparkle) ; shimmer after | 0.8 s | transient | ta-da moments |
| drop / bass-drop / boom | bass-drop + impact -3 ; boom | 0.7-2.6 s | start of the drop | beat drop, end card |
| stinger | stinger | 1.2 s | transient | logo/endcard |
| scene-cut | whip -5 lead 3f ; hit-soft -2 ; tick -14 | 0.3 s | the cut frame | auto: use for every hard cut |
| loop-point | reverse -14 (0.6 s) | | ends on frame 0 | seamless loops |

## Intensity guide
| value | meaning | typical |
|---|---|---|
| 0.2-0.4 | background detail | tick, small pop |
| 0.5-0.7 | normal action | pop, whoosh, hit-soft |
| 0.8-1.0 | hero moment | slam, impact, reveal |
Dynamic contrast makes it feel designed: at most 3-5 events per 10 s at >= 0.8.

## Registering events in a scene (copy)
```js
Lab.ev(T.title - 0.06, 'whoosh', { dur: 0.35, intensity: .6, label: 'title in' }); // motion START = T.title-0.06, length .35
Lab.ev(T.slam, 'impact', { intensity: 1, label: 'slam' });                          // the frame the picture HITS
Lab.ev(T.reveal - 1.2, 'riser', { dur: 1.2 });                                      // riser ends at T.reveal
Lab.ev(T.reveal, 'reveal', { intensity: .85 });
words.forEach((w, i) => Lab.ev(T.words + i * 0.12, 'pop', { intensity: .55, pitch: i }));
```
Time of an event = the instant the picture changes (the first frame that shows it), not the start of an ease.
