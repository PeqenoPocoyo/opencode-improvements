# Estilo 03 · VSL com interface animada
*O vídeo é uma conversa que vira interface: a câmera alterna tela cheia com punch-in e tela dividida com o apresentador num card, e cada palavra-chave falada ganha um elemento que entra exatamente na palavra.*

> Especificação destilada de um reel real produzido neste estilo (é o motor da skill `reel`) (38,8 s, 1080×1920, 30 fps, −14 LUFS),
> gravado num estúdio escuro com luz roxa e azul a partir de um bruto horizontal 2560×1440 de 40,9 s.
> Os quadros de referência estão em `anexos/` (seção 13). As cores e fontes citadas aqui são os valores
> **nativos** da referência; a pele (`pele.json`) pode trocá-los pelos papéis.

> **MOTOR EMBUTIDO — use, não reconstrua.** A pasta `modelo/` é o motor exato que produziu a referência aprovada:
> `kit/` (kit `K.*`: layouts, peças, legenda que segue a boca, grade, SFX — intocado), `montar.mjs`, `preparar.sh`,
> `ferramentas/` e `exemplo/` (o vídeo aprovado inteiro: beats, mapa, fontes, imagens, diário e o vídeo em 540p;
> remontado, sai idêntico ao original, pixel a pixel). Copie `modelo/` para `<P>/motor` e siga o `modelo/README.md`.
> **Nunca escreva um motor novo nem edite `kit/`.** Cada vídeo novo escreve só o seu `src/beats.js` (o mapa daquele
> conteúdo) e ajusta o `vsl.json` (enquadramento medido). Fluxo na seção 10.0.

---

## 0 · Em uma frase + os 3 sinais

**Em uma frase:** o apresentador fala e a tela responde — tudo que ele diz vira peça de interface que nasce
na palavra, numa alternância constante entre tela cheia (FULL, com punch-in) e tela dividida (SPLIT, conteúdo
em cima e o apresentador num card embaixo), com conteúdo verdadeiro na tela e cor suave no rosto.

**Os 3 sinais (invariantes — se faltar um, não é este estilo):**
1. **FULL ↔ SPLIT animado.** A câmera alterna entre tela cheia com punch-in e tela dividida com o apresentador
   num card de cantos marcados na metade de baixo. A troca é sempre animada (0,45 s), nunca corte seco.
2. **Cada palavra-chave ganha um elemento que entra exatamente na palavra.** Nada entra em "segundos
   chutados": toda entrada é ancorada ao onset da palavra no transcript. Algo novo aparece a cada 1,5–3 s.
3. **Interface verdadeira, de vidro, com a cor nos gráficos e não na pele.** Os painéis são cards de vidro
   escuro com brilho na cor de `destaque`; os fatos, preços e logos vêm de fontes oficiais ou de ilustração
   declarada; o rosto fica com cor natural.

---

## 1 · O motor em uma página

Este estilo obedece às **regras da casa R1–R11** (`regras-da-casa.md`, na raiz da skill). As que ele tensiona estão
marcadas abaixo.

1. **O vídeo é uma conversa que vira interface.** O apresentador nunca some por muito tempo. A câmera alterna
   entre FULL (tela cheia com punch-in) e SPLIT (conteúdo em cima, o apresentador num card embaixo). Cada
   palavra-chave falada ganha um elemento que entra **exatamente na palavra**.
2. **Tudo é ancorado no transcript, nunca em segundos chutados.** O motor resolve o tempo de cada peça por uma
   *frase exata* do transcript (`K.at("frase exata", n)` devolve o onset da primeira palavra da n-ésima
   ocorrência; `K.end("frase exata")` devolve o fim da última) e **lança erro se a frase não existir**. Um snapshot
   sem overlay nenhum é o sintoma clássico de âncora quebrada.
3. **O conteúdo da tela é verdadeiro** (R3). Os fatos vêm de páginas oficiais, os preços das páginas oficiais
   de preço e os logos do Wikimedia Commons. Telas do produto que não existem para captura viram **ilustração
   declarada**, feita com uma empresa fictícia. Lição de produção: *"busque screenshots e tudo o que precisar"*
   — nada de tela genérica nem de número inventado.
4. **O corte é apertado, mas nenhuma palavra é comida** (R5). O estilo recebe o vídeo já limpo do motor de
   corte (`corte/`), com J/L ligado; toda emenda foi conferida por transcrição. Nenhuma pausa > 0,35 s sobra.
5. **A cor é suave** (R4). Lição de produção: a grade padrão do estilo de origem era *"muito agressiva e
   escura"*. A cor de `destaque` fica nas telas e nos brilhos; no rosto, só um toque (filtro
   `saturate(1.04) contrast(1.05) brightness(0.97)` e camadas de tinta 0,3 / 0,25).
6. **O rosto nunca é coberto** (R1). Os textos ficam no peito ou em tela dividida. Este estilo **tensiona R1**
   em três peças — título atrás da cabeça, kicker no topo e carimbo — que só entram quando sobra espaço acima da
   cabeça (seção 3.5); no enquadramento da referência, nenhuma delas coube e todas desceram para o peito.
7. **Legenda que segue a boca.** A legenda é de 1–3 palavras sob o queixo, acompanhando a cabeça; some sozinha
   em SPLIT e é escondida em todo lettering no peito e em toda troca de layout.
8. **Som enxuto por padrão** (R2). O kit põe efeito em cada peça (a referência aprovada tem ~1,4/s). O padrão é
   `"sfxModo": "enxuto"`: ficam as peças grandes (glitch, carimbo, clique, trocas) e a digitação, até 0,8 efeito/s
   contando tudo, e o `verificar.py` aprova. O som exato da referência (`"referencia"`) só entra a pedido (`"sfxModo": "referencia"`
   no `vsl.json`), e reprova o item de SFX do verificador.
9. **Gancho assinatura:** 1–2 s de "bruto" dessaturado com HUD de filmadora → glitch → entra a grade na cor de
   `destaque`.
10. **Vem verificado antes de entregar** (R9). Lint, snapshot em cada beat e em cada troca, zona segura a cada
    0,25 s, áudio a −14 LUFS e `VERIFY.md` com as evidências.

---

## 2 · Formato e números gerais

| Item | Valor |
|---|---|
| Duração típica | 35–45 s (referência: 38,8 s a partir de um bruto de 40,9 s) |
| Resolução · fps | 1080×1920 · 30 fps |
| Bruto aceito | horizontal (ex.: 2560×1440) recortado pelo centro para 9:16, ou vertical nativo |
| Layouts | FULL (tela cheia com punch-in) · SPLIT (conteúdo em cima, card do apresentador embaixo) · PIP (apresentador pequeno) · takeover (tela sem o apresentador) |
| Proporção-alvo dos layouts | FULL ~40 % · SPLIT ~45 % · PIP ~8 % · takeover ~7 % (a referência ficou ~50/50 FULL/SPLIT, sem PIP) |
| Cadência de novidade | algo novo na tela a cada 1,5–3 s |
| Punch-in base | **medido por vídeo**: 1,06 na referência (o padrão de origem, 1,22, corta demais quando o rosto já ocupa muito do quadro) |
| Punch extra de impacto | 1,14–1,20, em corte seco, em frase de impacto |
| Troca de layout | sempre animada, 0,45 s, `power3.inOut` |
| Entradas | blur → nítido, 0,22–0,5 s, `power3.out` |
| Saídas | blur + fade, 0,2–0,25 s |
| Pausas residuais no vídeo limpo | nenhuma > 0,35 s (referência: só duas, de 0,31 s e 0,29 s) |
| SFX | ≤ 0,85 por segundo (R2); volume geral ~0,4 |
| Áudio final | −14 LUFS (±0,5), pico ≤ −0,5 dBFS (o render sai em ~−25 LUFS e é normalizado depois) |
| Zona segura | x 90–990 · y 220–1520; nada na coluna de botões (x > 940 e y > 1150) |

---

## 3 · Layouts e enquadramento (px em 1080×1920)

### 3.1 Parâmetros de enquadramento (valores aprovados na referência)

Estes parâmetros são lidos pelo gerador do estilo. Os de rosto e cabeça vêm de `ferramentas/rosto.py`
e são **medidos num quadro do vídeo limpo já com o punch aplicado**.

| Parâmetro | Valor aprovado | O que é |
|---|---|---|
| `punch` | 1,06 | escala base do FULL (medir por vídeo) |
| posição do vídeo em FULL | `50% 28%` | `object-position` da câmera em tela cheia |
| posição do vídeo em SPLIT | `50% 26%` | `object-position` da câmera dentro do card |
| posição do vídeo em PIP | `50% 24%` | `object-position` da câmera no PIP |
| caixa do rosto | x 310 · y 300 · w 540 · h 680 | região que nada pode cobrir (R1) |
| ponto da cabeça | x 580 · y 620 | centro usado pela legenda que segue a boca |
| topo do conteúdo em SPLIT (`topY`) | 240 | logo abaixo da zona segura (220) |
| linha da legenda (`capY`) | 1500 | limite inferior da legenda, dentro da zona segura |
| filtro de cor | `saturate(1.04) contrast(1.05) brightness(0.97)` | R4 |
| tinta 1 · tinta 2 | 0,30 · 0,25 | opacidade das duas camadas de cor sobre a câmera |

Na referência a cabeça vai de ~y 150 a ~y 1000 no FULL: a cabeça é alta no quadro e isso decide quase tudo
do enquadramento (ver 3.5).

### 3.2 FULL (tela cheia com punch-in)
- A câmera ocupa o quadro inteiro, com escala `punch` (1,06) e `object-position 50% 28%`.
- Punch extra (1,14–1,20) em frase de impacto, aplicado em **corte seco** entre frases — é o único corte seco
  permitido no estilo (a troca FULL↔SPLIT nunca é seca).
- Tudo que entra em FULL fica **no peito**, entre o queixo e a legenda:

  | Elemento | Posição |
  |---|---|
  | Lettering empilhado | `top` 1150–1180 |
  | Pílulas | y 1250–1390 |
  | Painel pequeno (ex.: painel de exportar) | caixa y 1170–1470 |
  | Botão de CTA | y 1300 |

### 3.3 SPLIT (conteúdo em cima, apresentador num card embaixo)
- **Conteúdo:** y 240–960, x 90–990 (cabeçalho com kicker + título no topo, painel/grade/leque abaixo).
- **Card do apresentador:** metade de baixo, com o vídeo em `object-position 50% 26%` e moldura de cantos
  (quatro "L" nos cantos, como mira de filmadora), o rosto inteiro dentro do card.
- A legenda que segue a boca **some sozinha** em SPLIT (o conteúdo de cima já carrega o texto).
- Dentro do SPLIT, os tops dos elementos não podem coincidir: o leque de slides entra em `top` 600 para não
  cair em cima da barra de progresso (lição de produção).

### 3.4 PIP e takeover
- **PIP:** o apresentador pequeno (`object-position 50% 24%`) com conteúdo dominando a tela. A referência não
  usou; fica como opção para trechos em que a interface precisa da tela inteira sem perder o apresentador.
- **Takeover:** cena só de interface, sem o apresentador (~7 % do vídeo, no máximo). É a 3ª opção de R1.

### 3.5 A costura FULL ↔ SPLIT
- Troca sempre animada: 0,45 s, `power3.inOut`. O vídeo encolhe/cresce entre o quadro inteiro e o card.
- **A legenda da boca é escondida em toda troca**, de `t − 0,05 s` a `t + 0,5 s`: ela acompanha o quadro
  encolhendo e "vaza" para fora da zona segura se ficar ligada (lição de produção: a varredura de zona segura
  acusou texto exatamente na transição de 25,7 s da referência). O gerador do estilo faz isso automaticamente.
- Uma transição de luz (flash ou light leak) pode cobrir a troca quando a cena pede impacto.

### 3.6 O que a altura da cabeça decide (tensão com R1)
Meça o topo da cabeça com `ferramentas/rosto.py`. Com **menos de ~300 px livres acima da cabeça**:
- título atrás da cabeça (com recorte do apresentador) **desligado** — na referência a cabeça cobria quase o
  título inteiro e ele ficou ilegível; no lugar, lettering empilhado no peito (`top` ~1150) com a legenda da
  boca escondida no mesmo intervalo;
- kicker no topo (y 250) **proibido** — encosta no cabelo; vai para o peito ou vira pílula;
- carimbo no alto (x 600, y 300) **proibido** — pega o alto da cabeça; vai para o peito, junto do painel.
O padrão do gerador é o peito; o alto do quadro só é liberado quando a medição mostra espaço.

---

## 4 · Corte e ritmo

### 4.1 Contrato com o motor de cortes
O corte do bruto não é do estilo. O motor de corte (`corte/`) tira pausas, respirações, "ééé", gaguejos e retomadas,
confere cada emenda por transcrição e entrega `clean.mp4` (30 fps, keyframe a cada 1 s) + `cortepalavras.json`,
obedecendo a R5. Este estilo pede o motor com **J/L ligado (4 quadros)**: a voz entra um pouco antes da imagem
em cada emenda, o que esconde os cortes num vídeo em que a câmera está sempre em movimento.

O estilo começa no vídeo limpo. Depois de qualquer recorte novo, retranscreva e remapeie tudo que dependia dos
tempos (cenas, SFX, ênfases, rastreio do rosto) — nunca misture tempos do bruto com os do vídeo limpo.

### 4.2 Onde o corte cai
- **Entre frases, em FULL:** punch extra em corte seco (1,14–1,20) na frase de impacto.
- **Na palavra-chave:** não há corte — a peça entra exatamente no onset da palavra, por cima da câmera.
- **Na troca de layout:** transição animada de 0,45 s, posicionada no começo da frase que pede o conteúdo
  (ex.: a troca para SPLIT entra em "economizar", e o painel de preços começa a revelar na mesma frase).
- **Em cena de luz:** flash ou light leak no onset da palavra que vira "virada" (ex.: "totalmente", "tudo").

### 4.3 Cadência
- Algo novo a cada 1,5–3 s: ou troca de layout, ou peça nova, ou passo novo dentro de um painel.
- Um painel revela seus passos **palavra a palavra** (ex.: linha de preço 1 → linha 2 → total riscado → "R$ 0"),
  cada passo na sua palavra.
- Grade de cards: cada card entra no nome falado ("Slides", "Docs", "Design" → 3 entradas em ~2 s).
- Regra do tempo de leitura: uma pílula ou lettering fica até o fim da frase (`fim("frase")`) ou até a próxima
  peça do mesmo lugar; nunca menos de ~0,8 s em tela.

### 4.4 Pausas
Nenhuma > 0,35 s no vídeo limpo. Uma pausa de 0,44 s que sobrou na referência foi tirada encurtando a janela
protegida do corte — pausa que sobra depois da montagem é remapeada pelo motor, nunca à mão.

---

## 5 · Movimento

### 5.1 Entradas
- **Blur → nítido:** `opacity 0`, `blur 8–18 px`, e `y 10–26 px` **ou** `scale 0,8–0,96` → estado final em
  0,22–0,5 s, `power3.out`.
- Três sabores de lettering: `blur` (o padrão acima), `glow` (nítido com brilho na cor de `destaque` que
  pulsa uma vez) e `letters` (letra a letra, para a frase de impacto).
- Peças de interface (painel, chat, grade) entram com o mesmo blur → nítido; seus **passos internos** entram
  cada um na sua palavra, com a mesma curva, e podem levar um SFX próprio só se forem "grandes".

### 5.2 Saídas
- Blur + fade em 0,2–0,25 s. Nada some em corte seco a não ser a câmera no punch de impacto.

### 5.3 Câmera
- **Troca de layout sempre animada:** 0,45 s, `power3.inOut`. Nunca corte seco FULL↔SPLIT.
- **FULL é sempre punch-in.** Punch extra (1,14–1,20) em corte seco na frase de impacto.
- A legenda da boca acompanha o ponto da cabeça; durante a troca ela é escondida (3.5).

### 5.4 Transições de luz
- **Flash:** pico de branco curto no onset da palavra, com `peak` configurável (~0,6–0,8).
- **Light leak:** mancha de luz na cor de `destaque` cruzando o quadro por `d` segundos (~0,6 s), usada para
  cobrir uma troca SPLIT → FULL.
- **Glitch:** só no gancho, logo depois do HUD de filmadora, junto do boom.

### 5.5 Cursor e digitação
- **Pedido digitando:** o texto do pedido entra no campo do chat a `cps` caracteres por segundo (~18–24), e o
  botão de enviar "aperta" em `send` (fim da frase falada).
- **Botão de CTA:** o cursor desliza até o botão e clica em `clickAt` (onset da palavra-código).
- **Seta desenhada:** no painel de exportar, a seta entre o deck e os logos é desenhada (stroke) em ~0,4 s.

### 5.6 O que NUNCA se faz
- Corte seco entre FULL e SPLIT.
- Entrada antes da palavra (antecipar) ou em "segundos chutados".
- "Camadas 3D" (profundidade falsa com parallax de camadas) — vetado na origem do estilo.
- Animar `scale`/`scaleX` sem incluir `opacity` no destino: a peça some no render.
- Animar `left`: o lint reprova; anime com `x`.
- Cobrir o rosto, escurecê-lo "só por um instante" ou colocar peça na coluna de botões.

---

## 6 · Legenda

- **Modo:** legenda de **1–3 palavras**, sem pílula, que **segue a boca** — posicionada sob o queixo a partir
  do `rosto.json` (rastreio do rosto por quadro-chave) e acompanhando a cabeça quando ela se move.
- **Fonte:** fonte de texto (nativa: Plus Jakarta Sans 700/800), na cor de `texto` (nativa `#ffffff`).
- **Palavras-acento:** uma lista declarada por vídeo (ex.: "Claude", "utiliza", "fácil", "prontos",
  "PowerPoint", "carrossel", "link") sai na cor de `apoio` (nativa `#b9a3ff`, lavanda).
- **Em SPLIT:** some sozinha (o cabeçalho de cima carrega a ideia).
- **Em lettering no peito:** escondida no mesmo intervalo do lettering, para não brigar com ele.
- **Em troca de layout:** escondida de `t − 0,05 s` a `t + 0,5 s` (automático no gerador).
- **Limite inferior:** `capY` 1500, dentro da zona segura.
- **Texto:** transcript corrigido à mão antes de montar (R6), guardando o original; a palavra-código do CTA
  em CAIXA ALTA ("SLIDES"). Correções típicas vistas na referência: Cloud → Claude · A → IA · Gama → Gamma ·
  carrocéis → carrosséis · vim → envio · "slides" (no CTA) → SLIDES.
- Palavra repetida pede âncora com mais contexto (`âncora("te entregar")`, não `âncora("entregar")`), ou a
  n-ésima ocorrência (`âncora("slides", 3)`).

---

## 7 · Peças e telas

### 7.1 Camadas da cena (de baixo para cima)
1. vídeo da câmera com grade de cor (filtro CSS + duas camadas de tinta na cor de `destaque`, opacidades
   0,30 e 0,25);
2. matte opcional do apresentador (só para título atrás da cabeça, quando couber);
3. overlays de vidro (painéis, pílulas, cards, lettering);
4. legenda que segue a boca.

### 7.2 Paleta nativa (por papel)

| Papel | Nativo | Onde |
|---|---|---|
| `fundo` | `#1f123d` (variantes `#0e0b1e`, `#2d1f50`) | fundo do SPLIT, vidro dos painéis |
| `texto` | `#ffffff` | lettering, títulos, legenda |
| `destaque` | `#8b5cf6` / `#9b63ff` | acento: brilhos, bordas, ícones, botão (gradiente `#8b55ff → #a47fff`) |
| `apoio` | `#b9a3ff` (lavanda) | palavras-acento na legenda e nos títulos |
| `acento2` | `#a59cc4` (muted) | kickers, rótulos pequenos, fonte dos preços |

**Fontes nativas:** fonte de destaque = Anybody 900 larga (display, CAIXA ALTA no lettering); fonte de texto =
Plus Jakarta Sans 700/800 (texto e UI); fonte técnica = JetBrains Mono (HUD de filmadora, rótulos técnicos).

### 7.3 Vidro
Card de vidro escuro: fundo `fundo` a ~70–80 % com desfoque de fundo, borda de 1 px em `destaque` a ~25 %,
raio ~24 px, brilho suave (`box-shadow` na cor de `destaque`, sem glow estourado — ver "brilho sem estourar"
nos portões). O card do apresentador em SPLIT usa a mesma linguagem, com os quatro cantos em "L".

### 7.4 Catálogo de peças (o vocabulário do gerador do estilo)
Toda peça recebe o tempo por âncora de frase e, opcionalmente, `until` (quando sai). Cores por papel.

| Peça | Quando entra | Composição |
|---|---|---|
| **HUD de filmadora** `(t0, t1, {label})` | gancho, 1–2 s iniciais | câmera dessaturada, cantos em "L", "REC" com ponto, timecode em fonte técnica, rótulo pequeno no canto inferior (ex.: "NOVIDADE · CLAUDE") |
| **Glitch** `(t)` | fim do HUD | deslocamento RGB + fatias por ~0,2 s; entra o boom e a grade de cor |
| **Punch** `(t, escala)` | entre frases | reenquadra a câmera em corte seco (1,06 base; 1,14–1,20 no impacto) |
| **Layout** `('split' \| 'full', t)` | começo da frase que pede conteúdo | troca animada de 0,45 s; esconde a legenda automaticamente |
| **Lettering empilhado** `([{text, t, style}], {top, until})` | frase de impacto em FULL | uma linha por palavra/grupo, fonte de destaque em caixa alta, `top` 1150–1180 (peito); estilos `blur` / `glow` / `letters` |
| **Esconder legenda** `(a, b)` | junto de lettering e trocas | some a legenda da boca no intervalo |
| **Flash** `(t, {peak})` · **Light leak** `(t, d)` | viradas de frase, trocas | transição de luz (5.4) |
| **Pílula** `(texto, t, {y, icon, kind, up, until})` | afirmação curta em FULL | cápsula de vidro com ícone e brilho em `destaque`, y 1250–1390; `kind: 'strike'` = riscada (para o que se deixa de pagar) |
| **Cabeçalho de seção** `({kicker, title, acc}, t, {y, until})` | topo do SPLIT | kicker pequeno em `acento2` + título em `texto` com palavras-acento em `apoio` |
| **Painel** `(html, t, {box, steps: [{sel, t, anim, sfx}], until})` | SPLIT (ou peito, se pequeno) | card de vidro com HTML próprio; cada `step` revela um seletor na sua palavra (tabela de preços, chat, painel de exportar) |
| **Grade de cards** `([{img, label, icon, t}], {top, cols, w, h, gx, until})` | lista falada | cards com imagem + rótulo + ícone, cada um entrando no nome falado |
| **Pedido digitando** `(texto, t, {x, y, w, cps, send, until})` | "é só você pedir…" | campo de chat com o texto digitando e o envio em `send` |
| **Barra de progresso** `(label, t, d, {box, until})` | "ele vai preparar…" | barra com rótulo e porcentagem, enchendo em `d` segundos |
| **Leque** `(imgs, t, {top, w, h, until})` | "todos os slides" / carrossel | 3–4 imagens em leque, leve rotação, entrando em cascata |
| **Carimbo** `(texto, t, {x, y, rot, until})` | "prontos" | carimbo rotacionado com hit; **no peito**, nunca no alto (3.6) |
| **Quadro tracejado** `(texto, t, {box}).recebe(img, t, {w, h})` | "um roteiro" | quadro com borda tracejada e rótulo em caixa alta que recebe o documento quando ele é dito |
| **Kicker** `(texto, t, {y, until})` | frase curta de apoio | texto pequeno em `acento2`; **no peito**, nunca em y 250 (3.6) |
| **Botão de CTA** `(texto, t, {y, w, clickAt})` | CTA final | botão com gradiente de `destaque`, cursor que clica em `clickAt`, y 1300 |
| **Legenda da boca** `({accent: […]})` | o vídeo inteiro | seção 6 |
| `âncora(frase, n)` · `fim(frase)` | tudo | tempos pelo transcript (n = n-ésima ocorrência) |

**Peças do vocabulário que a referência não usou** (existem no estilo, disponíveis): título atrás da cabeça
(precisa de matte e de espaço acima da cabeça), HUD no rosto, fileira 3D, órbita de logos, parede de cards,
logo isolado, letreiro rolante; antes/depois, etiqueta de preço, anel de progresso, bolha de DM, terminal;
versus, explosão de peças; e a família "editando ao vivo" (onda de áudio cortada, comparação, painel de
estilo, fluxo, comentário, cursor). **Vetado:** camadas 3D com parallax.

### 7.5 As telas da referência (composição de cada uma)
- **Painel de preços (SPLIT, 3,2–6,1 s):** cabeçalho "Quanto você deixa de pagar / Por ano, sem o Claude";
  tabela de vidro com linha "Gamma Pro · R$ 840/ano" → linha "Canva Pro · R$ 290/ano" → total "R$ 1.130"
  riscado → "Com o Claude · R$ 0" em `apoio`; rodapé com a fonte dos preços (páginas oficiais, plano anual).
  Marcas sem logo livre entram **só como texto**.
- **Grade de 3 cards (SPLIT, 6,2–8,1 s):** kicker "Elas se chamam" + título "Slides · Docs · Design";
  três cards com a imagem ilustrativa e o rótulo com ícone, cada um no nome falado.
- **Chat + pedido (SPLIT, 11,9–16,0 s):** card de vidro imitando o chat do produto (avatar, nome, "Como posso
  te ajudar hoje?"), campo com o pedido digitando ("Crie uma apresentação comercial p…") e botão de enviar.
- **Progresso → leque (SPLIT, 16,0–18,8 s):** cabeçalho "Sua apresentação pronta", barra "Criando os slides"
  até 97–100 %, depois leque de 3 slides em `top` 600.
- **Painel de exportar (FULL, no peito, 18,8–23,9 s):** caixa y 1170–1470 com kicker "Exportar apresentação",
  miniatura do deck → seta desenhada → logos oficiais (PowerPoint / Google Slides, do Wikimedia Commons).
- **Quadro "ROTEIRO" + carrossel (SPLIT, 25,6–32,9 s):** cabeçalho "Na mesma conversa / Do roteiro ao
  carrossel"; novo pedido digitando ("Agora cria um roteiro d…"); quadro tracejado "ROTEIRO" recebe o
  documento; depois leque de 4 slides de carrossel + selo "Carrossel no Instagram" com o logo oficial.
- **Pílulas riscadas + lettering (FULL, 32,9–36,8 s):** pílulas "GAMMA" e "CANVA" riscadas no peito → flash →
  lettering "TUDO EM / 1 CONVERSA".
- **CTA (FULL, 36,8–38,8 s):** botão "COMENTA SLIDES →" em y 1300 com cursor clicando no onset de "SLIDES";
  kicker "Link direto na sua DM" **no peito** (na referência ficou em y 250 e foi apontado como erro).

### 7.6 Ilustração declarada (quando não há print oficial)
As telas do produto que não existem para captura foram feitas em HTML próprio e renderizadas em JPG por um
navegador headless (caminho do navegador pela variável `CHROME`, R10):
- paleta fiel ao produto imitado (na referência: creme `#faf9f5`, terracota `#d97757`, Inter + Source Serif —
  cores de interface recriada ficam literais);
- empresa fictícia (na referência, uma padaria), nunca imitando um cliente real;
- peças: 4 slides de proposta comercial, 1 documento "roteiro", 1 canvas de design e 4 slides de carrossel;
- toda ilustração declarada em `assets/SOURCES.md` e na entrega.

---

## 8 · Som

- **Regra-mãe: R2** (≤ 0,85 SFX/s; whoosh só em troca de cena de verdade; hit só em carimbo, X ou impacto;
  nada em peça pequena nem em peça que entra < 0,6 s depois de outro som; volumes 0,1–0,2 da voz).
- **Onde o estilo põe som:** só nas peças grandes — troca de layout (whoosh), painel (whoosh curto na
  entrada), CTA (pop no clique), carimbo (hit), glitch (boom, só no gancho). Pílulas, cards de grade, passos
  internos de painel e kickers entram **sem som**.
- **Volume e densidade:** o padrão é `"sfxModo": "enxuto"` (`modelo/sfx-enxuto.js`, decisão de 28/10/2026). Ele
  aplica a R2 sem mexer no kit: ≤ 0,8 efeito/s contando a digitação, como o `verificar.py` conta. No teste com o
  exemplo ficaram 31 efeitos (0,80/s) e a verificação aprovou. A pele ajusta: intensidade 0,3 → enxuto e −3 dB;
  0,6 → enxuto; 0,85 → o som exato da referência (`"referencia"`, ≈ 1,4/s, que reprova o item de SFX do
  verificador); efeitos desligados → nenhum som além da voz.
- **Boom:** uma vez, no glitch do gancho.
- **Digitação:** no pedido digitando, sample natural a ~9 teclas/s, contínuo sobre o trecho, ≈ 12 dB abaixo
  da voz (R2).
- **Trilha:** a referência não tem trilha musical; só voz + SFX. Se entrar trilha, fica ≥ 13 LU abaixo da voz.
- **Fonte dos sons:** `modelo/kit/sfx/` (efeitos procedurais gerados por `modelo/ferramentas/gerar-sfx.mjs`, sem licença de terceiros).
- **Contagem por segundo** conferida no build antes do render (portão 8 da seção 11).

---

## 9 · Pele

**O que a pele troca** (`pele.json`): as duas fontes (destaque / texto) e os cinco papéis de cor (fundo, texto,
destaque, apoio, acento2). O gradiente do botão deriva de `destaque` (de `destaque` para `destaque` 20 % mais
claro); as duas camadas de tinta sobre a câmera usam `destaque` nas opacidades 0,30 e 0,25.

**O que fica fixo, seja qual for a pele:**
- o filtro de cor do rosto (`saturate(1.04) contrast(1.05) brightness(0.97)`) e o teto de tinta 0,3 (R4);
- a fonte técnica do HUD (nativa: JetBrains Mono) — é parte da assinatura do gancho;
- as cores de interface recriada (chat do produto, ilustrações) — fiéis ao produto;
- os logos oficiais (nunca recoloridos);
- a geometria: punch, posições, tops, zona segura, durações e easings.

**Clima:** escuro. O estilo foi calibrado para um estúdio escuro com luz colorida; com bruto claro ou neutro,
a grade pode subir **só com antes × depois mostrado e aprovado** (`anexos/cor-antes-depois.jpg` é o
exemplo do que "agressivo" × "suave" significa).

---

## 10 · Pipeline passo a passo

### 10.0 Com o motor embutido (o caminho padrão)
```bash
S=${REEL_SKILL:-~/.claude/skills/reel}; cd <P>
cp -R "$S/modelo" motor && cd motor
bash preparar.sh      # câmera 9:16 (corte/clean-916-grade.mp4) + voz (corte/corte.wav), transcript (preparo/palavras.json),
                      # fontes da pele, material de assets/oficiais, npm install, rastreio da boca, 1ª montagem
```
Depois, a sequência das fases 1 e 2 do `modelo/README.md`:
- **Fase 1:** transcript conferido → `vsl.json` medido → material + SOURCES → `assets/map.md` → `src/beats.js` →
  `node montar.mjs` + lint → `../entrega/planta.json` → `node ferramentas/cards.mjs`.
- **Fase 2:** snapshots → zona segura → render → só-câmera → `ferramentas/audio-final-vsl.sh` → `sons.json` → folha → `verificar.py`.

O `montar.mjs` aplica a pele (`pele-resolvida.json`): cores → variáveis do kit; fontes → `fontes.css`; som → modo e
volume. Com pele nativa, o resultado tem as cores da referência. Os passos 10.1–10.13 abaixo detalham cada etapa e os
critérios.

### 10.1 Corte (motor de corte `corte/`, J/L de 4 quadros ligado)
- **Entra:** o bruto (horizontal ou vertical).
- **Sai:** `clean.mp4` (30 fps, keyframe a cada 1 s — `-g 30`), `corte.wav`, `corte16k.wav`, `edl.json`,
  `cortepalavras.json`.
- **Critério:** nenhuma palavra comida (cada emenda conferida por transcrição em janela), nenhuma pausa
  > 0,35 s, última tomada certa de cada frase (R5). Exemplo ilustrativo do que o corte pelo som come em fala
  rápida e precisa ser protegido: "economizar", "pedir pra ele", "pro seu negócio", "um roteiro",
  "carrosséis no" — cada um virou um intervalo protegido do bruto, e o corte rodou de novo.

### 10.2 Recorte 9:16
- **Entra:** `clean.mp4` + `edl.json` (para ler o bruto em resolução cheia quando o bruto é horizontal).
- **Sai:** `assets/clean.mp4` 1080×1920 com o centro do horizontal recortado, 30 fps, keyframe a cada 1 s e a voz
  do `corte.wav` (feito por `modelo/preparar.sh`).
- **Critério:** rosto inteiro no quadro; o punch base escolhido (1,06) não corta a cabeça nem o queixo.

### 10.3 Transcrição e correção
- **Entra:** `clean.mp4` (ou `corte16k.wav`) → `ferramentas/preparar.py <video> <pasta>`.
- **Sai:** `palavras.json` (palavra a palavra com tempos), pausas > 0,4 s, `meta.json`; mais `words.txt`
  legível (palavras com tempos e pausas) para ler o mapa.
- **Critério:** transcript corrigido à mão (R6) com o original guardado em `transcript-bruto.json`; a
  correção é por tempo quando a palavra se repete; a palavra-código do CTA em caixa alta.
- Formato que o gerador lê: `{"words":[{"text","start","end"}],"audio_duration_secs"}`.

### 10.4 Rosto
- **Legenda que segue a boca:** `modelo/ferramentas/rastrear-boca.py` (MediaPipe com `VSL_PYTHON` + `FACE_MODEL`;
  sem MediaPipe, OpenCV) gera `assets/face-track.json`, que o kit lê (`K.mouthCaps`). `preparar.sh` já roda; sem
  ele, não há legenda.
- **Entra:** `clean.mp4` → `ferramentas/rosto.py <video> <pasta>` (medidas para o enquadramento).
- **Sai:** `rosto.json` por quadro-chave (topo da cabeça, queixo, centro, largura) + sugestões de enquadramento.
- **Critério:** caixa do rosto e ponto da cabeça medidos **com o punch aplicado**; decisão registrada: título
  atrás da cabeça ligado só com ≥ ~300 px livres acima da cabeça.

### 10.5 Matte (opcional)
- **Entra:** `clean.mp4` → `ferramentas/recortar.py <video> <pasta>` (modelo pela variável `RVM_MODEL`).
- **Sai:** `matte/` do apresentador.
- **Critério:** só roda se o passo 10.4 liberou título atrás da cabeça; senão, pula (na referência o matte foi
  gerado e não serviu).

### 10.6 Pesquisa e materiais (obrigatório antes dos beats)
- **Entra:** o transcript corrigido — cada afirmação e cada número dito.
- **Sai:** `assets/SOURCES.md` (arquivo, origem, URL, licença, data da consulta); `assets/img/` com logos
  oficiais e prints; `assets/mock/` com as ilustrações declaradas (HTML próprio → JPG).
- **Critério (R3):** cada fato com página oficial; cada preço com página oficial de preço, moeda e período;
  logos do Wikimedia Commons ou marca só como texto; CAPTCHA nunca burlado (ler a página num navegador
  normal); fala e tela em moedas diferentes conferidas e avisadas na entrega (na referência: fala
  "centenas de dólares", tela "R$ 1.130/ano" ≈ US$ 200 — coerente, avisado).

### 10.7 Mapa de beats
- **Entra:** `words.txt`, `rosto.json`, `SOURCES.md`.
- **Sai:** `assets/map.md` — tabela tempo × fala × câmera × peça (modelo na seção 12).
- **Critério:** algo novo a cada 1,5–3 s; proporção dos layouts perto do alvo; nenhuma peça prevista para o
  alto do quadro se 10.4 não liberou. **Mostrar o mapa antes de montar**, a não ser que o pedido diga para ir
  direto.

### 10.8 Composição (motor embutido + `npx hyperframes`)
- **Entra:** o mapa, os parâmetros de enquadramento (3.1), o transcript.
- **Sai:** a composição HTML do projeto, com uma chamada de peça por linha do mapa.
- **Critério:** `npx hyperframes lint` com 0 erros. O motor (`modelo/kit/kit.js`) já cumpre os requisitos
  abaixo, menos os marcados com ⚑, que são responsabilidade de quem escreve o `beats.js`:
  - toda entrada ancorada a uma frase do transcript; **frase inexistente lança erro** (nunca cai em tempo 0);
  - n-ésima ocorrência e fim de frase disponíveis;
  - ⚑ legenda da boca escondida em toda troca de layout (`K.hideMouth(t − 0.05, t + 0.5)`) e em todo lettering
    no peito (`K.hideMouth` no intervalo do `K.stack`) — como no `modelo/exemplo/beats-exemplo.js`;
  - ⚑ título atrás da cabeça só quando 10.4 liberou; kicker e carimbo no peito (o exemplo os tem no alto da
    cabeça — ver `modelo/exemplo/LEIA.md`, "o que corrigir");
  - SFX no modo enxuto por padrão (seção 8), que imprime a contagem por segundo no console;
  - punch base lido do `vsl.json` (medido por vídeo), nunca fixo.
  - Lição: um snapshot sem overlay nenhum = âncora quebrada; abra a composição no navegador e leia o console.

### 10.9 Snapshots e zona segura
- **Entra:** a composição.
- **Sai:** `npx hyperframes snapshot` em cada beat e em cada troca de layout → `snapshots/`;
  `ferramentas/zona-segura.py <video>` (varredura a cada 0,25 s).
- **Critério:** rosto livre em todos os quadros (R1); nada cortado; nada sobreposto (tops coincidentes no
  SPLIT); texto legível; brilho sem estourar; zona segura OK (x 90–990, y 220–1520, nada na coluna de botões).

### 10.10 Render e cor
- **Entra:** a composição aprovada → `npx hyperframes render -q high -o renders/<slug>-render-bruto.mp4`.
- **Sai:** o render bruto (sai em ~−25 LUFS).
- **Critério:** cor dentro de R4 (o `gradeFilter` e as tintas do `vsl.json` já são os valores aprovados);
  grade mais forte só com antes × depois aprovado.

### 10.11 Áudio final
- **Entra:** o render bruto → `bash ferramentas/audio-final-vsl.sh <bruto> <saida>` (na pasta do motor).
- **Sai:** `render/reel-vN.mp4` a −14 LUFS (±0,3), pico verdadeiro ≤ −1 dBTP, imagem copiada (`-c:v copy`), AAC 192 kbps
  48 kHz, `+faststart`.
- **Critério:** os efeitos do kit têm ataques rápidos. O `audio-final.sh` comum da skill (loudnorm linear +
  limitador a 0,94) deixou o pico em +1,2 dBTP neste estilo. O acabamento do estilo usa ganho + limitador em
  192 kHz, com o ganho calibrado em até 3 passadas. No teste deu −14,3 LUFS e −0,92 dBTP.

### 10.12 Verificação e entrega
- **Entra:** o final → `ferramentas/verificar.py <pasta>`.
- **Sai:** `VERIFY.md` com duração, LUFS e pico, palavras protegidas no corte, correções de legenda, lint,
  zona segura, o que foi corrigido nos snapshots, folha de quadros do final e pontos abertos.
- **Critério:** todos os portões da seção 11. **Nunca publicar nem enviar o vídeo.**

### 10.13 Ambiente
Tudo isolado por variável de ambiente (R10): `WHISPER_PYTHON`, `FACE_MODEL`, `RVM_MODEL`, `CHROME`. Nada
gravado em pastas globais do usuário. Problemas já vistos: transcrição "terminando" sem arquivo → fixar
`av==16.1.0`; snapshot quebrando com erro do postcss → `npm ci` na raiz; pasta de cache inexistente → criar
antes de baixar.

---

## 11 · Aceite numérico (portões — nada é entregue sem passar)

| # | Portão | Alvo |
|---|---|---|
| 1 | Corte | todas as emendas conferidas; nenhuma palavra comida; nenhuma pausa > 0,35 s |
| 2 | Legenda | transcript corrigido (nomes de produto, siglas, palavra-código em caixa alta); original guardado |
| 3 | Fatos | cada afirmação e cada número com fonte em `SOURCES.md`; ilustrações declaradas; moedas conferidas |
| 4 | Lint | `npx hyperframes lint` = 0 erros |
| 5 | Snapshots | 1 por beat + 1 por troca de layout: rosto livre · nada cortado · nada sobreposto · texto legível · brilho sem estourar |
| 6 | Zona segura | `ferramentas/zona-segura.py` = OK (x 90–990 · y 220–1520 · nada em x > 940 ∧ y > 1150), varredura a cada 0,25 s |
| 7 | Cor | filtro `saturate(1.04) contrast(1.05) brightness(0.97)`, tintas ≤ 0,3 / 0,25 — ou antes × depois aprovado |
| 8 | SFX | ≤ 0,85/s; volume geral ~0,4; só peças grandes; nada < 0,6 s depois de outro som |
| 9 | Áudio | −14 LUFS (±0,5); pico ≤ −0,5 dBFS; imagem não recodificada |
| 10 | Movimento | trocas de layout a 0,45 s `power3.inOut`; entradas 0,22–0,5 s; algo novo a cada 1,5–3 s |
| 11 | Sincronia | cada peça no onset da palavra ancorada (tolerância: 1 quadro); nenhuma peça antes da palavra |
| 12 | Duração · formato | 1080×1920 · 30 fps · 35–45 s |
| 13 | `VERIFY.md` | escrito, com evidências; vídeo **não** publicado nem enviado |

---

## 12 · Lições de produção

### 12.1 As correções que tornaram o resultado "aprovado"

**L-1 · Material real.** Nada de tela genérica ou número inventado. A pesquisa é uma etapa obrigatória do
pipeline (10.6), antes de escrever os beats. Prioridade: print/logo oficial → Commons → ilustração declarada
com empresa fictícia. CAPTCHA nunca se burla: troca-se de ferramenta.

**L-2 · Cor suave.** A grade padrão do estilo de origem era calibrada para "fazer ficar roxo" e, em cima de
um estúdio que já é escuro com luz colorida, escurecia e saturava demais o rosto.

| Parâmetro | Padrão de origem (reprovado) | **Aprovado** |
|---|---|---|
| filtro de cor | `saturate(1.08) contrast(1.2) brightness(0.8)` | `saturate(1.04) contrast(1.05) brightness(0.97)` |
| tinta 1 | 0,85 | **0,30** |
| tinta 2 | 0,55 | **0,25** |

Parta dos valores aprovados. Só suba a grade com bruto claro ou neutro, e mostre o antes × depois antes de
renderizar. A cor da identidade vem das telas, pílulas e brilhos, não de pintar o rosto.

**L-3 · Rosto nunca coberto.** Lettering e pílulas no peito, conteúdo pesado em SPLIT. As exceções que
apareceram e foram apontadas: kickers pequenos no topo (y 250) encostando no cabelo e carimbo "PRONTOS ✓"
(x 600, y 300) pegando o alto da cabeça → ambos para o peito. Checagem obrigatória do rosto em todos os
snapshots; um quadro com algo sobre o rosto é reprovado.

**L-4 · Título atrás da cabeça não funciona com cabeça alta.** A marca do estilo de origem ficou ilegível
porque a cabeça cobria quase tudo. Solução: lettering empilhado no peito (`top` ~1150) com a legenda da boca
escondida no mesmo intervalo. Regra: medir o topo da cabeça; < ~300 px livres → desligar o título atrás.

**L-5 · Menos efeito sonoro.** Os SFX automáticos de cada peça, a 0,55, passaram do ponto. SFX só nas peças
grandes, volume ~0,4, contagem por segundo no build.

### 12.2 Consertos técnicos no caminho

| Sintoma | Causa | Conserto |
|---|---|---|
| Transcrição "termina" sem gerar arquivo | biblioteca `av` nova incompatível com o transcritor | fixar `av==16.1.0` no ambiente |
| Palavras comidas no corte | o detector de voz descarta inícios/finais fracos em fala rápida | proteger o intervalo do bruto + conferir cada emenda por transcrição em janela (motor de corte, `corte/`) |
| Pausa de 0,44 s que sobrou | intervalo protegido largo demais | encurtar o intervalo e cortar de novo |
| Título atrás da cabeça ilegível | cabeça alta no quadro | lettering no peito (L-4) |
| Leque de slides em cima da barra de progresso | tops coincidindo no SPLIT | leque desceu para `top` 600 |
| Legenda vazando na troca FULL → SPLIT (25,7 s) | a legenda acompanha o quadro encolhendo | esconder a legenda de `t − 0,05` a `t + 0,5` em toda troca (automático no gerador) |
| Varredura de zona segura acusando texto | legenda na transição | o mesmo esconder |
| Snapshot sem overlay nenhum | âncora de frase lançou erro (frase não existe) | abrir no navegador, ler o console, ancorar com mais contexto |
| Snapshot quebra com erro do postcss | `node_modules` corrompido | `npm ci` na raiz |
| Áudio a −25 LUFS | o render não normaliza | loudnorm em duas passadas (10.11) |
| Filtro do ffmpeg quebrado no zsh | `$var:l` é modificador do zsh | `${var}` |
| CAPTCHA no navegador headless | proteção anti-robô do site | navegador normal, sem burlar |
| Peça some no render | animação só de `scale`/`scaleX` | incluir `opacity` no destino |
| Lint reprova a animação | animar `left` | animar com `x` |
| Âncora pega a palavra errada | palavra repetida | mais contexto na frase ou n-ésima ocorrência |
| Seek lento / quadro errado no vídeo limpo | poucos keyframes | `clean.mp4` com keyframe a cada 1 s (`-g 30`) |

### 12.3 O mapa real da referência (38,8 s) — modelo de `map.md`

| Tempo | Fala | Câmera | Peça |
|---|---|---|---|
| 0,0–1,0 | "O Claude acabou de lançar" | FULL bruto | HUD de filmadora "NOVIDADE · CLAUDE" → glitch + boom |
| 1,0–2,1 | "três ferramentas de IA" | FULL, punch 1,14 | lettering no peito: 3 FERRAMENTAS / DE IA |
| 2,1–3,2 | "totalmente gratuitas" | FULL | flash + TOTALMENTE / GRATUITAS + pílula "Em todos os planos · até no Free" |
| 3,2–6,1 | "economizar centenas de dólares por ano" | SPLIT | painel: Gamma Pro R$ 840 → Canva Pro R$ 290 → total R$ 1.130 riscado → "Com o Claude R$ 0" + fonte dos preços |
| 6,2–8,1 | "Slides, Docs e Design" | SPLIT | 3 cards, cada um no nome falado |
| 8,1–10,6 | "ficam dentro do chat que você já utiliza" | light leak → FULL | pílula "Dentro do chat do Claude" |
| 10,6–11,9 | "E pra utilizar é muito fácil" | FULL, punch 1,16 | kicker "É muito fácil" (no peito) |
| 11,9–16,0 | "é só você pedir… apresentação comercial pro seu negócio" | SPLIT | chat + pedido digitando |
| 16,0–18,8 | "ele vai preparar todos os slides" | SPLIT | barra "Criando os slides" → leque de 3 slides |
| 18,8–23,9 | "slides prontos… exportar… PowerPoint ou Google Slides" | FULL | carimbo PRONTOS ✓ (no peito) → painel no peito: deck → seta desenhada → logos |
| 23,9–25,6 | "Mas a novidade não para só nos slides" | FULL, punch 1,2 | lettering NÃO PARA / SÓ NOS SLIDES |
| 25,6–32,9 | "mesma conversa… roteiro… carrosséis no Instagram" | SPLIT | novo pedido → quadro ROTEIRO recebe o doc → leque do carrossel + selo Instagram |
| 32,9–36,8 | "em vez de pagar pelo Gamma ou pelo Canva… tudo em uma única conversa" | FULL | pílulas riscadas GAMMA / CANVA → flash → TUDO EM / 1 CONVERSA |
| 36,8–38,8 | "Comenta SLIDES e eu te envio o link" | FULL | botão CTA com cursor + kicker "Link direto na sua DM" (no peito) |

O fluxo de escrita é sempre: **primeiro o mapa** (tempo × fala × câmera × peça), **depois** o código do
gerador, só com chamadas de peça — uma por linha do mapa.

### 12.4 O que ficou como padrão deste estilo (diferenças em relação à origem)
- filtro de cor e tintas nos valores aprovados (L-2);
- punch medido por vídeo (1,06 no enquadramento da referência);
- SFX a 0,4 e só em peças grandes (L-5);
- título atrás da cabeça desligado automaticamente com cabeça alta; lettering no peito (L-4);
- kicker e carimbo nunca sobre a cabeça: padrão no peito (L-3);
- legenda da boca escondida automaticamente em toda troca de layout;
- pesquisa de fatos e materiais como etapa obrigatória antes dos beats, com `SOURCES.md` e o gerador de
  ilustrações declaradas como peça do estilo;
- conferência automática das emendas (já no motor de corte, `corte/`);
- normalização de áudio como passo final do render;
- checagem do rosto nos snapshots;
- caminhos isolados por variável de ambiente;
- perguntar ou mostrar o mapa de beats antes de montar, quando o pedido não disser para ir direto.
- Fora do escopo deste estilo: o look claro e a parte de geração de vídeo por IA da origem (viram estilos à
  parte).

---

## 13 · Anexos

| Arquivo | O que mostra |
|---|---|
| `anexos/quadros-01.png` | prancha com 16 quadros do reel de referência aprovado: HUD de filmadora do gancho, lettering no peito (3 FERRAMENTAS / DE IA, TOTALMENTE / GRATUITAS), SPLITs com grade de cards, chat + pedido digitando, barra de progresso, quadro ROTEIRO e leque do carrossel, painel de exportar no peito, pílula "Dentro do chat do Claude", lettering NÃO PARA / SÓ NOS SLIDES e TUDO EM / 1 CONVERSA, e o botão de CTA |
| `anexos/cor-antes-depois.jpg` | o mesmo quadro com a grade de origem (agressiva, escura) × a grade aprovada (suave), e um SPLIT com o painel de preços ao lado — a referência visual da regra R4 neste estilo |

Ambas as imagens são renders do próprio projeto de referência (nenhum quadro de vídeo de terceiro).

## 14 · Motor, modelo e exemplo (o que está na pasta `modelo/`)

| Caminho | O que é |
|---|---|
| `modelo/README.md` | o passo a passo das fases 1 e 2 com este motor (o que o brief do agente manda seguir) |
| `modelo/kit/` | o motor da referência aprovada, intocado: `kit.js` (kit `K.*`), `kit.css` (temas e geometria), `index.template.html`, `fonts/`, `sfx/` (efeitos procedurais, sem licença de terceiros). O GSAP 3.14.2 vem do `npm` |
| `modelo/montar.mjs` | monta `index.html` a partir de `src/beats.js` + transcript + `vsl.json` + rastreio da boca + pele + som; `--so-camera` gera a base só-câmera |
| `modelo/preparar.sh` | câmera 9:16 com a voz, transcript, fontes e material do projeto, `npm install`, rastreio da boca, 1ª montagem |
| `modelo/vsl-padrao.json` | o `vsl.json` inicial de todo vídeo novo (cor e grade aprovadas; enquadramento a medir) |
| `modelo/beats-modelo.js` | o `beats.js` inicial: gramática, regras e receitas comentadas |
| `modelo/sfx-enxuto.js` | o filtro do modo enxuto (R2) |
| `modelo/package.json` | `hyperframes` 0.7.109 (a versão da referência), `gsap` 3.14.2, `playwright` |
| `modelo/ferramentas/` | `rastrear-boca.py`, `cards.mjs` (cards da fase 1), `sons.mjs` (`sons.json`), `audio-final-vsl.sh` (−14 LUFS, pico ≤ −1 dBTP), `folha.sh` (folha do final), `zona-segura-dom.mjs`, `ilustracoes/`, `gerar-sfx.mjs` |
| `modelo/exemplo/` | o reel aprovado completo (`LEIA.md`, `beats-exemplo.js`, mapa, fontes, imagens, `progresso-exemplo.md`, vídeo em 540p) |

**Teste de fidelidade (28/10/2026):** o exemplo remontado com `montar.mjs` gerou um `index.html` byte a byte igual ao
da referência. Em 18 quadros comparados, 17 saíram idênticos pixel a pixel e 1 com PSNR de 72 dB.
