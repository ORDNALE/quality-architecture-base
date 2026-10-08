"""Utilitários compartilhados pelos testes (somente biblioteca padrão)."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "quality-review"
SCRIPTS = SKILL / "scripts"
EXAMPLES = ROOT / "examples"
QUARKUS_SAMPLE = EXAMPLES / "quarkus-layered-sample"
REACT_SAMPLE = EXAMPLES / "react-sample"

sys.dont_write_bytecode = True  # não criar __pycache__ dentro da skill
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def run_script(name: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-W", "error", str(SCRIPTS / name), *map(str, args)],
        capture_output=True, text=True, cwd=cwd,
    )


class TempDirMixin:
    """Cria um diretório temporário por teste, removido ao final."""

    def setUp(self) -> None:  # noqa: D401
        self._tmp = tempfile.TemporaryDirectory(prefix="qab-test-")
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def copy_example(self, source: Path, name: str = "project") -> Path:
        dest = self.tmp / name
        shutil.copytree(source, dest)
        return dest


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=qab", "-c", "user.email=qab@example.invalid", *args],
        cwd=cwd, check=True, capture_output=True, text=True,
    ).stdout
