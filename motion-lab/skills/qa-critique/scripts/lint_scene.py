#!/usr/bin/env python3
"""lint_scene.py - static lint of a scene HTML for the seek(t) purity contract, sameness traps and missing hooks.

  python3 lint_scene.py scene.html [--json] [--dna dna.json]      exit 0 = clean/warnings only, 1 = errors
Importable: from lint_scene import lint_text; issues = lint_text(src, path='scene.html')   -> list of dict(level,code,msg,line)
Levels: ERROR (breaks determinism/render), WARN (quality), INFO.
"""
import json, re, sys, os

RULES = [  # (level, code, regex, message)
    ("ERROR", "RANDOM", r"Math\.random\s*\(", "Math.random() breaks determinism. Use Lab.rng(seed) or Lab.noise."),
    ("ERROR", "CLOCK", r"\b(Date\.now|new Date|performance\.now)\s*\(", "Wall-clock time breaks determinism. Everything must be a function of t."),
    ("ERROR", "RAF", r"\brequestAnimationFrame\s*\(", "requestAnimationFrame: the renderer drives time via seek(t); never self-animate."),
    ("ERROR", "TIMER", r"\b(setTimeout|setInterval)\s*\(", "Timers are not frame-accurate. Compute state from t."),
    ("ERROR", "CSSANIM", r"@keyframes|animation\s*:|animation-name\s*:", "CSS animations ignore seek(t). Drive style from t in render()."),
    ("ERROR", "CSSTRANS", r"transition\s*:\s*(?!none)[a-z]", "CSS transitions smear frames. Remove; compute from t."),
    ("ERROR", "GFONTS", r"fonts\.googleapis\.com|fonts\.gstatic\.com", "Google Fonts are blocked in the render sandbox. Use kinetic-typography/fonts."),
    ("ERROR", "EXTERNAL", r"(?:src|href)\s*=\s*[\"']https?://(?!localhost)", "External URL: the sandbox has no network. Vendor it locally."),
    ("WARN", "AUTOPLAY", r"\.play\s*\(\s*\)", "media.play(): video/audio elements are not seekable by the renderer. Pre-render or use canvas."),
    ("WARN", "SCROLL", r"scrollTo|scroll-behavior\s*:\s*smooth", "Smooth scroll is time-based; compute scroll offset from t."),
    ("WARN", "FETCH", r"\bfetch\s*\(|XMLHttpRequest", "Network/async loading: make assets local and set window.__ready after load."),
    ("WARN", "WILLCHANGE", r"will-change", "will-change rarely helps in headless capture; remove."),
]
OLD_PALETTES = ["#4f46e5", "#6366f1", "#7c3aed", "#8b5cf6", "#0f172a", "#1e1b4b", "#06b6d4", "#22d3ee", "#f43f5e", "#0b1020", "#00e5ff", "#ff2d95"]  # the usual "AI blue/purple" defaults

def lint_text(src, path="scene.html", dna=None):
    out = []
    lines = src.split("\n")
    def add(level, code, msg, line=0): out.append(dict(level=level, code=code, msg=msg, line=line, file=path))
    # strip comments for pattern checks (cheap)
    body = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), src, flags=re.S)
    body = re.sub(r"(^|[^:])//[^\n]*", r"\1", body)
    bl = body.split("\n")
    for level, code, rx, msg in RULES:
        for i, l in enumerate(bl, 1):
            if re.search(rx, l): add(level, code, msg, i); break
    # contract
    if not re.search(r"window\.VIDEO\s*=|Lab\.init\s*\(", src): add("ERROR", "NO_VIDEO", "Missing window.VIDEO={w,h,duration,fps} (or Lab.init).")
    if not re.search(r"window\.seek\s*=|Lab\.init\s*\(|function seek\s*\(", src): add("ERROR", "NO_SEEK", "Missing window.seek(t) (or Lab.init with render).")
    if not re.search(r"Lab\.ev\s*\(|Lab\.evBeats\s*\(|Collage\.register\s*\(|Rig\.steps\s*\(|window\.EVENTS|EVENTS\s*=", src): add("WARN", "NO_EVENTS", "No events declared: sound sync will be blind. Add Lab.ev(t,'impact'|'whoosh'|…) for every hit/transition.")
    if re.search(r"document\.fonts", src) is None and re.search(r"font-family", src) and not re.search(r"fonts\.css|@font-face", src): add("WARN", "FONTS", "Fonts used but none embedded (fonts.css / @font-face). Text will fall back to a generic font.")
    if re.search(r"Lab\.init", src) is None and "__ready" not in src: add("WARN", "NO_READY", "window.__ready not set; renderer may capture before fonts/assets load.")
    # sameness traps
    low = src.lower()
    hits = [p for p in OLD_PALETTES if p in low]
    if len(hits) >= 3: add("WARN", "DEFAULT_PALETTE", f"Uses {len(hits)} stock 'AI-default' colours ({', '.join(hits[:4])}). Take the palette from dna.json instead.")
    if re.search(r"linear-gradient\([^)]*(#4f46e5|#7c3aed|#6366f1)", low) and "dna" not in low: add("WARN", "PURPLE_GRADIENT", "Purple/indigo gradient background is the #1 'same soul' signature. Use a DNA colour story.")
    ease = re.findall(r"['\"](inOutCubic|outCubic|inOutQuad|easeInOut)['\"]", src)
    if len(ease) >= 8 and len(set(ease)) <= 2: add("WARN", "ONE_EASE", f"{len(ease)} uses of the same easing: motion will feel generic. Use Lab.curves (snap/punch/whip/glide/settle) per intent.")
    if len(re.findall(r"Lab\.stagger|stagger", src)) == 0 and len(re.findall(r"opacity", src)) > 6: add("INFO", "NO_STAGGER", "Many reveals but no stagger: everything enters at once.")
    if re.search(r"font-size\s*:\s*(?:[0-9]|1[0-5])px", src): add("WARN", "TINY_TEXT", "Text below 16px will be unreadable on phones.")
    if len(re.findall(r"filter\s*:\s*blur\(", src)) > 12: add("WARN", "BLUR_COST", "Many CSS blur() elements: slow rendering and muddy look.")
    if len(src) > 400_000: add("WARN", "HUGE", "File > 400 KB: embed fewer assets / generate procedurally.")
    if dna:
        pal = [str(v).lower() for v in (dna.get("palette") or {}).values() if isinstance(v, str)] if isinstance(dna.get("palette"), dict) else [str(v).lower() for v in (dna.get("palette") or [])]
        used = sum(1 for c in pal if c in low)
        if pal and used == 0: add("WARN", "DNA_UNUSED", "None of the dna.json palette colours appear in the scene: the DNA is being ignored.")
    return out

def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--json", action="store_true"); ap.add_argument("--dna")
    a = ap.parse_args(); src = open(a.file, encoding="utf-8", errors="replace").read()
    dna = json.load(open(a.dna)) if a.dna and os.path.exists(a.dna) else None
    res = lint_text(src, a.file, dna)
    if a.json: print(json.dumps(res, indent=1))
    else:
        for r in res: print(f"{r['level']:5} {r['code']:16} line {r['line']:<5} {r['msg']}")
        print(f"\n{sum(r['level']=='ERROR' for r in res)} error(s), {sum(r['level']=='WARN' for r in res)} warning(s)")
    sys.exit(1 if any(r["level"] == "ERROR" for r in res) else 0)

if __name__ == "__main__": main()
