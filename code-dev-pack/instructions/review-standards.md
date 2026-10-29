# Padrões de Code Review

## Princípio Central
**Review não é aprovação.** É análise crítica que identifica problemas antes de chegar à produção.

## 1. Checklist de Review

### Segurança
- [ ] Sem SQL injection (queries parametrizadas)
- [ ] Sem XSS (sanitização de output)
- [ ] Sem command injection
- [ ] Sem secrets hardcoded
- [ ] Autenticação/autorização verificadas
- [ ] Inputs validados e sanitizados

### Corretude
- [ ] Lógica está correta?
- [ ] Edge cases cobertos?
- [ ] Tratamento de erros adequado?
- [ ] Race conditions?
- [ ] Null/undefined tratados?

### Performance
- [ ] Sem N+1 queries
- [ ] Sem loops desnecessários
- [ ] Sem memory leaks
- [ ] Caching adequado
- [ ] Lazy loading quando aplicável

### Manutenibilidade
- [ ] Código legível (nomes claros, funções pequenas)
- [ ] Sem duplicação (DRY)
- [ ] Sem complexidade desnecessária (KISS)
- [ ] Comentários para decisões não-óbvias
- [ ] Testes atualizados

### Estilo
- [ ] Segue padrões do projeto (lint, format)
- [ ] Nomenclatura consistente
- [ ] Imports organizados
- [ ] Sem código morto

## 2. Severidade de Findings

| Severidade | Descrição | Ação |
|---|---|---|
| **BLOCKER** | Bug crítico, vulnerabilidade, perda de dados | Bloquear merge |
| **MAJOR** | Bug não-crítico, code smell grave | Solicitar correção |
| **MINOR** | Melhoria de qualidade | Sugerir, não bloquear |
| **NIT** | Estilo, preferência | Opcional |

## 3. Formato de Review

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

## 4. Regras de Review

### O que verificar
- Corretude da lógica
- Cobertura de testes
- Segurança (OWASP Top 10)
- Performance (N+1, memory leaks)
- Manutenibilidade (DRY, KISS, SRP)
- Estilo (lint, format, nomenclatura)

### O que NÃO verificar
- Preferências pessoais de estilo (se não está no lint)
- Micro-otimizações prematuras
- Refatorações grandes (sugerir separadamente)

### Tom
- Construtivo, não destrutivo
- Explicar o "por quê", não apenas o "o quê"
- Sugerir soluções, não apenas apontar problemas
- Reconhecer código bom

## 5. Autoteste de Review

### Teste de Reinterpretação
```
DADO um código com vulnerabilidade conhecida (SQL injection)
QUANDO o review é executado
ENTÃO deve identificar a vulnerabilidade
SE não identificar → FAIL (review não funciona)
```

### Teste de Falso Positivo
```
DADO um código seguro (prepared statement)
QUANDO o review é executado
ENTÃO não deve reportar vulnerabilidade
SE reportar → FAIL (falso positivo)
```

## Metadata
- **Categoria**: Desenvolvimento/Review
- **Prioridade**: Alta
- **Aplicável a**: Qualquer linguagem de programação
- **Versão**: 1.0
- **Criado**: 2026-10-28