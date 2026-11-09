---
name: generative-play
description: Free, recreational, generative mode - no brief needed. Produces many different loopable pieces by crossbreeding DNA presets, 3D shader worlds, 34 art generators, kinetic type and FX (play_make.py), then lets the user pick and deepen one. Also series/mutations/constraint cards to stay creative. Use when the user says "me surpreenda", "explore", "brinca", "gera variações", "séries de loops", wants backgrounds/posters/loops without a message, or when ideas are stuck and the videos all look the same.
---

# generative-play — make a lot, look, choose, deepen

Creativity for a small model = **breadth by machine, taste by the human, depth by the model.** Do not ask what the user wants; show 6–8 real renders and let them point.

## Procedure
1. Project: `bash skills/scene-runtime/scripts/setup.sh play-proj` (copies all runtimes, fonts, three.js).
2. Make pieces: `python3 skills/generative-play/scripts/play_make.py --project play-proj --n 8 --seed <new number>`  (`--list` for recipes/presets; `--recipe type-poster --size 1080x1350`; `--repeat p03/piece.json --seed 77` for a series in the same recipe).
3. Render one still per piece (`--at 1.6 --root play-proj`) and tile them (PIL) into ONE sheet; **Read it**; write one line per piece (what it is, what is good).
4. Show the sheet to the user and recommend 2 (say why). Do not render videos for all.
5. Deepen the chosen one: edit its `CFG` in the scene (palette, shader, art, word, style), try 2 mutations (below), render the 6-second loop (`--fps 30 --sub 1`), add sound if asked (`sound-design-pro`, events at loop beats) and run `qa-critique` basics.
6. Log in the ledger (`dna_generate.py --add`), so the next play session starts elsewhere (new `--seed`, different `--recipe`).

## Recipes in play_make.py
`world-and-field` (3D shader + art field + word) · `art-poster` (gradient ground, focal art, word filled with art) · `pure-generative` (art only) · `shader-solo` · `type-poster` · `halftone-print` (riso/CMYK) · `terminal` (glyphs + plexus + CRT) · `orbit-system` (paper infographic). Add your own by adding an `if (r === 'name')` block in the template and a line in `RECIPES`.

## Mutation menu (change ONE structural thing, name the result)
Palette family swap · invert light/dark · polar↔cartesian · symmetry (mirror/N-fold) · scale ×4 / ÷4 · quantise to steps · feed a generator's output into another as a mask · replace noise by a sum of sines · slow it ×0.3 or speed ×3 · move the focal out of the centre and crop it · add one rule-breaking element (a single red dot, a single tilted line).

## Constraint cards (draw one, obey it for the whole piece/series)
2 colours + black · no gradients · all on a 12-col grid · diagonal motion only · one continuous camera move · type is the only graphic · monochrome + 1 accent that appears exactly 3 times · everything loops in 4 s · everything made of circles · everything made of lines · only one font weight.

## Series rules
A series = same recipe or same constraint + 6 different seeds/palettes → a coherent set (grid post, album). Keep 1 constant (grid, type, or frame) and vary 2.

## Quality bar for play pieces
No piece ships if: text clipped, contrast < 4:1 on the word, dead first second, loop seam visible (render t=0 and t=6: must match), or two pieces in the sheet look alike (change recipe/palette family).

## Files
`scripts/play_make.py` · template lives inside it (CFG JSON at the top of every generated scene = the whole piece)
