#!/usr/bin/env bash
# Áudio final do estilo 03 · VSL (R8): −14 LUFS integrado (±0,3) e pico verdadeiro ≤ −1 dBTP, sem recodificar a imagem.
# Os efeitos do kit têm ataques rápidos; o loudnorm linear não alcança o alvo e um limitador comum deixa o pico passar
# no AAC. Aqui: ganho + limitador em 192 kHz (pega o pico entre amostras), com o ganho calibrado em até 3 passadas.
# Uso (na pasta do motor):  bash ferramentas/audio-final-vsl.sh ../render/_reel-bruto.mp4 ../render/reel-vN.mp4
set -euo pipefail
IN="$1"; OUT="$2"; ALVO="${3:--14}"
med() { ffmpeg -nostats -i "$1" -af "loudnorm=I=${ALVO}:TP=-1:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p'; }
campo() { python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
I0=$(med "$IN" | campo input_i)
G=$(python3 -c "print(round(${ALVO} - (${I0}), 2))")
echo "— bruto: ${I0} LUFS → ganho inicial ${G} dB"
for n in 1 2 3; do
  ffmpeg -v error -y -i "$IN" -c:v copy -af "aresample=192000,volume=${G}dB,alimiter=limit=0.84:attack=1:release=50:level=false,aresample=48000" \
    -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
  J=$(med "$OUT"); I=$(echo "$J" | campo input_i); TP=$(echo "$J" | campo input_tp)
  echo "— passada ${n}: ganho ${G} dB → ${I} LUFS · pico ${TP} dBTP"
  D=$(python3 -c "print(round(${ALVO} - (${I}), 2))")
  python3 -c "import sys; sys.exit(0 if abs(${D}) <= 0.3 else 1)" && break
  G=$(python3 -c "print(round(${G} + ${D}, 2))")
done
python3 -c "import sys; sys.exit(0 if ${TP} <= -0.5 else 1)" || echo "AVISO: pico ${TP} dBTP acima de −0,5 — baixe o limit do alimiter (0,84 → 0,79)"
echo "final: $OUT"
