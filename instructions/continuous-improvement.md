# Continuous Improvement — Instrução de Melhoria Contínua

## Princípio Central
**O modelo se auto-alimenta com melhorias durante a conversa, ao vivo.** Não é melhoria em lote — é pesquisa em si mesmo + contexto, sob condição de melhoria contínua e reconsiderações contínuas.

## Trigger: qualquer discrepância
O hook `self-research.py` dispara quando o modelo **percebe ou minimamente suspeita** que precisa melhorar — seja por sinal mensurável (erro, falha) ou imensurável (incerteza, "acho que", "não é ideal").

## Ciclo de Auto-Melhoria ao Vivo

```
Conversa em andamento
    ↓
[SINAL DE DISCREPÂNCIA]  ← pode ocorrer a QUALQUER momento
    ↓
[TAREFA CRIADA]          ← registrada em self-research-tasks.json
    ↓
[PESQUISA DE COBERTURA]  ← skill? hook? instrucao?
    ↓
    ├─ COBERTO → aplicar recurso existente
    └─ NÃO COBERTO → desenvolver melhoria
                        ↓
                   [MENTALIZAR TESTE]
                        ↓
                   [EXECUTAR TESTE]
                        ↓
                   ├─ PASS → promover validated → commit → push
                   └─ FAIL → reconsiderar → reaprimorar → re-testar
```

## Pesquisa de Cobertura (deep research em si mesmo)

Ao detectar discrepância, pesquisar OBRIGATORIAMENTE:

1. **Skills**: `configs/skills-index.json` e `~/.config/opencode/skills/`
2. **Hooks**: `hooks/` e `hooks/reasoning/`
3. **Instruções**: `instructions/`
4. **Configs**: `configs/`
5. **Pacotes**: `code-dev-pack/`

Se nenhum cobrir → desenvolver novo recurso.

## Desenvolvimento de Novos Hooks (ao vivo)

Quando desenvolver novo hook durante a conversa:

1. Criar em `hooks/reasoning/` (ou diretório apropriado)
2. **Fail-open**: nunca quebrar a sessão por erro interno
3. Sem matchers restritivos (todo contexto é considerado)
4. Mentalizar teste: "este hook melhora X capacidade como?"
5. Executar autoteste
6. Atualizar `validation.json`
7. Commit + push

## Regeneratividade

Melhorias não são apenas correções — são **criação de novas capacidades**:
- Combinar hooks existentes de formas novas
- Antecipar necessidades futuras do fluxo de conversa
- Automatizar padrões de raciocínio recorrentes

## Treinamento por iteração
- Quanto mais o pacote é usado, mais discrepancies são detectadas.
- Mais discrepancies → mais tarefas → mais melhorias.
- O pacote cresce organicamente com o uso.

## Metadata
- **Tipo**: Instrução
- **Prioridade**: Crítica
- **Aplicável a**: Todos os modelos
- **Versão**: 1.0
- **Criado**: 2026-10-30