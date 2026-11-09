# Prompt: passada de som (efeitos “meio pá” → profissionais)

1. `render.mjs scene.html - --events out/events.json`; confira se há eventos em TODO hit/transição/clique (senão adicione `Lab.ev`).
2. `sync_cues.py out/events.json --out audio/ --dna dna.json --music-gen --profile social`.
3. Leia `audio/sound-report.md`: alinhamento (±1 frame), LUFS (-14 social), pico, equilíbrio espectral, avisos. Corrija o que o relatório apontar (aumentar sub/boom, reduzir densidade, trocar palette).
4. Faça `--variants 3` se o hit principal estiver em dúvida e entregue os 5 timestamps + as variantes para eu escolher de ouvido.
5. Nunca diga que “ouviu”; diga que verificou números/espectrograma.
