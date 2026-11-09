# Usage limits, context limits and recovery

Real incident while building this pack: two waves of 4 and 7 parallel agents both died with HTTP 429 ("5-hour limit"), leaving almost no files. Lessons:

## Prevention
1. Wave width 2–3. Never 7.
2. Write the spine yourself; delegate only heavy, well-bounded jobs.
3. Keep briefs file-based: point at a brief file on disk (`_build/briefs/NN.md`) so a retry re-uses it unchanged.
4. Have each worker write incremental files (runtime first, then docs, then examples), not one giant final write. A dead worker then leaves usable partial work.
5. Checkpoint after each wave: update `ORCHESTRATION.md` with done / partial / not started.

## Detection
- A worker result that is an error string (429, overloaded, timeout) means **zero trust**: inspect the disk.
- `python3 scripts/manifest.py diff <project>` shows what appeared; compare against the brief's file list.

## Recovery procedure
1. Stop launching. Read the error: a reset time means wait or do the work yourself.
2. List partial files; judge each: runs? renders? complete?
3. Rewrite the brief to say: "A previous attempt left partial files at <paths>. Inspect, verify, and CONTINUE; do not redo." (already included in motion-lab briefs).
4. Relaunch with a narrower wave (1–2 workers) or do the smallest pieces yourself.
5. If limits persist, switch to mode C (sequential personas) for the remaining roles and tell the user plainly which parts are not done.

## Context-limit recovery (the orchestrator's own context fills up)
- Keep `ORCHESTRATION.md` current: decisions, file paths, what each worker was told, what is verified.
- After any compaction, the first action is to re-read `ORCHESTRATION.md`, `storyboard.md`, `dna.json`, then `manifest.py diff`.
- Never keep large file contents only in conversation; they must exist on disk.

## Degrade gracefully
Full parallel waves → small waves → single worker at a time → sequential personas → one-scene-at-a-time with stills. Each step trades speed for reliability. Choose the lowest step that still finishes.

## What to tell the user
Say it plainly: "Parallel generation hit the account's usage limit twice; I wrote X, Y myself and verified Z. Parts not finished: …". No hiding.
