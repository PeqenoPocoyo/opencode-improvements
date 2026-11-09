"""lib_motion.py - shared helpers for the motion-lab hooks (Claude Code hook protocol: JSON on stdin; exit 0 = ok, exit 2 = block with stderr message shown to the model).
All hooks FAIL OPEN: if anything unexpected happens they exit 0, so a bug here can never brick the session."""
import json, os, re, sys

PACK = os.environ.get("MOTION_LAB_HOME") or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PACK, "skills", "qa-critique", "scripts"))

VIDEO_WORDS = re.compile(r"\b(v[ií]deo|motion|anima[cç][aã]o|reels?|tiktok|shorts?|intro|outro|trailer|promo|explainer|storyboard|title card|lower third|kinetic|transi[cç][aã]o|render|mp4|lottie|after effects|capcut|edit(?:ar|ing)? v[ií]deo|screen recording|demo de app|ui no v[ií]deo|anuncio|an[uú]ncio|b-?roll|legenda|caption)\b", re.I)
SOUND_WORDS = re.compile(r"\b(sfx|efeito sonoro|sound effect|som|[aá]udio|trilha|m[uú]sica|whoosh|mix|loudness)\b", re.I)
UI_WORDS = re.compile(r"\b(interface|dashboard|app|aplicativo|saas|website|site|landing|ui|tela|mockup|chat)\b", re.I)

def read_input():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}

def project_root(start=None):
    d = os.path.abspath(start or os.getcwd())
    for _ in range(8):
        if os.path.isdir(os.path.join(d, ".motion")) or os.path.exists(os.path.join(d, "dna.json")): return d
        p = os.path.dirname(d)
        if p == d: break
        d = p
    return os.path.abspath(start or os.getcwd())

def state_path(root): return os.path.join(root, ".motion", "session-state.json")

def load_state(root):
    try: return json.load(open(state_path(root)))
    except Exception: return {}

def save_state(root, st):
    try:
        os.makedirs(os.path.join(root, ".motion"), exist_ok=True); json.dump(st, open(state_path(root), "w"), indent=1)
    except Exception: pass

def is_scene_file(path, content=None):
    if not path or not path.lower().endswith((".html", ".htm")): return False
    base = os.path.basename(path).lower()
    if base in ("index.html",) and content is not None and "seek" not in content and "Lab.init" not in content: return False
    if content is not None: return ("seek" in content) or ("Lab.init" in content) or ("window.VIDEO" in content)
    return "scene" in path.lower() or "/scenes/" in path.replace("\\", "/").lower()

def block(msg):
    sys.stderr.write(msg.strip() + "\n"); sys.exit(2)

def context(msg):
    # SessionStart / UserPromptSubmit: stdout is injected as context for the model
    sys.stdout.write(msg.strip() + "\n"); sys.exit(0)

def safe_main(fn):
    try: fn()
    except SystemExit: raise
    except Exception as e:
        sys.stderr.write(f"[motion hook error, ignored] {e}\n"); sys.exit(0)
