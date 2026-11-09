# Why a layer looks fake → fix (ordered by how often it is the cause)

| # | Tell | Physical cause | Fix in this pack |
|---|---|---|---|
| 1 | Shadow direction/softness differs | Different light | `light_direction.py` → `paste` values for shadow blur/offset/alpha |
| 2 | Layer too clean | No sensor noise, no compression | `grain_measure.py` → `FX grain` at suggested amount/size; render overlay at 1× then add grain at output res |
| 3 | Colours too saturated / contrasty | Footage has lifted blacks, limited gamut | `grade_match.py --strength .6–.8` |
| 4 | Edges razor sharp | Optics soften | blur 0.5–1.2 px or `FX.apply(...{pass:'blur'})` |
| 5 | Floats while the camera moves | No tracking | `track_points.py` quad → matrix3d, or share handheld sway |
| 6 | No contact | Real objects touch with contact shadow | add a 6–10 px dark ambient-occlusion band under edges (very soft, alpha .25) |
| 7 | Wrong perspective | Flat layer on angled surface | pin with 4 corners (quad) not a rect |
| 8 | Motion blur mismatch | Footage has 180° shutter blur on fast moves | render overlay with `--sub 8` for fast moves |
| 9 | Lens artefacts missing | Footage has vignette/chromatic aberration/bloom | FX `vignette`, tiny `chroma`, `bloom` at .1 |
| 10 | Wrong depth of field | Object at same focus plane as subject | blur layers that sit in front/behind the focal plane by 1–3 px |

## Colour pipeline in two sentences
Measure the footage in Lab (mean/std, 1st/99th percentile of L). Move the overlay's statistics toward them by 60–80 % — full transfer destroys brand colours, none looks pasted.

## Rule of thumb for amounts
grain 0.03 (clean 4K), 0.08 (phone daylight), 0.15–0.25 (phone night). Compression reduces measured noise, so trust the measured number over the guess.

## What cannot be done here (be honest with the user)
Rotoscoping/keying, 3D camera solve, object removal, face retouch, relighting. Offer: layout around the subject, picture-in-picture, split screens, graphics beside the person.
