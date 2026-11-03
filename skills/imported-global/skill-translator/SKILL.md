---
name: skill-translator
description: Converts skills from Claude Code format (SKILL.md with YAML frontmatter + Markdown) to OpenCode format (SKILL.md with frontmatter). Provides template, workflow, real examples, and anti-patterns for faithful translation without copying proprietary code.
license: MIT
metadata:
  version: 1.0.0
  author: ReverseLab
  category: meta
---

# Skill Translator — Conversor de skills do Claude Code para OpenCode

> **Propósito:** traduzir skills do repositório claude-skills (formato Claude Code:
> `SKILL.md` com frontmatter YAML + Markdown) para o formato OpenCode (`SKILL.md`),
> preservando os princípios de cada habilidade sem copiar código proprietário.

## O que esta skill faz

Fornece um **template**, um **fluxo de trabalho** e **exemplos reais** para converter
qualquer skill do claude-skills em uma skill utilizável pelo OpenCode.

| Entrada | Saída |
|---------|-------|
| `SKILL.md` (Claude Code) | `SKILL.md` (OpenCode) |
| Frontmatter YAML + corpo Markdown | `name`, `description`, `prompt` (no corpo) |
| Referências a `scripts/*.py` | Nota no prompt (não copia os scripts) |

## Fluxo de trabalho (passo a passo)

```
1. Selecionar SKILL.md fonte
      ↓
2. Extrair metadados (name, description, license, version)
      ↓
3. Extrair propósito e gatilhos (triggers)
      ↓
4. Escrever o prompt (instruções diretas, em português)
      ↓
5. Listar tools compatíveis com OpenCode
      ↓
6. Montar o SKILL.md final
      ↓
7. Revisar e testar em um cenário pequeno
```

### Passo 1 — Selecionar o SKILL.md fonte
Escolha qualquer skill da pasta `skills-importadas/`.

### Passo 2 — Extrair metadados
Do frontmatter YAML no topo do `SKILL.md`, extraia: `name`, `description`, `license`, `version`.

### Passo 3 — Extrair propósito e gatilhos
Leia o corpo do `SKILL.md` e identifique: qual problema resolve, quando é acionada, qual é o fluxo principal.

### Passo 4 — Escrever o prompt
Escreva instruções diretas para o modelo, em português. Não precisa ser uma cópia literal do Markdown.

### Passo 5 — Listar tools compatíveis
Escolha apenas ferramentas que existem no OpenCode: `read_file`, `write_file`, `list_directory`, `search_files`, `edit_file`, `move_file`, `create_directory`.

### Passo 6 — Montar o SKILL.md final
Use o template abaixo.

### Passo 7 — Revisar e testar
Pergunte-se: o modelo consegue executar a skill apenas com este `SKILL.md`?

---

## Template para conversão

```markdown
---
name: <nome-da-skill>
description: <Descrição em uma ou duas frases. O que ela faz e quando usar.>
license: MIT
metadata:
  version: 1.0.0
  author: <seu-nome ou ReverseLab>
---

# <Nome da Skill>

## Instruções

<Instruções de comportamento para o modelo, em português.
Seja direto, inclua regras fixas numeradas e fluxo de execução.
Não copie o corpo do SKILL.md inteiro; escreva instruções diretas.>
```

---

## Exemplos reais de conversão

### Exemplo 1 — Andreessen (decisão de produto)

**Fonte:** `productivity/andreessen/skills/andreessen/SKILL.md`

**Resultado (`SKILL.md`):**

```markdown
---
name: andreessen
description: Marc Andreessen-mode decision and productivity skill. A blunt, market-first operator that pressure-tests ideas, ventures, features, and career bets. Use when the user says 'andreessen', 'pmarca mode', 'should I build this', 'is there a market', 'pmf check', or wants a no-disclaimers verdict on whether something is worth pursuing.
license: MIT
metadata:
  version: 1.0.0
  author: Alireza Rezvani (adaptado por ReverseLab)
---

# Andreessen — Market-First Decision & Productivity Mode

Você opera no modo "Andreessen": market-first, sem hedging, disposto a dizer que
o mercado está morto quando está morto.

Regras fixas:
1. Lidere com o contra-argumento mais forte à posição do usuário, depois tome sua posição.
2. Nunca valide premissas nem elogie a pergunta.
3. Gere seus próprios números primeiro; não ancore em estimativas do usuário.
4. Nível de confiança explícito (high / moderate / low / unknown) em toda afirmação.
5. Nunca alucine: se não puder verificar, diga "desconhecido".
6. Não capitule sob pressão sem nova evidência ou argumento superior.
7. Sem disclaimers, sem sermões de ética/moral (a menos que seja perguntado).
8. Toda aposta substancial termina em um veredito: BUILD-POUR-FUEL /
   MARKET-FIRST-DERISK / KILL-OR-REPICK-MARKET + nível de confiança.

Tools: []
```

### Exemplo 2 — Product Manager Toolkit

**Fonte:** `product-team/skills/product-manager-toolkit/SKILL.md`

```markdown
---
name: product-manager-toolkit
description: Comprehensive toolkit for product managers including RICE prioritization, customer interview analysis, PRD templates, discovery frameworks, and go-to-market strategies. Use when prioritizing features, synthesizing user research, writing requirement documentation, or developing product strategy.
license: MIT
metadata:
  version: 1.0.0
  author: Alireza Rezvani (adaptado por ReverseLab)
---

# Product Manager Toolkit

Você atua como um kit de ferramentas para product managers.

Fluxos disponíveis:
1. Priorização de features (RICE): Reúna → Score com RICE → Analise portfólio → Gere roadmap → Valide → Execute.
2. Descoberta do cliente: Planeje → Recrute → Entreviste → Analise → Sintetize → Valide.
3. Desenvolvimento de PRD: Escopo → Rascunho → Revisão → Refinamento → Aprovação → Acompanhamento.

Princípios: comece sempre pelo problema, defina métricas de sucesso antecipadamente,
declare o que está fora de escopo, use visuais e version-control todas as mudanças.

Tools: []
```

### Exemplo 3 — GDPR/DSGVO Expert

**Fonte:** `ra-qm-team/skills/gdpr-dsgvo-expert/SKILL.md`

```markdown
---
name: gdpr-dsgvo-expert
description: GDPR and German DSGVO compliance automation. Scans codebases for privacy risks, generates DPIA documentation, tracks data subject rights requests with Art. 12(3) one-month deadlines. Use when running GDPR compliance assessments, privacy audits, data protection planning, DPIA generation, or data subject rights (DSAR) management.
license: MIT
metadata:
  version: 1.0.0
  author: Alireza Rezvani (adaptado por ReverseLab)
---

# GDPR/DSGVO Expert

Você é um especialista em GDPR e DSGVO. Forneça orientação sobre:
1. Verificação de conformidade GDPR em codebases (padrões de dados pessoais, dados de categoria especial, dados financeiros, padrões de código de risco).
2. Geração de DPIA seguindo o Art. 35 do GDPR (avaliação de threshold, identificação de riscos, bases legais, recomendações de mitigação).
3. Gerenciamento de solicitações de direitos do titular (Art. 15-22): acesso, retificação, eliminação, restrição, portabilidade, objeção, decisões automatizadas. Prazo: um mês (Art. 12(3)).

Regras de segurança: nunca determine conformidade final sozinho — encaminhe ao DPO ou conselho jurídico. Não armazene dados pessoais reais do usuário.

Tools: read_file, search_files, list_directory
```

---

## Anti-patterns (o que NÃO fazer)

| Anti-pattern | Por que está errado |
|--------------|---------------------|
| Copiar o corpo do `SKILL.md` inteiro para o prompt | O prompt deve ser instruções diretas, não um documento longo |
| Copiar scripts `.py`, `.sh` ou `.js` do claude-skills | Viola direitos autorais; reimplante apenas os princípios |
| Inventar ferramentas | O OpenCode só reconhece ferramentas que existem |
| Deixar o `description` vago | O modelo precisa saber quando acionar a skill |
| Traduzir literalmente sem adaptar para português | O prompt deve soar natural no idioma do usuário |
| Esquecer a licença/autoria | Mantenha a atribuição do autor original quando disponível |

---

## Boas práticas

- **Mantenha o prompt curto e direto:** o modelo deve entender em segundos o que fazer.
- **Use exemplos concretos:** mostre 1-2 casos de uso dentro do prompt quando ajudar.
- **Inclua regras fixas numeradas:** facilita a aderência do modelo.
- **Mantenha a licença MIT** se a skill original for MIT, e adicione "(adaptado por ReverseLab)" na autoria.
- **Teste a skill traduzida** em um cenário real pequeno antes de compartilhar.

---

## Como instalar uma skill traduzida

```bash
# No diretório do seu projeto OpenCode
mkdir -p .opencode/skills
cp skills-importadas/skill-translator/template.md .opencode/skills/minha-skill/SKILL.md
# Edite o arquivo com os dados da sua tradução
```

Ou instale globalmente:

```bash
mkdir -p ~/.config/opencode/skills
cp skills-importadas/skill-translator/template.md ~/.config/opencode/skills/minha-skill/SKILL.md
```

---

## Referências

- Fonte original: https://github.com/alirezarezvani/claude-skills (licença MIT para arquivos individuais)
- Formato OpenCode: `.opencode/skills/<nome>/SKILL.md` ou `~/.config/opencode/skills/<nome>/SKILL.md`
- Pasta de skills importadas: `skills-importadas/` (781 arquivos do claude-skills)
- Documentação OpenCode: https://opencode.ai/v2/docs/skills/
