---
name: ui-in-video
description: Builds realistic APP / WEBSITE / DASHBOARD interfaces inside videos - windows, browsers, phones, sidebars, KPIs, charts, chat with streaming AI replies, command palettes, toasts, modals, code editors, tables, a human-like cursor with click ripples and a product-film camera (zoom/pan/tilt). Includes the pro structure of a product film, realism rules, and timing. Use whenever a video must show software ("UI no vídeo", interface de app, SaaS demo, app promo, feature announcement, explainer with a screen, mockup animado).
---

# ui-in-video — a product film is a story told with a cursor and a camera

Runtime: `runtime/ui-kit.js` (global `UI`, needs lab.js). DOM+SVG, deterministic: every component is `{el, at(t)}` and `scene.at(t)` is called once per frame inside `render(t)`.

## Workflow
1. **Write the story in 5 beats** (below) before any code. One screen = one idea.
2. **Pick tokens:** `UI.theme('dark'|'light'|'paper'|'glass', {accent, accent2,…})` — map from `dna.json` palette; fonts via CSS vars `--ui-font/--ui-mono` (embed fonts first).
3. **Build the world** (one `stage` div the size of the video). Put the app in a `UI.window/browser/phone`; pages inside with `UI.pages`.
4. **Fill with believable content** (rules below), then script: component entrances (`t0`), cursor keys, camera keys.
5. **Add events** for every click/toast/whoosh: `Lab.ev(t,'click')` etc. (sound-design-pro).
6. **Render stills** at the end of each beat and read them (text legible at phone size? cursor visible? nothing clipped?).

## The 5-beat product film (≈ 8–15 s per feature)
1. **Context (0–1.5 s):** app shell appears (window pop + sidebar slide + KPIs count up). Wide shot.
2. **Focus (1.5–3.5 s):** camera punches in to ONE element (KPI, input). Everything else dims or stays still.
3. **Action (3.5–7 s):** cursor travels (arc, 0.6–0.9 s), clicks (press + ripple + sound), the UI reacts within 100 ms (toggle, tab slide, palette, chat typing).
4. **Result (7–9 s):** the payoff animates (chart draws, AI streams its answer, success toast). Camera eases to frame it.
5. **Out (last 0.7 s):** pull back or cut on a match; leave the result readable for ≥ 1 s.

## Realism rules (this is what makes it look "real")
- **Real copy**, never "Lorem ipsum" or "Item 1": plausible names, amounts with thousands separators, relative dates ("2 min ago"), units. Numbers should not be round (128,450 not 100,000).
- **Hierarchy:** one accent colour for actions, muted greys for secondary text, consistent radii (token), 8-px spacing grid. Max 3 font sizes per screen + one big KPI.
- **State changes cause motion** (selection highlights, tab indicators slide, toggles spring) — never a hard swap of a whole panel except through `UI.pages`.
- **Cursor:** arc path (`arc:.12`), accelerates/decelerates (glide), pauses 0.15 s before a click, click = scale .86 + ripple. Cursor arrives *before* the UI reacts, never after. Hide it when not needed.
- **Typing:** 14–22 cps for inputs, 40–55 cps for AI streaming; AI "thinks" 0.6–1.2 s (dots) before streaming.
- **Camera:** zoom 1.3–1.7× on the active area; hand-held drift ±3 px (`Lab.handheld`); punch ease on pushes (`punch`), `glide` on drifts; never zoom while the cursor is mid-click.
- **Legibility on phone:** body text ≥ 20 px at 1080 wide, KPI ≥ 56 px; zoom in rather than shrinking text.
- **Depth:** shadow token + 1 px border; glass theme needs a colourful background behind it.

## Tilt / 3D presentation
Wrap the stage in a perspective: `UI.camera(stage,{persp:1800, keys:[{t,rx:.35,ry:-.4,zoom:.9,…}]})` for floating-screen shots; or use `transitions-projections` (`matrix3dFromQuad`) for a flat window onto a quad. Add a reflection/shadow plane in 2D under it.

## Components (see `reference/component-catalog.md`)
window, browser, phone, card, button(press), input(typing), chat(streaming), list, table, sidebar, tabs, toggle, kpi, barChart, lineChart, donut, progress, skeleton, badge, avatars, toast, modal, palette, code, notifications, pages, cursor, camera, icon(36).

## Anti-patterns
Static screenshot look (no state change); everything entering at once; cursor teleporting; text too small; random gradient "dashboards" with no meaning; same dark-blue SaaS theme every time (use the DNA!); all components same radius/spacing but different from the DNA; long idle holds without camera/typing motion.

## Files
`runtime/ui-kit.js` · `reference/{component-catalog,film-patterns,app-recipes}.md` · `examples/ui-dashboard-film.html` (10 s: dashboard build → KPI zoom → palette → chat → toast)
