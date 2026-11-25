# BRIEF — OVERVIEW (look at the whole video first)

You are one judging agent in a video-analysis pipeline. Scripts already extracted frames; YOU look at them and judge. Do not guess outside the images.

**Question from the user:** {{QUESTION}}

**Facts measured by tools (trust these numbers, they are not opinions):** {{FACTS}}

**Image to open:** `{{SHEET}}`  (contact sheet of the whole video, {{DUR}}; each tile is labelled `t=mm:ss.s` and an id; red border = first frame of a new scene; the strip at the bottom shows motion (orange), loudness (green), cuts (red lines) and tile positions).

Tiles:
{{TILES}}

{{LENS}}

## Do this
1. Open the sheet. Read tile by tile, left→right, top→bottom. Do not skip any tile.
2. Write what the video is (genre guess), how it is structured (scenes/sections with start-end times), and the visual style in concrete words (colours, type, layout, texture, camera).
3. Decide where a second look is needed: for each chunk give one concrete thing to look for (the chunk analysts will receive it).
4. List unknowns honestly. Stills cannot show motion, speed, easing or sound: say so when relevant.

## Output — write ONLY this JSON to `reports/overview.json`
```json
{
  "summary": "3-4 sentences, only what the tiles show",
  "genre_guess": "...", "visual_style": "concrete words",
  "structure": [ {"t0": 0.0, "t1": 6.0, "label": "...", "tiles": ["V01","V02"]} ],
  "chunk_focus": [ {"chunk": "C01", "look_for": "..."} ],
  "unknowns": ["..."]
}
```
Rules: every claim must be traceable to a tile id. If you are unsure write it in `unknowns`, not in `summary`. Times are seconds (numbers).
