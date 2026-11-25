---
name: deliberation-engine
description: >
  Handler de deliberacao visivel para DESENVOLVIMENTO. Antes de escrever codigo,
  produz um trace curto e citavel de "Avaliando ..." sobre eixos tecnicos, de seguranca,
  de custo e de reversibilidade, decide com registro em decision.json, implementa o
  minimo e verifica com evidencia. Use em feature, bugfix, refactor, migracao, integracao
  de API, tuning e revisao de arquitetura. Evita o "overthinking de 7 minutos": o trace
  e LIMITADO por orcamento (quick/standard/deep) e nunca substitui codigo por conversa.
---

# deliberation-engine — pensar em voz alta, deliver rapido

O modelo deve MOSTRAR a deliberacao (como o painel "Avaliando ..." de um modelo de raciocinio),
mas com **orcamento fixo**. O trace e parte do trabalho, nao o trabalho inteiro.

## Regra de ouro
Trace curto -> decisao registrada -> codigo -> verificacao. Nunca pule para o codigo sem o trace;
nunca transforme o trace em 7 minutos de "Avaliando" sem entregar.

## Steps (ordem obrigatoria)
1. **Decode** (1 linha): o que muda e por que.
2. **Trace de avaliacao** — escolha o orcamento:
   - `quick`: 6 avaliacoes (bug simples, typo, ajuste local)
   - `standard` (default): 12 avaliacoes
   - `deep`: 20 avaliacoes (migracao, arquitetura, security-sensitive)
   Eixo obrigatorio por bloco: escopo/API, compatibilidade/deps, seguranca/segredos,
   custo/performance, reversibilidade/rollback, testes/verificacao.
   Formato: `Avaliando <alvo especifico> -> <achado em 1 linha>`. Se nao houver evidencia,
   escreva `Avaliando ... -> desconhecido, precisa de verificacao` — nunca invente.
3. **Decide** -> escreva `decision.json` no workspace:
   `{"task","chosen","rejected":[{"option","why"}],"risks":[],"verify":["cmd1","cmd2"]}`
4. **Implementa** o menor diff possivel. Sem reescrita gratuita, sem novas abstracoes.
5. **Verifica** com os comandos de `verify` e reporte numeros (testes, lint, build, diff).
6. **Entrega** curta: o que mudou, o que foi verificado, o que ficou desconhecido.

## Anti-overthinking (o caso dos 7 minutos)
- Limite de tempo mental: se o trace passou de ~2 min, DECIDA com o que tem e implemente.
- Nenhuma avaliacao repete outra com palavras diferentes.
- Nunca avalie "legalidade", "硬化" ou "filosofia" sem relacao direta com o codigo em questao.
- Se o usuario pediu "go" / "sem perguntas": modo autonomo — cada duvida vira item do trace
  com `desconhecido` e é resolvida por verificacao no codigo, nao por mais especulacao.

## Handoff com outros handlers
- `research-lab/clarify-engine`: se a duvida e de PESQUISA (fontes, fatos), va la.
- `motion-lab/motion-director`: se o assunto e VIDEO, va la.
- `dev-handler`: se o assunto e CODIGO, fica aqui.
