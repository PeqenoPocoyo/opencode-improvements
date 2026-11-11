---
name: synthesis-writer
description: Escreve o relatório final da pesquisa a partir do knowledge-map - estrutura TL;DR -> corpo por dimensão -> cadeias de raciocínio -> tabela de claims -> gaps -> apêndice de fontes numeradas com citações. Separa FATO de INFERÊNCIA e usa o vocabulário da confiança. Último passo do pipeline antes do self-critique. Saída em research-report.md (ou docx sob pedido).
---

# Synthesis Writer — relatório final com citações

## Estrutura obrigatória

```markdown
# <Título> — <nível da pesquisa>

**TL;DR (3-5 linhas):** a resposta direta, com as 1-3 conclusões mais caras.

## 1. Contexto do pedido
<o que foi perguntado, em 2-3 linhas — nada de enrolação>

## 2. <Dimensão Q1>
<corpo curto, claims com citação inline [n]>

## 3. <Dimensão Q2> ...

## N. Conclusões (com cadeias)
<C1..Cn em formato reasoning-chain>

## Verificação de claims
<tabela do claim-verifier>

## Gaps e limitações
<[G] honestos: o que não encontramos e por quê>

## Fontes
[1] Título — URL — data — tipo
...
```

## Regras

- **Fato ≠ inferência:** frases de fato carregam [n]; frases de inferência começam com "nossa leitura:", "inferimos:", "provável que".
- **Vocabulário da confiança:** "confirmado por 2 fontes" > "provável" > "sinal" > "hipótese". Nunca "com certeza" sem fonte primária.
- **Densidade:** cada parágrafo do corpo deve ter ≥1 claim novo ou uma cadeia. Encheção de linguiça é proibida.
- **TL;DR primeiro:** se o usuário parar de ler ali, já leva a resposta.
- **Gaps são conteúdo:** um gap bem descrito ("não há dado público de X; proxy usado foi Y") vale mais que um parágrafo genérico.
- **Apêndice de fontes:** numerado, na ordem de citação, com tipo (primária/secundária) e data. Citação literal dos claims caros.
- **Formato:** default Markdown (`research-report.md`); docx/pdf sob pedido (usar converter existente, sem instalar nada).
- **Auto-abertura:** se gerar arquivo, chamar `browser.preview({ path })` imediatamente (regra do repo) e emitir balão de artifact.
