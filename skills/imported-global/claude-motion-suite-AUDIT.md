# AUDIT — claude-motion suite (toolkit + skills oficiais Remotion)

Data: 2026-11-02 · Auditor: agente (scanner stdlib + revisão manual) · Veredito: **PASS**

## Fontes auditadas

| Fonte | Ref | Licença | Uso |
|---|---|---|---|
| `github.com/whaleyxbt/claude-motion` | `e627941` (2026-10-09) | MIT | Toolkit de motion design: clone em `C:\Users\drici\Documents\claude-motion` |
| `remotion-dev/remotion` → `packages/skills` (sparse) | `b0279bc` (2026-11-02) | Remotion (skills distribuídas pela Remotion) | Skills oficiais UA, vendored com prefixo `remotion-*` |

## Scanner

- Regras HIGH: `os.system`, `subprocess(shell=True)`, `eval/exec`, `new Function`/`vm.runInContext`, `child_process.exec`, pipe `curl|sh`, `Invoke-Expression`, `rm -rf ~` e decodificação base64→shell.
- Regras MED: exfiltração de env/credenciais, tokens hardcoded (`sk-…`, `ghp_…`, `AKIA…`), escrita fora do cwd, download de executáveis.
- Alvo 1: **59 arquivos de código** · Alvo 2: **122 arquivos**.
- Grep de rede direcionado em todo código executável (`.mjs/.py/.sh/.ps1/.cmd/.cjs/.ts`): **somente 1 URL** (`scripts/sync-readme.ts` da Remotion — constante de doc para sync interno de README; benigna).

## Resultado por severidade

- **HIGH: 0** — nenhum achado em nenhum subprocesso shell, eval, pipe-to-shell ou exfiltração.
- **MED: 11, todos revisados:**
  - `claude-motion/examples/01-effort/README.md` (3×): links relativos `../../media/…` e `../../src/…` — falso positivo do regex de escape de path ( são links markdown).
  - `remotion-docs/SKILL.md`: chave Algolia `x-algolia-api-key=3e42dbd…` — **aceito**: é a search-only key pública do índice de busca de docs da própria Remotion; chaves search-only da Algolia são desenhadas para uso client-side.
  - `remotion-maps/techniques/cesium` (3×): instruções para o usuário obter **sua própria** key de Google Maps/MapTiler via env (`REMOTION_MAPTILER_KEY`, `REMOTION_GOOGLE_MAPS_API_KEY`). Aceito: padrão correto, não há key embutida.
  - Scripts de manutenção da Remotion (`prepare-embedded-skills.ts`, `sync-agent-skills.ts`, ancora em `remotion-maps/static-map`) (4×): caminhos relativos dentro do próprio repo — falso positivo.
- **LOW: ~520, todos sem ação** — URLs de registry no `package-lock.json`, links de docs e exemplos (`https://remotion.media/…` assets de demo), instrução `git clone` no README.

## Decisões de instalação

1. Toolkit completo clonado **fora** do repo de improvements (`C:\Users\drici\Documents\claude-motion`), por ser workspace de renderização (node_modules + outputs não pertencem ao repo).
2. Skills do toolkit (`motion-design`, `review-loop`, `sound-design`, `web-sims`) vendored em `~/.config/opencode/skills/` + espelhadas em `skills/imported-global/`, com nota "rodar dentro do clone" na descrição (o pipeline referencia paths do repo).
3. Colisão detectada: skill `remotion-render` já existe (renderer cloud via inference.sh, bundle belt). Solução: a skill oficial de CLI da Remotion foi vendored como **`remotion-render-cli`** (folder + frontmatter `name:` renomeados). Ambas coexistem.
4. `npm install` rodou APÓS auditar fontes e `package.json` (versões pinadas exatas; sem postinstall próprio do repo toolkit).

## Notas de licença / contexto

- Repo claude-motion: MIT. Remotion (engine): grátis para indivíduos e equipes pequenas; empresas acima do threshold precisam de licença paga.
- Pipeline 100% local e determinístico (sem créditos/API de geração): Remotion (React→MP4) e web sims (HTML+three.js → Chromium headless frame a frame → ffmpeg 60fps).
- Riscos funcionais herdados: primeiro render pode baixar Google Chrome Headless Shell (~100 MB) se não houver Chromium de sistema; `npm run sfx` chama `python3` (Windows: usar `python`).
