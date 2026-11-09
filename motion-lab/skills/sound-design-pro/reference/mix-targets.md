# Mix targets

| Target | Social (TikTok/Reels/Shorts) | Conservative (YouTube long / broadcast-ish) |
|---|---|---|
| Integrated loudness | -14 LUFS (+-1.5) | -16 LUFS (+-1.5) |
| True peak | <= -1.0 dBTP | <= -4.0 dBTP |
| LRA | 2-6 LU | 3-8 LU |
| Clipping | none (references clip at the platform; do not copy) | none |

## Spectral balance (shares of energy, measured on the references)
| Band | Hz | Target share of the mix |
|---|---|---|
| sub | 20-120 | 30-73 % |
| low | 120-400 | rest of the bass-heavy 65-90 % total below 400 |
| mid | 400-2000 | 8-30 % (voice lives here: voice-led videos are mid-heavy, v04 45 %) |
| high | 2-6 k | 2-7 % |
| air | 6-16 k | 0-7 % (only glass-ish styles reach 6-7 %) |
The cheap-beep spectrum is the opposite: energy at 1-6 kHz, no sub, no tail.

## Levels (before master), relative
- Voice: -6 dB (reference). Music: -18 dB under SFX, -14 dB when no SFX/voice. SFX hits: -9 dB. Sustained SFX under voice: ducked 8 dB.
- The master loop measures -> gain -> limiter -> measures again and writes the verified numbers into the report.

## Ducking
- Voice -> music + sustained SFX: -8 dB, 30 ms attack, 250 ms release.
- Big hit (>= .8) -> music: -3.5 dB for 150 ms.
- Hero hit: 120 ms dip before.

## When the report shows warnings
| Warning | Meaning | Action |
|---|---|---|
| SUB-HEAVY (> 73 % under 120 Hz) | small speakers reproduce none of it | add body 150-400 Hz: raise `--brightness`, swap boom -> impact, lower bass-drop layers |
| THIN (< 40 % under 400 Hz) | no weight | add boom/bass-drop layers to key hits, music with bass |
| HARSH (> 10 % above 2 kHz) | fatiguing | lower brightness, `swap` click -> hit-soft |
| SPARSE (> 25 % silence) | intentional? | add ticks/pops or keep if the style is sparse |
| DENSE (> 10 onsets/s) | mush | remove small events in the scene |
| first sound after 0.25 s | opening silent | add a hit at frame 0-10 |
| mono loss > 3 dB | phasey stereo | reduce width/pan sweeps |

## Reading qa_audio on dense mixes
`alignment` measures the audio onset nearest each event inside -50...+90 ms. In dense passages two events overlap, so the error looks bad although cues.json placed everything within 1 frame. The report counts `unmeasured` events: they are masking, not passes. To get a clean number, render the events isolated (one event per 0.9 s) and measure: that test gave +5...+7 ms for 13/13 measurable types.
