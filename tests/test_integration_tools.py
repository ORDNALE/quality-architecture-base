"""Integração com as ferramentas instaladas (pulados quando a ferramenta não existe).

- `claude plugin validate --strict` roda sempre que o Claude Code estiver instalado (sem chamada
  ao modelo, sem escrita).
- A descoberta da skill pelo Codex usa `codex debug prompt-input` (sem chamada ao modelo), mas lê a
  configuração do usuário e pode gravar logs do Codex; por isso só roda com QAB_INTEGRATION=1.
"""

import json
import os
import shutil
import subprocess
import unittest

from _helpers import QUARKUS_SAMPLE, ROOT, TempDirMixin, git

OPT_IN = os.environ.get("QAB_INTEGRATION") == "1"


@unittest.skipUnless(shutil.which("claude"), "Claude Code não instalado")
class ClaudePluginValidateTest(unittest.TestCase):
    def validate(self, target):
        return subprocess.run(["claude", "plugin", "validate", str(target), "--strict"],
                              capture_output=True, text=True, cwd=ROOT, timeout=120)

    def test_marketplace_plugin_skills_and_agents(self):
        for target in (".", ".claude-plugin/plugin.json", "skills", "agents"):
            with self.subTest(target=target):
                proc = self.validate(target)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("Validation passed", proc.stdout + proc.stderr)


@unittest.skipUnless(OPT_IN and shutil.which("codex"), "defina QAB_INTEGRATION=1 com o Codex instalado")
class CodexSkillDiscoveryTest(TempDirMixin, unittest.TestCase):
    def prompt_for(self, mode):
        project = self.copy_example(QUARKUS_SAMPLE, f"proj-{mode}")
        git(project, "init", "-q")
        subprocess.run(["bash", str(ROOT / "scripts/install.sh"), "--tool", "codex", "--scope", "project",
                        "--project", str(project), "--mode", mode], check=True, capture_output=True)
        proc = subprocess.run(["codex", "debug", "prompt-input", "$quality-review AUDIT"],
                              capture_output=True, text=True, cwd=project, timeout=180)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.dumps(json.loads(proc.stdout), ensure_ascii=False)

    def test_copy_install_is_discovered_as_quality_review(self):
        self.assertIn("- quality-review: Auditoria de arquitetura", self.prompt_for("copy"))

    def test_symlink_install_is_namespaced_by_plugin_manifest(self):
        self.assertIn("- quality-architecture-base:quality-review:", self.prompt_for("symlink"))


if __name__ == "__main__":
    unittest.main()
