import os
import shutil
import subprocess
import unittest

from _helpers import ROOT, TempDirMixin

INSTALL = ROOT / "scripts/install.sh"


@unittest.skipUnless(shutil.which("bash"), "bash indisponível")
class InstallTest(TempDirMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.project = self.tmp / "proj"
        self.home = self.tmp / "home"
        self.project.mkdir()
        self.home.mkdir()

    def install(self, *args):
        env = {**os.environ, "HOME": str(self.home)}
        return subprocess.run(["bash", str(INSTALL), *map(str, args)], capture_output=True, text=True, env=env)

    def files(self, base):
        return sorted(p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file() or p.is_symlink())

    def test_dry_run_changes_nothing(self):
        proc = self.install("--tool", "both", "--scope", "project", "--project", self.project, "--with-agents", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(list(self.project.iterdir()), [])
        self.assertIn("[dry-run]", proc.stdout)

    def test_default_modes_symlink_claude_copy_codex(self):
        proc = self.install("--tool", "both", "--scope", "project", "--project", self.project, "--with-agents")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        claude_skill = self.project / ".claude/skills/quality-review"
        codex_skill = self.project / ".agents/skills/quality-review"
        self.assertTrue(claude_skill.is_symlink())
        self.assertEqual(claude_skill.resolve(), (ROOT / "skills/quality-review").resolve())
        self.assertFalse(codex_skill.is_symlink())
        self.assertTrue((codex_skill / "SKILL.md").is_file())
        self.assertTrue((codex_skill / ".qab-install").is_file())
        self.assertEqual(sorted(p.name for p in (self.project / ".claude/agents").iterdir()),
                         ["quality-auditor.md", "quality-refactorer.md", "quality-validator.md"])
        self.assertEqual(sorted(p.name for p in (self.project / ".codex/agents").iterdir()),
                         ["quality_auditor.toml", "quality_refactorer.toml", "quality_validator.toml"])

    def test_does_not_touch_project_sources(self):
        (self.project / "pom.xml").write_text("<project/>")
        (self.project / "AGENTS.md").write_text("instruções do time")
        (self.project / ".gitignore").write_text("target/\n")
        self.install("--tool", "both", "--scope", "project", "--project", self.project, "--with-agents")
        self.assertEqual((self.project / "AGENTS.md").read_text(), "instruções do time")
        self.assertEqual((self.project / ".gitignore").read_text(), "target/\n")
        self.assertEqual((self.project / "pom.xml").read_text(), "<project/>")

    def test_refuses_overwrite_without_update_and_foreign_with_update(self):
        self.assertEqual(self.install("--tool", "codex", "--scope", "project", "--project", self.project).returncode, 0)
        again = self.install("--tool", "codex", "--scope", "project", "--project", self.project)
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("--update", again.stderr)
        self.assertEqual(self.install("--tool", "codex", "--scope", "project", "--project", self.project, "--update").returncode, 0)

        foreign = self.tmp / "foreign"
        (foreign / ".agents/skills/quality-review").mkdir(parents=True)
        (foreign / ".agents/skills/quality-review/SKILL.md").write_text("alheio")
        proc = self.install("--tool", "codex", "--scope", "project", "--project", foreign, "--update")
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual((foreign / ".agents/skills/quality-review/SKILL.md").read_text(), "alheio")

    def test_uninstall_removes_only_own_items(self):
        self.install("--tool", "both", "--scope", "project", "--project", self.project, "--with-agents")
        own_file = self.project / ".claude/agents/meu-agente.md"
        own_file.write_text("do time")
        proc = self.install("--tool", "both", "--scope", "project", "--project", self.project, "--with-agents", "--uninstall")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.files(self.project), [".claude/agents/meu-agente.md"])

    def test_user_scope_uses_home(self):
        proc = self.install("--tool", "claude", "--scope", "user")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.home / ".claude/skills/quality-review/SKILL.md").exists())

    def test_refuses_installing_into_base_repository(self):
        proc = self.install("--tool", "claude", "--scope", "project", "--project", ROOT)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse((ROOT / ".claude/skills").exists())

    def test_invalid_arguments(self):
        self.assertNotEqual(self.install("--tool", "vim", "--scope", "user").returncode, 0)
        self.assertNotEqual(self.install("--tool", "claude", "--scope", "project").returncode, 0)


if __name__ == "__main__":
    unittest.main()
