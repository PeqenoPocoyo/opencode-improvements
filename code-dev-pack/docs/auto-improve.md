# Protocolo de Auto-Melhoria para Desenvolvimento de Código

## Visão Geral
Este documento descreve como o pacote `code-dev-pack` se auto-melhora
com base em feedback real e uso em múltiplos dispositivos.

## Princípio Central
**Melhoria não é opcional.** É contínua. Cada uso gera feedback, cada feedback gera melhoria.

## Ciclo de Auto-Melhoria

```
Uso → Feedback → Análise → Implementação → Autoteste → Validação → Commit → Push → Sync
```

### 1. Uso
Um desenvolvedor (ou agente) usa um recurso do pacote (skill, hook, script, instrução).

### 2. Feedback
O usuário ou o sistema fornece feedback:
- **Positivo**: "funcionou bem", "útil", "rápido"
- **Negativo**: "não funciona", "lento", "confuso", "bugado"
- **Sugestão**: "poderia ter X", "seria melhor se Y"

### 3. Análise
O agente analisa o feedback e classifica:
- **P0**: Bug crítico ou segurança → corrigir imediatamente
- **P1**: Funcionalidade faltante importante → implementar em breve
- **P2**: Melhoria de qualidade → planejar
- **P3**: Nice-to-have → backlog

### 4. Implementação
O agente implementa a melhoria no recurso correspondente.

### 5. Autoteste
O script de autoteste valida a melhoria:
```bash
python scripts/autotest.py --resource <path>
```

### 6. Validação
- Se PASS → marcar como melhorado, incrementar usage_count
- Se FAIL → reverter, analisar, tentar abordagem diferente

### 7. Commit e Push
```bash
git add -A
git commit -m "improve: <recurso> — <descrição da melhoria>"
git push origin staging  # ou main
```

### 8. Sync
Outros dispositivos recebem via auto-sync (a cada hora).

## Validação Progressiva

```
raw → marked → validated → proactive
```

| Estado | Descrição | Threshold |
|---|---|---|
| `raw` | Recém-criado, não revisado | — |
| `marked` | Agente revisou e marcou | 0 usos |
| `validated` | Validação final aprovada | 3+ usos, 0 feedback negativo |
| `proactive` | Totalmente confiável, auto-aplicado | 7+ usos, 0 feedback negativo |

### Feedback negativo
- 1 feedback negativo → incrementar contador, manter estado
- 2+ feedbacks negativos → reverter para `raw`, notificar dispositivo de origem

## Multi-Device Contribution

### Cenário: 3 dispositivos
```
Device A (manhã)     Device B (tarde)     Device C (noite)
       |                    |                    |
   usa + feedback       usa + feedback       usa + feedback
       |                    |                    |
   melhora recurso      melhora recurso      melhora recurso
       |                    |                    |
   commit staging       commit staging       commit staging
       |                    |                    |
       v                    v                    v
   origin/staging  <----  origin/staging  ---->  origin/staging
       |                    |                    |
       v                    v                    v
   origin/main (promovido quando 3+ usos sem feedback negativo)
```

### Regras de contribuição
1. **Nunca sobrescrever** mudanças locais sem avisar (stash/pull/pop)
2. **Sempre reportar** o que foi sincronizado
3. **Validação é progressiva** — não promover sem uso real
4. **Feedback negativo reverte** — recursos com 2+ feedbacks voltam para raw
5. **Se algo falhar** — explicar e sugerir solução

## Teste de Reinterpretação

### O que é?
Um teste que valida se a melhoria realmente funcionou, executado em um
contexto **independente** do que gerou a melhoria.

### Como criar?
1. Identificar o comportamento esperado após a melhoria
2. Criar um cenário que exercita esse comportamento
3. Verificar se o resultado corresponde ao esperado
4. Se não corresponder, a melhoria não foi efetiva

### Marcação de Recursos
```yaml
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "descrição do teste"
test_result: "PASS"
```

## Auto-Observacao Negativa (CRITICO)

### O que e?
O agente observa suas proprias limitacoes, erros e incertezas e as registra
como feedback negativo para auto-melhoria, **sem depender do usuario**.

### Como funciona?
1. O agente gera uma resposta
2. O hook self-observation.py analisa a resposta
3. Se padroes negativos sao detectados, registra em validation.json
4. Se 2+ observacoes negativas -> recurso e revertido para raw
5. O agente analisa o gap -> implementa melhoria
6. Autoteste valida -> marca como melhorado
7. Commit + Push -> Sync para outros dispositivos

### Padroes detectados:
- **Erro admissao**: "nao funciona", "falhou", "bug", "erro", "quebrou"
- **Incerteza**: "nao tenho certeza", "talvez", "possivelmente", "acho que"
- **Retrabalho**: "vou corrigir", "ajustar", "refazer", "tentar novamente"
- **Limitacao**: "nao consigo", "nao e possivel", "limitacao", "nao suporta"

### Diferenca: Feedback do Usuario vs Auto-Observacao
| Aspecto | Feedback do Usuario | Auto-Observacao |
|---|---|---|
| Origem | Usuario diz "isso nao funciona" | Agente admite "nao funciona" |
| Dependencia | Depende do usuario | Autonomo |
| Velocidade | Lenta | Rapida (imediata) |
| Cobertura | Apenas o que o usuario ve | Tudo que o agente admite |

### Regra de ouro:
> Se o agente admite uma limitacao, ela DEVE ser registrada como feedback negativo.
> O ciclo de auto-melhoria nao depende do usuario — e autonomo.

## Regras de Ouro

1. **Se o usuário deu feedback, a melhoria DEVE ser implementada no pacote.**
   Não apenas respondida na conversa — implementada no repo.

2. **Não reusar padrões anteriores.**
   Cada recurso deve ter identidade própria.

3. **Não ter pressa.**
   Melhorar incrementalmente, testar cada mudança.

4. **Autoteste sempre.**
   Toda melhoria deve ter um teste que valida.

5. **Multi-device first.**
   Pensar em como o recurso funciona em 3 dispositivos diferentes.

## Metadata
- **Versão**: 1.0
- **Criado**: 2026-10-28
- **Pacote**: code-dev-pack
- **Objetivo**: Auto-melhoria contínua de desenvolvimento de código