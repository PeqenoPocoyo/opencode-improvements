# Padrões de Teste

## Princípio Central
**Testes são a especificação executável.** Se não tem teste, não existe.

## 1. Tipos de Teste

### Unitário
- Testa uma função/método isoladamente
- Mock de dependências externas
- Rápido (milissegundos)
- Determinístico (mesmo resultado sempre)

### Integração
- Testa interação entre componentes
- Usa dependências reais (banco, API)
- Mais lento (segundos)
- Pode ser não-determinístico

### E2E (End-to-End)
- Testa fluxo completo do usuário
- Usa browser/API real
- Lento (minutos)
- Frágil (depende de UI)

### Performance
- Mede tempo de resposta
- Mede uso de memória
- Mede throughput
- Comparação com baseline

## 2. Estrutura de Teste

### Padrão AAA
```python
def test_calculate_total_with_discount():
    # Arrange — preparar dados
    items = [Item(price=10, qty=2), Item(price=5, qty=1)]
    discount = 0.1
    
    # Act — executar a função
    total = calculate_total(items, discount)
    
    # Assert — verificar resultado
    assert total == 22.5
```

### Nomenclatura
```
test_<o_que>_<condicao>_<resultado_esperado>

Exemplos:
- test_calculate_total_with_discount_returns_reduced_price
- test_validate_email_with_invalid_format_returns_false
- test_create_user_with_duplicate_email_raises_error
- test_process_order_with_empty_items_returns_zero
```

## 3. Cobertura

### Métricas
- **Line coverage**: % de linhas executadas
- **Branch coverage**: % de branches (if/else) testados
- **Function coverage**: % de funções testadas

### Targets
- Código de produção: 80%+ line, 70%+ branch
- Código crítico (auth, pagamento): 100% line, 90%+ branch
- Código de teste: não medir

### O que NÃO testar
- Getters/setters triviais
- Código de terceiros (libs)
- Configuração estática
- Código de debug/logging

## 4. Mocking

### Quando usar
- Dependências externas (API, banco, filesystem)
- Código não-determinístico (random, time, network)
- Código lento (I/O, processamento pesado)

### Quando NÃO usar
- Lógica de negócio (testar com dados reais)
- Código puro (sem side effects)
- Código que já é rápido e determinístico

### Padrão
```python
from unittest.mock import patch, MagicMock

def test_send_email():
    with patch('email_service.send') as mock_send:
        mock_send.return_value = True
        result = notify_user('user@example.com', 'Hello')
        assert result is True
        mock_send.assert_called_once_with('user@example.com', 'Hello')
```

## 5. Fixtures

### Uso
- Dados de teste reutilizáveis
- Setup/teardown automático
- Isolamento entre testes

### Exemplo (pytest)
```python
import pytest

@pytest.fixture
def sample_user():
    return User(name="Test", email="test@example.com")

@pytest.fixture
def db_session():
    session = create_session()
    yield session
    session.rollback()
    session.close()

def test_create_user(db_session, sample_user):
    db_session.add(sample_user)
    db_session.commit()
    assert sample_user.id is not None
```

## 6. Testes de Edge Cases

### Valores limite
- 0, 1, -1
- MAX_INT, MIN_INT
- Empty string, None, null
- Empty list, single item, many items

### Inputs inválidos
- Tipo errado (string em vez de int)
- Formato errado (email sem @)
- Tamanho errado (string muito longa/curta)
- Caracteres especiais (SQL injection, XSS)

### Concorrência
- Múltiplas threads
- Race conditions
- Deadlocks

## 7. Testes de Regressão

### Quando criar
- Bug corrigido → teste que reproduz o bug
- Feature nova → testes de aceitação
- Refactoring → testes de caracterização

### Nomenclatura
```
test_regression_<issue_number>_<descricao>
```

## 8. Testes de Performance

### Métricas
- Tempo de resposta (p50, p95, p99)
- Throughput (requests/segundo)
- Uso de memória (MB)
- Uso de CPU (%)

### Baseline
- Estabelecer baseline antes de otimizar
- Comparar após mudanças
- Alertar se degradação > 10%

## Metadata
- **Categoria**: Desenvolvimento/Testes
- **Prioridade**: Alta
- **Aplicável a**: Qualquer linguagem de programação
- **Versão**: 1.0
- **Criado**: 2026-10-28