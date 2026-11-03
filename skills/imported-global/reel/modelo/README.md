# Modelo do estilo 03 · VSL com interface animada

O motor pronto deste estilo é **o mesmo que produziu a referência aprovada** (38,8 s, 1080×1920). O kit fica em
`kit/`, intocado. Remontado a partir de `exemplo/`, ele gera o `index.html` byte a byte igual ao da referência,
e os quadros saem iguais pixel a pixel. **O que muda de reel para reel é só o `src/beats.js`**, o mapa daquele
conteúdo, e o enquadramento medido no `vsl.json`. A pele (fontes, cinco cores, som) é opcional (`pele-resolvida.json`
na pasta do projeto); sem ela, cores, fontes e som são os da referência: nunca fixe cor ou fonte no código.

## O que é cada arquivo
| Arquivo | Papel |
|---|---|
| `kit/kit.js` · `kit/kit.css` | o motor: câmeras FULL/SPLIT/PIP com troca animada, punch, grade, peças (`K.stack`, `K.pill`, `K.panel`, `K.grid`, `K.prompt`, `K.fan`, `K.stamp`, `K.cta`…), legenda que segue a boca (`K.mouthCaps`), efeitos sonoros e âncoras na fala (`K.at`, que dá erro se a frase não existir). **Não edite** |
| `kit/index.template.html` · `kit/fonts/` · `kit/sfx/` | a página, as fontes nativas (Anybody, Plus Jakarta Sans, JetBrains Mono) e os efeitos procedurais (sem licença de terceiros) |
| `montar.mjs` | monta `index.html` = template + `src/beats.js` + transcript + `vsl.json` + boca + pele + som. `--so-camera` gera a versão só com a câmera |
| `preparar.sh` | câmera 9:16 com a voz (`assets/clean.mp4`), transcript no formato do kit, fontes e material do projeto, `npm install`, rastreio da boca e a 1ª montagem |
| `vsl-padrao.json` | o `vsl.json` inicial: a cor e a grade aprovadas (fixas, R4) e o enquadramento a medir (`punch`, `face`, `head`, `fullPos`, `splitPos`) |
| `beats-modelo.js` | o `src/beats.js` inicial: a gramática fala → câmera → peça e as regras, com receitas comentadas |
| `sfx-enxuto.js` | o modo `"sfxModo": "enxuto"`, o padrão (R2: ≤ 0,8 efeito/s contando a digitação), injetado pelo `montar.mjs` |
| `ferramentas/rastrear-boca.py` | `assets/face-track.json` (MediaPipe; sem ele, OpenCV) — sem esse arquivo a legenda não aparece |
| `ferramentas/cards.mjs` | os cards da fase 1: um PNG por tela de `../entrega/planta.json`, tirado do motor no meio da tela |
| `ferramentas/sons.mjs` | `../sons.json` com os efeitos que o kit criou (densidade para o VERIFY e o crítico) |
| `ferramentas/audio-final-vsl.sh` | o áudio final deste estilo: ganho + limitador em 192 kHz, calibrado em até 3 passadas (−14 LUFS ±0,3, pico ≤ −1 dBTP). Use este, não o `audio-final.sh` comum: com os ataques rápidos dos efeitos do kit, o comum deixa o pico passar (+1,2 dBTP no teste) |
| `ferramentas/folha.sh` | `../qa/folha-final.png` (16 quadros do final) |
| `ferramentas/zona-segura-dom.mjs` | a zona segura lida no DOM: aponta o elemento fora da caixa (complementa o `zona-segura.py` da skill) |
| `ferramentas/ilustracoes/` | telas ilustrativas em HTML próprio → JPG (ilustração declarada, R3) |
| `ferramentas/gerar-sfx.mjs` | regera `kit/sfx/` |
| `exemplo/` | **o reel aprovado inteiro**: `beats-exemplo.js`, `vsl.json`, `mapa.md`, `SOURCES.md`, `transcript.json`, `face-track.json`, `img/`, `progresso-exemplo.md` e o vídeo em 540p |

## Prova de que o motor roda nesta máquina (sem agente, ~1 min + render)
Com o preparo pronto, o exemplo monta inteiro:
`cp exemplo/beats-exemplo.js src/beats.js; cp exemplo/vsl.json .; cp exemplo/img/* assets/img/; cp exemplo/transcript.json assets/`
e depois `node montar.mjs && npx hyperframes lint`. (O `vsl.json` do exemplo não tem `sfxModo`, então
sai com o som exato da referência; num vídeo novo, parta do `vsl-padrao.json`, que já vem com o enxuto.) As falas do exemplo só ancoram no vídeo do exemplo. Com
outro vídeo, o `K.at` dá erro na primeira frase que não existe, e isso já prova que as âncoras funcionam.

## Como produzir com ele (fase 1 e fase 2 do brief)
```bash
P=<pasta do projeto>; S=${REEL_SKILL:-~/.claude/skills/reel}; cd "$P"
cp -R "$S/modelo" motor && cd motor
bash preparar.sh                       # câmera 9:16 + voz, transcript, fontes/material, npm install, boca, 1ª montagem
# ---------- fase 1 · planta ----------
# 1. confira assets/transcript.json (nomes como a marca escreve, palavra-código do CTA em caixa alta — R6)
# 2. meça num quadro de assets/clean.mp4, com o punch aplicado: face {x,y,w,h}, head {x,y}, punch, fullPos, splitPos → vsl.json
#    (cor, grade e tinta NÃO mudam). Topo da cabeça alto (< ~300 px livres acima)? Nada no alto no FULL: tudo no peito (R1).
# 3. material real em assets/img/ e ../assets/SOURCES.md (prints e logos oficiais; tela sem print → ferramentas/ilustracoes/)
# 4. assets/map.md (formato: exemplo/mapa.md) → src/beats.js (leia exemplo/beats-exemplo.js inteiro antes)
node montar.mjs && npx hyperframes lint                       # 0 erros; snapshot vazio = âncora quebrada (veja o console)
# 5. escreva ../entrega/planta.json (n, layout FULL|SPLIT, de, ate, fala, tela) — uma tela por linha do mapa
node ferramentas/cards.mjs                                    # ../entrega/cards/P01.png… + imagem preenchida; pare e responda
# ---------- fase 2 · render (versão N) ----------
npx hyperframes snapshot --at <cada troca e cada beat> -o snapshots   # rosto livre (R1), nada cortado, nada sobreposto
node ferramentas/zona-segura-dom.mjs . --strict                       # "zona segura OK"
npx hyperframes render -q high -o ../render/_reel-bruto.mp4
node montar.mjs --so-camera && npx hyperframes render -q high -o ../render/_camera-so.mp4 && node montar.mjs
bash ferramentas/audio-final-vsl.sh ../render/_reel-bruto.mp4 ../render/reel-vN.mp4   # −14 LUFS ±0,3, pico ≤ −1 dBTP
node ferramentas/sons.mjs                                             # ../sons.json
bash ferramentas/folha.sh ../render/reel-vN.mp4 ../qa/folha-final.png
python3 "$S/ferramentas/verificar.py" .. --video render/reel-vN.mp4 --sfx ../sons.json --camera ../render/_camera-so.mp4
#   (S = a raiz da skill reel; o verificar.py escreve ../VERIFY.md e roda a zona segura → ../qa/zona-segura.png; --sfx e --camera são relativos a esta pasta)
# MINUTAGEM.md (o mapa com os tempos finais) e progresso.md na pasta do projeto, como no exemplo/progresso-exemplo.md
```

## O padrão de qualidade é o exemplo, não um mínimo
O reel de `exemplo/` é a régua. Antes de escrever o `beats.js`, assista `exemplo/referencia-aprovada-540p.mp4`
e leia `exemplo/beats-exemplo.js` e `exemplo/progresso-exemplo.md` inteiros. O nível esperado tem quatro partes:
- **Densidade:** algo novo a cada 1,5–3 s, com FULL e SPLIT perto de 50/50.
- **Precisão:** toda peça entra na palavra, por `K.at`.
- **Verdade:**
  - preço com a página oficial de preço e a data;
  - logos do Wikimedia Commons;
  - telas de produto sem print viram ilustração declarada, com empresa fictícia.
- **Acabamento:**
  - troca de câmera animada, com `K.hideMouth(t − 0.05, t + 0.5)` em toda troca;
  - lettering no peito com `K.hideMouth` no intervalo;
  - legenda com as palavras-chave em `accent`.

Cada vídeo tem o seu mapa: não copie as telas do exemplo, copie o nível.

## O que corrigir em relação ao exemplo
O exemplo foi aprovado antes de a regra R1 ficar explícita. Duas peças dele tocam a cabeça:
- o carimbo "PRONTOS ✓" (x 600, y 300);
- os kickers do topo (y 250).

Num vídeo novo, carimbo e kicker vão no peito (y ≥ 1150) ou num trecho SPLIT.

## O que não muda (invariantes do pele.json)
- FULL ↔ SPLIT sempre em troca animada de 0,45 s.
- Cada palavra-chave ganha uma peça exatamente na palavra.
- A interface é de vidro escuro, com a cor no gráfico e não no rosto: filtro `saturate(1.04) contrast(1.05) brightness(0.97)` e tinta 0,3 / 0,25.
- O gancho é o HUD de filmadora → glitch.
- Som: enxuto por padrão (`"sfxModo": "enxuto"`, aprovado pelo `verificar.py`). O som exato da referência (`"referencia"`, ~1,4/s) só entra a pedido (`"sfxModo": "referencia"` no `vsl.json`).
- As regras da casa R1–R11 valem por cima.
