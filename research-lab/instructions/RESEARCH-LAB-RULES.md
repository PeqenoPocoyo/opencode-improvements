# Research Lab — Regras (as 10)

> Pacote de pesquisa profunda na internet. Análogo ao motion-lab: entry point + skills + guardas.

1. **Orçamento antes da busca.** `budget.json` (depth-router) existe antes de qualquer WebSearch. Hook bloqueia relatório sem ele.
2. **Nível por gatilho explícito.** "deep research"/"exaustivo"/"go" → exhaustive; "rápido" → quick; silêncio → standard. Upscale só avisando o usuário.
3. **Árvore antes da caça.** `question-graph.json` com perguntas fechadas, hipóteses falsificáveis e critérios de "respondida". Pergunta sem critério é podada.
4. **Triangulação mínima.** Claim comum: 2 fontes independentes. Claim caro (dinheiro/saúde/jurídico/número citável): 3, sendo ≥1 primária.
5. **Citação literal.** `sources.json` guarda a frase exata + URL + data. Paráfrase sem citação não é fonte.
6. **Anti-bolha obrigatório (deep/exhaustive).** Pelo menos 1 busca com os termos do lado contrário, por dimensão de risco.
7. **O mapa é o estado.** `knowledge-map.md` atualizado a cada rodada; contexto comprimido aos 60%; claims V/C nunca perdem a citação.
8. **80% → sintetizar.** Não emende "só mais uma busca". Gaps viram conteúdo honesto do relatório.
9. **Fato ≠ inferência.** Fato com [n]; inferência com lógica explícita (reasoning-chain). Conclusão contaminada é invalidada e refeita — nunca remendada.
11. **Teste de clareza antes de executar (Passo 0 - `clarify-engine`).** `clarify.json` antes do `budget.json`, sempre. Nebulosidade material em escopo/criterio/audiencia/restricao → pergunta ao usuario (1-3 perguntas de maior valor, opcoes fechadas, 1 rodada so). Usuario dispensou questionamentos ("go", "sem perguntas") → modo AUTONOMOUS: cada nebulosidade vira no de clarificacao perseguido com pesquisa+raciocinio, recursivamente, ate dissolver (resposta citada | hipotese explicita | gap declarado). NENHUMA nebulosidade silenciosa.
12. **QUALIDADE nao reflete QUANTIDADE. Sem excecao de regra.** Metricas de vaidade (n buscas/palavras/arquivos) nao contam; contam claims verificados, nebulosidades dissolvidas, retrabalho evitado. As regras valem 100% dos casos; excecao so por decisao EXPLICITA do usuario, registrada em `clarify.json -> rule_exceptions[]`. Se uma regra parece impedir qualidade: escalar ao usuario propondo a mudanca - NUNCA violar em silencio.
10. **Self-critique antes de entregar.** 5 perguntas adversariais + score; <70 → 1 passe de correção. Score e respostas vão no relatório.

## Fluxo

```
pedido → clarify-engine (clarify.json: testa nebulosidade → pergunta ou modo autonomo)
       → depth-router (budget.json)
       → question-graph (question-graph.json)
       → source-hunter (sources.json, WebSearch/WebFetch)
       → context-weaver (knowledge-map.md, consumo)
       → reasoning-chain + claim-verifier
       → synthesis-writer (research-report.md) [hook: gate de citação]
       → self-critique → entrega
```

## Hooks (guardas)

| Hook | Evento | Ação |
|---|---|---|
| `researchlab_session_start.py` | SessionStart | injeta regras + estado (budget/mapa existem?) |
| `researchlab_budget_guard.py` | PreToolUse Write/Edit | **bloqueia** relatório sem budget ou com orçamento estourado |
| `researchlab_claim_gate.py` | PreToolUse Write | **bloqueia** relatório sem `## Fontes` ou sources.json vazio |
| `researchlab_stop_gate.py` | Stop | avisa se pipeline aberto sem relatório (fail-open) |

Todos fail-open: erro interno nunca trava o trabalho — mas violação DE REGRA bloqueia (exit 2).
