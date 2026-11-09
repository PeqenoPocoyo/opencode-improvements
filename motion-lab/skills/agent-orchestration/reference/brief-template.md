# Worked example: the common brief used to build THIS pack with sub-agents

This is a real brief that was handed to every worker that built motion-lab. It is reproduced because it works:
it states the product, the complaint it solves, the read order, the required contents of the deliverable,
the non-negotiables, the exact test command, and the report format. Copy its shape for video work: replace
"skill folder" with "scene file", "SKILL.md" with "scene.html + EVENTS", and paths with the project's.

Why each part is there:
- *Context paragraph* gives judgment-call fuel (what the user hates, what good looks like).
- *Read first (ordered)* prevents the worker from inventing its own contract.
- *Required contents* is the definition of done.
- *Non-negotiables* are the rules that silently break things (determinism, test everything, write boundary).
- *Report format* makes verification fast: you compare the report to disk.

---

# Common brief for every sub-agent building a motion-lab skill

You are building ONE part of "motion-lab": a pack of skills/instructions that teaches weaker LLMs (GLM 5.3 Flash, Step 5 Preview…) to make creative, varied, professional motion-graphics videos in code (HTML + canvas/WebGL → MP4). The user's complaint: all generated videos have "the same soul" (same palette, fonts, easing, scenes, same 6 sound samples, sounds start late). The new pack must make output DIVERSE, art-directed and tightly synced.

## Read first (in this order)
1. /home/claude/motion-lab/CONVENTIONS.md  — the contract (seek(t) purity, EVENTS, paths, gates). Obey it.
2. /home/claude/motion-lab/skills/scene-runtime/runtime/lab.js — the core API you build on (do NOT edit it; if you need a change, say so in your report).
3. /home/claude/motion-lab/reference-analysis/references.md — what the 11 reference videos teach. Your skill must encode the relevant techniques as recipes (technique only; never copy brands/logos/characters).
4. For format: /tmp/claude-0/-home-claude/aeb2d003-7678-56b3-9cd4-063df201b4e7/scratchpad/toolkit/skill-pack-motion-graphics/skills/explainer-high-energy/SKILL.md (the old toolkit's SKILL.md format; note its flaws: fixed palette, fixed scene list, banned lists. Do the opposite: teach how to INVENT, give many options and variation knobs).

## What a skill folder must contain
- `SKILL.md` with YAML frontmatter: `name:` (kebab-case, = folder name) and `description:` (ONE paragraph: what it does + "Use when ..." trigger words in English; models pick skills by this text).
- Body written for WEAK models: imperative, numbered steps, decision tables ("if the idea is X → use technique Y"), exact numeric parameters (durations in seconds, easing names from Lab.ease/Lab.curves, spring w/z, counts, px), copy-paste code that WORKS, explicit "Do / Don't", common failure modes and their fix, a "Variation knobs" table (what to change so two videos from this skill never look alike), and a short "Weak-model protocol" (ordered checklist: what to do first, what to verify with stills, when to stop).
- `reference/*.md` for long catalogs (keep SKILL.md under ~400 lines; push detail into reference files, and link them with relative paths).
- `runtime/*.js` browser code (global namespace per CONVENTIONS §8), `scripts/*` when needed, `examples/*.html` demo scenes using the runtime (they are also tests and a quality bar).
- Everything English, very specific, no filler. Be generous with detail: the user explicitly wants maximum depth ("quanto mais detalhes melhor").

## Non-negotiables
- Runtime code must be deterministic and pure in time (CONVENTIONS §1). Register sound-relevant moments in demos with `Lab.ev(...)`.
- TEST EVERYTHING YOU WRITE. Render demo stills with:
  `cd /home/claude/motion-lab && NODE_PATH=$(npm root -g) node skills/scene-runtime/scripts/render.mjs <page.html> <outdir>/sheet.png --stills t1,t2,... --cols 3 --scale 360 --root /home/claude/motion-lab`
  then LOOK at the PNG with the Read tool and fix what is ugly/broken (clipped, flat, unreadable, wrong colors, shader compile errors in the console). Put test outputs under /tmp/claude-0/-home-claude/aeb2d003-7678-56b3-9cd4-063df201b4e7/scratchpad/<your-skill>/ — NOT in the pack. Page console errors print as [page error]/[page exception].
- WebGL in this sandbox is software (SwiftShader): fine for stills; keep demo resolutions modest (e.g. 540×960) and avoid >64 raymarch steps in tests. Node 22, Playwright + Chromium are installed globally (NODE_PATH=$(npm root -g)). npm registry works (npm i three, @fontsource/*); Google Fonts does NOT. Prefer zero-dependency code; if you use three.js, install it into a scratch dir and tell users to `npm i three` (do not copy node_modules into the pack).
- Do not invent facts about libraries; test them.
- Write only inside your assigned folders. Do not modify other skills' files.
- No emojis. No marketing tone. Plain, dense, correct.
- When done, reply with a SHORT report (<= 25 lines): files created (paths), public API (function names + one-line purposes), what you verified (and how), known limitations/caveats, anything the director should wire into other skills. Do not paste file contents.
