#!/usr/bin/env bash
# setup.sh <project-dir>  - create a motion-lab project: folders, lab/ runtimes, fonts, three.js, starter scene, ledger.
# Works from anywhere; finds the pack relative to this file. No network needed (fonts and three.js are vendored).
set -euo pipefail
PROJ="${1:?usage: setup.sh <project-dir>}"
PACK="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
mkdir -p "$PROJ"/{lab,assets,scenes,audio,out/stills,.motion}
# 1. every runtime/*.js of every skill -> lab/
for f in "$PACK"/skills/*/runtime/*.js "$PACK"/skills/*/runtime/*.mjs; do [ -f "$f" ] && cp "$f" "$PROJ/lab/"; done
# 2. vendored three.js (ES module) next to the runtimes
if [ -d "$PACK/skills/generative-3d-backgrounds/runtime/vendor" ]; then cp -r "$PACK/skills/generative-3d-backgrounds/runtime/vendor" "$PROJ/lab/"; fi
# 3. fonts (OFL woff2 + fonts.css + fonts.json)
if [ -d "$PACK/skills/kinetic-typography/fonts" ]; then rm -rf "$PROJ/lab/fonts"; cp -r "$PACK/skills/kinetic-typography/fonts" "$PROJ/lab/fonts"; fi
# 4. starter scene (paths rewritten to lab/)
if [ ! -f "$PROJ/scene.html" ]; then sed -e 's#\.\./runtime/lab\.js#lab/lab.js#' "$PACK/skills/scene-runtime/templates/scene.html" > "$PROJ/scene.html"; fi
# 5. ledger + docs pointers
[ -f "$PROJ/.motion/style-history.json" ] || echo '{"version":1,"entries":[]}' > "$PROJ/.motion/style-history.json"
echo "$PACK" > "$PROJ/.motion/pack-path.txt"
cat > "$PROJ/README-motion.md" <<EOF
# Motion project
Pack: $PACK
Pipeline: skills/motion-director/SKILL.md (brief -> concepts -> DNA -> storyboard -> build -> stills -> QA -> sound -> human check)
Render:   node $PACK/skills/scene-runtime/scripts/render.mjs scene.html out/stills/sheet.png --stills 0.5,1.5,3 --cols 3 --scale 360 --root .
Remember: export NODE_PATH=\$(npm root -g)
EOF
echo "project ready: $PROJ"
echo "  runtimes in lab/: $(ls "$PROJ/lab" | grep -c '\.js$') js files; fonts: $(ls "$PROJ/lab/fonts" 2>/dev/null | grep -c woff2) woff2"
echo "  next: write brief.md, then dna.json (style-dna), then storyboard.md"
