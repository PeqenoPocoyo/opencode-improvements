# Auto-Observação Negativa — Instrução

## Princípio Central
**A auto-melhoria não depende do usuário.** O agente observa suas próprias limitações,
erros e incertezas e as registra como feedback negativo para auto-melhoria.

## O que é uma observação negativa?
Qualquer padrão na resposta do agente que indique:
- **Erro admissão**: "não funciona", "falhou", "bug", "erro", "quebrou"
- **Incerteza**: "não tenho certeza", "talvez", "possivelmente", "acho que"
- **Retrabalho**: "vou corrigir", "ajustar", "refazer", "tentar novamente"
- **Limitação**: "não consigo", "não é possível", "limitação", "não suporta"

## Como funciona
1. O agente gera uma resposta
2. O hook `self-observation.py` analisa a resposta
3. Se padrões negativos são detectados, registra em `validation.json`
4. Se 2+ observações negativas → recurso é revertido para `raw`
5. O recurso pode ser re-marcado após correção

## Ciclo de Auto-Melhoria Autônomo

```
Agente responde → Hook analisa → Observação negativa detectada
     ↓
validation.json atualizado (feedback_negative++)
     ↓
Se 2+ negativos → reverter para raw
     ↓
Agente analisa o gap → implementa melhoria
     ↓
Autoteste valida → marcar como melhorado
     ↓
Commit + Push → Sync para outros dispositivos
```

## Regras

### 1. Detecção automática
- O hook `self-observation.py` detecta padrões negativos automaticamente
- Não depende de feedback explícito do usuário
- Fail-open: nunca quebra a sessão

### 2. Registro
- Cada observação negativa é registrada em `validation.json`
- Inclui: categoria, padrão, contagem, timestamp
- O recurso associado é identificado automaticamente

### 3. Reversão
- 2+ observações negativas → reverter para `raw`
- Notificar dispositivo de origem
- O dispositivo pode corrigir e re-marcar

### 4. Melhoria
- O agente analisa a observação negativa
- Implementa melhoria no recurso
- Testa com autoteste
- Marca como melhorado
- Commit e push

### 5. Multi-Device
- Observações negativas são sincronizadas via git
- Outros dispositivos podem ver e agir sobre as observações
- Cada dispositivo pode contribuir com melhorias

## Exemplos

### Exemplo 1: Erro de compilação
```
Agente: "O código não compila, vou corrigir o erro de sintaxe."
Hook: detecta "não compila" (error_admission) + "vou corrigir" (rework)
→ feedback_negative += 2
→ Se >= 2: reverter para raw
```

### Exemplo 2: Incerteza
```
Agente: "Não tenho certeza se essa abordagem funciona, talvez precise ajustar."
Hook: detecta "não tenho certeza" (uncertainty) + "talvez" (uncertainty) + "ajustar" (rework)
→ feedback_negative += 3
→ Se >= 2: reverter para raw
```

### Exemplo 3: Limitação
```
Agente: "Não consigo gerar imagem realista, não suporta fotorrealismo."
Hook: detecta "não consigo" (limitation) + "não suporta" (limitation)
→ feedback_negative += 2
→ Se >= 2: reverter para raw
```

## Integração com o Ciclo de Auto-Melhoria

```
┌─────────────────────────────────────────────────┐
│  CICLO DE AUTO-MELHORIA AUTÔNOMO                │
│                                                 │
│  1. Agente responde (com limitações)            │
│     ↓                                           │
│  2. Hook detecta observação negativa             │
│     ↓                                           │
│  3. validation.json atualizado                  │
│     ↓                                           │
│  4. Se 2+ negativos → reverter para raw         │
│     ↓                                           │
│  5. Agente analisa o gap                        │
│     ↓                                           │
│  6. Implementa melhoria                         │
│     ↓                                           │
│  7. Autoteste valida                            │
│     ↓                                           │
│  8. Marca como melhorado                        │
│     ↓                                           │
│  9. Commit + Push                               │
│     ↓                                           │
│  10. Sync para outros dispositivos              │
│     ↓                                           │
│  (volta para 1)                                 │
└─────────────────────────────────────────────────┘
```

## Diferença: Feedback do Usuário vs Auto-Observação

| Aspecto | Feedback do Usuário | Auto-Observação |
|---|---|---|
| **Origem** | Usuário diz "isso não funciona" | Agente admite "não funciona" |
| **Dependência** | Depende do usuário | Autônomo |
| **Velocidade** | Lenta (usuário precisa notar) | Rápida (imediata) |
| **Cobertura** | Apenas o que o usuário vê | Tudo que o agente admite |
| **Ciclo** | Reativo | Proativo |

## Metadata
- **Categoria**: Meta/DevOps
- **Prioridade**: Crítica
- **Aplicável a**: Todo o pacote de recursos
- **Versão**: 1.0
- **Criado**: 2026-10-28