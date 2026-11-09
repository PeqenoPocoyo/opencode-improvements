# Style sound palettes

Pick `dna.sound.palette[0]`. These are the palettes in `scripts/palettes.py` (run `python3 palettes.py` for the live list). A palette changes: key/scale, brightness, room size, which recipe plays for each event (`swap`), extra layers (`add`), what is removed (`drop`), tonal walks.

| Palette | Look it matches | Sound | Key / scale | BPM | Reverb | Brightness | Music bed |
|---|---|---|---|---|---|---|---|
| neon-mono | one-hue neon on black (v01, v07) | deep sub, long dark tails, tonal blips (pop/tick/appear -> blip), sweeping risers, bass-drop on big hits | A minor | 96-124 | large dark | .42 | cinematic |
| glass-dark | black + glossy glass (v05, v09) | glass dings, 6-11 kHz air shimmers over soft sub pulses, whoosh gets a shimmer tail | F# major-pent | 88-108 | hall | .68 | ambient |
| halftone-collage | duotone poster (v03) | paper slaps, stamps, bass hit per layer arrival, rip on scene-cut | D minor-pent | 92-110 | small room | .52 | boom-bap |
| clay-mono | cream + black clay 3D (v10) | soft thuds, wooden ticks, matte whooshes; no boom/bass-drop | C major-pent | 78-98 | small | .38 | lofi |
| editorial | grid-paper explainer (v08) | marimba blips, dial ticks for count-ups, stamp under impacts, chime tails on reveals | G major-pent | 100-116 | small bright | .55 | pop-pluck |
| product-film | UI as hero (v06 shipped silent) | tactile clicks, soft swipes, light chime on success; no big impacts | F major | 88-108 | small | .5 | ambient |
| radial-burst | node + rays + words (v07) | one tonal blip per word walking up the scale + soft sub tap; rising sweep for extension; low boom at the end | D minor-pent | 116-140 | medium | .5 | techno |
| torn-paper | torn paper typography (v11) | rips, slaps, tape, stamps, bass thump per word, snare-roll risers | A blues | 88-106 | small | .56 | boom-bap |
| live-3d | footage + CG objects (v02) | mechanical wheel clicks, panned soft whooshes, one shutter, gentle sub | C minor-pent | 80-100 | medium | .5 | ambient |
| default | no DNA | balanced | C minor-pent | 96-116 | medium | .5 | pop-pluck |

## Making a new palette (when none fits)
1. Copy the closest entry in `palettes.py`; rename.
2. Decide the MATERIAL of the picture (glass, paper, metal, wood, plastic, light) -> choose recipes: glass -> glass-ding/shimmer; paper -> paper-slap/rip/tape; metal -> stamp/impact; plastic/UI -> click/tick/blip; light/neon -> blip/zap/riser.
3. Pick key and scale by mood: minor/pentatonic minor = serious/night; major pentatonic = bright/friendly; blues = gritty.
4. Brightness: dark UI .35-.45; neutral .5; glossy .65-.7.
5. Room: small 0.6-0.8 (intimate/dry), medium 1.0, large 1.3-1.5 (epic/dark).
6. Test with a synthetic `events.json` and look at the report; two palettes on the same events should sound clearly different (compare the spectral balance lines).

## Anti-sameness for sound
Two videos in a row must not share palette + key + music family. Keep it in the ledger: `.motion/style-history.json` stores `dna.sound`; `dna_generate.py --check` compares them through the DNA distance.
