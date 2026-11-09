# Ready recipes (copy, change content/tokens, keep structure)

## 1. AI assistant answers a question (chat)
`UI.browser` or `UI.phone` → `UI.input` at bottom (typing 18 cps, `tType`) → send `UI.button` with `press` → `UI.chat` messages (user t = press time, AI think .9 s, 46 cps) → below the answer, result card (`UI.list` rows rising) → toast "Saved". Camera: wide → punch to the input → follow the answer downward.

## 2. Analytics dashboard
Window + sidebar; 2–3 KPIs (count up) → line chart draw → bar chart spring → donut → highlight an anomaly (badge `bad`, row highlight in `UI.table`). Camera punches on the anomaly.

## 3. Command palette / "search anything"
Backdrop = app (blurred via CSS `filter:blur(6px)` on stage while palette is open) → `UI.palette` types the query → selection moves → Enter → page switch (`UI.pages`).

## 4. Code editor / developer tool
`UI.window kind:'mac'` → `UI.code` (cps 40) in left half; right half `UI.card` "Preview" with `UI.skeleton` until `t1`, then the result list. Terminal strip below via `UI.code` with `$ ` lines.

## 5. Mobile app flow (3 screens)
`UI.phone` + `UI.pages` slide transitions; each screen: header (title 34 px), hero card, list; cursor replaced by tap ripple only (`UI.cursor` with tiny arrow hidden: `fill:'transparent', stroke:'transparent'`, ripple remains).

## 6. Checkout / payment
Form `UI.input`×3 typing in sequence; button press; `UI.progress` 0.8 s; success modal + confetti (motion-canvas-artwork `confetti`) + `success` sound.

## 7. Notification storm → calm
Five `UI.toast` stacked (stagger .25 s) then a single "Focus mode" toggle (`UI.toggle at`) clearing them (set toast `dur`).

## Content checklist
- 6–8 realistic nouns for the domain (customer names, products, cities).
- 3 numbers that tell a story (growth %, total, delta).
- One "hero" element per screen that is 2× larger than others.
- A believable timestamp / unread badge / avatar group.
