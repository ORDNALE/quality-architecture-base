#!/usr/bin/env python3
"""Valida a integridade e a coerência da Quality Architecture Base.

Verifica:
  - arquivos vazios;
  - links Markdown relativos e âncoras;
  - frontmatter do SKILL.md (nome, descrição, chaves) e versões coerentes (SKILL, plugin, CHANGELOG);
  - formato das regras (todos os campos, severidade válida) e unicidade de IDs;
  - toda menção a ID de regra, conflito (CF-NN) e guardrail (G-NN) existe;
  - caminhos citados dentro da skill existem;
  - toda regra é alcançável pelo roteamento (SKILL.md ou perfis);
  - workflows, papéis e templates obrigatórios, e seções essenciais dos workflows;
  - vocabulário de severidade/estado consistente entre evidência, contratos e templates;
  - adaptadores: manifesto/marketplace do Claude, subagentes Claude, agentes TOML do Codex.

Uso:
    python3 scripts/validate_repo.py [--root <dir>]
Exit code 0 sem erros; 1 com erros (avisos não falham).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

SKILL_REL = Path("skills/quality-review")
RULE_ID_RE = re.compile(r"\b(?:UNI|ARC|BCK|PER|PRF|FE|TST)-[A-Z0-9]+-\d{3}\b")
RULE_WILDCARD_RE = re.compile(r"\b((?:UNI|ARC|BCK|PER|PRF|FE|TST)-[A-Z0-9]+)-\*")
RULE_HEADING_RE = re.compile(r"^### ((?:UNI|ARC|BCK|PER|PRF|FE|TST)-[A-Z0-9]+-\d{3}) — (.+)$", re.M)
CF_RE = re.compile(r"\bCF-\d{2}\b")
CF_HEADING_RE = re.compile(r"^### (CF-\d{2}) — ", re.M)
G_RE = re.compile(r"\bG-\d{2}\b")
G_ROW_RE = re.compile(r"^\| (G-\d{2}) \|", re.M)
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
SKILL_PATH_RE = re.compile(r"`((?:rules|profiles|workflows|roles|templates|references|scripts)/[^`\s<>*]*)`")
SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
STATES = ["CONFIRMED", "PROBABLE", "NEEDS_VERIFICATION", "NOT_REPRODUCED"]
RULE_FIELDS = [
    "Aplica-se quando",
    "Verificar",
    "Evidência mínima",
    "Severidade base",
    "Falsos positivos / cuidados",
    "Correção preferida",
    "Conflitos",
]
SKILL_ALLOWED_KEYS = {"name", "description", "metadata", "license", "compatibility", "allowed-tools"}
TEXT_SUFFIXES = {".md", ".toml", ".json", ".yaml", ".yml", ".py", ".sh", ".template", ".java", ".tsx", ".ts", ".xml", ".properties", ".sql"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", "target", ".pytest_cache"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def files(root: Path, suffixes: set[str] | None = None) -> list[Path]:
    out = []
    for p in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.is_file() and (suffixes is None or p.suffix in suffixes):
            out.append(p)
    return out


def strip_fences(text: str) -> str:
    """Remove blocos ``` ``` (mantendo as linhas) para não validar exemplos de código."""
    return re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def slugify(heading: str) -> str:
    """Slug no estilo GitHub."""
    text = heading.strip().lower()
    text = re.sub(r"[`*_]", "", text)
    text = "".join(ch for ch in text if ch.isalnum() or ch in " -" or unicodedata.category(ch).startswith("L"))
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    text = strip_fences(path.read_text(encoding="utf-8"))
    result, counts = set(), {}
    for m in re.finditer(r"^#{1,6} (.+)$", text, re.M):
        slug = slugify(m.group(1))
        n = counts.get(slug, 0)
        result.add(slug if n == 0 else f"{slug}-{n}")
        counts[slug] = n + 1
    return result


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    data: dict[str, str] = {}
    current = None
    for line in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        nested = re.match(r"^\s+([\w-]+):\s*(.*)$", line)
        if top:
            current = top.group(1)
            data[current] = top.group(2).strip().strip('"')
        elif nested and current:
            data[f"{current}.{nested.group(1)}"] = nested.group(2).strip().strip('"')
    return data, text[m.end():]


# --------------------------------------------------------------------------- verificações

def check_empty(root: Path, rep: Report) -> None:
    for p in files(root):
        if p.stat().st_size == 0:
            rep.error(f"arquivo vazio: {p.relative_to(root)}")


def check_links(root: Path, rep: Report) -> None:
    for md in files(root, {".md"}):
        text = strip_fences(md.read_text(encoding="utf-8"))
        for m in LINK_RE.finditer(text):
            target = m.group(1)
            if re.match(r"^[a-z]+:", target) or target.startswith("mailto:"):
                continue
            path_part, _, anchor = target.partition("#")
            dest = md if not path_part else (md.parent / path_part).resolve()
            line = text.count("\n", 0, m.start()) + 1
            where = f"{md.relative_to(root)}:{line}"
            if not dest.exists():
                rep.error(f"link quebrado em {where}: {target}")
                continue
            if anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                rep.error(f"âncora inexistente em {where}: {target}")


def check_skill_frontmatter(root: Path, rep: Report) -> str | None:
    skill_md = root / SKILL_REL / "SKILL.md"
    if not skill_md.is_file():
        rep.error("SKILL.md ausente")
        return None
    parsed = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if not parsed:
        rep.error("SKILL.md sem frontmatter YAML")
        return None
    data, body = parsed
    top_keys = {k for k in data if "." not in k}
    if not top_keys <= SKILL_ALLOWED_KEYS:
        rep.error(f"SKILL.md: chaves de frontmatter não suportadas: {sorted(top_keys - SKILL_ALLOWED_KEYS)}")
    name = data.get("name", "")
    if name != skill_md.parent.name:
        rep.error(f"SKILL.md: name '{name}' difere do diretório '{skill_md.parent.name}'")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        rep.error(f"SKILL.md: name inválido '{name}'")
    desc = data.get("description", "")
    if not desc:
        rep.error("SKILL.md: description vazia")
    elif len(desc) > 1024:
        rep.error(f"SKILL.md: description com {len(desc)} caracteres (máx. 1024)")
    if len(body.splitlines()) > 500:
        rep.warn("SKILL.md com mais de 500 linhas; mova detalhes para arquivos de referência")
    return data.get("metadata.version")


def collect_rules(root: Path, rep: Report) -> dict[str, Path]:
    rules: dict[str, Path] = {}
    for md in sorted((root / SKILL_REL / "rules").rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        headings = list(RULE_HEADING_RE.finditer(text))
        if not headings:
            rep.error(f"arquivo de regras sem regras: {md.relative_to(root)}")
        for i, h in enumerate(headings):
            rid = h.group(1)
            if rid in rules:
                rep.error(f"ID de regra duplicado {rid}: {rules[rid].relative_to(root)} e {md.relative_to(root)}")
            rules[rid] = md
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            section = text[h.end():end]
            for field in RULE_FIELDS:
                fm = re.search(rf"^- \*\*{re.escape(field)}:\*\*\s*(.+)$", section, re.M)
                if not fm or not fm.group(1).strip():
                    rep.error(f"{rid} ({md.relative_to(root)}): campo ausente ou vazio '{field}'")
                elif field == "Severidade base" and not fm.group(1).strip().startswith(tuple(SEVERITIES)):
                    rep.error(f"{rid}: severidade base inválida '{fm.group(1).strip()}'")
                elif field == "Conflitos":
                    value = fm.group(1).strip()
                    if value != "nenhum conhecido" and not CF_RE.search(value):
                        rep.error(f"{rid}: campo Conflitos deve citar CF-NN ou 'nenhum conhecido'")
        # cabeçalhos que parecem regra mas fogem do formato
        for line in text.splitlines():
            if line.startswith("### ") and RULE_ID_RE.search(line) and not RULE_HEADING_RE.match(line):
                rep.error(f"cabeçalho de regra fora do formato em {md.relative_to(root)}: {line}")
    return rules


def check_references(root: Path, rules: dict[str, Path], rep: Report) -> None:
    skill = root / SKILL_REL
    conflicts = set(CF_HEADING_RE.findall((skill / "references/conflict-resolution.md").read_text(encoding="utf-8")))
    guardrails = set(G_ROW_RE.findall((skill / "references/safety.md").read_text(encoding="utf-8")))
    if not conflicts:
        rep.error("nenhum conflito CF-NN definido")
    if not guardrails:
        rep.error("nenhum guardrail G-NN definido")
    prefixes = {rid.rsplit("-", 1)[0] for rid in rules}
    for p in files(root, TEXT_SUFFIXES):
        rel = p.relative_to(root)
        if rel.parts[0] == "tests" or p.name == "validate_repo.py":
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix == ".md":
            text = strip_fences(text)
        for rid in set(RULE_ID_RE.findall(text)):
            if rid not in rules:
                rep.error(f"{rel}: menciona regra inexistente {rid}")
        for prefix in set(RULE_WILDCARD_RE.findall(text)):
            if prefix not in prefixes:
                rep.error(f"{rel}: menciona grupo de regras inexistente {prefix}-*")
        for cf in set(CF_RE.findall(text)):
            if cf not in conflicts:
                rep.error(f"{rel}: menciona conflito inexistente {cf}")
        for g in set(G_RE.findall(text)):
            if g not in guardrails:
                rep.error(f"{rel}: menciona guardrail inexistente {g}")


def check_skill_paths(root: Path, rep: Report) -> None:
    skill = root / SKILL_REL
    candidates = list(skill.rglob("*.md")) + list((root / "agents").glob("*.md")) + list((root / "integrations").rglob("*.toml"))
    for p in candidates:
        text = p.read_text(encoding="utf-8")
        for m in SKILL_PATH_RE.finditer(text):
            ref = m.group(1).rstrip(".,;:)")
            if ref.endswith("/"):
                ref = ref[:-1]
            if not (skill / ref).exists():
                rep.error(f"{p.relative_to(root)}: caminho da skill inexistente `{m.group(1)}`")


def check_routing(root: Path, rep: Report) -> None:
    skill = root / SKILL_REL
    routing_text = (skill / "SKILL.md").read_text(encoding="utf-8")
    for prof in (skill / "profiles").rglob("*.md"):
        routing_text += prof.read_text(encoding="utf-8")
    for rule_file in sorted((skill / "rules").rglob("*.md")):
        rel = rule_file.relative_to(skill).as_posix()
        directory = rule_file.parent.relative_to(skill).as_posix() + "/"
        stem_pattern = f"{directory}<"  # ex.: rules/architecture/<perfil>.md
        if rel not in routing_text and f"`{directory}`" not in routing_text and stem_pattern not in routing_text:
            rep.error(f"regra não alcançável pelo roteamento (SKILL.md/perfis): {rel}")


def check_structure(root: Path, rep: Report) -> None:
    skill = root / SKILL_REL
    required = {
        "workflows": ["INIT.md", "AUDIT.md", "FIX.md", "REVIEW.md"],
        "roles": ["ARCHITECTURE_AUDITOR.md", "CONTROLLED_REFACTORER.md", "REGRESSION_VALIDATOR.md"],
        "templates": ["PROJECT_PROFILE.md", "ARCHITECTURE_CONTRACT.md", "AUDIT_REPORT.md", "REVIEW_REPORT.md",
                      "REFACTORING_PLAN.md", "REGRESSION_REPORT.md", "QUALITY_STATE.md"],
        "profiles/architecture": ["layered.md", "hexagonal.md", "modular.md", "custom.md"],
        "profiles/stack": ["java-quarkus.md", "postgresql.md", "angular.md", "react.md", "typescript.md"],
        "references": ["contracts.md", "evidence.md", "conflict-resolution.md", "safety.md"],
    }
    skill_text = (skill / "SKILL.md").read_text(encoding="utf-8")
    for directory, names in required.items():
        for name in names:
            path = skill / directory / name
            if not path.is_file():
                rep.error(f"arquivo obrigatório ausente: {path.relative_to(root)}")
    for wf in required["workflows"]:
        text = (skill / "workflows" / wf).read_text(encoding="utf-8")
        for section in ("## Proibido", "## Passos", "## Critérios de saída"):
            if section not in text:
                rep.error(f"workflows/{wf}: seção ausente '{section}'")
        if f"workflows/{wf}" not in skill_text:
            rep.error(f"SKILL.md não roteia workflows/{wf}")
    for role in required["roles"]:
        if f"roles/{role}" not in skill_text:
            rep.error(f"SKILL.md não referencia roles/{role}")
    all_text = "".join(p.read_text(encoding="utf-8") for p in skill.rglob("*.md"))
    for tpl in required["templates"]:
        if all_text.count(f"templates/{tpl}") == 0 and all_text.count(f"`{tpl}`") == 0:
            rep.error(f"template não referenciado por nenhum arquivo da skill: {tpl}")
    # Guardrails críticos presentes nos workflows certos
    for wf in ("INIT.md", "AUDIT.md", "REVIEW.md"):
        if "G-02" not in (skill / "workflows" / wf).read_text(encoding="utf-8"):
            rep.error(f"workflows/{wf} deve proibir edição de fontes (G-02)")
    fix = (skill / "workflows/FIX.md").read_text(encoding="utf-8")
    for needle in ("fix_gate.py", "AUTHORIZED", "G-04", "G-05"):
        if needle not in fix:
            rep.error(f"workflows/FIX.md deve conter '{needle}'")


def check_vocabulary(root: Path, rep: Report) -> None:
    skill = root / SKILL_REL
    for rel in ("references/evidence.md", "references/contracts.md", "templates/AUDIT_REPORT.md"):
        text = (skill / rel).read_text(encoding="utf-8")
        for word in SEVERITIES + STATES:
            if word not in text:
                rep.error(f"{rel}: termo de severidade/estado ausente '{word}'")
    # Termos traduzidos/variantes que indicariam vocabulário divergente
    for p in skill.rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        for bad in ("CONFIRMADO", "PROVÁVEL", "CRÍTICO"):
            if re.search(rf"\b{bad}\b", text):
                rep.error(f"{p.relative_to(root)}: use o termo canônico em inglês em vez de '{bad}'")


def check_adapters(root: Path, skill_version: str | None, rep: Report) -> None:
    plugin_path = root / ".claude-plugin/plugin.json"
    market_path = root / ".claude-plugin/marketplace.json"
    plugin = market = None
    for path in (plugin_path, market_path):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            rep.error(f"{path.relative_to(root)} inválido: {exc}")
            continue
        if path == plugin_path:
            plugin = data
        else:
            market = data
    if plugin:
        # Verificado em Claude Code 2.1.295: agentes listados pela chave "agents" do manifesto não
        # carregaram numa instalação via marketplace; a pasta padrão agents/ carrega.
        if "agents" in plugin:
            rep.error("plugin.json não deve declarar 'agents'; use a pasta padrão agents/ na raiz")
        if not sorted((root / "agents").glob("*.md")):
            rep.error("pasta agents/ (subagentes do Claude Code) vazia ou ausente")
        if skill_version and plugin.get("version") != skill_version:
            rep.error(f"versão do plugin ({plugin.get('version')}) ≠ versão da skill ({skill_version})")
    if plugin and market:
        names = [p.get("name") for p in market.get("plugins", [])]
        if plugin.get("name") not in names:
            rep.error("marketplace.json não lista o plugin de plugin.json")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.M)
    if not m:
        rep.error("CHANGELOG.md sem versão no formato '## [x.y.z]'")
    elif skill_version and m.group(1) != skill_version:
        rep.error(f"versão do CHANGELOG ({m.group(1)}) ≠ versão da skill ({skill_version})")

    roles = {
        "auditor": "ARCHITECTURE_AUDITOR.md",
        "refactorer": "CONTROLLED_REFACTORER.md",
        "validator": "REGRESSION_VALIDATOR.md",
    }
    for md in sorted((root / "agents").glob("*.md")):
        parsed = parse_frontmatter(md.read_text(encoding="utf-8"))
        if not parsed:
            rep.error(f"{md.relative_to(root)}: sem frontmatter")
            continue
        data, body = parsed
        for key in ("name", "description", "tools"):
            if not data.get(key):
                rep.error(f"{md.relative_to(root)}: campo '{key}' ausente")
        if data.get("name") != md.stem:
            rep.error(f"{md.relative_to(root)}: name '{data.get('name')}' difere do arquivo")
        role = next((r for k, r in roles.items() if k in md.stem), None)
        if role and f"roles/{role}" not in body:
            rep.error(f"{md.relative_to(root)}: não aponta para roles/{role}")
        if "refactorer" not in md.stem and re.search(r"\b(Edit|Write)\b", data.get("tools", "")):
            rep.error(f"{md.relative_to(root)}: papel somente leitura com ferramenta de edição")

    names = set()
    for toml_file in sorted((root / "integrations/codex/agents").glob("*.toml")):
        if tomllib is None:
            rep.warn("tomllib indisponível (Python < 3.11); agentes Codex não validados")
            break
        try:
            data = tomllib.loads(toml_file.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            rep.error(f"{toml_file.relative_to(root)}: TOML inválido: {exc}")
            continue
        for key in ("name", "description", "developer_instructions"):
            if not str(data.get(key, "")).strip():
                rep.error(f"{toml_file.relative_to(root)}: campo obrigatório '{key}' ausente")
        if data.get("name") != toml_file.stem:
            rep.error(f"{toml_file.relative_to(root)}: name '{data.get('name')}' difere do arquivo")
        if data.get("name") in names:
            rep.error(f"agente Codex duplicado: {data.get('name')}")
        names.add(data.get("name"))
        role = next((r for k, r in roles.items() if k in toml_file.stem), None)
        if role and f"roles/{role}" not in data.get("developer_instructions", ""):
            rep.error(f"{toml_file.relative_to(root)}: não aponta para roles/{role}")
    if "auditor" in " ".join(names):
        auditor = tomllib.loads((root / "integrations/codex/agents/quality_auditor.toml").read_text(encoding="utf-8")) if tomllib else {}
        if tomllib and auditor.get("sandbox_mode") != "read-only":
            rep.error("quality_auditor.toml deve usar sandbox_mode = \"read-only\"")

    yaml_text = (root / SKILL_REL / "agents/openai.yaml").read_text(encoding="utf-8")
    for key in ("interface:", "display_name:", "short_description:", "policy:", "allow_implicit_invocation:"):
        if key not in yaml_text:
            rep.error(f"agents/openai.yaml: chave ausente '{key}'")


def validate(root: Path) -> Report:
    rep = Report()
    check_empty(root, rep)
    check_links(root, rep)
    version = check_skill_frontmatter(root, rep)
    rules = collect_rules(root, rep)
    check_references(root, rules, rep)
    check_skill_paths(root, rep)
    check_routing(root, rep)
    check_structure(root, rep)
    check_vocabulary(root, rep)
    check_adapters(root, version, rep)
    rep.rules_count = len(rules)  # type: ignore[attr-defined]
    return rep


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    rep = validate(args.root.resolve())
    for w in rep.warnings:
        print(f"AVISO: {w}")
    for e in rep.errors:
        print(f"ERRO:  {e}")
    print(f"regras: {getattr(rep, 'rules_count', 0)} · erros: {len(rep.errors)} · avisos: {len(rep.warnings)}")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
