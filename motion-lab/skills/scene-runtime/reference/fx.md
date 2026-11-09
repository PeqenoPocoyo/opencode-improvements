# fx.js reference (WebGL2 post-processing)

Global `FX`. Zero dependencies, deterministic (grain/glitch reseed per frame from t). Source = canvas/img/video; output opaque in `fx.canvas`.

```js
const fx = FX.create(1080,1920);
stage.appendChild(fx.canvas);                       // or drawImage(fx.canvas,0,0) into a 2D canvas
function render(t){ drawScene2D(t); fx.apply(sceneCanvas, [ {pass:'bloom',intensity:.9}, {pass:'chromatic',amount:.002+.01*Lab.hit(t,T.slam,.15)}, {pass:'grain',amount:.06}, {pass:'vignette'} ], t); }
```

Rules: (1) draw the scene into ONE canvas, run FX once per frame on that canvas, never per element; (2) passes run in the order given (bloom before grain, grade before halftone); (3) animate any numeric param from t (amount, intensity, start, focus); (4) FX works on display-referred sRGB, thresholds are on encoded values; (5) one FX instance per size; create it once outside render; (6) CPU-less: needs WebGL2 (SwiftShader in the render sandbox is fine at <= 1080x1920, expect 20-60 ms per pass chain).

## Pass catalog (defaults shown)

| pass | defaults | what / when |
|---|---|---|
| chromatic | amount=0.004, angle=0, radial=1 | RGB split. radial=1: grows toward the edges (lens); 0: linear along angle. Animate amount on hits (0.002 idle, 0.012 on a hit). |
| grain | amount=0.08, size=1, lumaW=1, color=0 | Film grain. lumaW=1 weights mid-tones. Reseeds every frame from t. 0.04-0.12 typical. |
| vignette | amount=0.5, size=0.7, soft=0.55, color=#000000 | Darken corners toward color. |
| halftone | size=9, angle=0.5236, mode=0, contrast=1.1, ink=#14161c, paper=#f1eadb, blend=1 | mode 0 round dots, 1 lines, 2 CMYK (angles 15/75/0/45, multiply on paper). blend mixes with the original. |
| duotone | dark=#10123a, light=#f4e9c8, contrast=1 | Map luminance to two colours. |
| tritone | a=#0b0b2b, b=#b3262f, c=#ffe9b0, mid=0.5, contrast=1 | Gradient map with three stops (shadows a, mids b, highlights c). |
| posterize | levels=5, mixAmt=1 | Quantise each channel. |
| grade | lift=0, gamma=1, gain=1, saturation=1, contrast=1, temperature=0, tint=0, exposure=0 | Colour grade. temperature + = warm, tint + = magenta. |
| filmic | exposure=1, shoulder=1 | ACES-style tone curve: rolls off highlights; pair with bloom. |
| scanlines | count=540, strength=0.18, flicker=0.03 | Horizontal lines. count = lines per frame height. |
| crt | curvature=0.07, scan=0.2, mask=0.15, bleed=0.0015, vignette=0.3 | CRT look: barrel, scanlines, RGB mask, horizontal bleed. |
| lens | distortion=0.12, zoom=1 | Barrel (+) or pincushion (-) distortion. |
| dirblur | radius=24, angle=0, samples=16 | Directional (motion) blur along angle. radius in px. Use on whips. |
| radialBlur | amount=0.08, cx=0.5, cy=0.5, samples=20 | Zoom blur from (cx,cy). Whoosh/zoom-through/impact. |
| pixelate | size=10 | Mosaic pixels (px). |
| displace | amount=0.012, scale=3, speed=0.4, seedOffset=0 | Noise displacement (heat haze, liquid). Time-continuous. |
| ripple | cx=0.5, cy=0.5, freq=34, amp=0.012, speed=2.2, decay=2.2, start=0 | Expanding ring wave from a point; animate start = event time. |
| glitch | amount=0.5, blocks=14, rgb=0.012, speed=12 | Block shifts + RGB split; amount 0 = off. Triggered per frame (deterministic). |
| kaleido | segments=6, angle=0, zoom=1, cx=0.5, cy=0.5 | Kaleidoscope mirror. |
| mirror | axis=0, offset=0.5 | axis 0 mirrors x at offset, 1 mirrors y. |
| lightleak | strength=0.45, a=#ff8a3d, b=#ff2d6f, speed=0.15, seedOffset=1 | Warm light leak, screen-blended, drifting with t. |
| dust | density=0.5, size=2, speed=0.05, bright=0.9 | Floating specks, additive. Seeded by cell; moves with t. |
| paperTexture | strength=0.3, scale=2, warm=0.06 | Paper fibre/tooth multiplied over the frame (use under ink, or on the whole frame at low strength). |
| sharpen | amount=0.5 | Unsharp mask. |
| edge | amount=1, color=#ffffff, base=0, threshold=0.05 | Sobel outline drawn over base (0 = pure lines). |
| invert | amount=1 | Invert colours (amount 0..1). |
| colorize | color=#ff3b6b, amount=0.35, mode=0 | Tint: mode 0 multiply-ish, 1 screen, 2 overlay. |
| flash | amount=0, color=#ffffff | Add a flash: animate amount 1 -> 0 over 3-4 frames on a hit. |
| bloom | threshold=0.62, knee=0.25, intensity=0.9, radius=14, tint=#ffffff | Glow on highlights. threshold = luminance where glow starts, radius in px at half res (x1.0..x3). 0.5-1.2 intensity. |
| glow | threshold=0.35, knee=0.4, intensity=1.1, radius=30, tint=#ffffff | Wide soft glow (bloom with low threshold and big radius). |
| blur | radius=6 | Gaussian blur, radius in px. |
| tiltshift | focus=0.5, width=0.12, radius=7 | Blur away from a horizontal focus band (miniature look). focus/width in uv. |

## Chains (FX.chains.*, functions returning pass lists)
neonBloom, halftonePoster, filmWarm, glassDark, riso, vhs, cleanEditorial. Spread and edit: `[...FX.chains.neonBloom({ca:.004}), {pass:'flash',amount:flashAmt}]`.

## Recipes by look
| look | chain |
|---|---|
| neon on black | bloom(thr .55, int 1, r 18) > chromatic(.002) > grain(.05) > vignette(.5) |
| halftone poster | grade(contrast 1.15) > halftone(size 9, dots) > grain(.09) |
| risograph | duotone(dark,light) > grain(.1,size 1.5) > paperTexture(.25) |
| warm film | grade(temperature .5) > lightleak(.3) > grain(.07) > vignette(.4) |
| VHS / glitch | chromatic(linear) > scanlines > glitch(.12) > grain(color) > crt |
| glass dark | bloom(.5, .8, 22) > chromatic(.003) > vignette(.55) > grain(.035) |
| miniature city | tiltshift(focus .5, width .12, r 7) > grade(saturation 1.15) |
| hit feedback | chromatic amount spikes, radialBlur(.06) decays, flash(1 -> 0 over 3 frames) |
| whip transition | dirblur(radius 60..0, angle along the move) on both scenes |

## Performance
bloom/glow = 11 draws, blur/tiltshift = up to 8, others = 1. Keep chains under ~6 passes per frame for long renders. Lower resolution (render at 720x1280, upscale in ffmpeg) if a draft is slow.

## Failure modes
| symptom | fix |
|---|---|
| black frame | shader error in console (`FX shader "x": ...`) or WebGL2 missing |
| flipped image | do not draw fx.canvas upside down; it is already upright |
| banding in gradients | add grain >= .03 |
| bloom washes the frame | raise threshold (.7-.8) or lower intensity |
| text ghosting after blur | use the blur pass (downsampled) not stacked offsets |
| halftone moire | size >= 6 px, angle 30 deg (0.5236) |
