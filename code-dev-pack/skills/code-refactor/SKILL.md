---
name: code-refactor
description: Refactoring assistido de código. Identifica code smells, sugere refatorações, aplica transformações seguras (extract method, rename, inline, etc.) e valida que testes continuam passando. Use quando melhorar código existente sem mudar comportamento. Integra com autoteste para validação.
---

# Code Refactor — Skill

## Princípio Central
**Refactoring não muda comportamento.** Muda estrutura. Se o comportamento muda, não é refactoring — é feature ou bug.

## Code Smells (sinais de refactoring necessário)

### 1. Métodos longos
- **Sintoma**: Método com mais de 20 linhas
- **Refactoring**: Extract Method
- **Teste**: Método original e extraído produzem mesmo resultado

### 2. Classes grandes
- **Sintoma**: Classe com mais de 300 linhas ou 10+ métodos
- **Refactoring**: Extract Class
- **Teste**: Comportamento externo não muda

### 3. Duplicação
- **Sintoma**: Mesmo código em 2+ lugares
- **Refactoring**: Extract Method/Class
- **Teste**: Ambos os caminhos produzem mesmo resultado

### 4. Nomes ruins
- **Sintoma**: Variáveis/métodos com nomes genéricos (data, temp, x)
- **Refactoring**: Rename
- **Teste**: Compilação passa, testes passam

### 5. Condicionais complexas
- **Sintoma**: if/else aninhado 3+ níveis
- **Refactoring**: Guard Clauses, Strategy Pattern
- **Teste**: Todos os branches testados

### 6. Feature Envy
- **Sintoma**: Método usa mais dados de outra classe
- **Refactoring**: Move Method
- **Teste**: Comportamento não muda

## Catálogo de Refactorings

### Extract Method
```python
# Antes
def process_order(order):
    # calcular total
    total = 0
    for item in order.items:
        total += item.price * item.quantity
    # aplicar desconto
    if order.customer.is_premium:
        total *= 0.9
    # salvar
    db.save(order, total)
    return total

# Depois
def calculate_total(order):
    total = sum(item.price * item.quantity for item in order.items)
    if order.customer.is_premium:
        total *= 0.9
    return total

def process_order(order):
    total = calculate_total(order)
    db.save(order, total)
    return total
```

### Guard Clauses
```python
# Antes
def get_payment_status(order):
    if order is not None:
        if order.is_paid:
            if order.is_shipped:
                return "completed"
            else:
                return "paid"
        else:
            return "pending"
    else:
        return "invalid"

# Depois
def get_payment_status(order):
    if order is None:
        return "invalid"
    if not order.is_paid:
        return "pending"
    if not order.is_shipped:
        return "paid"
    return "completed"
```

### Rename
```python
# Antes
def calc(d, r):
    return d * (1 + r)

# Depois
def calculate_total_with_tax(amount, tax_rate):
    return amount * (1 + tax_rate)
```

## Teste de Reinterpretação

### Cenário: Refactoring que muda comportamento
```
DADO um refactoring aplicado
QUANDO os testes são executados
ENTÃO todos os testes devem passar
SE algum teste falhar → FAIL (comportamento mudou)
```

### Cenário: Refactoring sem teste
```
DADO um código sem testes
QUANDO refactoring é solicitado
ENTÃO deve sugerir escrever testes primeiro
SE refatorar sem testes → FAIL (risco alto)
```

## Autoteste

```bash
# Analisar code smells
python scripts/autotest.py --refactor --analyze <file>

# Aplicar refactoring específico
python scripts/autotest.py --refactor --apply extract-method --file <path>

# Verificar que testes passam após refactoring
python scripts/autotest.py --refactor --verify
```

## Regras de Segurança

1. **Sempre rodar testes antes e depois** do refactoring
2. **Nunca refatorar e adicionar feature ao mesmo tempo**
3. **Commits pequenos** — um refactoring por commit
4. **Se testes falharem** — reverter imediatamente

## Integração com Multi-Device

- Refactorings são commitados com mensagem `refactor: <descrição>`
- Outros dispositivos recebem via sync
- Se refactoring quebra testes em outro dispositivo → feedback negativo

## Metadata
- **Categoria**: Desenvolvimento/Refactoring
- **Prioridade**: Alta
- **Aplicável a**: Qualquer linguagem de programação
- **Dependências**: code-tdd, code-review
- **Versão**: 1.0
- **Criado**: 2026-10-28