---
name: style-dna
description: Chooses, generates and validates the Style DNA (dna.json) of a video - palette, type, texture, motion personality, transitions, camera, sound palette, signature moves, forbidden list - so no two videos share the same look ("same soul"). Includes 12 reference-derived presets, a generator with a variety ledger that refuses looks too close to the previous videos, and rules for inventing a style from a mood word. Use at the start of ANY video, motion graphic, intro, reel, explainer or animation, before writing scene code, and whenever the user says outputs look the same, generic, templated or "AI-looking".
---

# style-dna — a style is DATA, chosen per video, never defaulted

The "same soul" problem has one cause: the model reaches for the same palette, fonts, easing and scene list every time. This skill makes the look an explicit, validated file (`dna.json`) that is **different from the last videos by construction**.

## What you do (5 steps)
1. **Read the ledger:** `.motion/style-history.json` (create the folder if missing). Note the last 3 DNA names. They are forbidden starting points.
2. **Get 3 divergent candidates:**
   `python3 skills/style-dna/scripts/dna_generate.py --candidates 3 --out-dir dnas/ --history .motion/style-history.json [--mood "calm,nocturnal"] [--dark|--light]`
   It prints name, family, constraint and pairwise distance (want >= 0.45). Alternatively start from a preset: `--list`, then `--preset NAME --mutate SEED` (a preset is a technique starting point; mutate re-hues, swaps display font within the family and re-times it so you never ship a reference clone).
3. **Choose one** with the brief (motion-director step "3 concepts"): the one that best serves the IDEA, not the one you like. Edit by hand if needed: change at most the palette hue, fonts, 2 signatureMoves.
4. **Validate:** `python3 skills/style-dna/scripts/dna_generate.py --check dnas/dna-candidate-2.json --history .motion/style-history.json` -> exit 0 required (schema, contrast ink/bg >= 4.5, shipped fonts, valid ease names, sound palette, distance >= 0.45 to the last 5). Copy it to `<project>/dna.json`.
5. **After the video ships:** `python3 skills/style-dna/scripts/dna_generate.py --add dna.json --name <video> --history .motion/style-history.json` (qa-critique's `fingerprint.py --add` fills the measured half of the same entry).

## The schema (dna.json)
```json
{
 "name": "...", "version": 1, "family": "neon-mono | live-3d | halftone-poster | glass-dark | editorial | product-film | radial-burst | clay-mono | torn-paper | terminal-brutal | swiss-poster | soft-3d-toy | custom",
 "mood": ["..."], "constraint": "the ONE hard rule that makes it a style",
 "palette": {"mode":"mono|duotone|neutral-pop|tri-accent|analogous|complementary|paper-ink","dark":true,"hue":150,
             "bg":"#..","bg2":"#..","ink":"#..","ink2":"#..","accent":"#..","accent2":"#..","support":["#..","#.."]},
 "type": {"display":"Anton","body":"Inter Tight","mono":"JetBrains Mono","accentSerif":null,"case":"upper|lower|sentence|mixed",
          "tracking":{"display":0.01,"body":0,"label":0.18},"weights":{"display":400,"body":400},"scale":[1,1.6,2.6]},
 "texture": {"grain":0..1,"vignette":0..1,"halftone":0..1,"paper":0..1,"scan":0..1,"bloom":0..1,"dust":0..1,"chromatic":0..1,"lightleak":0..1},
 "motion": {"personality":"calm-precise|snappy-punchy|elastic-pop|heavy-cinematic|jittery-handmade|fluid-liquid|mechanical-steps",
            "ease":["outExpo","inOutSine"],"curves":["glide","settle"],"spring":{"w":9,"z":0.85},"stagger":0.07,"cutRate":0.5,"hitStyle":"...","hold":[0.7,1.6]},
 "transitions": ["names from transitions-projections"], "camera": {"move":"slow-push","drift":0.01,"parallax":true,"shake":0.1,"dof":false,"overscan":0.04},
 "layout": {"grid":"center-stack","margins":64,"density":"sparse","aspect":"9:16"},
 "sound": {"palette":["neon-mono"],"bpm":96,"key":"A","scale":"minor","reverb":"large-dark","brightness":0.45,"mix":{"music":-18,"sfx":-9,"voice":-6},"profile":"social"},
 "signatureMoves": ["2-5 recognisable recipes"], "forbidden": ["what this video must NOT do"], "refs": ["v01"]
}
```
Full field-by-field meaning: `reference/schema.md`. Reading it in a scene: inline the JSON (`const DNA = {...}`) or `fetch('dna.json')`; use `Lab.mixColor` for tints, `DNA.motion.ease[0]` via `Lab.ease.get`, `DNA.texture.*` for FX strength.

## The five dials that make two videos feel different (change at least three vs the previous video)
| Dial | Range | What to change |
|---|---|---|
| Palette logic | mono / duotone / neutral-pop / tri-accent / analogous / complementary / paper-ink + dark or light | not just the hue: the LOGIC |
| Type character | caps condensed / heavy grotesk / serif italic / slab / mono / rounded / marker, + accent face | display font, case, tracking, mixing |
| Texture | neon bloom / halftone / paper / scan / grain / clay vignette / glass / clean | at least one visible texture |
| Motion personality | calm-precise, snappy-punchy, elastic-pop, heavy-cinematic, jittery-handmade, fluid-liquid, mechanical-steps | ease set + spring + stagger + cut rate |
| Transition set | 3 named transitions, one per seam | never crossfade everywhere |
Also: camera (locked / push / orbit / handheld / push-through), layout density, sound palette.

## Inventing a DNA from a mood (when no preset fits)
1. Write the CONSTRAINT first (one sentence). Strong ones: "one hue + neutrals", "duotone with halftone on everything", "everything is paper", "everything is dark glass", "monospace only", "three accents on grid paper", "cream clay + one tone shift".
2. Choose the material (glass, paper, clay, light, ink, metal, screen) -> texture + sound palette + transitions.
3. Choose type that matches the material (references/type-character.md).
4. Choose palette logic + hue with `reference/palettes.md` (OKLCH recipes, contrast rules).
5. Choose motion personality from `reference/motion-personalities.md`.
6. List 3 signatureMoves (things a viewer would recognise) and 4-6 forbidden items.
7. Run `--check`.

## Anti-sameness rules (hard)
- Never start from the previous video's DNA. `--check` fails below distance 0.45.
- No default "centered card on purple-blue gradient", no Inter-only, no same spring on everything.
- At least one element per scene must break the grid or scale (huge numeral, cropped type, offset object).
- Every scene changes at least two of: background tone, object type, type treatment, camera move.
- If the user supplies brand colours/fonts, they replace palette/type; everything else must still be chosen fresh.

## Variation knobs
| Knob | Effect |
|---|---|
| `--seed` | different random draw, same constraints |
| `--family` | force a family |
| `--mood a,b` | words: calm, nocturnal, energetic, playful, luxury, tech, warm, cold, gritty, clean, retro, cinematic |
| `--hue 0..360` | force the accent hue |
| `--dark / --light` | base lightness |
| `--min-distance` | stricter variety (default .45) |
| `--mutate SEED` | re-hue + re-font + re-time a preset |

## Weak-model protocol
1. Never type a palette from your head. Run the generator, then edit.
2. Never skip `--check`. Quote its output in your message to the user.
3. Keep every colour in scene code coming from `DNA.palette` (the linter flags stray hex that is not in the DNA).
4. If the user dislikes the look, change ONE dial and re-run `--check`.

## Failure modes
| Symptom | Fix |
|---|---|
| `SAME_SOUL` | the message lists which fields equal the previous video; change those |
| contrast error | raise `ink` lightness or lower `bg`; display text needs >= 3:1, body >= 4.5:1 |
| purple/blue-on-dark warning | pick another hue unless the brief demands it |
| font not in shipped set | embed it yourself or choose from `skills/kinetic-typography/fonts/fonts.json` |
| every video still feels the same | you changed hue only: change palette logic + type + motion personality |

Files: `dna/*.json` (12 presets: neon-mono-night, live-3d-icon-arc, halftone-poster-loop, talking-head-designed-broll, glass-icon-universe, product-film-ui, radial-neon-burst, editorial-explainer, glass-folder-render, clay-mono-editorial, torn-paper-collage, terminal-brutalist) · `scripts/dna_generate.py` · `reference/schema.md` `palettes.md` `type-character.md` `motion-personalities.md` `textures.md`.
