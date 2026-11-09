# storyboard.md template

```
# Storyboard — <video name>          bpm <n>  beat <s>  fps <n>  size <w>x<h>  DNA <name>

| # | start | end | beat (what the viewer sees) | camera | transition IN | events (type @ t, dur) | owner |
|---|-------|-----|-----------------------------|--------|---------------|-------------------------|-------|
| 1 | 0.00 | 3.00 | HOOK: giant "12" counts to 18, half hidden by a silhouette | slow push 1.00->1.06 | none (frame 0) | riser @0.0 dur 1.5 ; slam @1.6 ; tick x6 @1.7.. | scene-01 |
| 2 | 3.00 | 6.00 | ... | handheld jitter | whip pan 10 f | whoosh @2.9 dur .3 ; pop x3 | scene-02 |

## Seams (entry/exit states)
| seam | out-state of N (last frame) | in-state of N+1 (first frame) | transition | overlap |
|------|------------------------------|--------------------------------|------------|---------|
| 1->2 | numeral centered, scale 1.06 | same numeral centered scale 1.0 on new bg | match-cut carry | 0 |

## Loop? yes/no — end frame equals frame 0 because: ...
## Text inventory (every string on screen, in the user's language): ...
## Asset inventory: fonts, svg, textures to generate: ...
## Risks / cheats: ...
```

## Checks before building
- Times are multiples of beat/4.
- Sum of slots = duration.
- No two consecutive seams use the same transition.
- Every row has >= 1 event.
- Every row changes >= 2 of {background tone, object, type treatment, camera}.
- Hook frame described concretely (shapes, sizes, positions).
- Text inventory reading time fits each slot (chars/15 s).
