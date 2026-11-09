# Product-film patterns (what the pros do)

## Camera grammar
| Move | Use | Numbers |
|---|---|---|
| **Establishing wide** | first 1–1.5 s | zoom 1.0, slight handheld drift |
| **Punch-in** | focus one element | 1.35–1.7×, 0.9–1.4 s, ease `punch`; centre the element at 40% height (not 50%) for portrait |
| **Pan-follow** | follow the cursor's destination | start moving 0.2 s *before* the cursor arrives |
| **Pull-back reveal** | show the result in context | 1.4× → 1.05×, 1.2 s, `glide` |
| **Tilt float** | hero shot of the whole screen | `persp:1800`, rx .25–.4, ry ±.35, zoom .85–.95, 2–3 s slow drift |
| **Whip to next screen** | between features | 8–12 frames + `whoosh`; next screen already moving |

## Pacing table (per feature)
Intro 1.2 s · action 3–5 s · result 2 s · hold 0.8 s. A 30 s video holds 3 features max. Never keep one camera setting for more than ~3 s.

## Layout recipes (1080×1920)
- **Hero window:** x 60, y 260, w 960, h 1180 (leaves headline room above and caption below).
- **Phone:** w 560 h 1160 centred, tilted ry −.25; surrounding floating cards (KPI, toast) at different z/scale.
- **Split story:** top 45% big headline (kinetic-typography), bottom 55% UI window cropped by the frame edge (suggests more).
- **Landscape 1920×1080:** window 1500×860 centred; sidebar 300.

## Reveal vocabulary
Window `pop` (spring) · sidebar `slide-r` stagger 60 ms · cards `rise` stagger 100–150 ms · KPIs count up 1.2 s `outExpo` · charts draw 1.6 s `glide` · toast spring from top · modal scale .9→1 + scrim.

## Sound for UI (hand to sound-design-pro)
click/tick on each click; `pop` on window/modal; `whoosh` on camera punches; soft `appear` on card entrances (quantised, max 1 per 120 ms); `success` on result; typing: faint `key` at 12–16 per second (or none — silence is fine under music).

## Mistakes to avoid
- Zooming into blurry low-res text: authored size ≥ 20 px at 1080; camera zoom doesn't re-rasterise in screenshots, so check stills.
- UI animating while camera moves fast (motion soup). Alternate: camera moves, then UI acts.
- Cursor hidden behind overlays: cursor lives in the topmost layer.
- Same screen twice with only colours changed.
