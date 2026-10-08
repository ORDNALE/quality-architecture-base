#!/usr/bin/env python3
"""Portão de autorização do modo FIX (somente leitura).

Valida o bloco de autorização de um REFACTORING_PLAN.md e, opcionalmente, se os arquivos
alterados estão dentro de "Arquivos autorizados".

A "Evidência da autorização" precisa citar o identificador do plano (nome do arquivo sem .md).
Como o plano não existe quando o usuário pede o FIX, isso impede que o próprio pedido inicial seja
usado como autorização: a aprovação tem de ser posterior e referir-se a este plano.

Exit codes:
    0  autorizado (e, se verificado, todas as alterações dentro do escopo)
    1  erro de uso ou plano sem bloco de autorização legível
    2  NÃO autorizado (status diferente de AUTHORIZED ou campos obrigatórios vazios)
    3  autorizado, mas há arquivos alterados FORA do escopo

Uso:
    python3 fix_gate.py check <plano.md>
    python3 fix_gate.py check <plano.md> --project <dir> --changed-from-git
    python3 fix_gate.py check <plano.md> --project <dir> --changed-from-snapshot <baseline.json>
    python3 fix_gate.py check <plano.md> --changed caminho/A.java --changed caminho/B.java

--changed-from-git considera TODAS as alterações não commitadas (inclusive as que já existiam
antes do FIX). Se havia alterações do usuário antes do FIX, prefira --changed-from-snapshot com o
snapshot de baseline criado por tree_snapshot.py.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.dont_write_bytecode = True  # não gravar __pycache__ dentro da skill instalada
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import matches_any  # noqa: E402

START = "<!-- qab:authorization:start -->"
END = "<!-- qab:authorization:end -->"
VALID_STATUS = {"PENDING", "AUTHORIZED", "REJECTED"}
QUALITY_DIR = ".quality/"


@dataclass
class Authorization:
    status: str = ""
    authorized_by: str = ""
    date: str = ""
    evidence: str = ""
    findings: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    business_rule_change: str = ""


@dataclass
class GateResult:
    authorized: bool
    problems: list[str]
    authorization: Authorization
    changed: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)


def _clean(value: str) -> str:
    value = re.sub(r"<!--.*?-->", "", value).strip()
    # Placeholders de template (<...>) contam como vazio.
    return "" if re.fullmatch(r"<[^>]*>", value) else value


def parse_authorization(text: str) -> Authorization | None:
    if START not in text or END not in text:
        return None
    block = text.split(START, 1)[1].split(END, 1)[0]
    auth = Authorization()
    current_list: list[str] | None = None
    keys = {
        "status": "status",
        "autorizado por": "authorized_by",
        "data": "date",
        "evidência da autorização": "evidence",
        "evidencia da autorizacao": "evidence",
        "achados autorizados": "findings",
        "arquivos autorizados": "files",
        "alteração de regra de negócio autorizada": "business_rule_change",
        "alteracao de regra de negocio autorizada": "business_rule_change",
    }
    for line in block.splitlines():
        top = re.match(r"^-\s*([^:]+):\s*(.*)$", line)
        sub = re.match(r"^\s{2,}-\s*(.+)$", line)
        if top:
            attr = keys.get(top.group(1).strip().lower())
            value = _clean(top.group(2))
            current_list = None
            if attr in {"findings", "files"}:
                current_list = getattr(auth, attr)
                current_list.extend(v.strip() for v in value.split(",") if v.strip())
            elif attr:
                setattr(auth, attr, value)
        elif sub and current_list is not None:
            item = _clean(sub.group(1).strip().strip("`"))
            if item:
                current_list.append(item)
    return auth


def validate(auth: Authorization, plan_id: str | None = None) -> list[str]:
    problems = []
    status = auth.status.upper()
    if status not in VALID_STATUS:
        problems.append(f"Status inválido ou ausente: '{auth.status}' (esperado um de {sorted(VALID_STATUS)})")
    elif status != "AUTHORIZED":
        problems.append(f"Status é {status}; FIX exige AUTHORIZED")
    if not auth.authorized_by:
        problems.append("'Autorizado por' vazio")
    if not auth.date:
        problems.append("'Data' vazia")
    if not auth.evidence:
        problems.append("'Evidência da autorização' vazia (cite a autorização literal do usuário)")
    elif plan_id and plan_id.lower() not in auth.evidence.lower():
        problems.append(
            f"'Evidência da autorização' não cita o identificador do plano '{plan_id}': a autorização "
            "deve ser uma mensagem do usuário posterior à apresentação do plano (o pedido inicial de FIX não serve)"
        )
    if not auth.findings:
        problems.append("'Achados autorizados' vazio")
    if not auth.files:
        problems.append("'Arquivos autorizados' vazio")
    return problems


def changed_from_git(project: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(project), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        check=True, capture_output=True,
    ).stdout.decode("utf-8", errors="replace")
    entries = out.split("\0")
    paths, i = [], 0
    while i < len(entries):
        entry = entries[i]
        if len(entry) < 4:
            i += 1
            continue
        code, path = entry[:2], entry[3:]
        paths.append(path)
        if "R" in code or "C" in code:  # renomeação/cópia: próximo campo é a origem
            paths.append(entries[i + 1])
            i += 1
        i += 1
    return sorted(set(paths))


def changed_from_snapshot(project: Path, snapshot: Path) -> list[str]:
    from tree_snapshot import collect, diff  # noqa: PLC0415 — import local intencional

    data = json.loads(snapshot.read_text(encoding="utf-8"))
    changes = diff(data["files"], collect(project.resolve(), data.get("excludes") or []))
    return sorted({p for v in changes.values() for p in v})


def check(plan: Path, changed: list[str] | None) -> GateResult | None:
    auth = parse_authorization(plan.read_text(encoding="utf-8"))
    if auth is None:
        return None
    problems = validate(auth, plan.stem)
    result = GateResult(authorized=not problems, problems=problems, authorization=auth)
    if changed is not None:
        result.changed = [p for p in changed if not p.startswith(QUALITY_DIR)]
        result.out_of_scope = [p for p in result.changed if not matches_any(p, auth.files)]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("check")
    c.add_argument("plan", type=Path)
    c.add_argument("--project", type=Path, default=Path("."))
    group = c.add_mutually_exclusive_group()
    group.add_argument("--changed-from-git", action="store_true")
    group.add_argument("--changed-from-snapshot", type=Path)
    group.add_argument("--changed", action="append", help="arquivo alterado (relativo ao projeto); repetível")
    c.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    if not args.plan.is_file():
        print(f"erro: plano não encontrado: {args.plan}", file=sys.stderr)
        return 1
    changed = None
    try:
        if args.changed_from_git:
            changed = changed_from_git(args.project)
        elif args.changed_from_snapshot:
            changed = changed_from_snapshot(args.project, args.changed_from_snapshot)
        elif args.changed:
            changed = args.changed
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        print(f"erro ao obter arquivos alterados: {exc}", file=sys.stderr)
        return 1

    result = check(args.plan, changed)
    if result is None:
        print(f"erro: bloco de autorização ({START} … {END}) não encontrado em {args.plan}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    else:
        print(f"plano: {args.plan}")
        print(f"status: {result.authorization.status or '(vazio)'}")
        if result.problems:
            print("NÃO AUTORIZADO:")
            for p in result.problems:
                print(f"  - {p}")
        else:
            print(f"autorizado por: {result.authorization.authorized_by} em {result.authorization.date}")
            print(f"achados: {', '.join(result.authorization.findings)}")
            print(f"arquivos autorizados: {', '.join(result.authorization.files)}")
        if changed is not None:
            print(f"arquivos alterados (excluindo {QUALITY_DIR}): {len(result.changed)}")
            for p in result.out_of_scope:
                print(f"  FORA DO ESCOPO: {p}")
    if not result.authorized:
        return 2
    if result.out_of_scope:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
