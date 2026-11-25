# /dev — Dev Handler (deliberacao antes do codigo)

Uso: /dev [quick|standard|deep] <pedido>

1. Trace `Avaliando ...` (quick=6 / standard=12 / deep=20 linhas; uma evidencia por linha).
2. Escreva `decision.json`: chosen, rejected[], risks[], verify[].
3. Implemente o menor diff possivel.
4. Rode os comandos de `verify` e cite os numeros (testes, lint, build).
5. Entrega: o que mudou / o que foi verificado / o que ficou desconhecido.

Regra anti-7-minutos: se o trace passou de ~2 min, DECIDA e implemente. Nunca troque codigo por especulacao.
