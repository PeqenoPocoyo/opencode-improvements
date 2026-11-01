---
name: filesystem
description: Operações de sistema de arquivos local (ler, gravar, listar, buscar, mover, editar e inspecionar arquivos e diretórios) com restrição a diretórios permitidos (allowlist). Inspirada na extensão Filesystem (MCP, Anthropic) — reimplementação própria dos princípios de navegação e manipulação de arquivos.
license: MIT
metadata:
  version: 1.0.0
  author: ReverseLab
  category: system
---

# Filesystem — Operações de sistema de arquivos local

> **Inspiração:** extensão Filesystem (MCP, Anthropic) — permite que um assistente leia e grave arquivos diretamente no sistema de arquivos local.
> **Este arquivo é uma reimplementação própria dos princípios observados**, não uma cópia do código ou da documentação original da Anthropic.

## O que esta skill faz

Expõe um conjunto de ferramentas para interagir com o sistema de arquivos local de forma controlada:

| Ferramenta | Finalidade |
|------------|------------|
| `read_file` | Lê o conteúdo de um arquivo de texto. |
| `read_multiple_files` | Lê vários arquivos em uma única chamada. |
| `list_directory` | Lista as entradas (arquivos e subdiretórios) de um diretório. |
| `directory_tree` | Exibe uma árvore recursiva de diretórios, com profundidade limitada. |
| `search_files` | Busca arquivos por nome ou padrão dentro de um diretório raiz. |
| `get_file_info` | Retorna metadados: tamanho, tipo, última modificação. |
| `write_file` | Cria ou sobrescreve um arquivo com conteúdo fornecido. |
| `edit_file` | Aplica uma edição direcionada (substitui um trecho exato) em um arquivo. |
| `move_file` | Move ou renomeia um arquivo/diretório. |
| `create_directory` | Cria um novo diretório. |

## Modelo de segurança (allowlist)

A skill só opera dentro de **diretórios explicitamente permitidos** (allowlist). Isso evita acesso acidental ou intencional a áreas sensíveis do sistema.

- Caminhos absolutos fora da allowlist são rejeitados.
- Tentativas de traversal de diretório (`..`) são bloqueadas.
- Operações destrutivas (sobrescrita, exclusão, move) exigem confirmação do usuário quando o contexto não torna a intenção óbvia.

## Fluxo de execução recomendado

```
Entrada do usuário → validação de caminho → verificação na allowlist
      ↓
Escolha da ferramenta (read / write / list / search / edit / move / ...)
      ↓
Execução da operação
      ↓
Confirmação do resultado (releitura ou relistagem)
      ↓
Resposta ao usuário com caminhos, tamanhos e avisos
```

### Exemplo de interação

Usuário: "Leia o arquivo `AGENTS.md` e me resuma o que é o ReverseLab."

Assistente:
1. `get_file_info` → confirma que `AGENTS.md` existe e está na allowlist.
2. `read_file` → lê o conteúdo.
3. Resume para o usuário, citando o caminho lido.

Usuário: "Crie um arquivo `notas.md` em `C:/ReverseLab/case-notes/` com o seguinte conteúdo..."

Assistente:
1. `create_directory` (se `case-notes/` não existir).
2. `write_file` → grava o conteúdo.
3. `read_file` → confirma o que foi gravado.
4. Informe o caminho final.

## Diferenças em relação à extensão Filesystem (MCP)

| Aspecto | Extensão Filesystem (MCP) | Esta skill (OpenCode) |
|---------|---------------------------|-----------------------|
| Camada | Protocolo MCP (`@modelcontextprotocol/server-filesystem`) | Skill nativa do OpenCode (SKILL.md) |
| Controle de acesso | Configurado pelo cliente Claude Desktop | Allowlist definida na configuração |
| Escopo | Leitura/gravação geral no FS do usuário | Restrito aos diretórios da allowlist |

## Como usar no OpenCode

1. Copie esta pasta para `~/.config/opencode/skills/filesystem/` ou `.opencode/skills/filesystem/`.
2. Adapte a allowlist com os diretórios que deseja permitir.
3. Ative a skill no cliente OpenCode e peça operações de arquivo em linguagem natural.

## Aviso

Esta skill manipula arquivos no seu computador. Antes de usar, revise o código e entenda o que ele faz. Não conceda acesso a diretórios que contenham credenciais, chaves privadas ou dados sensíveis, a menos que você esteja ciente do risco.

Tools: read_file, write_file, list_directory, search_files, edit_file, move_file, create_directory, get_file_info, directory_tree, read_multiple_files
