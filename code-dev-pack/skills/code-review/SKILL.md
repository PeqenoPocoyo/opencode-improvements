---
name: code-review
description: Code review automático e assistido. Analisa diffs, identifica bugs, vulnerabilidades, code smells e sugere melhorias. Use quando revisar PRs, diffs, commits ou código colado. Integra com autoteste para validação de mudanças.
---

# Code Review — Skill

## Princípio Central
**Revisão não é aprovação.** É análise crítica que identifica problemas antes de chegar à produção.

## Checklist de Review

### 1. Segurança
- [ ] Sem SQL injection (queries parametrizadas)
- [ ] Sem XSS (sanitização de output)
- [ ] Sem command injection (execução de comandos segura)
- [ ] Sem secrets hardcoded (API keys, tokens, senhas)
- [ ] Autenticação/autorização verificadas
- [ ] Inputs validados e sanitizados

### 2. Corretude
- [ ] Lógica está correta?
- [ ] Edge cases cobertos?
- [ ] Tratamento de erros adequado?
- [ ] Race conditions?
- [ ] Null/undefined tratados?

### 3. Performance
- [ ] Sem N+1 queries
- [ ] Sem loops desnecessários
- [ ] Sem memory leaks
- [ ] Caching adequado
- [ ] Lazy loading quando aplicável

### 4. Manutenibilidade
- [ ] Código legível (nomes claros, funções pequenas)
- [ ] Sem duplicação (DRY)
- [ ] Sem complexidade desnecessária (KISS)
- [ ] Comentários para decisões não-óbvias
- [ ] Testes atualizados

### 5. Estilo
- [ ] Segue padrões do projeto (lint, format)
- [ ] Nomenclatura consistente
- [ ] Imports organizados
- [ ] Sem código morto

## Severidade de Findings

| Severidade | Descrição | Ação |
|---|---|---|
| **BLOCKER** | Bug crítico, vulnerabilidade, perda de dados | Bloquear merge |
| **MAJOR** | Bug não-crítico, code smell grave | Solicitar correção |
| **MINOR** | Melhoria de qualidade | Sugerir, não bloquear |
| **NIT** | Estilo, preferência | Opcional |

## Formato de Review

### Por arquivo
```
## src/auth/login.ts

### BLOCKER
- Linha 42: SQL injection — query não parametrizada
  - Fix: usar prepared statement

### MAJOR
- Linha 78: Senha em texto plano no log
  - Fix: remover log ou mascarar

### MINOR
- Linha 15: Função muito longa (45 linhas)
  - Suggest: extrair para funções menores

### NIT
- Linha 3: Import não utilizado
  - Fix: remover
```

### Resumo
```
## Resumo do Review

**Veredicto**: REQUEST_CHANGES (1 BLOCKER, 2 MAJOR, 3 MINOR, 1 NIT)

**Pontos positivos**:
- Boa cobertura de testes
- Código bem estruturado

**Pontos de atenção**:
- Segurança: SQL injection na linha 42
- Performance: N+1 query na linha 90

**Recomendação**: Corrigir BLOCKER e MAJOR antes de merge.
```

## Teste de Reinterpretação

### Cenário: Review sem findings
```
DADO um código com vulnerabilidade conhecida (SQL injection)
QUANDO o review é executado
ENTÃO deve identificar a vulnerabilidade
SE não identificar → FAIL (review não funciona)
```

### Cenário: Review com falso positivo
```
DADO um código seguro (prepared statement)
QUANDO o review é executado
ENTÃO não deve reportar vulnerabilidade
SE reportar → FAIL (falso positivo)
```

## Autoteste

```bash
# Revisar um diff
python scripts/autotest.py --review --diff <file>

# Revisar um arquivo
python scripts/autotest.py --review --file <path>

# Verificar cobertura de review
python scripts/coverage-check.py --review
```

## Integração com Multi-Device

- Reviews são commitados junto com o código
- Outros dispositivos recebem as findings via sync
- Se uma finding é corrigida → incrementa usage_count
- 3+ reviews sem falso positivo → promove para proactive

## Metadata
- **Categoria**: Desenvolvimento/Review
- **Prioridade**: Alta
- **Aplicável a**: Qualquer linguagem de programação
- **Dependências**: code-tdd, code-refactor
- **Versão**: 1.0
- **Criado**: 2026-10-28