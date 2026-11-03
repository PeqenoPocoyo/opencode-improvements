#!/usr/bin/env bash
# preparar.sh — prepara a composição do estilo 03 · VSL dentro da pasta do motor (<P>/motor, a cópia deste modelo/).
# Rode em <P>/motor:   bash preparar.sh
# Avulso (fora do estúdio):   bash preparar.sh --video clean.mp4 [--palavras cortepalavras.json|palavras.json|transcript.json] [--audio corte.wav]
#
# Lê do projeto do estúdio (a pasta-mãe, P):
#   câmera   P/corte/clean-916-grade.mp4 (9:16 já com grading, se houver) → senão clean-916.mp4 → senão corte/clean.mp4
#   voz      P/corte/corte.wav (senão o áudio da própria câmera)
#   palavras P/preparo/palavras.json (corrigido, R6) → senão P/corte/cortepalavras.json
#   fontes   P/assets/fonts/ (fontes.css da pele) · material real P/assets/oficiais/ e P/assets/gerados/ → assets/img/
# Escreve aqui (na pasta do motor):
#   assets/clean.mp4        1080×1920, 30 fps, keyframe a cada 1 s (-g 30), com a voz (horizontal → recorte do centro)
#   assets/transcript.json  {"words":[{"text","start","end"}],"audio_duration_secs"} (+ transcript-whisper.json, a cópia original)
#   assets/face-track.json  rastreio da boca (ferramentas/rastrear-boca.py: MediaPipe; sem ele, OpenCV)
#   node_modules/           npm install (hyperframes 0.7.109, gsap 3.14.2, playwright) — ou VSL_NODE_MODULES=<pasta pronta>
#   vsl.json, src/beats.js, src/index.template.html, index.html (primeira montagem)
# Variáveis (R10): VSL_PYTHON (Python com mediapipe/opencv; padrão python3), FACE_MODEL, VSL_NODE_MODULES, CHROME.
set -euo pipefail
M="$(cd "$(dirname "$0")" && pwd)"; cd "$M"; P="$(cd .. && pwd)"
VIDEO=""; PALAVRAS=""; AUDIO=""
while [[ $# -gt 0 ]]; do case "$1" in
  --video) VIDEO="$2"; shift 2;; --palavras) PALAVRAS="$2"; shift 2;; --audio) AUDIO="$2"; shift 2;;
  *) echo "opção desconhecida: $1"; exit 1;; esac; done
mkdir -p assets/img src snapshots
PY="${VSL_PYTHON:-python3}"

# --- entradas ---
if [[ -z "$VIDEO" ]]; then
  for f in "$P/corte/clean-916-grade.mp4" "$P/corte/clean-916.mp4" "$P/corte/clean.mp4"; do [[ -f "$f" ]] && { VIDEO="$f"; break; }; done
fi
[[ -z "$AUDIO" && -f "$P/corte/corte.wav" ]] && AUDIO="$P/corte/corte.wav"
if [[ -z "$PALAVRAS" ]]; then
  for f in "$P/preparo/palavras.json" "$P/corte/cortepalavras.json"; do [[ -f "$f" ]] && { PALAVRAS="$f"; break; }; done
fi
[[ -f "${VIDEO:-}" ]] || { echo "câmera não encontrada (corte/clean-916-grade.mp4 ou --video)"; exit 1; }
echo "câmera: $VIDEO"; echo "voz: ${AUDIO:-(da própria câmera)}"; echo "palavras: ${PALAVRAS:-(nenhuma — transcreva antes)}"

# --- câmera 9:16 com a voz, keyframe a cada 1 s (sem isso o render congela quadros) ---
read -r W H < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$VIDEO" | tr ',' ' ')
VF="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
[[ "$W" == 1080 && "$H" == 1920 ]] && VF="null"
if [[ -n "$AUDIO" ]]; then
  ffmpeg -v error -y -i "$VIDEO" -i "$AUDIO" -map 0:v:0 -map 1:a:0 -vf "$VF" -r 30 -c:v libx264 -crf 16 -preset medium -g 30 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart assets/clean.mp4
else
  ffmpeg -v error -y -i "$VIDEO" -map 0:v:0 -map '0:a:0?' -vf "$VF" -r 30 -c:v libx264 -crf 16 -preset medium -g 30 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -movflags +faststart assets/clean.mp4
fi
echo "assets/clean.mp4 pronto (${W}×${H} → 1080×1920)"

# --- transcript no formato do kit ---
if [[ -n "$PALAVRAS" ]]; then
  python3 - "$PALAVRAS" assets/clean.mp4 assets <<'PY'
import json, subprocess, sys, os
src, video, out = sys.argv[1:4]
d = json.load(open(src, encoding="utf-8"))
if isinstance(d, dict) and "words" in d: W = [{"text": w["text"], "start": w["start"], "end": w["end"]} for w in d["words"]]
elif d and isinstance(d[0], list): W = [{"text": t, "start": a, "end": b} for a, b, t in d]          # cortepalavras.json
else: W = [{"text": w["t"], "start": w["i"], "end": w["f"]} for w in d]                            # preparo/palavras.json
W = [w for w in W if str(w["text"]).strip()]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout)
t = {"words": [{"text": str(w["text"]).strip(), "start": round(float(w["start"]), 3), "end": round(float(w["end"]), 3)} for w in W], "audio_duration_secs": round(dur, 3)}
if not os.path.exists(os.path.join(out, "transcript-whisper.json")): json.dump(t, open(os.path.join(out, "transcript-whisper.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(t, open(os.path.join(out, "transcript.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(f"assets/transcript.json: {len(t['words'])} palavras, {dur:.2f} s — confira nomes e a palavra-código do CTA (R6)")
PY
fi

# --- fontes da pele e material real do projeto ---
if [[ -d "$P/assets/fonts" ]]; then cp -R "$P/assets/fonts/." assets/fonts/ 2>/dev/null || true; fi
for d in "$P/assets/oficiais" "$P/assets/gerados"; do if [[ -d "$d" ]]; then cp -R "$d/." assets/img/ 2>/dev/null || true; fi; done

# --- dependências (versões da referência) ---
if [[ ! -e node_modules ]]; then
  if [[ -n "${VSL_NODE_MODULES:-}" && -d "$VSL_NODE_MODULES" ]]; then ln -s "$VSL_NODE_MODULES" node_modules; echo "node_modules: $VSL_NODE_MODULES"
  else npm install --no-audit --no-fund --silent && echo "npm ok (hyperframes 0.7.109 · gsap 3.14.2)"; fi
fi

# --- rastreio da boca (a legenda que segue a boca depende dele) ---
"$PY" ferramentas/rastrear-boca.py assets/clean.mp4 assets/face-track.json || echo "AVISO: rastreio da boca falhou — sem ele não há legenda (defina VSL_PYTHON com mediapipe ou opencv)"

# --- primeira montagem ---
node montar.mjs
cat <<EOF

Motor pronto em: $M
Fase 1: confira assets/transcript.json (R6) · meça face/head/punch num quadro → vsl.json · material → assets/img + ../assets/SOURCES.md
        · assets/map.md → src/beats.js (régua: exemplo/beats-exemplo.js) · ../entrega/planta.json → node ferramentas/cards.mjs
Fase 2: ver README.md (render, só-câmera, áudio, sons.json, folha, zona segura, VERIFY).
EOF
