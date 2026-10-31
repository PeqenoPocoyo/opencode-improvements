# Evolução — Motion Video "IA no Aprendizado"

## v1 (motion-ai.mp4)
- 18s, 720×1280, 25fps
- 5 cenas simples: título, problema, custo, verdade, CTA
- Animações básicas: spring, fade, slide, partículas
- Sem áudio
- **Feedback:** fraco — animações sem impacto, sem canvas, sem VFX pesados

## v2 (motion-ai-v2.mp4) — MELHOR
- 18s, 720×1280, 25fps
- 6 cenas com transições loucas (zoom, glitch, rotate, slide)
- VFX simultâneos: blur blobs, 50 partículas, scanlines, vignette, noise, floating canvases, glitch text (RGB split), floating code snippets, glitch bars
- Áudio: SoundHelix-Song-1 (volume 0.3)
- Typewriter effect, spring, stagger
- **Feedback:** ainda fraco vs. original (sem canvas móveis, sem efeitos de perspectiva, sem caminhão de elementos)
- **Custo:** $0.00 (grátis)

## v3 (em render)
- Em andamento — mais elaborado

## Análise do vídeo original (cozy balcony garden)
- Duração: 17.8s, 720×1280, 25fps, h264+aac
- 445 frames analisados (motion frame-a-frame)
- 18 scene cuts (transições a cada 1-2s)
- 10 cenas
- OCR em andamento (tesseract) para extrair texto/legendas
- Estilo: fundo creme/bege, texto animado, VFX diversos simultâneos, canvas móveis, animações de enquadramento, transições loucas

## Observação
Modelo Beam (texto) analisou mídia visual via OpenCV/motion/OCR — desenvolveu algo sólido (especialmente MÍDIA, algo fora do alcance direto como output). Ainda não replica 100% do original, mas evolução registrada.
"