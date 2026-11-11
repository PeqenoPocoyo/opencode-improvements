---
name: context-weaver
description: Acumula, deduplica e comprime os achados da pesquisa em knowledge-map.md - mapa de conhecimento vivo com claims, fontes, nível de confiança, conflitos marcados e gaps listados. Mantém o contador de consumo no budget.json. Use continuamente durante a pesquisa (não só no fim) para que contexto antigo seja comprimido sem perder claims.
---

# Context Weaver — mapa de conhecimento vivo

## knowledge-map.md

```markdown
# Knowledge Map — <assunto> (nível: deep)

## Q1 — <dimensão>
- **[V] claim verificado** — <frase>  [1][2]
- **[P] parcial** — <frase>  [3] (apenas 1 fonte, cara → precisa de 2ª)
- **[C] conflito** — A diz X [1]; B diz Y [4]. → resolvido em favor de A (fonte primária, mais recente)
- **[G] gap** — não encontramos dado de <X>; busca com <termos alternativos> falhou

## Gaps acumulados
- ...

## Consumo
- buscas: 7/20 · fontes: 12/25 · contexto: ~46k/80k (58%)
```

## Regras

- **Atualize a cada rodada de busca**, não no fim. O mapa é o estado do pipeline — se a sessão compactar, ele sobrevive no disco.
- **Dedup:** claim repetido com fonte nova = +1 confirmação (conte `supporters`), não nova linha.
- **Compressão progressiva:** quando o contexto passar de 60% do orçamento, resuma buscas antigas em 1 linha por fonte (mantenha a citação literal dos claims V e C — o resto pode virar referência).
- **Conflitos nunca são apagados:** viram linha [C] e o verificador decide com hierarquia de fonte (primária > secundária; recente > antiga; independente > interessada).
- **Gaps são ouro:** cada gap vira item honesto no relatório final — e, em deep/exhaustive, gera 1 busca de resgate com termos alternativos antes de desistir.
- **Atualize `budget.json.consumed`** a cada busca/fonte adicionada.
