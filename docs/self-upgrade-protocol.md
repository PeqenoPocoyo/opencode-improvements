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
