# Type character (from the shipped fonts)

Fonts live in `skills/kinetic-typography/fonts/` (OFL, woff2, `fonts.css`, `fonts.json` with moods and pairings). Never rely on system fonts.

| character | display | body | accent | case | tracking | when |
|---|---|---|---|---|---|---|
| condensed caps slam | Anton / Bebas Neue / Oswald | Inter Tight | - | UPPER | 0-.06em | sports, trailers, neon numerals |
| heavy grotesk tone-shift | Inter Tight 800 / Archivo 800 | Inter Tight 400 | Instrument Serif italic | sentence | -.03em | clay, product, editorial |
| serif editorial | Instrument Serif / Playfair / DM Serif | Inter Tight | italic of the same | sentence | -.02em | storytelling, luxury |
| poster slab | Alfa Slab One | Archivo | Permanent Marker | UPPER | .1em | halftone, torn paper |
| stencil / war-poster | Black Ops One | Oswald | Permanent Marker | UPPER | .12em | gritty |
| geometric thin | Outfit 300 / Syne | Inter Tight | - | lower | 0 | glass, radial burst |
| mono terminal | JetBrains Mono / Space Mono | same | - | UPPER | .01em | terminal, data |
| rounded friendly | Fredoka / Nunito | Nunito | Caveat | sentence | 0 | kids, toy 3D |
| wide display | Unbounded / Syne | Inter Tight | - | UPPER or lower | 0 | tech, music |
| width-morph | Archivo (wdth 62-125) | Archivo | - | UPPER | 0 | stretch reveals |

## Mixing in one sentence (v08)
Grotesk 800 for the claim words, serif italic light-grey for the connective words: `<b>Make</b> <i>something</i> <b>people</b> <i>want</i>`. Same x-height, different texture. Never mix three families.

## Size hierarchy
scale [1, 1.6, 2.6]: body 1 (e.g. 42 px at 1080 wide), subhead 1.6, hero 2.6 -> or hero 4-8x for giant numerals. Line height: display .9-1.0, body 1.3. Safe area 9:16: x 64-1016, y 220-1560.

## Rules
- Caps faces (Anton, Bebas, Black Ops, Rubik Mono) need case upper; do not set them in lowercase.
- Emphasis = a change of tone (grey -> black), weight (400 -> 800), face (sans -> serif italic) or scale, not only colour.
- One emphasised word per line.
- Embedded fonts: `<link rel=stylesheet href=lab/fonts/fonts.css>` (setup.sh copies) and wait `document.fonts.ready` (render.mjs does).
