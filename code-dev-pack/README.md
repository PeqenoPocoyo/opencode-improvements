# Code Development Pack — Pacote de Recursos Integrado

> Pacote de recursos para desenvolvimento de código com suporte a autoteste e auto-melhoria.
> Integrado ao repositório opencode-improvements.

## Estrutura

```
code-dev-pack/
├── skills/                    # Skills de desenvolvimento de código
│   ├── code-tdd/              # Test-Driven Development
│   ├── code-review/           # Code Review automático
│   ├── code-refactor/         # Refactoring assistido
│   ├── code-debug/            # Debugging sistemático
│   └── code-test-gen/         # Geração de testes
├── hooks/                     # Hooks de autoteste
│   ├── pre-write-quality.py   # Valida código antes de escrever
│   ├── post-write-test.py     # Roda testes após mudança
│   ├── session-start-check.py # Verifica estado do projeto
│   └── session-end-report.py  # Gera relatório de testes
├── instructions/              # Instruções de qualidade
│   ├── code-quality.md        # Padrões de qualidade de código
│   ├── testing-standards.md   # Padrões de teste
│   └── review-standards.md    # Padrões de review
├── scripts/                   # Scripts de autoteste
│   ├── autotest.py            # Runner de autoteste
│   ├── coverage-check.py      # Verificador de cobertura
│   └── quality-report.py      # Relatório de qualidade
├── configs/                   # Configurações
│   ├── test-config.json       # Config de teste
│   └── quality-config.json    # Config de qualidade
├── docs/                      # Documentação
│   ├── code-dev-guide.md      # Guia de desenvolvimento
│   └── auto-improve.md        # Protocolo de auto-melhoria
└── validation.json            # Rastreamento de validação
```

## Princípio Central

**Código deve ser testável, testado e melhorado continuamente.**

Cada recurso (skill, hook, instrução, script) deve:
1. Ser **autotestável** — ter testes que validam seu funcionamento
2. Ser **auto-melhorável** — melhorar com base em feedback real
3. Ser **integrado** — funcionar em conjunto com outros recursos
4. Ser **multi-device** — sincronizar entre dispositivos via git

## Ciclo de Auto-Melhoria

```
Feedback → Análise → Implementação → Teste → Validação → Commit → Push → Sync
```

### 1. Feedback
Usuário ou dispositivo identifica gap, bug ou oportunidade de melhoria.

### 2. Análise
Agente analisa o feedback e classifica:
- P0: Bug crítico ou segurança
- P1: Funcionalidade faltante importante
- P2: Melhoria de qualidade
- P3: Nice-to-have

### 3. Implementação
Agente implementa a melhoria no recurso correspondente.

### 4. Teste (Autoteste)
Script de autoteste valida se a melhoria funciona:
```bash
python scripts/autotest.py --resource <path> --scenario <test>
```

### 5. Validação
Se teste PASS → marcar como validado
Se teste FAIL → reverter, analisar, tentar abordagem diferente

### 6. Commit e Push
Commit com mensagem descritiva, push para staging/main

### 7. Sync
Outros dispositivos recebem via auto-sync

## Validação Progressiva

```
raw → marked → validated → proactive
```

- `raw → marked`: Agente revisa e aprova (commit em staging)
- `marked → validated`: 3+ usos sem feedback negativo
- `validated → proactive`: 7+ usos sem feedback negativo
- 2+ feedbacks negativos → reverter para raw

## Autoteste

Cada recurso deve ter um cenário de teste independente:

### Teste de Reinterpretação
```
DADO um recurso melhorado
QUANDO executado em contexto independente
ENTÃO o comportamento esperado deve ocorrer
SE não ocorrer → FAIL (reverter)
```

### Exemplo de autoteste
```python
# scripts/autotest.py
def test_skill(skill_path, scenario):
    """Testa se a skill funciona conforme o cenário."""
    # 1. Carregar a skill
    # 2. Executar o cenário
    # 3. Verificar o resultado
    # 4. Retornar PASS/FAIL
```

## Multi-Device

### Fluxo de contribuição
```
Device A → melhora → commit staging → push
Device B → sync → recebe → usa → feedback
Device C → sync → recebe → usa → feedback
→ 3+ usos sem feedback negativo → promove para main
```

### Auto-sync
- Windows: Task Scheduler a cada hora
- Mac/Linux: Cron a cada hora
- Manual: "sync opencode" ou scripts/sync.ps1

## Regras

- Nunca commitar segredos
- Preferir commits pequenos e descritivos
- Sempre reportar o que foi sincronizado
- Validação é progressiva
- Feedback negativo reverte
- Se algo falhar, explicar e sugerir solução
- **Não reusar padrões anteriores** — cada recurso deve ter identidade própria
- **Não ter pressa** — melhorar incrementalmente, testar cada mudança

## Metadata
- **Versão**: 1.0
- **Criado**: 2026-10-28
- **Objetivo**: Aprimoramento contínuo de desenvolvimento de código
- **Dispositivos**: 3 (multi-device sync)