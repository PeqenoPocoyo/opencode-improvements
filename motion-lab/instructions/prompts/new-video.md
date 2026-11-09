# Prompt: novo vídeo (cole e preencha os [colchetes])

Siga `$MOTION_LAB_HOME/instructions/MOTION-LAB-RULES.md`. Tarefa: criar um vídeo [TEMA / PRODUTO / MENSAGEM] para [PLATAFORMA], [LARGURA×ALTURA], [DURAÇÃO] s.

Passos obrigatórios, nesta ordem, mostrando o resultado de cada um em 1–3 linhas:
1. Ideia em UMA frase + público + objetivo.
2. Gere 3 DNAs divergentes (`dna_generate.py --candidates 3`). Descreva cada um em 1 linha (paleta, tipografia, personalidade de movimento, textura, sound palette) e escolha um, explicando por quê. Ele NÃO pode se parecer com os vídeos anteriores do ledger.
3. Beat sheet: cenas com durações DIFERENTES, gancho no 1º segundo, payoff com hold ≥ 1 s.
4. Monte o projeto com `setup.sh`, construa cena por cena (≤ 250 linhas por arquivo), rodando `lint_scene.py` a cada etapa.
5. Renderize 6 stills, LEIA o PNG e liste 2 problemas; corrija.
6. Som: `Lab.ev` em todo hit/transição → `sync_cues.py` com a palette do DNA.
7. Draft mp4 → `qa_video.py`, `contact_sheet.py` (leia), `frame_diff.py`, `fingerprint.py`. Nota pelo rubric; no máx. 3 passes.
8. Entrega no formato final (arquivo, o que é, look, checks, problemas conhecidos, 5 timestamps de som para eu ouvir).
