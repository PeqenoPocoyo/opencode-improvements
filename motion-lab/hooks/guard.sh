#!/usr/bin/env bash
# guard.sh - manual fallback for harnesses WITHOUT hook support (Beam, OpenCode, plain chat agents). The model runs these commands itself at the named moments.
#   guard.sh start                 -> prints the 12 rules + project state            (run at the beginning of every video job)
#   guard.sh scene scene.html      -> lint (exit 1 = fix before rendering)           (run after every edit of a scene)
#   guard.sh stills scene.html t1,t2,t3 -> renders a contact sheet of stills          (then READ the png)
#   guard.sh qa video.mp4 [w h fps dur] -> qa + contact sheet + frame_diff + fingerprint (run before delivering)
set -e
HOME_DIR="${MOTION_LAB_HOME:-$(cd "$(dirname "$0")/.." && pwd)}"
export NODE_PATH="${NODE_PATH:-$(npm root -g 2>/dev/null)}"
case "$1" in
  start) echo '{}' | python3 "$HOME_DIR/hooks/motion_session_start.py" ;;
  scene) python3 "$HOME_DIR/skills/qa-critique/scripts/lint_scene.py" "$2" ${3:+--dna "$3"} ;;
  stills) node "$HOME_DIR/skills/scene-runtime/scripts/render.mjs" "$2" "${4:-out/stills.png}" --stills "$3" --cols 3 --scale 540 ;;
  qa) V="$2"; S="$HOME_DIR/skills/qa-critique/scripts"
      python3 "$S/qa_video.py" "$V" ${3:+--expect-w $3 --expect-h $4 --expect-fps $5 --expect-dur $6} || true
      python3 "$S/frame_diff.py" "$V" || true
      python3 "$S/contact_sheet.py" "$V" "${V%.*}.sheet.png" --n 24 && echo "NOW READ ${V%.*}.sheet.png and score it with qa-critique/reference/rubric.md"
      python3 "$S/fingerprint.py" "$V" --add || true ;;
  *) sed -n 2,6p "$0" ;;
esac
