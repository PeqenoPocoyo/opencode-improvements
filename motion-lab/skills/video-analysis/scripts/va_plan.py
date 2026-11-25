#!/usr/bin/env python3
"""va_plan.py - STEP 2. Turn the manifest into a fixed IMAGE budget (not a time budget): chunks, tile timestamps, and ready-to-send briefs for the judging agents.
  python3 va_plan.py analysis/ --question "what makes the motion feel premium?" [--lens general|motion|tutorial|ad|talk|sport|surveillance|film] [--budget quick|standard|deep] [--chunks N] [--tiles T] [--overview-tiles N]
Budget presets (images per agent sheet / max chunks / target seconds per chunk):  quick 16/0/-   standard 16/16/30   deep 20/40/12.
A 10 s clip and a 3 h film both give <= max chunks sheets: long videos get coarser tiles; the zoom step (va_zoom.py) is how agents go deeper.
Tile selection = equal "visual information" (cumulative novelty) mixed 30 % with equal time, plus forced picks: first frame of each scene, last frame of the chunk.
Writes plan.json, briefs/overview.md, briefs/chunk-XX.md, reports/ (empty, agents write there).
"""
import argparse, json, os, sys, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from va_lib import fmt_t

PRESETS = dict(quick=dict(tiles=16, max_chunks=0, target=1e9), standard=dict(tiles=16, max_chunks=16, target=30.0), deep=dict(tiles=20, max_chunks=40, target=12.0))
TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")

def cum(mass, af):
    c = np.concatenate([[0], np.cumsum(mass)]); return c / c[-1]

def t_at_quantile(c, af, q):
    i = int(np.searchsorted(c, q)); return min(i / af, len(c) / af)

def pick_tiles(t0, t1, n, scenes, c, af, min_gap_frac=.4, prefix=""):
    """returns list of (t, kind). equal-information quantiles + forced scene starts + end."""
    n = max(1, n); span = max(1e-3, t1 - t0); chosen = []
    inside = [s for s in scenes if t0 - 1e-6 <= s["t0"] < t1 - .3]
    force = [(min(t1 - .05, s["t0"] + .15), "scene_start") for s in inside]
    if len(force) > n // 2:   # too many scenes: keep the longest ones
        force = sorted(sorted(inside, key=lambda s: -(s["t1"] - s["t0"]))[: n // 2], key=lambda s: s["t0"]); force = [(min(t1 - .05, s["t0"] + .15), "scene_start") for s in force]
    if not force or force[0][0] > t0 + .3: force = [(t0 + .05, "scene_start" if not force else "fill")] + force
    chosen += force; chosen.append((max(t0, t1 - .08), "end"))
    q0 = c[min(len(c) - 1, int(t0 * af))]; q1 = c[min(len(c) - 1, int(t1 * af))]; need = n - len(chosen); gap = span / n * min_gap_frac
    if need > 0:
        cand = []
        for k in range(need * 3):  # oversample candidates, then greedily keep those far from chosen
            u = (k + .5) / (need * 3); tm = t_at_quantile(c, af, q0 + (q1 - q0) * u); tu = t0 + span * u; cand.append(.8 * tm + .2 * tu)
        pool = sorted(set(round(x, 2) for x in cand))
        for _ in range(need):
            best, bd = None, -1
            for x in pool:
                d = min(abs(x - y[0]) for y in chosen)
                if d > bd: best, bd = x, d
            if best is None or bd < gap * .35: break
            chosen.append((best, "fill")); pool.remove(best)
    chosen = sorted(chosen, key=lambda x: x[0])
    # drop near-duplicates, prefer forced kinds
    out = []
    for t, k in chosen:
        if out and t - out[-1][0] < gap * .4:
            if k in ("scene_start", "end") and out[-1][1] == "fill": out[-1] = (t, k)
            continue
        out.append((round(t, 2), k))
    return out[:n + 2]

def snap_boundaries(bounds, cuts, span):
    out = []
    for b in bounds:
        if cuts:
            nearest = min(cuts, key=lambda c: abs(c - b))
            if abs(nearest - b) < span * .15: b = nearest
        out.append(b)
    return out

def render_tpl(name, **kw):
    s = open(os.path.join(TPL, name), encoding="utf-8").read()
    for k, v in kw.items(): s = s.replace("{{" + k + "}}", str(v))
    return s

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("analysis"); ap.add_argument("--question", default="Describe what happens in this video, scene by scene, and what stands out."); ap.add_argument("--lens", default="general"); ap.add_argument("--budget", default="standard", choices=list(PRESETS))
    ap.add_argument("--chunks", type=int); ap.add_argument("--tiles", type=int); ap.add_argument("--overview-tiles", type=int, default=24); a = ap.parse_args()
    man = json.load(open(os.path.join(a.analysis, "manifest.json"))); tl = np.load(os.path.join(a.analysis, "timeline.npz")); af = man["analysis"]["analysis_fps"]; dur = man["video"]["duration"]; P = PRESETS[a.budget]
    tiles_per = a.tiles or P["tiles"]; c = cum(tl["mass"], af); scenes = man["scenes"]; cuts = man["cuts"]
    nch = a.chunks if a.chunks is not None else (0 if P["max_chunks"] == 0 else int(min(P["max_chunks"], max(1, math.ceil(dur / P["target"])))))
    # chunk boundaries: 50 % equal time + 50 % equal information, snapped to scene cuts when close
    bounds = [0.0]
    for k in range(1, nch):
        u = k / nch; bt = .5 * (u * dur) + .5 * t_at_quantile(c, af, u); bounds.append(bt)
    bounds.append(dur); span = dur / max(1, nch); bounds = [bounds[0]] + snap_boundaries(bounds[1:-1], cuts, span) + [bounds[-1]]
    bounds = sorted(set(round(b, 2) for b in bounds)); chunks = []
    for k in range(len(bounds) - 1):
        t0, t1 = bounds[k], bounds[k + 1]
        if t1 - t0 < .2: continue
        tl_ = pick_tiles(t0, t1, min(tiles_per, max(4, math.ceil((t1 - t0) * 8))), scenes, c, af); cid = f"C{len(chunks) + 1:02d}"
        tiles = [dict(id=f"{cid}-{i + 1:02d}", t=t, kind=kd) for i, (t, kd) in enumerate(tl_)]
        if chunks:  # context tile: last frame of previous chunk (so events at the seam are not lost)
            prev = chunks[-1]["tiles"][-1]; tiles.insert(0, dict(id=f"{cid}-00", t=prev["t"], kind="ctx"))
        chunks.append(dict(id=cid, t0=t0, t1=t1, scenes=[s["i"] for s in scenes if s["t1"] > t0 and s["t0"] < t1], tiles=tiles, sheet=f"sheets/{cid}.jpg", brief=f"briefs/{cid}.md"))
    ov = pick_tiles(0, dur, min(a.overview_tiles, max(4, math.ceil(dur * 8))), scenes, c, af); overview = dict(tiles=[dict(id=f"V{i + 1:02d}", t=t, kind=kd) for i, (t, kd) in enumerate(ov)], sheet="sheets/overview.jpg", brief="briefs/overview.md")
    plan = dict(version=1, video=man["video"], question=a.question, lens=a.lens, budget=a.budget, tiles_per_sheet=tiles_per, overview=overview, chunks=chunks)
    for d in ("briefs", "reports", "sheets"): os.makedirs(os.path.join(a.analysis, d), exist_ok=True)
    json.dump(plan, open(os.path.join(a.analysis, "plan.json"), "w"), indent=1)
    lens_txt = open(os.path.join(TPL, "lens", a.lens + ".md"), encoding="utf-8").read() if os.path.exists(os.path.join(TPL, "lens", a.lens + ".md")) else open(os.path.join(TPL, "lens", "general.md"), encoding="utf-8").read()
    facts = f"{fmt_t(dur)} total, {man['video']['width']}x{man['video']['height']}, {len(scenes)} scenes (cuts at {', '.join(fmt_t(x) for x in cuts[:12])}{'…' if len(cuts) > 12 else ''}), mean motion {man['stats']['mean_motion']}, audio: {'yes' if man['audio'] else 'none'}"
    open(os.path.join(a.analysis, "briefs", "overview.md"), "w", encoding="utf-8").write(render_tpl("brief_overview.md", QUESTION=a.question, LENS=lens_txt, FACTS=facts, SHEET=overview["sheet"], TILES="\n".join(f"- {t['id']}  t={fmt_t(t['t'])}  {t['kind']}" for t in overview["tiles"]), DUR=fmt_t(dur)))
    for ch in chunks:
        aud = ""
        if man["audio"]:
            sil = [s for s in man["audio"]["silences"] if s[1] > ch["t0"] and s[0] < ch["t1"]]; pk = [p for p in man["audio"]["peak_onsets"] if ch["t0"] <= p <= ch["t1"]]
            aud = f"Audio numbers (measured, you cannot hear): silences {sil or 'none'}; loud onsets at {[fmt_t(p) for p in pk] or 'none'}."
        open(os.path.join(a.analysis, ch["brief"]), "w", encoding="utf-8").write(render_tpl("brief_chunk.md", QUESTION=a.question, LENS=lens_txt, CID=ch["id"], T0=fmt_t(ch["t0"]), T1=fmt_t(ch["t1"]), T0S=ch["t0"], T1S=ch["t1"], SHEET=ch["sheet"], AUDIO=aud,
                                                                         TILES="\n".join(f"- {t['id']}  t={fmt_t(t['t'])}  {t['kind']}" for t in ch["tiles"]), NTILES=len(ch["tiles"])))
    imgs = 1 + len(chunks); print(f"plan: {len(chunks)} chunks x {tiles_per} tiles + overview {len(overview['tiles'])} tiles = {imgs} sheets for a {fmt_t(dur)} video -> {a.analysis}/plan.json, briefs/")
main()
