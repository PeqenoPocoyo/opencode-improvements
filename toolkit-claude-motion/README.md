# 02 · Dia do Juízo Final

![preview](../../media/juizo-preview.gif)

10 s · 1080×1080 · 60 fps · stereo, −14.1 LUFS · source: [`src/juizo/JuizoVideo.tsx`](../../src/juizo/JuizoVideo.tsx)

An apocalyptic title piece: a doomsday clock ticks 00:00:03 → 00:00:00 while a bar of hope drains, tension creeps in as camera shake, then one impact — flash, shockwave rings and debris — and the verdict slams in: *DIA DO **JUÍZO** FINAL* with the subtitle "ninguém está a salvo."

## Prompt

> do it, tema: dia do juízo final

## Process

| Step | Time |
| --- | --- |
| Storyboard → first cut (with sound) | ~25 min |
| Contact-sheet review → fixes (title enters earlier, aftermath glow fills the flash-to-title gap, bigger debris) → final cut | ~6 min |
| Model | GLM 5.3 Flash |

What the agent did on its own: storyboard into `timeline-juizo.json`, a single-file scene component reusing `Mask`/`Roll`/`Grain` primitives, procedural sound from the same timeline (13 sounds, D-minor drone that falls a half step at zero, one riser landing exactly on the one impact of the piece), contact-sheet review of every beat, a loudness pass to −14 LUFS, and the Windows-ARM64 render workaround (`--sequence` JPEG + system ffmpeg encode).

## Notes

- One hero moment: the impact at 4.15 s. Everything before builds to it (creeping shake, draining bar, riser); everything after resolves it (flash → aftermath → title slam → hold).
- The afterglow overlay was added in review: the flash-to-title gap read as "loading" on the contact sheet.
