---
id: plcopen-ladder-gen
name: plcopen-ladder-gen
description: Gerador de programas Ladder em formato PLCOpen XML (IEC 61131-10) para importação no MasterTool IEC XE (Altus Nexto XP325). Gera arquivos .xml com rungs de ladder, variáveis, temporizadores e contadores. Use quando precisar criar projetos Ladder para CLP XP325, gerar programas IEC 61131-3, ou exportar lógica para MasterTool. Triggers: "plcopen", "ladder", "XP325", "MasterTool", "IEC 61131", "gerar ladder", "programa CLP".
---

# PLCOpen Ladder Generator

Gerador de programas Ladder em formato PLCOpen XML (IEC 61131-10) compatível com
MasterTool IEC XE (Altus Nexto XP325).

## Quando usar

- Criar programas Ladder para CLP XP325 (Nexto Xpress)
- Gerar arquivos PLCOpen XML para importação no MasterTool IEC XE
- Prototipar lógica de controle (selo de motor, temporizadores, contadores)
- Exportar programas IEC 61131-3 em formato padrão

## Comandos (CLI)

```bash
# Gerar programa de selo de motor
python scripts/plcopen-ladder-gen.py --output motor_selo.xml --name "MotorSelo"

# Gerar com nome customizado
python scripts/plcopen-ladder-gen.py -o meu_projeto.xml -n "MinhaLogica"

# Saída em JSON
python scripts/plcopen-ladder-gen.py --json
```

## Instruções de importação no MasterTool IEC XE

1. Abrir o MasterTool IEC XE
2. Projeto → Importar → PLCopenXML
3. Selecionar o arquivo .xml gerado
4. Verificar se as variáveis e rungs foram importados corretamente
5. Compilar (F11) — corrigir erros se houver
6. Baixar para o CLP XP325 (Login)

## Estrutura do PLCOpen XML gerado

```xml
<project>
  <fileHeader .../>
  <contentHeader .../>
  <types>
    <pous>
      <pou name="MotorSelo" pouType="program">
        <interface>
          <localVars>
            <!-- variáveis: StartBtn, StopBtn, Motor, Overload, Timer1, TimerDone -->
          </localVars>
        </interface>
        <body>
          <LD>
            <!-- Rung 1: Selo de motor -->
            <!-- Rung 2: Temporizador TON 5s -->
          </LD>
        </body>
      </pou>
    </pous>
  </types>
  <instances>
    <configurations>
      <configuration name="Config0">
        <resource name="Res0">
          <task name="MainTask" priority="0" interval="T#20ms">
            <pouInstance name="MotorSelo" typeName="MotorSelo"/>
          </task>
        </resource>
      </configuration>
    </configurations>
  </instances>
</project>
```

## Exemplo de Ladder gerado

### Rung 1 — Selo de motor
```
| StartBtn  Motor   StopBtn  Overload | Motor |
+----| |-----+-----| |----+----|/|----+----|/|----( )---+
|           |                   |               |
|           +-------------------+               |
```

### Rung 2 — Temporizador
```
| Motor | [TON Timer1 (PT=5s)] | TimerDone |
+----| |---+---[TON]---+----( )---+
|       |   |         |            |
```

## Variáveis geradas

| Variável | Tipo | Descrição |
|---|---|---|
| StartBtn | BOOL | Botão de partida (NA) |
| StopBtn | BOOL | Botão de parada (NF) |
| Motor | BOOL | Contator do motor |
| Overload | BOOL | Relé térmico (NF) |
| Timer1 | TON | Temporizador TON 5s |
| TimerDone | BOOL | Timer concluído |

## Anti-padrões

- ❌ Não validar o XML antes de importar (use `python -c "import xml.etree.ElementTree; ET.parse('file.xml')"`)
- ❌ Usar nomes de variáveis com espaços ou caracteres especiais (MasterTool pode rejeitar)
- ❌ Esquecer de configurar o CLP (XP325) no MasterTool antes de importar
- ❌ Não compilar (F11) após importação — erros de tipo podem ocorrer
- ❌ Importar sem verificar se a versão do MasterTool suporta PLCOpen XML

## Limitações

- O formato PLCOpen XML é um padrão de troca; a importação pode exigir ajustes no MasterTool
- Variáveis de I/O (entradas/saídas físicas) precisam ser mapeadas manualmente no MasterTool
- Configuração de hardware (XP325) não é incluída no XML — deve ser feita no MasterTool
- O programa gerado é um POU (Program Organization Unit) — precisa ser vinculado a uma task

## Notas

- O gerador pode ser estendido para outros tipos de Ladder (contadores, comparadores, etc.)
- O formato segue o padrão IEC 61131-10 (PLCOpen XML)
- Compatível com qualquer ferramenta que suporte PLCOpen XML (CODESYS, TwinCAT, etc.)
- O arquivo gerado é XML válido e pode ser validado com qualquer parser XML
