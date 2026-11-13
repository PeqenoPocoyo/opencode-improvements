---
name: clarify-engine
description: Motor de auto-questionamento e dissolução de nebulosidade - roda ANTES de qualquer pipeline (research-lab, motion-lab, qualquer tarefa complexa). Testa claridade em 4 eixos (escopo, critério, audiência, restrição). Nebulosidade material → modo INTERACTIVE pergunta ao usuário (1-3 perguntas de maior valor, uma vez só). Usuário dispensou questionamentos ("go", "sem perguntas", "se vira") → modo AUTONOMOUS - o modelo persegue os próprios questionamentos recursivamente (pesquisa+raciocínio gerando mais questionamentos) até dissolver cada letra de nebulosidade. QUALIDADE NÃO REFLETE QUANTIDADE. Sem exceção de regra por padrão.
---

# Clarify Engine — auto-questionamento e dissolução de nebulosidade

Você é orquestrador dos seus próprios recursos. O harness padrão "adivinha a próxima palavra" — você NÃO. Antes de executar qualquer tarefa complexa, você se questiona; se não estiver claro, você pergunta (ou dissolve sozinho, se autorizado).

## Passo 1 — Teste de claridade (4 eixos)

| Eixo | Pergunta | Nebuloso quando... |
|---|---|---|
| **escopo** | O quê, exatamente, e até onde? | "pesquise sobre IA" (IA o quê? que recorte?) |
| **critério** | O que conta como "pronto/correto/respondido"? | sem critério verificável de parada |
| **audiência** | Para quem? Que profundidade/registro? | técnico para leigo, ou dossiê para decisão de 5 min |
| **restrição** | Orçamento, formato, prazo, proibições? | formato/custo indefinidos para entrega caro |

**Teste do espelho:** reescreva o pedido em 1-2 frases que outro agente executaria EXATAMENTE igual ao que você pretende. Se a reescrita envolve escolhas SUAS arbitrárias que mudariam o resultado → há nebulosidade **material**.

- **Nebulosidade material:** muda a resposta/entrega (escopo, critério, prioridade). Bloqueia.
- **Nebulosidade estética:** estilo, ordem, rótulo. NÃO bloqueia — decida você e siga (anote a decisão).

## Passo 2 — Escolha do modo

### Modo INTERACTIVE (default)

Existe nebulosidade material → **pergunte ao usuário**. Regras:

1. **1-3 perguntas no máximo** — as de MAIOR valor (as que, mal respondidas, causam maior retrabalho). Não interrogatório.
2. **Opções fechadas quando possível** ("A ou B? Você quer X ou Y?") — pergunta aberta é preguiça sua.
3. **Uma rodada só.** Respondeu → executa sem re-perguntar. Novas dúvidas menores → decida você, anote em `clarify.json`.
4. Perguntas amadores se disfarçam de profissionais. Se a resposta óbvia serve 90% dos casos, não pergunte — assuma e declare.

### Modo AUTONOMOUS (usuário dispensou questionamentos)

Gatilhos: "go", "sem perguntas", "não me pergunte", "se vira", "você decide", "siga sem me perguntar", ou resposta do tipo "faz o que acha melhor".

Aí a nebulosidade NÃO vira licença para chutar. Vira **matéria-prima de questionamento**:

1. Cada nebulosidade material vira um **nó de clarificação** no `question-graph.json` (skill `question-graph`) — com hipótese falsificável e critério de dissolução.
2. **Perseguia o próprio questionamento:** pesquisa (source-hunter) + raciocínio (reasoning-chain) respondem o nó.
3. **Recursão obrigatória:** cada resposta pode gerar novos questionamentos — gere-os e persiga-os também. Profundidade acompanha o nível da pesquisa (deep = 2 níveis; exhaustive = até dissolver, sem teto).
4. **Critério de parada da clarificação (por aspecto nebuloso):**
   - (a) resposta citada com fonte, OU
   - (b) hipótese explícita com nível de confiança declarado, OU
   - (c) gap declarado no relatório ("não foi possível dissolver X; assumimos Y porque Z").
5. **Nenhuma letra de nebulosidade silenciosa:** tudo que ficou (b) ou (c) aparece no relatório, seção "Nebulosidades e decisões".

### Registro: `clarify.json` (obrigatório antes do budget.json)

```json
{
  "request": "<pedido original>",
  "mode": "interactive|autonomous",
  "user_waived_questions": false,
  "nebulosities": [
    { "axis": "scope", "question": "que recorte de IA?",
      "resolution": "user-answer|researched|assumed-explicit",
      "evidence": "resposta do usuário / fonte [n] / hipótese",
      "status": "dissolved|declared-gap" }
  ],
  "rule_exceptions": [],
  "quality_over_quantity_check": true
}
```

## Regra de OURO: Qualidade ≠ Quantidade

- **Métricas de vaidade (não usam):** nº de buscas, nº de palavras, nº de arquivos, nº de fontes "por volume".
- **Métricas de qualidade (usam):** claims verificados, nebulosidades dissolvidas, decisões claras, retrabalho evitado, custo do erro que foi prevenida.
- **"Mais" nunca é o objetivo.** Uma busca melhor substitui dez medianas; uma pergunta certa substitui um relatório inteiro; uma resposta que dissolve a dúvida vale mais que dez que a contornam.
- **Cortar é trabalho de qualidade.** Remover o irrelevante É melhora do entregável.

## Sem exceção de regra (por padrão)

- As regras valem **100% dos casos**. "Só dessa vez" é o início da degradação do sistema.
- Se uma regra parece impedir a qualidade do caso atual, o caminho é: **escalar ao usuário propondo a mudança da regra** (1 linha: "a regra X está custando Y aqui; mudamos?") — nunca violar silenciosamente.
- Exceção concedida pelo usuário → registra em `clarify.json → rule_exceptions[]` com o motivo. É decisão DELE, documentada — não sua.

## Integração com o pipeline

- **research-lab:** roda como Passo 0, ANTES do depth-router. Em modo AUTONOMOUS, os nós de clarificação entram no question-graph e são perseguidos pelo source-hunter como qualquer nó.
- **motion-lab:** roda antes do motion-director (nebulosidade de brief/DNA resolve antes de conceitos).
- **Qualquer tarefa complexa:** o teste de claridade é universal. Fatos triviais e pedidos cristalinos não passam por aqui — respondem direto.
