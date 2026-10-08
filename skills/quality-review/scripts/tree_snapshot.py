#!/usr/bin/env python3
"""Snapshot de hashes de um projeto para provar que fontes não mudaram (ou só no escopo).

create  grava um snapshot JSON FORA do projeto (recusa caminho interno).
compare recalcula e lista arquivos adicionados, removidos e modificados. Alterações que casam
        com --allow são aceitas. Exit code 0 = nenhuma alteração não permitida; 3 = há
        alterações não permitidas; 1 = erro de uso.

Diretórios de build/dependências/VCS e `.quality/` são ignorados por padrão (ver _common.py).

Uso:
    python3 tree_snapshot.py create  <projeto> --output <arquivo.json> [--exclude <glob> ...]
    python3 tree_snapshot.py compare <projeto> --snapshot <arquivo.json> [--allow <glob> ...] [--format text|json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # não gravar __pycache__ dentro da skill instalada
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import is_inside, iter_files, matches_any, rel  # noqa: E402

FORMAT_VERSION = 1


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(root: Path, excludes: list[str]) -> dict[str, str]:
    files = {}
    for path in iter_files(root):
        relative = rel(path, root)
        if excludes and matches_any(relative, excludes):
            continue
        files[relative] = file_hash(path)
    return files


def diff(old: dict[str, str], new: dict[str, str]) -> dict[str, list[str]]:
    return {
        "added": sorted(set(new) - set(old)),
        "removed": sorted(set(old) - set(new)),
        "modified": sorted(p for p in set(old) & set(new) if old[p] != new[p]),
    }


def cmd_create(args: argparse.Namespace) -> int:
    root = args.project.resolve()
    output = args.output.resolve()
    if is_inside(output, root):
        print(f"erro: o snapshot deve ficar FORA do projeto analisado ({output})", file=sys.stderr)
        return 1
    data = {"format": FORMAT_VERSION, "root": str(root), "excludes": args.exclude, "files": collect(root, args.exclude)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")
    print(f"snapshot: {len(data['files'])} arquivos -> {output}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    root = args.project.resolve()
    data = json.loads(args.snapshot.read_text(encoding="utf-8"))
    if data.get("format") != FORMAT_VERSION:
        print("erro: formato de snapshot desconhecido", file=sys.stderr)
        return 1
    changes = diff(data["files"], collect(root, data.get("excludes") or []))
    allowed = {k: [p for p in v if args.allow and matches_any(p, args.allow)] for k, v in changes.items()}
    disallowed = {k: [p for p in v if p not in allowed[k]] for k, v in changes.items()}
    has_disallowed = any(disallowed.values())
    if args.format == "json":
        print(json.dumps({"allowed": allowed, "disallowed": disallowed, "ok": not has_disallowed}, indent=2, ensure_ascii=False))
    else:
        total = sum(len(v) for v in changes.values())
        print(f"alterações desde o snapshot: {total} (permitidas: {sum(len(v) for v in allowed.values())})")
        for kind in ("added", "removed", "modified"):
            for p in disallowed[kind]:
                print(f"  NÃO PERMITIDA  {kind:8s} {p}")
            for p in allowed[kind]:
                print(f"  permitida      {kind:8s} {p}")
        print("resultado: OK" if not has_disallowed else "resultado: ALTERAÇÕES NÃO PERMITIDAS")
    return 3 if has_disallowed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create")
    c.add_argument("project", type=Path)
    c.add_argument("--output", type=Path, required=True)
    c.add_argument("--exclude", action="append", default=[], help="glob relativo a ignorar (repetível)")
    c.set_defaults(func=cmd_create)
    k = sub.add_parser("compare")
    k.add_argument("project", type=Path)
    k.add_argument("--snapshot", type=Path, required=True)
    k.add_argument("--allow", action="append", default=[], help="glob de alteração permitida (repetível)")
    k.add_argument("--format", choices=("text", "json"), default="text")
    k.set_defaults(func=cmd_compare)
    args = parser.parse_args(argv)
    if not args.project.is_dir():
        print(f"erro: diretório não encontrado: {args.project}", file=sys.stderr)
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
