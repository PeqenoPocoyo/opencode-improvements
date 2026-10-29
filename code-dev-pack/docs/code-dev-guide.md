# Guia de Desenvolvimento de Código

## Visão Geral
Este guia descreve como usar o pacote `code-dev-pack` para desenvolvimento de código
com suporte a autoteste e auto-melhoria.

## Estrutura do Pacote

```
code-dev-pack/
├── skills/          # 5 skills de desenvolvimento
├── hooks/           # 4 hooks de autoteste
├── instructions/    # 3 instruções de qualidade
├── scripts/         # 1 script de autoteste
├── configs/         # 2 configs (teste + qualidade)
└── docs/            # 2 documentos (guia + auto-melhoria)
```

## Skills Disponíveis

### code-tdd
Test-Driven Development. Ciclo Red-Green-Refactor.
- Use quando: escrever novas funcionalidades, corrigir bugs, refatorar
- Trigger: "TDD", "teste primeiro", "red-green-refactor"

### code-review
Code review automático e assistido.
- Use quando: revisar PRs, diffs, commits, código colado
- Trigger: "review", "code review", "revisar código"

### code-refactor
Refactoring assistido de código.
- Use quando: melhorar código existente sem mudar comportamento
- Trigger: "refactor", "refatorar", "code smell"

### code-debug
Debugging sistemático com método científico.
- Use quando: investigar bugs, erros, comportamento inesperado
- Trigger: "debug", "bug", "erro", "investigar"

### code-test-gen
Geração automática de testes.
- Use quando: aumentar cobertura, testar código legado, gerar testes
- Trigger: "gerar testes", "aumentar cobertura", "test gen"

## Hooks de Autoteste

### pre-write-quality.py
Valida código antes de escrever (secrets, complexidade, testes).
- Fail-open: nunca quebra a sessão
- Reporta warnings no stderr

### post-write-test.py
Roda testes após mudança.
- Encontra arquivo de teste correspondente
- Executa testes (pytest/jest)
- Reporta resultado

## Scripts

### autotest.py
Runner de autoteste para validar recursos do pacote.
```bash
# Testar todos
python scripts/autotest.py --all

# Testar uma skill
python scripts/autotest.py --skill code-tdd

# Testar um hook
python scripts/autotest.py --hook pre-write-quality

# Testar um recurso
python scripts/autotest.py --resource skills/code-tdd/SKILL.md
```

## Fluxo de Desenvolvimento

### 1. Escrever código (TDD)
```
1. Escrever teste (RED)
2. Escrever código mínimo (GREEN)
3. Refatorar (REFACTOR)
4. Rodar autoteste
```

### 2. Revisar código
```
1. Executar code-review
2. Corrigir findings (BLOCKER, MAJOR)
3. Re-executar review
4. Aprovar quando limpo
```

### 3. Refatorar
```
1. Identificar code smells
2. Aplicar refactoring
3. Rodar testes (devem passar)
4. Commit com "refactor: <descrição>"
```

### 4. Debugar
```
1. Reproduzir o bug
2. Isolar (teste mínimo)
3. Diagnosticar (hipóteses)
4. Corrigir (mínimo)
5. Verificar (todos os testes)
```

### 5. Gerar testes
```
1. Analisar código existente
2. Gerar testes (unit, integration, edge cases)
3. Executar testes
4. Verificar cobertura (>= 80%)
```

## Auto-Melhoria

### Feedback-Driven
Quando o usuário der feedback:
1. Analisar o feedback
2. Implementar a melhoria
3. Testar (autoteste)
4. Marcar como melhorado
5. Commit e push

### Multi-Device
- Cada dispositivo pode melhorar recursos
- Melhorias são commitadas em staging
- Outros dispositivos recebem via auto-sync
- 3+ usos sem feedback negativo → promove para main

## Metadata
- **Versão**: 1.0
- **Criado**: 2026-10-28
- **Pacote**: code-dev-pack
- **Objetivo**: Desenvolvimento de código com autoteste e auto-melhoria