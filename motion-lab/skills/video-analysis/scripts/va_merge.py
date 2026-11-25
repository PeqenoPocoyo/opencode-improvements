#!/usr/bin/env python3
"""va_merge.py - STEP 5. Deterministic referee for the judging agents' JSON reports. It never judges the video; it checks FORM and EVIDENCE.
  python3 va_merge.py analysis/ [--min-conf 0.6] [--gap 20]
Reads plan.json + reports/*.json. Checks: schema, times inside chunk, tile ids exist, confidence range, text copied (legible flag), coverage (missing chunk reports, long silent stretches
with no event), duplicates at chunk seams (merged). Writes:
  merged_timeline.md      chronological events of all chunks (+ text seen), flags marked
  followups.json          zoom_requests (agents' needs_zoom + low-confidence/inferred events) and problems (schema errors, missing reports) -> run va_zoom.py --followups
  briefs/verify-XX.md     one verify brief per zoom request (after va_zoom.py has produced images) , briefs/synth.md  the final synthesis brief
Exit code 0 always; read `problems` in the output. Re-run after every new batch of reports.
"""
import argparse, difflib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from va_lib import fmt_t
TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
KINDS = {"scene", "object", "action", "text", "ui", "camera", "style", "transition", "other", "cut", "audio"}

def load(p):
    try: return json.load(open(p, encoding="utf-8")), None
    except Exception as e:
        try:  # tolerate agents that wrap JSON in prose / code fences
            t = open(p, encoding="utf-8").read(); i, j = t.find("{"), t.rfind("}"); return json.loads(t[i:j + 1]), f"JSON had extra text around it (repaired): {os.path.basename(p)}"
        except Exception: return None, f"{os.path.basename(p)}: not valid JSON ({e})"

def num(x):
    try: return float(x)
    except Exception: return None

def tpl(name, **kw):
    s = open(os.path.join(TPL, name), encoding="utf-8").read()
    for k, v in kw.items(): s = s.replace("{{" + k + "}}", str(v))
    return s

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("analysis"); ap.add_argument("--min-conf", type=float, default=.6); ap.add_argument("--gap", type=float, default=20.0); a = ap.parse_args()
    plan = json.load(open(os.path.join(a.analysis, "plan.json"))); R = os.path.join(a.analysis, "reports"); problems, events, texts, zoom = [], [], [], []; tile_ids = {}
    for ch in plan["chunks"]: tile_ids[ch["id"]] = {t["id"] for t in ch["tiles"]}
    ov, err = load(os.path.join(R, "overview.json")) if os.path.exists(os.path.join(R, "overview.json")) else (None, None)
    if err: problems.append(dict(level="warn", where="overview", msg=err))
    if not ov: problems.append(dict(level="error", where="overview", msg="reports/overview.json missing or invalid: run the overview agent first"))
    covered = set()
    for ch in plan["chunks"]:
        p = os.path.join(R, ch["id"] + ".json")
        if not os.path.exists(p): problems.append(dict(level="error", where=ch["id"], msg=f"report missing ({fmt_t(ch['t0'])}-{fmt_t(ch['t1'])}): send briefs/{ch['id']}.md to an agent")); continue
        rep, err = load(p)
        if err: problems.append(dict(level="warn", where=ch["id"], msg=err))
        if rep is None: continue
        covered.add(ch["id"])
        if rep.get("chunk_id") != ch["id"]: problems.append(dict(level="warn", where=ch["id"], msg=f"chunk_id says {rep.get('chunk_id')!r}"))
        for k in ("summary", "events", "unknowns"):
            if k not in rep: problems.append(dict(level="warn", where=ch["id"], msg=f"field '{k}' missing"))
        for i, e in enumerate(rep.get("events") or []):
            t = num(e.get("t")); where = f"{ch['id']} event {i + 1}"
            if t is None: problems.append(dict(level="error", where=where, msg="t is not a number")); continue
            if not (ch["t0"] - 1.0 <= t <= ch["t1"] + 1.0): problems.append(dict(level="error", where=where, msg=f"t={t} outside chunk {ch['t0']}-{ch['t1']}")); continue
            if e.get("tile") not in tile_ids[ch["id"]]: problems.append(dict(level="warn", where=where, msg=f"tile {e.get('tile')!r} not in this chunk (no evidence reference)"))
            c = num(e.get("confidence")); c = .5 if c is None or not (0 <= c <= 1) else c
            if e.get("kind") not in KINDS: problems.append(dict(level="info", where=where, msg=f"unknown kind {e.get('kind')!r}"))
            ev = dict(t=t, chunk=ch["id"], tile=e.get("tile"), kind=e.get("kind", "other"), what=str(e.get("what", "")).strip(), conf=c, seen=bool(e.get("seen", True))); events.append(ev)
        for tx in rep.get("text_seen") or []:
            t = num(tx.get("t"))
            if t is None: continue
            texts.append(dict(t=t, chunk=ch["id"], tile=tx.get("tile"), text=str(tx.get("text", "")), legible=bool(tx.get("legible", True))))
            if not tx.get("legible", True): zoom.append(dict(t0=max(0, t - .3), t1=t + .3, mode="crop", why=f"text not legible at tile {tx.get('tile')}: transcribe", src=ch["id"]))
        for z in rep.get("needs_zoom") or []:
            t0, t1 = num(z.get("t0")), num(z.get("t1"))
            if t0 is None or t1 is None: problems.append(dict(level="warn", where=ch["id"], msg="needs_zoom without numeric t0/t1")); continue
            zoom.append(dict(t0=t0, t1=max(t1, t0 + .05), mode=z.get("mode", "burst") if z.get("mode") in ("burst", "crop", "pair") else "burst", why=str(z.get("why", "")), src=ch["id"], crop=z.get("crop")))
    # dedupe at seams
    events.sort(key=lambda e: e["t"]); out = []
    for e in events:
        dup = next((o for o in reversed(out[-6:]) if abs(o["t"] - e["t"]) <= 1.0 and o["chunk"] != e["chunk"] and difflib.SequenceMatcher(None, o["what"].lower(), e["what"].lower()).ratio() >= .6), None)
        if dup:
            if e["conf"] > dup["conf"]: dup.update(e)
            continue
        out.append(e)
    events = out
    # weak evidence -> zoom requests
    for e in events:
        if e["conf"] < a.min_conf or not e["seen"]:
            zoom.append(dict(t0=max(0, e["t"] - .6), t1=e["t"] + .6, mode="burst" if e["kind"] in ("action", "camera", "transition", "style") else "crop", why=f"{'inferred' if not e['seen'] else 'low confidence ' + str(e['conf'])}: {e['what'][:90]}", src=e["chunk"]))
    # long gaps without any event inside covered chunks
    for ch in plan["chunks"]:
        if ch["id"] not in covered: continue
        ts = sorted([ch["t0"]] + [e["t"] for e in events if e["chunk"] == ch["id"]] + [ch["t1"]])
        for x, y in zip(ts, ts[1:]):
            if y - x > a.gap: problems.append(dict(level="info", where=ch["id"], msg=f"no event between {fmt_t(x)} and {fmt_t(y)} ({y - x:.0f}s): real stillness, or missed? (check tiles in that range)"))
    # unique zoom ids
    old = {}
    try:
        for z in json.load(open(os.path.join(a.analysis, 'followups.json'))).get('zoom_requests', []):
            if z.get('images'): old[(round(z['t0'], 1), round(z['t1'], 1), z['mode'])] = z['images']
    except Exception: pass
    seen = set(); zr = []
    for z in zoom:
        k = (round(z["t0"], 1), round(z["t1"], 1), z["mode"])
        if k in seen: continue
        seen.add(k); z["id"] = f"Z{len(zr) + 1:02d}"
        if k in old and all(os.path.exists(i) for i in old[k]): z["images"] = old[k]
        zr.append(z)
    fu = dict(problems=problems, zoom_requests=zr[:60], coverage=dict(chunks=len(plan["chunks"]), reported=len(covered), overview=bool(ov)))
    json.dump(fu, open(os.path.join(a.analysis, "followups.json"), "w"), indent=1)
    L = [f"# Merged timeline — {plan['question']}", "", f"Video {fmt_t(plan['video']['duration'])} · chunks reported {len(covered)}/{len(plan['chunks'])} · events {len(events)}", ""]
    if ov: L += ["## Overview (agent)", ov.get("summary", ""), "", "Structure: " + "; ".join(f"{fmt_t(s.get('t0', 0))}-{fmt_t(s.get('t1', 0))} {s.get('label', '')}" for s in ov.get("structure", [])), ""]
    L += ["## Events", "", "| t | kind | what | tile | conf | |", "|---|---|---|---|---|---|"]
    for e in events: L.append(f"| {fmt_t(e['t'])} | {e['kind']} | {e['what'].replace('|', '/')} | {e['tile']} | {e['conf']:.2f} | {'⚠ inferred' if not e['seen'] else ('? weak' if e['conf'] < a.min_conf else '')} |")
    if texts: L += ["", "## Text seen on screen", ""] + [f"- {fmt_t(x['t'])} `{x['text']}`{'' if x['legible'] else ' (illegible → zoom)'} [{x['tile']}]" for x in sorted(texts, key=lambda x: x['t'])]
    answers = []
    for ch in plan["chunks"]:
        rep = load(os.path.join(R, ch["id"] + ".json"))[0] if ch["id"] in covered else None
        if rep: answers += [f"- ({ch['id']}) {x}" for x in rep.get("answers_question") or []]
    if answers: L += ["", "## Chunk answers to the question", ""] + answers
    unk = []
    for ch in plan["chunks"]:
        rep = load(os.path.join(R, ch["id"] + ".json"))[0] if ch["id"] in covered else None
        if rep: unk += [f"- ({ch['id']}) {x}" for x in rep.get("unknowns") or []]
    if unk: L += ["", "## Unknowns declared by agents", ""] + unk
    open(os.path.join(a.analysis, "merged_timeline.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    # verify briefs for zoom requests that already have images; synth brief always
    nv = 0
    for z in fu["zoom_requests"]:
        if z.get("images"):
            nv += 1; open(os.path.join(a.analysis, "briefs", f"verify-{z['id']}.md"), "w", encoding="utf-8").write(tpl("brief_verify.md", FID=z["id"], QUESTION=plan["question"], T0=fmt_t(z["t0"]), T1=fmt_t(z["t1"]), T0S=z["t0"], T1S=z["t1"], WHY=z["why"], MODE=z["mode"], IMAGES=", ".join(z["images"])))
    open(os.path.join(a.analysis, "briefs", "synth.md"), "w", encoding="utf-8").write(tpl("brief_synth.md", QUESTION=plan["question"], TIMELINE="merged_timeline.md", FOLLOWUPS="followups.json"))
    err = sum(p["level"] == "error" for p in problems); warn = sum(p["level"] == "warn" for p in problems)
    print(f"reports {len(covered)}/{len(plan['chunks'])} chunks, overview {'ok' if ov else 'MISSING'} · events {len(events)} · problems: {err} error, {warn} warn · zoom requests {len(fu['zoom_requests'])} (verify briefs ready: {nv})")
    for p in problems[:25]: print(f"  [{p['level']}] {p['where']}: {p['msg']}")
    if fu["zoom_requests"] and not any(z.get("images") for z in fu["zoom_requests"]): print("  next: python3 va_zoom.py <video> --followups analysis/followups.json --out-dir analysis/zoom ; re-run va_merge.py ; send briefs/verify-*.md")
main()
