# Ownership table (fill before launching anyone)

| Path | Owner | Others may |
|---|---|---|
| brief.md, dna.json, storyboard.md, ORCHESTRATION.md, stitch.html | Director | read |
| lookdev/** | Art director | read |
| scenes/01-<name>.html (+ .assets/) | Scene engineer 01 | read |
| scenes/02-<name>.html (+ .assets/) | Scene engineer 02 | read |
| assets/** | Asset builder | read |
| audio/** | Sound designer | read |
| out/qa/** | QA critic | read |
| out/*.mp4, out/events.json | Director (integrator) | read |

Rules: one owner per path. If two workers need the same file, split it (e.g. `assets/icons-ui.svg` vs `assets/icons-hero.svg`) or give it to one worker and have the other send needs in its report. Generate a machine-checkable version with `python3 scripts/manifest.py owners-template <project>`.
