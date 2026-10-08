import shutil
import sys
import unittest

from _helpers import ROOT, TempDirMixin

sys.path.insert(0, str(ROOT / "scripts"))
import validate_repo  # noqa: E402


class RepositoryIntegrityTest(unittest.TestCase):
    def test_repository_is_valid(self):
        report = validate_repo.validate(ROOT)
        self.assertEqual(report.errors, [], "\n".join(report.errors))


class ValidatorDetectsProblemsTest(TempDirMixin, unittest.TestCase):
    """O validador precisa falhar quando a base é corrompida (testes de mutação)."""

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "base"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.skill = self.root / "skills/quality-review"

    def errors(self):
        return "\n".join(validate_repo.validate(self.root).errors)

    def edit(self, rel, old, new):
        path = self.root / rel
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_copy_is_valid_before_mutation(self):
        self.assertEqual(self.errors(), "")

    def test_duplicate_rule_id(self):
        self.edit("skills/quality-review/rules/universal/code-quality.md", "### UNI-QUA-002 —", "### UNI-QUA-001 —")
        self.assertIn("ID de regra duplicado UNI-QUA-001", self.errors())

    def test_missing_rule_field(self):
        self.edit("skills/quality-review/rules/persistence/pagination.md", "- **Evidência mínima:** E3 + justificativa", "- **Prova:** E3 + justificativa")
        self.assertIn("PER-PAG-001", self.errors())

    def test_unknown_rule_reference(self):
        self.edit("skills/quality-review/workflows/AUDIT.md", "## Passos", "## Passos\n\nVer PER-ZZZ-999.")
        self.assertIn("regra inexistente PER-ZZZ-999", self.errors())

    def test_unknown_conflict_reference(self):
        self.edit("skills/quality-review/rules/persistence/pagination.md", "- **Conflitos:** CF-11, CF-01", "- **Conflitos:** CF-99")
        self.assertIn("conflito inexistente CF-99", self.errors())

    def test_broken_link(self):
        self.edit("README.md", "[LICENSE](LICENSE)", "[LICENSE](NAO-EXISTE)")
        self.assertIn("link quebrado", self.errors())

    def test_plugin_manifest_must_not_declare_agents(self):
        self.edit(".claude-plugin/plugin.json", '"version": "0.1.0",', '"version": "0.1.0",\n  "agents": ["./agents/quality-auditor.md"],')
        self.assertIn("não deve declarar 'agents'", self.errors())

    def test_version_mismatch(self):
        self.edit(".claude-plugin/plugin.json", '"version": "0.1.0"', '"version": "9.9.9"')
        self.assertIn("versão do plugin", self.errors())

    def test_readonly_agent_with_edit_tool(self):
        self.edit("agents/quality-auditor.md", "tools: Read, Grep, Glob, Bash", "tools: Read, Grep, Glob, Bash, Edit")
        self.assertIn("somente leitura com ferramenta de edição", self.errors())

    def test_skill_path_reference(self):
        self.edit("skills/quality-review/SKILL.md", "`workflows/INIT.md`", "`workflows/START.md`")
        self.assertIn("workflows/START.md", self.errors())

    def test_skill_name_must_match_directory(self):
        self.edit("skills/quality-review/SKILL.md", "name: quality-review", "name: quality-audit")
        self.assertIn("difere do diretório", self.errors())


if __name__ == "__main__":
    unittest.main()
