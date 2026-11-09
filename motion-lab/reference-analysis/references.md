# Reference analysis — what the 11 reference videos teach

Method: 12–18 frames per video (contact sheets), scene-cut detection, loudness (EBU R128), onset detection and band-energy shares on the audio, cut↔onset alignment. I cannot hear; sound conclusions come from measurements, not taste. Cut counts from automatic scene detection are **inflated by fast camera moves** (v03, v11): read them as "very busy", not as exact edit counts.

These videos are technique references. **Never copy a reference's brand, logo, character, watermark, copy or exact layout.** Rebuild the *technique* with your own subject.

| id | format | length | style family | one-line signature |
|---|---|---|---|---|
| v01 | 9:16 30 fps | 15.5 s | Neon monochrome silhouette story | one hue (green) on black, flat vector figures with rim light, giant glowing numerals, text as scenery |
| v02 | 9:16 25 fps | 10 s | Live-action + 3D compositing | real macro shot of a hand on a mouse; glossy 3D app icons orbit in an arc, motion-blurred, in front of a shallow-DoF background |
| v03 | 9:16 30 fps | 15 s | Halftone collage poster loop | duotone blue + red halftone, layered cutouts, camera pushes through the stack, seamless loop |
| v04 | 9:16 30 fps | 65.8 s | Talking head + designed B-roll | person with centered word-by-word captions, cutaway scenes: dark green lamp + paper note, serif-italic on white, glowing brain, circuit grid, magnet note, social-post mock |
| v05 | 9:16 60 fps | 16.7 s | Glass icon universe (dark) | dark glossy rounded-square icons with colored rim light, floating in a ring, bloom halo, text swaps "Any case / Any need" |
| v06 | 16:9 24 fps | 81.6 s | Product film (UI as hero) | screen UI rebuilt as vector, cursor choreography, dashboard → projected into a 3D city grid, comments/threads, export fan-out, cream editorial look; **no audio track** |
| v07 | 9:16 30 fps | 6.6 s | Radial neon typographic burst | single glowing node, 12 rays, words fly along rays, a ray extends to a new keyword, loops |
| v08 | 9:16 29.97 fps | 17.9 s | Editorial explainer | grid paper, grotesk + serif-italic type mixing, purple/orange/lime accents, 3D-rendered brain cutout, count-up numbers with glow, bar chart, sparkle stars, target & arrow |
| v09 | 9:16 30 fps | 88 s | Tutorial screen recording | someone building a glass 3D folder with cards popping out in After Effects: null controllers, light-sweep effect, front/back layers, final glossy green render with cursor arrow |
| v10 | 9:16 30 fps | 33.5 s | Monochrome "clay" 3D editorial | cream background with vignette, black/grey 3D-rendered objects (rocket, magnifier, hand, seesaw, statue), bold grotesk with weight/tone shifts, strikethrough, pill labels, dark end card |
| v11 | 9:16 60 fps | 27 s | Torn-paper collage typography | off-white paper, red/black ink, halftone cutout portraits, torn edges, tape/label strips, window-blind shadows crossing the frame, hand-drawn circle |

## 1. Cross-cutting findings (these are the real lessons)

1. **One hard constraint per video.** Every strong reference limits itself: one hue + neutrals (v01, v07, v10), duotone (v03), a 3-color accent set on a neutral (v08), or one material (paper in v11, glass in v05). "Everything looks the same" in AI output is the opposite: default palette + default fonts + default easing. Pick a constraint FIRST (see `style-dna`).
2. **Typography is a character, not a caption.** v08 mixes grotesk and serif-italic *in the same sentence*; v10 shifts words from grey to black as they are spoken; v01 uses numerals the size of the figure; v11 uses stencil/condensed slabs on tape strips. Type is staged, layered behind/in front of objects, and animated per word with its own motion.
3. **Objects feel physical.** Soft contact shadows, rim light, specular edge, slight rotation (v05, v09, v10). Nothing is a flat rectangle floating with a CSS drop-shadow.
4. **The camera never sits still.** Even "static" shots have a slow push, parallax between layers, or a drift (v03, v10, v01, v06). Cuts are replaced by camera moves *through* things.
5. **Transitions are carried by an object or a shape.** v01: dashed frame / stair / book, v05: the ring that forms and dissolves, v08: arc strokes and sparkle stars sweeping through, v11: paper tears and white flashes, v06: UI element expands into the next scene.
6. **Texture is always present.** Grain, vignette, halftone, paper fibre, scanlines, bloom. Flat vector with no texture reads as "template".
7. **Rhythm is built from three levels at once.** Macro (scene length 2–4 s), meso (a word/object every 0.3–0.6 s), micro (a glow/shake/scale pulse on each hit, 0.1–0.25 s decay).
8. **Hook inside the first second.** All the short-form references show a strong shape, number or movement at frame 0–10; none open on black or a logo.
9. **Sound lands on the frame.** In the polished ones (v03, v09, v10, v11) the audio onset closest to a visual change has a **median offset of +7 to +19 ms (v09 −22 ms)** — i.e. within one frame at 30 fps. In v01 and v04 it was +46…+92 ms (later) and those feel looser. Rule: transient of the sound inside ±1 frame of the visual impact, never later than +1 frame.
10. **Loud and bass-heavy.** Social references measure **−13 to −15 LUFS integrated** (v09 tutorial −20, v02 −17.7), true peaks often at/above 0 dBFS (clipped by the platform encode — do not copy that). **65–90 % of the energy sits below 400 Hz** (sub 120 Hz: 30–73 %). Little above 2 kHz: 2–7 %. The "cheap beep" sound is the opposite spectrum (energy 1–6 kHz, no sub, no tail).
11. **Few elements, big.** v07 has one node and words; v05 has one icon at a time; v10 has one object + one line of text per beat. Density comes from motion, not from clutter.
12. **Variety inside a video:** each scene changes at least two of {background tone, object type, type treatment, camera move}. Sameness inside one video reads as a loop of one template.

## 2. Per-reference breakdown (technique → how to rebuild it generatively, with no source images)

### v01 — Neon monochrome silhouette story (15.5 s, 0.65 cuts/s, −14.3 LUFS)
- **Look:** background = dark → bright green vertical gradient + floor reflection; figures = flat dark polygons with a thin bright rim light on the lit edges; huge numerals (`12`, `18`) glowing, partially covered by the figure; small glowing captions; subtle dust particles; corner watermark.
- **Motion:** word-by-word captions that scale in on voice-over rhythm; counters tick (12 → 18); camera drifts; scenes are metaphors (staircase, desk, telescope, book) rather than diagrams.
- **Transition devices:** dashed-line frame rotating, black beat, lens-like focus pull, a ball covering text.
- **Rebuild:** `vector-characters` (skeleton rig + polygon silhouettes + rim light), `kinetic-typography` (glow numerals), `style-dna` neon-mono recipe, `generative-3d-backgrounds` (vertical gradient + volumetric haze shader).
- **Sound (measured):** 61 BPM feel, sub+low 84 %, onset density 7.7/s (voice-over + hits), loudness −14.3 LUFS.

### v02 — Live action + 3D icon arc (10 s, no cuts, −17.7 LUFS)
- **Look:** a real shot, shallow depth of field. 3D glossy rounded-square icons placed on an arc above the hand, each with a rim highlight and motion blur while rotating along the arc as the mouse wheel is scrolled. Icons swap (new set slides in) → the arc continues.
- **Rebuild:** `live-action-compositing` (match grade, DoF, shadow, grain) + `generative-3d-backgrounds` three.js rounded-box icons with canvas-drawn glyph textures; arc = parametric path; scroll-link = icon index driven by a velocity curve; motion blur = render subframes.
- **Sound:** 3.4 onsets/s, 20 % silence, sub/low 81 % — sparse, wheel clicks + soft whooshes.

### v03 — Halftone collage poster loop (15 s, −14.7 LUFS, cut↔onset 69/78 within 80 ms, median +7 ms)
- **Look:** duotone blue/cream photo layers with red halftone crowds; cutouts (signs, a van, a bird) on separate layers; sky with grain; small corner meta text; the camera pushes through the stack (zoom + slight tilt), signs fly in with rotation and overshoot, then pull out; **the end frame equals the first frame (loop)**.
- **Rebuild:** `collage-paper-texture` (halftone shader, duotone map, cutout with white sticker border, parallax layers), `transitions-projections` (zoom-through), `scene-runtime` loop helpers.
- **Sound:** sub 65 %, 10.5 onsets/s — hits on every layer arrival; transient on the frame.

### v04 — Talking head + designed B-roll (65.8 s, 15 cuts, −13 LUFS)
- **Look:** speaker with **center-screen lowercase word-by-word caption** (white, small, one word at a time). B-roll cutaways are *designed scenes*, each in a different world but sharing a palette (deep green, cream, yellow highlighter): (1) hanging lamp spotlight on dark green with a pinned paper note (text underlined in red); (2) white page, vintage illustration of people, serif italic words scattered; (3) glowing brain on green; (4) blueprint grid with circuit lines, gears, a tiny video thumbnail with a label; (5) pegboard/magnet with a green sticky note; (6) social post UI mock.
- **Rebuild:** `video-orchestration` (cutaway planning from transcript), `kinetic-typography` (caption styles), `ui-in-video` (post mock), `generative-3d-backgrounds` (spotlight cone + dust), `collage-paper-texture` (paper note).
- **Sound:** voice leads (mid band 45 %), sub 41 %; only 2/15 cuts have an onset within 80 ms (cutaways are not hit-synced — they ride the voice). Lesson: *talking-head videos sync to words, not to beats*.

### v05 — Glass icon universe (16.7 s, 60 fps, −14.5 LUFS)
- **Look:** pure black; each icon is a dark rounded square with a thin multi-color gradient rim (orange→violet), glossy inner glyph, soft colored bloom behind the focused icon (electric blue ring/halo); icons float around the title text ("Any case", "Any need") at different depths with blur on far ones; formation changes: scattered → ring → single icon (arrow) → scatter. Text swaps with a blur cross-fade.
- **Rebuild:** `generative-3d-backgrounds` three.js recipe "glass icon" (RoundedBox + fresnel rim shader + bloom) or the 2D canvas version in `fx.js` (rim gradient stroke + radial glow); ring layout = angle k·2π/n with spring radius; depth = scale + blur by z.
- **Sound:** 5.6 onsets/s, bright air band 6.8 % (the only reference with real air) — glassy ticks/shimmers on formation.

### v06 — Product film: UI as the hero (81.6 s, 16:9, **no audio**)
- **Look:** warm light-grey canvas; the product UI rebuilt as clean vectors; a speaker's video in a rounded player chrome; a pink editorial slide; dashboards with charts and tooltips; **"Projecting dashboard coordinates into a 3D city grid"** — 2D scatter points become glowing pins on an isometric low-poly city (soft pastel buildings, fog, tilt-shift), with tooltips ("Fernhill — 20 bikes", clock chips "6:30 am"); a comment thread card; an "Export" button that fans out to logos (tiles); final text edit "Claude makes it Yo…" with a selection highlight and cursor.
- **Techniques:** cursor choreography (click ripple, drag), window chrome, scrubber timeline, camera pushes into UI, **projection of 2D data into 3D**, tilt-shift, soft pastel clay city, chip tooltips.
- **Rebuild:** `ui-in-video` (UI kit + cursor + data viz), `transitions-projections` (2D→3D lift), `generative-3d-backgrounds` (instanced low-poly city).
- **Sound:** none present. If you add sound, keep it sparse and tactile (click, soft whoosh, tick, a single chime).

### v07 — Radial neon typographic burst (6.6 s, −14.7 LUFS)
- **Look:** black; a small diamond-in-circle node and the word SUCCESS; 12 white rays burst out from the center like a clock; words ("Focus", "Discipline"…) appear in green glow *along* the rays, rotated to the ray angle, staggered clockwise; at the end one ray extends and a new word (ACTION) appears bigger in cyan-white; ends back at the node (loop).
- **Rebuild:** `kinetic-typography` (text on radial layout), `motion-canvas-artwork` (radial layouts), glow via canvas shadowBlur or FX bloom; stagger = clockwise `i * 0.12 s`; ray draw = stroke-dashoffset with `outExpo`.
- **Sound:** sub 73 %, 10.5 onsets/s: each word = a short tonal tick + a soft sub tap; the extension = rising sweep; end = low thud.

### v08 — Editorial explainer (17.9 s, −13.2 LUFS, cut↔onset 2/2)
- **Look:** light grid paper; typography mixing **geometric grotesk (bold, black) + high-contrast serif italic (light grey)** inside one sentence; accent colors: royal purple, orange, lime; 3D-rendered brain cutout in a dotted circle; numbers count up with a soft orange glow; a bar chart whose bars rise with a line drawing across; labels inside dashed selection boxes with corner handles; 4-point sparkle stars sweeping in with a big grey arc; a target with an arrow that flies in.
- **Rebuild:** `kinetic-typography` (mixed-font lines, blur-in per word), `ui-in-video` (dashed selection boxes, chart), `motion-canvas-artwork` (sparkles, arcs). Illustrations (brain, target) → draw as simple 3D-lit vector or use three.js spheres/torus; or ask the user for an asset.
- **Sound:** 5.8 onsets/s, mid band 40 % (more "voice/pad" than boom); cut↔onset exact.

### v09 — After Effects tutorial (88 s, −20.2 LUFS)
- **Teaches the object, not the screen recording.** The final piece: a translucent green glass **folder** (front plate + back plate), cards pop up from inside with a parallax, light sweep along the glass edge, a glossy arrow cursor, dark green radial background. Built from: front layer + back layer, null controllers for rotation, "CC Light Sweep" (a moving specular band masked to the layer), cards between the two plates.
- **Rebuild:** three.js (two RoundedBox plates + transmissive material + cards between) or a CSS 3D version (`transform-style: preserve-3d` with front/back plates and sandwiched cards); light sweep = animated gradient mask; controller = one group node holding all rotation.

### v10 — Monochrome clay 3D editorial (33.5 s, −14.9 LUFS, cut↔onset 7/8, median +9 ms)
- **Look:** cream (#F3F0E8-ish) paper with a **strong vignette and a faint grid**; a leaf silhouette in the corners; a logo at the top; objects in grayscale 3D (shiny black rocket, black magnifier, hand with floating glossy app icons, statue with laptop, ball on a seesaw) with soft shadows; headline in a heavy grotesk with a **grey→black tone shift for the emphasized word**, supporting line in regular weight; pill labels (dark, white text, soft shadow) stacking; strikethrough on a word; end card on near-black.
- **Rebuild:** `generative-3d-backgrounds` three.js "clay" material (MeshStandard roughness .35, black/grey, soft area light + ground shadow), `kinetic-typography` (tone-shift emphasis), `ui-in-video` (pills).
- **Sound:** sub 46 %, low 30 %, 7.3 onsets/s, 8 scenes ≈ 4 s each; each scene = whoosh in + soft impact + 2–3 ticks for pills.

### v11 — Torn-paper collage typography (27 s, 60 fps, −13.3 LUFS, cut↔onset 91/104, median +19 ms)
- **Look:** off-white crumpled paper background with diagonal window-blind shadows drifting across; black-and-white halftone portraits with red torn-paper blocks behind; words on tape/label strips (stencil slab / condensed grotesk, red or black), grid-line overlays, a hand-drawn cyan scribble circle around the key word; end: black card + logo.
- **Rebuild:** `collage-paper-texture` (procedural torn edges with noise, paper fibre texture, shadow overlay as animated gradient bars, label strips with slight rotation, scribble circle via `Lab.sketchPath` + stroke draw), halftone shader from `fx.js`, flash-frame transition (white flash 2–3 frames).
- **Sound:** sub 61 %, 5 onsets/s, 11 % silence (hits with air between); paper-rip/slap/tape sounds + a bass thump per word.

## 3. Style-family → recipe map

| family | background | objects | type | texture | camera | transitions | sound palette |
|---|---|---|---|---|---|---|---|
| Neon mono | vertical gradient of ONE hue, floor reflection | flat polygon figures + rim light | condensed grotesk, glowing | dust, scan, bloom | slow push + drift | focus pull, frame-carry | sub drones, low tick, whoosh-reverse |
| Live + 3D | the real footage | glossy 3D icons on a path | none or tiny | match footage grain | static | object-carry | wheel click, soft whoosh |
| Halftone collage | duotone sky | cutout stickers (white border) | stencil caps | halftone + grain | push-through + tilt | zoom-through, flash | slap, paper, bass hit |
| Talking head + B-roll | per-cutaway worlds, shared palette | designed props (note, lamp) | serif italic + sans captions | paper, dust | static + gentle push | hard cut on word | voice-led; sparse FX |
| Glass icons | black + colored bloom | glossy rounded squares | thin sans | bloom + rim | slow dolly + depth blur | ring formation | glass tick, shimmer, sub |
| Product film | warm neutral | vector UI + 3D city | UI font | very light | pushes into UI | element-expands-into-scene | click, soft whoosh, chime |
| Radial burst | black | rays + glow words | thin geometric sans | bloom | locked | loop | tonal tick, sweep |
| Editorial explainer | grid paper | 3D cutouts, charts | grotesk + serif italic | very light | gentle push | arc/sparkle sweep | pad + tick |
| Glass folder | dark radial green | plates + cards | none | specular sweep | slow orbit | none | glassy tick |
| Clay mono | cream + vignette | black 3D objects | heavy grotesk, tone shift | grain + vignette | slow push | object carry | impact + ticks |
| Torn paper | paper + shadow bars | halftone cutouts + tape | stencil/condensed | paper, halftone | jittery handheld | flash, tear | paper, slap, bass |

## 4. What the *toolkit videos* had instead (why they felt the same)
Same default palette, same Geist/Inter type, same spring easing, same "pill → card" morph, same HUD, same scene order, no texture, synthetic oscillator sound with the same 6 samples, sound started at the cue time instead of aligned by transient. None of the 11 references does any of that.
