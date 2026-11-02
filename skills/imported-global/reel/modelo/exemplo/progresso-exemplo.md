# Progresso do reel de referência (aprovado) — o caminho que levou ao resultado

**Vídeo:** "3 ferramentas grátis do Claude". O bruto é horizontal, 2560×1440 e 40,9 s, num estúdio escuro com
luz colorida. O final tem 38,8 s em 1080×1920, a −14 LUFS. Telas: 15 beats, com FULL e SPLIT perto de 50/50,
sem PIP.

## 1 · Corte
Corte pelo som com J/L de 4 quadros. O corte comeu sílabas em fala rápida em cinco lugares: "economizar",
"pedir pra ele", "pro seu negócio", "um roteiro" e "carrosséis no". Cada um virou um intervalo protegido do
bruto, e o corte rodou de novo. Toda emenda foi conferida por transcrição em janela. Sobraram duas pausas
naturais (0,31 s e 0,29 s).

## 2 · Transcript (R6)
Correções feitas à mão:

| Whisper | Correto |
|---|---|
| Cloud | Claude |
| A | IA |
| Gama | Gamma |
| carrocéis | carrosséis |
| vim | envio |
| slides | SLIDES (a palavra-código do CTA) |

## 3 · Enquadramento
O rosto ocupa muito do quadro, então o punch base foi 1,06, não 1,22. `face`/`head` foram medidos num quadro com
o punch aplicado. O topo da cabeça fica quase no alto do quadro: o título atrás da cabeça ficou ilegível e virou
lettering no peito (`K.stack`, top 1150–1180) com `K.hideMouth` no mesmo intervalo.

## 4 · Material real (R3)
- **Fatos:** "grátis em todos os planos, até no Free" e "exporta para PowerPoint e Google Slides", ambos em páginas
  oficiais, com a data anotada.
- **Preços:** nas páginas oficiais de preço em pt-BR, plano anual (Gamma Pro R$ 840, Canva Pro R$ 290).
  - A página tinha anti-robô: lida num navegador normal, nunca burlada.
- **Logos:** do Wikimedia Commons. Marca sem logo livre entrou só como texto.
- **Telas do produto:** não havia captura oficial, então viraram ilustração em HTML próprio, com a empresa fictícia
  "Padaria Trigo & Mel" (slides, documento, canvas de design, carrossel), declarada no SOURCES.
- **Moedas:** a fala diz "centenas de dólares" e a tela mostra R$ 1.130/ano (≈ US$ 200). É coerente, e foi avisado.

## 5 · Mapa → beats
Ver `mapa.md` e `beats-exemplo.js`. A cada fala, a peça que mostra a ideia:
- **Gancho:** HUD "NOVIDADE · CLAUDE" → glitch.
- **Preço:** painel com as linhas reveladas na palavra, o total riscado e "Com o Claude R$ 0".
- **Lista:** 3 cards, cada um no nome falado.
- **Pedido:** chat + pedido digitando → barra "Criando os slides" → leque de slides.
- **Exportar:** painel no peito com seta desenhada e logos.
- **Virada:** lettering no peito.
- **Antigo × novo:** pílulas riscadas → flash → "TUDO EM 1 CONVERSA".
- **CTA:** botão com cursor.

A legenda segue a boca, com as palavras-chave em `accent`.

## 6 · Verificação
- O lint saiu com 0 erros, e os snapshots foram tirados em cada beat e em cada troca de câmera.
- Snapshots corrigidos no caminho:
  - o leque de slides estava sobre a barra de progresso e desceu para top 600;
  - a legenda vazava na troca FULL→SPLIT aos 25,7 s, e entrou `K.hideMouth(t − 0.05, t + 0.5)`.
- A zona segura foi varrida a cada 0,25 s e saiu OK.
- O render saiu a −25 LUFS. A normalização em duas passadas levou a −14 LUFS, com pico −0,6 dBFS.

## 7 · A correção que tornou o resultado "aprovado"
A primeira versão tinha a grade de cor da origem, que ficou muito agressiva e escura no rosto: contraste 1,2,
brilho 0,8, tinta 0,85/0,55. A versão aprovada usa `saturate(1.04) contrast(1.05) brightness(0.97)` com tinta
0,3/0,25. O roxo ficou nas telas e nos brilhos; o rosto ficou natural.
