---
name: code-debug
description: Debugging sistemático de código. Guia investigação de bugs com método científico: reproduzir, isolar, diagnosticar, corrigir, verificar. Inclui técnicas de logging, breakpoints, tracing e análise de stack traces. Use quando investigar bugs, erros ou comportamento inesperado. Integra com autoteste para validação da correção.
---

# Code Debug — Skill

## Princípio Central
**Debugging não é tentativa e erro.** É investigação sistemática com método científico.

## Método Científico de Debugging

### 1. Reproduzir
```
1. Obter passos exatos para reproduzir o bug
2. Reproduzir consistentemente (100% das vezes)
3. Se não reproduzir → coletar mais informações
4. Documentar: input, output esperado, output obtido
```

### 2. Isolar
```
1. Reduzir o caso de teste ao mínimo
2. Remover dependências externas
3. Criar teste unitário que reproduz o bug
4. Se o teste não reproduz → o bug está na integração
```

### 3. Diagnosticar
```
1. Formular hipóteses sobre a causa
2. Testar cada hipótese com experimentos
3. Usar logging, breakpoints, tracing
4. Analisar stack traces e error messages
```

### 4. Corrigir
```
1. Implementar a correção mínima
2. Não refatorar junto com a correção
3. Adicionar teste que previne regressão
4. Verificar que o teste original passa
```

### 5. Verificar
```
1. Rodar todos os testes (não apenas o do bug)
2. Verificar que não introduziu novos bugs
3. Testar edge cases relacionados
4. Code review da correção
```

## Técnicas de Debugging

### Logging Estruturado
```python
import logging
logging.basicConfig(level=logging.DEBUG)

def process_order(order):
    logging.debug(f"Processing order: {order.id}")
    logging.debug(f"Items: {len(order.items)}")
    try:
        result = calculate_total(order)
        logging.debug(f"Total calculated: {result}")
        return result
    except Exception as e:
        logging.error(f"Error calculating total: {e}", exc_info=True)
        raise
```

### Breakpoints (pdb)
```python
import pdb

def complex_function(data):
    pdb.set_trace()  # Para aqui
    # investigar variáveis
    # n (next), s (step), c (continue), p (print)
    return result
```

### Tracing
```python
import trace
tracer = trace.Trace(trace=1, count=1)
tracer.run('main()')
```

### Análise de Stack Trace
```
1. Ler de baixo para cima (origem do erro)
2. Identificar a função onde o erro ocorreu
3. Verificar os parâmetros passados
4. Verificar o estado das variáveis
5. Procurar por padrões (null, undefined, tipo errado)
```

## Tipos de Bugs Comuns

### 1. Off-by-one
```python
# Bug: loop vai até len(items) (exclusivo, perde último)
for i in range(len(items)):  # OK
for i in range(len(items) - 1):  # BUG: perde último item
```

### 2. Null/None
```python
# Bug: não verifica None
def get_name(user):
    return user.name  # BUG se user is None

# Fix
def get_name(user):
    if user is None:
        return None
    return user.name
```

### 3. Tipo errado
```python
# Bug: string + int
def add(a, b):
    return a + b  # BUG se a é string e b é int

# Fix
def add(a, b):
    return int(a) + int(b)
```

### 4. Race condition
```python
# Bug: duas threads modificam mesma variável
counter = 0
def increment():
    global counter
    counter += 1  # BUG: não atômico

# Fix
import threading
lock = threading.Lock()
def increment():
    global counter
    with lock:
        counter += 1
```

### 5. Memory leak
```python
# Bug: referência circular
class Node:
    def __init__(self):
        self.children = []
        self.parent = None

# Fix: usar weakref
import weakref
class Node:
    def __init__(self):
        self.children = []
        self._parent = None
    @property
    def parent(self):
        return self._parent() if self._parent else None
    @parent.setter
    def parent(self, value):
        self._parent = weakref.ref(value) if value else None
```

## Teste de Reinterpretação

### Cenário: Bug não reproduzível
```
DADO um bug reportado mas não reproduzível
QUANDO o debugging é aplicado
ENTÃO deve coletar mais informações (logs, ambiente, steps)
SE tentar corrigir sem reproduzir → FAIL (risco alto)
```

### Cenário: Correção que introduz novo bug
```
DADO uma correção implementada
QUANDO todos os testes são executados
ENTÃO nenhum teste deve falhar
SE algum teste falhar → FAIL (regressão)
```

## Autoteste

```bash
# Reproduzir bug
python scripts/autotest.py --debug --reproduce <test_case>

# Verificar correção
python scripts/autotest.py --debug --verify <test_case>

# Rodar todos os testes
python scripts/autotest.py --debug --all
```

## Integração com Multi-Device

- Bugs são reportados com steps de reprodução
- Correções são commitadas com mensagem `fix: <descrição>`
- Outros dispositivos recebem via sync
- Se correção não funciona em outro dispositivo → feedback negativo

## Metadata
- **Categoria**: Desenvolvimento/Debugging
- **Prioridade**: Alta
- **Aplicável a**: Qualquer linguagem de programação
- **Dependências**: code-tdd, code-review
- **Versão**: 1.0
- **Criado**: 2026-10-28