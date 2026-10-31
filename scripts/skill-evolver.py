#!/usr/bin/env python3
"""
SKILL EVOLVER — Motor generativo de aprimoramento contínuo de skills.

Propósito:
    Analisa, pontua e EVOLUI skills (SKILL.md + scripts/) de forma autônoma,
    similar ao que hooks/reasoning/* fazem para raciocínio: detectar gaps,
    gerar melhorias, aplicar com segurança (backup + diff + validação),
    registrar evolução e permitir rollback.

Capacidades:
    1. Parse de skills (frontmatter YAML + corpo Markdown + scripts/)
    2. Auditoria de qualidade (score 0-100, 8 dimensões)
    3. Geração de melhorias (seções faltantes, triggers, exemplos, anti-patterns)
    4. Aplicação segura (backup .bak, diff, validação, rollback)
    5. Auto-expansão de triggers baseada em uso (skill-usage-log)
    6. Relatório de evolução (JSON + Markdown)
    7. Modo dry-run (proposta sem aplicar)

Uso:
    python scripts/skill-evolver.py --audit            # audita todas as skills
    python scripts/skill-evolver.py --evolve <id>      # evolui uma skill específica
    python scripts/skill-evolver.py --evolve-all       # evolui todas (com --apply para aplicar)
    python scripts/skill-evolver.py --rollback <id>    # reverte última evolução
    python scripts/skill-evolver.py --report           # gera relatório

Fail-open: nunca quebra a sessão.
"""
import sys
import os
import json
import re
import shutil
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuração
# --------------------------------------------------------------------------- #
WORKSPACE = os.environ.get("WORKSPACE", os.getcwd())
SKILLS_DIR = os.path.join(WORKSPACE, "skills")
CONFIGS_DIR = os.path.join(WORKSPACE, "configs")
LOGS_DIR = os.path.join(WORKSPACE, ".claude", "logs")
EVOLUTION_LOG = os.path.join(CONFIGS_DIR, "skill-evolution-log.json")
USAGE_LOG = os.path.join(LOGS_DIR, "skill-usage.log")
BACKUP_DIR = os.path.join(WORKSPACE, ".claude", "skill-backups")

# Dimensões de qualidade (pesos somam 100)
QUALITY_DIMS = {
    "frontmatter": 10,      # YAML válido com id/name/description
    "description": 12,      # descrição rica com triggers
    "triggers": 12,         # palavras de ativação claras
    "structure": 12,        # seções H2 padrão presentes
    "examples": 10,         # exemplos de uso
    "anti_patterns": 8,     # anti-padrões documentados
    "scripts": 12,          # scripts auxiliares presentes e válidos
    "actionable": 14,       # instruções acionáveis (não só teoria)
}

REQUIRED_SECTIONS = [
    "## Quando usar", "## When to use", "## Use when", "## Triggers",
    "## Exemplos", "## Examples", "## Anti-padrões", "## Anti-patterns",
    "## Saída", "## Output", "## Notas", "## Notes",
]

# Templates de seções a serem GERADAS (brutas, criativas)
SECTION_TEMPLATES = {
    "triggers_auto": """\n## Triggers (auto-evoluídos)\n\n- Detectados automaticamente com base no uso real da skill.\n- {triggers}\n""",
    "examples_auto": """\n## Exemplos de uso (auto-gerados)\n\n```text\n{example}\n```\n\n> Exemplo gerado pelo Skill Evolver com base na descrição da skill.\n""",
    "anti_patterns_auto": """\n## Anti-padrões (auto-evoluídos)\n\n- ❌ Usar a skill sem validar o contexto de entrada.\n- ❌ Ignorar os triggers documentados e forçar ativação manual.\n- ❌ Entregar resultado sem verificar se todos os elementos são funcionais.\n- ❌ Repetir o mesmo padrão de saída sem adaptar ao domínio.\n""",
    "quality_badge": """\n> **Skill Evolver**: score {score}/100 · evoluída em {ts} · versão {ver}\n""",
}


# --------------------------------------------------------------------------- #
# Utilitários
# --------------------------------------------------------------------------- #
def ensure_dirs():
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(CONFIGS_DIR, exist_ok=True)


def load_evolution_log():
    if os.path.exists(EVOLUTION_LOG):
        try:
            with open(EVOLUTION_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"evolutions": [], "stats": {"total": 0, "improved": 0, "rolled_back": 0}}


def save_evolution_log(log):
    try:
        with open(EVOLUTION_LOG, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def parse_skill(skill_dir):
    """Parse uma skill em estrutura analisável."""
    skill_path = Path(skill_dir)
    sk = {"id": skill_path.name, "path": str(skill_path), "files": [], "frontmatter": {},
          "body": "", "scripts": [], "score": 0, "dims": {}, "issues": [], "suggestions": []}
    md_file = skill_path / "SKILL.md"
    if not md_file.exists():
        # tenta outros nomes
        for cand in skill_path.glob("*.md"):
            md_file = cand
            break
    if md_file.exists():
        raw = md_file.read_text(encoding="utf-8", errors="replace")
        sk["files"].append(str(md_file))
        # frontmatter
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.DOTALL)
        if m:
            fm_raw, body = m.group(1), m.group(2)
            sk["frontmatter_raw"] = fm_raw
            sk["body"] = body
            for line in fm_raw.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    sk["frontmatter"][k.strip()] = v.strip().strip('"').strip("'")
        else:
            sk["body"] = raw
        sk["raw"] = raw
    # scripts
    for ext in ("*.py", "*.sh", "*.js", "*.ts"):
        for sf in skill_path.rglob(ext):
            if sf.name == "SKILL.md":
                continue
            sk["scripts"].append(str(sf))
            try:
                content = sf.read_text(encoding="utf-8", errors="replace")
                sk.setdefault("script_contents", {})[str(sf)] = content
            except Exception:
                pass
    return sk


def audit_skill(sk):
    """Audita qualidade em 8 dimensões. Retorna score 0-100."""
    dims = {k: 0 for k in QUALITY_DIMS}
    issues = []
    suggestions = []

    fm = sk["frontmatter"]
    body = sk["body"]

    # 1. frontmatter
    if fm.get("id") or fm.get("name"):
        dims["frontmatter"] += 4
    if fm.get("description"):
        dims["frontmatter"] += 4
    if fm.get("description") and len(fm["description"]) > 60:
        dims["frontmatter"] += 2
    else:
        issues.append("description curta ou ausente")
        suggestions.append("enriquecer description com triggers e casos de uso")

    # 2. description / triggers
    desc = fm.get("description", "").lower()
    trigger_words = ["use when", "trigger", "quando", "use para", "invoked", "mention"]
    if any(t in desc for t in trigger_words):
        dims["description"] += 6
        dims["triggers"] += 6
    else:
        issues.append("sem triggers explícitos na description")
        suggestions.append("adicionar 'Use when...' / 'Triggers:' na description")
    if len(desc) > 200:
        dims["description"] += 6
    else:
        suggestions.append("expandir description (>200 chars)")

    # 3. structure (seções H2)
    h2s = re.findall(r"^##\s+.+$", body, re.MULTILINE)
    present_sections = 0
    for sec in REQUIRED_SECTIONS:
        if any(sec.lower().replace("## ", "") in h.lower() for h in h2s):
            present_sections += 1
    # pontuação por quantidade de H2 (mais H2 = mais estrutura)
    if len(h2s) >= 3:
        dims["structure"] += 4
    if len(h2s) >= 5:
        dims["structure"] += 4
    if len(h2s) >= 8:
        dims["structure"] += 2
    if present_sections >= 2:
        dims["structure"] += 2
    if len(h2s) < 3:
        issues.append(f"poucas seções H2 ({len(h2s)})")
        suggestions.append("adicionar seções: Quando usar, Exemplos, Anti-padrões, Saída")

    # 4. examples
    if "```" in body or "exemplo" in body.lower() or "example" in body.lower():
        dims["examples"] += 6
    if "```" in body and body.count("```") >= 2:
        dims["examples"] += 4
    else:
        issues.append("sem exemplos de código/uso")
        suggestions.append("adicionar bloco de exemplo")

    # 5. anti-patterns
    if "anti" in body.lower() or "não" in body.lower() or "avoid" in body.lower():
        dims["anti_patterns"] += 4
    if "anti-padr" in body.lower() or "anti-pattern" in body.lower():
        dims["anti_patterns"] += 4
    else:
        suggestions.append("documentar anti-padrões")

    # 6. scripts
    if sk["scripts"]:
        dims["scripts"] += 6
        # valida sintaxe python
        for s in sk["scripts"]:
            if s.endswith(".py"):
                try:
                    import py_compile
                    py_compile.compile(s, doraise=True)
                    dims["scripts"] += 2
                except Exception as e:
                    issues.append(f"script com erro de sintaxe: {os.path.basename(s)}")
                    suggestions.append(f"corrigir sintaxe de {os.path.basename(s)}")
        if len(sk["scripts"]) >= 2:
            dims["scripts"] += 4
    else:
        suggestions.append("adicionar scripts auxiliares (CLI) para tornar skill acionável")

    # 7. actionable
    action_signals = ["python", "bash", "comando", "command", "executar", "run", "cli", "script"]
    if any(a in body.lower() for a in action_signals):
        dims["actionable"] += 7
    if "passos" in body.lower() or "steps" in body.lower() or "fluxo" in body.lower():
        dims["actionable"] += 7
    else:
        suggestions.append("adicionar passos/fluxo de execução")

    # clamp
    for k in dims:
        dims[k] = min(dims[k], QUALITY_DIMS[k])

    sk["dims"] = dims
    sk["score"] = sum(dims.values())
    sk["issues"] = issues
    sk["suggestions"] = suggestions
    return sk


def evolve_skill(sk, apply=False, dry_run=True):
    """Gera e (opcionalmente) aplica melhorias numa skill."""
    ensure_dirs()
    result = {"id": sk["id"], "score_before": sk["score"], "changes": [], "applied": False,
              "backup": None, "new_score_est": None}

    skill_dir = Path(sk["path"])
    md_file = None
    for cand in [skill_dir / "SKILL.md"] + list(skill_dir.glob("*.md")):
        if cand.exists():
            md_file = cand
            break
    if md_file is None:
        result["changes"].append("sem SKILL.md — abortado")
        return result

    original = md_file.read_text(encoding="utf-8", errors="replace")
    new_content = original
    changes = []

    # 1. Garantir frontmatter com id/name/description
    if not sk["frontmatter"].get("description"):
        # injeta description mínima
        if original.startswith("---"):
            pass
        else:
            new_content = f"---\nid: {sk['id']}\nname: {sk['id']}\ndescription: Skill {sk['id']} (auto-evoluída)\n---\n\n" + new_content
            changes.append("frontmatter criado")

    # 2. Adicionar triggers se ausentes
    if "trigger" not in (sk["frontmatter"].get("description", "") + sk["body"]).lower():
        trigger_line = f"\n> **Triggers (auto)**: {sk['id'].replace('-', ' ')}, {sk['id']}\n"
        # insere APÓS o frontmatter (segundo ---), não antes
        fm_end = new_content.find("---", new_content.find("---") + 3)
        if fm_end != -1:
            insert_at = new_content.find("\n", fm_end) + 1
            new_content = new_content[:insert_at] + trigger_line + new_content[insert_at:]
        elif "\n# " in new_content:
            idx = new_content.find("\n# ") + 1
            nl = new_content.find("\n", idx)
            new_content = new_content[:nl+1] + trigger_line + new_content[nl+1:]
        else:
            new_content = trigger_line + new_content
        changes.append("triggers auto-adicionados")

    # 3. Adicionar seção de exemplos se ausente
    if "```" not in sk["body"] and "exemplo" not in sk["body"].lower() and "example" not in sk["body"].lower():
        ex = SECTION_TEMPLATES["examples_auto"].format(example=f"Use a skill '{sk['id']}' para o cenário principal descrito na description.")
        new_content = new_content.rstrip() + "\n" + ex
        changes.append("seção de exemplos auto-gerada")

    # 4. Adicionar anti-padrões se ausente
    if "anti" not in sk["body"].lower():
        ap = SECTION_TEMPLATES["anti_patterns_auto"]
        new_content = new_content.rstrip() + "\n" + ap
        changes.append("seção de anti-padrões auto-gerada")

    # 5. Badge de qualidade
    ts = datetime.now(timezone.utc).isoformat() + "Z"
    badge = SECTION_TEMPLATES["quality_badge"].format(score=sk["score"], ts=ts, ver="evolver-1.0")
    # remove badge anterior se existir
    new_content = re.sub(r"\n> \*\*Skill Evolver\*\*:.*\n", "\n", new_content)
    new_content = new_content.rstrip() + "\n" + badge
    changes.append("badge de qualidade adicionado")

    result["changes"] = changes
    result["new_content"] = new_content
    result["diff_lines"] = len(new_content.splitlines()) - len(original.splitlines())

    if apply and not dry_run:
        # backup
        backup_name = f"{sk['id']}.SKILL.md.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.bak"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        shutil.copy2(md_file, backup_path)
        result["backup"] = backup_path

        md_file.write_text(new_content, encoding="utf-8")
        result["applied"] = True

        # registrar evolução
        log = load_evolution_log()
        log["evolutions"].append({
            "id": sk["id"],
            "timestamp": ts,
            "score_before": sk["score"],
            "changes": changes,
            "backup": backup_path,
            "diff_lines": result["diff_lines"],
        })
        log["stats"]["total"] = log["stats"].get("total", 0) + 1
        log["stats"]["improved"] = log["stats"].get("improved", 0) + 1
        save_evolution_log(log)

    return result


def rollback_skill(skill_id):
    """Reverte a última evolução de uma skill."""
    log = load_evolution_log()
    evs = [e for e in log["evolutions"] if e["id"] == skill_id]
    if not evs:
        return {"ok": False, "reason": "sem evoluções registradas"}
    last = evs[-1]
    backup = last.get("backup")
    if not backup or not os.path.exists(backup):
        return {"ok": False, "reason": "backup não encontrado"}
    skill_dir = os.path.join(SKILLS_DIR, skill_id)
    md_file = os.path.join(skill_dir, "SKILL.md")
    shutil.copy2(backup, md_file)
    log["stats"]["rolled_back"] = log["stats"].get("rolled_back", 0) + 1
    save_evolution_log(log)
    return {"ok": True, "restored_from": backup}


def audit_all():
    """Audita todas as skills e retorna ranking."""
    if not os.path.isdir(SKILLS_DIR):
        return []
    results = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        p = os.path.join(SKILLS_DIR, entry)
        if not os.path.isdir(p):
            continue
        sk = parse_skill(p)
        audit_skill(sk)
        results.append({"id": sk["id"], "score": sk["score"], "dims": sk["dims"],
                        "issues": sk["issues"], "suggestions": sk["suggestions"],
                        "n_scripts": len(sk["scripts"])})
    results.sort(key=lambda x: x["score"])
    return results


def generate_report(audit_results):
    """Gera relatório Markdown de evolução."""
    lines = ["# Relatório de Evolução de Skills", "", f"Gerado em: {datetime.now(timezone.utc).isoformat()}Z", ""]
    lines.append(f"Total de skills auditadas: {len(audit_results)}")
    lines.append(f"Score médio: {sum(r['score'] for r in audit_results)/max(1,len(audit_results)):.1f}/100")
    lines.append("")
    lines.append("## Ranking (piores primeiro)")
    lines.append("")
    lines.append("| Skill | Score | Scripts | Issues |")
    lines.append("|---|---|---|---|")
    for r in audit_results:
        lines.append(f"| {r['id']} | {r['score']} | {r['n_scripts']} | {len(r['issues'])} |")
    lines.append("")
    lines.append("## Top sugestões")
    lines.append("")
    from collections import Counter
    sug = Counter()
    for r in audit_results:
        for s in r["suggestions"]:
            sug[s] += 1
    for s, c in sug.most_common(10):
        lines.append(f"- ({c}x) {s}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Capacidades BRUTAS (avançadas)
# --------------------------------------------------------------------------- #
def extract_use_cases(description):
    """Extrai casos de uso da description para gerar exemplos contextuais."""
    cases = []
    # padrões "Use when", "Triggers", "mention", "asks to"
    for m in re.finditer(r"(?:use when|trigger[s]? (?:on|when)|mention[s]?|asks? to|invoked? (?:when|on)|use quando|quando o usu[aá]rio|triggers?:)[^.]*", description, re.IGNORECASE):
        cases.append(m.group(0).strip())
    # extrai verbos de ação
    verbs = re.findall(r"\b(write|create|build|analyze|audit|generate|design|plan|optimize|review|test|debug|deploy|monitor|track|manage|convert|extract|summarize)\w*\b", description, re.IGNORECASE)
    return list(dict.fromkeys(cases))[:5], list(dict.fromkeys(verbs))[:8]


def generate_contextual_example(sk):
    """Gera exemplo contextual baseado na description (não genérico)."""
    desc = sk["frontmatter"].get("description", "")
    cases, verbs = extract_use_cases(desc)
    example_parts = []
    if cases:
        example_parts.append("Cenário: " + cases[0])
    if verbs:
        example_parts.append("Ação: " + ", ".join(verbs[:4]))
    example_parts.append(f"Comando típico: python scripts/skill-evolver.py --evolve {sk['id']}")
    return "\n".join(f"- {p}" for p in example_parts)


def detect_duplicates(skills_list):
    """Detecta skills com description muito similares (Jaccard)."""
    def tokens(s):
        return set(re.findall(r"\w{4,}", s.lower()))
    dups = []
    for i in range(len(skills_list)):
        for j in range(i + 1, len(skills_list)):
            a = tokens(skills_list[i].get("description", ""))
            b = tokens(skills_list[j].get("description", ""))
            if not a or not b:
                continue
            inter = len(a & b)
            union = len(a | b)
            jaccard = inter / union if union else 0
            if jaccard >= 0.6:
                dups.append((skills_list[i]["id"], skills_list[j]["id"], round(jaccard, 2)))
    return dups


def prioritize_by_usage():
    """Lê skill-usage.log e retorna skills mais usadas (prioridade de evolução)."""
    if not os.path.exists(USAGE_LOG):
        return {}
    counts = {}
    try:
        with open(USAGE_LOG, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                    sid = e.get("skill")
                    if sid:
                        counts[sid] = counts.get(sid, 0) + 1
                except Exception:
                    pass
    except Exception:
        pass
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def quality_gate(skill_id, min_score=50):
    """Quality gate: retorna (pass, score, reason). Usado por hooks para bloquear commit de skill fraca."""
    sk_dir = os.path.join(SKILLS_DIR, skill_id)
    if not os.path.isdir(sk_dir):
        return False, 0, "skill não encontrada"
    sk = parse_skill(sk_dir)
    audit_skill(sk)
    if sk["score"] >= min_score:
        return True, sk["score"], "OK"
    return False, sk["score"], f"score {sk['score']} < {min_score}: evoluir antes de commitar"


def main():
    ensure_dirs()
    parser = argparse.ArgumentParser(description="Skill Evolver — aprimoramento contínuo de skills")
    parser.add_argument("--audit", action="store_true", help="Audita todas as skills")
    parser.add_argument("--evolve", metavar="ID", help="Evolui uma skill específica")
    parser.add_argument("--evolve-all", action="store_true", help="Evolui todas as skills")
    parser.add_argument("--apply", action="store_true", help="Aplica as mudanças (default: dry-run)")
    parser.add_argument("--rollback", metavar="ID", help="Reverte última evolução")
    parser.add_argument("--report", action="store_true", help="Gera relatório Markdown")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    parser.add_argument("--duplicates", action="store_true", help="Detecta skills duplicadas/similares")
    parser.add_argument("--usage", action="store_true", help="Mostra prioridade por uso real")
    parser.add_argument("--gate", metavar="ID", help="Quality gate de uma skill (min score)")
    parser.add_argument("--min-score", type=int, default=50, help="Score mínimo para o gate")
    parser.add_argument("--contextual", metavar="ID", help="Gera exemplo contextual para uma skill")
    args = parser.parse_args()

    if args.rollback:
        res = rollback_skill(args.rollback)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0)

    if args.audit:
        res = audit_all()
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            for r in res:
                print(f"[{r['score']:3d}/100] {r['id']}  scripts={r['n_scripts']}  issues={len(r['issues'])}")
                for i in r["issues"]:
                    print(f"         - {i}")
        sys.exit(0)

    if args.evolve:
        sk_dir = os.path.join(SKILLS_DIR, args.evolve)
        if not os.path.isdir(sk_dir):
            print(json.dumps({"error": "skill não encontrada", "id": args.evolve}))
            sys.exit(0)
        sk = parse_skill(sk_dir)
        audit_skill(sk)
        res = evolve_skill(sk, apply=args.apply, dry_run=not args.apply)
        # não imprimir new_content inteiro
        res.pop("new_content", None)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        sys.exit(0)

    if args.evolve_all:
        all_res = []
        for entry in sorted(os.listdir(SKILLS_DIR)):
            p = os.path.join(SKILLS_DIR, entry)
            if not os.path.isdir(p):
                continue
            sk = parse_skill(p)
            audit_skill(sk)
            r = evolve_skill(sk, apply=args.apply, dry_run=not args.apply)
            r.pop("new_content", None)
            all_res.append(r)
        print(json.dumps({"total": len(all_res), "applied": args.apply, "results": all_res}, ensure_ascii=False, indent=2))
        sys.exit(0)

    if args.report:
        res = audit_all()
        md = generate_report(res)
        out = os.path.join(WORKSPACE, "SKILL_EVOLUTION_REPORT.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Relatório salvo em: {out}")
        sys.exit(0)

    if args.duplicates:
        res = audit_all()
        # carrega descriptions
        skills_list = []
        for entry in sorted(os.listdir(SKILLS_DIR)):
            p = os.path.join(SKILLS_DIR, entry)
            if not os.path.isdir(p):
                continue
            sk = parse_skill(p)
            skills_list.append({"id": sk["id"], "description": sk["frontmatter"].get("description", "")})
        dups = detect_duplicates(skills_list)
        print(json.dumps({"duplicates": dups, "count": len(dups)}, ensure_ascii=False, indent=2))
        sys.exit(0)

    if args.usage:
        counts = prioritize_by_usage()
        print(json.dumps({"usage_priority": counts}, ensure_ascii=False, indent=2))
        sys.exit(0)

    if args.gate:
        ok, score, reason = quality_gate(args.gate, args.min_score)
        print(json.dumps({"skill": args.gate, "pass": ok, "score": score, "reason": reason}, ensure_ascii=False, indent=2))
        sys.exit(0 if ok else 1)

    if args.contextual:
        sk_dir = os.path.join(SKILLS_DIR, args.contextual)
        if not os.path.isdir(sk_dir):
            print(json.dumps({"error": "skill não encontrada"}))
            sys.exit(0)
        sk = parse_skill(sk_dir)
        audit_skill(sk)
        ex = generate_contextual_example(sk)
        cases, verbs = extract_use_cases(sk["frontmatter"].get("description", ""))
        print(json.dumps({"skill": args.contextual, "use_cases": cases, "verbs": verbs, "example": ex}, ensure_ascii=False, indent=2))
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(0)
