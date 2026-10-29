# Padrões de Qualidade de Código

## Princípio Central
**Código de qualidade não é código que funciona.** É código que funciona, é legível, é testável e é manutenível.

## 1. Nomenclatura

### Variáveis
- Nomes descritivos (não `x`, `temp`, `data`)
- Booleanos: prefixo `is_`, `has_`, `can_`, `should_`
- Listas/arrays: plural (`users`, `items`)
- Dicionários/maps: `user_by_id`, `config_map`

### Funções/Métodos
- Verbos: `calculate_total`, `validate_email`, `get_user`
- Máximo 20 linhas por função
- Máximo 3 parâmetros (usar objeto se mais)
- Um nível de abstração por função

### Classes
- Substantivos: `User`, `OrderProcessor`, `PaymentGateway`
- Máximo 300 linhas
- Máximo 10 métodos públicos
- Responsabilidade única (SRP)

## 2. Estrutura

### Organização de Arquivos
```
src/
├── models/          # Entidades de domínio
├── services/        # Lógica de negócio
├── repositories/    # Acesso a dados
├── controllers/     # Interface (API, CLI)
├── utils/           # Utilitários
└── config/          # Configuração
```

### Imports
- Standard library primeiro
- Third-party depois
- Local por último
- Ordenados alfabeticamente dentro de cada grupo

### Comentários
- Código deve ser auto-explicativo
- Comentar decisões não-óbvias
- Comentar "por quê", não "o quê"
- TODO/FIXME com issue reference

## 3. Tratamento de Erros

### Regras
- Nunca engolir exceções silenciosamente
- Usar exceções específicas (não genéricas)
- Logar com contexto suficiente
- Fail-fast: validar inputs no início

### Padrão
```python
def process_order(order_id):
    if not order_id:
        raise ValueError("order_id is required")
    
    try:
        order = db.get(order_id)
    except DatabaseError as e:
        logger.error(f"Failed to fetch order {order_id}: {e}")
        raise OrderNotFoundError(f"Order {order_id} not found") from e
    
    return order
```

## 4. Testes

### Cobertura Mínima
- 80% de line coverage
- 70% de branch coverage
- 100% de cobertura para código crítico (auth, pagamento, etc.)

### Padrão AAA
```python
def test_calculate_total():
    # Arrange
    items = [Item(price=10, qty=2), Item(price=5, qty=1)]
    
    # Act
    total = calculate_total(items)
    
    # Assert
    assert total == 25
```

### Nomenclatura
```
test_<o_que>_<condicao>_<resultado_esperado>
```

## 5. Performance

### Regras
- Evitar N+1 queries (usar eager loading)
- Evitar loops aninhados O(n²) quando possível
- Usar caching para dados frequentemente acessados
- Lazy loading para recursos pesados
- Paginação para listas grandes

### Profiling
- Medir antes de otimizar
- Usar profilers (cProfile, py-spy, etc.)
- Documentar decisões de performance

## 6. Segurança

### Regras
- Nunca commitar secrets
- Validar todos os inputs
- Sanitizar outputs (XSS prevention)
- Usar queries parametrizadas (SQL injection prevention)
- Princípio do menor privilégio
- HTTPS sempre

## 7. Git

### Commits
- Pequenos e descritivos
- Formato: `tipo: descrição` (feat, fix, refactor, test, docs, chore)
- Um commit por mudança lógica
- Nunca commitar código que não compila

### Branches
- `main` — produção
- `develop` — desenvolvimento
- `feature/*` — novas funcionalidades
- `fix/*` — correções de bugs
- `refactor/*` — refatorações

### Pull Requests
- Descrição clara do que mudou
- Link para issue/ticket
- Screenshots para mudanças de UI
- Testes passando
- Review aprovado

## Metadata
- **Categoria**: Desenvolvimento/Qualidade
- **Prioridade**: Crítica
- **Aplicável a**: Qualquer linguagem de programação
- **Versão**: 1.0
- **Criado**: 2026-10-28