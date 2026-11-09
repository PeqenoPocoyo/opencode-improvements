# Concept methods (how to get past the default idea)

The default idea is: "title, three icons, a card, fade". Replace it with a concept.

## 1. From topic to claim
Topic = "time management". Claim = "your day is a staircase, and most people stand on the first step". A claim can be drawn; a topic cannot. Write the claim as a sentence with a verb.

## 2. From claim to metaphor to image
| Claim shape | Metaphor family | Image examples |
|---|---|---|
| growth, progress | climb, build, grow | stairs, stacking bars, tree rings, rocket |
| focus, clarity | light, zoom, tune | spotlight cone, focus pull, signal from noise |
| speed, efficiency | track, flow, shortcut | racing lines, conveyor, arrow cutting a maze |
| connection | network, bridge, orbit | nodes and edges, ring of icons, magnet |
| risk, fragility | glass, balance, edge | seesaw, cracking plate, tightrope |
| chaos -> order | sort, align, tidy | scattered shapes snapping to a grid |
| time | clock, scroll, count | clock hands, tickers, sun arc, odometer |
| money, value | scale, stack, meter | bars, coin stacks as bars, price tag flip |
| decision | fork, switch, coin | two doors, toggle, split screen |
| secret, reveal | cover, peel, tear | paper tear, curtain, blind shadows opening |
Pick the metaphor whose image is simple enough to draw with one object + one motion.

## 3. Concept cards (when stuck, draw one and obey it)
1. **Scale shift** - show the subject giant/tiny (numerals the size of the person).
2. **Material swap** - everything is paper / glass / clay / light / ink / metal.
3. **Constraint** - one hue, one font, one shape family, 4 colours max.
4. **Camera as character** - the camera tunnels through objects; no cuts, only moves.
5. **Inversion** - show the problem as a big pretty thing, solution as a tiny precise one.
6. **Loop** - the end becomes the start; the last word is the first.
7. **Grid game** - everything snaps to a 12-column grid with one rotated rebel.
8. **Counting** - a number changes and the world reacts to it.
9. **One object, many lives** - the same shape becomes six things by morphing.
10. **Interface as stage** - UI elements are the actors; cursor is the camera.
11. **Rhythm first** - choose BPM and let beats drive every change; picture follows sound.
12. **Reveal by subtraction** - start busy, remove until the claim remains.
13. **Zoom through** - each scene is inside an element of the previous.
14. **Handmade** - cut, tear, tape, stamp; imperfection is the style.
15. **Data as landscape** - the chart becomes terrain/city; fly over it.
16. **Typography as architecture** - letters are the buildings/rooms.

## 4. Divergence test (three concepts must differ)
| Axis | A | B | C |
|---|---|---|---|
| metaphor | | | |
| material/texture | | | |
| palette logic | | | |
| motion personality | | | |
| camera | | | |
| type character | | | |
| structure (linear / loop / list / reveal) | | | |
Fill the table. Fewer than 3 rows differ across ALL pairs -> rewrite the closest pair.

## 5. Concept write-up template
```
CONCEPT B — "<name>"
Pitch: one line.     Metaphor: ...     Material: ...     Structure: ...
Frame 0 (hook): ...
Signature move: ...  (what the viewer will remember)
Mid-point surprise: ...
Last frame: ...      Loop? yes/no
DNA seed: mood words / family / hue
Serves the idea because: ...
Risks: ... (what could look bad or be hard to build) and how to cheat it
```

## 6. Buildability filter
Prefer concepts whose key image can be made with the runtimes: shapes + type + shader backgrounds + three.js primitives + collage layers + UI kit + rig figures. Avoid concepts that need photographs, faces, brand logos or realistic humans; replace with silhouettes, halftone figure busts, icons, objects.

## 7. Cheats for hard images
| Wanted | Cheat |
|---|---|
| realistic person | silhouette with rim light (rig.js), halftone bust (collage.js), or hands only |
| city | instanced boxes with fog and tilt-shift (3D bg skill) |
| product shot | glossy rounded-box + canvas glyph + studio light |
| crowd | `Rig.crowd(n,seed)` or dot grid |
| landscape | fbm mountains shader + fog |
| brain/organ | glowing node graph or noise blob with rim |
| money | stacked rounded rectangles as bars |
