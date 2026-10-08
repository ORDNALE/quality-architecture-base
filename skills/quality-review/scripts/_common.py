"""Utilitários compartilhados pelos scripts da skill quality-review.

Somente biblioteca padrão. Nenhuma função aqui escreve no projeto analisado.
"""

from __future__ import annotations

import fnmatch
import os
import re
from pathlib import Path
from typing import Iterator

# Diretórios ignorados por padrão em varreduras: VCS, artefatos de build, dependências,
# caches de IDE e o diretório de artefatos de qualidade do próprio projeto consumidor.
DEFAULT_EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".quality",
        "target",
        "build",
        "dist",
        "out",
        "node_modules",
        ".angular",
        ".gradle",
        ".mvn-cache",
        ".idea",
        ".vscode",
        ".next",
        ".nuxt",
        "coverage",
        "__pycache__",
        ".pytest_cache",
        ".venv",
        "venv",
    }
)


def iter_files(root: Path, excluded_dirs: frozenset[str] = DEFAULT_EXCLUDED_DIRS) -> Iterator[Path]:
    """Percorre arquivos regulares sob ``root`` sem seguir symlinks de diretório."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in excluded_dirs)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.is_file() and not path.is_symlink():
                yield path


def rel(path: Path, root: Path) -> str:
    """Caminho relativo com separador ``/``."""
    return path.relative_to(root).as_posix()


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Converte glob com suporte a ``**`` (qualquer profundidade) em regex ancorada.

    ``*`` não atravessa ``/``; ``**/`` casa zero ou mais diretórios; ``**`` no fim casa tudo.
    """
    pattern = pattern.strip()
    if pattern.startswith("./"):
        pattern = pattern[2:]
    i, out = 0, []
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif c == "*":
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def matches_any(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if glob_to_regex(pattern).match(path) or fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def find_line(text: str, needle: str, start: int = 0) -> int | None:
    """Número da linha (1-based) da primeira ocorrência de ``needle`` a partir de ``start``."""
    idx = text.find(needle, start)
    if idx < 0:
        return None
    return text.count("\n", 0, idx) + 1


def is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
