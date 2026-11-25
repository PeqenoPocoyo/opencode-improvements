# Sampling — why these frames

## Budget in images, not seconds
Let B = images the pipeline may open. Chunks = min(max_chunks, ceil(duration / target_s)); tiles per sheet T fixed (16–20; > 24 tiles are unreadable at ≤ 1568 px). So the tile spacing grows with duration: 3 h with 16 chunks × 16 tiles → ~42 s per tile on average. Zoom is the multiplier for detail.

## Equal-information tiles
During `va_prepare` each analysed frame gets novelty n = mean|Δgray| + ½·L1(Δhistogram). Mass m = clip(n, p97) + 0.12·mean(n): cuts cannot dominate, static stretches keep a floor. Cumulative mass M(t) ∈ [0,1].
Tiles inside a chunk: forced (first frame of each scene, chunk end), then candidates at quantiles of M blended 80 % + 20 % uniform time, picked greedily by max-min distance (no near duplicates). Chunk boundaries: 50 % equal time + 50 % equal mass, snapped to a cut within 15 % of the chunk length.

## Analysis resolution
64×36 gray+RGB-histogram per frame at min(8 fps, 4000/duration). That is enough for cuts, motion level, brightness; it is NOT used for judging. Judging always uses the full-quality extracted tiles.

## Cut detection
cut at frame i if hist_dist[i] > max(0.22, median + 9·MAD) and pixel diff > 0.06 and it is a local maximum, with ≥ 0.6 s between cuts. Tuned on hard cuts; dissolves are handled by novelty, not cuts.

## Audio numbers
8 kHz mono RMS per 0.5 s in dBFS; silence = < −50 dBFS for ≥ 1 s; onset = jump > 8 dB between consecutive windows (top 12). Nothing speech-specific: if a transcript exists (SRT from the user or whisper outside this skill), give it to the synthesis agent as extra data.

## Timestamp semantics
A tile labelled t shows the frame decoded at `-ss t` (nearest following frame). An event "between tile k−1 and k" has uncertainty = gap. For gap < 0.5 s the label is exact enough; otherwise burst.
