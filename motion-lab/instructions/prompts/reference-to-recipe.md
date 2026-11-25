# Prompt: transformar um vídeo/print de referência em RECEITA (sem copiar)

Referência: [arquivo/frames]. Rode `skills/video-analysis` (`va_run.py <ref> --lens motion --question "receita visual e de movimento"`; leia cada sheet, `va_merge.py`, `va_zoom.py --burst` nas 2–3 transições para medir velocidade/overshoot) e escreva a receita em 8 linhas:
1. Paleta (5 hex, com papel de cada uma) · 2. Tipografia (caráter, peso, caixa, tracking; qual fonte do pack chega mais perto) · 3. Grade/layout · 4. Personalidade de movimento (curvas por nome, velocidade, overshoot, stagger) · 5. Câmera · 6. Textura/acabamento (grão, halftone, vidro, papel…) · 7. Transições (quais do catálogo e por quê) · 8. Sentimento do som (palette).
Depois: **mude DUAS dessas linhas de propósito** (ex.: paleta e transições) e construa o vídeo novo. Registre no DNA (`dna.json`) com o nome “inspired-by-<ref>”. Rode `fingerprint.py` contra o vídeo da referência se tiver o mp4: a distância deve ser > 0.25.
