#!/usr/bin/env bash
# Áudio final (regra R8): −14 LUFS integrado (±0,5), pico ≤ −0,5 dBFS, sem recodificar a imagem.
# Uso: ferramentas/audio-final.sh <video de entrada> <video de saída> [alvo LUFS, padrão -14]
# Imprime a medição antes e depois. Usa loudnorm em duas passadas; se o pico ficar alto, limita.
set -euo pipefail
IN="$1"; OUT="$2"; ALVO="${3:--14}"
medir() { ffmpeg -v info -nostats -i "$1" -af "loudnorm=I=${ALVO}:TP=-1:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/{/,/}/p'; }
echo "— antes:"; J=$(medir "$IN"); echo "$J"
I=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['input_i'])")
TP=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['input_tp'])")
LRA=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['input_lra'])")
TH=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['input_thresh'])")
OFF=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['target_offset'])")
ffmpeg -v error -y -i "$IN" \
  -af "loudnorm=I=${ALVO}:TP=-1:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${TH}:offset=${OFF}:linear=true:print_format=summary,alimiter=limit=0.94:attack=3:release=60" \
  -c:v copy -c:a aac -b:a 192k "$OUT"
echo "— depois:"; J2=$(medir "$OUT"); echo "$J2"
# o loudnorm linear pode errar por ~0,5 LU (soma o target_offset); se passou de ±0,3 LU, corrige com ganho simples
I2=$(echo "$J2" | python3 -c "import json,sys;print(json.load(sys.stdin)['input_i'])")
DIFF=$(python3 -c "print(round(${ALVO} - (${I2}), 2))")
if python3 -c "import sys; sys.exit(0 if abs(${DIFF}) > 0.3 else 1)"; then
  echo "— ajuste fino de ${DIFF} dB"
  TMP="${OUT%.mp4}-tmp.mp4"
  ffmpeg -v error -y -i "$OUT" -af "volume=${DIFF}dB,alimiter=limit=0.94:attack=3:release=60" -c:v copy -c:a aac -b:a 192k "$TMP" && mv "$TMP" "$OUT"
  echo "— final:"; medir "$OUT"
fi
