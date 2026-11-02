# Audit de segurança — suíte Higgsfield (9 skills oficiais)

- **Fonte**: github.com/higgsfield-ai/skills @ main (oficial, **MIT license**)
- **Data**: 2026-11-02 | **Scanner**: skill-security-auditor (estático)
- **Complemento instalado**: MCP remoto oficial `https://mcp.higgsfield.ai/mcp` (OAuth, 185 tools catalogadas) + CLI `@higgsfield/cli@1.2.2` via npm pinned (pós-install bloqueado pela política npm — funcionalidade verificada: `--version` OK, `auth login` OK)

## Verdict do scanner

| Skill | Verdict | CRITICAL | HIGH |
|---|---|---|---|
| generate | PASS | 0 | 0 |
| marketplace-cards | PASS | 0 | 0 |
| product-photoshoot | PASS | 0 | 0 |
| soul-id | PASS | 0 | 0 |
| video-explainer | PASS | 0 | 0 |
| websites | PASS | 0 | 0 |
| youtube-thumbnail | PASS | 0 | 0 |
| brandkit | WARN | 0 | 3 |
| faceless-video | WARN | 0 | 6 |

## Revisão manual dos 9 HIGH — todos falsos positivos

| Achado | Conclusão |
|---|---|
| `brandkit/scripts/brandkit.py:66-68` FS-ABUSE ×3 | Lookup de CA-bundles padrão do OS (`/etc/ssl/…`, `ca-certificates.crt`, `ca-bundle.crt`) apenas `.is_file()`. TLS correto, sem desativação de verificação |
| `faceless-video/scripts/assemble_blocks.sh:187` + `assemble_slides.sh:132` CODE-EXEC | `python3 -c` inline serializando JSON de variáveis próprias via `argv` (sem interpolação de input externo no código). Mesmo padrão de estilo já aceito no audit da skill `reel` |
| `faceless-video/scripts/audio_to_captions.py:392,396,418` FS-ABUSE ×3 | `shutil.rmtree` sobre dirs temporários que o próprio script criou (`mktemp -d` / `shutil.rmtree(source.parent)` no `finally`). Limpeza de temp próprio |
| `faceless-video/scripts/burn_captions.sh:58` CODE-EXEC | `python3 -c` p/ uppercase de arquivo SRT próprio da skill. Inocente |

## Notas aceitas (documentadas)

1. **[BOOTSTRAP]** 7 SKILL.md referenciam `curl -fsSL …higgsfield-ai/cli/main/install.sh | sh` como bootstrap do CLI. Mitigado: CLI já instalado via `npm install -g @higgsfield/cli@1.2.2` (pinned, sem versão mutável) — o bootstrap não deve disparar com CLI presente. Superfície só ativa se o CLI for desinstalado e o procedimento da skill seguir literalmente.
2. **[DOWNLOAD]** `higgsfield-websites/references/game-3d-animation.md:70` menciona baixar tarball do `download.blender.org` do zero, sem checksum. Documento de referência on-demand (não executa por conta própria). Vamos revisar manualmente caso a skill de sites/games seja usada com essa referência.

## Não encontrados (scanner clean)

- Exfiltração de rede — nenhum achado além dos acima
- Acesso a credenciais (~/.ssh, ~/.aws, env scraping) — nenhum achado
- Prompt injection em SKILL.md — nenhum achado (SKILL.md contêm instruções pró-usuário: pedir confirmação até antes de ações caras/destrutivas)
- Ofuscação (base64/hex/chr chains) — nenhum achado

## Proveniência

Vendored as-is do repo oficial MIT. Para atualizar: baixar nova main zip + re-auditar (a versão atual tem 9 skills; o wrapper não-oficial jurislm/higgsfield-plugin documentava 7 — as novas são `brandkit`, `faceless-video`, `youtube-thumbnail`).
