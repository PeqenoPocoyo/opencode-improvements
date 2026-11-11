---
name: reasoning-chain
description: Cadeia de raciocínio verificável - cada passo (premissa -> inferência -> conclusão) carrega fonte ou lógica explícita. Implementa chain-of-verification (resposta -> perguntas de verificação -> respostas isoladas -> correção). Use para transformar claims soltos do knowledge-map em conclusões confiáveis, e para raciocínios de múltiplos passos onde um erro no meio contamina tudo.
---

# Reasoning Chain — raciocínio encadeado e verificável

## Formato (por conclusão do relatório)

```markdown
**Conclusão C1:** <enunciado>

| Passo | Conteúdo | Tipo | Fonte/Lógica |
|---|---|---|---|
| 1 | <premissa> | fato | [2][5] |
| 2 | <inferência do passo 1> | inferência | se P1 ∧ regra R, então I2 |
| 3 | <dado de mercado> | fato | [7] |
| 4 | <conclusão parcial> | inferência | C3 = C1+I2 sobre D3 |
```

- **Tipo `fato`:** precisa de fonte (linhas [n] do sources.json). Sem fonte → reclassifique como inferência ou corte.
- **Tipo `inferência`:** precisa da lógica explícita (qual regra conecta os passos). "Obviamente" não é lógica.
- **Cada inferência é o elo mais fraco:** se você não escreveria a regra num tribunal de auditória, não a use.

## Chain-of-Verification (CoVe) — para conclusões caras

1. Escreva a resposta preliminar.
2. Gere 3-5 perguntas de verificação que, se respondidas diferente, mudariam a resposta.
3. Responda cada uma ISOLADAMENTE (sem olhar a resposta preliminar), só com o knowledge-map.
4. Compare: divergiu → corrija a resposta e anote a correção.

## Regras

- **Nada de saltos:** entre o passo N e N+1, o leitor deve conseguir reconstruir o raciocínio sem te perguntar nada.
- **Incerteza quantificada:** "provável", "sinal forte", "dado único" — use o vocabulário da confiança, não "com certeza".
- **Conclusão contaminada:** se um passo foi desverificado (claim-verifier marcou `contradicted`), TODA a cadeia que dependia dele é invalidada e refeita — não remendo.
- Máx 1 conclusão caro por 400 palavras de relatório (densidade > volume).
