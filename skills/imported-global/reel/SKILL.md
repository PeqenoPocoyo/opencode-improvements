---
name: reel
description: Edita um REEL / Short / vídeo vertical 9:16 do início ao fim, sem painel e sem escolhas — a pessoa manda a gravação bruta dela falando e a skill CORTA (tira silêncios, respirações, "éé", gaguejos, erros, retomadas e repetições, com o motor de corte pelo som aprovado em produção) e EDITA com o motor "VSL com interface animada" (o mesmo motor, kit e regras que produziram o reel de referência aprovado — câmera alternando tela cheia com punch-in e tela dividida, cada palavra-chave virando uma peça de interface que entra exatamente na palavra, legenda que segue a boca, efeitos sonoros enxutos, −14 LUFS). Entrega render/reel-v1.mp4 verificado e itera a pedido. Use SEMPRE que pedirem para "editar esse reel", "corta e edita", "faz o reel desse vídeo", "monta esse bruto", "edita esse vídeo pro Instagram", "limpa e edita", "faz a VSL", ou passarem um vídeo vertical/horizontal falado para virar reel rápido — mesmo sem citar a skill. NÃO é o estúdio de reels com painel e estilos (isso é outra skill), NÃO serve para vídeo longo do YouTube, showreel sem alguém falando, roteiro, copy ou carrossel.
---

# reel · corta e edita no motor VSL

Uma skill, dois motores, zero painel. A pessoa manda o vídeo; você corta com o **motor de corte**
(`corte/`) e edita com o **motor VSL** (`modelo/`, o kit intocado que produziu a referência aprovada), seguindo
as **regras da casa** (`regras-da-casa.md`, valem por cima de tudo) e o **ESTILO.md** (a espec do motor).
O resultado é o mesmo que o estúdio entregaria no estilo VSL com a pele nativa: mesmas cores, fontes, som e
regras. **Nunca publique nem envie o vídeo** (R9). **Nenhum nome de terceiro** no vídeo nem nos arquivos (R11).

Leia antes de começar (nesta ordem, inteiros): `regras-da-casa.md` → `corte/CORTE.md` → `ESTILO.md` →
`modelo/README.md` → `modelo/exemplo/LEIA.md`. Lição que paga a leitura: **o padrão de qualidade é o exemplo,
não um mínimo** (`modelo/exemplo/beats-exemplo.js` é a régua; cada vídeo tem o seu mapa).

## Mapa da skill
```
SKILL.md              este arquivo (o fluxo)
regras-da-casa.md     R1–R11: rosto nunca coberto, SFX com parcimônia, material real, nenhuma palavra comida, −14 LUFS…
ESTILO.md             a espec do motor VSL: layouts, enquadramento, movimento, legenda, peças, som, pipeline, aceite, lições
pele.json             os valores nativos (fontes, cinco cores, invariantes) — a pele da referência
corte/                motor de corte: CORTE.md (roteiro) · references/EDICAO-BRUTA.md (o porquê) · scripts/ · exemplo/
modelo/               motor VSL: kit/ (intocado) · montar.mjs · preparar.sh · ferramentas/ · exemplo/ (o reel aprovado) · README.md
ferramentas/          preparar.py · rosto.py · ancoras.py · verificar.py · zona-segura.py · recortar.py · audio-final.sh
anexos/               quadros da referência e o antes × depois da cor
```
`S=~/.claude/skills/reel` (ou `REEL_SKILL`). Variáveis de ambiente (R10): `WHISPER_MODEL`, `VSL_PYTHON`
(Python com mediapipe ou opencv), `FACE_MODEL`, `VSL_NODE_MODULES`, `CHROME`, `RVM_PYTHON` (só para matte).

## Fluxo (ordem fixa)

### 0 · Projeto
1. Crie **uma pasta por reel** ao lado do vídeo: `reel-<slug>/` com `corte/`, `render/`, `qa/`, `entrega/`,
   `assets/`. Nunca reaproveite outra edição; nunca escreva na pasta do bruto fora dela.
2. Primeira vez na máquina: `python3 $S/corte/scripts/0-checar.py` (ffmpeg, whisper-cli, numpy, modelo).
3. Diga em uma linha o que vai acontecer ("Cortando e editando no motor VSL; o v1 chega em alguns minutos")
   e avise antes de cada etapa lenta. Etapas longas rodam em segundo plano.

### 1 · Corte (motor de corte, `corte/CORTE.md` inteiro)
`B=$S/corte/scripts` · tudo em `corte/`:
```bash
python3 $B/1-tomadas.py "<bruto>" corte && cat corte/tomadas.txt      # LEIA inteiro antes de escolher
# escreva corte/keeps.json (regras dos keeps: a melhor tomada completa de cada frase; falsa largada fora)
python3 $B/2-vicios.py corte
python3 $B/3-corte.py "<bruto>" corte                                  # J/L de 4 quadros (o padrão do VSL)
python3 $B/4-conferir.py corte --prompt "<nomes próprios do vídeo>" && cat corte/conferencia.txt
```
Critério (R5): todos os blocos de `conferencia.txt` aprovados; **nenhuma palavra comida**; nenhuma pausa > 0,25 s.
Palavra comida → proteja o intervalo (`raw`/`force`) e corte de novo. Se a pessoa disser que o vídeo **já está
limpo**, pule: `cp "<vídeo>" corte/clean.mp4` e transcreva com `$S/ferramentas/preparar.py corte/clean.mp4 preparo`.
Sai: `corte/clean.mp4`, `corte.wav`, `edl.json`, `cortepalavras.json`.

### 2 · Motor VSL · preparo
```bash
cp -R "$S/modelo" motor && cd motor && bash preparar.sh
```
Faz a câmera 9:16 com a voz (`assets/clean.mp4`), o transcript no formato do kit, `npm install`, o rastreio da
boca e a 1ª montagem. Sem `pele-resolvida.json` a pele é a **nativa** (a da referência): não crie uma.

### 3 · Fase 1 · planta (`modelo/README.md`)
1. **Transcript** (R6): corrija `assets/transcript.json` à mão (Cloud → Claude, A → IA, nomes como a marca
   escreve, palavra-código do CTA em CAIXA ALTA); o original fica em `transcript-whisper.json`.
2. **Enquadramento**: `python3 $S/ferramentas/rosto.py assets/clean.mp4 ../preparo --916` e meça num quadro
   com o punch aplicado → `vsl.json` (`punch`, `face`, `head`, `fullPos`, `splitPos`; cor e grade **não** mudam).
   Menos de ~300 px livres acima da cabeça → nada no alto em FULL: lettering, kicker e carimbo no peito (R1).
3. **Material real** (R3): prints e logos oficiais em `assets/img/` + `../assets/SOURCES.md` (origem, licença,
   data); fato e preço com página oficial; tela sem print → ilustração declarada (`ferramentas/ilustracoes/`).
   Nunca invente logo, número ou print.
4. **Mapa → beats**: `assets/map.md` (tempo × fala × câmera × peça, como `exemplo/mapa.md`) e depois
   `src/beats.js`, uma chamada `K.*` por linha do mapa, tempos só por `K.at("frase exata")` (leia
   `exemplo/beats-exemplo.js` inteiro antes). Algo novo a cada 1,5–3 s; FULL ≈ SPLIT; `K.hideMouth` em toda
   troca e em todo lettering; `K.mouthCaps` por último.
5. `node montar.mjs && npx hyperframes lint` (0 erros; snapshot vazio = âncora quebrada, leia o console).
6. `../entrega/planta.json` (n, layout, de, ate, fala, tela) e `node ferramentas/cards.mjs` → `entrega/cards/P01.png…`.

**Portão:** por padrão **vá direto para a fase 2** — a pessoa pediu rapidez. Pare e mostre o mapa ou os cards só
se ela pedir ("me mostra antes") ou se houver dúvida de conteúdo que só ela resolve (fato, preço, nome).

### 4 · Fase 2 · render (`modelo/README.md`)
```bash
npx hyperframes snapshot --at <cada troca e cada beat> -o snapshots      # rosto livre (R1), nada cortado/sobreposto
node ferramentas/zona-segura-dom.mjs . --strict                           # "zona segura OK"
npx hyperframes render -q high -o ../render/_reel-bruto.mp4
node montar.mjs --so-camera && npx hyperframes render -q high -o ../render/_camera-so.mp4 && node montar.mjs
bash ferramentas/audio-final-vsl.sh ../render/_reel-bruto.mp4 ../render/reel-v1.mp4   # −14 LUFS ±0,3 · pico ≤ −1 dBTP
node ferramentas/sons.mjs && bash ferramentas/folha.sh ../render/reel-v1.mp4 ../qa/folha-final.png
python3 "$S/ferramentas/verificar.py" .. --video render/reel-v1.mp4 --sfx ../sons.json --camera ../render/_camera-so.mp4
```
Depois escreva `MINUTAGEM.md` (beat a beat: tempo, fala, o que aparece, layout, som) e `progresso.md` na pasta
do projeto. **Critique antes de mostrar:** `VERIFY.md` todo aprovado, folha de quadros, R1 (rosto), R2 (SFX ≤ 0,8/s
no modo enxuto), R6 (legenda), R7 (zona segura), R8 (áudio). Até 2 rodadas de ajuste antes de entregar.

### 5 · Entrega e iteração
Responda com: caminho do `reel-v1.mp4`, duração (bruto → corte → final), LUFS e pico, número de telas e de
efeitos, o que ficou de fora no corte e o que foi protegido, correções de legenda, fontes dos fatos, pontos
abertos. Ajuste pedido → `reel-v<N+1>.mp4` (versões anteriores ficam em `render/`); mudança de corte →
retranscreva e remapeie (`corte/scripts/remapear.py`), nunca recronometre à mão.

## Regras de condução
- **Os motores não se reescrevem.** `modelo/kit/` e `corte/scripts/` ficam intocados; cada vídeo escreve só
  `src/beats.js`, `vsl.json`, `keeps.json` e os ajustes. Um parâmetro do corte muda só pelo diagnóstico da
  seção 9 de `corte/references/EDICAO-BRUTA.md`, um de cada vez, registrado.
- **Uma versão por rodada**, completa e verificada.
- **Som enxuto** (`"sfxModo": "enxuto"`, o padrão do `vsl-padrao.json`): ≤ 0,8 efeito/s contando a digitação,
  digitação sempre contínua. O som exato da referência (`"referencia"`) só a pedido.
- **Material real** sempre; ilustração só declarada. **Rosto nunca coberto.** **Zona segura.**
- **Você produz** nesta sessão. Se a pessoa pedir um agente ou um modelo específico, lance um agente
  general-purpose com este SKILL.md + `ESTILO.md` + `modelo/README.md` como brief e critique a entrega.
- Falhou algo (ffmpeg, whisper, modelo, npm, Chrome)? Diga em uma linha o que fazer; `corte/scripts/0-checar.py`
  diagnostica a máquina.
