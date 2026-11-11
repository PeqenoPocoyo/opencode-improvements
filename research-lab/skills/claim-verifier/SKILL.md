---
name: claim-verifier
description: Tabela de verificação de claims - cada afirmação do relatório classificada como verified/partial/unverified/contradicted, com fontes e nível de confiança. Gate de qualidade: o relatório final não sai com claims unverified acima do limite do nível (quick=2, standard=3, deep=2, exhaustive=0 sem flag explícita). Use antes de qualquer entrega e no self-critique.
---

# Claim Verifier — gate de verificação

## Tabela (vai no relatório, seção "Verificação de claims")

| # | Claim | Status | Fontes | Confiança | Nota |
|---|---|---|---|---|---|
| 1 | <afirmação factual> | verified | [1][2] primárias | alta | concordância total |
| 2 | <afirmação> | partial | [3] só 1 | média | caro → falta 2ª fonte |
| 3 | <afirmação> | unverified | – | baixa | inferência nossa, marcada |
| 4 | <afirmação> | contradicted | [4] vs [5] | – | usamos a versão [4] (primária) |

## Limites por nível (claims `unverified` permitidos na entrega)

| Nível | Limite unverified | Regra |
|---|---|---|
| quick | 2 | desde que não sejam caros |
| standard | 3 | marcados e isolados em "inferências" |
| deep | 2 | caros exigem 3 fontes ou vira gap |
| exhaustive | 0 | ou flag explícita do usuário aceitando risco |

## Critérios

- **Caro** = envolve dinheiro, saúde, jurídico, reputação de pessoa/empresa, número que alguém vai citar.
- **verified:** ≥2 fontes independentes concordando (3 se caro), sendo ≥1 primária ou de referência.
- **contradicted:** fontes divergem → registre as duas versões + critério de decisão (hierarquia: primária > secundária; recente > antiga; independente > interessada).
- **unverified:** só inferência nossa ou 1 fonte fraca → deve ficar VISÍVEL no relatório (nunca embutido como fato).

## Regras

- Rode ANTES do synthesis-writer e de novo no self-critique.
- Claim `contradicted` não some: vira linha de conflito com a decisão explicada.
- Se o limite estourar: (a) 1 busca de resgate por claim estourado (se orçamento permitir), ou (b) degrade o claim para "hipótese não confirmada" visível.
