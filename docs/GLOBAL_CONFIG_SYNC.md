# Global config sync (OpenCode / Claude skills)

## Onde fica a configuracao global neste dispositivo

- Config OpenCode (global): `C:\Users\<usuario>\.config\opencode`
- Skills instaladas globalmente: `C:\Users\<usuario>\.config\opencode\skills`
- Total de skills agora instaladas: **~1350**
- Hooks / instrucoes / settings: mesmo diretório (`settings.json`, `instructions.md` ou `instructions/*.md`, `hooks/`)
- Backup/download de skills individuais: `C:\Users\<usuario>\Downloads\skills` (estrutura `<autor>/<repo>/<skill>`)

## Repositorio (este projeto)

Diretorio do repo: `C:\Users\drici\Documents\OpenCode`

Pastas uteis:
- `skills/` -> skills locais usadas pelo projeto (OpenCode desktop)
- `hooks/` -> hooks versionados
- `instructions/` -> instrucoes + SUPERPROMPT
- `configs/` -> `skills-index.json` (indice pesquisavel de todas as skills globais)
- `scripts/` -> automacoes/sync
- `docs/` -> documentacao

## Como outro dispositivo deve se configurar

1. Clonar este repositorio:
   `git clone <URL_DO_REPO>`
2. Instalar OpenCode/Claude (mesmas versoes).
3. Copiar ou sincronizar as skills globais:
   - Opcao A (recomendada): `robocopy <repo>\...` nao se aplica porque skills nao estao no repo por tamanho. Use o script abaixo.
   - Opcao B (manual): criar `%USERPROFILE%\.config\opencode` e copiar skills de um backup/export.
4. Executar o script de sincronia do CHARACTER farming? ops.

## Script de sincronia (Windows)

Crie um arquivo `scripts/sync-global-skills.ps1` com:

```powershell
$src = "C:\backups\opencode-global"
$dst = "$env:USERPROFILE\.config\opencode"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
robocopy "$src\skills" "$dst\skills" /E /MT:8 /FFT /R:2 /W:1
Copy-Item "$src\instructions.md" "$dst\" -Force -ErrorAction SilentlyContinue
Copy-Item "$src\settings.json" "$dst\" -Force -ErrorAction SilentlyContinue
```

Para exportar de uma maquina que ja tem tudo (origem), compactar `~/.config/opencode` e mover para `C:\backups\opencode-global` antes.

## Observacoes

- `Downloads\skills` contem copias individuais (nested) e pode ser usado para restaurar uma skill solta.
- O indice `configs/skills-index.json` nao instala skills, serve para descoberta/roteamento proativo.
- Skills com o mesmo `name` entre pacotes sobrescrevem-se parcialmente no carregamento; prefira `npx skills add <repo> -g` para fontes oficiais quando precisar reintegrar.
