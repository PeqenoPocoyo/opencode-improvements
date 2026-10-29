---
name: code-tdd
description: Test-Driven Development para desenvolvimento de código. Guia o ciclo Red-Green-Refactor, gera testes antes do código, valida cobertura e qualidade. Use quando escrever novas funcionalidades, corrigir bugs, ou refatorar código existente. Integra com autoteste para validação contínua.
---

# Code TDD — Test-Driven Development

## Princípio Central
**Escreva o teste antes do código.** O teste define o comportamento esperado. O código existe para fazer o teste passar.

## Ciclo Red-Green-Refactor

### 1. RED — Escrever teste que falha
```
1. Escrever um teste para a funcionalidade desejada
2. Executar o teste → deve FALHAR (red)
3. Se o teste passar → o teste está errado ou a funcionalidade já existe
```

### 2. GREEN — Escrever código mínimo
```
1. Escrever o código MÍNIMO para fazer o teste passar
2. Não otimizar, não refatorar, não adicionar extras
3. Executar o teste → deve PASSAR (green)
```

### 3. REFACTOR — Melhorar o código
```
1. Refatorar o código (sem mudar comportamento)
2. Executar todos os testes → devem continuar passando
3. Se algum teste falhar → a refatoração quebrou algo
```

## Regras de TDD

### Regra 1: Teste antes do código
- Nunca escrever código sem um teste correspondente
- O teste define o contrato, o código implementa

### Regra 2: Um teste por vez
- Escrever um teste, fazer passar, refatorar
- Não escrever múltiplos testes de uma vez

### Regra 3: Código mínimo
- Escrever apenas o necessário para passar o teste
- Não adicionar funcionalidades não testadas

### Regra 4: Testes rápidos
- Testes devem rodar em milissegundos
- Testes lentos não são TDD

### Regra 5: Testes independentes
- Cada teste deve ser independente
- Ordem de execução não importa

## Estrutura de Teste

### Padrão AAA (Arrange, Act, Assert)
```python
def test_something():
    # Arrange — preparar dados
    input_data = {"key": "value"}
    
    # Act — executar a função
    result = function_under_test(input_data)
    
    # Assert — verificar resultado
    assert result == expected_value
```

### Nomenclatura de Testes
```
test_<o_que>_<condicao>_<resultado_esperado>

Exemplos:
- test_calculate_total_with_discount_returns_reduced_price
- test_validate_email_with_invalid_format_returns_false
- test_create_user_with_duplicate_email_raises_error
```

## Cobertura de Teste

### O que testar:
- Happy path (caso de sucesso)
- Edge cases (valores limite, vazio, null)
- Error cases (inputs inválidos, exceções)
- Integração (interação entre componentes)

### O que NÃO testar:
- Getters/setters triviais
- Código de terceiros (libs)
- Configuração estática

### Métricas:
- **Line coverage**: % de linhas executadas
- **Branch coverage**: % de branches (if/else) testados
- **Target**: 80%+ para código de produção

## Teste de Reinterpretação

### Cenário: Novo método sem teste
```
DADO um novo método sem teste correspondente
QUANDO o desenvolvedor tenta commitar
ENTÃO o hook de pre-commit deve bloquear
SE o commit passar sem teste → FAIL
```

### Cenário: Teste que passa sem código
```
DADO um teste que passa sem implementação
QUANDO o teste é executado
ENTÃO deve falhar (teste está errado)
SE passar → FAIL (teste inválido)
```

## Autoteste

```bash
# Rodar todos os testes
python scripts/autotest.py --suite all

# Rodar testes de uma skill específica
python scripts/autotest.py --skill code-tdd

# Verificar cobertura
python scripts/coverage-check.py --min 80
```

## Integração com Multi-Device

- Testes são commitados junto com o código
- Outros dispositivos recebem os testes via sync
- Se um teste falha em outro dispositivo → feedback negativo
- 2+ falhas → reverter para raw

## Metadata
- **Categoria**: Desenvolvimento/Testes
- **Prioridade**: Crítica
- **Aplicável a**: Qualquer linguagem de programação
- **Dependências**: code-test-gen, code-review
- **Versão**: 1.0
- **Criado**: 2026-10-28