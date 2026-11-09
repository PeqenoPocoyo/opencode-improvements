# Animation principles → what to type

| Principle | In rig.js / your scene |
|---|---|
| Squash & stretch | `blob` hop: sy = 1 + 0.22·sin(air) in flight, 1 − 0.28 on landing crouch, sx = 1/sy (volume kept). Never scale one axis only. |
| Anticipation | jump: crouch 18 % of `dur`; before a wave raise the hand 0.15 s; before a whip-turn move eyes first. |
| Staging | One action per beat. Others hold (idle). Silhouette must read: arms away from torso when acting. |
| Follow-through / overlap | antenna lags 0.9 rad behind hover (`bot`); hat/hair: add `Lab.spring` on a copy of the head y and offset by (spring − head). |
| Slow in/out | all arrivals `easeOutCubic`/`smooth`; never linear except machines. |
| Arcs | hand/foot paths are sines (arcs); never straight-line tween a limb. |
| Secondary action | blink, breathing (`idle` hip y ±1.6 px), LED blinking, shadow scale. |
| Timing | See table. Faster = lighter / smaller / more nervous. |
| Exaggeration | Scale 1.2× the amplitude you think is right for 1080-wide frames; phone screens are small. |
| Solid drawing | consistent light (top-left highlight on blob), outline width constant (4–5 px in character space). |
| Appeal | big head, big eyes, simple silhouette. `Rig.face` size = 1.15 × head radius. |

## Timing table (30 fps)
| Action | Duration | Notes |
|---|---|---|
| Blink | 0.16 s, every 3.2 s ± 40 % | `Rig.blink` |
| Hop (blob) | period 0.9–1.4 s | air 60 %, landing 40 % |
| Jump (biped) | 0.7–1.0 s | crouch 18 %, air 67 %, land 15 % |
| Wave | 2.2 cycles/s | 3–4 cycles then stop |
| Walk | 1 cycle/s (2 steps) at scale 1 | run 2–2.4 cycles/s |
| Head turn | 0.2–0.3 s | eyes first |
| Surprise "take" | 0.12 s in, hold 0.5 s | mood `surprised`, mouth .5 |
| Syllable | 7/s | `Rig.talk` rate |

## Walk maths (so feet don't skate)
Foot x = sin(φ)·stride; when the foot is planted its ground speed = hip speed. Each half-cycle a planted foot travels 2·stride (80 px at stride 40), so one full cycle moves the body 4·stride = 160 px·scale; at `speed 1` that is 160 px/s·scale. For 1080 px crossing in 4 s you need ≈ 270 px/s → `speed 1.7` (still an integer cycles count over the shot: choose duration so speed·duration is an integer).

## Acting beats (30–60 s explainer guide)
1 enter (walk, 2 s) → 2 look at the thing (eyes, 0.3 s) → 3 surprise take (0.6 s) → 4 explain (point + talk 3 s) → 5 reaction (happy bounce 0.8 s) → 6 exit or hold idle. Put a `Lab.ev` at 3 (`pop`), at 5 (`success` small) and footsteps in 1.

## Common mistakes
- Character hovering because y is the centre not the ground (y is the GROUND).
- Mirrored text on a flipped (`face:-1`) character: draw text outside the Rig call.
- Hands always at the same height: use `action:'dance'` or `point` instead of faking.
- Talking without eyes moving: add `look` drift `[sin(t*.5)*.4, 0]`.
