# Question playbooks (pick one; each = lens + extra steps + deliverable)

## 1. "Analyse this reference video" (motion-lab)
Lens `motion`, budget `standard`. After the merge: extract a **recipe**: palette (5 hex guesses from tiles; confirm with a crop), type style, layout grid, background treatment, transition types, beats (cut times from `manifest.cuts` + agent structure), motion character (from bursts at 2–3 transitions: speed px/frame, overshoot yes/no), sound facts (loudness/onset numbers only). Deliver `reference-to-recipe` format (`instructions/prompts/reference-to-recipe.md`) and add a row to `reference-analysis/references.md`.

## 2. Tutorial / screen recording → steps
Lens `tutorial`, `--budget deep` if > 5 min. Deliverable: numbered procedure; each step = action + UI element (exact label) + timestamp. Zoom every `legible:false` text. Check final state vs initial state.

## 3. Ad / social video breakdown
Lens `ad`. Deliverable: hook (0–2 s) · promise · proof · CTA · claims copied exactly · pacing (cuts in first 5 s = from manifest) · format notes.

## 4. QA of a render we made (motion-lab)
Lens `motion`. Compare against the storyboard: for each planned beat, did a tile show it at that time? Use `--pair` around transitions, `--burst` on entrances. Deliver pass/fail list with timestamps. (Complements `qa-critique`, which measures; this looks.)

## 5. Long footage triage ("find the good parts" / "what happened")
Lens `general`/`surveillance`/`sport`, `--budget deep`. Overview → chunks → rank events by confidence × relevance → zoom on top 5 → timeline with timestamps and "no change" stretches listed.

## 6. Interview / lecture
Lens `talk`. If an SRT exists attach it to the synthesis agent. Deliverable: topic map with timestamps, slide texts, framing changes.

## 7. Film scene breakdown
Lens `film`. Shot list: scene, size, movement (needs burst), location, characters (described), cut rhythm (from manifest), grade.

## 8. Compare two videos
Run the pipeline on each (separate out dirs), same question and lens; give the synthesis agent both merged timelines; ask for differences with timestamps on both sides.

## 9. "Is X in the video?" (search)
Quick budget + zoom: overview first; if X is small use `--window` sweeps over candidate ranges with crops; absence = "not seen in sampled tiles (list ranges checked)", never "not in the video".

## Writing the user's question into `--question`
Be literal and include the deliverable: "List every on-screen text with timestamps and say which scenes use a serif typeface." Vague questions give vague reports.
