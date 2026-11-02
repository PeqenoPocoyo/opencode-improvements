# Exemplo aprovado — o reel de referência deste estilo

Este é o vídeo que definiu o padrão do estilo 03, aprovado como está: "3 ferramentas grátis do Claude",
38,8 s, 1080×1920, 30 fps, −14 LUFS. Ele foi montado com **este mesmo motor** (`../kit/`, intocado).
Remontado a partir desta pasta, o `index.html` sai byte a byte igual ao original, e os quadros saem iguais
pixel a pixel.

**Use como régua de qualidade, não como molde.** Cada vídeo novo tem o seu mapa de beats, feito a partir do que
é falado nele. O que se copia daqui é o nível:
- densidade (algo novo a cada 1,5–3 s);
- precisão (tudo entra na palavra);
- verdade (fatos com fonte, ilustração declarada);
- acabamento (vidro, brilho, troca de câmera animada, legenda que segue a boca).

## Arquivos
| Arquivo | O que é |
|---|---|
| `referencia-aprovada-540p.mp4` | o vídeo aprovado, em resolução reduzida, para assistir e comparar quadros |
| `beats-exemplo.js` | o roteiro visual completo (15 beats); é a melhor referência de uso do kit `K.*` |
| `vsl.json` | o enquadramento e a cor aprovados (`gradeFilter`, `tint`, `tint2`, `punch` 1,06…) |
| `mapa.md` | o mapa tempo × fala × câmera × peça (o formato que o `assets/map.md` de um vídeo novo deve ter) |
| `SOURCES.md` | as fontes dos fatos, dos preços e das imagens (o padrão da regra R3) |
| `transcript.json` | o transcript corrigido (R6) que os beats ancoram |
| `face-track.json` | o rastreio da boca usado pela legenda |
| `progresso-exemplo.md` | o caminho da produção: corte, transcript, enquadramento, material real, verificação e a correção de cor |
| `img/` | logos oficiais (Wikimedia Commons) e as telas ilustrativas (empresa fictícia "Padaria Trigo & Mel") |

## Remontar o exemplo (teste do motor)
Na pasta do motor do projeto (`<P>/motor`, a cópia do `modelo/`), depois do `preparar.sh` com o vídeo do exemplo:
```bash
cp exemplo/beats-exemplo.js src/beats.js && cp exemplo/vsl.json . && cp exemplo/img/* assets/img/
cp exemplo/transcript.json exemplo/face-track.json assets/
node montar.mjs && npx hyperframes lint
```
O vídeo da câmera do exemplo não acompanha a skill. Com o `clean.mp4` original, o `index.html` sai byte a byte igual.

## O que corrigir quando reaproveitar um trecho deste exemplo
O exemplo foi aprovado antes da regra R1 (rosto nunca coberto) ficar explícita. Três peças tocam a cabeça e
**não devem ser copiadas na mesma posição**:
- **carimbo "PRONTOS ✓"** (`K.stamp`, x 600, y 300): fica na testa, aos ~20 s. Num vídeo novo, ponha no peito,
  junto do painel de exportar (y ≥ 1150);
- **kicker "É muito fácil"** (`K.kickerTop`, y 250) e **"Link direto na sua DM"** (y 250): encostam no cabelo.
  Num vídeo novo, use uma pílula no peito (`K.pill`, y ~1390) ou ponha o kicker num trecho SPLIT.

## Som
O exemplo tem os efeitos do kit sem filtro: 56 efeitos em 38,8 s (≈ 1,4/s, contando a digitação). Esse é o som exato
do vídeo aprovado, e o `vsl.json` do exemplo o reproduz. **Num vídeo novo, o padrão é o enxuto** (`"sfxModo":
"enxuto"` no `vsl-padrao.json`): ficam as peças grandes e a digitação, até 0,8 efeito/s, e o `verificar.py` aprova.
No exemplo, o enxuto fica com 31 efeitos (0,80/s).
