# Anatomy of designed sounds (why they do not sound cheap)

A real sound effect is several sounds stacked, each doing one job. Layers by job:

| Job | Typical content | Time | Band |
|---|---|---|---|
| SUB | sine falling 90-130 Hz -> 40 Hz, saturated | 0-0.5 s | 30-120 |
| TRANSIENT / CRACK | 3-8 ms noise burst, high-passed | 0 ms | 1.8-8 k |
| BODY | low sine/triangle 150-250 Hz thud or filtered pink noise | 0-0.3 s | 120-600 |
| MID SNAP | 20-30 ms band noise | +0.4 ms | 700-5 k |
| TEXTURE / AIR | hp noise with envelope | motion length | 4 k+ |
| TAIL | generated-IR reverb of the body | 0.4-1.5 s | 120-2 k |
| LEAD / ANTICIPATION | whip/reverse 3 frames early | -100 ms | broad |

## 25 designed sounds (recipe: layers, numbers)
| Sound | Layers and numbers |
|---|---|
| impact | sub drop 92+40i -> 43 Hz (45 ms, decay .12+.24i s) ; thud-body 220 -> 84 Hz -4.5 dB ; noise-body lp sweep 260-3.4k exp(-t/50ms) -9 dB ; crack 6-7 ms hp 1.8 k -3 dB ; mid-snap 700-5.2 k 30 ms -6 dB ; tail reverb 0.45+i s -11 dB ; master saturation 1.3 |
| hit-soft | sub 105+25i -> 52 Hz ; soft body lp 520 Hz 90 ms -6 dB ; felt tick 3 ms -12 dB ; room 0.15 s -13 dB |
| slam | sub long 120 -> 38 Hz 1.5 s ; thud 250 -> 80 Hz ; crash noise hp 450 sweeping lp 9 k -> 1.5 k -2.5 dB ; crack 8 ms -1 dB ; flam second hit +24 ms -9 dB ; 5 debris ticks over 0.3 s ; big room 1.5 s |
| boom | sub 70 -> 36 Hz 2.6 s ; brown-noise rumble lp falling from 700 Hz -4 dB ; soft click -9 dB ; huge dark reverb |
| bass-drop | sine falling 120 -> 34 Hz over 0.7 s, saturated harmonics, sustained sub, pre-click |
| whoosh | band-passed pink noise sweeping 170 -> 2.3 kHz with the peak at 35-60 % ; low rumble -3 dB ; air hp 4.2 k -18 dB ; stereo sweep for lr/rl ; tail |
| whip | 0.2 s rising noise, stops with a crack at 82 % (anchor) |
| riser | rising band noise + detuned saw glide + accelerating pulse; ENDS on the anchor; variants: mix, pulse, siren, snare-roll |
| reverse | reversed bright crash / reversed sub hit / reversed bell; ENDS on the anchor |
| pop | short pitched sine pluck with pitch dip + tiny noise tick |
| click | 2-5 ms transient + 1.2-3 k resonance; variants soft/hard/mechanical |
| key (typing) | click + low thock; seeded per-key velocity/pitch; spacebar deeper |
| glitch | 5-9 stuttered slices of bit-crushed noise, square blips, ring-mod, hard gated |
| zap | FM sweep 3.5 k -> 180 Hz in 0.16 s + crackle band + small sub |
| shimmer | high inharmonic partials with slow swell, 6-11 kHz air |
| glass-ding | inharmonic partials (1x, 2.4x, 4.5x, 7x, 9.8x) with exponential decays |
| chime/success | key-tuned bell triad rising; success adds shimmer +3 frames |
| reveal | upward whoomph landing on anchor + sub thud + sparkle after |
| stamp | dull wooden knock + short noise "ka" + low thud |
| paper-slap | broadband crack + low thump + short flutter |
| paper-rip | irregular grain crackle with rising density + band-passed fibre noise + low tear |
| tape | 0.18 s dense grains ripping, ending in a soft stick |
| camera-shutter | two clacks (open strong, close softer 38 ms later) + body resonance |
| heartbeat | lub-dub at bpm, sub-heavy |

## Rules of thumb
1. Hit = SUB + CRACK + BODY. If one is missing it sounds fake: no sub = thin, no crack = muffled, no body = "two separate sounds".
2. Pitch of the sub follows the picture mass: big object 38-45 Hz, small 52-70 Hz.
3. Tail length follows the room of the look: dry paper style 0.2 s, hall glass 1.5 s.
4. Every layer gets its own envelope with exponential decay; linear fades sound like fades.
5. Add 1-2 dB gain and +-1 semitone jitter between repeats so repeated sounds do not machine-gun.
6. Tonal sounds sit in the video's key; random pitches sound like errors.
7. Saturation on the sum (1.3-2.2) glues layers.
8. Stereo: low end mono, highs wider; whoosh sweeps pan with the motion.
