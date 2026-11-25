# BRIEF — CHUNK {{CID}}  ({{T0}} → {{T1}})

You are one judging agent. You only analyse THIS time range. Other agents analyse the other chunks; a script merges everything.

**Question from the user:** {{QUESTION}}

**Image to open:** `{{SHEET}}` — {{NTILES}} tiles, each labelled `t=mm:ss.s` + id. Red border = first frame of a scene. Grey tile `-00` (CTX) = last frame of the previous chunk, for continuity only (do not report events before {{T0}}). The strip under the grid shows motion (orange), loudness (green), cuts (red lines), tile ticks.

Tiles:
{{TILES}}

{{AUDIO}}

{{LENS}}

## Do this
1. Open the sheet and read EVERY tile in order. Compare each tile with the previous one: what changed (subject, layout, text, colour, camera, UI state)?
2. Record events with the time of the tile that shows them (the true time is between that tile and the previous one — say so in `what` if it matters).
3. Copy visible text EXACTLY (characters as seen). If it is too small to read, mark `legible:false` and add a `needs_zoom` for it.
4. Answer the user's question for this range, citing tile ids.
5. Everything you cannot decide from stills (speed, easing, smoothness, sound, exact counts, small details) goes to `unknowns` or `needs_zoom` — never into `events` as fact.

## Output — write ONLY this JSON to `reports/{{CID}}.json`
```json
{
  "chunk_id": "{{CID}}",
  "summary": "2-3 sentences, only what the tiles show",
  "events": [ {"t": 0.0, "tile": "{{CID}}-01", "kind": "scene|object|action|text|ui|camera|style|transition|other", "what": "...", "confidence": 0.8, "seen": true} ],
  "text_seen": [ {"t": 0.0, "tile": "{{CID}}-01", "text": "exact text", "legible": true} ],
  "answers_question": ["bullet, with tile id"],
  "unknowns": ["..."],
  "needs_zoom": [ {"t0": 0.0, "t1": 0.0, "mode": "burst|crop|pair", "why": "..."} ]
}
```
Rules: `t` must lie inside {{T0S}}–{{T1S}} seconds (numbers). `seen:false` = inference (allowed, but flagged). `confidence` 0..1: use <0.6 whenever a detail needs a closer look. No invented names of people/brands unless printed in the frame. Do not describe sound beyond the numbers above.
