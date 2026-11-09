# Music beds

Licensed or user-supplied music always beats the procedural bed. `musicgen.py` / `sync_cues.py --music-gen` makes a SCRATCH bed (kick/clap/hat patterns per genre family, sub bass on chords in key, pad, pluck, sidechain pump) so the video has a pulse while you work; say so to the user and offer to swap.

## Options
| Source | How | Notes |
|---|---|---|
| User music | `--music file.mp3` ; add `--music-detect` to find BPM/beat offset, `--music-align hero` to shift so the first big hit lands on a beat | check licence of what the user provides |
| Procedural | `--music-gen [family]` families: cinematic, ambient, lofi, boom-bap, pop-pluck, techno | bed = 8-32 bars at bpm in the DNA key |
| CC0 / free libraries | Mixkit, YouTube Audio Library (check each track's licence), Pixabay | record title, URL, licence in `audio/music-licence.txt` (`--music-source`, `--music-license`) |

## Beat-grid discipline
1. `beat = 60/bpm`. Put visual hits on beat/4 or beat/2 multiples (CONVENTIONS §4) unless the DNA says free time.
2. If the music is not yours: detect BPM and the first downbeat; shift the music (`--music-offset`) so a downbeat lands on the hero hit.
3. Cut on bars: scene changes on bar starts (every 4 beats), small changes on beats.
4. Risers end on a downbeat; the drop follows on that beat.
5. End on the downbeat of the last bar; add a 0.3 s tail fade (`--music-fade-out`).
6. Music level -18 dB under SFX; duck under voice (automatic).
7. Music arc: `--music-arc build` raises intensity into the final third; `--music-drop auto` places a drop at the hero hit.

## Mood -> bed
| Mood | family | bpm | key |
|---|---|---|---|
| nocturnal, serious | cinematic / ambient | 70-100 | minor |
| friendly explainer | pop-pluck | 100-116 | major pent |
| gritty poster | boom-bap | 88-106 | blues/minor |
| techno burst | techno | 116-140 | minor pent |
| calm product | ambient / lofi | 80-98 | major |

## Licence hygiene
Never include a track you cannot name and licence. Never use a ripped track. Put the credit text the licence requires in the post/description. If unsure, use the procedural bed or no music.
