# Níveis de profundidade — tabela de referência

| | quick | standard | deep | exhaustive |
|---|---|---|---|---|
| Buscas | 1-2 | 3-6 | 8-20 | 20+ |
| Fontes | 1-3 | 4-8 | 10-25 | 30+ |
| Contexto | ~5k | ~20k | ~80k | sem teto prático |
| Sub-agentes | 0 | 0 | 1 por ramo | ondas paralelas |
| Profundidade da árvore | 0 | 1 | 2 | 3 níveis |
| Claims unverified na entrega | ≤2 | ≤3 | ≤2 | 0 (ou flag do usuário) |
| Anti-bolha | opcional | 1 busca | 1 por dimensão de risco | 1+ por nó |
| Entrega | resposta + links | briefing citado | relatório completo | dossiê + apêndices |

## Gatilhos

- exhaustive: "deep research", "exaustivo", "dossiê", "sem limite", "go", "não economize"
- deep: "pesquise a fundo", "investigue", "relatório completo"
- quick: "rápido", "só me diz", "quick check"
- standard: default

## Subida de nível

Máximo automático = deep. **Exhaustive exige pedido explícito do usuário** (custa contexto de verdade). Ao subir nível, avise em 1 linha.
