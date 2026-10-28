# Instrução: Artefatos Inline e Review Pane

> Define quando usar artefatos inline (na conversa) vs Review pane (arquivo).
> Baseado nas regras globais do OpenCode do dispositivo Cesar.

## Artefatos Inline (skill `inline-artifacts`)

Use **PROATIVAMENTE** (não apenas quando solicitado):

- Quando explicar um conceito, prefira um visual inline (card, diagrama, SVG) em vez de bloco de texto.
- Ao apresentar dados, comparações, fluxos, hierarquias ou status, renderize um artefato inline (card HTML, diagrama Mermaid, SVG) diretamente na mensagem.
- Quando um visual ajudar a compreensão, gere-o inline mesmo sem pedido explícito.
- Mantenha HTML inline autocontido (apenas estilos inline, sem `<script>`).
- Para conteúdo interativo/editável, recorra a `artifact-balloon` (Review pane).

**Não espere o usuário pedir "mostra visualmente" — decida autonomamente quando um visual ajuda.**

## Artefatos em Review Pane (skill `artifact-balloon`)

Use `artifact-balloon` para arquivos grandes, interativos ou editáveis (HTML completo, React/TSX, PDF, imagens binárias).

Não é obrigatório enviar tudo para o Review pane — fluxos simples, cards e diagramas devem ficar inline na conversa.

## Regra de Decisão

| Situação | Onde renderizar |
|---|---|
| Conceito simples, comparação curta, status | Inline (card/SVG/Mermaid) |
| Dashboard interativo, simulador, formulário | Review pane (arquivo HTML) |
| Dados tabulares extensos | Inline (tabela) ou Review pane (se > 20 linhas) |
| Diagrama de fluxo/arquitetura | Inline (Mermaid) |
| Artefato editável pelo usuário | Review pane |

## Anti-Padrões

- ❌ Enviar card simples de 5 linhas para o Review pane
- ❌ Responder com 3 parágrafos de texto quando um diagrama inline resolve
- ❌ Gerar HTML completo com `<script>` inline na conversa (usar Review pane)

## Metadata

- **Tipo**: Instrução
- **Prioridade**: Alta
- **Aplicável a**: Todos os artefatos e respostas visuais
- **Dependências**: artifact-generation, artifact-creator, inline-artifacts, artifact-balloon