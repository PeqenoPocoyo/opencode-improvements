#!/usr/bin/env python3
"""manifest.py - snapshot a project folder and diff it after a wave of workers.

  python3 manifest.py snapshot <project>                    # before the wave
  python3 manifest.py diff <project> [--owners owners.json] # after the wave
  python3 manifest.py owners-template <project>             # write an owners.json skeleton

owners.json: {"worker-name": ["scenes/02-*.html", "scenes/02-*.assets/**"], ...}
In diff mode with --owners, files changed that match NO owner pattern are listed as UNOWNED writes,
and files matching more than one owner as CONFLICTS. Exit code 1 if either exists.
Snapshot is stored in <project>/.motion/manifest.json (ignored dirs: node_modules, .git, out/stills).
"""
import sys, os, json, hashlib, fnmatch, argparse

IGN = ('node_modules', '.git', '__pycache__')

def walk(root):
    res = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in IGN and not os.path.relpath(os.path.join(dp, d), root).replace('\\', '/').startswith(('out/stills', '.motion'))]
        for f in fn:
            p = os.path.join(dp, f); rel = os.path.relpath(p, root).replace('\\', '/')
            try:
                st = os.stat(p); h = hashlib.sha1(open(p, 'rb').read()).hexdigest()[:12]
            except OSError:
                continue
            res[rel] = {'size': st.st_size, 'sha': h}
    return res

def matches(rel, pats):
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel, p.replace('**', '*')) for p in pats)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['snapshot', 'diff', 'owners-template'])
    ap.add_argument('project')
    ap.add_argument('--owners')
    a = ap.parse_args()
    root = a.project; mdir = os.path.join(root, '.motion'); mp = os.path.join(mdir, 'manifest.json')
    if a.cmd == 'owners-template':
        os.makedirs(mdir, exist_ok=True)
        json.dump({'director': ['brief.md', 'dna.json', 'storyboard.md', 'ORCHESTRATION.md', 'stitch.html'],
                   'scene-01': ['scenes/01-*'], 'scene-02': ['scenes/02-*'], 'assets': ['assets/**'],
                   'sound': ['audio/**'], 'qa': ['out/qa/**']}, open(os.path.join(mdir, 'owners.json'), 'w'), indent=2)
        print('wrote', os.path.join(mdir, 'owners.json')); return 0
    cur = walk(root)
    if a.cmd == 'snapshot':
        os.makedirs(mdir, exist_ok=True); json.dump(cur, open(mp, 'w'), indent=1)
        print(f'snapshot: {len(cur)} files'); return 0
    if not os.path.exists(mp):
        print('no snapshot; run snapshot first'); return 2
    old = json.load(open(mp))
    added = sorted(k for k in cur if k not in old)
    removed = sorted(k for k in old if k not in cur)
    changed = sorted(k for k in cur if k in old and cur[k]['sha'] != old[k]['sha'])
    print('ADDED   ', *(f'\n  + {k} ({cur[k]["size"]} B{"  EMPTY!" if cur[k]["size"] == 0 else ""})' for k in added))
    print('CHANGED ', *(f'\n  ~ {k}' for k in changed))
    print('REMOVED ', *(f'\n  - {k}' for k in removed))
    bad = 0
    own = a.owners or (os.path.join(mdir, 'owners.json') if os.path.exists(os.path.join(mdir, 'owners.json')) else None)
    if own:
        owners = json.load(open(own))
        for k in added + changed:
            who = [w for w, p in owners.items() if matches(k, p)]
            if not who: print(f'UNOWNED WRITE: {k}'); bad = 1
            elif len(who) > 1: print(f'CONFLICT: {k} claimed by {who}'); bad = 1
    return bad

if __name__ == '__main__':
    sys.exit(main())
