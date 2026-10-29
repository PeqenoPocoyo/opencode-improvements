---
name: code-test-gen
description: Geração automática de testes. Analisa código existente e gera testes unitários, de integração e edge cases. Usa padrões AAA, nomenclatura descritiva e cobertura de branches. Use quando precisar aumentar cobertura, testar código legado ou gerar testes para novas funcionalidades. Integra com autoteste para validação.
---

# Code Test Gen — Skill

## Princípio Central
**Testes não são opcionais.** São a especificação executável do comportamento esperado.

## Tipos de Teste Gerados

### 1. Testes Unitários
- Testam uma função/método isoladamente
- Mock de dependências externas
- Cobertura de branches (if/else, try/catch)

### 2. Testes de Integração
- Testam interação entre componentes
- Usam dependências reais (banco, API)
- Verificam fluxo completo

### 3. Testes de Edge Cases
- Valores limite (0, -1, MAX, MIN)
- Inputs vazios (null, undefined, "", [])
- Inputs inválidos (tipo errado, formato errado)
- Concorrência (race conditions)

### 4. Testes de Regressão
- Testes que reproduzem bugs corrigidos
- Previne que o bug volte

## Padrão de Geração

### Passo 1: Análise do Código
```
1. Identificar funções/métodos públicos
2. Identificar parâmetros e tipos de retorno
3. Identificar branches (if/else, switch, try/catch)
4. Identificar dependências (imports, chamadas externas)
5. Identificar edge cases (null, empty, boundary)
```

### Passo 2: Geração de Testes
```
Para cada função/método:
1. Happy path (caso de sucesso)
2. Edge cases (valores limite)
3. Error cases (inputs inválidos)
4. Branch coverage (cada if/else)
```

### Passo 3: Validação
```
1. Executar todos os testes gerados
2. Verificar que passam
3. Verificar cobertura (target: 80%+)
4. Se algum teste falha → analisar e corrigir
```

## Template de Teste (Python/pytest)

```python
import pytest
from module import function_under_test

class TestFunctionUnderTest:
    """Testes para function_under_test."""

    def test_happy_path(self):
        """Caso de sucesso com input válido."""
        # Arrange
        input_data = {"key": "value"}
        # Act
        result = function_under_test(input_data)
        # Assert
        assert result == expected_value

    def test_empty_input(self):
        """Input vazio retorna valor padrão."""
        result = function_under_test({})
        assert result == default_value

    def test_null_input(self):
        """Input null lança exceção."""
        with pytest.raises(ValueError):
            function_under_test(None)

    def test_invalid_type(self):
        """Input de tipo errado lança exceção."""
        with pytest.raises(TypeError):
            function_under_test("string_instead_of_dict")

    def test_boundary_value(self):
        """Valor limite é tratado corretamente."""
        result = function_under_test({"key": MAX_VALUE})
        assert result == expected_boundary_result
```

## Template de Teste (JavaScript/Jest)

```javascript
describe('functionUnderTest', () => {
  it('should return expected value for valid input', () => {
    // Arrange
    const input = { key: 'value' };
    // Act
    const result = functionUnderTest(input);
    // Assert
    expect(result).toBe(expectedValue);
  });

  it('should handle empty input', () => {
    const result = functionUnderTest({});
    expect(result).toBe(defaultValue);
  });

  it('should throw for null input', () => {
    expect(() => functionUnderTest(null)).toThrow();
  });

  it('should handle boundary values', () => {
    const result = functionUnderTest({ key: MAX_VALUE });
    expect(result).toBe(expectedBoundaryResult);
  });
});
```

## Nomenclatura de Testes

```
test_<o_que>_<condicao>_<resultado_esperado>

Exemplos:
- test_calculate_total_with_discount_returns_reduced_price
- test_validate_email_with_invalid_format_returns_false
- test_create_user_with_duplicate_email_raises_error
- test_process_order_with_empty_items_returns_zero
```

## Cobertura de Branches

Para cada função, gerar testes para:
- Cada `if` (true e false)
- Cada `elif` / `else if`
- Cada `else`
- Cada `case` em switch/match
- Cada `except` / `catch`
- Cada `finally`

## Teste de Reinterpretação

### Cenário: Teste gerado não passa
```
DADO um teste gerado automaticamente
QUANDO executado
ENTÃO deve passar (se o código está correto)
SE falhar → analisar se é bug no código ou no teste
```

### Cenário: Cobertura insuficiente
```
DADO um conjunto de testes gerados
QUANDO a cobertura é medida
ENTÃO deve ser >= 80%
SE < 80% → gerar mais testes
```

## Autoteste

```bash
# Gerar testes para um arquivo
python scripts/autotest.py --test-gen --file <path>

# Gerar testes para um diretório
python scripts/autotest.py --test-gen --dir <path>

# Verificar cobertura após geração
python scripts/coverage-check.py --min 80
```

## Integração com Multi-Device

- Testes gerados são commitados junto com o código
- Outros dispositivos recebem via sync
- Se teste gerado falha em outro dispositivo → feedback negativo
- 3+ gerações sem falha → promove para proactive

## Metadata
- **Categoria**: Desenvolvimento/Testes
- **Prioridade**: Alta
- **Aplicável a**: Qualquer linguagem de programação
- **Dependências**: code-tdd, code-review
- **Versão**: 1.0
- **Criado**: 2026-10-28