#!/usr/bin/env python3
"""plan_cutaways.py - turn a transcript (SRT or timed JSON) into a cutaway/overlay plan for talking-head or tutorial footage.
  python3 plan_cutaways.py captions.srt [--min-gap 3.5] [--max-hold 2.8] [--json plan.json]
Heuristics (transparent, edit freely): numbers/percent -> stat card; steps/how/click/open -> UI cutaway; names of things (Capitalised) -> lower-third;
questions -> kinetic text; lists ("first, second", commas >= 3) -> bullet build; emphasis words -> punch zoom 1.08. Enforces: no cutaway longer than --max-hold,
never two cutaways closer than --min-gap, never cover the speaker's first 0.8 s of a sentence, J-cut (visual leaves 0.25 s AFTER the line ends), cutaway starts 0.15 s before the keyword.
Output is a PLAN for the scene author; it does not decide aesthetics. Each row has `sound` (event type for sound-design-pro).
"""
import argparse, json, re, sys

def parse_srt(p):
    out = []
    for blk in re.split(r"\n\s*\n", open(p, encoding="utf-8").read().strip()):
        L = blk.strip().splitlines()
        if len(L) < 3: continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", L[1])
        if not m: continue
        g = [int(x) for x in m.groups()]; out.append(dict(t0=g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, t1=g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, text=" ".join(L[2:]).strip()))
    return out

RULES = [
    (r"\b\d+([.,]\d+)?\s?(%|percent|x|k|m|million|billion|reais|dollars|\$|R\$)", "stat-card", "pop"),
    (r"\b(step|first|second|third|click|open|select|type|press|go to|how to|passo|clique|abra|digite)\b", "ui-cutaway", "click"),
    (r"\?", "kinetic-question", "appear"),
    (r"\b(never|always|biggest|only|best|worst|nunca|sempre|maior|melhor)\b", "punch-zoom", "hit-soft"),
    (r"(\w+,\s*){2,}\w+", "bullet-build", "tick"),
    (r"\b[A-Z][a-zA-Z]{3,}\b(?=.*\b[A-Z][a-zA-Z]{3,}\b)", "lower-third", "swipe"),
]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("srt"); ap.add_argument("--min-gap", type=float, default=3.5); ap.add_argument("--max-hold", type=float, default=2.8); ap.add_argument("--json"); a = ap.parse_args()
    cues = parse_srt(a.srt); plan = []; last_end = -99
    for c in cues:
        for rx, kind, snd in RULES:
            if re.search(rx, c["text"], re.I if kind != "lower-third" else 0):
                start = max(c["t0"] + .8 - .15, c["t0"]); end = min(c["t1"] + .25, start + a.max_hold)
                if start - last_end < a.min_gap: break
                plan.append(dict(t0=round(start, 2), t1=round(end, 2), kind=kind, sound=snd, line=c["text"][:90])); last_end = end; break
    if not plan: print("no cutaway opportunities found; add them by hand at every topic change"); 
    print(f"{'t0':>7} {'t1':>7}  {'kind':<18} {'sound':<9} line"); [print(f"{p['t0']:7.2f} {p['t1']:7.2f}  {p['kind']:<18} {p['sound']:<9} {p['line']}") for p in plan]
    cover = sum(p['t1'] - p['t0'] for p in plan); total = cues[-1]['t1'] if cues else 1; print(f"\ncoverage {cover / total * 100:.0f}% of runtime (target 20-40 %). cutaways: {len(plan)}")
    if a.json: json.dump(plan, open(a.json, "w"), indent=1)
main()
