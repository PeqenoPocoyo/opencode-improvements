---
name: self-critique
description: Revisão adversarial do próprio relatório de pesquisa - 5 perguntas hostis (qual claim morre primeiro, o que a fonte contrária diria, onde está a bolha, o que faltou, se o TL;DR sobrevive sozinho), score 0-100 e máx 2 passes de correção. Último passo do pipeline antes da entrega. Use sempre que um relatório for gerado, especialmente em deep/exhaustive.
---

# Self Critique — adversarial do próprio relatório

## As 5 perguntas (responda TODAS, por escrito, antes de entregar)

1. **Qual claim morre primeiro?** Se um advogado do diabo atacasse só UM ponto, qual seria e ele sobrevive? (cheque a tabela de claims)
2. **O que a fonte contrária diria?** Você buscou o dissenso (anti-bolha)? Se não, faça 1 busca agora (se orçamento permitir) ou declare como gap.
3. **Onde está a bolha?** Apenas fontes do mesmo tipo/idioma/lado? Conte os tipos no apêndice — se 100% secundária, degrade a confiança global 1 degrau.
4. **O que faltou?** Qual dimensão do question-graph ficou `open`/`unanswerable`? Está nos gaps, com custo estimado de uma rodada 2?
5. **O TL;DR sobrevive sozinho?** Se o usuário ler SÓ o TL;DR, leva a resposta correta? Claims caros estão lá com hedging correto?

## Score (0-100)

- Triangulação: 30 (claims caros com 3 fontes)
- Anti-bolha: 20 (dissenso buscado e reportado)
- Cadeias: 20 (inferências com lógica explícita)
- Gaps: 15 (honestos, com custo de rodada 2)
- TL;DR: 15 (responde sozinho)

## Regras

- **< 70 → 1 passe de correção obrigatório** (conserte os 2 piores itens) e re-score. Máx 2 passes; depois, entregue com o score final e as ressalvas visíveis.
- O score e as 5 respostas vão NO RELATÓRIO (seção "Self-critique", no fim) — transparência total.
- Não score inflacionado: o critic é você contra você. "Tudo ok, 95" sem evidência = red flag.
- Se o usuário der feedback negativo depois ("paia", "superficial"), rode o ciclo feedback-driven: implemente a melhoria no pacote (skills/hooks), teste, marque em validation.json, commite.
