# Textures (texture block of the DNA)

Every video has at least one VISIBLE texture. Flat vector = template look. Values are 0-1 strengths used by the scene or FX.

| key | what | cheap implementation | FX.js pass |
|---|---|---|---|
| grain | film/sensor noise | 6 seeded 256 px noise tiles, overlay blend at `grain` opacity, offset per frame (template scene.html) | `grain` |
| vignette | dark corners | radial gradient to rgba(0,0,0,vignette) | `vignette` |
| halftone | dot screen | canvas dot grid sized by luminance, or FX pass | `halftone` (dots/lines/cmyk) |
| paper | fibre + crumple + tooth | `Collage.paper(w,h,seed,opts)` pre-rendered | `paperTexture` |
| scan | scanlines + flicker | 2 px lines every 4 px at alpha .08-.2, 60 Hz flicker | `scanlines`, `crt` |
| bloom | glow on highlights | canvas `shadowBlur` on bright shapes or FX | `bloom` |
| dust | drifting particles in a light cone | 80-200 seeded points, slow curl-noise drift, additive | `dust` |
| chromatic | RGB split on edges and hits | 3 offset draws or FX | `chromatic` |
| lightleak | warm gradient sweep | additive gradient moving with noise | `lightleak` |

## Budget
Grain 0.03-0.12 | vignette 0.1-0.55 | bloom 0.1-0.9 | scan 0.1-0.6. If two textures fight (halftone + scan) choose one as primary (>= .5) and the other secondary (<= .2).

## Where to apply
Apply texture on TOP of the whole frame (post), not per element, so everything shares one surface. Exception: paper layers in collage have their own paper under the ink.

## Heavy-filter rule
CONVENTIONS §1.8: no big CSS blur/drop-shadow on moving elements. Pre-bake glows to a canvas, or use FX.js.
