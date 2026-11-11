---
name: question-graph
description: Rede generativa de questionamento - decompõe o pedido raiz em uma árvore de perguntas pesquisáveis com hipóteses, critérios de "respondida" e fontes-alvo. Segundo passo do pipeline research-director (após depth-router). Salva question-graph.json. Use para destrinchar qualquer assunto em dimensões pesquisáveis, evitar buscas vagas e permitir delegação a sub-agentes por ramo.
---

# Question Graph — árvore generativa de perguntas

## Estrutura (question-graph.json)

```json
{
  "root": { "id": "q0", "question": "<pergunta do usuário reescrita de forma pesquisável>", "level": "deep" },
  "nodes": [
    {
      "id": "q1", "parent": "q0", "dimension": "mercado",
      "question": "Qual o tamanho do mercado X no Brasil em 2025?",
      "hypothesis": "Crescimento >10% a.a. pós-2023",
      "answered_when": "número com fonte primária ou 2 secundárias independentes",
      "target_sources": ["IBGE", "relatórios setoriais", "notícias financeiras"],
      "children": ["q1.1", "q1.2"],
      "status": "open"
    }
  ]
}
```

## Como gerar

1. **Raiz:** reescreva o pedido como pergunta única e verificável. Se o pedido for vago, volte ao usuário (1 pergunta de esclarecimento, não 5).
2. **Dimensões (3-7):** fatos/estado-da-arte, números/dados, atores/concorrentes, riscos/controvérsias, histórico/tendência, opinião/consenso especializado, regulatório (quando aplicável).
3. **Profundidade por nível:** quick = 0 filhos (só raiz); standard = 1 nível; deep = 2 níveis; exhaustive = até 3 níveis.
4. **Cada nó precisa de:** pergunta fechada (sim/não ou número/entidade), hipótese inicial (mesmo fraca), critério objetivo de "respondida", fontes-alvo.
5. **Poda:** descarte perguntas sem critério verificável ("é bom X?" → transforme em "quais métricas de X e valores?").

## Regras

- **Pergunta de nó ≠ busca.** Uma pergunta pode precisar de 1-3 buscas. O source-hunter decide.
- **Hipótese falsificável:** se não dá para estar errado, não é hipótese.
- **Dimensões obrigatórias para deep/exhaustive:** riscos/controvérsias E opinião contrária (anti-bolha).
- Atualize `status`: open → hunting → answered/contradicted/unanswerable. Nós `unanswerable` viram gaps no relatório final.
- O graph é VIVO: novos nós podem surgir durante a caça (surpresas legítimas), mas cada novo nó entra com hipótese + critério.
