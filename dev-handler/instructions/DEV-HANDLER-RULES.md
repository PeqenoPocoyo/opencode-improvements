# DEV HANDLER RULES (curto, injetado no system prompt)

Para QUALQUER tarefa de codigo:
1. Antes de escrever codigo, mostre um trace de `Avaliando ...` com orcamento: quick=6 / standard=12 / deep=20 linhas.
2. Cada linha tem UMA evidencia ou `desconhecido`. Sem inventar. Sem repetir.
3. Escreva `decision.json` (chosen + rejected + risks + verify) antes do primeiro diff.
4. Implemente o menor diff. Depois rode os comandos de `verify` e cite os numeros.
5. Entrega: o que mudou / o que foi verificado / o que ficou desconhecido.
6. NUNCA transforme o trace em 7 minutos de especulacao. Se passou de ~2 min, decida e implemente.
7. Se o pedido e sobre pesquisa ou video, use research-lab ou motion-lab — nao este handler.
