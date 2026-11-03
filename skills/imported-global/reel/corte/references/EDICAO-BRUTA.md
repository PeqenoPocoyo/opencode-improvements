# Edição Bruta

**Módulo 1 do pipeline de edição**
*Versão 1.1 · 27/10/2026 · Status: aprovado em produção · Skill: `~/.claude/skills/reel` (pasta `corte/`)*

> Este documento é **autossuficiente**. Quem o lê (pessoa ou agente) precisa conseguir cortar um vídeo bruto
> com a mesma qualidade da v2 aprovada sem ter visto a conversa que o originou. É a referência completa da skill
> `reel`, pasta `corte/` (o `CORTE.md` é o roteiro curto; este documento é o porquê). Por isso explica não só **o que
> fazer**, mas também **por que** cada regra existe e **como decidir** quando a regra não cobre o caso.
>
> **Fonte oficial:** este arquivo dentro da skill. Ajustes são feitos aqui e registrados na seção 16.

---

## Sumário

0. [Onde este módulo entra no processo](#0--onde-este-módulo-entra-no-processo)
1. [Glossário](#1--glossário)
2. [Princípios](#2--princípios-o-que-faz-o-resultado-ficar-bom)
3. [Pré-requisitos e instalação](#3--pré-requisitos)
4. [O fluxo, passo a passo](#4--o-fluxo-passo-a-passo)
5. [Como escolher as tomadas: o raciocínio editorial](#5--como-escolher-as-tomadas-o-raciocínio-editorial)
6. [O motor de corte por dentro](#6--o-motor-de-corte-por-dentro)
7. [Conferência e critérios de aceite](#7--conferência-e-critérios-de-aceite)
8. [Contrato de saída: o que o módulo entrega para os estilos](#8--contrato-de-saída-o-que-o-módulo-entrega-para-os-estilos)
9. [Diagnóstico: sintoma → causa → ajuste](#9--diagnóstico-sintoma--causa--ajuste)
10. [Armadilhas do Whisper](#10--armadilhas-do-whisper)
11. [Exemplo comentado: a decupagem da v2](#11--exemplo-comentado-a-decupagem-da-v2)
12. [Histórico: o que deu errado na v1 e virou regra](#12--histórico-o-que-deu-errado-na-v1-e-virou-regra)
13. [Instruções para o agente](#13--instruções-para-o-agente-futura-skill)
14. [Do pacote que não entrou (opcional)](#14--do-pacote-que-não-entrou-opcional)
15. [Arquivos e origem](#15--arquivos-e-origem)
16. [Limites conhecidos e próximos passos](#16--limites-conhecidos-e-próximos-passos)

---

## 0 · Onde este módulo entra no processo

```
 BRUTO (gravação com erros, retomadas, pausas)
   │
   ▼
 ┌──────────────────────────────────────────┐
 │ MÓDULO 1 · EDIÇÃO BRUTA (este documento) │  → fala limpa + mapa de tempos
 └──────────────────────────────────────────┘
   │   clean.mp4 · corte.wav · edl.json · cortepalavras.json
   ▼
 ┌──────────────────────────────────────────┐
 │ MÓDULO 2 · ESTILO DE EDIÇÃO 1 / 2 / 3     │  → enquadramento, legendas, imagens, zoom, efeitos, trilha
 │ (a pessoa escolhe o estilo)              │
 └──────────────────────────────────────────┘
   │
   ▼
 VÍDEO FINAL
```

**Responsabilidade deste módulo:** decidir **qual fala fica** e **onde exatamente** cada trecho começa e
termina. Mais nada.

**Fora deste módulo:** formato (9:16, 16:9), recorte de câmera, legendas desenhadas, imagens, zoom, trilha,
efeitos sonoros e correção de cor. Isso é responsabilidade dos estilos.

**Regra de fronteira:** depois deste módulo, **nenhum estilo volta ao bruto para escolher fala**. Se um estilo
precisa de outro corte, ele pede uma nova rodada deste módulo e remapeia seus tempos (seção 4, passo 5).

---

## 1 · Glossário

| Termo | Significado |
|---|---|
| **Bruto** | A gravação original, sem cortes. É a fonte de todos os tempos "da fonte". |
| **Tomada** | Cada vez que uma frase foi dita. Uma frase pode ter de 1 a 4 tomadas no bruto. |
| **Retomada** | Uma tomada repetida porque a anterior não ficou boa. |
| **Falsa largada** | Uma tomada que começa e é abandonada, às vezes numa palavra só ("Então..."). |
| **Frase abandonada** | Uma tomada que começa bem e para no meio ("É só você pedir..."). |
| **Vício (de fala)** | Hesitação sem conteúdo: "éé", "ããã", "hum", "eh", ou uma conjunção esticada ("eeee"). |
| **Keep** | Um trecho do bruto escolhido para ficar (`from`/`to` em segundos da fonte). É a decisão editorial. |
| **Trecho** | Pedaço contínuo de áudio que o motor mantém. Um keep vira 1 ou mais trechos, porque as pausas internas também saem. |
| **Emenda** | O ponto onde dois trechos se encontram no corte final. |
| **Vale (de energia)** | O instante mais silencioso perto de um ponto de corte. Cortar no vale não corta palavra. |
| **Tilt (inclinação espectral)** | Quanto a energia grave (80–900 Hz) supera a aguda (2–7 kHz), em dB. Voz tem tilt alto; respiração e "sss" têm tilt baixo ou negativo. |
| **p90 da fala** | O volume abaixo do qual ficam 90 % dos quadros com som. Mede o "nível de gravação" da voz. |
| **LEAD / TAIL** | A margem mantida antes do primeiro som (0,06 s) e depois do último (0,14 s) de cada trecho. |
| **HOLE** | O tamanho máximo de silêncio que **fica** dentro de uma frase (0,20 s). Silêncio maior sai. |
| **ISLAND** | O tamanho mínimo de um som para contar como fala (0,07 s). Estalos menores são descartados. |
| **Corte J / L** | No corte J, o som da próxima frase entra antes da imagem: a imagem antiga segue alguns quadros. No corte L, a imagem da próxima frase chega antes do som. Deixa a emenda menos seca. |
| **EDL** | *Edit decision list*: a lista de trechos com o tempo na fonte e no corte (`edl.json`). |
| **Tempo da fonte / tempo do corte** | Segundos contados no bruto vs. segundos contados no vídeo cortado. **Nunca misture os dois.** |

---

## 2 · Princípios (o que faz o resultado ficar bom)

1. **Quem decide o que fica é você, lendo; quem decide onde cortar é o som.**
   A escolha das tomadas é editorial, feita lendo o texto real de cada trecho. O ponto exato do corte é medido
   no áudio (volume, timbre e vale). O tempo de palavra do Whisper **nunca** é ponto de corte: ele chega
   deslocado em décimos de segundo e, em silêncio longo, chega inventado.

2. **Uma frase, uma tomada: a melhor completa.**
   Toda retomada, falsa largada, frase abandonada, "alô, alô", tosse e teste sai. Entre as tomadas completas,
   a padrão é a mais recente, salvo quando ela é mais longa ou tem muleta e outra está igualmente completa e
   mais enxuta (seção 5).

3. **Falsa largada de uma palavra também é retomada.**
   Foi o erro da v1: um "Então..." abortado ficou colado no "Então, ao invés de..." seguinte. O keep começa
   **na palavra que vale**.

4. **A transcrição longa esconde repetições. A conferência transcreve cada emenda sozinha.**
   O Whisper leu "Então... Então, ao invés de" como um "Então" só. Por isso a conferência trata as emendas
   uma a uma e procura repetições automaticamente.

5. **Respiração não é fala. Pausa boa tem até 0,2 s.**
   O detector usa volume **e** timbre. Com limiar só de volume, a respiração passa como fala e a pausa fica
   longa (outro erro da v1).

6. **Informação certa acima de tomada inteira.**
   Pode montar uma fala com pedaços de tomadas diferentes, desde que cada pedaço comece e termine em fim de
   frase. Quando tomadas diferentes dizem coisas diferentes, escolha a que passa a informação correta e, se
   houver dúvida, pergunte a quem gravou.

7. **O corte não pode soar cortado.**
   Fade de 8/12 ms em cada trecho (sem estalo), borda no vale, LEAD/TAIL para não comer sílaba e J/L nas
   emendas.

8. **Nada é entregue sem a conferência do passo 4 lida inteira.**

---

## 3 · Pré-requisitos

Validado num Mac M5 (macOS) com:

| Ferramenta | Onde | Para quê |
|---|---|---|
| `ffmpeg` 8.x | `/opt/homebrew/bin/ffmpeg` | extrair áudio, cortar, codificar |
| `whisper-cli` (whisper.cpp) | `/opt/homebrew/bin/whisper-cli` | transcrição local, roda na GPU (Metal) |
| Modelo `large-v3-turbo` | `~/.cache/whisper-cpp/ggml-large-v3-turbo.bin` (1,6 GB) | melhor equilíbrio entre precisão e velocidade em PT-BR |
| Python com numpy | `/usr/bin/python3` (3.9, numpy 2.0) | análise de áudio e o motor |

Para trocar o modelo, defina `WHISPER_MODEL=/caminho/do/modelo.bin` antes de rodar.

**Em outra máquina, rode primeiro `python3 scripts/0-checar.py`.** Ele confere ffmpeg, whisper-cli, numpy e o
modelo, e diz como instalar o que faltar:

- **Mac:** `brew install ffmpeg whisper-cpp` · `pip3 install numpy`.
- **Windows:** `winget install Gyan.FFmpeg`; o whisper.cpp vem do zip `whisper-bin-x64` das releases do
  github.com/ggml-org/whisper.cpp (ponha a pasta no PATH); `python -m pip install numpy`. Rode os scripts com
  `PYTHONUTF8=1` e `python` no lugar de `python3`.
- **Modelo:** `ggml-large-v3-turbo.bin` (1,6 GB), de huggingface.co/ggerganov/whisper.cpp, em
  `~/.cache/whisper-cpp/`. Outro modelo funciona (`medium`, `large-v3`): o alinhamento de tempo é escolhido
  pelo nome do arquivo. Em PC lento, o `medium` é aceitável para o passo 1; a precisão das emendas cai um pouco.
- **Sem Mac**, o encoder do `clean.mp4` é o `libx264` (mais lento, mesma qualidade).

---

## 4 · O fluxo, passo a passo

Todos os comandos rodam na pasta dos scripts. `PASTA` é uma pasta de trabalho, **uma por vídeo**
(ex.: `cortes/2026-11-03-reel-x`, ao lado do bruto). O script cria a pasta se ela não existir.

```bash
cd ~/.claude/skills/reel/corte/scripts
python3 0-checar.py            # só na primeira vez em cada máquina
```

### Passo 1 · Mapa de tomadas

```bash
python3 1-tomadas.py "/caminho/do/bruto.mp4" PASTA
```

**O que faz.** O script extrai o áudio em 16 kHz mono (`audio16k.wav`) e mede o volume a cada 10 ms. Marca
como "som" tudo que passa do piso de ruído da sala + 18 dB (o piso é o volume abaixo do qual ficam 10 % dos
quadros) e junta buracos menores que 0,15 s. Depois transcreve **cada trecho sozinho**, com 0,15 s de folga
de cada lado.

**Saídas.** `tomadas.txt`, para ler, e `tomadas.json` (`[{from, to, texto}]`).

**Por que não transcrever o vídeo inteiro de uma vez.** Num bruto com retomadas há silêncios longos, e nesses
silêncios o Whisper **inventa fala**, em geral repetindo a frase anterior. Os tempos também saem errados. No
bruto da v2 ele produziu 8 s de texto num trecho sem som algum. Transcrever trecho a trecho elimina isso e
mostra cada retomada separada.

**Como ler.** Cada linha é `início-fim (duração) :: texto`. Retomadas aparecem como linhas parecidas em
sequência. Falsas largadas aparecem como linhas curtas terminando em "...". Exemplo real:

```
 141.33- 141.94 ( 0.6s) :: Então...                                   ← falsa largada: fica FORA
 142.77- 147.11 ( 4.3s) :: Então, ao invés de você pagar pelo Gama...  ← tomada que vale
```

### Passo 2 · Escolher os keeps

É o único passo de julgamento. As regras completas estão na seção 5. Escreva `PASTA/keeps.json`:

```json
{"keeps": [
  {"from": 5.80,   "to": 12.15,  "why": "gancho (tomada única)"},
  {"from": 142.80, "to": 149.50, "why": "Gamma/Canva + CTA (pula a falsa largada 'Então...' de 141,3)"}
]}
```

| Campo | Obrigatório | Significado |
|---|---|---|
| `from`, `to` | sim | segundos **da fonte**, com folga de 0,1 a 0,2 s em volta do texto. O motor encosta no vale. |
| `why` | recomendado | qual tomada é e o que foi pulado. Vai para o relatório. |
| `raw` | não | `true` = mantém o trecho exatamente como está, sem detector (ver seção 5.4). |

A ordem dos keeps no arquivo é a ordem no vídeo final. Normalmente segue a ordem da fonte, mas não precisa.

Depois, rode a transcrição que mostra os vícios, só dentro dos keeps:

```bash
python3 2-vicios.py PASTA
```

O script transcreve cada keep palavra a palavra, com um prompt cheio de "éé, ããã, hum, né", e grava
`vicios/k{i}.json` (tempos da fonte). Com esse prompt o Whisper **escreve** as hesitações em vez de apagá-las,
e o motor consegue removê-las. Leia a saída: um "éé" no meio de uma frase boa aparece aqui.

### Passo 3 · O motor de corte

```bash
python3 3-corte.py "/caminho/do/bruto.mp4" PASTA
# opções: --jl 4 (padrão; 0 desliga, 6 fica mais suave) · --sem-video (só áudio + edl, mais rápido)
```

O funcionamento interno está na seção 6. **Saídas:** `edl.json`, `corte.wav`, `corte16k.wav`,
`vicios-removidos.txt` e `clean.mp4`. Na tela aparecem o nível medido da fala, os limiares usados, quantos
vícios saíram, quantos trechos ficaram, em quantas emendas entrou J/L e a duração final.

Ajustes finos sem mexer em código, em `PASTA/ajustes.json` (tempos **da fonte**):

```json
{"cut": [[143.10, 143.40]], "keep": [88.5], "force": [[60.2, 60.4]]}
```

- `cut`: força a saída de um trecho (um "né" que o Whisper não escreveu, um estalo de boca).
- `keep`: protege um vício detectado que deve ficar (uma hesitação que faz parte da piada).
- `force`: mantém um som que não é voz e o detector descartaria (estalo de dedo, palma).

### Passo 4 · Conferência

```bash
python3 4-conferir.py PASTA --prompt "Claude, Slides, Docs, Design, PowerPoint, Gamma, Canva"
# --prompt: nomes próprios DESTE vídeo (o padrão é genérico: Claude, Claude Code, IA, ChatGPT, Instagram, YouTube)
```

Os critérios de aceite estão na seção 7. A saída fica em `conferencia.txt` e `cortepalavras.json`. Se
algo falhar, ajuste `keeps.json`/`ajustes.json`, volte ao passo 3 e confira de novo.

### Passo 5 (só se a edição já existia) · Remapear

Se legendas, cards, zooms ou efeitos já foram cronometrados num corte anterior e o corte mudou, **não
recronometre à mão**:

```python
import os, sys; sys.path.insert(0, os.path.expanduser("~/.claude/skills/reel/corte/scripts"))
from remapear import Mapa
m = Mapa("corte-antigo/cortepalavras.json", "corte-novo/cortepalavras.json")
m.novo(2.73)    # tempo antigo → novo  (2.62 na v2)
m.velho(2.62)   # tempo novo → antigo  (use este para renderizar quadro a quadro no tempo novo)
```

O script alinha as palavras em comum dos dois cortes e interpola entre elas. Um elemento cronometrado na
palavra X continua na palavra X. Foi assim que a v2 manteve toda a edição visual da v1.

---

## 5 · Como escolher as tomadas: o raciocínio editorial

### 5.1 · Para cada frase do roteiro

1. Liste no `tomadas.txt` todas as tomadas daquela frase.
2. Descarte as **incompletas**: as que terminam em "...", param no meio ou perdem um pedaço da ideia.
3. Descarte as que têm **tropeço audível**: palavra trocada ("você pode para ele escrever"), gagueira,
   palavra repetida.
4. Entre as que sobraram, a **padrão é a mais recente**: em geral quem grava repete até sair bom.
5. **Exceção:** se a mais recente for mais longa, tiver muleta ("a partir daí, então", "por exemplo" sobrando)
   ou soar mais arrastada, e outra for igualmente completa e mais enxuta, fique com a enxuta. Reel premia
   densidade.
6. **Se tomadas diferentes dizem coisas diferentes** (quem gravou mudou o conteúdo de uma tomada para outra),
   escolha pela **informação correta**. Se não der para saber qual é a correta, **pergunte** a quem gravou.

### 5.2 · Juntar pedaços de tomadas diferentes

Pode, quando:
- cada pedaço começa e termina em **fim de frase ou de oração** (nunca no meio de uma palavra ou de um
  sintagma);
- a entonação do fim do primeiro pedaço combina com o começo do segundo (uma frase que termina descendo
  seguida de uma que começa nova);
- o resultado fica mais correto ou mais enxuto do que qualquer tomada inteira.

Exemplo da v2: "...escreva um documento de uma página." (tomada de 86 s) + "Ele pode até criar carrosséis no
Instagram pra acompanhar esse material." (tomada de 121 s). Assim cada ferramenta ficou com o exemplo certo.

### 5.3 · Bordas do keep

- Dê **0,1 a 0,2 s de folga** antes da primeira e depois da última palavra. O motor procura o vale para fora
  do texto, então folga demais não estraga.
- A folga **não pode alcançar a tomada vizinha**. Se duas tomadas estão a menos de 1 s uma da outra (caso do
  "Então..." a 0,9 s do "Então" bom), o `from` vai **colado** no início da tomada boa.
- O tempo que aparece no `tomadas.txt` é o início do trecho com folga. Para achar o início exato da palavra,
  veja `vicios/k{i}.json` (tempo de palavra) e, na dúvida, o volume em `audio16k.wav`.

### 5.4 · Palavra fraca no começo

O tempo de início das palavras do Whisper costuma vir **atrasado**, e uma palavra soprada ("Se", "E" fraco)
pode ficar abaixo do limiar do detector. Se a conferência mostrar a primeira sílaba comida:
1. adiante o `from` desse keep em 0,1 a 0,2 s; ou
2. marque o keep com `"raw": true` (entra exatamente como está, sem detector); ou
3. use `force` em `ajustes.json` só para aquele pedaço.

### 5.5 · O que sempre sai

"Alô, alô", testes de som, tosse, pigarro, "deixa eu refazer", comentários fora do roteiro, risada que não
faz parte do conteúdo, falsas largadas e frases abandonadas.

---

## 6 · O motor de corte por dentro

Esta seção explica cada decisão do `3-corte.py`, para que ele possa ser ajustado com segurança.

### 6.1 · Análise do som

- O áudio é lido em 16 kHz mono e dividido em **quadros de 10 ms** (`HOP 160`), cada um analisado numa
  **janela de 30 ms** (`WIN 480`) com Hann.
- Por quadro, o motor calcula:
  - **volume** em dB (RMS);
  - **tilt** = energia de 80–900 Hz ÷ energia de 2–7 kHz, em dB.

### 6.2 · O que é fala

```
fala = (volume > T1  E  tilt > 12 dB)   OU   (volume > T2  E  tilt > 0 dB)
```

- A primeira condição pega a **voz normal**: volume moderado e dominância grave.
- A segunda pega **consoantes fortes** ("s", "x", "ch"): mais agudas, mas altas.
- **Respiração** é aguda e baixa, então falha nas duas e sai. Ruído de sala é baixo, então também sai.

**Calibração pelo nível da gravação.** O pacote original usa T1 = −33 dB e T2 = −26 dB fixos, o que só
funciona se a voz estiver gravada num certo nível. Aqui o motor mede o **p90 da fala** e desloca os dois
limiares para que esse p90 equivalha a −20 dB:

```
REF_DB = −20 ;  OFF = p90 − REF_DB ;  T1 = −33 + OFF ;  T2 = −26 + OFF
```

`REF_DB` é a constante no topo de `3-corte.py`. **Quanto menor o `REF_DB`, mais altos os limiares**, e mais o
motor corta (−22 corta mais que −20; −18 corta menos).

Na v2, p90 = −24,5 dB, OFF = −4,5, T1 = −37,5 dB e T2 = −30,5 dB.
*A referência de −20 dB é uma escolha nossa (o pacote não declara o nível esperado) e foi validada neste
vídeo. Se uma gravação muito diferente der problema, este é o primeiro número a revisar (seção 9).*

### 6.3 · Vícios

Lidos de `vicios/k*.json`:
- **Hesitação pura** ("aa", "ee", "eh", "ah", "hum", "hm", "uh", "umm", "mm", ou qualquer palavra feita de uma
  letra só repetida): o intervalo inteiro vira silêncio.
- **Conjunção esticada** ("e", "a", "um", "o" com duração entre 0,45 e 1,6 s): ficam os primeiros 0,14 s e o
  resto do "eeee" sai.
- Acima de 1,6 s, o motor não corta sozinho: é retomada ou pausa longa, e a decisão é editorial (keep ou
  `ajustes.cut`).
- Tudo que saiu fica listado em `vicios-removidos.txt`.

### 6.4 · De quadros a trechos

| Regra | Valor | Por quê |
|---|---|---|
| Buracos menores que `HOLE` dentro da fala **ficam** | 0,20 s | é o respiro natural entre palavras; tirar deixa a fala robótica |
| Buraco criado pela remoção de um vício **não** é fechado | — | senão o vício voltaria |
| Ilhas de "fala" menores que `ISLAND` saem | 0,07 s | estalos de boca, clique de mouse |
| `LEAD` antes do primeiro quadro de fala | 0,06 s | protege o ataque da palavra |
| `TAIL` depois do último quadro de fala | 0,14 s | protege o "s" e as vogais finais, que decaem devagar |
| Bordas do keep → vale de energia | início: 0,15 s para trás e 0,03 s para frente · fim: 0,03 s para trás e 0,15 s para frente | o corte cai no silêncio, procurando para fora do texto |
| Trechos a menos de 0,08 s um do outro se fundem | 0,08 s | evita microcortes |
| Início e fim arredondados para o quadro de 30 fps | 1/30 s | imagem e som cortam no mesmo quadro |
| Trechos com menos de 2 quadros saem | 0,067 s | sobras sem conteúdo |

### 6.5 · Áudio

- Lido em **48 kHz estéreo** do bruto (qualidade cheia, não os 16 kHz da análise).
- **Fade de 8 ms na entrada e 12 ms na saída** de cada trecho: elimina o estalo da emenda sem ser audível
  como fade.
- O motor **não** aplica compressão, equalização nem normalização. Isso fica a cargo do estilo (a v2 usou
  passa-alta de 70 Hz, compressor 3:1 e loudnorm −14 LUFS).

### 6.6 · Cortes J/L

- Só entram em **emendas reais**, onde saiu pelo menos 0,25 s entre um trecho e outro.
- Alternam: J, L, J, L... O deslocamento é de `--jl` quadros (padrão 4 = 0,133 s).
- **J** (`vshift` positivo): a imagem do trecho anterior continua 4 quadros depois que o som do próximo
  começou.
- **L** (`vshift` negativo): a imagem do próximo trecho aparece 4 quadros antes do som dele.
- Efeito: a emenda soa e parece natural, como numa conversa real, em vez de "pular" seco.
- Para desligar: `--jl 0`. Para deixar mais perceptível e suave: `--jl 6`.

### 6.7 · Vídeo

- O `clean.mp4` sai no **enquadramento original do bruto** (sem recorte; o recorte é do estilo), a 30 fps,
  com keyframe a cada 1 s (`-g 30`). Sem keyframe frequente, renderizadores que pulam no tempo congelam
  quadros.
- Encoder: `h264_videotoolbox` a 16 Mb/s (rápido no Mac); se falhar, `libx264 -crf 18`.

---

## 7 · Conferência e critérios de aceite

O `4-conferir.py` gera quatro blocos. Para **aceitar** o corte, todos precisam passar:

| Bloco | O que é | Critério de aceite |
|---|---|---|
| **Texto do corte** | transcrição inteira, palavra a palavra | Lido do começo ao fim. Toda frase do roteiro presente uma vez só, nenhuma palavra comida, nenhum verbo faltando. Erros de **nome** do Whisper ("Cláudio") não reprovam: são corrigidos na legenda. |
| **Repetições coladas** | a mesma palavra ou expressão (de 1 a 4 palavras) duas vezes seguidas | "nenhuma". Uma repetição intencional ("muito, muito fácil") pode ficar, desde que registrada no relatório. |
| **Emendas** | cada ponto de corte transcrito sozinho numa janela de ±2 s, **sem prompt** | Todas legíveis e coerentes: sem meia palavra, sem retomada murmurada, sem palavra duplicada. |
| **Pausas** | silêncios acima de 0,25 s (abaixo de −38 dB) | "nenhuma". |

**Atenção às janelas.** A janela de uma emenda às vezes mostra o texto começando no meio (o Whisper engole o
começo de recortes curtos). Isso **não** é defeito do corte. Confirme na janela vizinha ou no texto inteiro.
Uma palavra que some em **todos** os lugares é defeito.

**Teste final de ouvido.** A conferência automática não substitui assistir ao `clean.mp4` uma vez. A
sincronia de boca e a naturalidade das emendas só se validam vendo.

Resultado da v2: nenhuma repetição, nenhuma pausa, 12 emendas legíveis, 38,77 s.

---

## 8 · Contrato de saída: o que o módulo entrega para os estilos

Tudo fica dentro de `PASTA/`. **Todo estilo consome apenas estes arquivos.**

| Arquivo | Formato | Tempo | Uso no estilo |
|---|---|---|---|
| `clean.mp4` | H.264 30 fps, enquadramento original, com áudio do corte e J/L aplicado | corte | base visual pronta, para estilos que só sobrepõem elementos |
| `corte.wav` | 48 kHz estéreo, sem tratamento | corte | trilha de voz: o estilo aplica EQ, compressão e loudness |
| `corte16k.wav` | 16 kHz mono | corte | transcrição e análise |
| `edl.json` | lista de trechos (abaixo) | fonte ↔ corte | para quem precisa voltar ao bruto em resolução cheia (ex.: recortar 9:16 do 2560×1440 original sem perda) |
| `cortepalavras.json` | `[[início, fim, "palavra"], ...]` | corte | legendas e sincronia de elementos com palavras |
| `keeps.json`, `tomadas.txt`, `conferencia.txt`, `vicios-removidos.txt` | texto/JSON | fonte | auditoria e relatório |

**Formato do `edl.json`:**

```json
[
 {"src": 6.0,   "dur": 6.1333, "out": 0.0,  "nf": 184, "vshift": 0.0},
 {"src": 12.37, "dur": 1.2,    "out": 6.1333, "nf": 36, "vshift": 0.0},
 {"src": 13.87, "dur": 3.5667, "out": 7.3333, "nf": 107, "vshift": 0.1333}
]
```

| Campo | Significado |
|---|---|
| `src` | início do trecho **no bruto** (s) |
| `dur` | duração do trecho (s), múltiplo exato de 1/30 |
| `out` | início do trecho **no corte** (s) |
| `nf` | duração em quadros de 30 fps |
| `vshift` | deslocamento do corte de **imagem** entre o trecho anterior e este (+ = J, − = L, 0 = corte reto) |

**Como um estilo calcula, para um instante `T` do corte, qual quadro do bruto mostrar e qual áudio tocar:**

```
áudio:  trecho i com out_i ≤ T < out_i + dur_i     →  fonte = src_i + (T − out_i)
imagem: VSTART_0 = 0 ;  VSTART_j = out_j + vshift_j
        trecho j com VSTART_j ≤ T < VSTART_{j+1}  →  fonte = src_j + (T − out_j)
```

(Foi exatamente assim que o renderizador da v2 leu o bruto em 2560×1440 para recortar o 9:16.)

**Legendas:** `cortepalavras.json` vem do Whisper como está. O estilo aplica as correções de nome
(seção 10) e decide como agrupar e exibir as palavras.

---

## 9 · Diagnóstico: sintoma → causa → ajuste

| Sintoma na conferência / no ouvido | Causa provável | Ajuste |
|---|---|---|
| Frase dobrada ou "então então" | keep pegou uma falsa largada ou duas tomadas | mover `from`/`to`; separar em dois keeps |
| Primeira sílaba comida | palavra soprada abaixo do limiar, ou `from` atrasado | adiantar `from` 0,1–0,2 s; `"raw": true`; `force` |
| Final da palavra cortado ("slide" em vez de "slides") | TAIL curto para essa voz, ou keep `to` curto | estender `to`; subir `TAIL` para 0,18 |
| Respiração audível entre frases | limiares baixos demais para essa gravação | conferir o p90 impresso; `REF_DB` de −20 para −22 (limiares sobem 2 dB) |
| Palavras inteiras sumindo em trechos baixos | limiares altos demais (voz baixa, microfone longe) | `REF_DB` de −20 para −18 (limiares descem 2 dB); `force` no trecho |
| Fala soando "metralhadora", sem respiro | `HOLE` pequeno | subir `HOLE` para 0,25 |
| Pausas ainda perceptíveis | `HOLE` grande, ou silêncio com ruído alto (ar-condicionado) | baixar `HOLE` para 0,15; conferir se o ruído não passa como fala |
| "éé" que ficou | o Whisper não escreveu o vício | `ajustes.cut` com o intervalo |
| Hesitação que deveria ficar foi cortada | vício detectado em contexto intencional | `ajustes.keep` com o início dela |
| Estalo na emenda | corte fora do vale | conferir se a borda do keep não está dentro de palavra; folga maior |
| Emenda parecendo "pulo" de imagem | J/L desligado ou pequeno | `--jl 4` ou `--jl 6` |
| Boca fora de sincronia perto da emenda | J/L grande demais para aquele trecho | `--jl 2` ou `--jl 0` |

Os parâmetros `HOLE`, `ISLAND`, `LEAD`, `TAIL` e `REF_DB` ficam no topo de `3-corte.py`.
**Mude um por vez** e registre a mudança na seção 16.

---

## 10 · Armadilhas do Whisper

Todas aconteceram neste vídeo.

| Armadilha | Como aparece | O que fazer |
|---|---|---|
| **Inventa fala em silêncio longo** | repete a frase anterior dentro de um silêncio de 8 s | mapear tomadas pela energia e transcrever trecho a trecho (passo 1) |
| **Tempos de palavra errados** | várias palavras com o mesmo tempo; sequências "esticadas" | nunca cortar pelo tempo de palavra; cortar pelo som (passo 3) |
| **Esconde repetição** | "Então... Então, ao invés" vira um "Então" só | emendas sozinhas + caça a repetições (passo 4) |
| **Engole o começo de recorte curto** | a janela da emenda começa no meio da frase | janela de ±2 s; confirmar na janela vizinha ou no texto inteiro |
| **Prompt de vícios em janela curta inventa vícios** | aparece "é, ah, hum, é..." onde não há nada | prompt de vícios só nos keeps (passo 2); emendas **sem** prompt |
| **Pula uma frase na transcrição longa** | "Ele pode até criar" sumiu da transcrição do arquivo final | transcrever só aquela janela antes de concluir. A frase estava no áudio |
| **Erra nomes** | ver tabela abaixo | corrigir na legenda; `--prompt` com os nomes próprios ajuda |

**Correções de nome já vistas (aplicar na legenda):**

| Whisper escreve | Correto |
|---|---|
| Cláudio, Cloud, Claudio | **Claude** |
| de A (em "ferramentas de A") | **de IA** |
| Gama, ganho | **Gamma** |
| Câmbio, Can | **Canva** |
| te vi um link / tive um link | **te envio um link** |
| Designs, designing | **Design** |

---

## 11 · Exemplo comentado: a decupagem da v2

**Bruto:** gravação de exemplo de 2min33, HEVC 2560×1440, 23,976 fps, o apresentador
falando para a câmera, várias tomadas por frase.
**Resultado:** 38,77 s, 13 trechos, 6 emendas com J/L, nenhum vício, nenhuma pausa acima de 0,21 s.
Arquivos em `exemplo/`.

### Decisão frase a frase

| # | Frase | Tomadas no bruto (s) | Escolhida | Por quê |
|---|---|---|---|---|
| — | "Alô, alô" | 0,95 | **fora** | teste de som |
| 1 | Gancho: "O Claude acabou de lançar três ferramentas de IA totalmente gratuitas…" | 5,81 | 5,80–12,15 | tomada única e completa |
| 2 | "Elas se chamam Slides, Docs e Design e ficam dentro do chat…" | 12,28 (com pausa interna em 13,7) | 12,30–17,45 | tomada única; a pausa interna de 0,3 s sai sozinha no motor |
| 3 | "E pra utilizar é muito fácil… apresentação comercial… ele prepara todos os slides" | 17,65 (abandonada) · 19,95 (abandonada) · 24,12 (termina em "e a...") · 30,84 (só o começo) · 34,43 (abandonada) · **38,59–46,28** · 65,97–74,75 | 38,60–46,25 | A de 38,6 s é completa e enxuta. A de 66 s (mais recente) também é completa, mas mais longa e com muleta ("pedir para ele aquilo que…", "A partir daí, então, ele vai preparar"). **Exceção da regra 5.1.5.** |
| 4 | "Depois… você pode exportar… PowerPoint ou Google Slides" | 46,20 ("ou, por exemplo, Google Slides e...") · **78,88–84,48** | 78,90–84,45 | a de 46 s tem "por exemplo" sobrando e termina pendurada em "e..."; a de 79 s é a mais recente e limpa |
| 5 | "Mas essa novidade não para só nos slides. Na mesma conversa… um documento de uma página." | **86,16–92,17** · 94,14 (termina em "documento") · 108,85 (tropeço: "pode para ele escrever") · 114,97 (completa, longa: "página inteira para você utilizar no seu site"; "não para nos slides", sem "só") · 131,15 (a última; muda o conteúdo para "roteiro → carrosséis") | 86,10–92,15 | completa e enxuta, com "documento de uma página", que é o exemplo certo do **Docs** |
| 6 | "Ele pode até criar carrosséis no Instagram pra acompanhar esse material." | **121,78–125,42** (cauda da tomada de 115 s) | 121,80–125,35 | dá ao **Design** o exemplo dele; **juntar tomadas (5.2)**: começa em fim de frase e encaixa depois de "documento de uma página." |
| — | "Com base nesse material." | 140,00 | **fora** | cauda da tomada de 131 s, que foi descartada |
| — | "Então..." | 141,33 | **fora** | **falsa largada de uma palavra** (o erro da v1) |
| 7 | "Então, ao invés de você pagar pelo Gamma ou pelo Canva… Comenta SLIDES e eu te envio um link…" | **142,77–149,53** | 142,80–149,50 | `from` colado no início da tomada boa, para não alcançar o "Então..." 0,9 s antes |

### O que o motor fez

```
nível da fala (p90) -24.5 dB → limiares -37.5 / -30.5 dB
vícios removidos: 0
13 trechos · J/L em 6 emendas · duração 38.77s
```

Os 7 keeps viraram 13 trechos, porque as pausas internas de mais de 0,2 s saíram. Exemplos: 12,37–13,57 e
13,87–17,43 (a pausa entre "Slides" e "Docs" saiu); 38,67–43,87 e 44,00–46,20.

---

## 12 · Histórico: o que deu errado na v1 e virou regra

A v1 foi feita sem este método: corte por volume simples e conferência só pela transcrição longa.

| Erro na v1 | Causa | Regra criada |
|---|---|---|
| "Então" repetido antes de "Então, ao invés de…" | o keep começava em 141,35 s e pegava a falsa largada; a transcrição longa juntou os dois "Então" | princípio 3; seção 5.3 (borda colada quando as tomadas estão próximas); emendas conferidas sozinhas |
| Pausas com respiração entre frases | fala detectada só pelo volume, com limiar baixo (−52 dB), então a respiração contava como fala | princípio 5; detector com volume + tilt e calibração pelo p90 |
| Bordas com respiro sobrando | margem fixa depois do último som | bordas no vale; LEAD/TAIL de 0,06/0,14 s |
| Duração: 40,3 s | — | v2: 38,8 s com o mesmo conteúdo |

---

## 13 · Instruções para o agente

(O `SKILL.md` resume isto. Aqui está a versão completa.) Quando pedirem para cortar, decupar, limpar ou
"tirar os erros" de uma gravação:

1. **Confirme o bruto** (caminho) e crie a `PASTA` de trabalho ao lado dele ou na pasta do projeto. Rode
   `ffprobe` e anote duração, resolução e fps.
2. **Antes de cada etapa lenta**, avise em uma linha curta ("Transcrevendo as tomadas, leva alguns
   minutos."), para a espera não parecer travamento. Rode as etapas longas em segundo plano.
3. **Passo 1**, depois **leia `tomadas.txt` inteiro**. Nunca escolha keeps sem ter lido todas as tomadas.
4. **Passo 2 (keeps):** siga a seção 5. **Pergunte** a quem gravou só quando tomadas diferentes disserem coisas
   diferentes e não der para saber qual é a correta. Nos outros casos, decida e registre no `why`.
5. **Passos 2b, 3 e 4.** Leia `conferencia.txt` inteiro. Se algum critério da seção 7 falhar, corrija e repita.
   Não entregue com critério falhando.
6. **Entregue** com este relatório (em português, curto):

   ```
   Corte pronto: <caminho do clean.mp4>  ·  <duração bruto> → <duração corte>
   Tomadas usadas: <lista com fonte e o "why">
   Ficou de fora: <falsas largadas, frases abandonadas, testes, tosse...>
   Vícios removidos: <n> (lista em vicios-removidos.txt)
   Conferência: repetições <ok>, emendas <ok>, pausas <ok>
   Incertezas: <o que só dá para validar ouvindo, ou decisões de conteúdo tomadas>
   ```

7. **Não faça** neste módulo: recorte 9:16, legendas desenhadas, imagens, trilha, normalização de volume.
   Isso é do estilo.
8. **Nunca** apague o bruto nem escreva dentro da pasta do bruto sem pedido. A `PASTA` de trabalho é
   descartável e pode ser refeita.

---

## 14 · Opcionais (só se pedirem)

Usar só se pedirem:

- **Voz em 1,05x**: acelera levemente o ritmo, preservando o tom.
  `ffmpeg -i clean.mp4 -filter_complex "[0:v]setpts=PTS/1.05[v];[0:a]atempo=1.05[a]" -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -crf 20 -r 30 -c:a aac -b:a 192k clean-105.mp4`.
  Se usar, refaça o `cortepalavras.json` sobre o arquivo acelerado.
- **Teto de 90 s por reel**: se o corte passar, avise quem gravou do que pode cair.
- **Encoder automático** (NVIDIA / Quick Sync / AMD / Apple): aqui o Mac usa `h264_videotoolbox` e
  as outras máquinas, `libx264`.

---

## 15 · Arquivos

```
~/.claude/skills/reel/corte/
├── CORTE.md                        o roteiro curto que o agente segue (fluxo, regras, aceite, entrega)
├── references/
│   └── EDICAO-BRUTA.md             ← este documento (o porquê de tudo)
├── scripts/
│   ├── 0-checar.py                 passo 0: confere ffmpeg, whisper-cli, numpy e modelo; diz como instalar
│   ├── comum.py                    whisper-cli, áudio 16 kHz, prompts (vícios e nomes), escolha do modelo
│   ├── 1-tomadas.py                passo 1: mapa de tomadas pela energia + texto real de cada trecho
│   ├── 2-vicios.py                 passo 2b: transcrição sem esconder vícios, por keep
│   ├── 3-corte.py                  passo 3: o motor (som + vícios + vale + J/L) → edl, corte.wav, clean.mp4
│   ├── 4-conferir.py               passo 4: texto, repetições, emendas ±2 s, pausas
│   └── remapear.py                 passo 5: leva tempos de um corte antigo para o novo
├── exemplo/                        o gabarito da v2 aprovada
│   ├── tomadas.txt                 o mapa de tomadas do bruto
│   ├── keeps.json                  as 7 decisões editoriais, com o "why"
│   ├── edl.json                    os 13 trechos resultantes
│   └── conferencia.txt             a conferência aprovada
```

**Teste de regressão (na máquina que tem o bruto de exemplo):** depois de mudar o motor, rode os passos 1 a
4 com `exemplo/keeps.json` sobre o bruto de exemplo
e compare o `edl.json` com `exemplo/edl.json`. Se a mudança não era para alterar este caso, eles precisam ser
idênticos.
