# dna.json field reference

| field | type | meaning | consumer |
|---|---|---|---|
| name | string | unique video look id; goes into the ledger | all |
| family | string | which technique family (neon-mono, ..., custom) | director, generator |
| mood | string[] | words the look must evoke | director, QA rubric |
| constraint | string | the ONE hard rule; QA checks it | QA |
| palette.mode | enum | palette logic | distance, QA |
| palette.dark | bool | dark base? | |
| palette.hue | 0-360 | accent hue (deg) | distance |
| palette.bg/bg2 | #hex | background and secondary background (gradient end) | scene bg |
| palette.ink/ink2 | #hex | text, muted text | type |
| palette.accent/accent2 | #hex | primary and secondary accent | emphasis, glow |
| palette.support[] | #hex[] | ramps, charts | UI, charts |
| type.display/body/mono | font family | must be in fonts.json or embedded | type.js |
| type.accentSerif | font or null | accent face for emphasis words | type.js |
| type.case | upper/lower/sentence/mixed | | type.js |
| type.tracking | {display, body, label} em | | |
| type.weights | {display, body} | 100-900 | |
| type.scale | [1, x, y] | hierarchy ratio | |
| texture.* | 0-1 | strengths (see textures.md) | FX / post |
| motion.personality | enum | see motion-personalities.md | all scenes |
| motion.ease[] | Lab.ease names | main eases | |
| motion.curves[] | Lab.curves names | named curves | |
| motion.spring | {w,z} | Lab.spring params | |
| motion.stagger | s | per-element delay | |
| motion.cutRate | cuts/s | edit density | storyboard |
| motion.hitStyle | string | how beats look | |
| motion.hold | [min,max] s | hold range per state | |
| transitions[] | names | allowed transitions (transitions-projections catalog) | stitch |
| camera | {move, drift, parallax, shake, dof, overscan} | | |
| layout | {grid, margins, density, aspect} | | |
| sound | {palette[], bpm, key, scale, reverb, brightness, mix, profile} | | sound-design-pro |
| signatureMoves[] | string[] | recognisable recipes (2-5) | scene engineers |
| forbidden[] | string[] | must-not list | lint + QA |
| refs[] | string[] | reference ids that inspired it | docs |

Unknown extra fields are allowed (custom DNA). Required for `--check`: name, palette (bg, ink, accent, accent2), type.display, texture, motion, transitions, camera, sound, signatureMoves, forbidden.
