#!/usr/bin/env python3
"""
CLP Multi-Platform Ladder/ST/FBD Generator — IEC 61131-3

Gera programas para múltiplas plataformas de CLP:
  - PLCOpen XML (IEC 61131-10) → MasterTool, CODESYS, TwinCAT, Beckhoff
  - L5K (Rockwell/Allen-Bradley) → Studio 5000, RSLogix 5000
  - SCL (Siemens) → TIA Portal, Step 7
  - ST (Structured Text genérico) → qualquer IEC 61131-3
  - FBD (Functional Block Diagram) → CODESYS, TwinCAT

Exemplos incluídos:
  - motor_seal: selo de motor com partida/parada
  - star_delta: partida estrela-triângulo
  - level_control: controle de nível com histerese
  - sequencer: sequenciador de 4 passos
  - pid_temp: controle PID de temperatura
  - conveyor: esteira com sensores e atuadores

Uso:
    python scripts/clp-multi-gen.py --format plcopen --example motor_seal --output out.xml
    python scripts/clp-multi-gen.py --format l5k --example star_delta --output out.L5K
    python scripts/clp-multi-gen.py --format scl --example pid_temp --output out.scl
    python scripts/clp-multi-gen.py --format st --example all --output out.st
    python scripts/clp-multi-gen.py --list  # lista exemplos e formatos

Fail-open: nunca quebra a sessão.
"""
import sys
import os
import json
import argparse
from datetime import datetime, timezone

WORKSPACE = os.environ.get("WORKSPACE", os.getcwd())


# =========================================================================== #
# MODELOS DE PROGRAMA (dados puros, independentes de formato)
# =========================================================================== #

EXAMPLES = {}

EXAMPLES["motor_seal"] = {
    "name": "MotorSelo",
    "description": "Selo de motor com partida/parada e temporizador de desligamento",
    "vars": [
        ("StartBtn", "BOOL", "Botao de partida (NA)"),
        ("StopBtn", "BOOL", "Botao de parada (NF)"),
        ("Motor", "BOOL", "Contator do motor"),
        ("Overload", "BOOL", "Rele termico (NF)"),
        ("Timer1", "TON", "Temporizador TON 5s"),
        ("TimerDone", "BOOL", "Timer concluido"),
    ],
    "rungs": [
        {
            "comment": "Selo de motor: partida com retencao",
            "contacts": [
                ("StartBtn", False), ("Motor", False), ("StopBtn", True), ("Overload", True),
            ],
            "coil": ("Motor", False),
        },
        {
            "comment": "Temporizador: apos 5s de motor ligado, ativa TimerDone",
            "contacts": [("Motor", False)],
            "timer": ("Timer1", "Motor", "T#5s"),
            "coil": ("TimerDone", False),
        },
    ],
}

EXAMPLES["star_delta"] = {
    "name": "PartidaEstrelaTriangulo",
    "description": "Partida estrela-triangulo com temporizacao e intertravamento",
    "vars": [
        ("StartBtn", "BOOL", "Botao de partida"),
        ("StopBtn", "BOOL", "Botao de parada (NF)"),
        ("K1_Estrela", "BOOL", "Contator estrela"),
        ("K2_Triangulo", "BOOL", "Contator triangulo"),
        ("K3_Linha", "BOOL", "Contator linha"),
        ("TimerTransicao", "TON", "Temporizador de transicao 3s"),
        ("MotorLigado", "BOOL", "Motor em funcionamento"),
    ],
    "rungs": [
        {
            "comment": "Partida: aciona estrela + linha",
            "contacts": [("StartBtn", False), ("StopBtn", True), ("K2_Triangulo", True)],
            "coils": [("K1_Estrela", False), ("K3_Linha", False)],
        },
        {
            "comment": "Temporizador de transicao estrela -> triangulo",
            "contacts": [("K1_Estrela", False)],
            "timer": ("TimerTransicao", "K1_Estrela", "T#3s"),
        },
        {
            "comment": "Transicao: desliga estrela, liga triangulo",
            "contacts": [("TimerTransicao.Q", False), ("K1_Estrela", False)],
            "coils": [("K1_Estrela", True), ("K2_Triangulo", False)],
        },
        {
            "comment": "Motor ligado: selo de funcionamento",
            "contacts": [("K2_Triangulo", False), ("StopBtn", True)],
            "coil": ("MotorLigado", False),
        },
    ],
}

EXAMPLES["level_control"] = {
    "name": "ControleNivel",
    "description": "Controle de nivel de tanque com histerese (liga/desliga bomba)",
    "vars": [
        ("NivelAlto", "BOOL", "Sensor de nivel alto"),
        ("NivelBaixo", "BOOL", "Sensor de nivel baixo"),
        ("Bomba", "BOOL", "Bomba de enchimento"),
        ("AlarmeNivelAlto", "BOOL", "Alarme de nivel alto"),
        ("TimerAlarme", "TON", "Temporizador de alarme 10s"),
    ],
    "rungs": [
        {
            "comment": "Liga bomba quando nivel baixo (histerese)",
            "contacts": [("NivelBaixo", False), ("NivelAlto", True)],
            "coil": ("Bomba", False),
        },
        {
            "comment": "Selo de bomba: mantem ligada ate nivel alto",
            "contacts": [("Bomba", False), ("NivelAlto", True)],
            "coil": ("Bomba", False),
        },
        {
            "comment": "Alarme: nivel alto por mais de 10s",
            "contacts": [("NivelAlto", False)],
            "timer": ("TimerAlarme", "NivelAlto", "T#10s"),
        },
        {
            "comment": "Ativa alarme se timer concluido",
            "contacts": [("TimerAlarme.Q", False)],
            "coil": ("AlarmeNivelAlto", False),
        },
    ],
}

EXAMPLES["sequencer"] = {
    "name": "Sequenciador",
    "description": "Sequenciador de 4 passos com temporizacao",
    "vars": [
        ("Start", "BOOL", "Botao de inicio"),
        ("Reset", "BOOL", "Botao de reset"),
        ("Step1", "BOOL", "Passo 1 ativo"),
        ("Step2", "BOOL", "Passo 2 ativo"),
        ("Step3", "BOOL", "Passo 3 ativo"),
        ("Step4", "BOOL", "Passo 4 ativo"),
        ("TimerStep", "TON", "Temporizador de passo 2s"),
        ("Done", "BOOL", "Sequencia concluida"),
    ],
    "rungs": [
        {
            "comment": "Passo 1: inicia ao pressionar Start",
            "contacts": [("Start", False), ("Step1", True), ("Step2", True), ("Step3", True), ("Step4", True)],
            "coil": ("Step1", False),
        },
        {
            "comment": "Timer do passo 1",
            "contacts": [("Step1", False)],
            "timer": ("TimerStep", "Step1", "T#2s"),
        },
        {
            "comment": "Transicao passo 1 -> 2",
            "contacts": [("TimerStep.Q", False), ("Step1", False)],
            "coils": [("Step1", True), ("Step2", False)],
        },
        {
            "comment": "Timer do passo 2",
            "contacts": [("Step2", False)],
            "timer": ("TimerStep", "Step2", "T#2s"),
        },
        {
            "comment": "Transicao passo 2 -> 3",
            "contacts": [("TimerStep.Q", False), ("Step2", False)],
            "coils": [("Step2", True), ("Step3", False)],
        },
        {
            "comment": "Transicao passo 3 -> 4",
            "contacts": [("TimerStep.Q", False), ("Step3", False)],
            "coils": [("Step3", True), ("Step4", False)],
        },
        {
            "comment": "Sequencia concluida",
            "contacts": [("Step4", False), ("TimerStep.Q", False)],
            "coil": ("Done", False),
        },
        {
            "comment": "Reset: desliga tudo",
            "contacts": [("Reset", False)],
            "coils": [("Step1", True), ("Step2", True), ("Step3", True), ("Step4", True), ("Done", True)],
        },
    ],
}

EXAMPLES["pid_temp"] = {
    "name": "ControlePIDTemp",
    "description": "Controle PID de temperatura com setpoint e alarme",
    "vars": [
        ("TempAtual", "REAL", "Temperatura atual (sensor)"),
        ("Setpoint", "REAL", "Temperatura desejada"),
        ("Kp", "REAL", "Ganho proporcional"),
        ("Ki", "REAL", "Ganho integral"),
        ("Kd", "REAL", "Ganho derivativo"),
        ("SaidaPID", "REAL", "Saida do controlador PID"),
        ("Aquecedor", "BOOL", "Aquecedor ligado"),
        ("AlarmeAlto", "BOOL", "Alarme temperatura alta"),
        ("TempAlto", "REAL", "Limite de alarme alto"),
    ],
    "rungs": [
        {
            "comment": "Bloco PID: calcula saida com base no erro",
            "pid": ("PID1", "TempAtual", "Setpoint", "Kp", "Ki", "Kd", "SaidaPID"),
        },
        {
            "comment": "Ativa aquecedor se saida PID > 0",
            "contacts": [("SaidaPID", False)],
            "coil": ("Aquecedor", False),
        },
        {
            "comment": "Alarme: temperatura acima do limite",
            "contacts": [("TempAtual", False), ("TempAlto", False)],
            "coil": ("AlarmeAlto", False),
        },
    ],
}

EXAMPLES["conveyor"] = {
    "name": "EsteiraControle",
    "description": "Controle de esteira com sensores e atuadores",
    "vars": [
        ("SensorEntrada", "BOOL", "Sensor de peca na entrada"),
        ("SensorSaida", "BOOL", "Sensor de peca na saida"),
        ("MotorEsteira", "BOOL", "Motor da esteira"),
        ("Cilindro", "BOOL", "Cilindro de empurrar"),
        ("TimerCilindro", "TON", "Temporizador do cilindro 1s"),
        ("ContadorPecas", "CTU", "Contador de pecas"),
        ("TotalPecas", "INT", "Total de pecas processadas"),
    ],
    "rungs": [
        {
            "comment": "Liga esteira quando peca detectada na entrada",
            "contacts": [("SensorEntrada", False), ("SensorSaida", True)],
            "coil": ("MotorEsteira", False),
        },
        {
            "comment": "Selo de esteira: mantem ligada ate peca na saida",
            "contacts": [("MotorEsteira", False), ("SensorSaida", True)],
            "coil": ("MotorEsteira", False),
        },
        {
            "comment": "Ativa cilindro quando peca na saida",
            "contacts": [("SensorSaida", False)],
            "coil": ("Cilindro", False),
        },
        {
            "comment": "Temporizador do cilindro",
            "contacts": [("Cilindro", False)],
            "timer": ("TimerCilindro", "Cilindro", "T#1s"),
        },
        {
            "comment": "Desativa cilindro apos timer",
            "contacts": [("TimerCilindro.Q", False)],
            "coil": ("Cilindro", True),
        },
        {
            "comment": "Conta pecas processadas",
            "contacts": [("SensorSaida", False)],
            "counter": ("ContadorPecas", "SensorSaida", "TotalPecas"),
        },
    ],
}


# =========================================================================== #
# RENDERERS (um por formato)
# =========================================================================== #

def render_plcopen_xml(example, project_name):
    """Gera PLCOpen XML (IEC 61131-10)."""
    vars_decl = ""
    for vname, vtype, vdesc in example["vars"]:
        vars_decl += f'''            <variable name="{vname}" type="{vtype}">
              <documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">{vdesc}</xhtml></documentation>
            </variable>\n'''

    rungs_xml = ""
    for i, rung in enumerate(example["rungs"]):
        rungs_xml += f'            <rung>\n'
        rungs_xml += f'              <documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">{rung["comment"]}</xhtml></documentation>\n'
        rungs_xml += '              <leftPowerRail/>\n'

        # Contacts
        x = 40
        for cname, negated in rung.get("contacts", []):
            neg = "true" if negated else "false"
            rungs_xml += f'''              <contact name="{cname}" negated="{neg}" edge="none">
                <position x="{x}" y="20"/>
                <connectionPointIn><relPosition x="0" y="0"/></connectionPointIn>
                <connectionPointOut><relPosition x="20" y="0"/></connectionPointOut>
              </contact>\n'''
            x += 40

        # Timer block
        if "timer" in rung:
            tname, ten, tpt = rung["timer"]
            rungs_xml += f'''              <block typeName="TON" instanceName="{tname}" executionOrderId="{i}">
                <position x="{x}" y="10"/>
                <inputVariables>
                  <variable formalParameter="IN"><connectionPointIn><relPosition x="0" y="5"/></connectionPointIn></variable>
                  <variable formalParameter="PT"><connectionPointIn><relPosition x="0" y="15"/></connectionPointIn>
                    <addData><data name="constantValue" handleUnknown="preserve"><value>{tpt}</value></data></addData>
                  </variable>
                </inputVariables>
                <outputVariables>
                  <variable formalParameter="Q"><connectionPointOut><relPosition x="40" y="5"/></connectionPointOut></variable>
                  <variable formalParameter="ET"><connectionPointOut><relPosition x="40" y="15"/></connectionPointOut></variable>
                </outputVariables>
              </block>\n'''
            x += 60

        # PID block
        if "pid" in rung:
            pname, pin, psp, pkp, pki, pkd, pout = rung["pid"]
            rungs_xml += f'''              <block typeName="PID" instanceName="{pname}" executionOrderId="{i}">
                <position x="{x}" y="10"/>
                <inputVariables>
                  <variable formalParameter="PV"><connectionPointIn><relPosition x="0" y="0"/></connectionPointIn></variable>
                  <variable formalParameter="SP"><connectionPointIn><relPosition x="0" y="10"/></connectionPointIn></variable>
                  <variable formalParameter="KP"><connectionPointIn><relPosition x="0" y="20"/></connectionPointIn></variable>
                  <variable formalParameter="KI"><connectionPointIn><relPosition x="0" y="30"/></connectionPointIn></variable>
                  <variable formalParameter="KD"><connectionPointIn><relPosition x="0" y="40"/></connectionPointIn></variable>
                </inputVariables>
                <outputVariables>
                  <variable formalParameter="OUT"><connectionPointOut><relPosition x="50" y="0"/></connectionPointOut></variable>
                </outputVariables>
              </block>\n'''
            x += 70

        # Coils
        _coils = rung.get("coils", [rung["coil"]] if isinstance(rung.get("coil"), tuple) else [])
        for cname, negated in _coils:
            if isinstance(cname, str):
                neg = "true" if negated else "false"
                rungs_xml += f'''              <coil name="{cname}" negated="{neg}">
                <position x="{x}" y="20"/>
                <connectionPointIn><relPosition x="0" y="0"/></connectionPointIn>
              </coil>\n'''
                x += 40

        # Single coil
        if "coil" in rung and isinstance(rung["coil"], tuple):
            cname, negated = rung["coil"]
            neg = "true" if negated else "false"
            rungs_xml += f'''              <coil name="{cname}" negated="{neg}">
                <position x="{x}" y="20"/>
                <connectionPointIn><relPosition x="0" y="0"/></connectionPointIn>
              </coil>\n'''

        rungs_xml += '              <rightPowerRail/>\n'
        rungs_xml += '            </rung>\n'

    creation_dt = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://www.plcopen.org/xml/tc6_0201">
  <fileHeader companyName="MECATRON" productName="CLP Multi-Gen" productVersion="1.0" creationDateTime="{creation_dt}"/>
  <contentHeader name="{project_name}" modificationDateTime="{creation_dt}">
    <coordinateInfo><ld><scaling x="1" y="1"/></ld></coordinateInfo>
  </contentHeader>
  <types>
    <dataTypes/>
    <pous>
      <pou name="{project_name}" pouType="program">
        <interface>
          <localVars>
{vars_decl}
          </localVars>
        </interface>
        <body>
          <LD>
{rungs_xml}
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
            <pouInstance name="{project_name}" typeName="{project_name}"/>
          </task>
        </resource>
      </configuration>
    </configurations>
  </instances>
  <addData/>
</project>
'''


def render_l5k(example, project_name):
    """Gera L5K (Rockwell/Allen-Bradley)."""
    tags = ""
    for vname, vtype, vdesc in example["vars"]:
        ab_type = {"BOOL": "BOOL", "INT": "INT", "REAL": "REAL", "TON": "TIMER", "CTU": "COUNTER"}.get(vtype, vtype)
        tags += f"  {vname} : {ab_type};\n"

    rungs = ""
    for i, rung in enumerate(example["rungs"]):
        rungs += f"  Rung {i}:\n"
        rungs += f"    {rung['comment']}\n"
        # Build rung text
        contacts = [f"XIC({c[0]})" if not c[1] else f"XIO({c[0]})" for c in rung.get("contacts", [])]
        coil = ""
        if "coil" in rung and isinstance(rung["coil"], tuple):
            cname, neg = rung["coil"]
            coil = f"OTE({cname})" if not neg else f"OTU({cname})"
        elif "coils" in rung:
            coil = " ".join(f"OTE({c[0]})" if not c[1] else f"OTU({c[0]})" for c in rung["coils"])
        timer = ""
        if "timer" in rung:
            tname, ten, tpt = rung["timer"]
            timer = f"TON({tname},?,?)"
        parts = contacts + ([timer] if timer else []) + ([coil] if coil else [])
        rungs += f"    {' '.join(parts)};\n"

    return f'''RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="33.02" TargetName="{project_name}" TargetType="Program" ContainsContext="true" Owner="MECATRON" ExportDate="{datetime.now(timezone.utc).strftime('%a %b %d %H:%M:%S %Y')}" ExportOptions="References NoRawData L5KData DecoratedData Context Dependencies ForceProtectedEncoding AllProjDocTrans">
<Controller Use="Context" Name="CLP">
  <Tags>
{tags}  </Tags>
  <Programs Use="Context">
    <Program Use="Target" Name="{project_name}" TestEdits="false" MainRoutineName="Main" Disabled="false" UseAsFolder="false">
      <Routines>
        <Routine Name="Main" Type="RLL">
          <RLLContent>
{rungs}          </RLLContent>
        </Routine>
      </Routines>
    </Program>
  </Programs>
</Controller>
</RSLogix5000Content>
'''


def render_scl(example, project_name):
    """Gera SCL (Siemens TIA Portal)."""
    # Variable declarations
    vars_decl = ""
    for vname, vtype, vdesc in example["vars"]:
        scl_type = {"BOOL": "Bool", "INT": "Int", "REAL": "Real", "TON": "TON", "CTU": "CTU"}.get(vtype, vtype)
        vars_decl += f'    {vname} : {scl_type}; // {vdesc}\n'

    # Logic
    logic = ""
    for rung in example["rungs"]:
        logic += f'    // {rung["comment"]}\n'
        contacts = " AND ".join(f'"{c[0]}"' if not c[1] else f'NOT "{c[0]}"' for c in rung.get("contacts", []))
        if "coil" in rung and isinstance(rung["coil"], tuple):
            cname, neg = rung["coil"]
            if neg:
                logic += f'    IF {contacts} THEN "{cname}" := FALSE; END_IF;\n'
            else:
                logic += f'    IF {contacts} THEN "{cname}" := TRUE; END_IF;\n'
        elif "coils" in rung:
            for cname, neg in rung["coils"]:
                if neg:
                    logic += f'    IF {contacts} THEN "{cname}" := FALSE; END_IF;\n'
                else:
                    logic += f'    IF {contacts} THEN "{cname}" := TRUE; END_IF;\n'
        if "timer" in rung:
            tname, ten, tpt = rung["timer"]
            logic += f'    "{tname}"(IN := {contacts}, PT := {tpt});\n'
        if "pid" in rung:
            pname, pin, psp, pkp, pki, pkd, pout = rung["pid"]
            logic += f'    "{pname}"(PV := "{pin}", SP := "{psp}", KP := "{pkp}", KI := "{pki}", KD := "{pkd}");\n'
            logic += f'    "{pout}" := "{pname}".OUT;\n'
        logic += "\n"

    return f'''// SCL Program: {project_name}
// Gerado pelo CLP Multi-Gen
// Compativel com: Siemens TIA Portal, Step 7

FUNCTION_BLOCK "{project_name}"
{{ S7_Optimized_Access := 'TRUE' }}
VERSION : 0.1
   VAR
{vars_decl}   END_VAR

BEGIN
{logic}END_FUNCTION_BLOCK
'''


def render_st(example, project_name):
    """Gera Structured Text genérico (IEC 61131-3)."""
    vars_decl = ""
    for vname, vtype, vdesc in example["vars"]:
        vars_decl += f"    {vname} : {vtype}; (* {vdesc} *)\n"

    logic = ""
    for rung in example["rungs"]:
        logic += f"    // {rung['comment']}\n"
        contacts = " AND ".join(f"{c[0]}" if not c[1] else f"NOT {c[0]}" for c in rung.get("contacts", []))
        if "coil" in rung and isinstance(rung["coil"], tuple):
            cname, neg = rung["coil"]
            if neg:
                logic += f"    IF {contacts} THEN {cname} := FALSE; END_IF;\n"
            else:
                logic += f"    IF {contacts} THEN {cname} := TRUE; END_IF;\n"
        elif "coils" in rung:
            for cname, neg in rung["coils"]:
                if neg:
                    logic += f"    IF {contacts} THEN {cname} := FALSE; END_IF;\n"
                else:
                    logic += f"    IF {contacts} THEN {cname} := TRUE; END_IF;\n"
        if "timer" in rung:
            tname, ten, tpt = rung["timer"]
            logic += f"    {tname}(IN := {contacts}, PT := {tpt});\n"
        if "pid" in rung:
            pname, pin, psp, pkp, pki, pkd, pout = rung["pid"]
            logic += f"    {pname}(PV := {pin}, SP := {psp});\n"
            logic += f"    {pout} := {pname}.OUT;\n"
        logic += "\n"

    return f'''// Structured Text Program: {project_name}
// Gerado pelo CLP Multi-Gen
// Compativel com: qualquer IEC 61131-3 (CODESYS, TwinCAT, etc.)

PROGRAM {project_name}
VAR
{vars_decl}END_VAR

{logic}END_PROGRAM
'''


def render_fbd(example, project_name):
    """Gera FBD (Functional Block Diagram) em texto."""
    lines = [f"// FBD Program: {project_name}", "// Gerado pelo CLP Multi-Gen", ""]
    lines.append("VAR")
    for vname, vtype, vdesc in example["vars"]:
        lines.append(f"    {vname} : {vtype}; // {vdesc}")
    lines.append("END_VAR")
    lines.append("")
    lines.append("// Blocos funcionais:")
    for rung in example["rungs"]:
        lines.append(f"// {rung['comment']}")
        contacts = " AND ".join(f"{c[0]}" + (" (NC)" if c[1] else "") for c in rung.get("contacts", []))
        if "coil" in rung and isinstance(rung["coil"], tuple):
            cname, neg = rung["coil"]
            lines.append(f"// [{contacts}] --> {'NOT ' if neg else ''}{cname}")
        elif "coils" in rung:
            for cname, neg in rung["coils"]:
                lines.append(f"// [{contacts}] --> {'NOT ' if neg else ''}{cname}")
        if "timer" in rung:
            tname, ten, tpt = rung["timer"]
            lines.append(f"// TON({tname}): IN={ten}, PT={tpt}")
        if "pid" in rung:
            pname, pin, psp, pkp, pki, pkd, pout = rung["pid"]
            lines.append(f"// PID({pname}): PV={pin}, SP={psp}")
        lines.append("")
    return "\n".join(lines)


# =========================================================================== #
# MAIN
# =========================================================================== #

FORMATS = {
    "plcopen": ("xml", render_plcopen_xml),
    "l5k": ("L5K", render_l5k),
    "scl": ("scl", render_scl),
    "st": ("st", render_st),
    "fbd": ("fbd", render_fbd),
}

def main():
    parser = argparse.ArgumentParser(description="CLP Multi-Platform Generator (IEC 61131-3)")
    parser.add_argument("--format", "-f", choices=list(FORMATS.keys()), default="plcopen",
                        help="Formato de saída")
    parser.add_argument("--example", "-e", default="motor_seal",
                        help="Exemplo de programa (ou 'all' para todos)")
    parser.add_argument("--output", "-o", default=None, help="Arquivo de saída")
    parser.add_argument("--name", "-n", default=None, help="Nome do programa")
    parser.add_argument("--list", "-l", action="store_true", help="Lista exemplos e formatos")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    if args.list:
        print("Exemplos disponíveis:")
        for k, v in EXAMPLES.items():
            print(f"  {k}: {v['description']}")
        print()
        print("Formatos disponíveis:")
        for k, (ext, _) in FORMATS.items():
            print(f"  {k}: .{ext}")
        sys.exit(0)

    if args.example == "all":
        examples_to_gen = list(EXAMPLES.keys())
    else:
        if args.example not in EXAMPLES:
            print(json.dumps({"error": f"exemplo '{args.example}' não encontrado", "available": list(EXAMPLES.keys())}))
            sys.exit(0)
        examples_to_gen = [args.example]

    ext, renderer = FORMATS[args.format]
    results = []

    for ex_key in examples_to_gen:
        ex = EXAMPLES[ex_key]
        prog_name = args.name or ex["name"]
        content = renderer(ex, prog_name)

        if args.output:
            if len(examples_to_gen) == 1:
                out_path = os.path.join(WORKSPACE, args.output)
            else:
                out_path = os.path.join(WORKSPACE, f"{ex_key}.{ext}")
        else:
            out_path = os.path.join(WORKSPACE, f"{ex_key}.{ext}")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        results.append({"example": ex_key, "name": prog_name, "format": args.format,
                        "output": out_path, "size": len(content)})

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"Gerado: {r['output']} ({r['size']} bytes) — {r['example']}")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(0)
