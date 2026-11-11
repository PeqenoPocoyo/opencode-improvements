---
name: budget-guard
description: Guarda de orçamento - contabiliza buscas, fontes e tokens de contexto consumidos vs o budget.json do depth-router. Aos 80% do orçamento, força síntese; ao atingir 100%, bloqueia novas buscas (exceto nível exhaustive). Também define limites por claim caro. Use em conjunto com o hook researchlab-budget_guard e consulte antes de CADA busca.
---

# Budget Guard — orçamento de contexto e tokens

## Contadores (budget.json → consumed)

Atualize após cada operação:

| Operação | Custo estimado |
|---|---|
| WebSearch | +800 tokens (query + snippets) |
| WebFetch de página | +2.000 tokens (média; páginas grandes +5k) |
| Sub-agente (ramo) | +orçamento do ramo (definido no dispatch) |
| Cada rodada de síntese parcial | +1.000 |

## Regras de corte

- **80% do orçamento:** avise no chat (1 linha), pare de abrir NOVOS ramos, termine o ramo atual.
- **100%:** nenhuma busca nova. Sintetize com o knowledge-map atual. Exceção única: 1 busca de resgate para claim caro `unverified` (se o nível permitir).
- **exhaustive:** sem teto — mas com checkpoint a cada 20 buscas: reporte progresso ao usuário (1 linha) e continue. O usuário pode interromper com "chega".
- **Downgrade honesto:** se o orçamento acabou com gaps críticos, o relatório lista o que FALTARIA pesquisar e o custo estimado para uma rodada 2. Nunca finja completude.

## Sub-agentes (deep/exhaustive)

- Orçamento por ramo = orçamento total ÷ nº de ramos abertos (mín 1 busca, 2 fontes por nó).
- Sub-agente estourou? Ele retorna o que tem + gaps. NUNCA continua além.
- Resultados dos sub-agentes entram no knowledge-map com a mesma regra de triangulação.

## Falha comum (evite)

- Buscar mais do mesmo depois de 2 resultados contraditórios sem mudar os TERMOS. Mudar termos > aumentar volume.
- WebFetch em página paga/muro: 1 tentativa, depois troca por fonte alternativa. Não insista.
