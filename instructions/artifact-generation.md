# Instrução: Geração de Artefatos

> Esta instrução define como e quando gerar artefatos HTML interativos.

## Regra de Geração Espontânea

O agente DEVE gerar um artefato sem ser explicitamente solicitado quando:

1. **O usuário tem dúvida** — um visual explica melhor que texto.
2. **O usuário pede exemplos** — um artefato interativo é mais didático.
3. **Dados precisam de visualização** — métricas, gráficos, comparações.
4. **Simulação é útil** — física, circuitos, processos, sistemas.
5. **O tema é complexo** — diagramas, fluxos, arquiteturas.
6. **O usuário parece engajado** — aprofundar com visual.
7. **Há oportunidade de "mostrar"** — não apenas "dizer".

### Gatilho Interno
> Se você pensou "seria legal mostrar isso visualmente" → gere o artefato.  
> Não espere o usuário pedir "crie um artefato".

## Formato do Artefato

### Estrutura Obrigatória
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Título Descritivo</title>
  <style>/* CSS inline */</style>
</head>
<body>
  <!-- Estrutura semântica -->
  <script>/* JS inline */</script>
</body>
</html>
```

### Requisitos Mínimos
- [ ] Auto-contido (funciona offline)
- [ ] Todos os botões/inputs/links funcionam
- [ ] Pelo menos 1 efeito reativo ao mouse/scroll
- [ ] Pelo menos 1 animação com propósito
- [ ] Paleta diferente do artefato anterior
- [ ] Layout diferente do artefato anterior
- [ ] Título descritivo
- [ ] Responsivo (min 320px)

## Anti-Repetição

### Histórico de Artefatos
Manter mentalmente os últimos 3 artefatos criados:
- Paleta usada
- Layout usado
- Estrutura de abas/seções

### Regra
- Não repetir paleta consecutivamente
- Não repetir layout consecutivamente
- Não repetir estrutura de abas

## Qualidade

### Checklist (executar antes de entregar)
1. Todos os botões têm onclick?
2. Todos os inputs têm output?
3. Todos os links navegam?
4. Canvas renderiza?
5. Modais abrem/fecham?
6. Tratamento de erro existe?
7. Estados vazios tratados?
8. Responsivo?
9. Sem código morto?
10. Paleta diferente do anterior?

### Se falhar em qualquer item → corrigir antes de entregar

## Localização
- Artefatos salvos em: `artefatos/<nome-descritivo>.html`
- Nome: lowercase, hífens, sem espaços
- Exemplo: `artefatos/orbital-gravity-sandbox.html`

## Metadata
- **Tipo**: Instrução
- **Prioridade**: Alta
- **Aplicável a**: Todos os artefatos HTML
- **Dependências**: functional-ui, creative-design, artifact-creator
