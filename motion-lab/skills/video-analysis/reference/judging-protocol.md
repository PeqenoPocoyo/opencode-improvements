# Judging protocol (how to run the "fuzzy" agents)

## Roles
- **Overview agent** (1): sees the whole video on one sheet. Produces structure + chunk_focus. Runs FIRST; its `chunk_focus` can be appended to chunk briefs (`look_for`).
- **Chunk agents** (N ≤ 16 standard, 40 deep): one sheet each. Independent; can run in parallel (≤ 3 at once).
- **Verify agents**: only for zoom requests. One image set each.
- **Synthesis agent** (1): never sees frames, only validated reports.
Separate agents for separate sheets keeps each context small and prevents an early guess from colouring later chunks.

## Prompt to give a sub-agent (copy)
> You are a judging agent for video analysis. Read the brief `analysis/briefs/C03.md` completely. Then open the image it names with the Read tool and examine EVERY tile. Write ONLY the JSON the brief specifies to `analysis/reports/C03.json`. Do not run any other command. Do not read other chunks' reports. Finish by replying with one line: the path you wrote.

(Equivalent for overview/verify/synth.) The brief contains everything else, so the prompt stays tiny and identical for all agents.

## Dispatching waves (see agent-orchestration)
1. Wave 0: overview agent alone.
2. Wave 1..k: chunk agents, ≤ 3 per wave, each gets its brief path only.
3. After each wave: `ls analysis/reports/` — a missing file means the agent did not finish (rate limit/stop): re-run THAT chunk, do not guess it.
4. `va_merge.py` → problems list → fix missing/invalid reports → zoom → verify wave → synthesis.

## No sub-agent tool (Beam / single model)
Loop yourself: for each brief in dispatch order: read brief → open image → write report. Keep each report on disk immediately (context may be cut). Do the overview first. Never summarise from memory of earlier sheets: re-open if needed.

## Report quality gates (the referee enforces some; you enforce the rest)
- every event has a tile id and a time inside the chunk
- text copied character by character
- uncertain → low confidence + needs_zoom (not a confident guess)
- no sound claims beyond measured numbers
- `answers_question` bullets each cite a tile

## When agents disagree (overlap at chunk seams, two reports about the same moment)
Do not average. Run `va_zoom.py --pair t1 t2` or a burst at the moment and send ONE verify brief. The verify finding wins; keep the loser listed as "disputed" in the synthesis.

## Cost guide (images opened)
quick = 1 · standard ≈ 1 + chunks (1–17) + zooms (usually 2–6) · deep ≈ 1 + up to 40 + zooms. Stop early if the user's question is answered: say which chunks you skipped.
