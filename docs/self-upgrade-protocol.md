# Protocolo de Auto-Upgrade — Documentação

## Visão Geral
Este documento descreve o protocolo completo de auto-aprimoramento do pacote de recursos do OpenCode.

## Estrutura do Pacote

```
opencode-improvements/
├── skills/           # Skills personalizadas (SKILL.md)
│   ├── functional-ui/
│   ├── creative-design/
│   └── self-upgrade/
├── hooks/            # Hooks (PreToolUse, etc.)
│   └── pre-tool-use-security.sh
├── instructions/     # Instruções globais
│   └── AGENTS.md
├── configs/          # Configurações
│   └── mcp.example.json
├── notes/            # Anotações e insights
│   └── conversation-insights.md
├── docs/             # Documentação
│   └── self-upgrade-protocol.md
├── artefatos/        # Artefatos HTML
│   └── cte-dashboard-estoque.html
└── README.md
```

## Ciclo de Auto-Upgrade

### 1. Detecção de Oportunidade
- Usuário solicita melhoria
- Padrão de problema recorrente identificado
- Recurso desatualizado detectado

### 2. Scan de Recursos
```bash
# Listar todos os recursos
find skills/ hooks/ instructions/ configs/ notes/ docs/ -type f
```

### 3. Análise de Gaps
Para cada recurso, verificar:
- [ ] Funcionalidade completa?
- [ ] Documentação atualizada?
- [ ] Testes passando?
- [ ] Sem bugs conhecidos?
- [ ] Sem duplicação?

### 4. Proposta de Melhoria
Gerar lista priorizada (P0-P3) com:
- Descrição da melhoria
- Justificativa
- Impacto esperado
- Risco
- Teste de validação

### 5. Implementação
- Criar branch para a melhoria
- Implementar
- Atualizar metadata
- Commit

### 6. Teste de Reinterpretação
- Criar cenário de teste independente
- Executar
- Registrar PASS/FAIL

### 7. Validação
- Verificar efetividade
- Verificar regressões
- Atualizar documentação

### 8. Commit e Push
- Commit final
- Push para branch
- Atualizar changelog

## Metadata de Melhoria

Cada recurso melhorado deve ter:
```yaml
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "descrição"
test_result: "PASS"
```

## Generatividade

Melhorias não são apenas correções — são **criação de novas capacidades**:
- Combinar recursos existentes de formas novas
- Antecipar necessidades futuras
- Automatizar padrões recorrentes

## Feedback-Driven Improvement (CRÍTICO)

### O que é?
Melhoria baseada em feedback real do usuário durante o uso. Não é melhoria teórica — é melhoria que acontece quando o usuário diz "isso não funciona" ou "pode ser melhor".

### Como funciona?
1. **Usuário usa o recurso** (skill, hook, instrução, artefato)
2. **Usuário dá feedback** (positivo, negativo, ou sugestão de melhoria)
3. **Agente analisa o feedback** e identifica o gap
4. **Agente implementa a melhoria** no recurso
5. **Agente testa** se a melhoria resolve o feedback
6. **Agente marca** o recurso com metadata de melhoria
7. **Agente commita e pusha** para o repositório

### Exemplos de feedback-driven improvement:
- "balão de artifacts é genérico" → Adicionar 10 regras de criatividade
- "botão de explorer não funciona" → Adicionar regra de exibibilidade
- "não desperta meu interesse" → Redesign com hero dramático, urgência, gamificação
- "ta todo bugado" → Corrigir layout, animações, interatividade

### Regra de ouro:
> Se o usuário deu feedback, a melhoria DEVE ser implementada no pacote de recursos.
> Não apenas respondida na conversa — implementada no repo.

## Multi-Device Contribution Flow

### Cenário: 3 dispositivos em momentos diferentes
```
Dispositivo A (manhã)     Dispositivo B (tarde)     Dispositivo C (noite)
       |                        |                        |
   usa + feedback            usa + feedback          usa + feedback
       |                        |                        |
   melhora recurso           melhora recurso         melhora recurso
       |                        |                        |
   commit + push staging     commit + push staging    commit + push staging
       |                        |                        |
       v                        v                        v
   origin/staging  <--------  origin/staging  -------->  origin/staging
       |                        |                        |
       v                        v                        v
   origin/main (promovido quando 3+ usos sem feedback negativo)
```

### Fluxo de contribuição:
1. **Dispositivo usa recurso** → identifica gap ou oportunidade
2. **Agente melhora o recurso** → implementa a melhoria
3. **Agente marca como `marked`** → commit em `staging`
4. **Outros dispositivos recebem** → via auto-sync (a cada hora)
5. **Uso bem-sucedido** → incrementa `usage_count`
6. **3+ usos sem feedback negativo** → promove para `main` (estado `validated`)
7. **7+ usos sem feedback negativo** → promove para `proactive` (auto-aplicado)

## Auto-Observacao Negativa (CRITICO)

### O que e?
O agente observa suas proprias limitacoes, erros e incertezas e as registra
como feedback negativo para auto-melhoria, sem depender do usuario.

### Como funciona?
1. O agente gera uma resposta
2. O hook self-observation.py analisa a resposta
3. Se padroes negativos sao detectados, registra em validation.json
4. Se 2+ observacoes negativas -> recurso e revertido para raw
5. O agente analisa o gap -> implementa melhoria
6. Autoteste valida -> marca como melhorado
7. Commit + Push -> Sync para outros dispositivos

### Padroes detectados:
- Erro admissao, Incerteza, Retrabalho, Limitacao

### Diferenca: Feedback do Usuario vs Auto-Observacao
| Aspecto | Feedback do Usuario | Auto-Observacao |
|---|---|---|
| Origem | Usuario diz "isso nao funciona" | Agente admite "nao funciona" |
| Dependencia | Depende do usuario | Autonomo |
| Velocidade | Lenta | Rapida (imediata) |
| Cobertura | Apenas o que o usuario ve | Tudo que o agente admite |

## Changelog

### 2026-10-28 — v1.1
- Criado AGENTS.md (instruções globais)
- Criado skill functional-ui
- Criado skill creative-design
- Criado skill self-upgrade
- Criado hook pre-tool-use-security.sh
- Criado config mcp.example.json
- Criado notes/conversation-insights.md
- Criado docs/self-upgrade-protocol.md
- 7 artefatos HTML criados e testados

### 2026-10-28 — v1.0 (inicial)
- Scaffold do projeto
- 1 artefato (cte-dashboard-estoque.html)
