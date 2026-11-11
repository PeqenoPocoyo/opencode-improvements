# Research Lab — pesquisa profunda na internet com orçamento e guardas

Pacote para **deep research**: busca na web, coleta de contexto, redes generativas de
questionamento (question-graph), raciocínio encadeado verificável (reasoning-chain),
triangulação de fontes e relatórios com citação — com **orçamento por nível de detalhamento**
(quick / standard / deep / exhaustive) que pode consumir MUITO contexto quando o pedido exige.

## Estrutura

```
research-lab/
├── README.md                  # este arquivo
├── skills/                    # 10 skills (cada uma com SKILL.md)
│   ├── research-director/     # entry point — orquestra o pipeline
│   ├── depth-router/          # nível + orçamento (budget.json)
│   ├── question-graph/        # rede generativa de questionamento
│   ├── source-hunter/         # busca + triangulação (sources.json)
│   ├── context-weaver/        # knowledge-map.md (estado vivo)
│   ├── reasoning-chain/       # cadeias verificáveis (CoVe)
│   ├── claim-verifier/        # gate de claims (tabela)
│   ├── synthesis-writer/      # relatório com citações
│   ├── budget-guard/          # contadores + regras de corte
│   └── self-critique/         # adversarial 5 perguntas + score
├── hooks/                     # 4 guardas fail-open (Python stdlib)
├── instructions/              # RESEARCH-LAB-RULES.md + depth-levels.md
└── LEIA-ME.pt-BR.md           # versão curta em português
```

## Uso

Diga no chat: "deep research sobre X" (ou "pesquise a fundo", "dossiê de X", "go").
O pipeline roda e entrega `research-report.md` + fontes + gaps.

## Instalação (OpenCode global)

Skills → `~/.config/opencode/skills/` (copiar as 10 pastas).
Hooks → registrar em `~/.config/opencode/hook/hooks.yaml` (padrão yaml-hooks,
scripts copiados para `hook/scripts/researchlab-*`).

Licença: uso pessoal. Todos os hooks são fail-open e stdlib-only.
