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

## v3 (motion-ai-v3.mp4)
- 18s, 720×1280, 25fps
- 6 cenas com transições (zoom, glitch, rotate, slide, persp)
- VFX: 5 blur blobs, 50 partículas, scanlines, vignette, noise, glitch text (RGB), floating cards, typewriter, spring, stagger
- Áudio: SoundHelix-Song-1
- Custo: $0.00

## v5 (motion-ai-v5.mp4) — MELHOR AINDA
- 24.7s, 720×1280, 30fps (matching o clipe original)
- 9 cenas com cortes no ritmo da música (1.5+1.5+2+3+2.5+2.5+3+3+5.7 = 24.7s)
- Transições: zoom, glitch (RGB split), rotate, slide, persp (rotateY+scale)
- VFX pesados: 6 blur blobs, 60 partículas, scanlines, vignette, noise, glitch text multicanal, floating canvases (código, emojis, scroll-stopping), typewriter, spring, stagger, perspectiva 3D
- Áudio: SoundHelix (placeholder)
- Custo: $0.00

## Análise do vídeo original (clipe animado — NÃO skincare)
- Duração: 24.7s, 720×1280, 30fps, h264+aac
- 741 frames analisados (motion frame-a-frame)
- 51 scene cuts (52 cenas) → cortes a cada ~0.5-1s (frenético)
- 15 onsets de áudio detectados (transições sincronizadas com a música)
- OCR: tesseract capturando pouco texto (fontes artísticas)
- Estilo: scroll-stopping, canvas móveis, VFX simultâneos, perspectiva, animações de enquadramento, transições loucas

## Observação
Modelo Beam (texto) analisou mídia visual via OpenCV/motion/OCR/áudio — desenvolveu algo sólido (especialmente MÍDIA, algo fora do alcance direto como output). Ainda não replica 100% do original (falta visão computacional avançada: detecção de objetos, layout, depth estimation, VFX específicos), mas evolução registrada (v1→v5).
- Duração: 17.8s, 720×1280, 25fps, h264+aac
- 445 frames analisados (motion frame-a-frame)
- 18 scene cuts (transições a cada 1-2s)
- 10 cenas
- OCR em andamento (tesseract) para extrair texto/legendas
- Estilo: fundo creme/bege, texto animado, VFX diversos simultâneos, canvas móveis, animações de enquadramento, transições loucas

## Observação
Modelo Beam (texto) analisou mídia visual via OpenCV/motion/OCR — desenvolveu algo sólido (especialmente MÍDIA, algo fora do alcance direto como output). Ainda não replica 100% do original, mas evolução registrada.
"