
# Motor de corte · módulo 1 (a decupagem)
*Roteiro curto do motor de corte da skill `reel` (pasta `corte/`). Idêntico ao motor aprovado em produção em out/2026; o documento completo é `references/EDICAO-BRUTA.md`.*

**A regra em uma frase:** *você decide o que fica lendo; o som decide onde cortar.* A escolha das tomadas é
editorial, feita sobre o texto real de cada trecho. O ponto exato do corte é medido no áudio, nunca no tempo
de palavra do Whisper.

O documento completo, com o porquê de cada regra, a calibração, o diagnóstico e a decupagem comentada do
caso aprovado, está em **`references/EDICAO-BRUTA.md`**. Leia as seções 5 (escolher tomadas) e 7 (critérios
de aceite) antes do primeiro corte da sessão. O caso aprovado está em `exemplo/`, com `tomadas.txt`,
`keeps.json`, `edl.json` e `conferencia.txt`.

## Fluxo

`S=~/.claude/skills/reel/corte/scripts` · `PASTA` = uma pasta de trabalho por vídeo, criada ao lado do
bruto (ex.: `<pasta do bruto>/corte-<data>`). No Windows, rode com `PYTHONUTF8=1` e use `python` no lugar de
`python3`.

Antes de cada etapa lenta (passos 1, 2 e 3), avise em uma linha ("Transcrevendo as tomadas, leva alguns
minutos.") e rode em segundo plano.

0. **Máquina pronta?** Na primeira vez em cada máquina: `python3 $S/0-checar.py`. Se faltar algo, ele diz
   como instalar.
1. **Mapa de tomadas:** `python3 $S/1-tomadas.py "<bruto>" PASTA`, depois **leia `PASTA/tomadas.txt`
   inteiro**. O script acha a fala pela energia e transcreve cada trecho sozinho. Retomadas aparecem como
   linhas parecidas em sequência; falsas largadas, como linhas curtas terminando em "...".
2. **Keeps:** escreva `PASTA/keeps.json` → `{"keeps":[{"from","to","why"}]}` (segundos **da fonte**, na
   ordem do vídeo final). As regras estão logo abaixo.
   Depois rode `python3 $S/2-vicios.py PASTA` e leia a saída, que mostra os "éé/hum" dentro de cada keep.
3. **Motor:** `python3 $S/3-corte.py "<bruto>" PASTA` (`--jl 4` é o padrão; `--jl 0` desliga o J/L;
   `--sem-video` gera só o áudio e o edl). Ajustes finos ficam em `PASTA/ajustes.json`
   `{"cut":[[a,b]],"keep":[t],"force":[[a,b]]}`, com tempos da fonte.
4. **Conferência:** `python3 $S/4-conferir.py PASTA --prompt "<nomes próprios do vídeo>"`. Leia
   `conferencia.txt` **inteiro**. Se algum critério falhar, volte ao passo 2 ou 3.
5. **Só se a edição visual já existia** e o corte mudou: remapeie os tempos com `scripts/remapear.py`
   (`Mapa(velho, novo).novo(t)`). Não recronometre à mão.

## Regras dos keeps (resumo da seção 5)

- **Uma frase, uma tomada: a melhor completa.** Descarte as incompletas (terminam em "...", param no meio) e
  as com tropeço. Entre as completas, a padrão é a **mais recente**. A exceção é quando ela é mais longa ou
  tem muleta e outra está igualmente completa e mais enxuta: aí fica a enxuta.
- **Falsa largada de uma palavra também sai.** Se duas tomadas estão a menos de 1 s uma da outra, o `from`
  vai **colado** no início da tomada boa, para a folga não alcançar a falsa largada.
- **Folga de 0,1 a 0,2 s** em volta do texto. O motor encosta a borda no silêncio mais próximo, procurando
  para fora do texto.
- **Juntar tomadas** só vale quando cada pedaço começa e termina em fim de frase e o resultado fica mais
  correto ou mais enxuto.
- **Se tomadas diferentes dizem coisas diferentes**, escolha pela informação correta. Se não der para saber
  qual é a correta, **pergunte** a quem gravou. Nos outros casos, decida e registre no `why`.
- **Sempre sai:** "alô, alô", teste de som, tosse, "deixa eu refazer", comentário fora do roteiro.
- **Primeira sílaba comida:** adiante o `from`, marque o keep com `"raw": true` ou use `force`.

## Critérios de aceite (não entregue sem todos)

| Bloco do `conferencia.txt` | Precisa vir |
|---|---|
| Texto do corte | cada frase uma vez só, nenhuma palavra comida (erro de **nome** do Whisper não reprova: corrige na legenda) |
| Repetições coladas | "nenhuma" (ou uma repetição intencional, registrada) |
| Emendas (±2 s, sem prompt) | todas legíveis, sem meia palavra nem retomada murmurada. Começar no meio da frase é o Whisper, não o corte: confirme na janela vizinha |
| Pausas > 0,25 s | "nenhuma" |

**Armadilhas do Whisper:** inventa fala em silêncio longo, esconde repetição na transcrição longa, engole o
começo de recorte curto, inventa "é, ah, hum" quando recebe o prompt de vícios numa janela curta, e às vezes
pula uma frase inteira na transcrição longa. Antes de concluir que algo sumiu, transcreva só aquela janela.

## Entrega

Corte pronto em `PASTA/clean.mp4`. Para o estilo, ficam `corte.wav`, `edl.json` e `cortepalavras.json`; o
contrato completo está na seção 8 do documento. Relatório curto, em português:

```
Corte pronto: <caminho do clean.mp4>  ·  <duração bruto> → <duração corte>
Tomadas usadas: <lista com tempo na fonte e o "why">
Ficou de fora: <falsas largadas, frases abandonadas, testes, tosse...>
Vícios removidos: <n>
Conferência: repetições ok · emendas ok · pausas ok
Incertezas: <decisões de conteúdo tomadas; o que só se valida ouvindo>
```

**Não faça neste módulo:** recorte 9:16, legendas desenhadas, imagens, trilha, normalização de volume (é
tudo do estilo). Nunca apague o bruto nem escreva dentro da pasta dele fora da `PASTA` de trabalho.

## Ajustar esta skill

Ela foi validada em um bruto (voz masculina, microfone dinâmico próximo, sala tratada). Quando um corte sair
errado em outra gravação:
1. ache o sintoma na tabela da seção 9 do documento (sintoma → causa → ajuste);
2. mude **um** parâmetro por vez no topo de `scripts/3-corte.py` (`REF_DB`, `HOLE`, `ISLAND`, `LEAD`, `TAIL`)
   ou trate o caso com `ajustes.json`;
3. registre na seção 16 do documento: o que mudou, em que tipo de gravação e por quê.
Se uma mudança vale para todas as gravações, mude o padrão. Se vale só para um tipo (lapela, ambiente
ruidoso), anote como perfil na seção 16 em vez de trocar o padrão.
