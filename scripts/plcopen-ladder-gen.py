#!/usr/bin/env python3
"""
PLCOpen XML Generator for MasterTool IEC XE (Altus Nexto XP325)

Gera um arquivo PLCOpen XML (IEC 61131-10) com programa Ladder que pode ser
importado no MasterTool IEC XE via: Projeto → Importar → PLCopenXML.

Uso:
    python scripts/plcopen-ladder-gen.py --output meu_projeto.xml
    python scripts/plcopen-ladder-gen.py --output meu_projeto.xml --name "MotorSelo"

O arquivo gerado pode ser importado no MasterTool IEC XE:
    1. Abrir o MasterTool IEC XE
    2. Projeto → Importar → PLCopenXML
    3. Selecionar o arquivo .xml gerado
    4. Compilar e baixar para o CLP XP325

Fail-open: nunca quebra a sessão.
"""
import sys
import os
import json
import argparse
from datetime import datetime, timezone

WORKSPACE = os.environ.get("WORKSPACE", os.getcwd())

# --------------------------------------------------------------------------- #
# Template PLCOpen XML para Ladder (IEC 61131-10)
# --------------------------------------------------------------------------- #

PLCOPEN_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://www.plcopen.org/xml/tc6_0201">
  <fileHeader companyName="MECATRON-ZERO" productName="PLCOpen Ladder Generator" productVersion="1.0" creationDateTime="{creation_dt}"/>
  <contentHeader name="{project_name}" modificationDateTime="{creation_dt}">
    <coordinateInfo>
      <fbd>
        <scaling x="1" y="1"/>
      </fbd>
      <ld>
        <scaling x="1" y="1"/>
      </ld>
      <sfc>
        <scaling x="1" y="1"/>
      </sfc>
    </coordinateInfo>
  </contentHeader>
  <types>
    <dataTypes/>
    <pous>
      <pou name="{pou_name}" pouType="program">
        <interface>
          <localVars>
{var_declarations}
          </localVars>
        </interface>
        <body>
          <LD>
{rungs}
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
            <pouInstance name="{pou_name}" typeName="{pou_name}"/>
          </task>
        </resource>
      </configuration>
    </configurations>
  </instances>
  <addData/>
</project>
'''

# --------------------------------------------------------------------------- #
# Definição de variáveis e rungs para o exemplo de selo de motor
# --------------------------------------------------------------------------- #

def generate_motor_seal_ladder():
    """Gera um programa Ladder de selo de motor com partida/parada."""
    vars_decl = '''            <variable name="StartBtn" type="BOOL">
              <documentation>
                <xhtml xmlns="http://www.w3.org/1999/xhtml">Botão de partida (NA)</xhtml>
              </documentation>
            </variable>
            <variable name="StopBtn" type="BOOL">
              <documentation>
                <xhtml xmlns="http://www.w3.org/1999/xhtml">Botão de parada (NF)</xhtml>
              </documentation>
            </variable>
            <variable name="Motor" type="BOOL">
              <documentation>
                <xhtml xmlns="http://www.w3.org/1999/xhtml">Contator do motor</xhtml>
              </documentation>
            </variable>
            <variable name="Overload" type="BOOL">
              <documentation>
                <xhtml xmlns="http://www.w3.org/1999/xhtml">Relé térmico (NF)</xhtml>
              </documentation>
            </variable>
            <variable name="Timer1" type="TON">
              <documentation>
                <xhtml xmlns="http://www.w3.org/1999/xhtml">Temporizador TON 5s</xhtml>
              </documentation>
            </variable>
            <variable name="TimerDone" type="BOOL">
              <documentation>
                <xhtml xmlns="http://www.w3.org/1999/xhtml">Timer concluído</xhtml>
              </documentation>
            </variable>'''

    rungs = '''            <rung>
              <documentation>
                <xhtml xmlns="http://www.w3.org/1999/xhtml">Selo de motor: partida com retenção</xhtml>
              </documentation>
              <leftPowerRail/>
              <contact name="StartBtn" negated="false" edge="none">
                <position x="40" y="20"/>
                <connectionPointIn>
                  <relPosition x="0" y="0"/>
                </connectionPointIn>
                <connectionPointOut>
                  <relPosition x="20" y="0"/>
                </connectionPointOut>
              </contact>
              <contact name="Motor" negated="false" edge="none">
                <position x="80" y="20"/>
                <connectionPointIn>
                  <relPosition x="0" y="0"/>
                </connectionPointIn>
                <connectionPointOut>
                  <relPosition x="20" y="0"/>
                </connectionPointOut>
              </contact>
              <contact name="StopBtn" negated="true" edge="none">
                <position x="120" y="20"/>
                <connectionPointIn>
                  <relPosition x="0" y="0"/>
                </connectionPointIn>
                <connectionPointOut>
                  <relPosition x="20" y="0"/>
                </connectionPointOut>
              </contact>
              <contact name="Overload" negated="true" edge="none">
                <position x="160" y="20"/>
                <connectionPointIn>
                  <relPosition x="0" y="0"/>
                </connectionPointIn>
                <connectionPointOut>
                  <relPosition x="20" y="0"/>
                </connectionPointOut>
              </contact>
              <coil name="Motor" negated="false">
                <position x="220" y="20"/>
                <connectionPointIn>
                  <relPosition x="0" y="0"/>
                </connectionPointIn>
              </coil>
              <rightPowerRail/>
            </rung>
            <rung>
              <documentation>
                <xhtml xmlns="http://www.w3.org/1999/xhtml">Temporizador: após 5s de motor ligado, ativa TimerDone</xhtml>
              </documentation>
              <leftPowerRail/>
              <contact name="Motor" negated="false" edge="none">
                <position x="40" y="20"/>
                <connectionPointIn>
                  <relPosition x="0" y="0"/>
                </connectionPointIn>
                <connectionPointOut>
                  <relPosition x="20" y="0"/>
                </connectionPointOut>
              </contact>
              <block typeName="TON" instanceName="Timer1" executionOrderId="0">
                <position x="80" y="10"/>
                <inputVariables>
                  <variable formalParameter="IN">
                    <connectionPointIn>
                      <relPosition x="0" y="5"/>
                    </connectionPointIn>
                  </variable>
                  <variable formalParameter="PT">
                    <connectionPointIn>
                      <relPosition x="0" y="15"/>
                    </connectionPointIn>
                    <addData>
                      <data name="constantValue" handleUnknown="preserve">
                        <value>T#5s</value>
                      </data>
                    </addData>
                  </variable>
                </inputVariables>
                <outputVariables>
                  <variable formalParameter="Q">
                    <connectionPointOut>
                      <relPosition x="40" y="5"/>
                    </connectionPointOut>
                  </variable>
                  <variable formalParameter="ET">
                    <connectionPointOut>
                      <relPosition x="40" y="15"/>
                    </connectionPointOut>
                  </variable>
                </outputVariables>
              </block>
              <coil name="TimerDone" negated="false">
                <position x="160" y="20"/>
                <connectionPointIn>
                  <relPosition x="0" y="0"/>
                </connectionPointIn>
              </coil>
              <rightPowerRail/>
            </rung>'''

    return vars_decl, rungs


def main():
    parser = argparse.ArgumentParser(description="PLCOpen XML Generator for MasterTool IEC XE")
    parser.add_argument("--output", "-o", default="motor_selo.xml", help="Arquivo de saída .xml")
    parser.add_argument("--name", "-n", default="MotorSelo", help="Nome do projeto/POU")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    vars_decl, rungs = generate_motor_seal_ladder()
    creation_dt = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    xml = PLCOPEN_TEMPLATE.format(
        creation_dt=creation_dt,
        project_name=args.name,
        pou_name=args.name,
        var_declarations=vars_decl,
        rungs=rungs,
    )

    out_path = os.path.join(WORKSPACE, args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)

    result = {
        "output": out_path,
        "project_name": args.name,
        "pou_name": args.name,
        "format": "PLCOpen XML (IEC 61131-10)",
        "compatible_with": "MasterTool IEC XE (Altus Nexto XP325)",
        "import_instructions": [
            "1. Abrir o MasterTool IEC XE",
            "2. Projeto → Importar → PLCopenXML",
            "3. Selecionar o arquivo .xml gerado",
            "4. Compilar (F11) e baixar para o CLP XP325",
        ],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Arquivo PLCOpen XML gerado: {out_path}")
        print(f"Projeto: {args.name}")
        print(f"Formato: PLCOpen XML (IEC 61131-10)")
        print(f"Compatível com: MasterTool IEC XE (Altus Nexto XP325)")
        print()
        print("Instruções de importação:")
        for step in result["import_instructions"]:
            print(f"  {step}")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(0)
