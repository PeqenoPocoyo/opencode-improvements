# Motion personalities

Personality = easing set + spring + stagger + hold times + hit style + cut rate. The same layout feels like a different video under a different personality. Names are Lab.ease names (`Lab.ease.get('outExpo')`) and `Lab.curves.*`.

| personality | ease | curves | spring w / z | stagger s | hold s | cuts/s | hit style | feels | use for |
|---|---|---|---|---|---|---|---|---|---|
| calm-precise | outExpo, inOutSine | glide, settle | 9 / .85 | .07 | .7-1.6 | .5 | glow-pulse | confident, quiet | product, neon-mono, serious explainers |
| snappy-punchy | outQuart, outBack | punch, snap | 16 / .55 | .035 | .25-.7 | 1.1 | scale-punch + shake | energetic | social hooks, sports, posters |
| elastic-pop | outBack, outElastic | settle, punch | 13 / .4 | .05 | .4-1.0 | .8 | overshoot-pop | playful | kids, apps, explainers |
| heavy-cinematic | inOutCubic, outQuint | drop, glide | 6 / 1.0 | .09 | 1.0-2.2 | .35 | slow-slam | weighty | trailers, luxury, clay |
| jittery-handmade | outCubic, steps | snap | 14 / .5 | .045 | .2-.6 | 1.4 | slap + flash, 12 fps stepping | raw | collage, zine, punk |
| fluid-liquid | inOutSine, outCirc | glide, whip | 7 / .9 | .06 | .6-1.5 | .55 | soft ripple | smooth | glass, music, wellness |
| mechanical-steps | inOutQuart, linear | snap, whip | 20 / 1.0 | .03 | .3-.9 | .9 | tick step | precise | terminal, tech, radial |

## Rules that apply to all
1. Every move has a start and a settle; the settle takes 2-4x longer than the attack for organic feel, equal for mechanical.
2. Stagger by 0.03-0.09 s per element, never all at once; reverse order on exit.
3. Hold a state for the `hold` range before the next move; a video with no holds feels frantic.
4. Overshoot only on arrivals (back/elastic), never on exits.
5. Secondary motion (follow-through 4-6 frames, drift 1-2 %) on everything that stops.
6. Never use the same ease for position, scale and opacity: position = main ease, scale = same family but shorter, opacity = linear or sine, 30 % faster.
7. Anticipation before a big move: 3 frames of opposite motion (squash, pull-back).
8. Camera moves use the slowest ease of the set.

## Spring parameters (Lab.spring(t, w, z))
w = angular frequency (rad/s): 6 heavy, 9 calm, 13-16 snappy, 20 mechanical. z = damping ratio: 1 critical (no overshoot), .85 small overshoot, .55 visible, .4 bouncy.

## Hit styles (how a beat looks)
| hitStyle | recipe |
|---|---|
| glow-pulse | `Lab.hit(t,t0,.4)` multiplies glow strength 1 -> 1.8 -> 1 |
| scale-punch+shake | scale 1 -> 1.08 -> 1 over 0.22 s (`Lab.curves.punch`) + `Lab.shake(t,{amp:20,decay:.3})` |
| overshoot-pop | scale 0.6 -> 1.15 -> 1 with outBack(1.9) |
| slow-slam | drop from +120 px with `Lab.curves.drop`, shake amp 10, decay .6 |
| slap+flash | rotate +-6 deg, scale 1.25 -> 1 in 0.28 s, 3-frame white flash |
| soft-ripple | ring expanding 0 -> 1 over 0.6 s, opacity 0.4 -> 0 |
| tick-step | `Lab.steps(n)` snaps values; no easing |

## Beat-grid
`beat = 60/bpm`. cutRate .35-.5/s = a cut every 2-3 s; 1.4/s = nearly every beat at 100 bpm.
