---
name: depth-router
description: Define o nível de profundidade da pesquisa (quick/standard/deep/exhaustive) e o orçamento correspondente de buscas, fontes e tokens de contexto. Roda como PRIMEIRO passo do pipeline research-director. Gera budget.json. Detecta o nível por gatilhos explícitos no prompt ("deep research", "exaustivo", "sem limite", "go" = exhaustive; "rápido" = quick) e por heurística de complexidade (domínios cruzados, decisão caras, datas/numeros). Bloqueia execução sem orçamento definido.
---

# Depth Router — nível de profundidade e orçamento

## Níveis

| Nível | Buscas | Fontes | Contexto (tokens) | Sub-agentes | Entrega |
|---|---|---|---|---|---|
| `quick` | 1-2 | 1-3 | ~5k | 0 | Resposta direta + links |
| `standard` | 3-6 | 4-8 | ~20k | 0 | Briefing com citações |
| `deep` | 8-20 | 10-25 | ~80k | 1 por ramo | Relatório completo |
| `exhaustive` | 20+ | 30+ | sem teto prático | ondas paralelas | Dossiê + apêndices |

## Como detectar o nível

1. **Gatilhos explícitos (vencem tudo):**
   - `exhaustive`: "deep research", "exaustivo", "dossiê", "sem limite", "go", "tudo que existir", "não economize"
   - `quick`: "rápido", "só me diz", "quick check", "de cabeça"
   - `deep`: "pesquise a fundo", "investigue", "relatório completo"
   - `standard`: default quando nada é dito
2. **Heurística de complexidade** (para standard vs deep):
   - ≥3 dimensões na árvore de perguntas → +1 nível
   - Decisão cara envolvida (dinheiro, saúde, jurídico, compra) → +1 nível
   - Assunto com controvérsia/dados conflitantes conhecidos → +1 nível
   - Máximo: deep (exhaustive SÓ por pedido explícito)

## Saída: `budget.json`

```json
{
  "level": "deep",
  "detected_by": "explicit:'deep research'",
  "budget": { "max_searches": 20, "max_sources": 25, "max_context_tokens": 80000, "subagents": true },
  "consumed": { "searches": 0, "sources": 0, "context_tokens": 0 },
  "rules": { "synthesize_at_pct": 80, "min_sources_per_claim": 2, "min_sources_expensive_claim": 3 }
}
```

## Regras

- **Sem budget.json no disco, nada executa** (o hook `researchlab-budget_guard` bloqueia escrita de relatório sem ele).
- `consumed` é atualizado a cada busca/fonte (pelo `context-weaver`).
- **80% do orçamento → parar de buscar, sintetizar** com o que tem (listar gaps honestamente).
- `exhaustive` não tem teto, MAS ainda exige: claims verificados, triangulação e gaps listados. Sem limite ≠ sem rigor.
- Recusar upscale silencioso: se você subir o nível, diga ao usuário e o motivo (1 linha).
